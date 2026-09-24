// VR Stereo Spectator: sourcevr for 3D televisions.
//
// A replacement for the Source engine's sourcevr module (interface
// "SourceVirtualReality001", Source SDK 2013). The engine's own VR path
// renders each eye with the geometry this module supplies, into the
// viewport this module chooses; this module presents a stereoscopic
// television as the "headset": fixed pose, no lens distortion, both eyes
// packed side by side or top and bottom in the game's own window, which the
// television unpacks.
//
// Geometry: parallel eye cameras with an off-centre frustum, so both eyes
// share one screen plane at the convergence distance (no toe-in, no vertical
// parallax). Source coordinates are x forward, y left, z up; the projection
// convention follows mathlib's MatrixBuildPerspectiveX (view looks down -z,
// depth 0..1).
//
// Configuration, from the environment (Steam launch options accept
// "VAR=value %command%"):
//   SVRTV_LAYOUT       sbs (default) or tab
//   SVRTV_WIDTH/HEIGHT output size in pixels (default 1920x1080; match -w/-h)
//   SVRTV_ASPECT       displayed aspect, default WIDTH/HEIGHT
//   SVRTV_SEPARATION   eye separation in game units (default 2.5, about 64 mm)
//   SVRTV_CONVERGENCE  distance of the screen plane in game units (default 120)
//   SVRTV_SWAP         1 swaps the eyes
//   SVRTV_LOG          path of a log file (default: stderr only)
//
// Builds for 32-bit (today's native HL2) and 64-bit Source games alike.

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

#include "sourcevr/isourcevirtualreality.h"

namespace {

struct Config {
	bool tab;
	int width, height;
	double aspect;
	double separation;
	double convergence;
	bool swap;
	FILE *log;
};

Config g_cfg;

double env_double(const char *name, double def)
{
	const char *v = getenv(name);
	return (v && *v) ? atof(v) : def;
}

void logf(const char *fmt, ...)
{
	va_list ap;
	va_start(ap, fmt);
	fputs("[vr-stereo-spectator] ", stderr);
	vfprintf(stderr, fmt, ap);
	va_end(ap);
	if (g_cfg.log) {
		va_start(ap, fmt);
		vfprintf(g_cfg.log, fmt, ap);
		va_end(ap);
		fflush(g_cfg.log);
	}
}

void load_config()
{
	const char *layout = getenv("SVRTV_LAYOUT");
	g_cfg.tab = layout && !strcmp(layout, "tab");
	g_cfg.width = (int)env_double("SVRTV_WIDTH", 1920);
	g_cfg.height = (int)env_double("SVRTV_HEIGHT", 1080);
	g_cfg.aspect = env_double("SVRTV_ASPECT", (double)g_cfg.width / g_cfg.height);
	g_cfg.separation = env_double("SVRTV_SEPARATION", 2.5);
	g_cfg.convergence = env_double("SVRTV_CONVERGENCE", 120.0);
	g_cfg.swap = env_double("SVRTV_SWAP", 0) != 0;
	const char *lp = getenv("SVRTV_LOG");
	g_cfg.log = (lp && *lp) ? fopen(lp, "a") : NULL;
	if (g_cfg.convergence <= 0)
		g_cfg.convergence = 120.0;
	logf("config: layout=%s %dx%d aspect=%.4f separation=%.3f convergence=%.1f swap=%d\n",
	     g_cfg.tab ? "tab" : "sbs", g_cfg.width, g_cfg.height, g_cfg.aspect,
	     g_cfg.separation, g_cfg.convergence, (int)g_cfg.swap);
}

// +1 for the left eye, -1 for the right eye. The cameras never swap;
// SVRTV_SWAP only changes which half each eye is packed into.
double eye_sign(ISourceVirtualReality::VREye eye)
{
	return (eye == ISourceVirtualReality::VREye_Left) ? 1.0 : -1.0;
}

void set_identity(VMatrix &m)
{
	for (int i = 0; i < 4; i++)
		for (int j = 0; j < 4; j++)
			m.m[i][j] = (i == j) ? 1.0f : 0.0f;
}

class CSourceVRTelevision : public ISourceVirtualReality
{
public:
	CSourceVRTelevision() : m_active(false), m_fovX(75.0f) {}

	// IAppSystem
	bool Connect(CreateInterfaceFn) { return true; }
	void Disconnect() {}
	void *QueryInterface(const char *name)
	{
		return (name && !strcmp(name, SOURCE_VIRTUAL_REALITY_INTERFACE_VERSION)) ? this : NULL;
	}
	InitReturnVal_t Init() { return INIT_OK; }
	void Shutdown() {}

	// The television is always present; VR mode is on only after vr_activate.
	bool ShouldRunInVR() { return m_active; }
	bool IsHmdConnected() { return true; }

