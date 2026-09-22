// stereo-modeset: claim a DRM connector in a 3D mode and draw a disparity
// pattern until interrupted. Run from a bare VT as root with no compositor
// running (needs DRM master). This is the smoke test for the amdgpu VSIF patch:
// if the TV auto-switches into 3D when this tool modesets a stereo mode,
// the kernel patch is emitting the HDMI vendor-specific infoframe correctly.
//
// cc -o stereo-modeset stereo-modeset.c $(pkg-config --cflags --libs libdrm)
// usage: stereo-modeset [card] [connector] [sbs|tab|fp|deep12|deep10|deep8] [isolate] [vsif]
//        [bpc12|bpc10|bpc8] [fmt=rgbfull|rgblimited|rgbauto|yuv444|yuv422] [720p|hz24]
// defaults: /dev/dri/card0 HDMI-A-1 sbs
// 720p: pick the 1280x720@60 variant instead of 1080p60 (sbs/tab only)
// hz24: pick the 1920x1080@24 variant instead of 60 Hz (sbs/tab only)
// deep12: plain 1080p60 link-depth probe; bpc12 layers the same max-bpc
// request onto sbs/tab/fp so the already-proven 3D path remains active.
// deep10/deep8: identical probe with max bpc clamped to 10 or 8. Every run
// paints its format and requested depth in big yellow text near the top
// (per eye in 3D), and deep probes add a bottom band of colour bars over
// near-black/near-white steps that expose matrix and range errors.
// fmt=: request the pixel encoding and quantization range through the
// standard "color format" and "Broadcast RGB" connector properties.
//
// vsif: the proprietary nvidia-drm path. nvidia-drm never sets
// stereo_allowed, so no 3D-flagged mode survives pruning -- but it exposes
// the NV_HDMI_VSIF_METADATA connector blob whose payload crosses into NVKMS
// with the modeset. TaB/SBS-half share the 2D link timing, so a plain
// 1920x1080@60 modeset plus an injected HDMI 3D VSIF drives the sink into
// 3D with no kernel change. FP is refused there (its timing is doubled).
// SPDX-License-Identifier: CC0-1.0

#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

enum stereo_layout {
	LAYOUT_SBS,
	LAYOUT_TAB,
	LAYOUT_FP,
	LAYOUT_DEEP12,
};

static volatile sig_atomic_t stop_flag;
static void on_term(int sig) { (void)sig; stop_flag = 1; }

static char const *stereo_name(uint32_t flags)
{
	switch (flags & DRM_MODE_FLAG_3D_MASK) {
	case DRM_MODE_FLAG_3D_FRAME_PACKING:         return "frame packing";
	case DRM_MODE_FLAG_3D_TOP_AND_BOTTOM:        return "top-and-bottom";
	case DRM_MODE_FLAG_3D_SIDE_BY_SIDE_HALF:     return "side-by-side half";
	default:                                     return NULL;
	}
}

static int parse_layout(char const *arg, enum stereo_layout *layout,
			char const **name, uint32_t *flag)
{
	if (!strcmp(arg, "sbs")) {
		*layout = LAYOUT_SBS;
		*name = "side-by-side half";
		*flag = DRM_MODE_FLAG_3D_SIDE_BY_SIDE_HALF;
	} else if (!strcmp(arg, "tab")) {
		*layout = LAYOUT_TAB;
		*name = "top-and-bottom";
		*flag = DRM_MODE_FLAG_3D_TOP_AND_BOTTOM;
	} else if (!strcmp(arg, "fp")) {
		*layout = LAYOUT_FP;
		*name = "frame packing";
		*flag = DRM_MODE_FLAG_3D_FRAME_PACKING;
	} else if (!strcmp(arg, "deep12")) {
		*layout = LAYOUT_DEEP12;
		*name = "12-bpc SDR transport";
		*flag = 0;
	} else if (!strcmp(arg, "deep10")) {
		*layout = LAYOUT_DEEP12;
		*name = "10-bpc SDR transport";
		*flag = 0;
	} else if (!strcmp(arg, "deep8")) {
		*layout = LAYOUT_DEEP12;
		*name = "8-bpc SDR transport";
		*flag = 0;
	} else {
		return -1;
	}
	return 0;
}

static uint32_t pref_w = 1920, pref_h = 1080, pref_hz = 60;

