# Draft 03: comment on ValveSoftware/Source-1-Games #1013 ("GL Stereoscopic 3d option", 2013, open)

Status: DRAFT for Daniel. Post after draft 01, and its number, #8297, is filled in.
Target: https://github.com/ValveSoftware/Source-1-Games/issues/1013

---

Thirteen years later, side-by-side and top-and-bottom 3D for Half-Life 2 exist, on the path this thread guessed: the VR mode.
The game's VR interface already renders two eyes, so a replacement `sourcevr.so` points them at a 3D television or projector instead of a headset, with the HUD and crosshair on the screen plane.
It runs on Linux with `-vulkan`: https://github.com/danielcamposramos/sony-bravia-linux/tree/main/tools/vr-stereo-spectator
The engine-side issues it works around are in #8297.
