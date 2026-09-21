// stereo-modeset: claim a DRM connector in a 3D mode and draw a disparity
// pattern until interrupted. Run from a bare VT as root with no compositor
// running (needs DRM master). This is the smoke test for the amdgpu VSIF patch:
// if the TV auto-switches into 3D when this tool modesets a stereo mode,
// the kernel patch is emitting the HDMI vendor-specific infoframe correctly.
//
// cc -o stereo-modeset stereo-modeset.c $(pkg-config --cflags --libs libdrm)
// usage: stereo-modeset [card] [connector] [sbs|tab|fp] [isolate] [vsif] [720p|hz24]
// defaults: /dev/dri/card0 HDMI-A-1 sbs
// 720p: pick the 1280x720@60 variant instead of 1080p60 (sbs/tab only)
// hz24: pick the 1920x1080@24 variant instead of 60 Hz (sbs/tab only)
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
	} else {
		return -1;
	}
	return 0;
}

static uint32_t pref_w = 1920, pref_h = 1080, pref_hz = 60;

static int mode_score(drmModeModeInfo const *mode, enum stereo_layout layout,
		      uint32_t flag)
{
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

int main(int argc, char **argv)
{
	char const *path = argc > 1 ? argv[1] : "/dev/dri/card0";
	char const *want = argc > 2 ? argv[2] : "HDMI-A-1";
	char const *layout_arg = argc > 3 ? argv[3] : "sbs";
	int isolate = 0, vsif = 0;
	char const *want_stereo;
	enum stereo_layout layout;
	uint32_t want_flag;

	if (parse_layout(layout_arg, &layout, &want_stereo, &want_flag)) {
		fprintf(stderr, "unknown layout '%s'; use sbs, tab, or fp\n",
			layout_arg);
		return 2;
	}
	for (int i = 4; i < argc; i++) {
		if (!strcmp(argv[i], "isolate"))
			isolate = 1;
		else if (!strcmp(argv[i], "vsif"))
			vsif = 1;
		else if (!strcmp(argv[i], "720p")) {
			pref_w = 1280; pref_h = 720;
		} else if (!strcmp(argv[i], "hz24"))
			pref_hz = 24;
		else {
			fprintf(stderr, "unknown option '%s'; use isolate, vsif, 720p and/or hz24\n",
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
					uint32_t by0 = eye_h >= 900 ? 180 + b * 240 : 40 + b * 150;
					uint32_t box_h = eye_h >= 900 ? 160 : 100;
					static const uint32_t col[3] = { 0xc02020u, 0x20c020u, 0x2040c0u };
					if (x >= bx0 && x < bx0 + 220 && y >= by0 && y < by0 + box_h)
						c = col[b];
				}
				px[(y0 + y) * stride + x0 + x] = c;
			}
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
