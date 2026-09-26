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
| `SVRTV_LOG` | none | append a log to this file; relative to the module's folder, and falls back there when the path cannot be opened |

## In the game

The first version made Half-Life 2 crash at every launch: it forced VR mode
at start even with no layout set, and the client's first call,
`GetViewportBounds(eye, NULL, NULL, &w, &h)`, passes NULL for the outputs it
does not want. Both are fixed: the module is inert without a layout and
accepts NULL outputs (`test_geometry.cpp` checks both).

2026-09-24: installed as `bin/sourcevr.so` (Valve's kept as
`bin/sourcevr.so.valve`; Steam's "Verify integrity of game files" restores
it), the game loads it and runs in 2D with no crash, on both Sonys, through
the bench suite's view steps (`tools/hl2-bench/`).

**First full 3D playback, same day:** build `c3595682…` (32-bit) played the
reference demo in side-by-side 3D on the EX725 with Vulkan (DXVK), 9857
frames at 59.9 fps, no crash. Daniel watched with glasses: real depth, no
ghosting, the default separation (2.5) and convergence (120) looked right,
crosshair in 3D. In that build each eye renders straight into its half of
the frame.

**The HUD, same day (build `2765a3bb…`):** the 3D scene at the back, the
HUD as a transparent layer across the whole screen, identical in both eyes,
so it sits on the screen plane. Daniel: "perfect hud". How it works, and
what it took:

- The engine never calls `CreateRenderTargets` (not even with
  `VRModeAdapter "0"` in `videoconfig_linux.cfg`; with that edit in place
  the watch lost vsync, so it was reverted).
  The module takes the material system from the factory passed to
  `Connect()` and makes its targets on first use, inside the engine's
  render-target allocation bracket: one per eye, the HUD sheet `_rt_gui`
  (640x480, which this game only makes when VR is set up at start), and a
  copy of that sheet, `_rt_svrtv_gui`, refreshed once a frame.
- Each eye renders into its own target; `DoDistortionProcessing` copies it
  into its half of the frame, and `CompositeHud` (which also runs during
  screenshots) blends the HUD copy over it.
- The HUD paste first showed a purple-black checkerboard (Source's missing
  texture). Tests ruled out the texture (the engine's own
  `_rt_FullFrameFB` showed the same), the material (a healthy one did too),
  and the interface layout (the 2013 and 2025 SDK headers agree on every
  slot the module calls). The cause: with the engine's threaded renderer, a
  material first used without a main-thread precache draws as the error
  material. The module now holds a reference and calls
  `CacheUsedMaterials()` once (log: `precached 0 -> 1`).
- The client's own `vgui/inworldui` is not used: it is set up while
  `_rt_gui` does not exist. The paste uses `vgui/icon_con_grey`, the same
  kind of material (the server browser's connection icon, never shown in
  single-player), with its `$basetexture` pointed at the HUD copy.
- The sheet is 4:3; by default it is stretched across the full width, as
  Daniel asked; `SVRTV_HUD43=1` keeps the 4:3 shape.

**Crosshair and the rest, same day (build `8c35ea5b…`):** Daniel, with
glasses: crosshair visible, identical in both eyes; muzzle sprite on the
muzzle; HUD at the top. Two modes:

| mode | how | crosshair | picture |
|---|---|---|---|
| full resolution (default) | eyes at their half of the frame (960x1080) | HL2's classic crosshair, drawn by the module on the 2D layer, once per eye | sharp: for high-resolution textures |
| native crosshair | `SVRTV_EYE=640x480` | the client's own (quick-info dot and brackets), centred | softer: fine for the original textures |

- In VR mode the client paints its crosshair straight into each eye at the
  centre of a 640x480 screen (dump: eye pixel ~314,240), whatever the eye
  size. With 640x480 eyes that is the true centre; at full resolution the
  module turns it off (`crosshair 0`) and draws `crosshair_default`
  (`sprites/crosshairs`, 0,48, 24x24) with `sprites/crosshairs_tluc`, which
  blends by the texture's alpha. HL2's quick-info dot (`sprites/qi_center`)
  is additive, DXT1 without alpha: drawn per eye its look depended on the
  background, which differs between the eyes; drawn into the HUD sheet it
  became a black square.
