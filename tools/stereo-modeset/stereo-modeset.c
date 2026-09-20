// stereo-modeset: claim a DRM connector in a 3D mode and draw a disparity
// pattern until interrupted. Run from a bare VT as root with no compositor
// running (needs DRM master). This is the smoke test for the amdgpu VSIF patch:
// if the TV auto-switches into 3D when this tool modesets the SBS-half mode,
// the kernel patch is emitting the HDMI vendor-specific infoframe correctly.
//
// cc -o stereo-modeset stereo-modeset.c $(pkg-config --cflags --libs libdrm)
// usage: stereo-modeset [card] [connector]   defaults: /dev/dri/card0 HDMI-A-1
// SPDX-License-Identifier: CC0-1.0

#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

static char const *want_stereo = "side-by-side half";

static char const *stereo_name(uint32_t flags)
{
	switch (flags & DRM_MODE_FLAG_3D_MASK) {
	case DRM_MODE_FLAG_3D_FRAME_PACKING:         return "frame packing";
	case DRM_MODE_FLAG_3D_TOP_AND_BOTTOM:        return "top-and-bottom";
	case DRM_MODE_FLAG_3D_SIDE_BY_SIDE_HALF:     return "side-by-side half";
	default:                                     return NULL;
	}
}

int main(int argc, char **argv)
{
	char const *path = argc > 1 ? argv[1] : "/dev/dri/card0";
	char const *want = argc > 2 ? argv[2] : "HDMI-A-1";

	setvbuf(stdout, NULL, _IOLBF, 0); /* log capture: survive timeout kill */

	int fd = open(path, O_RDWR | O_CLOEXEC);
	if (fd < 0) { perror("open"); return 1; }
	if (drmSetClientCap(fd, DRM_CLIENT_CAP_STEREO_3D, 1) ||
	    drmSetClientCap(fd, DRM_CLIENT_CAP_ASPECT_RATIO, 1)) {
		fprintf(stderr, "client caps refused\n"); return 1;
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
	for (int i = 0; i < conn->count_modes; i++) {
		drmModeModeInfo *m = &conn->modes[i];
		char const *s = stereo_name(m->flags);
		if (s) printf("stereo mode: %-10s %4ux%u @%u %s\n",
			      m->name, m->hdisplay, m->vdisplay, m->vrefresh, s);
		if (!mode && s && !strcmp(s, want_stereo) &&
		    m->hdisplay == 1920 && m->vrefresh >= 59)
			mode = m;
	}
	if (!mode) { fprintf(stderr, "no %s mode on %s -- kernel patch not active?\n",
			     want_stereo, want); return 1; }
	printf("choosing %s @%u (%s)\n", mode->name, mode->vrefresh, want_stereo);

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

	struct drm_mode_create_dumb cre = { 0 };
	cre.width = mode->hdisplay; cre.height = mode->vdisplay; cre.bpp = 32;
	if (drmIoctl(fd, DRM_IOCTL_MODE_CREATE_DUMB, &cre)) { perror("dumb create"); return 1; }
	uint32_t fb;
	if (drmModeAddFB(fd, cre.width, cre.height, 24, 32, cre.pitch, cre.handle, &fb)) {
		perror("AddFB"); return 1; }
	struct drm_mode_map_dumb map = { 0 }; map.handle = cre.handle;
	drmIoctl(fd, DRM_IOCTL_MODE_MAP_DUMB, &map);
	uint32_t *px = mmap(0, cre.size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, map.offset);
	if (px == MAP_FAILED) { perror("mmap"); return 1; }

	if (drmModeSetCrtc(fd, crtc_id, fb, 0, 0, &conn->connector_id, 1, mode)) {
		perror("SetCrtc"); return 1;
	}
	printf("modeset done -- TV should auto-switch now. q/ESC quits.\n");

	fcntl(STDIN_FILENO, F_SETFL, fcntl(STDIN_FILENO, F_GETFL) | O_NONBLOCK);
	uint32_t half = mode->hdisplay / 2, stride = cre.pitch / 4;
	for (int frame = 0;; frame++) {
		/* three boxes at disparities -32/0/+32 px: depth on the TV */
		int drift = ((frame >> 2) & 31) - 16;  /* slow horizontal drift */
		for (uint32_t y = 0; y < mode->vdisplay; y++)
			for (uint32_t x = 0; x < mode->hdisplay; x++) {
				int right = x >= half;
				uint32_t lx = right ? x - half : x;
				uint32_t c = ((lx / 40 + y / 40) & 1) ? 0x202020u : 0u;
				for (int b = 0; b < 3; b++) {
					int disp = (b - 1) * 32;                    /* -32 0 +32 */
					int shift = drift + (right ? -1 : 1) * (disp / 2);
					uint32_t bx0 = (uint32_t)(300 + shift);
					uint32_t by0 = 180 + b * 240;
					static const uint32_t col[3] = { 0xc02020u, 0x20c020u, 0x2040c0u };
					if (lx >= bx0 && lx < bx0 + 220 && y >= by0 && y < by0 + 160)
						c = col[b];
				}
				px[y * stride + x] = c;
			}
		char k;
		while (read(STDIN_FILENO, &k, 1) > 0)
			if (k == 'q' || k == 27) goto out;
		struct timespec ts = { 0, 50000000 }; nanosleep(&ts, NULL);
	}
out:
	if (saved) { drmModeSetCrtc(fd, saved->crtc_id, saved->buffer_id, saved->x,
				      saved->y, &conn->connector_id, 1, &saved->mode);
		     drmModeFreeCrtc(saved); }
	printf("restored\n");
	return 0;
}
