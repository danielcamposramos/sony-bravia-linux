# NVIDIA mode-list issue 1: CTA VICs only at the 1000/1001 rate (draft, ON HOLD)

**Status:** text approved by the owner on 2026-09-23. It is **not filed**. The owner is holding it because of timing: Andy Ritger has just answered #1382 and #1384, and our kapi question on #1382 is still waiting for his reply.

This is the first of the "small separate issues, one bug each" promised on [#1384](https://github.com/NVIDIA/open-gpu-kernel-modules/issues/1384#issuecomment-5787595679).

## Title

nvtiming: CTA-861 VICs are added only at the 1000/1001 rate, so 24.000/30.000/60.000 Hz modes are missing

## Body

For each VIC in the EDID's Video Data Block, `parse861bShortTiming()` adds one timing, at the rate stored in `EIA861B[]`.
For the 59.94/60 family that is the 1000/1001 rate: 59.94, 29.97 or 23.976 Hz.
The integer-rate version of the same VIC (60, 30 or 24 Hz) is never added.
It only appears when the EDID also carries a DTD for it.

CTA-861 defines these VICs at both rates.
The table's own comments say so, for example `@23.97/24 (Format 32)`.
The DRM core adds both rates (`add_alternate_cea_modes()` in `drm_edid.c`).

**Measured** on a Sony KDL-46HX855 (EDID attached), RTX 3060, driver 615.71.09, kernel 7.0.10:

- nvidia-drm lists 17 modes. nouveau and amdgpu list 22 distinct timings from the same EDID.
- Missing on NVIDIA: 1920x1080 at 24.000 and 30.000 Hz (VIC 32, 34), 1280x720 at 24.000 and 30.000 Hz (VIC 60, 62), 720x480 at 60.000 Hz (VIC 2, 3), 640x480 at 60.000 Hz (VIC 1).
- 1080p60 and 720p60 are present at 60.000 Hz only because this EDID also has DTDs for them.

**Proposed fix** (patch attached): after each such SVD timing, add the integer-rate twin with the same VIC.
The sink's native flag stays on the table rate.

**Tested:** I ran the timing library in userspace on this EDID.
Before: 28 timings. After: 40.
The 12 added timings are exactly the integer-rate twins of VICs 1, 2, 3, 4, 5, 6, 7, 16, 32, 34, 60 and 62.
The kernel modules build cleanly with the patch.
BENCH_RESULT_LINE

Would you like this as a pull request?

Attachments: `hx855-edid.bin`, `nvidia-615.71.09-cta-dual-rate-vics.patch`, `run29` log.

## Before filing

1. Run the bench harness and replace `BENCH_RESULT_LINE` with the measured result. Predicted: nvidia-drm goes from 17 to 23 modes, adding 1080p24/30, 720p24/30, 480p60 and 640x480 at the integer rates. That is 23 rather than 22 because NVIDIA keeps a near-duplicate 640x480 at 25.17 MHz (see note 2 below).
   `sudo systemd-run --unit=nvidia-cta-dualrate --collect sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nvidia-cta-dualrate-probe.sh`
   The harness swaps only `nvidia_modeset` (patched) and `nvidia_drm` (stock, reloaded on top). The nvidia core and CUDA containers are not touched. The desktop goes down for the swap and comes back by itself. Log: `/K3D/temp/run29-nvidia-cta-dualrate-probe.log`; copy it to `tools/stereo-modeset/` after the run.
2. Push branch `fix-cta-dual-rate-vics` to the fork only if Andy says he wants a pull request.

## Kept out of this issue on purpose (one bug each)

1. **No interlaced modes reach DRM.** The stock parser already produces 1080i and 480i/576i timings from this EDID, and none appears in nvidia-drm's list. The TV declares 3D frame packing on VIC 5 and VIC 20 (1080i), so this blocks the broadcast-3D formats. nouveau and amdgpu list no interlaced 2D modes on this setup either, so it needs its own measurement first.
2. **Pixel clocks are rounded to 10 kHz.** `parse861bShortTiming()` sets `pclk1khz = pclk * 10`, so 148.3516 MHz becomes 148.350 MHz and 27.027 MHz becomes 27.030 MHz. `RRx1kToPclk1khz()` already exists and gives 1 kHz precision. The error is within HDMI tolerance, but it also leaves 640x480 at 25.170 and 25.175 MHz as two separate entries. The patch above keeps the existing rounding, so it changes one thing only.

## Evidence

- Patch: `docs/upstream/nvidia-615.71.09-cta-dual-rate-vics.patch` (commit 66e733c on branch `fix-cta-dual-rate-vics` in `/K3D/temp/nvidia-open-cta-wt`, based on tag 615.71.09).
- Built module: `/K3D/temp/nvidia-open-cta-wt/kernel-open/nvidia-modeset.ko`, sha256 prefix `db60b86af15cc8b0`, vermagic matches the running kernel. Build recipe: `IGNORE_CC_MISMATCH=1 CC=gcc-15 make modules -j$(nproc)` at the top level, without `SYSSRC` (passing it hides Debian's split common headers from conftest).
- Userspace parse test: `tools/nvtiming-parse-test/`, with stock and patched outputs for this EDID.
- Stock mode list: `tools/stereo-modeset/run12-nvidia-proprietary-probe-no-stereo-2026-09-21.log`. nouveau: `run3`. amdgpu: `run10`.
- Spec rule as implemented by DRM: `cea_mode_alternate_clock()` and `add_alternate_cea_modes()` in `drivers/gpu/drm/drm_edid.c`.
