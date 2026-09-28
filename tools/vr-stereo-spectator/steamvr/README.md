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

**2026-09-28, first runs (SteamVR 2.17.10, Linux, KWin 6.7.4 on Wayland):**

- **The driver works.** SteamVR loads it, reads its settings and takes it as the headset (`Loaded server driver stereodisplay`; `ActualTrackingSystemName: stereodisplay`). It has to be installed where SteamVR's Steam Runtime container can see it: `~/.local/share/steamvr-drivers/stereodisplay` (a path under `/K3D` is "not a directory" from inside).
- **SteamVR on Linux draws no windowed headset.** Its compositor switched to the desktop-window mode the sample asks for (`Forcing debug mode for stereodisplay driver`), then refused: "CHmdWindowSDL: VR requires direct mode". On Linux the compositor drives the headset's display itself, leased from the desktop compositor (DRM lease, `wp_drm_lease_device_v1`): "Tried to find direct display through Wayland: (nil)", `VRInitError_Compositor_CannotDRMLeaseDisplay`.
- **What a lease needs:** KWin offers an output for leasing only when the kernel marks its connector non-desktop (`KWin::DrmConnector::isNonDesktop`), and the kernel sets that from the display's EDID (known headsets, or a DisplayID extension declaring a head-mounted display). The next step is the direct-mode driver: the display reported as real, identified by the 3D display's EDID, and the 3D display marked non-desktop while SteamVR runs.
- **Along the way:** SteamVR's compositor picks Wayland whenever `WAYLAND_DISPLAY` is set (it ignores `SDL_VIDEODRIVER`); a Steam started from an environment without the session's runtime folder breaks every socket its games need (`steamvr-3dtv.sh` repairs that); under KWin, gamescope's X11 window opens under the mouse, not on `--display-index` (a KWin rule places it, as the HL2 bench does). The compositor lists `VK_NV_display_stereo` among NVIDIA's Vulkan instance extensions: stereo on a display the application drives directly, the NVIDIA route to HDMI 3D to look into.

`steamvr-3dtv.sh`: SteamVR inside gamescope for the display (launch options `sh ~/.local/bin/steamvr-3dtv %command%`), logging to `~/.local/state/steamvr-3dtv.log`, settings in `~/.config/steamvr-3dtv.env`.
