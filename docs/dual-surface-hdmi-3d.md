# Dual eye surfaces to HDMI 3D

Status: implementation analysis completed 2026-09-20; nouveau frame-packing
hardware run passed on the KDL-46HX855 at 21:37-21:39 UTC-3; the first
amdgpu run passed automatic 3D signaling but produced a black picture; the
staged DC timing fix then passed end to end at 23:24-23:26 UTC-3 with the
disparity picture visible through the AMD link (run 10).

This note answers three connected questions: why the minimal amdgpu patch can
prove SBS-half but is not yet a complete frame-packing implementation; whether
two eye surfaces such as an OpenXR compositor receives can be carried to a 3D
television; and what the Android boxes already prove about the path.

## The conclusion

[proven] Two eye surfaces can be packed into the formats these televisions
accept. The operation is already implemented in the open wiz3D/iZ3D code:
`OutputMethods/SideBySideOutput/Output_dx9.cpp` fetches separate left and right
backbuffers and copies them into the two halves of one primary surface;
the DX10 path uses horizontal and vertical packing shaders. This is the same
composition step a Linux compositor would perform on OpenXR eye images.

[proven] SBS-half and top-and-bottom fit inside an ordinary 1920x1080 scanout.
The compositor scales the eye images to 960x1080 or 1920x540, respectively,
then requests the matching DRM stereo mode so the HDMI VSIF tells the sink how
to interpret those pixels. The patched amdgpu path has already done this end
to end for SBS-half on the KDL-46HX855.

[proven, source audit] Full frame packing uses a different scanout and link
timing. A 1920x1080@24 DRM mode is expressed in per-eye terms. Its framebuffer
holds 1080 left-eye lines, the ordinary 45-line vertical blanking interval,
and 1080 right-eye lines: 2205 lines total. DRM's `CRTC_STEREO_DOUBLE`
transformation doubles the pixel clock, adds the original vertical total to
`crtc_vdisplay`, and doubles `crtc_vtotal`. Nouveau applies this transformation
and explicitly sets its input height to `vdisplay + vtotal`; i915 applies the
same DRM helper.

[proven, hardware] The stock nouveau path on the GA106 then completed that
chain on the NVIDIA GPU's own HDMI cable and BRAVIA input. The tool selected
the exact logical 1920x1080@24 frame-packing mode, allocated 1920x2205,
and the television entered 3D automatically with the disparity pattern
visible in depth. The harness restored the stock NVIDIA stack, desktop,
daemons and all five containers. The captured record is
`../tools/stereo-modeset/run5-nouveau-frame-packing-pass-2026-09-20.log`.

[proven, source audit] amdgpu DC has substantial stereo machinery. It defines
`VIEW_3D_FORMAT_SIDE_BY_SIDE`, `VIEW_3D_FORMAT_TOP_AND_BOTTOM`,
`TIMING_3D_FORMAT_HW_FRAME_PACKING` and software-packed variants. Its resource
code adjusts scaler geometry for SBS/TaB, its display-mode calculations account
for the doubled frame-packing clock, its OPP code programs 3D active-space
registers, and its info-packet module can build stereo packets from those
fields.

[proven, source audit] The Linux amdgpu glue does not connect DRM's stereo flags
to that DC machinery. `fill_stream_properties_from_drm_display_mode()` assigns
`TIMING_3D_FORMAT_NONE`, and no later mapping turns a
`DRM_MODE_FLAG_3D_FRAME_PACKING` mode into DC frame-packing timing. The project
patch intentionally leaves that assignment alone and adds the smaller missing
pieces: allow the EDID modes through validation and emit the already-computed
HDMI VSIF. That is sufficient for userspace-packed SBS/TaB. It is insufficient
for full frame-packing link timing.

[inferred] AMD therefore does not face a fundamental “cannot compose two
eyes” barrier. The immediate Linux gap is the missing DRM-to-DC translation
and validation work needed to activate dormant DC stereo paths safely. A
complete patch needs to map each DRM stereo layout to the correct DC timing
and view format, use the corresponding adjusted timing, validate bandwidth
and plane geometry, and prove it on real generations. The current minimal
patch should remain scoped to the SBS/TaB behavior it has actually proven.

