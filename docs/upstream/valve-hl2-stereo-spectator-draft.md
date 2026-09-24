# Draft: Half-Life 2 VR mode on a 3D display (for ValveSoftware/Source-1-Games)

Status: DRAFT, raw material for Daniel. Not posted.
Target: https://github.com/ValveSoftware/Source-1-Games/issues (Half-Life 2, Linux).
Evidence: `tools/vr-stereo-spectator/sourcevr/README.md` and `FORMULA.md` in this repository; logs under `/K3D/temp/hl2-bench/` (local).

---

**Title:** Half-Life 2 (Linux): VR mode drives a 3D TV with a replacement sourcevr.so; five things that would make it clean

Half-Life 2 plays in stereo 3D on a 3D television on Linux, through the game's own VR interface.
I wrote a replacement `sourcevr.so` that implements `SourceVirtualReality001` for a display instead of a headset: off-axis eyes, side by side or top and bottom, no head tracking.
It is public, under the Source 1 SDK License: https://github.com/danielcamposramos/sony-bravia-linux/tree/main/tools/vr-stereo-spectator

**Tested:** current Half-Life 2 build (`hl2_complete`), Linux native, `-vulkan`, RTX 3060 on the proprietary driver, Sony KDL-46HX855 and KDL-46EX725 in side-by-side 3D.
A full playthrough section worked: save loads, level transitions, shadows, HUD, menus, no crash.

Getting there needed workarounds for five behaviours of the VR mode.
None of them matters for a headset the way it does for a display, which is why I am reporting them.

**1. `sourcevr_<game>.cfg` does not run.**
When VR mode starts from `ShouldForceVRMode()`, neither `hl2/cfg/sourcevr_hl2.cfg` nor `hl2_complete/cfg/sourcevr_hl2_complete.cfg` executed (an `echo` line in each never printed with `-condebug`).
So your own Half-Life 2 VR settings (`vr_first_person_uses_world_model 0`, `hud_draw_fixed_reticle 0`, `r_flashlightscissor 0`) never apply.
The module now issues them itself.

**2. `CreateRenderTargets()` is never called, and `_rt_gui` does not exist.**
With VR forced at start, the engine never called `CreateRenderTargets()`, not even with `VRModeAdapter "0"` in `videoconfig_linux.cfg`.
The client then looks for `_rt_gui` (`couldn't find materials/_rt_gui.vtf`), and `vgui/inworldui` is set up against the missing texture and draws the error checkerboard for the rest of the session.
The module creates its targets on first use and pastes the HUD with another material.

**3. The crosshair is painted for a 640x480 screen.**
In VR mode the client paints the crosshair into each eye at the centre of its 640x480 UI screen, unscaled (measured at eye pixel 314,240 of a 960x1080 eye).
At any other eye size it lands off-centre.
The module offers 640x480 eyes, or turns `crosshair` off and draws `crosshair_default` itself.

**4. The muzzle flash sprite misses the gun, and `viewmodel_fov` is a cheat.**
In VR mode the weapon is drawn with the eye projection, but `FormatViewModelAttachment()` still converts the attachment from `viewmodel_fov` to the world's field of view.
With `viewmodel_fov 90` (under `sv_cheats 1`, in a demo) the sprite sits exactly on the muzzle.
**The ask:** allow `viewmodel_fov` while VR mode is active, or skip the conversion when the weapon uses the eye projection.
A stereo view changes only the cameras, so it gives no advantage the 2D view does not have.

**5. OpenGL crashes in VR mode.**
With `-opengl` (ToGL), every VR run that lasted past 20 seconds crashed at about that point in the material system's render thread (`materialsystem.so`, `studiorender.so`, `shaderapidx9.so`, then libc).
With `-vulkan` the same runs are stable.
Core dumps are available.

Why this matters beyond one game: a VR engine already renders two eyes, so it can drive every 3D television, projector and monitor people still own, with no headset.
Half-Life 2 showed what has to change for that, and the list is short.
It is written up here: https://github.com/danielcamposramos/sony-bravia-linux/blob/main/tools/vr-stereo-spectator/FORMULA.md

---

Notes for Daniel (not for posting):
- Disclosure line, if you want it, goes once at the end, per the repo's rule.
- Point 1's evidence: the `echo` markers (2026-09-24 16:23, runs a10/a13); point 2: module log and console; point 3: `svrtv-frame.tga` dump; point 4: Daniel's eye, runs with `viewmodel_fov 75` (almost) and `90` (exact); point 5: coredumps 15:34, 16:23, 16:25 and the a08/a10/a13/a14/a19 runs.
- The first-playback stop of timed demos (2 frames) is a separate, non-VR issue; not in this draft.
