// Read-only probe: does the kernel expose HDMI 3D stereo modes for a connector
// when a client sets DRM_CLIENT_CAP_STEREO_3D?
//
// Enumerates modes twice on the same card, once without the capability and once
// with it, and reports the difference. Performs no modeset and takes no DRM
// master, so it is safe to run under a live compositor.
//
// cc -o stereo-probe stereo-probe.c $(pkg-config --cflags --libs libdrm)
// SPDX-License-Identifier: CC0-1.0

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

static char const *stereo_name(unsigned flags)
{
	switch (flags & DRM_MODE_FLAG_3D_MASK) {
	case DRM_MODE_FLAG_3D_NONE:                  return NULL;
	case DRM_MODE_FLAG_3D_FRAME_PACKING:         return "frame packing";
	case DRM_MODE_FLAG_3D_FIELD_ALTERNATIVE:     return "field alternative";
	case DRM_MODE_FLAG_3D_LINE_ALTERNATIVE:      return "line alternative";
	case DRM_MODE_FLAG_3D_SIDE_BY_SIDE_FULL:     return "side-by-side full";
	case DRM_MODE_FLAG_3D_L_DEPTH:               return "L + depth";
	case DRM_MODE_FLAG_3D_L_DEPTH_GFX_GFX_DEPTH: return "L + depth + gfx";
	case DRM_MODE_FLAG_3D_TOP_AND_BOTTOM:        return "top-and-bottom";
	case DRM_MODE_FLAG_3D_SIDE_BY_SIDE_HALF:     return "side-by-side half";
	default:                                     return "unknown";
	}
}

static int count_modes(char const *path, char const *want, int caps, int list)
{
	int fd = open(path, O_RDWR | O_CLOEXEC);
	if (fd < 0) {
		fprintf(stderr, "open %s: %s\n", path, strerror(errno));
		return -1;
	}

	if (caps) {
		static const struct { uint64_t cap; char const *name; } c[] = {
			{ DRM_CLIENT_CAP_STEREO_3D, "STEREO_3D" },
			{ DRM_CLIENT_CAP_ASPECT_RATIO, "ASPECT_RATIO" },
		};
		for (unsigned k = 0; k < sizeof c / sizeof *c; k++) {
			if (!(caps & (1 << k))) continue;
			int rc = drmSetClientCap(fd, c[k].cap, 1);
			printf("  drmSetClientCap(%s, 1) -> %d%s\n", c[k].name,
			       rc, rc == 0 ? " (accepted)" : " (REFUSED)");
			if (rc != 0) { close(fd); return -1; }
		}
	}

	drmModeRes *res = drmModeGetResources(fd);
	if (!res) { fprintf(stderr, "  drmModeGetResources failed\n"); close(fd); return -1; }

	int total = 0, stereo_modes = 0;
	for (int i = 0; i < res->count_connectors; i++) {
		drmModeConnector *c = drmModeGetConnector(fd, res->connectors[i]);
		if (!c) continue;

		char name[64];
		snprintf(name, sizeof name, "%s-%u",
		         drmModeGetConnectorTypeName(c->connector_type), c->connector_type_id);

		if (want && strcmp(name, want) != 0) { drmModeFreeConnector(c); continue; }

		total += c->count_modes;
		for (int m = 0; m < c->count_modes; m++) {
			char const *s = stereo_name(c->modes[m].flags);
			if (s) stereo_modes++;
			if (list) {
				char fl[96] = "";
				unsigned f = c->modes[m].flags;
				if (f & DRM_MODE_FLAG_INTERLACE) strcat(fl, "interlace ");
				if (f & DRM_MODE_FLAG_DBLSCAN) strcat(fl, "dblscan ");
				if (f & DRM_MODE_FLAG_DBLCLK) strcat(fl, "dblclk ");
				if (s) { strcat(fl, s); strcat(fl, " "); }
				printf("    %-14s %4ux%-4u @%3u Hz clk=%6u flags=%#08x %s\n",
				       name, c->modes[m].hdisplay, c->modes[m].vdisplay,
				       c->modes[m].vrefresh, c->modes[m].clock, f, fl);
			}
		}
		drmModeFreeConnector(c);
	}

	drmModeFreeResources(res);
	close(fd);
	printf("  modes on %s: %d total, %d stereo\n", want ? want : "(all)", total, stereo_modes);
	return total;
}

int main(int argc, char **argv)
{
	char const *path = argc > 1 ? argv[1] : "/dev/dri/card0";
	char const *want = argc > 2 ? argv[2] : "HDMI-A-1";

	printf("probe: %s connector %s\n\n", path, want);
	printf("without caps:\n");
	int a = count_modes(path, want, 0, 0);
	printf("\nwith STEREO_3D:\n");
	int b = count_modes(path, want, 1, 0);
	printf("\nwith ASPECT_RATIO:\n");
	int c = count_modes(path, want, 2, 1);
	printf("\nwith STEREO_3D|ASPECT_RATIO:\n");
	int d = count_modes(path, want, 3, 1);

	printf("\nverdict: ");
	if (a < 0 || b < 0 || c < 0 || d < 0)	printf("probe failed\n");
	else if (b > a || d > c)
		printf("the kernel DOES expose stereo mode(s) on request\n");
	else
		printf("no stereo modes appeared even with the capability set\n");
	printf("(counts: none=%d stereo=%d aspect=%d both=%d)\n", a, b, c, d);
	return 0;
}
