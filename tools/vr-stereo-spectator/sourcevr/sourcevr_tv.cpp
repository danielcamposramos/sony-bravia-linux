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
#include "materialsystem/imaterialsystem.h"
#include "materialsystem/itexture.h"

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
char g_dir[1024];   // this module's directory, with the trailing slash

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
	slash[1] = 0;
	snprintf(g_dir, sizeof(g_dir), "%s", path);
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
	// A relative log path is taken from this module's directory: Steam runs
	// the game in a runtime container that sees the game's folders but not
	// necessarily the caller's.
	const char *lp = setting("SVRTV_LOG");
	if (lp && *lp) {
		char full[1200];
		snprintf(full, sizeof(full), "%s%s", lp[0] == '/' ? "" : g_dir, lp);
		g_cfg.log = fopen(full, "a");
		// An absolute path outside what the container shares cannot be
		// opened; log next to the module instead.
		if (!g_cfg.log) {
			snprintf(full, sizeof(full), "%ssvrtv.log", g_dir);
			g_cfg.log = fopen(full, "a");
		}
	}
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
	CSourceVRTelevision() : m_active(false), m_fovX(75.0f), m_ms(NULL), m_factory(NULL), m_triedTargets(false)
	{
		m_rt[0] = m_rt[1] = NULL;
		m_shown[0] = m_shown[1] = false;
		for (int i = 0; i < 8; i++)
			m_traced[i] = false;
	}

	// IAppSystem
	// The engine connects the module like any app system; its factory
	// reaches the material system, which the render targets need.
	bool Connect(CreateInterfaceFn factory)
	{
		trace(5, "Connect");
		m_factory = factory;
		return true;
	}
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
		int vx, vy, vw, vh;
		ensure_targets();
		if (m_rt[0] && m_rt[1]) {
			// Each eye renders into its own target, from its corner.
			half(eye, NULL, NULL, &vw, &vh);
			vx = vy = 0;
		} else
			half(eye, &vx, &vy, &vw, &vh);
		if (x) *x = vx;
		if (y) *y = vy;
		if (w) *w = vw;
		if (h) *h = vh;
	}

	// Where an eye goes in the output frame.
	void half(VREye eye, int *x, int *y, int *w, int *h)
	{
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

	// No lenses, so "distortion processing" is just putting the eye's picture
	// into its half of the frame. The client calls it after each eye, except
	// while a screenshot is being taken; CompositeHud comes after it in every
	// frame, screenshots included, and shows the eye if this did not.
	bool DoDistortionProcessing(VREye eye)
	{
		trace(0, "DoDistortionProcessing");
		show(eye);
		return true;
	}

	// The HUD and menus are painted into the client's "_rt_gui" target
	// (640x480); the client works out where that sheet sits in each eye's
	// view (normalised device coordinates) and asks the module to paste it.
	// The client's own in-world HUD materials do the blending.
	bool CompositeHud(VREye eye, float ndc[4], bool, bool, bool translucent)
	{
		trace(1, "CompositeHud");
		show(eye);
		if (!m_ms)
			return false;
		ITexture *gui = m_ms->FindTexture("_rt_gui", NULL, false);
		IMaterial *mat = m_ms->FindMaterial(translucent ? "vgui/inworldui" : "vgui/inworldui_opaque", TEXTURE_GROUP_VGUI, false);
		if (!gui || !mat)
			return false;
		int hx, hy, hw, hh;
		half(eye, &hx, &hy, &hw, &hh);
		// NDC: x -1..1 left to right, y -1..1 bottom to top.
		int x0 = hx + (int)((ndc[0] * 0.5f + 0.5f) * hw);
		int x1 = hx + (int)((ndc[2] * 0.5f + 0.5f) * hw);
		int y0 = hy + (int)((0.5f - ndc[3] * 0.5f) * hh);
		int y1 = hy + (int)((0.5f - ndc[1] * 0.5f) * hh);
		if (x1 <= x0 || y1 <= y0)
			return false;
		int tw = gui->GetActualWidth(), th = gui->GetActualHeight();
		CMatRenderContextPtr ctx(m_ms);
		ctx->PushRenderTargetAndViewport(NULL, 0, 0, g_cfg.width, g_cfg.height);
		ctx->DrawScreenSpaceRectangle(mat, x0, y0, x1 - x0, y1 - y0, 0, 0, tw - 1, th - 1, tw, th);
		ctx->PopRenderTargetAndViewport();
		return true;
	}

	// Copies an eye's target into its half of the frame, once per frame.
	void show(VREye eye)
	{
		int i = (eye == VREye_Left) ? 0 : 1;
		if (!m_ms || !m_rt[i] || m_shown[i])
			return;
		m_shown[i] = true;
		int hx, hy, hw, hh;
		half(eye, &hx, &hy, &hw, &hh);
		Rect_t src = { 0, 0, hw, hh };
		Rect_t dst = { hx, hy, hw, hh };
		CMatRenderContextPtr ctx(m_ms);
		ctx->PushRenderTargetAndViewport(NULL);
		ctx->CopyTextureToRenderTargetEx(0, m_rt[i], &src, &dst);
		ctx->PopRenderTargetAndViewport();
	}

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
		// Called once per frame before the eyes render: a new frame.
		m_shown[0] = m_shown[1] = false;
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

	// One colour target per eye, the size of its half of the frame; depth is
	// the frame's own (MATERIAL_RT_DEPTH_SHARED, which needs a target no
	// larger than the frame). The engine calls this inside its render-target
	// allocation. Without targets, each eye renders straight into its half.
	void CreateRenderTargets(IMaterialSystem *ms)
	{
		trace(2, "CreateRenderTargets");
		if (!g_cfg.enabled || !ms)
			return;
		m_ms = ms;
		m_triedTargets = true;
		make_targets();
	}

	// This engine never calls CreateRenderTargets (2026-09-24 log: the
	// client asks for GetRenderTarget first). So the targets are made on
	// first use, inside the allocation bracket render targets need.
	void ensure_targets()
	{
		if (m_triedTargets || !g_cfg.enabled || !m_active)
			return;
		m_triedTargets = true;
		if (!m_ms && m_factory) {
			m_ms = (IMaterialSystem *)m_factory(MATERIAL_SYSTEM_INTERFACE_VERSION_OLD, NULL);
			logf("material system %s: %s\n", MATERIAL_SYSTEM_INTERFACE_VERSION_OLD, m_ms ? "found" : "not found");
		}
		if (!m_ms)
			return;
		m_ms->BeginRenderTargetAllocation();
		make_targets();
		m_ms->EndRenderTargetAllocation();
	}

	void make_targets()
	{
		IMaterialSystem *ms = m_ms;
		static const char *names[2] = { "_rt_svrtv_left", "_rt_svrtv_right" };
		for (int i = 0; i < 2; i++) {
			int w, h;
			half(i ? VREye_Right : VREye_Left, NULL, NULL, &w, &h);
			m_rt[i] = ms->CreateNamedRenderTargetTextureEx(names[i], w, h, RT_SIZE_LITERAL,
				ms->GetBackBufferFormat(), MATERIAL_RT_DEPTH_SHARED,
				0x4 | 0x8 | 0x100 | 0x200,   // TEXTUREFLAGS_CLAMPS|CLAMPT|NOMIP|NOLOD
				0);
			logf("render target %s: %dx%d requested, %dx%d made\n", names[i], w, h,
			     m_rt[i] ? m_rt[i]->GetActualWidth() : 0, m_rt[i] ? m_rt[i]->GetActualHeight() : 0);
		}
		if (!m_rt[0] || !m_rt[1])
			m_rt[0] = m_rt[1] = NULL;
	}
	void ShutdownRenderTargets()
	{
		trace(3, "ShutdownRenderTargets");
		m_rt[0] = m_rt[1] = NULL;
	}
	ITexture *GetRenderTarget(VREye eye, EWhichRenderTarget which)
	{
		trace(4, "GetRenderTarget");
		ensure_targets();
		if (which != RT_Color)
			return NULL;
		return m_rt[eye == VREye_Left ? 0 : 1];
	}
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
	// Logs the first call of each traced method: which parts of the
	// interface the engine and client actually use, and in what order.
	void trace(int n, const char *what)
	{
		if (n < 0 || n >= 8 || m_traced[n])
			return;
		m_traced[n] = true;
		logf("first call: %s\n", what);
	}

	bool m_active;
	float m_fovX;
	IMaterialSystem *m_ms;
	CreateInterfaceFn m_factory;
	bool m_triedTargets;
	ITexture *m_rt[2];
	bool m_shown[2];
	bool m_traced[8];
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