	void GetViewportBounds(VREye eye, int *x, int *y, int *w, int *h)
	{
		// The left eye takes the first half: left in side-by-side, top in
		// top-and-bottom, as HDMI 1.4 packs them.
		bool first = (eye == VREye_Left) != g_cfg.swap;
		if (g_cfg.tab) {
			*x = 0;
			*w = g_cfg.width;
			*h = g_cfg.height / 2;
			*y = first ? 0 : g_cfg.height / 2;
		} else {
			*y = 0;
			*h = g_cfg.height;
			*w = g_cfg.width / 2;
			*x = first ? 0 : g_cfg.width / 2;
		}
	}

	// No lenses: nothing to undistort, and the HUD is left to the client.
	bool DoDistortionProcessing(VREye) { return false; }
	bool CompositeHud(VREye, float[4], bool, bool, bool) { return false; }

	// Fixed pose: the head is where the game camera is.
	VMatrix GetMideyePose()
	{
		VMatrix m;
		set_identity(m);
		return m;
	}

	// Called with the game's field of view each frame; keep it for the
	// projection.
	bool SampleTrackingState(float playerGameFov, float)
	{
		if (playerGameFov > 1.0f && playerGameFov < 179.0f)
			m_fovX = playerGameFov;
		return true;
	}

	bool GetDisplayBounds(VRRect_t *r)
	{
		r->nX = 0;
		r->nY = 0;
		r->nWidth = g_cfg.width;
		r->nHeight = g_cfg.height;
		return true;
	}

	bool GetEyeProjectionMatrix(VMatrix *out, VREye eye, float zNear, float zFar, float fovScale)
	{
		// Source's fov is defined for a 4:3 screen; widen it to the displayed
		// aspect as the engine does for widescreen, then apply the zoom scale.
		double t = tan(m_fovX * M_PI / 360.0) * (g_cfg.aspect / (4.0 / 3.0));
		if (fovScale > 0.0f)
			t *= fovScale;
		// Tangent bounds of the mid-eye window, shifted for this eye so the
		// window at the convergence distance is shared by both eyes. The left
		// eye sits to the left of the mid-eye, so its window centre lies to its
		// right.
		double shift = eye_sign(eye) * (g_cfg.separation / 2.0) / g_cfg.convergence;
		double l = -t + shift, r = t + shift;
		double b = -t / g_cfg.aspect, tp = t / g_cfg.aspect;

		VMatrix &m = *out;
		for (int i = 0; i < 4; i++)
			for (int j = 0; j < 4; j++)
				m.m[i][j] = 0.0f;
		m.m[0][0] = (float)(2.0 / (r - l));
		m.m[0][2] = (float)((r + l) / (r - l));
		m.m[1][1] = (float)(2.0 / (tp - b));
		m.m[1][2] = (float)((tp + b) / (tp - b));
		m.m[2][2] = zFar / (zNear - zFar);
		m.m[2][3] = zNear * zFar / (zNear - zFar);
		m.m[3][2] = -1.0f;
		return true;
	}

	// Mid-eye to eye: a sideways shift of half the separation. Source's +y is
	// left, so the left eye moves +y and the right eye -y.
	VMatrix GetMidEyeFromEye(VREye eye)
	{
		VMatrix m;
		set_identity(m);
		m.m[1][3] = (float)(eye_sign(eye) * g_cfg.separation / 2.0);
		return m;
	}

	int GetVRModeAdapter() { return 0; }
	bool WillDriftInYaw() { return false; }

	// No offscreen targets: each eye renders straight into its viewport of
	// the game's own frame.
	void CreateRenderTargets(IMaterialSystem *) {}
	void ShutdownRenderTargets() {}
	ITexture *GetRenderTarget(VREye, EWhichRenderTarget) { return NULL; }
	void GetRenderTargetFrameBufferDimensions(int &w, int &h)
	{
		w = g_cfg.width;
		h = g_cfg.height;
	}

	bool Activate()
	{
		m_active = true;
		logf("activated\n");
		return true;
	}
	void Deactivate()
	{
		m_active = false;
		logf("deactivated\n");
	}

	// "VR because Steam said so": skips the client's headset-adapter checks.
	bool ShouldForceVRMode() { return true; }
	void SetShouldForceVRMode() {}

private:
	bool m_active;
	float m_fovX;
};

CSourceVRTelevision g_television;

} // namespace

// The Source interface factory, as tier1's EXPOSE_SINGLE_INTERFACE would
// export it, without linking tier1.
extern "C" __attribute__((visibility("default")))
void *CreateInterface(const char *name, int *returnCode)
{
	static bool configured = false;
	if (!configured) {
		load_config();
		configured = true;
	}
	if (name && !strcmp(name, SOURCE_VIRTUAL_REALITY_INTERFACE_VERSION)) {
		if (returnCode)
			*returnCode = IFACE_OK;
		logf("CreateInterface(%s): television\n", name);
		return &g_television;
	}
	if (returnCode)
		*returnCode = IFACE_FAILED;
	return NULL;
}

// No C++ runtime: the only object is static, so the deleting destructor the
// vtable references is never called.
void operator delete(void *) noexcept {}
void operator delete(void *, size_t) noexcept {}
extern "C" void __cxa_pure_virtual() { abort(); }
