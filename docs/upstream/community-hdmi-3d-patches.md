# Community HDMI 1.4 3D driver patches — apply now, upstream in parallel

The premise: a 3D television declares its stereo formats in its own EDID, but Linux
drivers prune those modes before userspace ever sees them — amdgpu hard-denied stereo
outright, and the proprietary nvidia-drm never opted in. The open nouveau driver shows
what compliance looks like: same card, same TV, 51 modes with 29 stereo, no patch
needed. These patches close the gap on the other two drivers *today*, without waiting
for maintainers and distros to pick the upstream series up. Everything here is
hardware-verified on Sony KDL-46HX855 (2012) and KDL-46EX725 (2011) class sinks; run
logs sit in `tools/stereo-modeset/run*-*-2026-09-*.log` next to the reference client.

## NVIDIA proprietary kernel-open 615.71.09 (nvidia-drm) — installable now

**Patch:** [nvidia-615.71.09-hdmi-3d-community.patch](nvidia-615.71.09-hdmi-3d-community.patch)
(install + rollback instructions are in the patch file header itself; dry-run verified
against pristine 615.71.09 sources; applies with `patch -p1` inside `/usr/src/nvidia-615.71.09`).

- What you get: the connector stops hiding the sink's EDID-advertised stereo modes from
  clients that opt in (`DRM_CLIENT_CAP_STEREO_3D`). Six C lines, mirroring the opt-in
  nouveau has carried for years.
- What you still need: a userspace writer for the shipped `NV_HDMI_VSIF_METADATA` blob
  property so the 3D announcement rides the modeset. The repo's `stereo-modeset`
  reference client does exactly that and proves the path end-to-end (SBS-half 1080p60
  and TaB 1080p24 display in 3D). Compositor support is its own lane; the exposure is
  the precondition.
- Known boundary, honestly: frame-packing modes will list but need doubled scanout
  timing inside NVKMS to display — separate firmware-side work, not in this patch.

## amdgpu on 7.0-era trees (DCN generation with `amdgpu_dm.c`) — backport pair

**Patches:** [0001](0001-drm-amdgpu-expose-HDMI-stereo-modes-and-emit-the-VSIF.patch)
then [0002](0002-drm-amdgpu-expand-DC-stream-timing-for-frame-packing-modes.patch),
in series order, `patch -p1` inside a pristine 7.0.x tree. Verified applying cleanly
against the v7.0 tag, built, booted, and driven to picture on the TV (all three
layouts across the project's run series, including full frame packing at 1080p24).

- 0001 un-prunes stereo modes and emits the HDMI 1.4 3D VSIF from the mode flags
  (including the 3D_Ext_Data byte this Sony wants for TaB — matching real sinks, as
  the upstream series also found on a JVC projector).
- 0002 doubles the DC stream timing for frame-packing modes so FP actually displays
  instead of engaging signal with a black picture.
- On 7.3+ you do **not** want these: Adrian Betschart's v3 series is the upstream
  implementation for the current tree (amd-gfx, September 2026 — picture-verified on
  this same TV, Tested-by on file). This pair is the stable-tree insurance and the
  act-now path for anyone stuck on 7.0-era distro kernels.

## nouveau — nothing to patch

Stock nouveau already exposes stereo modes and already wires the VSIF on commit; it is
the control in every matrix here. If your GPU runs nouveau, HDMI 1.4 3D mode exposure
works today with zero changes.

## Safety and support notes

These are kernel patches: you rebuild and boot at your own risk, on hardware you can
recover. Rollback for the NVIDIA patch is a source-package reinstall plus a dkms
rebuild; for the kernel pair, keep your distro's stock kernel installed alongside.
Versions are pinned in each filename; a `-p1 --dry-run` against your tree is step zero.
Bug reports, matrix results from other sinks, and improvement PRs are welcome in the
repo — that's also where the upstream issue drafts live when the contribution path
moves.

## If upstream does not act

Upstream first, always.
Every fix here goes to NVIDIA, AMD and the kernel lists before anything else, in small verified pieces, at the maintainers' pace.
That is the path we want, and we are on it.

But the NVIDIA kernel modules are open source under the MIT licence, and the licence gives everyone the right to modify and redistribute them.
If a fix is right, measured and offered, and still never lands, the answer is not a fight.

**We do the FOSS thing and fork it.**

We carry the patches against each major driver release, published here with the same verification as everything else.
Whoever wants them, uses them.
Whoever does not, does not.
Nobody is forced either way, and upstream stays welcome to take any of it at any time.

We do not want this outcome.
It is the fallback that keeps the work alive, not the plan.
