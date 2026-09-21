# stereo-modeset — first unblocked stereo modeset on amdgpu DC

Verdict: **PASS** [proven — Daniel, KDL-46HX855, 2026-09-20 19:26-19:28 UTC-3].

With the two-line-concept kernel patch applied to amdgpu, setting the EDID's
SBS-half 1920x1080@60 mode made the Sony switch itself into 3D — no remote
button — and the disparity pattern was perceived in depth: red and blue boxes
popped out, green sat at screen level. Full record: `run7-pass-2026-09-20.log`
in this directory.

## The kernel patch under test

`linux-source-7.0` (build tree at `/K3D/temp/k317/linux-source-7.0`, Makefile
fudged to SUBLEVEL=10/EXTRAVERSION=+deb14-amd64 so vermagic matches the
running Debian kernel), both changes in
`drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c`:

1. `amdgpu_dm_connector_init_helper`: `stereo_allowed = true` — stops the
   core's mode validation from pruning the EDID's 3D-flagged alternates with
   `MODE_NO_STEREO`.
2. `fill_stream_properties_from_drm_display_mode` (HDMI branch): when the
   mode carries `DRM_MODE_FLAG_3D_*`, pack the already-computed vendor
   infoframe (`hdmi_vendor_infoframe_pack(&hv_frame, ...)`) into
   `stream->hfvsif_infopacket` and set `.valid = true`, so DC's existing
   packet machinery puts the VSIF on the wire. `timing_3d_format` stays NONE
   on purpose — it drives DC's stereo plane-address flip, wrong for a
   userspace-composed SBS buffer.

## Numbers (from the probe inside the same run)

- stock driver: 22 modes with/without `DRM_CLIENT_CAP_STEREO_3D`, 0 stereo.
- patched driver: 51 modes with the cap set, **29 stereo-flagged**; ASPECT
  pass unchanged (30, aspect duplicates only).

## Run history — five failures before the patch ever executed

1. vermagic precheck tripped on modinfo's trailing space (nothing tested).
2. `modprobe -r amdgpu` refused: Plasma held DRM fds and fbcon bound the GPU
   (fixed: terminate user session, wait fds, unbind vtcon1).
3. `/tmp` is wiped at boot; build tree vanished (fixed: `/K3D/temp/k317`).
4. `insmod: Unknown symbol in module` — `modprobe -r` removes the whole unused
   16-module dependency chain and bare insmod resolves nothing. Script kept
   going driverless, leaving an alive-but-pictureless box (hard reset).
   That reset, inside `/K3D`'s `commit=600` ext4 window, zeroed the just-built
   `.ko` and ate its debug copy (fixed: preload deps, self-restore on any
   failure, sync after builds).
5. vermagic precheck correctly refused the zeroed module (nothing tested).
6. Aggregate `modprobe $DEPS` exited silently yet the helper modules
   (`gpu_sched`, `drm_buddy`, `amdxcp`, `drm_exec`) were absent at insmod —
   `Unknown symbol ... (err -2)` in kern.log. Restore path worked; back to
   desktop with no reboot.
7. Per-module verify loop against `/proc/modules` loaded all 16 (`loaded ok`
   each), insmod succeeded, probe printed 29 stereo modes, modeset picked
   SBS-half 1080p60, **TV auto-switched to 3D for 90s**, desktop returned.

## What this unlocks

- The upstream contribution: amdgpu DC is the only major DRM driver that
  hard-denies stereo (`stereo_allowed = false`); i915 and vc4 allow it,
  nouveau allows it and already wires the VSIF on commit. This patch is the
  minimal delta to join them, with a real consumer verified (KDL-46HX855,
  EDID-advertised SBS/TaB/FP).
- Next ports per project direction: verify nouveau's path on the GTX card,
  and carry the flag+VSIF wiring to nvidia-drm (NVIDIA/open-gpu-kernel-modules,
  which never contained stereo handling — 3D Vision was retired in 2019,
  before the 2022 open-sourcing).

Tools here: `stereo-modeset.c` (bare-VT DRM client: sets caps, selects
`sbs`, `tab` or `fp`, and draws three drifting boxes at disparities
-32/0/+32), `run-3d-test.sh` (detached systemd-run harness that swaps the
module, runs probe + modeset, and always restores the desktop), and
`run-nouveau-test.sh` (the equivalent stock-nouveau reference run).

## Layout selector and frame-packing geometry

The third `stereo-modeset` argument is optional and defaults to `sbs`:

```
stereo-modeset /dev/dri/cardN HDMI-A-N sbs
stereo-modeset /dev/dri/cardN HDMI-A-N tab
stereo-modeset /dev/dri/cardN HDMI-A-N fp
```

`sbs` selects 1920x1080 side-by-side-half at 60 Hz and puts one scaled eye
in each 960-pixel half. `tab` selects 1920x1080 top-and-bottom at 60 Hz and
puts one scaled eye in each 540-line half.

`fp` prefers the exact 1920x1080@24 frame-packing mode. DRM describes that
mode in per-eye terms, so its public `vdisplay` is still 1080. The scanout
buffer must contain both eyes and the vertical blanking interval between
them: `vdisplay + vtotal`, which is 1080 + 1125 = 2205 lines for this CEA
mode. The test draws the left eye at line 0, leaves lines 1080-1124 blank,
and starts the right eye at line 1125. This follows DRM's own
`CRTC_STEREO_DOUBLE` transformation and nouveau's input-height handling.

Frame packing is a stronger driver test than SBS/TaB. The already-proven
amdgpu patch exposes the mode and emits its HDMI VSIF, but deliberately
leaves `timing_3d_format` unset; consequently it does not yet ask DC to
double the link timing. Nouveau and i915 do apply DRM's stereo timing
transformation. Run nouveau first as the positive control:

```
sudo systemd-run --unit=nouveau-3d-test --collect sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nouveau-test.sh fp
```

Until that run is visually confirmed, frame packing remains [qualified].
The SBS-half result above remains [proven]. The implementation analysis is
in `../../docs/dual-surface-hdmi-3d.md`.
