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
// Configuration: KEY=VALUE lines in svrtv.ini next to this module (so a
// benchmark suite can switch steps by rewriting one file), overridden by the
// same names in the environment (Steam launch options accept
// "VAR=value %command%"):
//   SVRTV_LAYOUT       sbs or tab; unset, the module stays inert and the game
//                      runs in 2D exactly as with Valve's module
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
#include <stdint.h>

#include "sourcevr/isourcevirtualreality.h"

namespace {

struct Config {
	bool enabled;   // 3D requested (SVRTV_LAYOUT set); otherwise fully inert
	bool tab;
	int width, height;
	double aspect;
	double separation;
	double convergence;
	bool swap;
	FILE *log;
};

Config g_cfg;

// svrtv.ini next to this module: up to 32 KEY=VALUE lines.
char g_ini[32][2][128];
int g_nini;

// Hex without strtoul/sscanf, which current glibc redirects to its
// C23 variants (GLIBC_2.38) under _GNU_SOURCE.
uintptr_t parse_hex(const char **c)
{
	uintptr_t v = 0;
	for (;; (*c)++) {
		char h = **c;
		int d = (h >= '0' && h <= '9') ? h - '0' : (h >= 'a' && h <= 'f') ? h - 'a' + 10 : -1;
		if (d < 0)
			return v;
		v = v * 16 + d;
	}
}

// Finds this module's own path in /proc/self/maps (plain stdio, so no
// newer-glibc symbol such as dladdr@GLIBC_2.34 is pulled in).
bool module_path(char *out, size_t size)
{
	FILE *m = fopen("/proc/self/maps", "r");
	if (!m)
		return false;
	uintptr_t self = (uintptr_t)&module_path;
	char line[1200];
	bool found = false;
	while (fgets(line, sizeof(line), m)) {
		const char *c = line;
		uintptr_t lo = parse_hex(&c);
		if (*c++ != '-')
			continue;
		uintptr_t hi = parse_hex(&c);
		if (self < lo || self >= hi)
			continue;
		char *p = strchr(line, '/');
		if (p) {
			p[strcspn(p, "\n")] = 0;
			snprintf(out, size, "%s", p);
			found = true;
		}
		break;
	}
	fclose(m);
	return found;
}

void load_ini()
{
	char path[1024];
	if (!module_path(path, sizeof(path)))
		return;
	char *slash = strrchr(path, '/');
	if (!slash)
		return;
	snprintf(slash + 1, sizeof(path) - (slash + 1 - path), "svrtv.ini");
	FILE *f = fopen(path, "r");
	if (!f)
		return;
	char line[300];
	while (g_nini < 32 && fgets(line, sizeof(line), f)) {
		char *eq = strchr(line, '=');
		if (line[0] == '#' || !eq)
			continue;
		*eq = 0;
		char *val = eq + 1;
		val[strcspn(val, "\r\n")] = 0;
		snprintf(g_ini[g_nini][0], 128, "%s", line);
		snprintf(g_ini[g_nini][1], 128, "%s", val);
		g_nini++;
	}
	fclose(f);
}

// The environment wins over svrtv.ini.
const char *setting(const char *name)
{
	const char *v = getenv(name);
	if (v && *v)
		return v;
	for (int i = 0; i < g_nini; i++)
		if (!strcmp(g_ini[i][0], name))
			return g_ini[i][1];
	return NULL;
}

double env_double(const char *name, double def)
{
	const char *v = setting(name);
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
	load_ini();
	const char *layout = setting("SVRTV_LAYOUT");
	g_cfg.enabled = layout && *layout;
	g_cfg.tab = layout && !strcmp(layout, "tab");
	g_cfg.width = (int)env_double("SVRTV_WIDTH", 1920);
	g_cfg.height = (int)env_double("SVRTV_HEIGHT", 1080);
	g_cfg.aspect = env_double("SVRTV_ASPECT", (double)g_cfg.width / g_cfg.height);
	g_cfg.separation = env_double("SVRTV_SEPARATION", 2.5);
	g_cfg.convergence = env_double("SVRTV_CONVERGENCE", 120.0);
	g_cfg.swap = env_double("SVRTV_SWAP", 0) != 0;
	const char *lp = setting("SVRTV_LOG");
	g_cfg.log = (lp && *lp) ? fopen(lp, "a") : NULL;
	if (g_cfg.convergence <= 0)
		g_cfg.convergence = 120.0;
	logf("config (%d lines from svrtv.ini): enabled=%d layout=%s %dx%d aspect=%.4f separation=%.3f convergence=%.1f swap=%d\n",
	     g_nini, (int)g_cfg.enabled, g_cfg.tab ? "tab" : "sbs", g_cfg.width, g_cfg.height, g_cfg.aspect,
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

	// Without SVRTV_LAYOUT the module behaves like Valve's with no headset:
	// no device, never VR. (Reporting a device and forcing VR mode always made
	// the client switch to VR at startup in 2D runs, and crash; see below.)
	bool ShouldRunInVR() { return g_cfg.enabled && m_active; }
	bool IsHmdConnected() { return g_cfg.enabled; }

	void GetViewportBounds(VREye eye, int *x, int *y, int *w, int *h)
	{
		// The left eye takes the first half: left in side-by-side, top in
		// top-and-bottom, as HDMI 1.4 packs them.
		// Any output may be NULL: the client's Activate() asks only for the
		// size (client_virtualreality.cpp, GetViewportBounds(eye, NULL, NULL,
		// &w, &h)). Writing through those crashed Half-Life 2 at startup.
		bool first = (eye == VREye_Left) != g_cfg.swap;
		int vx, vy, vw, vh;
		if (g_cfg.tab) {
			vx = 0;
			vw = g_cfg.width;
			vh = g_cfg.height / 2;
			vy = first ? 0 : g_cfg.height / 2;
		} else {
			vy = 0;
			vh = g_cfg.height;
			vw = g_cfg.width / 2;
			vx = first ? 0 : g_cfg.width / 2;
		}
		if (x) *x = vx;
		if (y) *y = vy;
		if (w) *w = vw;
		if (h) *h = vh;
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
		if (!g_cfg.enabled)
			return false;
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
	bool ShouldForceVRMode() { return g_cfg.enabled; }
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
