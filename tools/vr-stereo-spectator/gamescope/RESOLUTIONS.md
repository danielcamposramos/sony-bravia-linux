# gamescope and stereo frames: what it delivers stock, and where our formats fit

Read from gamescope's source on 2026-09-27 (upstream `master` at `ad2763d`, 2026-09-23, in our fork `danielcamposramos/gamescope`; the build we run is Debian's 3.16.24 with `nested-present-mode.patch`, so line numbers below are upstream's). Measurements referenced are our own runs, named where used. The Steam Frame figures are reported, not measured here.

## 1. The game's screen is the nested screen

- Its size is `-w`/`-h`. Without them it is the output size; with `-h` alone, the width is 16:9 of it (`main.cpp` 1050-1061).
- Each Xwayland server gets a virtual output whose one real mode is that size (`wlserver_set_xwayland_server_mode`, `wlserver.cpp` 3566), and Xwayland runs with `force_xrandr_emulation = true` (`wlserver.cpp` 1877-1882). So a game sees the nested size plus smaller emulated modes, which gamescope scales for it, and never a mode larger than the nested screen.
- That is the source-level cause of run q18: 3840x1080 and 1920x2160 were never offered inside a 1920x1080 nested screen, and every DXVK swapchain stayed 1920x1080.

## 2. Resizing the nested screen at run time

- The root-window property `GAMESCOPE_XWAYLAND_MODE_CONTROL` takes four values: server, width, height, allowSuperRes (`steamcompmgr.cpp` 7225-7260). Without allowSuperRes the size is capped at the output; with it, any size ("super resolution", larger than the output and scaled down). gamescope deletes the property once the root has the new size. Our q21 build uses it; that branch has an open regression (the mouse pinned inside gamescope), to be isolated against q17 first.
- After a resize every window's placement is re-armed ("Screen-sized is relative to the screen", `steamcompmgr.cpp` 6150-6163).

## 3. From the game's image to the output

