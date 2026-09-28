STEREO 3D FOR HALF-LIFE 2 (WINDOWS)
VR Stereo Spectator, test build of 2026-09-28

Half-Life 2 in real stereo 3D on a 3D TV, projector or monitor.
The game already carries Valve's VR render path from 2013: this module presents your 3D display to the engine as its headset, so the engine itself renders both eyes with real stereo geometry, and your display unpacks them.
No per-game shader fixes, no wrapper around the renderer.

Status of this build: the same code has been played on a 3D TV on Linux, every format (2026-09-24 to 2026-09-28).
The Windows build loads and passes its geometry test outside the game (under Wine), both 32-bit and 64-bit.
Its first run inside the game on Windows is the test this package is for.


WHAT YOU NEED

- Half-Life 2 from Steam, the Windows version, as installed by Steam (no mods needed).
- A 3D display that accepts top and bottom or side by side over HDMI (most 3D TVs of the 2010s do), with its glasses.
- About one minute.


INSTALL

1. Start Half-Life 2 once from Steam and quit, so Steam finishes its first-run setup.
2. Double-click install.bat.
   It finds Half-Life 2 in your Steam libraries (or drag the "Half-Life 2" folder onto install.bat).
   It keeps Valve's own module as bin\sourcevr.dll.valve, installs ours, and adds the 3D section to the game's options menu.
   Today's Half-Life 2 runs a 32-bit engine, so it gets the 32-bit module; a 64-bit engine, where a game has one, gets the 64-bit module.
3. In Steam: Half-Life 2 > Properties > Launch options, put one of these two lines (see "The muzzle flash, cheats and achievements" below):

   -gamepadui -stereo3d
   -gamepadui -stereo3d +sv_cheats 1 +viewmodel_fov 90

   -gamepadui turns on the game's newer menu, where the 3D section lives.
   -stereo3d starts the game in 3D; without it, turn 3D on from the menu (the choice is saved).

Steam's "Verify integrity of game files" puts Valve's module back: run install.bat again after it.


PLAYING IN 3D

In the game: Options > Video, the 3D section:

- Stereo 3D: on or off.
- 3D format:
  Top and bottom, full (recommended): each eye rendered at your full resolution and shrunk into its half, supersampled and sharp.
  Side by side, full: the same, side by side.
  Top and bottom, and Side by side: each eye rendered at half the resolution; lighter, for weaker machines.
- Swap eyes: if the depth looks inside out.

Nothing changes until Apply, which reloads 3D once with all your choices.
Then set your TV to the same format with its 3D button (top and bottom, or side by side).

While 3D is on, the module turns motion blur off (it smears differently in each eye) and sets anisotropic filtering to 16x; your own values come back when 3D is turned off, or at the next start if the game quit in 3D.
The menus and the HUD are shown at full size, flat on the screen plane.


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

- Red/cyan anaglyph, row-interleaved and checkerboard outputs: Linux only for now (they run through gamescope).
- Frame packing (the HDMI 3D signal that switches a TV to 3D by itself): it needs the graphics driver to offer HDMI 3D modes; not in the menu yet.
- Spectator mode (someone plays in a VR headset while the PC screen shows both eyes in 3D): next.


UNINSTALL

Double-click uninstall.bat.
If the game last quit with 3D on, it asks you first to start the game, set Stereo 3D to off, Apply and quit, so your own crosshair, motion blur and filtering settings come back.
It then puts Valve's module back and removes the 3D menu.


IF SOMETHING GOES WRONG

The module writes a log next to itself: Half-Life 2\bin\svrtv.log (delete bin\svrtv.ini to stop logging).
Please report with that log: https://github.com/danielcamposramos/sony-bravia-linux/issues


SOURCE AND LICENSE

Source: https://github.com/danielcamposramos/source-sdk-2013 (branch stereo3d-full-res-wip, src/sourcevr_display), under the Source 1 SDK License.
The story, measurements and test runs: https://github.com/danielcamposramos/sony-bravia-linux/tree/main/tools/vr-stereo-spectator
Built by Daniel Campos Ramos, with AI assistance (Claude); every run checked on a 3D TV by Daniel.
menu\gamepadui\options.res is the game's own options file with the 3D section added.