- When VR starts, the module issues console commands itself through the
  engine's client interface (`VEngineClient013`, from the `Connect()`
  factory; `ClientCmd_Unrestricted` sits at the same slot in the 2013 and
  2025 headers). Default (`SVRTV_ONVR`): `vr_moveaim_mode 7`,
  `vr_moveaim_mode_zoom 7` (the view follows the game, not a headset: the
  SDK's HMM_SHOOTMOVELOOKMOUSE; the default left the view fixed while the
  demo's player looked around), then Valve's own HL2 VR settings from
  `hl2/cfg/sourcevr_hl2.cfg` (`vr_first_person_uses_world_model 0`,
  `hud_draw_fixed_reticle 0`, `r_flashlightscissor 0`), which the client is
  meant to run when VR starts and this build does not.
- `crosshair` is a saved setting. When the module turns it off it leaves
  `svrtv-crosshair-off` next to itself; stopping VR, or the next start of
  the game (2D included, after `config.cfg`), turns it back on.
- HUD: HL2's health and ammo row (sheet rows 432-467 of 480, 12 rows above
  the bottom) moves to the top with the same 12-row margin, and the rest of
  the sheet moves down by that band's height, whole (`SVRTV_HUDTOP=0.125`,
  the band's fraction of the sheet; 0 keeps HL2's layout). Swapping the two
  bands instead cut the weapon selection (drawn at the top) in two. While
  a menu or dialog is open (the client passes `translucent` false when the
  cursor is visible), the sheet keeps HL2's layout: moving the band sent
  Save/Cancel to the top and made the cursor wrap around.
- Muzzle sprite: the flash sprite at the gun's tip is placed by converting
  the gun's attachment from `viewmodel_fov` to the world's field of view;
  in VR mode the gun is drawn with the eye projection, so the sprite
  missed the gun. `viewmodel_fov 90` puts it exactly on the muzzle
  (confirmed by eye). It is a cheat-protected setting (`sv_cheats 1`), so
  it is not in the defaults. For Valve: allow it for this view.


**First real playthrough, same day (build `ed278357…`, HX855, Vulkan, side
by side):** Daniel loaded an old save and rode the airboat through the
canals chased by the helicopter: "what a blast". In one launch: two save
loads (`d1_town_01`, `d1_canals_10`) and two level transitions
(`d1_canals_10` to `11` to `12`), no hang, no crash; shadows right;
weapon selection, HUD, crosshair and menus whole.

Compared with wiz3D's own record for Half-Life 2 (README compatibility
table, `effcol/wiz3D`): "Mostly Working. `steam_legacy` beta branch. Use
`-game` command line argument. Shadows have issues." Here: the current
build, native Linux, shadows right, because the engine renders each eye
itself. wiz3D is universal (one DX9 proxy for hundreds of games, HelixMod
shader fixes); this module reaches only Source games that carry Valve's VR
interface. A side-by-side run on the same machine is session C of the
bench.


**Mouse, same day (build `2942846f…`):** the game's UI cursor uses window
pixels 1:1 (a logged trace: it started at the window centre, 960,540),
while the sheet both eyes show is the window's top-left 640x480; at the
left edge the cursor went down to y 819, off the sheet. While VR is on, the
module confines the system pointer to that 640x480 rectangle through the
game's own SDL2 (`SDL_SetWindowMouseRect`, found in the already-loaded
`libSDL2-2.0.so.0`; older SDL: the pointer is pulled back each frame).
Daniel: "perfect, mouse won't exit the menu screen". `SVRTV_CONFINE=0`
turns it off; `SVRTV_MOUSELOG=1` logs the pointer next to the UI cursor.
Inside gamescope the same fence pinned the pointer to the sheet's
bottom-right corner, in play and in the menus (2026-09-25), so the module
leaves it off when `GAMESCOPE_WAYLAND_DISPLAY` is set (gamescope sets it for
the games it starts); `SVRTV_CONFINE=1` forces it on.
The module looks SDL up with `dlopen`/`dlsym` pinned to their original
glibc versions; before glibc 2.34 those lived in `libdl`, so the module
needs a glibc of 2.34 or newer in the game's container (Steam's runtime
uses the host's glibc when it is newer).

Open:

- OpenGL in VR mode crashes after 20 s in the engine's render thread
  (materialsystem, studiorender, shaderapidx9), not in the module; every
  OpenGL 3D run did. Use `-vulkan` for 3D.
- In VR mode, the second level reload within one launch hung (GPU idle) in
  a repeated timed demo. Real play did not: see below.
- 3D view screenshots come out black (the first frame in VR mode).
- Test switches: `SVRTV_HUDCOPY=1` (paste the sheet with a plain copy),
  `SVRTV_HUDTEX=<texture>` (sample another texture), `SVRTV_HUDMAT=<material>`.

To try 3D by hand: Steam launch options
`SVRTV_LAYOUT=sbs SVRTV_LOG=svrtv.log %command% -vulkan -w 1920 -h 1080 -console`
(a relative log path lands next to the module; Steam runs the game in a
container that may not see other folders),
television in side-by-side 3D mode. The module forces VR mode at start;
`vr_activate` in the console does the same by hand.
