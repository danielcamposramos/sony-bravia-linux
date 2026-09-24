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

What did not work, and why the view step is now one picture:

- The camera sequence in `listenserver.cfg` never ran in single-player.
- The same sequence in `game.cfg` ran before the player existed: `getpos`
  printed `0 0 0` during loading, `setang` did nothing, and the sequence
  stalled. `wait` does not hold commands until the player is in.
- `screenshot` waits for the next rendered frame, which is the spawn view.
  Different viewpoints come from the demo instead (the `frame` steps).
