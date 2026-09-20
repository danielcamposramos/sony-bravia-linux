# stereo-kms-probe — evidence record

Question answered here: on a 2011/2012-vintage Sony BRAVIA whose EDID declares HDMI 1.4
3D (side-by-side half, top-and-bottom, frame packing), can the Linux display stack on this
host modeset a stereo mode at all — and if not, which layer drops it?

## Result [proven] (2026-09-20, kernel 7.0.10+deb14-amd64, Wayland, amdgpu iGPU)

**No. The kernel driver prunes every stereo mode at probe time, before any userspace
capability is consulted.** On amdgpu nothing above the driver (SDL, KWin, wlroots, gamescope)
has a stereo mode it could even request.

## The EDID (what should exist)

`/sys/class/drm/card0-HDMI-A-1/edid` connected to the KDL-46HX855 decodes (edid-decode) as:

- `3D present`, with a 3D-capable-VIC bitmask covering VICs 31, 16, 20, 5, 19, 4, 32
  → side-by-side half horizontal + top-and-bottom on all seven
- Specific structure fields: **frame packing on VICs 20, 5, 34, 60, 62**
  (1080i50, 1080i60, 1080p30, 720p24, 720p30), plus top-and-bottom on VIC 34

Both GPUs and both OSes on this host read this EDID and report the set as 3D-capable
(owner-verified fact). The EDID path is healthy end to end.

## The kernel-side mechanism (linux 7.0 source, reads verified in-tree)

1. `drm_edid.c` creates stereo modes unconditionally for any EDID with an HDMI VSDB:
   `add_alternate_cea_modes()` is called from the main EDID parse at :6970; it copies CEA
   modes and OR's `DRM_MODE_FLAG_3D_*` per the VSDB declarations, plus a hardcoded legacy
   alternate table (:4688-4696). The modes ARE born.
2. At probe validation (`__drm_helper_update_and_validate`,
   `drm_probe_helper.c:456-461`), the allowed flag set is built from connector caps;
   `drm_mode_validate_flag` (:71-86) marks any 3D mode `MODE_NO_STEREO` unless
   `connector->stereo_allowed` — pruned and destroyed.
3. The ioctl-side filter `drm_mode_expose_to_userspace()` (`drm_connector.c:3283`)
   hides stereo modes from clients without `DRM_CLIENT_CAP_STEREO_3D`, and hides
   aspect-ratio duplicates from clients without `DRM_CLIENT_CAP_ASPECT_RATIO`.
4. sysfs `/sys/class/drm/cardN-X/modes` (`drm_sysfs.c:279 modes_show`) prints
   `connector->modes` **raw** — no filters at all.

## Who allows stereo (tree-wide grep, linux 7.0)

| driver | line | stereo_allowed |
|---|---|---|
| i915 | intel_hdmi.c:3097 | = true (all HDMI) |
| nouveau (≥G92, incl. GSP) | nouveau_connector.c:1420 | = true (DP/eDP/HDMI) |
| vc4 (RPi) | vc4_hdmi.c:589 | = 1 |
| **amdgpu DC** | **amdgpu_dm.c:8975** | **= false — hard deny** |
| nvidia-drm 615.71.09 (kernel-open = proprietary branch, same source) | — | never set (default false) |

amdgpu's connector init also sets `interlace_allowed = false` and
`doublescan_allowed = false` — note in passing: this is why the probe's userspace list
contains no `1080i` entries at all even though the EDID carries 1080i50 (DTD5 + VIC 20)
and 1080i60 (VIC 5); they die at `MODE_NO_INTERLACE` the same way.

No `DRM_MODE_FLAG_3D_*`/frame-packing handling exists anywhere in nvidia-drm or
nvidia-modeset. Under X11 the NVIDIA X server bypasses DRM connector mode lists entirely
(its own EDID/metamode layer knows the HDMI 1.4 3D VICs), which is why the owner has seen
this television auto-enable 3D from an EDID mode on the NVIDIA card under X11 — while the
KMS arm of the same driver cannot expose those modes. [proven for X11 by owner's prior
run; mechanism inferred from source]

## The probe (this directory)

`stereo-probe.c` — read-only libdrm probe; performs no modesetting, takes no DRM master,
safe under a live compositor. Counts and lists modes per connector under four capability
combinations. Build:

```
cc -Wall -o stereo-probe stereo-probe.c $(pkg-config --cflags --libs libdrm)
```

Run: `./stereo-probe /dev/dri/card0 HDMI-A-1`

Measured on 2026-09-20, KDL-46HX855 on amdgpu card0-HDMI-A-1:

```
without caps:               22 total, 0 stereo
STEREO_3D (accepted):       22 total, 0 stereo
ASPECT_RATIO (accepted):    30 total, 0 stereo
STEREO|ASPECT (accepted):   30 total, 0 stereo
sysfs modes:                30
```

The 8-mode sysfs-vs-userspace discrepancy that started the count chase resolves to
aspect-ratio duplicates hidden by `drm_mode_expose_to_userspace` (4:3 vs 16:9 variants of
the same timing — the EDID offers SD VICs in both aspects). Not stereo, not a bug.

## Consequences for the campaign

- The desktop stack (SDL / X11 toolkits / KWin / wlroots / gamescope) is off the hook on
  this host: there is nothing for it to request. Filing compositor bugs against this
  hardware/driver combo would be wrong.
- The concrete upstream target is **amdgpu DC**: it is the only in-tree driver that
  explicitly denies stereo; making `stereo_allowed` conditional on a DC path that can
  actually program HDMI 1.4 frame packing (link timing doubling + VSIF 3D_Structure) is
  the feature. nvKMS is a second, parallel gap (never sets the flag).
- Counter-demo platforms that already pass the whole chain: i915 and vc4. The Raspberry Pi
  frame-packing demos of the last decade are vc4's `stereo_allowed = 1` doing exactly this.

## Pending verification branches

- Cable moved to card1 (NVIDIA KMS, Wayland): predict identical 0-stereo result (flag
  never set). Run the probe there when convenient — one command, one line of truth.
- Intel i915 machine or RPi on this TV: predict stereo modes appear with the cap set;
  that run would demonstrate the EDID→VSIF chain end-to-end on Linux and give the
  campaign its positive control.
