# HL2 bench suite

Every planned Half-Life 2 configuration in one unattended session per
driver stack: 2D and stereo (the VR Stereo Spectator module in
`tools/vr-stereo-spectator/`), OpenGL and Vulkan, HL2 RTX, and wiz3D as the
reference, on the RTX 3060 and both Sony televisions.

`hl2-suite.sh STEPS_FILE [--only id1,id2] [--force] [--reboot-after]` runs a
steps file. Each step launches the game through Steam, collects what the
step produces, closes the game and waits for Steam before the next step.
Results go to `/K3D/temp/hl2-bench/suite-<time>-<name>/`, one folder per
step plus `summary.tsv`. The header of `hl2-suite.sh` lists the step kinds
and what each one collects.

| file | what |
|---|---|
| `session-0-displays.conf` | which television is which: one 2D view per Sony |
| `session-a-proprietary.conf` | proprietary NVIDIA driver: views, timed demos, demo frames, the HX855 cross-check, a last 3D watch step |
| `session-b-open.conf` | the test kernel (nouveau + Mesa, NVK): the same steps without HL2 RTX |
| `session-c-wiz3d.conf` | HL2's Windows build under Proton, plain and with wiz3D |
| `session-w-watch.conf` | one 3D watch step (Vulkan, side by side) |
| `game-wrap.sh` | Steam launch option for Half-Life 2 and HL2 RTX: `game-wrap.sh %command%`; adds the current step's arguments and environment, does nothing outside a suite run |
| `wiz3d-setup.sh` | installs wiz3D for one step and removes it after |
| `arm-session-b.sh`, `session-b-autostart.sh`, `hl2-bench-nouveau.service`, `hl2-bench-session-b.desktop` | the one-shot boot into the test kernel for session B, which runs by itself and reboots back |

## How the pieces are placed

- **Display.** The steps file names an output (`HDMI-A-2`); the suite turns
  it into HL2's `-displayindex` and adds a KWin window rule (position and
  fullscreen, forced) for the step, because the game otherwise opens on the
  screen under the mouse. The KWin rules file is backed up and restored
  byte for byte.
- **GPU.** The desktop runs on the AMD iGPU; the game renders on the RTX
  3060 through PRIME offload. The `# gpu:` line picks the variables:
  `nvidia` (proprietary) or `mesa` (nouveau), which also removes the NVIDIA
  offload variables that Steam's own environment carries.
- **In-game commands.** The engine runs `exec game.cfg` in `GameInit()` on
  every map load, single-player included; `listenserver.cfg` runs only under
  the multiplayer rules. No `game.cfg` ships in the game's VPKs, so the
  suite writes a loose one for view steps and removes it after the step and
  on exit.

## Results

**Session 0, 2026-09-24 15:14:** both view steps rendered on the intended
television, the HX855 on the AMD port (`HDMI-A-1`) and the EX725 on the
NVIDIA port (`HDMI-A-2`), and each saved its picture of the spawn view and
closed by itself. The stereo module was installed and inert (no layout
set); no crash.

**First full 3D playback, 2026-09-24 15:40:** a watch step (Vulkan, side
by side, `session-w-watch.conf`) played the whole reference demo on the
EX725: 9857 frames in 164.7 s, 59.9 fps at real speed, no crash. Daniel
watched with glasses: real depth, real colours, no ghosting, crosshair in
3D, no HUD (see the module README).

Session A, first pass (stopped after a09, rerun in progress), what it
taught:

| step | result |
|---|---|
| a05 HL2 RTX view | the level rendered, path traced; the window landed on the HX855 (the KWin rule matched only `hl2_linux`, not Proton's window) |
| a06 OpenGL 2D | 224.5 fps focused; 161.6 fps in the run where the window lost focus |
| a07 Vulkan 2D | 59.9 fps: locked to vsync; `mat_vsync 0` does not reach DXVK |
| a08 OpenGL 3D | crashed after 20 s in the engine's render thread (materialsystem, studiorender, shaderapidx9), not in the module |
| a09 Vulkan 3D | went side by side once the demo played |

Session A, second pass (same day, 15:48-16:31, with the fixes below):

| step | result |
|---|---|
| a06 OpenGL 2D, EX725 | 464 / 473 fps |
| a07 Vulkan 2D, EX725 | 585 / 588 fps |
| a09 Vulkan 3D side by side | 444 fps (view fixed ahead); 380 fps once the view followed the demo (mode 7); a third run in one launch hung on the level reload |
| a18 OpenGL 2D, HX855 through PRIME | 550 / 561 fps, faster than direct; not yet understood |
| a08, a10, a13, a14, a19 OpenGL 3D | crash after 20 s, every time (engine render thread) |
| a11, a15 HL2 RTX | the demo is refused: `game directories don't match (hl2rtx / hl2_complete)`; HL2 RTX needs its own demo |
| a12 OpenGL 2D demo frame | saved (with `timedemo_runcount 2` before `benchframe`) |
| a16 Vulkan 3D watch | full demo at 60 fps, the view following the recorded one |

Fixes that came out of it:

- The engine sleeps 50 ms per frame while its window is unfocused
  (`engine_no_focus_sleep`, saved in `config.cfg`). A temporary
  `hl2/cfg/autoexec.cfg` sets it to 0 during sessions; restore 50 after.
- Benchmark steps on Vulkan get `DXVK_CONFIG="d3d9.presentInterval = 0"`.
- This demo's first playback always stops after 2 frames, 2D included.
  The summary keeps that row (about 0.2 fps); it is not a result. A watch step is therefore a timed demo
  with 2 runs and vsync on, which at 60 Hz takes exactly the demo's real
  length.
- This build writes `hl2/sourcebench.csv` in lowercase.
- 3D view pictures come out black: the first frame in VR mode is empty.
- The game's DXVK is v2.0: it reads a config file, not the `DXVK_CONFIG`
  variable (2.1+); `game-wrap.sh` writes the file next to the game. Watch
  steps force vsync there (`presentInterval = 1`).
- Every timed step needs 2 runs or more; 3D steps exactly 2.
- The KWin rule matches Proton windows too (`steam_app_220`,
  `steam_app_2477290`).
- `-condebug`: the whole console from the first line, as `condebug.log`.
- `SVRTV_EXTRA="KEY=value ..."` adds module settings to `svrtv.ini` for a
  test run.

What did not work, and why the view step is now one picture:

- The camera sequence in `listenserver.cfg` never ran in single-player.
- The same sequence in `game.cfg` ran before the player existed: `getpos`
  printed `0 0 0` during loading, `setang` did nothing, and the sequence
  stalled. `wait` does not hold commands until the player is in.
- `screenshot` waits for the next rendered frame, which is the spawn view.
  Different viewpoints come from the demo instead (the `frame` steps).