- ReShade runs first, on the game's buffer at the game's size (our anaglyph, rows and checkerboard effects live here).
- The scaler maps that image onto the output (`-W`/`-H`), `calc_scale_factor_scaler`, `steamcompmgr.cpp` 1956-2000: `auto` and `fit` scale uniformly and keep the aspect (bars), `fill` scales uniformly and crops, `stretch` scales each axis on its own, `integer` uses whole multiples; `-m` caps the scale. Filters: `linear`, `nearest`, `fsr`, `nis`, `pixel`, `sgsr`.
- **The scale math uses the nested size given at startup** (`g_nNestedWidth`/`g_nNestedHeight`), and a mode-control resize does not update it (its only other writer, `steamcompmgr.cpp` 10268, runs when the output itself changes). So after resizing to 1920x2160 on a 1920x1080 output, `auto`/`fit` shows the whole frame at half size, 960x1080 with bars, and only `stretch` produces the 1920x1080 top-and-bottom frame a TV expects. The full formats therefore need `-S stretch` today (or a patch, section 7). **But `-S stretch` breaks the relative mouse** in the build we run (3.16.24 with our patch), even at an exact 1:1 scale: run q23 (2026-09-27) moved the aim the wrong way and snapped it back to the centre, where run q22, identical without stretch, was free. The same class is open upstream: [#2042](https://github.com/ValveSoftware/gamescope/issues/2042) (camera mouse constrained to a small box or locked on stretched resolutions) and [#1605](https://github.com/ValveSoftware/gamescope/issues/1605) (the mouse leaving the game with `-S stretch`).

## 4. The output

- Nested (`sdl`, `wayland`): a window on the desktop, the path we use.
- Embedded (`drm`, SteamOS): gamescope drives the screen itself and asks the kernel only for `DRM_CLIENT_CAP_ATOMIC` (`Backends/DRMBackend.cpp` 1516), never `DRM_CLIENT_CAP_STEREO_3D`. Our own probe measured what that means on the KDL-46HX855: 22 modes and 0 stereo without the capability, 51 modes and 29 stereo with it (`tools/stereo-kms-probe/`). On SteamOS, then, no frame packing and no automatic 3D signal to the TV: side by side and top and bottom work, switched on the TV by hand.
- OpenVR (`--backend openvr`): the output becomes a SteamVR overlay, a virtual screen in the headset, with the `--vr-overlay-*` options. It is always shown as one flat image: the backend never sets a stereo flag (`Backends/OpenVRBackend.cpp`), although SteamVR's overlay API has `VROverlayFlags_SideBySide_Parallel`, "renders 50% of the texture in each eye" (`openvr.h`, bundled copy, line 3850). There is no top-and-bottom flag, so side by side is the headset format.

## 5. The eyes, on the module's side

The module makes one pair of eye surfaces per eye size, on first use, and keeps them (`select_targets`/`make_targets`; sizes from `eye_size()` and `half()`), for a 1920x1080 2D size:

| format | eye surface | frame |
|---|---|---|
| half side by side | 960x1080 | 1920x1080 |
| half top and bottom | 1920x540 | 1920x1080 |
| full side by side | 1920x1080 | 3840x1080 |
| full top and bottom | 1920x1080 | 1920x2160 |
| frame packing 1080p | 1920x1080 | 1920x2205 |

The projection needs no change for the full formats: it is built on the displayed 16:9 aspect whatever the packing, and a full eye is 16:9. So the full formats already render full-resolution eyes; what fails is the destination, a frame that does not fit the screen gamescope gives the game. Daniel's q17 observations match: full top and bottom showed a single eye, full side by side with anaglyph went all red (the right eye outside the buffer). `SVRTV_EYE=WxH` remains the developer override for rendering eyes at another size.

## 6. Steam Frame (reported)

- Displays: 2160x2160 per eye, LCD, pancake lenses, up to 144 Hz (Linus Tech Tips, *Steam Frame Review*).
- Chip: Snapdragon 8 Gen 3 ([VR.org](https://vr.org/steam-frame-games)); LTT calls it "a two generation old cell phone chip". SteamOS on ARM, with Proton and FEX for x86 games.
- Flat games on a virtual screen: LTT played Just Cause 2 "on a 150in virtual screen" at 1080p; flat-game certification asks for 720p at 30 fps (VR.org). Whether that screen is gamescope's OpenVR overlay is likely but not stated in Valve's documentation ([Steamworks](https://partner.steamgames.com/doc/steamhardware/steamframe)).
- For stereo in a headset, half side by side gives each eye 960 pixels across; full side by side (3840x1080) gives each eye 1920, close to what a 2160-wide panel can show.

## 7. What this points to

In gamescope, each small and in the spirit of [ValveSoftware/gamescope#2438](https://github.com/ValveSoftware/gamescope/pull/2438):

1. **Stereo modes on SteamOS:** set `DRM_CLIENT_CAP_STEREO_3D`, and let a game ask for an HDMI 3D mode through a root-window property, the pattern gamescope already uses (mode control, ReShade effect and technique). The kernel side can live in SteamOS's own kernel (for amdgpu, the HDMI 1.4 3D series already measured on the KDL-46HX855, all three layouts passing (run 11)) without waiting for mainline.
2. **A stereo option for the OpenVR overlay** (for example `--vr-overlay-stereo sbs`, setting `VROverlayFlags_SideBySide_Parallel`), so a full side-by-side game shows in 3D on the virtual screen of any SteamVR headset, the Frame included.
3. **The scale math after a resize:** use the live nested size, so the full formats map correctly without forcing `stretch`.

**Resolved in the module instead (2026-09-28, run q24):** the full formats no longer need a bigger screen. Each eye is rendered at the whole 2D size and shrunk into the frame the screen already has, supersampled, so nothing in gamescope is resized or stretched and the mouse stays free. Daniel: full top and bottom is the new recommended default. A larger frame (a 4K passive set, the Steam Frame's overlay) comes from starting the game's screen at that size, never from a resize at run time; item 2 above is the path for the headset.
