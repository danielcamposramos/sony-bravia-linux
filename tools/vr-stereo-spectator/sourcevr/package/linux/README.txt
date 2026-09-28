STEREO 3D FOR HALF-LIFE 2 AND SOURCE GAMES (LINUX)
VR Stereo Spectator, build of 2026-09-28: play and spectate

Half-Life 2 in real stereo 3D on a 3D TV, projector or monitor.
The game already carries Valve's VR render path from 2013: this module presents your 3D display to the engine as its headset, so the engine itself renders both eyes with real stereo geometry, and your display unpacks them.
No per-game shader fixes, no wrapper around the renderer.

Status: played on a 3D TV (Sony KDL-46HX855, NVIDIA RTX 3060, Debian testing, KDE Plasma on Wayland), every format, natively and through gamescope, 2026-09-24 to 2026-09-28.


WHAT YOU NEED

- Half-Life 2 from Steam, the native Linux version, as installed by Steam (no mods needed).
- A 3D display that accepts top and bottom or side by side over HDMI (most 3D TVs of the 2010s do), with its glasses; or any colour screen and red/cyan glasses, through gamescope (below).


INSTALL

1. Start Half-Life 2 once from Steam and quit, so Steam finishes its first-run setup.
2. Run ./install.sh (or ./install.sh "/path/to/steamapps/common/Half-Life 2").
   It finds Half-Life 2 in your Steam libraries (native or Flatpak Steam), keeps Valve's own module as bin/sourcevr.so.valve, installs ours, and adds the 3D section to the game's options menu.
3. In Steam: Half-Life 2 > Properties > Launch options, put one of these two lines (see "The muzzle flash, cheats and achievements" below):

   -vulkan -gamepadui -stereo3d
   -vulkan -gamepadui -stereo3d +sv_cheats 1 +viewmodel_fov 90

   -vulkan is required: the OpenGL renderer crashes in the VR path (reported to Valve).
   -gamepadui turns on the game's newer menu, where the 3D section lives.
   -stereo3d starts the game in 3D; without it, turn 3D on from the menu (the choice is saved).

Steam's "Verify integrity of game files" puts Valve's module back: run install.sh again after it.

With more than one screen, the game opens on the screen that has the mouse. On KDE Plasma a window rule puts it on the TV every time: System Settings > Window Management > Window Rules, window class hl2_linux, position forced to the TV's corner, fullscreen forced.


PLAYING IN 3D

In the game: Options > Video, the 3D section:

- Stereo 3D: on or off.
- 3D format:
  Top and bottom, full (recommended): each eye rendered at your full resolution and shrunk into its half, supersampled and sharp.
  Side by side, full: the same, side by side.
  Top and bottom, and Side by side: each eye rendered at half the resolution; lighter, for weaker machines.
- 3D output (only when the game runs inside gamescope): 3D display, red/cyan anaglyph (CRT or modern screens), row-interleaved (passive 3D screens), checkerboard (DLP).
- Swap eyes: if the depth looks inside out.

Nothing changes until Apply, which reloads 3D once with all your choices.
Then set your TV to the same format with its 3D button (top and bottom, or side by side).

While 3D is on, the module turns motion blur off (it smears differently in each eye) and sets anisotropic filtering to 16x; your own values come back when 3D is turned off, or at the next start if the game quit in 3D.
The menus and the HUD are shown at full size, flat on the screen plane.


ANAGLYPH AND THE OTHER OUTPUTS: THROUGH GAMESCOPE

