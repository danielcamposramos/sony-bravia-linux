# VR Stereo Spectator: `sourcevr` for 3D televisions

A replacement for the Source engine's VR module, `sourcevr.so`, that
presents a stereoscopic television to the engine as its "headset". Source
games from the 2013 SteamVR era still carry that VR render path; with this
module the engine itself renders both eyes, with real stereo geometry, into
one side-by-side or top-and-bottom frame the television unpacks. No lens
distortion, no head tracking, no per-game shader fixes.

**Status (2026-09-24): built and geometry-verified, not yet run in a game.**
License: the Source 1 SDK License, the license of the SDK it is built on
(`LICENSE`, `LICENSE-SOURCE-1-SDK`); provenance in [../PROVENANCE.md](../PROVENANCE.md).

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

`KEY=VALUE` lines in `svrtv.ini` next to the module (so the bench suite
switches steps by rewriting one file). The same names in the environment
win, so Steam's launch options (`VAR=value %command%`) work too. Without
`SVRTV_LAYOUT` the module stays inert: it reports no headset, never forces
VR mode, and the game runs in 2D exactly as with Valve's module.

| variable | default | meaning |
|---|---|---|
| `SVRTV_LAYOUT` | unset (inert) | `sbs` or `tab` |
| `SVRTV_WIDTH`, `SVRTV_HEIGHT` | 1920, 1080 | output size; match `-w`/`-h` |
| `SVRTV_ASPECT` | width/height | displayed aspect |
| `SVRTV_SEPARATION` | 2.5 | eye separation in game units (about 64 mm) |
| `SVRTV_CONVERGENCE` | 120 | distance of the screen plane in game units |
| `SVRTV_SWAP` | 0 | 1 packs the right eye first |
| `SVRTV_LOG` | none | append a log to this file |

## In the game

The first version made Half-Life 2 crash at every launch: it forced VR mode
at start even with no layout set, and the client's first call,
`GetViewportBounds(eye, NULL, NULL, &w, &h)`, passes NULL for the outputs it
does not want. Both are fixed: the module is inert without a layout and
accepts NULL outputs (`test_geometry.cpp` checks both).

2026-09-24: installed as `bin/sourcevr.so` (Valve's kept as
`bin/sourcevr.so.valve`; Steam's "Verify integrity of game files" restores
it), the game loads it and runs in 2D with no crash, on both Sonys, through
the bench suite's view steps (`tools/hl2-bench/`). The 3D steps are next.

To try 3D by hand: Steam launch options
`SVRTV_LAYOUT=sbs SVRTV_LOG=/K3D/temp/svrtv.log %command% -w 1920 -h 1080 -console`,
television in side-by-side 3D mode. The module forces VR mode at start;
`vr_activate` in the console does the same by hand.

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
