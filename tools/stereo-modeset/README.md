# stereo-modeset — first unblocked stereo modeset on amdgpu DC

SBS-half verdict: **PASS** [proven — Daniel, KDL-46HX855, amdgpu,
2026-09-20 19:26-19:28 UTC-3].

Frame-packing verdict: **PASS** [proven — Daniel, KDL-46HX855, nouveau on
GA106, 2026-09-20 21:37-21:39 UTC-3]. The TV auto-entered 3D through the
NVIDIA GPU's separate HDMI cable/input while the tool scanned a 1920x2205
two-eye framebuffer in the logical 1920x1080@24 frame-packing mode. Full
record: `run5-nouveau-frame-packing-pass-2026-09-20.log`.

amdgpu frame-packing verdict: **PASS** [proven — Daniel, KDL-46HX855,
patched amdgpu with the frame-packing timing patch, 2026-09-20
23:24-23:26 UTC-3]. Same logical 1920x1080@24 mode, same 1920x2205 two-eye
buffer as the nouveau control, TV auto-entered 3D and this time the
disparity picture was visible through the AMD HDMI link. Run 10 was fully
isolated: the harness removed only `nvidia_drm` (CUDA containers stayed
alive) and the modesetter blanked the non-target CRTC, so the result is
attributable to the AMD link alone. Full record:
`run10-amdgpu-frame-packing-pass-2026-09-20.log`. The boundary run that
motivated the fix (signal pass, black picture, run 8
21:43-21:45 UTC-3, record `run8-amdgpu-frame-packing-signal-pass-image-fail-2026-09-20.log`)
showed the same sink entering 3D on a usable FP VSIF while DC scanned the
frame with un-expanded 1080-line timing.

Upstream v3-as-posted verdict: **PASS** on all three layouts [proven —
Daniel, KDL-46HX855, Adrian Betschart's amd-gfx v3 series built into a
7.3-rc4 kernel, 2026-09-21 12:14-12:19 UTC-3]. The series was applied
verbatim to the 7.3-rc4 tarball, booted one-shot via dpkg, and driven by
the harness's kernel-under-test mode (no module swap). The probe numbers
are identical to the 7.0 port's (22 modes/0 stereo without the cap, 51/29
with it), and in a single desktop-down window the television auto-entered
3D and displayed the disparity picture for top-and-bottom 1920x1080@60
(the layout patch 2/3's 3D_Ext_Data byte serves), side-by-side-half
1920x1080@60, and frame packing 1920x1080@24 with the 1920x2205 packed
buffer (patch 3/3's stream sizing). Full record:
`run11-betschart-v3-7.3rc4-all-pass-2026-09-21.log`.

That run also exposed a useful multi-link result. The NVIDIA cable was on a
second HDMI input of the same television, not a second screen. Switching
between the TV's inputs during the AMD window showed both inputs in 3D: AMD
black, NVIDIA with only the lower portion of the image. The AMD process only
committed `card0/HDMI-A-1`; NVIDIA had retained/reasserted the preceding
frame-packing state. [proven] Both independent HDMI links can put the sink in
3D. [qualified] Driving the EX725 and HX855 simultaneously from the two GPUs
is the logical next use, but has not yet been run on two physical sets.

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

The same client and nouveau transaction now also stage the HDMI deep-colour
probe. `deep12` selects ordinary 1920x1080p60, requests the connector's
`max bpc=12`, and displays a deterministic corruption-visible ramp. `sbs12`,
`tab12`, and `fp12` retain nouveau's already-proven 3D modes and VSIF/timing
path while requesting the same 12-bpc link. These combined modes must follow a
successful `deep12` run; they test packet coexistence rather than replacing
the 3D implementation. The custom module defaults to
`/K3D/temp/k317/nouveau-hdmi-deep-colour-experimental.ko`, and the harness
refuses a vermagic or fixed-EDID mismatch before modesetting.

The HX855's two occupied inputs have input-specific HDMI physical addresses,
so their complete EDID hashes differ even though their declared display
capabilities do not. AMD/input 1.0.0.0 is `fbe6a3b4…eadc`; NVIDIA/input
3.0.0.0—the nouveau test target—is `4f6cc1c8…5dc9`. The harness gates on the
latter rather than treating the control input's hash as universal.

After the dual-input observation, the AMD harness was tightened for future
one-at-a-time work: it removes only `nvidia_drm` while leaving the NVIDIA CUDA
stack and containers running, and invokes the modesetter with `isolate` so
all non-target AMD CRTCs are blanked. It restores `nvidia_drm` before SDDM.

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
transformation. The nouveau positive control was run with:

```
sudo systemd-run --unit=nouveau-3d-test --collect sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nouveau-test.sh fp
```

The run is [proven] by both the captured mode/scanout log and Daniel's visual
confirmation on the NVIDIA-connected TV input. The implementation analysis
and the remaining amdgpu boundary are in
`../../docs/dual-surface-hdmi-3d.md`.

The amdgpu FP fix is proven as module
`/K3D/temp/k317/amdgpu-fp-experimental.ko` (name kept from its staging; the
behavior is no longer experimental). It applies DRM's
`CRTC_STEREO_DOUBLE` transform to the local DC stream mode and uses
`drm_mode_get_hv_timing()` for the stream rectangle, so DC receives
1920/2750 horizontal active/total, 2205/2250 vertical active/total and
148.5 MHz while retaining one userspace-packed plane. It deliberately leaves
DC's `timing_3d_format` and `view_format` unset to avoid the dormant stereo
plane-address path. The incremental source patch is
`../../docs/upstream/amdgpu-dc-hdmi-frame-packing.patch`,
[proven, hardware] by run 10. The AMD harness automatically selects it only
for `fp`; `sbs` and `tab` keep using the preserved known-good module.