static int mode_score(drmModeModeInfo const *mode, enum stereo_layout layout,
		      uint32_t flag)
{
	if (layout == LAYOUT_DEEP12) {
		if ((mode->flags & DRM_MODE_FLAG_3D_MASK) ||
		    mode->hdisplay != 1920 || mode->vdisplay != 1080 ||
		    mode->vrefresh != 60)
			return -1;
		return mode->clock == 148500 ? 2 : 1;
	}

	if ((mode->flags & DRM_MODE_FLAG_3D_MASK) != flag)
		return -1;

	if (layout == LAYOUT_FP) {
		if (mode->hdisplay != 1920 || mode->vdisplay != 1080 ||
		    mode->vrefresh != 24)
			return -1;
		/* Prefer exact 24.000 Hz over the equivalent 23.976 mode. */
		return mode->clock == 74250 ? 2 : 1;
	}

	if (mode->hdisplay != pref_w || mode->vdisplay != pref_h ||
	    mode->vrefresh != pref_hz)
		return -1;
	/* exact-CEA clocks: 1080p60 is 148.5 MHz, 720p60/1080p24 are 74.25 */
	{
		uint32_t pref_clk = (pref_w == 1920 && pref_hz == 60) ? 148500 : 74250;
		return pref_clk == mode->clock ? 2 : 1;
	}
}

static void draw_label(uint32_t *px, uint32_t stride, uint32_t width,
		       uint32_t height, const char *text)
{
	/* callers offset px to place the label inside an eye region */
	/* 8x8 hand glyphs, one byte per row, bit 7 = leftmost pixel.
	 * Only the characters the depth labels need. */
	static const struct { char c; uint8_t g[8]; } FONT[] = {
		{ '0', { 0x3C, 0x66, 0x6E, 0x76, 0x66, 0x66, 0x3C, 0 } },
		{ '1', { 0x18, 0x38, 0x18, 0x18, 0x18, 0x18, 0x7E, 0 } },
		{ '2', { 0x3C, 0x66, 0x06, 0x0C, 0x30, 0x60, 0x7E, 0 } },
		{ '-', { 0x00, 0x00, 0x00, 0x7E, 0x00, 0x00, 0x00, 0 } },
		{ 'A', { 0x18, 0x3C, 0x66, 0x66, 0x7E, 0x66, 0x66, 0 } },
		{ 'B', { 0x7C, 0x66, 0x66, 0x7C, 0x66, 0x66, 0x7C, 0 } },
		{ 'C', { 0x3C, 0x66, 0x60, 0x60, 0x60, 0x66, 0x3C, 0 } },
		{ 'G', { 0x3C, 0x66, 0x60, 0x6E, 0x66, 0x66, 0x3C, 0 } },
		{ 'I', { 0x3C, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3C, 0 } },
		{ 'L', { 0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x7E, 0 } },
		{ 'M', { 0x63, 0x77, 0x7F, 0x6B, 0x63, 0x63, 0x63, 0 } },
		{ 'P', { 0x7C, 0x66, 0x66, 0x7C, 0x60, 0x60, 0x60, 0 } },
		{ 'R', { 0x7C, 0x66, 0x66, 0x7C, 0x6C, 0x66, 0x66, 0 } },
		{ 'T', { 0x7E, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0 } },
		{ 'D', { 0x78, 0x6C, 0x66, 0x66, 0x66, 0x6C, 0x78, 0 } },
		{ 'E', { 0x7E, 0x60, 0x60, 0x7C, 0x60, 0x60, 0x7E, 0 } },
		{ 'F', { 0x7E, 0x60, 0x60, 0x7C, 0x60, 0x60, 0x60, 0 } },
		{ 'N', { 0x66, 0x76, 0x7E, 0x7E, 0x6E, 0x66, 0x66, 0 } },
		{ 'O', { 0x3C, 0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0 } },
		{ 'S', { 0x3C, 0x66, 0x60, 0x3C, 0x06, 0x66, 0x3C, 0 } },
		{ 'U', { 0x66, 0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0 } },
		{ 'V', { 0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x18, 0 } },
		{ 'Y', { 0x66, 0x66, 0x66, 0x3C, 0x18, 0x18, 0x18, 0 } },
		{ '4', { 0x0C, 0x1C, 0x3C, 0x6C, 0x7E, 0x0C, 0x0C, 0 } },
		{ '8', { 0x3C, 0x66, 0x66, 0x3C, 0x66, 0x66, 0x3C, 0 } },
	};
	int len = strlen(text), scale = 12;

	if (8 * len * scale > (int)width - 64)
		scale = ((int)width - 64) / (8 * len);
	if (scale < 1)
		scale = 1;

	uint32_t gw = 8 * scale * len, gh = 8 * scale;
	uint32_t x0 = (width - gw) / 2, y0 = 48;

	for (uint32_t y = y0 - 8; y < y0 + gh + 8 && y < height; y++)
	for (uint32_t x = x0 - 16; x < x0 + gw + 16 && x < width; x++)
		px[y * stride + x] = 0;

	for (int ci = 0; ci < len; ci++) {
		const uint8_t *g = NULL;
		for (size_t f = 0; f < sizeof(FONT) / sizeof(FONT[0]); f++)
			if (FONT[f].c == text[ci])
				g = FONT[f].g;
		if (!g)
			continue;
		for (int r = 0; r < 8; r++)
		for (int i = 0; i < 8; i++)
			if ((g[r] >> (7 - i)) & 1)
				for (int dy = 0; dy < scale; dy++)
				for (int dx = 0; dx < scale; dx++)
					px[(y0 + r * scale + dy) * stride +
					   x0 + (ci * 8 + i) * scale + dx] = 0xFFFF00;
	}
}

