# KWin stereo 3D: the first runs on real TVs, 2026-10-01 to 10-03

Evidence for the KWin stereo work under review in [plasma/kwin #324](https://invent.kde.org/plasma/kwin/-/work_items/324). The design in one page: [STEREO3D.md](https://invent.kde.org/danielcamposramos/kwin/-/blob/stereo3d/STEREO3D.md). Code: the `stereo3d` branch of [invent.kde.org/danielcamposramos/kwin](https://invent.kde.org/danielcamposramos/kwin/-/tree/stereo3d).

Hardware: a Sony KDL-46HX855 (AMD iGPU, amdgpu) and a Sony KDL-46EX725 (RTX 3060), both 2011-era 3D TVs that declare HDMI 1.4 3D modes and 12-bit deep colour (225 MHz TMDS). Kernel 7.3.0-rc1 with the HDMI 3D patches. Photos taken with a phone by Daniel; the TVs' own information banners are the readout. GPS data was removed from the photos; everything else is as taken.

## The display's 3D modes in KDE's display settings (2026-10-01, 03:11 to 03:14)

Both TVs, each in frame packing and in half side by side and top and bottom, every mode chosen in KDE's own display settings: the output mode changer (KScreen) lists the 3D modes beside the 2D ones and KWin switches the TV into 3D (Daniel, the same night). How to read the photos: the mouse pointer rests on the active mode in the list, and the TV's own on-screen display (the banner: resolution, 12bit, 3D, "3D: Sim") shows what the set is receiving, so each photo pairs the mode chosen with the display's readout.

KWin branch at [92dfde1](https://invent.kde.org/danielcamposramos/kwin/-/commit/92dfde1) (`drm: side by side (full), and 3D layouts for displays without 3D detection`), with [0672162](https://invent.kde.org/danielcamposramos/kwin/-/commit/0672162) (`drm: list a display's HDMI 3D modes with its other modes`) and [57b02a2](https://invent.kde.org/danielcamposramos/kwin/-/commit/57b02a2) (frame packing modes) below it.

- [IMG_20261001_031131.jpg](photos/IMG_20261001_031131.jpg): the HX855 in a 3D mode chosen in the display settings. Its banner: **16:9, 1080p HD, 12bit, 3D**, and "3D: Sim" (on). The flat desktop is in both eyes.
- [IMG_20261001_031147.jpg](photos/IMG_20261001_031147.jpg), [IMG_20261001_031255.jpg](photos/IMG_20261001_031255.jpg), [IMG_20261001_031403.jpg](photos/IMG_20261001_031403.jpg): the refresh-rate list on the display settings page, with the 3D modes listed beside the 2D ones and labelled, for example "60.00 Hz (3D top and bottom)" and "(3D frame packing, suggested for games)" / "(… suggested for movies)". Both TVs and the 2D monitor are on the page.
- [IMG_20261001_031238.jpg](photos/IMG_20261001_031238.jpg): the EX725 (HDMI 4) in 3D from the 3060: **16:9, 1080p HD, 12bit, 3D**, "3D: Sim".
- [IMG_20261001_031354.jpg](photos/IMG_20261001_031354.jpg): the HX855 again, 12bit 3D, with the mode list open.

## A stereo window on an ordinary desktop (2026-10-01, 20:20)

KWin at [128a0d6](https://invent.kde.org/danielcamposramos/kwin/-/commit/128a0d6) (`Stereo content: apply the rule when a Wayland window opens`) on [01e24b6](https://invent.kde.org/danielcamposramos/kwin/-/commit/01e24b6) (`Stereo content: windows whose picture holds one view per eye`).

- [IMG_20261001_202022.jpg](photos/IMG_20261001_202022.jpg): the HX855 in top and bottom 1080p60, banner **1080p HD, 12bit, 3D**, "3D: Sim". An mpv window plays a side by side (half) test clip whose views read LEFT and RIGHT, marked as stereo by a KWin window rule: KWin sends each half of the window to its eye, while the rest of the desktop (icons, widgets, clock) stays flat around it. The doubled outline on "RIGHT" is the phone catching the TV's alternating eye frames without glasses.
- [scripts/rule.sh](scripts/rule.sh): the window rule, set with `kwriteconfig6` (`stereo3d=sbs-half` for mpv's window class) and applied with `qdbus6 org.kde.KWin /KWin reconfigure`. [scripts/play-clip.sh](scripts/play-clip.sh) starts the clip; [scripts/session.env](scripts/session.env) points a shell at the desktop session.
- The clip (42 MB, not included): 60 s of 1080p24 side by side (half), the left view labelled LEFT and the right labelled RIGHT, with the H.264 frame-packing SEI (side by side).

Later that night, with the TV switched from top and bottom to frame packing 1080p30 while the clip played, the window kept its 3D with no restart: the window declares its picture and KWin chooses the output format every frame.

## A game handing over two full eyes (2026-10-02)

KWin at [4714c8e](https://invent.kde.org/danielcamposramos/kwin/-/commit/4714c8e) (`Stereo content: fullscreen keeps the program's frame, input in the left view`) and [92b0714](https://invent.kde.org/danielcamposramos/kwin/-/commit/92b0714).

- [2026-10-02-hl2-version-b-frame-3840x1080.png](photos/2026-10-02-hl2-version-b-frame-3840x1080.png): Half-Life 2 rendering two full 1920x1080 eyes side by side in one 3840x1080 window, declared to KWin as full side by side; KWin showed it in 2D, side by side (half), top and bottom (half) and frame packing 720p60 on the HX855, rendered on the RTX 3060.
- [2026-10-02-hl2-version-b-menu-sheet-1920x1080.png](photos/2026-10-02-hl2-version-b-menu-sheet-1920x1080.png): the game's 2D menu sheet at its ordinary size, drawn into both eyes at screen depth.

## One window across a 3D TV and a 2D monitor (2026-10-03, 20:51)

KWin package 4:6.7.4-2+stereo3d11, the same LEFT/RIGHT clip in mpv under the same window rule ([scripts/rule.sh](scripts/rule.sh), [scripts/play-clip.sh](scripts/play-clip.sh)). The HX855 (HDMI-A-1) in frame packing 1080p30, "30.00 Hz (3D frame packing)" in the display settings, with the AOC LE26W154 (DP-1), a 2D monitor, to its right; both on the AMD iGPU.

- [IMG_20261003_205141.jpg](photos/IMG_20261003_205141.jpg): the mpv window on the 2D monitor shows the left view only (LEFT). That is the design: two eyes reach a screen only when a 3D mode is active, and a 2D output takes the left view. The display settings on the HX855 show its frame packing mode.
- [IMG_20261003_205154.jpg](photos/IMG_20261003_205154.jpg): the same window dragged across both monitors. The part on the HX855 is in 3D (the phone caught the TV's right-eye frame: "RIG"), and the part on the 2D monitor shows the left view ("EFT"). One window, two outputs, each output taking from the same two eyes what it can show: the output is the last step, per monitor.

Done by Daniel Ramos, with an AI assistant doing the legwork under his direction; the TV readings are his.