Red/cyan anaglyph (any colour screen), row-interleaved and checkerboard are drawn by gamescope, with the effect svrtv-anaglyph.fx that the module installs for it.
Two things keep the depth smooth there: the game must not wait for vsync inside gamescope (DXVK's d3d9.presentInterval = 0), and gamescope's own window must not wait either.
The second one is our change to gamescope, ValveSoftware/gamescope#2438 (open, 2026-09-28); with stock gamescope the depth can swim.
Do not use gamescope's -S stretch: it breaks the mouse.
The full recipe, measured: https://github.com/danielcamposramos/sony-bravia-linux/tree/main/tools/vr-stereo-spectator/anaglyph


SPECTATING IN 3D (SOURCETV AND THE OBSERVER CAMERAS)

Stereo here is the 2D game with a second camera, so every view the game already has gets its second eye, with no map or game changes: your own view, a spectator's in-eye, chase and free cameras, the cameras mappers place in levels, SourceTV's director, and demos.
SourceTV sends the game's state, not video: each viewer's game renders the picture, so one broadcast serves 2D and 3D viewers alike, each in the format they choose.
Half-Life 2 has no spectator mode; its demos (record, playdemo) play in 3D. The multiplayer Source games have the spectator cameras and SourceTV (see the next section).
Tested 2026-09-28 on Half-Life 2: Deathmatch built from our source, 64-bit, on a 3D TV: the spectator's free camera and a SourceTV demo, in 3D.
Known, and not the 3D: a SourceTV demo recorded on a listen server stopped at the same point in 2D and in 3D, also with no module loaded at all, with Source's own "Host_Error: CL_PreserveExistingEntity: missing client entity"; we are reporting it to Valve separately.


OTHER SOURCE GAMES (64-BIT)

The package also carries the module for the 64-bit Source engine (Half-Life 2: Deathmatch, Source SDK Base 2013 Multiplayer and its mods).
Give the game's folder to the installer: ./install.sh "/path/to/steamapps/common/<game folder>"
Launch options: -vulkan -vr -stereo3d
In our tests the 64-bit engine loaded the module only with -vr. The 3D menu is Half-Life 2's; there, 3D comes from -stereo3d, or vr_display_3d 1 and vr_display_apply in the console (vr_display_layout picks the format, as in the menu: 2 top and bottom full, 3 side by side full, 1 top and bottom, 0 side by side).
With Valve's current game code the module draws its own crosshair in every view, the spectator's chase and free cameras included; our source's client code places the game's own crosshair by the game's rules (first person and in-eye only), which is part of our pull request to Valve.
Tested with Half-Life 2: Deathmatch built from our source on Source SDK Base 2013 Multiplayer; Valve's own Half-Life 2: Deathmatch from Steam is not tried yet.
Online: the engine refuses secure (VAC) servers while an unsigned VR module is loaded. Use it offline, on LAN, and for demos.


THE MUZZLE FLASH, CHEATS AND ACHIEVEMENTS

In Half-Life 2's VR view the muzzle flash is drawn beside the gun, not on it.
The fix is one console setting, viewmodel_fov 90, and Half-Life 2 treats it as a cheat, so it needs sv_cheats 1.

With cheats (+sv_cheats 1 +viewmodel_fov 90): the muzzle flash sits on the gun, and Steam achievements are off while cheats are on.
Without cheats: achievements work, and the muzzle flash shows beside the gun. Everything else is the same.

This lasts until Valve accepts this use as not cheating.
Our pull request to Valve asks for exactly that; for Source games Valve builds from its public SDK (the 64-bit ones), the fix is already in the pull request's client code.


CAN THIS BE USED TO CHEAT?

Yes, and we say so plainly.
Stereo 3D needs a second camera: the game draws the world twice, once from each eye, a few centimetres apart.
A camera the game did not plan for is exactly what a cheat needs: moved further away, it could show what the player should not see from where they stand.
This module keeps the eyes at a normal human distance (about 64 mm), and its source code is public for anyone to check.
In multiplayer, the engine warns that an unsigned VR module blocks secure (VAC) servers: this is for single player.


WHAT IS NOT IN THIS BUILD

- Loading screens in 3D: they show in one eye. The game draws them straight to the screen while no 3D view is rendered, outside the path that puts the menus and HUD in both eyes; the fix is in Valve's engine, and our pull request asks for it.
- Frame packing (the HDMI 3D signal that switches a TV to 3D by itself): it needs the graphics driver to offer HDMI 3D modes; not in the menu yet.
- Spectating from a VR headset (someone plays in the headset while the PC screen shows both eyes in 3D): next.


UNINSTALL

Run ./uninstall.sh.
If the game last quit with 3D on, it asks you first to start the game, set Stereo 3D to off, Apply and quit, so your own crosshair, motion blur and filtering settings come back.
It then puts Valve's module back and removes the 3D menu.


IF SOMETHING GOES WRONG

The module writes a log next to itself: Half-Life 2/bin/svrtv.log (delete bin/svrtv.ini to stop logging).
Please report with that log: https://github.com/danielcamposramos/sony-bravia-linux/issues


SOURCE AND LICENSE

Source: https://github.com/danielcamposramos/source-sdk-2013 (branch stereo3d-full-res-wip, src/sourcevr_display), under the Source 1 SDK License; rebuild it byte for byte with src/sourcevr_display/build32-hl2.sh.
The story, measurements and test runs: https://github.com/danielcamposramos/sony-bravia-linux/tree/main/tools/vr-stereo-spectator
Built by Daniel Campos Ramos, with AI assistance (Claude); every run checked on a 3D TV by Daniel.
menu/gamepadui/options.res is the game's own options file with the 3D section added.
