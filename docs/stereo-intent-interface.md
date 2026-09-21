# Stereo intent from media and applications to HDMI

Status: architecture note, 2026-09-20. No Wayland protocol or compositor code
is claimed as implemented.

## Historical precedent

[proven, contemporary documentation] Windowed stereo beside an ordinary mono
desktop predates the consumer 3D-driver era. VMD documented “stereo in a
window” on SGI RealityEngine2: its display window was stereoscopic while other
windows appeared normally. StereoGraphics documented windowed OpenGL stereo
on HP Visualize FX hardware in 1998. Nvidia's GPU Programming Guide says
OpenGL quad-buffered stereo works in windowed mode, and its 2004 Quadro guide
says stereoscopic and monoscopic applications can run simultaneously. The
four-buffer application contract was front/back left plus front/back right.

This history validates the composition model, not an automatic SEI path.
Those applications explicitly selected a stereo-capable visual and submitted
left and right buffers. In the proposed media path, SEI or container metadata
lets a player derive the equivalent intent automatically. The compositor
still has to duplicate the mono desktop into both eye canvases, place the two
player views at the same window rectangle, and commit a stereo output mode.
Switching the HDMI mode alone would make the television reinterpret a normal
desktop frame and cannot produce correct windowed stereo.

Primary references: [VMD 1.5 CrystalEyes documentation](https://www.ks.uiuc.edu/Research/vmd/vmd-1.5/ug/node104.html),
[StereoGraphics' 1998 HP programming guide](https://www.schneider-digital.com/wp-content/downloadcenter/3D-Stereo/How_To_implement_QuadBuffer_Stereo/older_instructions/how_to_implement_stereo.pdf),
[Nvidia GPU Programming Guide](https://developer.download.nvidia.cn/GPU_Programming_Guide/GPU_Programming_Guide.pdf),
and [Nvidia Quadro Release 60 workstation guide](https://download.nvidia.com/Windows/61.76/61.76_Quadro_Release_60_Graphics_Display_Property_Users_Guide..pdf).

## Existing contract and missing contract

[proven, specification] OpenXR already carries the eye primitives needed for
this design. `XR_VIEW_CONFIGURATION_TYPE_PRIMARY_STEREO` defines view 0 as
left and view 1 as right. `XrCompositionLayerQuad` carries one swapchain
subimage plus `XR_EYE_VISIBILITY_LEFT`, `RIGHT` or `BOTH`. [inferred] Two quad
layers with the same pose and size, one visible to each eye, directly express
Daniel's "same projection surface, one image per eye" model. See the official
[OpenXR view-configuration](https://registry.khronos.org/OpenXR/specs/1.1/man/html/XrViewConfigurationType.html)
and [quad-layer](https://registry.khronos.org/OpenXR/specs/1.1/man/html/XrCompositionLayerQuad.html)
definitions.

[proven, local audit] The complete XML set installed as wayland-protocols 1.49
contains no occurrence of stereo, stereoscopic, left-eye, right-eye or
multiview. This establishes the gap on this Debian system. It is not a claim
that no compositor-private protocol or later proposal exists anywhere.

## Keep content layout separate from output layout

The input descriptor says what the application or decoder produced. It must
not prescribe the HDMI packing. An H.264/H.265
`frame_packing_arrangement` SEI may describe side-by-side, top-and-bottom,
checkerboard, row-interleaved or another source arrangement. OpenXR normally
supplies separate eye images. MPO supplies two still images. Matroska carries
a track-level stereo layout.

The compositor first resolves and, where necessary, unpacks those sources into
left and right logical views. It then chooses an output independently from the
EDID intersection and current policy: SBS-half, TaB or full frame packing. A
TaB file may therefore become an SBS HDMI frame, and separate OpenXR eye images
may become any of the three.

## Normalized stereo intent

A player/runtime-to-compositor contract needs these semantics, regardless of
its eventual wire representation:

| field | purpose |
|---|---|
| state | mono, stereo, or explicit cancellation |
| source packing | separate views, SBS, TaB, frame sequential, row/column interleaved, checkerboard |
| eye order | which view is physically left and right |
| sampling | full resolution or horizontally/vertically subsampled |
| view regions | crop rectangles when both views share one buffer |
| lifetime | decoded-stream persistence, track lifetime, still-image display, or live session |
| provenance | resolved player metadata, OpenXR, explicit user choice, or heuristic |

The player should resolve conflicts among bitstream, container and user
metadata before publishing the descriptor. The display protocol should carry
one resolved truth rather than reproduce every media format's precedence
rules.

## Surface and commit semantics

One logical window owns one placement, clip, stacking position and input
region. Its stereo content can arrive as two synchronized buffers or as one
packed buffer plus two view regions. The compositor must sample the left view
only into its left-eye canvas and the right view only into its right-eye
canvas. Paired buffers need one atomic presentation point so a new left image
cannot appear beside an old right image.

Ordinary surfaces are sampled identically into both eye canvases. They remain
at screen depth while the stereo window carries disparity. Window decorations,
panels, subtitles and the pointer follow this mono rule unless they explicitly
publish stereo content. Fullscreen is the same composition with the stereo
surface covering the output.

The eventual Wayland shape could extend a normal `wl_surface` with stereo
state and a synchronized second-eye attachment, or carry two view regions in
one submitted buffer. That choice needs compositor and zero-copy prototyping;
this note defines the behavior it must preserve rather than freezing an XML
API prematurely.

## Activation and lifetime

HDMI stereo mode belongs to an output, while stereo intent belongs to a
surface. Compositor policy bridges them. A reasonable first policy activates
stereo while a stereo surface is visible and focused or fullscreen, then
restores the previous output configuration when the surface becomes mono,
closes, loses its session, or publishes explicit cancellation.

SEI needs persistent state. The frame-packing message can arrive on keyframes
while applying to the pictures between them. Clearing intent whenever the
current decoded frame lacks side data would make the HDMI output flap between
2D and 3D. The player or decoder wrapper must retain the last valid arrangement
until its cancellation, replacement, seek reset or end of stream.

The existing Android VLC watcher is a prototype for this state machine: it
observes stereo playback, selects the vendor display mode and restores the
prior mode later. End-to-end intent propagation moves that state into the
decoder/player/compositor chain and removes the per-application polling layer.

## Two outputs

For EX725 and HX855 together, policy first intersects both EDIDs and chooses
one shared layout, timing and eye order. The compositor builds the two eye
canvases once and packs them once. The packed result can then be scanned out on
both links, subject to DMA-BUF sharing or a cross-GPU copy.

If the sinks have no acceptable common mode, both outputs still reuse the same
logical eye canvases but run separate final packers. VSIF generation remains
per connector. A second game or movie render is unnecessary.