[proven, hardware] With the same logical 1920x1080@24 mode and 1920x2205
userspace buffer as the nouveau positive control, patched amdgpu made the
BRAVIA enter 3D automatically but displayed black. This separates the two
halves experimentally: mode exposure and HDMI FP signaling work, while usable
frame-packed scanout does not. Record:
`../tools/stereo-modeset/run8-amdgpu-frame-packing-signal-pass-image-fail-2026-09-20.log`.

[proven, source audit] The black result has a concrete geometry boundary.
DRM's legacy SetCrtc path calls `drm_mode_get_hv_timing()`, so the primary
plane presented to amdgpu is 1920x2205. amdgpu creates the DC stream from the
unadjusted requested mode, however, and its CRTC `mode_fixup()` is a no-op.
DC therefore receives a 1920x1080 stream at 74.25 MHz while its plane is 2205
lines high. This is the mismatch the nouveau path avoids with
`CRTC_STEREO_DOUBLE`.

[proven, hardware — run 10, 2026-09-20 23:24-23:26 UTC-3, isolated to the
AMD link] The experiment (staged at the time of the analysis, since proven) treats FP
as one userspace-packed surface throughout. It applies
`drm_mode_set_crtcinfo(..., CRTC_STEREO_DOUBLE)` to amdgpu's local stream mode
and derives the stream rectangle with `drm_mode_get_hv_timing()`. For the
chosen mode DC then receives horizontal active/total 1920/2750, vertical
active/total 2205/2250 and a 148.5 MHz pixel clock. It deliberately keeps
`timing_3d_format` and `view_format` at NONE, avoiding DC's dormant stereo
address-flip path; the already-proven custom VSIF continues to identify the
ordinary expanded scanout as HDMI frame packing. The incremental patch is
`upstream/amdgpu-dc-hdmi-frame-packing.patch`.

## Two links, one sink, and the two-TV direction

[proven by owner observation] The AMD and NVIDIA cables were connected to two
HDMI inputs of the same BRAVIA. During the AMD test window, switching the TV
between those inputs showed both input paths in 3D. AMD showed black; NVIDIA
showed only the lower portion of its retained frame. The test process itself
opened only AMD `card0/HDMI-A-1`, so this was not one atomic commit spanning
two GPUs. NVIDIA had retained or reasserted the earlier nouveau frame-packing
state through its own link.

The important architectural result is that the standard HDMI 3D signal works
independently on both GPU links. [inferred] Once each scanout path is mastered,
the same arrangement can terminate one GPU at the EX725 and the other at the
HX855, giving two simultaneous 3D displays. That two-physical-TV arrangement
has not yet been run, so it remains [qualified].

For the next debugging passes, the AMD harness explicitly removes the
`nvidia_drm` display leaf while leaving `nvidia`, `nvidia_uvm`, CUDA and the
containers running. The modesetter's `isolate` option blanks non-target CRTCs
on the selected GPU. This makes each result attributable to exactly one HDMI
link; the dual-output path can be re-enabled deliberately after both links
have correct buffers.

### Render cost of two outputs

The HDMI VSIF is connector metadata and is cheap to emit on two links. It does
not require rendering the 3D scene again. The expensive boundary is whether
the two sinks can consume the same packed pixels.

The preferred EX725+HX855 path is one common mode: same stereo layout,
resolution, refresh rate and eye order. Render the left/right eye pair once,
pack it once, and present that result on both connectors. Because the outputs
belong to different GPUs, the implementation may need DMA-BUF sharing or a
cross-device copy; that cost is still below a second game render.

If the two sinks need different layouts or timings, each needs its own final
packing/composition pass, for example FP for one and SBS-half for the other.
That is heavier, but it still should reuse the same rendered eye textures
rather than render the scene twice. Common-mode negotiation is therefore a
performance requirement for the first dual-TV implementation, not just a
convenience.

## What a Linux TV-3D output backend would do

A compositor target for gamescope, Monado or another OpenXR-capable component
would receive the two final eye images and select one of three presentation
paths:

| output | composition | DRM/driver requirement |
|---|---|---|
| SBS half | scale left and right to 960x1080 and place them side by side | expose SBS-half mode and emit its HDMI VSIF |
| TaB | scale left and right to 1920x540 and stack them | expose top-and-bottom mode and emit its HDMI VSIF |
| frame packing | retain both 1920x1080 eyes, place left at line 0 and right at line 1125 in a 1920x2205 buffer | expose FP mode, emit FP VSIF, and program doubled link timing |

[qualified] A 2026-09-20 audit of gamescope's documented command line and DRM
backend found OpenVR overlay support but no SBS, TaB or HDMI frame-packing
output target. That makes this a concrete compositor feature to build rather
than a switch that is already present. Monado supplies the open OpenXR runtime
side of the path, but this project has not yet demonstrated a Monado-to-TV
presentation backend.

The best first implementation is SBS-half. It matches the already-proven AMD
kernel patch, uses a normal-sized framebuffer, preserves 60 Hz presentation,
and can reuse the packing operation wiz3D has demonstrated for years. TaB is
the same class of change. Frame packing should follow after the kernel timing
path is proven independently on nouveau and then implemented correctly in
amdgpu DC.

## One stereo-intent path for video and rendering

SEI detection is not limited to rendered 3D. It is the strongest automatic
trigger for decoded H.264/H.265 video. FFmpeg already exposes the
`frame_packing_arrangement` SEI as decoded-frame stereo metadata; the Kodi and
mpv work in this project prove that the layout can survive as far as the
player. Matroska StereoMode, player or filename hints, MPO metadata, and a pair
of OpenXR eye surfaces are other producers of the same intent.

The missing interface should normalize those producers into one descriptor:
layout, left/right order, whether each view is full or subsampled, source and
lifetime. The display policy then intersects that intent with each connected
sink's EDID and chooses a common output mode. For two compatible televisions,
one SEI event can select one shared SBS/TaB/FP packing, compose it once, and
present it on both links. Different sink capabilities require separate final
packing passes, while the decoded frames or rendered eye textures remain
shared.

The signal lifecycle matters. In-band SEI may arrive only on keyframes and its
persistence flag carries the state across intervening pictures, so losing the
layout on the next frame would make the output flap back to 2D. Container
metadata normally applies for the track lifetime. Live-rendering intent applies
for the OpenXR session. End of track, explicit cancellation, or session loss
must release the stereo mode and restore the prior display configuration.

[inferred] The first useful Linux integration is therefore a media-player to
compositor path: decoded-frame SEI or container stereo metadata requests a
stereo output, and the compositor owns mode negotiation, packing, cloning and
restoration. The OpenXR path can later publish the same descriptor with two
live surfaces. This keeps HDMI policy out of each decoder and avoids separate
watchers for VLC, mpv, Kodi and games.

### Stereo inside an ordinary desktop window

The HDMI 3D mode is global to the link, but stereo content can occupy one
window. The compositor maintains a left-eye and right-eye output canvas. A
normal desktop surface is placed at the same coordinates with the same pixels
in both canvases, which puts it at screen depth. A stereo surface has one
logical window rectangle and two buffers: the compositor places its left
buffer in that rectangle on the left canvas and its right buffer in the same
rectangle on the right canvas. Window clipping, stacking and decoration remain
desktop operations; only the sampled texture differs by eye.

This also handles mixed content. A stereo game or movie can run in a window
while panels, another application, subtitles and the pointer are duplicated
into both views. Fullscreen is the same operation with the stereo rectangle
covering the output. The two finished canvases are then packed once for HDMI,
and the television separates them again.

[proven by owner observation of published demo footage] The reuse is not
merely architectural: in Valve's Steam Frame demonstrations the wearer's game
was simultaneously visible on a conventional monitor, which means the
compositor already produced at least one conventional-display eye surface on
a standard output path. Feeding that same surface class to a TV packer is a
retargeting of an output that demonstrably exists, not a request for a new
rendering stage.