/* Set a connector enum property by its value name; 0 on success. */
static int set_enum_prop(int fd, drmModeConnector *conn, const char *prop,
			 const char *value)
{
	for (int i = 0; i < conn->count_props; i++) {
		drmModePropertyPtr pr = drmModeGetProperty(fd, conn->props[i]);
		int ret = -1;

		if (!pr)
			continue;
		if (strcmp(pr->name, prop)) {
			drmModeFreeProperty(pr);
			continue;
		}
		for (int e = 0; e < pr->count_enums; e++) {
			if (strcmp(pr->enums[e].name, value))
				continue;
			ret = drmModeConnectorSetProperty(fd, conn->connector_id,
							  pr->prop_id,
							  pr->enums[e].value);
			if (ret)
				perror(prop);
			else
				printf("requested connector property %s=%s\n",
				       prop, value);
			break;
		}
		if (ret && ret != -1)
			ret = -2;
		else if (ret == -1)
			fprintf(stderr, "%s has no value '%s'\n", prop, value);
		drmModeFreeProperty(pr);
		return ret;
	}
	fprintf(stderr, "connector has no '%s' property\n", prop);
	return -1;
}

/* Bottom quarter of a deep-colour frame: 100% colour bars (a wrong or
 * swapped YCbCr matrix tints them) over near-black 0..32 and near-white
 * 219..255 steps (a quantization-range mismatch crushes or clips them).
 */
static void draw_test_band(uint32_t *px, uint32_t stride, uint32_t w, uint32_t h)
{
	static const uint32_t bars[8] = {
		0xffffff, 0xffff00, 0x00ffff, 0x00ff00,
		0xff00ff, 0xff0000, 0x0000ff, 0x000000,
	};
	static const uint8_t lo[8] = { 0, 4, 8, 12, 16, 20, 24, 32 };
	static const uint8_t hi[8] = { 219, 227, 231, 235, 239, 243, 251, 255 };
	uint32_t y0 = h * 3 / 4, ym = y0 + (h - y0) / 2;

	for (uint32_t y = y0; y < h; y++)
	for (uint32_t x = 0; x < w; x++) {
		uint32_t c;

		if (y < ym) {
			c = bars[x * 8 / w];
		} else {
			uint32_t i = x * 16 / w;
			uint8_t v = i < 8 ? lo[i] : hi[i - 8];

			c = v << 16 | v << 8 | v;
		}
		px[y * stride + x] = c;
	}
}

