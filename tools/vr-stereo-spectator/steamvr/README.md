# SteamVR on a 3D display: the stereodisplay driver

Everything SteamVR draws (SteamVR Home, the dashboard with Big Picture, any VR game, the stereo screenshots it keeps) shown in stereo on a 3D television, projector or monitor, with the display as the headset. Daniel, 2026-09-28: "we should port VR Big Picture to 3DTVs". It is the spectator at the level of SteamVR instead of one game, and where the stereo captures get reviewed.

It is Valve's own virtual-headset sample, OpenVR's `samples/drivers/drivers/simplehmd` (BSD-3-Clause, [LICENSE-OPENVR](LICENSE-OPENVR)), whose display is already a desktop window with each eye in half of it and no lens. The first commit here is the sample unchanged; the changes for a 3D display are their own commit:

- **Layout:** side by side (left eye left) or top and bottom (left eye on top), as HDMI 1.4 packs them; the display stretches each half back to the whole screen.
- **Eyes:** [FORMULA.md](../FORMULA.md), section 1: a window, not a headset. The eyes look straight ahead, half the IPD to each side, and each eye's view is shifted so both frame the same screen at `screen_distance_meters`, where depth is zero.
- **Head:** fixed at `head_height_meters`, no neck model; the sample's up-and-down test motion is gone.
- **Refresh:** the display's (`display_frequency`, 60 Hz).

Settings (`stereodisplay/resources/settings/default.vrsettings`, section `stereodisplay_display`): the window's place and size on the desktop (the 3D display's output), the eyes' render size (1920x1080 each by default, full size, as the module's full formats), `layout` (`sbs` or `tab`), `fov_horizontal_degrees`, `screen_distance_meters`, `head_height_meters`.

## Build and register

    ./build.sh                     # out/stereodisplay/, in the Steam Runtime SDK image
    ~/.steam/steam/steamapps/common/SteamVR/bin/linux64/vrpathreg.sh adddriver "$PWD/out/stereodisplay"

## Status

Built 2026-09-28; not yet run. Open questions for the first run: whether SteamVR on Linux shows a desktop-window headset (its Linux use has been direct-mode headsets), and how the dashboard is driven without VR controllers (a gamepad, or the sample controller driver).