[inferred] That surface pairing is the reusable part of the Steam Frame/HMD
model. An OpenXR compositor already receives eye-specific images and projects
them onto corresponding per-eye surfaces. A TV backend replaces lens-warped
HMD presentation with a flat projection surface and an SBS, TaB or FP packer.
[direction set by Daniel, 2026-09-20] The Steam Frame aim is explicitly
bi-directional, and the two directions are different engineering paths that
share this document's middle layer. Inbound: play existing 3D media (MVC
Blu-ray, SBS/TaB files, SEI-flagged streams) correctly inside the headset,
which needs the stereo-intent descriptor and decoder-side layout handling but
never touches HDMI. Outbound: carry the Frame's own dual-surface output (or
its host PC's, when streaming) to an external 3D screen through the SBS/TaB/FP
backend above. Neither direction is a substitute for the other; both consume
the same normalized layout, eye order and view-resolution semantics.

For non-OpenXR applications, a Wayland protocol or equivalent compositor API
still has to associate two submitted buffers with one logical surface and
carry eye order and layout intent. This is the missing desktop contract behind
the Windows-style observation that windowed 3D works once global 3D output is
enabled. The proposed behavior and metadata boundary are specified in
`stereo-intent-interface.md`.

## Android correction: output exists, intent propagation is missing

[proven by owner hardware tests] Older Android HDMI devices in the project
already drive these BRAVIAs using standard HDMI stereo modes. The RK device
exposes off, frame-packing, top-and-bottom and side-by-side selections in its
display sysfs interface. The T10 display stack exposes SBS and TaB through its
vendor display command, and its later controlled transaction reached a
1920x2160 frame-packing link mode on the television.

The VLC watcher used on those devices is therefore policy glue. It detects
that the foreground content is stereo and selects the output mode which the
display stack already knows how to generate. It does not invent a proprietary
Android substitute for HDMI 3D.

[inferred] The watcher becomes unnecessary when stereo intent travels through
the whole media path: container or elementary-stream metadata reaches the
player, the player reports the decoded layout, the Android framework or
compositor selects the matching display mode, and the HDMI driver emits the
standard timing and infoframe. That is the same missing connection seen on
Linux, at a higher layer. Android hardware evidence therefore strengthens the
case for automatic, content-driven output instead of weakening it.

## Test order and current result

1. Run the new `fp` path on nouveau, whose source already applies stereo timing doubling — **PASS [proven]**.
2. Record the chosen 1920x1080@24 logical mode, 1920x2205 framebuffer, TV auto-switch and visible depth — **DONE**.
3. Preserve that run as the frame-packing positive control — **DONE**.
4. Run the identical payload on the AMD iGPU's separate HDMI output — **SIGNAL PASS / IMAGE FAIL [proven]**.
5. Repeat future AMD work with the other GPU and every non-target CRTC explicitly dark — **ISOLATION IMPLEMENTED, not yet run**.
6. Keep the existing AMD patch claim at SBS/TaB picture+signaling and FP signaling until DC timing mapping produces an FP picture.
7. Prototype a dual-surface-to-SBS output backend before attempting compositor-driven FP.

The positive-control command was:

```
sudo systemd-run --unit=nouveau-3d-test --collect sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nouveau-test.sh fp
```

## Source anchors

- Linux DRM timing transform: `drivers/gpu/drm/drm_modes.c`, `drm_mode_set_crtcinfo()`.
- Nouveau scanout and timing handling: `drivers/gpu/drm/nouveau/dispnv50/head.c`.
- i915 adjusted-mode handling: `drivers/gpu/drm/i915/display/intel_display.c`.
- amdgpu DRM-to-DC translation: `drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c`.
- DC stereo types and machinery: `drivers/gpu/drm/amd/display/dc/dc_types.h`, `dc/core/dc_resource.c`, `dc/opp/dcn10/dcn10_opp.c`, `display/modules/info_packet/info_packet.c`.
- Existing dual-surface packer: [wiz3D SideBySideOutput](https://github.com/effcol/wiz3D/tree/main/OutputMethods/SideBySideOutput).
- Candidate Linux compositor: [ValveSoftware/gamescope](https://github.com/ValveSoftware/gamescope).
- Open OpenXR runtime: [Monado](https://gitlab.freedesktop.org/monado/monado).
