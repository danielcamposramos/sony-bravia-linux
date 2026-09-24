// Loads the built module and checks the stereo geometry numerically:
// zero parallax at the convergence distance, uncrossed (behind-screen)
// parallax far away, crossed (in-front) parallax near, and the viewports.
#include <dlfcn.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "sourcevr/isourcevirtualreality.h"
typedef void *(*Factory)(const char *, int *);

// Source world point relative to the mid-eye (forward, left, up) -> NDC x
// for one eye: move to the eye (GetMidEyeFromEye), convert Source axes to
// view space (x right = -left, y up = up, z = -forward), project.
static double ndc_x(ISourceVirtualReality *vr, ISourceVirtualReality::VREye e, double fwd, double left)
{
	VMatrix off = vr->GetMidEyeFromEye(e), p;
	vr->GetEyeProjectionMatrix(&p, e, 7.0f, 30000.0f, 1.0f);
	double l = left - off.m[1][3];
	double vx = -l, vz = -fwd;
	double cx = p.m[0][0] * vx + p.m[0][2] * vz, cw = p.m[3][2] * vz;
	return cx / cw;
}
int main(int argc, char **argv)
{
	void *h = dlopen(argv[1], RTLD_NOW);
	if (!h) { printf("dlopen: %s\n", dlerror()); return 1; }
	int rc = -1;
	ISourceVirtualReality *vr = (ISourceVirtualReality *)((Factory)dlsym(h, "CreateInterface"))(SOURCE_VIRTUAL_REALITY_INTERFACE_VERSION, &rc);
	// The client's Activate() asks only for the size: NULL x and y must be fine.
	{ int w = -1, h = -1; vr->GetViewportBounds(ISourceVirtualReality::VREye_Left, NULL, NULL, &w, &h);
	  printf("NULL outputs accepted: size %dx%d\n", w, h); }
	if (getenv("SVRTV_EXPECT_INERT")) {
		bool inert = !vr->IsHmdConnected() && !vr->ShouldForceVRMode() && !vr->Activate() && !vr->ShouldRunInVR();
		printf("%s\n", inert ? "INERT OK (no headset, no forced VR, Activate refused)" : "INERT FAIL");
		return !inert;
	}
	printf("CreateInterface rc=%d ptr=%s  QueryInterface self=%d  ShouldForceVRMode=%d\n", rc, vr ? "ok" : "NULL",
	       vr && vr->QueryInterface(SOURCE_VIRTUAL_REALITY_INTERFACE_VERSION) == vr, vr->ShouldForceVRMode());
	vr->SampleTrackingState(75.0f, 0.0f);
	printf("ShouldRunInVR before/after Activate: %d/", vr->ShouldRunInVR()); vr->Activate(); printf("%d\n", vr->ShouldRunInVR());
	int ok = 1;
	static const double dists[] = {60.0, 120.0, 400.0, 5000.0};
	for (double d : dists) {
		double L = ndc_x(vr, ISourceVirtualReality::VREye_Left, d, 0), R = ndc_x(vr, ISourceVirtualReality::VREye_Right, d, 0);
		const char *where = fabs(R - L) < 1e-6 ? "on screen" : (R > L ? "behind screen" : "in front");
		printf("  point %6.0f units ahead: left %+.5f right %+.5f  parallax %+.5f NDC  -> %s\n", d, L, R, R - L, where);
		if (d == 120.0 && fabs(R - L) > 1e-6) ok = 0;
		if (d > 120.0 && !(R > L)) ok = 0;
		if (d < 120.0 && !(R < L)) ok = 0;
	}
	int x, y, w, hh;
	vr->GetViewportBounds(ISourceVirtualReality::VREye_Left, &x, &y, &w, &hh); printf("  viewport left  %d,%d %dx%d\n", x, y, w, hh);
	vr->GetViewportBounds(ISourceVirtualReality::VREye_Right, &x, &y, &w, &hh); printf("  viewport right %d,%d %dx%d\n", x, y, w, hh);
	printf("%s\n", ok ? "GEOMETRY OK" : "GEOMETRY FAIL");
	return !ok;
}
