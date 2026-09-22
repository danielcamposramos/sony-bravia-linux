# Live recon: NVIDIA trains 10-bit where AMD trains 12-bit on the same sink (2026-09-22)

Context: during the #1382 stereo_allowed A/B probing, Daniel noticed the TV OSD
reporting lower signal depth on the NVIDIA input than on the AMD input. Verified
here in plain 2D desktop mode (no 3D involved, no session drop), both HDMI links
live simultaneously as extended-desktop outputs, KDL-46HX855 the sink for the AMD
head and a second HDMI input of the same set for the NVIDIA head.

Bench identification (owner-provided, 2026-09-22): the AMD head is the iGPU of a
Ryzen 5 5500G (Cezanne, Vega) on an ASUS TUF GAMING X570-PLUS/BR board; the
NVIDIA head is a GALAX GeForce RTX 3060 (GA106, 12 Gb VRAM) in the same machine.
This is also the bench behind #1384's machine line.

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

## Tracker sweep 2026-09-22 — no existing report of this symptom anywhere

Ran before any filing decision (owner-directed). Queries against
NVIDIA/open-gpu-kernel-modules, issues+PRs, all states: "color depth",
"bit depth", "deep color", "10 bit", "12 bit", "bpc", "banding", "HDR",
"ycbcr", "limited range", "422". **No open or closed issue describes this
symptom** — identical EDID deep-color declaration, identical exposed DRM
ceilings, yet the link trains 10-bit where another driver trains 12, with
Windows unaffected. Our eventual filing would be the first.

Same-shape siblings found, all independent reporters/hardware, each another
axis of the same NVKMS-narrows-the-EDID-surface family:

- **#1348** (2026-09-10, RTX 5090 + Samsung Odyssey G95NC, **615.71.09** —
  this measurement's driver): HF-VSDB `DSC_MaxSlices=7` parsed as 12
  slices @ 600 MHz, **forcing YCbCr 4:2:2 limited** on HDMI 2.1. A VSDB
  parse that narrows the link's color format — the closest sibling, same
  version. Zero maintainer replies as of sweep date.
- **#1369** (2026-09-21): 3440x1440@240 pruned after a sink power cycle
  with an identical EDID, Windows unaffected — mode-enumeration narrowing,
  sibling to our 17/51 prune.
- **#1184**: EDID `Max_FRL_Rate=6` ignored, capped at 4K60 on a
  force-enabled connector — another declared capability dropped.
- **#1285 / #779 / #933** (RTX 50-series): HDR activation failures —
  `Colorspace` atomic commit EINVAL, HDR property absent, HDR refusing to
  enable. HDR10's common HDMI transport is 10-bit YCbCr 4:2:2 carried at
  12-bit container depth, so a driver that narrows wire depth and refuses
  colorimetry would land in exactly this family. [qualified] Connective
  tissue to this measurement, not a proven link.
- **#1101**: HDR DRM properties missing on force-enabled connectors —
  reported fixed on 610.43.02, i.e. the open glue *can* expose the HDR
  property surface once it is wired (precedent for the stereo lane too).

Test-scope caveat (owner's position, recorded verbatim in substance): no
bench in this project owns an HDR display, so the HDR-family connection is
argued from the transport mechanics above and from the sibling tickets —
it is NOT measured here. The owner assesses the HDR failures on NVIDIA
cards as certainly related to this color-depth bug; this document keeps
the [qualified] marker on the mechanistic chain until an HDR-capable sink
confirms it on the link.
