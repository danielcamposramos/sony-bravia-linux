# Live recon: NVIDIA trains 10-bit where AMD trains 12-bit on the same sink (2026-09-22)

Context: during the #1382 stereo_allowed A/B probing, Daniel noticed the TV OSD
reporting lower signal depth on the NVIDIA input than on the AMD input. Verified
here in plain 2D desktop mode (no 3D involved, no session drop), both HDMI links
live simultaneously as extended-desktop outputs, KDL-46HX855 the sink for the AMD
head and a second HDMI input of the same set for the NVIDIA head.

## Measured

| layer | AMD (card0, HDMI-A-1) | NVIDIA proprietary 615.71.09 (card1, HDMI-A-2) |
|---|---|---|
| sink EDID deep color | DC_36bit + DC_30bit | DC_36bit + DC_30bit (same) |
| DRM connector `max bpc` | range [8, 16] = 16 | range [8, 16] = 16 (same) |
| debugfs `output_bpc` | `Maximum: 12` | `Maximum: 12` (same) |
| live trained depth, driver expose | none (no `Current` line) | none (no `Current` line) |
| `infoframes` debugfs dir | empty (hook not wired) | empty (hook not wired) |
| **TV OSD signal detail (2D, 1080p60)** | **12-bit** | **10-bit** |

[proven — Daniel, OSD read on both inputs while both links were live,
2026-09-22]. Windows control: the same TV reports 12-bit under Windows with the
same NVIDIA card [proven — Daniel, prior Windows use], so the delta is
Linux-driver-side, not hardware.

## Reading

The only layer that differs is NVKMS link policy: it accepts the EDID's 36-bit
declaration enough to surface `max bpc 16` / `Maximum: 12` upward, then trains
30-bit anyway. [qualified] The mechanism (fixed 30-bit cap vs conservative
selection) is not visible from open code.

This is the third measured symptom of one shape of problem in NVKMS:

1. the EDID mode list is narrowed before DRM (17 modes vs 51 on unpatched
   nouveau, same EDID — run12/run18);
2. `stereo_allowed` is a correct opt-in with nothing to admit because no
   EDID stereo variant ever becomes a DRM mode (run18 A/B, #1382);
3. deep color is advertised upward (12-bit max) but trained at 10 on the wire.

[qualified] The same NVKMS EDID-surface narrowing may also sit behind the
earlier TaB troubles (runs 14–16: engage-but-black/mute on some timings before
run17 passed at 1080p24), i.e. 3D-structure handling, but that link is
circumstantial until a VSDB-aware read of NVKMS EDID parsing exists.

Method notes for reproduction: outputs were enabled from the live Plasma/Wayland
session (`kscreen-doctor output.HDMI-A-1.enable output.HDMI-A-2.enable`); legacy
`modetest -M nvidia-drm -s <conn>:1920x1080-60` is refused while the session
holds DRM master on card1 (expected).
