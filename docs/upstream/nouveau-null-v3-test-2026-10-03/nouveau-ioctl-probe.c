// SPDX-License-Identifier: MIT
/* Calls the two nouveau ioctls Jim Cromie's v3 1/3 and 2/3 harden, on a GPU with no GR
 * engine (no firmware): each must return an error, and the kernel must not oops. */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <drm/drm.h>
#include <drm/nouveau_drm.h>

int main(int argc, char **argv)
{
	const char *node = argc > 1 ? argv[1] : "/dev/dri/renderD129";
	int fd = open(node, O_RDWR | O_CLOEXEC);
	if (fd < 0) { printf("open %s: %s\n", node, strerror(errno)); return 2; }

	struct drm_nouveau_getparam gp = { .param = NOUVEAU_GETPARAM_GRAPH_UNITS };
	int r = ioctl(fd, DRM_IOCTL_NOUVEAU_GETPARAM, &gp);
	printf("GETPARAM_GRAPH_UNITS: ret=%d errno=%d (%s) value=0x%llx\n", r, r ? errno : 0,
	       r ? strerror(errno) : "ok", (unsigned long long)gp.value);

	struct drm_nouveau_get_zcull_info zi;
	memset(&zi, 0, sizeof(zi));
	r = ioctl(fd, DRM_IOCTL_NOUVEAU_GET_ZCULL_INFO, &zi);
	printf("GET_ZCULL_INFO: ret=%d errno=%d (%s)\n", r, r ? errno : 0, r ? strerror(errno) : "ok");
	close(fd);
	return 0;
}
