# VR Stereo Spectator: `sourcevr` for 3D televisions

A replacement for the Source engine's VR module, `sourcevr.so`, that
presents a stereoscopic television to the engine as its "headset". Source
games from the 2013 SteamVR era still carry that VR render path; with this
module the engine itself renders both eyes, with real stereo geometry, into
one side-by-side or top-and-bottom frame the television unpacks. No lens
distortion, no head tracking, no per-game shader fixes.

**Status (2026-09-24): built and geometry-verified, not yet run in a game.**

## How it fits the engine

Read from the Source SDK 2013 client (`src/game/client/view.cpp`,
`client_virtualreality.cpp`) and the interface header
(`src/public/sourcevr/isourcevirtualreality.h`, `SourceVirtualReality001`):

- `vr_activate` in the console switches VR on. Because the module answers
  `ShouldForceVRMode()` with true, the client skips its headset-adapter
  checks and calls `Activate()`, then runs `exec sourcevr_<moddir>.cfg`.
- For each eye the client asks `GetViewportBounds()` and renders into that
  rectangle, so the module decides the packing.
- Each eye's camera is the mid-eye moved by `GetMidEyeFromEye()` (Source
  coordinates: x forward, y left, z up) and projected with
  `GetEyeProjectionMatrix()` (mathlib convention: view down -z, depth 0..1).
- Distortion runs only in `DoDistortionProcessing()`, which does nothing
  here.

Half-Life 2's native Linux build (checked 2026-09-24, build 19307283) is
32-bit, ships `bin/sourcevr.so` exporting `SourceVirtualReality001`, and its
client still has the whole VR path (`vr_activate`, `vr_stereo_swap_eyes`,
the HUD and projection settings). The shipped module contains no headset
SDK code.

## Geometry

Parallel eye cameras with an off-centre frustum: both eyes share one screen
plane at the convergence distance, with no toe-in and no vertical parallax.
The field of view is the game's own (passed in each frame), widened from
Source's 4:3 definition to the displayed aspect, and the projection uses the
displayed aspect whatever the packing, because the television stretches each
half back to full size.

## Build

```
./build.sh [path/to/source-sdk-2013/src]
```

Builds `out/32/sourcevr.so` and `out/64/sourcevr.so` in a `debian:testing`
container against Valve's SDK headers (a sparse checkout of
`ValveSoftware/source-sdk-2013` with `src/public`, `src/common`, `src/tier1`
and `src/mathlib`). No C++ runtime is linked: the module needs only `libc`
and `libm`, at GLIBC 2.1.3 (32-bit) and 2.2.5 (64-bit), so it loads in any
Steam runtime. The only export is `CreateInterface`.

## Verified without the game

`test_geometry.cpp` loads a built module and checks it numerically: a point
at the convergence distance has zero parallax, farther points are behind the
screen, nearer points in front, and the viewports match the layout. All
pass for 32-bit and 64-bit, side-by-side and top-and-bottom, with and
without the eye swap (2026-09-24). The first version of the swap option
swapped both the cameras and the halves, which cancelled out; the test
caught it.

## Configuration

Environment variables, set through Steam's launch options
(`VAR=value %command%`):

| variable | default | meaning |
|---|---|---|
| `SVRTV_LAYOUT` | `sbs` | `sbs` or `tab` |
| `SVRTV_WIDTH`, `SVRTV_HEIGHT` | 1920, 1080 | output size; match `-w`/`-h` |
| `SVRTV_ASPECT` | width/height | displayed aspect |
| `SVRTV_SEPARATION` | 2.5 | eye separation in game units (about 64 mm) |
| `SVRTV_CONVERGENCE` | 120 | distance of the screen plane in game units |
| `SVRTV_SWAP` | 0 | 1 packs the right eye first |
| `SVRTV_LOG` | none | append a log to this file |

## First in-game test (planned)

1. Back up Valve's module: `bin/sourcevr.so` to `bin/sourcevr.so.valve`.
   Copy `out/32/sourcevr.so` in its place. Steam's "Verify integrity of
   game files" restores Valve's.
2. Launch options:
   `SVRTV_LAYOUT=sbs SVRTV_LOG=/K3D/temp/svrtv.log %command% -w 1920 -h 1080 -console`
3. In the console: `map d1_town_01`, then `vr_activate`. Television in
   side-by-side 3D mode.

Open questions only the game can answer:

- whether the engine loads the module and calls `CreateInterface` at start
  (the log says);
- whether rendering straight into the viewports works with no offscreen
  targets (`GetRenderTarget` returns none), or the eyes must render into
  targets that the module then copies into the frame;
- how the menus and HUD behave: VR mode forces a 640x480 UI and can draw
  the HUD in the world;
- whether `GetDisplayBounds` resizes the window as intended;
- comfortable defaults for separation and convergence, compared with wiz3D
  on the same scene.
