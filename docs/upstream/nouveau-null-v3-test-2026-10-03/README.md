# Test of Jim Cromie's nouveau NULL-dereference series, 2026-10-03

The series: "[PATCH 0/3] nouveau: fix 3 null-ptr derefs", 2026-10-02 ([lore](https://lore.kernel.org/nouveau/20261002-my-fixups-v1-0-a83d20f9d3fe@gmail.com/)).
Tested kernel: 7.3.0-rc1 with patches 1/3 and 2/3, branch [`pkg6-jim-null-v3`](https://github.com/danielcamposramos/linux/tree/pkg6-jim-null-v3) (9ee31760a775). Patch 3/3 does not apply on 7.3-rc1 (`nvkm_gsp_gcx_ready()` is not there yet) and is untested.
Hardware: NVIDIA RTX 3060 (GA106) passed through with vfio-pci to a QEMU/KVM guest running that kernel; a Sony KDL-46EX725 3D TV on the card's HDMI port for the with-firmware run.

## Without firmware

The whole `nvidia/ga106` firmware folder was removed and the initramfs rebuilt ([dmesg-no-firmware-boot.txt](dmesg-no-firmware-boot.txt)):

```
nouveau 0000:00:05.0: acr: firmware unavailable
nouveau 0000:00:05.0: gr: firmware unavailable
nouveau 0000:00:05.0: sec2: firmware unavailable
nouveau 0000:00:05.0: DRM: GETPARAM_GRAPH_UNITS: no gr engine or func
```

The last line is patch 1/3's path, reached by the desktop session at boot. No oops in the log.

Both ioctls called directly on the render node with [nouveau-ioctl-probe.c](nouveau-ioctl-probe.c) ([output](ioctl-probe-output.txt)):

```
GETPARAM_GRAPH_UNITS: ret=-1 errno=19 (No such device) value=0x0
GET_ZCULL_INFO: ret=-1 errno=25 (Inappropriate ioctl for device)
```

`-ENOTTY` is patch 2/3's return when there is no GR engine. No kernel messages and no oops during the calls. KWin composited; Vulkan (`vulkaninfo`) listed no NVK device, and GL (`eglinfo`) fell back to llvmpipe after zink found no device.

A first pass renamed only the GSP firmware link: nouveau then used its own Ampere path with the ACR/GR/SEC2 firmware, so the GR engine came up and NVK and zink gave a GL 4.6 device, also with no oops ([dmesg-gsp-link-only.txt](dmesg-gsp-link-only.txt)).

## With firmware

The folder restored: `gsp: RM version: 570.144`, no oops over the session ([dmesg-with-firmware-3d-modes.txt](dmesg-with-firmware-3d-modes.txt), [dmesg-with-firmware-720p60-fp.txt](dmesg-with-firmware-720p60-fp.txt)). The EX725's HDMI 1.4 3D modes, set with `kscreen-doctor` and read on the TV's own Display key: top and bottom 1080p60, side by side 1080p60, frame packing 1080p24 and 720p60, each engaged by the TV itself at 12 bits per component. nouveau's `link_config` reported 12 bpc (36 bpp) in every mode; frame packing 1080p24 and 720p60 run a 148.5 MHz pixel clock, 222.75 MHz TMDS at 12 bpc, under the TV's 225 MHz limit.

Done by Daniel Ramos, with an AI assistant doing the legwork under his direction; the TV readings are his.

**Sent:** the Tested-by for 1/3 and 2/3, with this folder linked, as a reply to the cover letter on the nouveau, dri-devel and linux-kernel lists, 2026-10-03 18:20 -03 (Message-ID `20261003212010.113714-1-Capitain_Jack@yahoo.com`).