int main(int argc, char **argv)
{
	char const *path = argc > 1 ? argv[1] : "/dev/dri/card0";
	char const *want = argc > 2 ? argv[2] : "HDMI-A-1";
	char const *layout_arg = argc > 3 ? argv[3] : "sbs";
	int isolate = 0, vsif = 0, max_bpc = 0;
	char const *fmt_arg = NULL;
	char label[48];
	char const *want_stereo;
	enum stereo_layout layout;
	uint32_t want_flag;

	if (parse_layout(layout_arg, &layout, &want_stereo, &want_flag)) {
		fprintf(stderr, "unknown layout '%s'; use sbs, tab, fp, deep12, deep10 or deep8\n",
			layout_arg);
		return 2;
	}
	max_bpc = layout != LAYOUT_DEEP12 ? 0 :
		  !strcmp(layout_arg, "deep10") ? 10 :
		  !strcmp(layout_arg, "deep8") ? 8 : 12;
	for (int i = 4; i < argc; i++) {
		if (!strcmp(argv[i], "isolate"))
			isolate = 1;
		else if (!strcmp(argv[i], "vsif"))
			vsif = 1;
		else if (!strcmp(argv[i], "bpc12"))
			max_bpc = 12;
		else if (!strcmp(argv[i], "bpc10"))
			max_bpc = 10;
		else if (!strcmp(argv[i], "bpc8"))
			max_bpc = 8;
		else if (!strncmp(argv[i], "fmt=", 4))
			fmt_arg = argv[i] + 4;
		else if (!strcmp(argv[i], "720p")) {
			pref_w = 1280; pref_h = 720;
		} else if (!strcmp(argv[i], "hz24"))
			pref_hz = 24;
		else {
			fprintf(stderr, "unknown option '%s'; use isolate, vsif, bpc12, bpc10, bpc8, fmt=..., 720p and/or hz24\n",
				argv[i]);
			return 2;
		}
	}
	if (vsif) {
		if (layout == LAYOUT_FP) {
			fprintf(stderr, "vsif injection cannot do frame packing: its link timing is doubled, the injection only announces the packing\n");
			return 2;
		}
		want_flag = 0; /* plain 2D timing; the 3D layout rides the injected VSIF */
	}

	setvbuf(stdout, NULL, _IOLBF, 0); /* log capture: survive timeout kill */

	int fd = open(path, O_RDWR | O_CLOEXEC);
	if (fd < 0) { perror("open"); return 1; }
	if (drmSetClientCap(fd, DRM_CLIENT_CAP_STEREO_3D, 1) ||
	    drmSetClientCap(fd, DRM_CLIENT_CAP_ASPECT_RATIO, 1)) {
		fprintf(stderr, "client caps refused\n"); return 1;
	}
	/* connector property lists are only handed to atomic-capable clients */
	if (vsif && drmSetClientCap(fd, DRM_CLIENT_CAP_ATOMIC, 1)) {
		fprintf(stderr, "atomic cap refused (needed to find the VSIF property)\n");
		return 1;
	}

	drmModeRes *res = drmModeGetResources(fd);
	drmModeConnector *conn = NULL;
	for (int i = 0; i < res->count_connectors && !conn; i++) {
		drmModeConnector *c = drmModeGetConnector(fd, res->connectors[i]);
		char name[64];
		snprintf(name, sizeof name, "%s-%u",
			 drmModeGetConnectorTypeName(c->connector_type), c->connector_type_id);
		if (!strcmp(name, want) && c->connection == DRM_MODE_CONNECTED)
			conn = c;
		else
			drmModeFreeConnector(c);
	}
	if (!conn) { fprintf(stderr, "connector %s not found/connected\n", want); return 1; }

	drmModeModeInfo *mode = NULL;
	int best_score = -1;
	for (int i = 0; i < conn->count_modes; i++) {
		drmModeModeInfo *m = &conn->modes[i];
		char const *s = stereo_name(m->flags);
		if (s) printf("stereo mode: %-10s %4ux%u @%u %s\n",
			      m->name, m->hdisplay, m->vdisplay, m->vrefresh, s);
		int score = mode_score(m, layout, want_flag);
		if (score > best_score) {
			mode = m;
			best_score = score;
		}
	}
	if (!mode) { fprintf(stderr, "no suitable %s mode on %s%s\n",
			     want_stereo, want,
			     vsif ? "" : " -- kernel stereo support not active?"); return 1; }
	printf("choosing %s %ux%u @%u clk=%u (%s)\n", mode->name, mode->hdisplay,
	       mode->vdisplay, mode->vrefresh, mode->clock, want_stereo);
	if (vsif)
		printf("vsif mode: %s is announced by the injected blob; the timing stays plain 2D\n",
		       want_stereo);

	drmModeEncoder *enc = conn->encoder_id
		? drmModeGetEncoder(fd, conn->encoder_id) : NULL;
	uint32_t crtc_id = 0;
	if (enc && enc->crtc_id) {
		crtc_id = enc->crtc_id;
	} else {
		for (int e = 0; e < conn->count_encoders && !crtc_id; e++) {
			drmModeEncoder *en = drmModeGetEncoder(fd, conn->encoders[e]);
			if (!en) continue;
			for (int c = 0; c < res->count_crtcs && !crtc_id; c++)
				if (en->possible_crtcs & (1 << c))
					crtc_id = res->crtcs[c];
			if (en != enc) drmModeFreeEncoder(en);
		}
	}
	if (enc) drmModeFreeEncoder(enc);
	if (!crtc_id) { fprintf(stderr, "no usable crtc\n"); return 1; }

	drmModeCrtc *saved = drmModeGetCrtc(fd, crtc_id);

	/* Detached hardware tests must not leave another connector on this GPU
	 * scanning an unrelated framebuffer. The other DRM device is isolated by
	 * its harness, because one fd cannot control CRTCs owned by another GPU.
	 */
	if (isolate) {
		for (int i = 0; i < res->count_crtcs; i++) {
			uint32_t other_id = res->crtcs[i];
			if (other_id == crtc_id)
				continue;
			drmModeCrtc *other = drmModeGetCrtc(fd, other_id);
			if (other && other->buffer_id) {
				printf("isolate: disabling non-target CRTC %u\n", other_id);
				if (drmModeSetCrtc(fd, other_id, 0, 0, 0,
						   NULL, 0, NULL)) {
					perror("disable non-target CRTC");
					drmModeFreeCrtc(other);
					return 1;
				}
			}
			if (other)
				drmModeFreeCrtc(other);
		}
	}

	struct drm_mode_create_dumb cre = { 0 };
	/* The logical frame-packing mode is one eye high. The framebuffer holds
	 * both eyes separated by one ordinary vertical blanking interval:
	 * 1080 + (1125 - 1080) + 1080 = 2205 lines for 1080p24.
	 */
	uint32_t buffer_height = layout == LAYOUT_FP
		? mode->vdisplay + mode->vtotal : mode->vdisplay;
	cre.width = mode->hdisplay; cre.height = buffer_height; cre.bpp = 32;
	if (drmIoctl(fd, DRM_IOCTL_MODE_CREATE_DUMB, &cre)) { perror("dumb create"); return 1; }
	uint32_t fb;
	if (drmModeAddFB(fd, cre.width, cre.height, 24, 32, cre.pitch, cre.handle, &fb)) {
		perror("AddFB"); return 1; }
	struct drm_mode_map_dumb map = { 0 }; map.handle = cre.handle;
	drmIoctl(fd, DRM_IOCTL_MODE_MAP_DUMB, &map);
	uint32_t *px = mmap(0, cre.size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, map.offset);
	if (px == MAP_FAILED) { perror("mmap"); return 1; }

	uint32_t vsif_prop = 0, vsif_blob = 0;
	uint32_t max_bpc_prop = 0;
	if (max_bpc) {
		for (int i = 0; i < conn->count_props && !max_bpc_prop; i++) {
			drmModePropertyPtr pr = drmModeGetProperty(fd, conn->props[i]);
			if (pr) {
				if (!strcmp(pr->name, "max bpc"))
					max_bpc_prop = pr->prop_id;
				drmModeFreeProperty(pr);
			}
		}
		if (!max_bpc_prop) {
			fprintf(stderr, "max bpc property not found on %s\n", want);
			return 1;
		}
		if (drmModeConnectorSetProperty(fd, conn->connector_id,
						max_bpc_prop, max_bpc)) {
			perror("set max bpc");
			return 1;
		}
		printf("requested connector property max bpc=%d\n", max_bpc);
	}

	/* Output encoding and quantization range through the standard
	 * connector properties ("color format" and "Broadcast RGB"), set by
	 * enum name so the same request works on every kernel exposing them.
	 */
	char const *fmt_label = "RGB";
	if (fmt_arg) {
		static const struct { const char *arg, *fmt, *range, *label; } F[] = {
			{ "rgbfull",    "RGB",       "Full",           "RGB FULL" },
			{ "rgblimited", "RGB",       "Limited 16:235", "RGB LIMITED" },
			{ "rgbauto",    "RGB",       "Automatic",      "RGB AUTO" },
			{ "yuv444",     "YUV 4:4:4", "Automatic",      "YUV444" },
			{ "yuv422",     "YUV 4:2:2", "Automatic",      "YUV422" },
		};
		size_t f;

		for (f = 0; f < sizeof(F) / sizeof(F[0]); f++)
			if (!strcmp(fmt_arg, F[f].arg))
				break;
		if (f == sizeof(F) / sizeof(F[0])) {
			fprintf(stderr, "unknown fmt '%s'; use rgbfull, rgblimited, rgbauto, yuv444 or yuv422\n",
				fmt_arg);
			return 2;
		}
		if (set_enum_prop(fd, conn, "Broadcast RGB", F[f].range) ||
		    set_enum_prop(fd, conn, "color format", F[f].fmt))
			return 1;
		fmt_label = F[f].label;
	}
	snprintf(label, sizeof(label), "%s%s %d-BIT",
		 layout == LAYOUT_SBS ? "SBS " : layout == LAYOUT_TAB ? "TAB " :
		 layout == LAYOUT_FP ? "FP " : "", fmt_label, max_bpc ? max_bpc : 8);
	printf("frame label: %s\n", label);
	if (vsif) {
		/* Payload per NV_DRM common ioctl doc: 3-byte HDMI OUI (LSB
		 * first) followed by the VSIF body without its header.
		 * PB4 = extended/3D video format marker (0x2 << 5); PB5 =
		 * 3D_Structure << 4 (CTA-861-H: TaB 6, SBS-half 8); PB6 =
		 * 3D_Ext_Data, 0 = standard horizontal sub-sampling.
		 * HDMI 1.4b requires PB6 only for SBS-half, but send the zero
		 * byte for TaB as well: this Sony KDL-46HX855 ignores the
		 * announcement without it (run 13), the same behaviour behind
		 * the amd-gfx v3 2/3 series on a JVC projector, and the same
		 * choice the DRM core's own VSIF helper makes.
		 */
		uint8_t p[6] = { 0x03, 0x0c, 0x00, 0x2 << 5, 0, 0 };
		const uint32_t plen = 6; /* Ext_Data byte always on, see above */
		p[4] = (layout == LAYOUT_SBS ? 0x8 : 0x6) << 4;
		for (int i = 0; i < conn->count_props && !vsif_prop; i++) {
			drmModePropertyPtr pr = drmModeGetProperty(fd, conn->props[i]);
			if (pr) {
				if (!strcmp(pr->name, "NV_HDMI_VSIF_METADATA"))
					vsif_prop = pr->prop_id;
				drmModeFreeProperty(pr);
			}
		}
		if (!vsif_prop) {
			fprintf(stderr, "NV_HDMI_VSIF_METADATA not found on %s -- not an nvidia-drm connector?\n", want);
			return 1;
		}
		if (drmModeCreatePropertyBlob(fd, p, plen, &vsif_blob)) {
			perror("CreatePropertyBlob vsif"); return 1; }
		if (drmModeConnectorSetProperty(fd, conn->connector_id, vsif_prop, vsif_blob)) {
			perror("set NV_HDMI_VSIF_METADATA"); return 1; }
		printf("injected NV_HDMI_VSIF_METADATA as blob %u (%u bytes:", vsif_blob, plen);
		for (uint32_t i = 0; i < plen; i++)
			printf(" %02x", p[i]);
		printf(")\n");
	}

	if (drmModeSetCrtc(fd, crtc_id, fb, 0, 0, &conn->connector_id, 1, mode)) {
		perror("SetCrtc"); return 1;
	}
	printf("scanout buffer: %ux%u; modeset done%s -- TV should auto-switch now. q/ESC quits.\n",
	       cre.width, cre.height, isolate ? " (isolated)" : "");

	/* the harness fires us under timeout(1): leave the wire clean on TERM */
	signal(SIGTERM, on_term);
	signal(SIGINT, on_term);

	fcntl(STDIN_FILENO, F_SETFL, fcntl(STDIN_FILENO, F_GETFL) | O_NONBLOCK);
	uint32_t stride = cre.pitch / 4;
	memset(px, 0, cre.size); /* includes the frame-packing inter-eye gap */
	for (int frame = 0; !stop_flag; frame++) {
		if (layout == LAYOUT_DEEP12) {
			/* XRGB8888 is intentional here: this first probe tests physical
			 * HDMI link depth, not high-precision scanout. Smooth ramps and
			 * a checker overlay make gross corruption immediately visible.
			 */
			if (!frame) {
				for (uint32_t y = 0; y < mode->vdisplay; y++)
				for (uint32_t x = 0; x < mode->hdisplay; x++) {
					uint32_t r = x * 255 / (mode->hdisplay - 1);
					uint32_t g = y * 255 / (mode->vdisplay - 1);
					uint32_t b = (x + y) * 255 /
						     (mode->hdisplay + mode->vdisplay - 2);
					if (((x / 64) ^ (y / 64)) & 1)
						b = (b + 24) > 255 ? 255 : b + 24;
					px[y * stride + x] = r << 16 | g << 8 | b;
				}
				draw_test_band(px, stride, mode->hdisplay, mode->vdisplay);
				draw_label(px, stride, mode->hdisplay, mode->vdisplay, label);
			}
			char k;
			while (read(STDIN_FILENO, &k, 1) > 0)
				if (k == 'q' || k == 27) goto out;
			struct timespec ts = { 0, 50000000 };
			nanosleep(&ts, NULL);
			continue;
		}

		/* three boxes at disparities -32/0/+32 px: depth on the TV */
		int drift = ((frame >> 2) & 31) - 16;  /* slow horizontal drift */
		for (int eye = 0; eye < 2; eye++) {
			uint32_t x0 = 0, y0 = 0;
			uint32_t eye_w = mode->hdisplay, eye_h = mode->vdisplay;

			if (layout == LAYOUT_SBS) {
				eye_w /= 2;
				x0 = eye ? eye_w : 0;
			} else if (layout == LAYOUT_TAB) {
				eye_h /= 2;
				y0 = eye ? eye_h : 0;
			} else {
				/* The second eye starts after the first eye's active
				 * image and its complete vertical blanking interval.
				 */
				y0 = eye ? mode->vtotal : 0;
			}

			for (uint32_t y = 0; y < eye_h; y++)
			for (uint32_t x = 0; x < eye_w; x++) {
				uint32_t c = ((x / 40 + y / 40) & 1) ? 0x202020u : 0u;
				for (int b = 0; b < 3; b++) {
					int disp = (b - 1) * 32;                    /* -32 0 +32 */
					int shift = drift + (eye ? -1 : 1) * (disp / 2);
					uint32_t bx0 = (uint32_t)(300 + shift);
					/* tiers sized to the eye region: the 720p TaB eye is only
					 * 360 rows tall and run 16 showed the blue box clipped
					 * to a sliver when it ran off the eye bottom */
					uint32_t by0 = eye_h >= 900 ? 180 + b * 240
						     : eye_h >= 500 ? 40 + b * 150
						     : 40 + b * 115;
					uint32_t box_h = eye_h >= 900 ? 160
						       : eye_h >= 500 ? 100 : 60;
					static const uint32_t col[3] = { 0xc02020u, 0x20c020u, 0x2040c0u };
					if (x >= bx0 && x < bx0 + 220 && y >= by0 && y < by0 + box_h)
						c = col[b];
				}
				px[(y0 + y) * stride + x0 + x] = c;
			}
			draw_label(px + y0 * stride + x0, stride, eye_w, eye_h, label);
		}
		char k;
		while (read(STDIN_FILENO, &k, 1) > 0)
			if (k == 'q' || k == 27) goto out;
		struct timespec ts = { 0, 50000000 }; nanosleep(&ts, NULL);
	}
out:
	if (vsif_prop) {
		/* pull the 3D announcement off the wire before the TV sees 2D timing */
		drmModeConnectorSetProperty(fd, conn->connector_id, vsif_prop, 0);
		drmModeDestroyPropertyBlob(fd, vsif_blob);
	}
	if (saved) { drmModeSetCrtc(fd, saved->crtc_id, saved->buffer_id, saved->x,
				      saved->y, &conn->connector_id, 1, &saved->mode);
		     drmModeFreeCrtc(saved); }
	printf("restored\n");
	return 0;
}
