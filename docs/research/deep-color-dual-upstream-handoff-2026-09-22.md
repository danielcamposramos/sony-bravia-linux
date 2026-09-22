# HDMI Deep Color dual-upstream handoff (2026-09-22)

This is the restart point for the paired nouveau and NVIDIA submissions.
It records measured facts separately from source conclusions and explicitly
marks the claims that still need hardware.

## Bench result that closes the nouveau diagnosis

Hardware: GALAX RTX 3060 (GA106, 12 GB) to Sony KDL-46HX855 over HDMI,
1920x1080p60 SDR RGB. The sink EDID advertises HDMI VSDB `DC_30` and
`DC_36`; its 225 MHz ceiling narrowly admits the 222.75 MHz 12-bpc stream.

Run 5 loaded the cumulative v4 module, SHA-256
`2cfde710b18ab50451f453f27b38f52dbb06e124f03b622c7781a01490504c0e`.
The final GSP HDMI-audio-path readback was
`enable=1 subpack=0x01002610`; the low 24 bits are the required GCP payload
`0x002610`, and the masked update preserved the generation-owned high bit.
The TV reported **12-bit** and displayed a stable green-to-purple gradient
over black and white squares. There was no incompatible-signal OSD. Public
test wording requested by the owner: **passed with full colors (pun
intended)**.

The first three deep-color experiments failed because the GSP HDMI-audio
operation runs after display commit and replaced the prepared GCP with a
depth-less packet. NVIDIA's proprietary path performs the same audio
operation, then rebuilds GCP CD/PP from committed head depth. Caching the
armed CD/PP and restoring them after audio gives nouveau the same ordering
and made the physical link work.

Canonical log:
`tools/stereo-modeset/run23-nouveau-deep12-gcp-audio-preserve-pass-2026-09-22.log`.

## Nouveau series state

Working tree: `/tmp/nouveau-drm-misc`, branch
`nouveau-hdmi-deep-color`, currently based on drm-misc-next commit
`73ef663c`. Three signed-off commits:

1. `drm/nouveau: select HDMI deep-color link depth`
2. `drm/nouveau: pass HDMI GCP deep-color state through NVIF`
3. `drm/nouveau: program HDMI deep-color GCP fields`

The series attaches `max bpc`, selects EDID- and bandwidth-valid RGB depth,
programs 30/36/48-bpp head state, carries GCP CD/PP through NVIF, and
preserves the values across the late audio write. Twelve bpc is measured.
Ten bpc follows the same code and was already functional on the proprietary
control. Sixteen bpc is implemented from HDMI `DC_48`, NVIDIA display-class
`BPP_48_444`, and GCP CD=7, but is **not tested** because the bench has no
DC_48 sink. Phrase the result as “might enable professional 16-bit displays;
the mechanism is the same, but we do not own the hardware to test or claim
it.”

Generated patches: `/tmp/nouveau-deep-color-series-v2/`. Before submitting:

- wrap the one overlong line in commit 2 and regenerate;
- rebase the series on the actual `drm/nouveau` `nouveau-next` target;
- build all three commits' final tree and run checkpatch;
- write a cover letter with the run-5 evidence and scope below;
- push a contributor fork and open the GitLab MR if authentication exists.

## NVIDIA series state

Working tree: `/tmp/nvidia-open`, branch
`fix-hdmi-deep-color-default`, official 615.71.09 base `61dcc937`.
One uncommitted line changes
`kernel-open/nvidia-modeset/nvidia-modeset-linux.c` from
`max_output_color_depth = 10` to `12`. A complete `make modules -j8` passed.

The current installed 615.71.09 open kernel module confirms
`hdmi_deepcolor=Y` but `max_output_color_depth=10`. Public NVKMS source
already parses `DC_30`, `DC_36` and `DC_48`, and already constructs and
programs 10/12-bpc output for RGB, YCbCr 4:4:4, YCbCr 4:2:0 and YCbCr
4:2:2. The Linux default cap prevents 12-bpc selection. The Windows 616.64
driver installed on this same GA106 machine has already driven this same
sink at 12-bit, providing the strongest cross-OS control.

Commit the one-line change with Daniel's Signed-off-by, then hardware-test
the installed Linux driver using the existing module parameter set to 12
before publishing. The PR must name
<https://github.com/NVIDIA/open-gpu-kernel-modules/issues/1384> as the
primary issue, cite the nouveau MR as its **open-source counterpart**, and
use the exact successful-test phrase above if the test passes.

## Standards and exact scope

HDMI Deep Color on the wire defines 30, 36 and 48 bits per pixel: 10, 12
and 16 bits per component. There is **no HDMI 14-bpc Deep Color code**.
Fourteen-bit internal processing or the EDID base digital-depth enumeration
must not be represented as a 14-bpc HDMI transport mode.

The nouveau series is RGB-only because nouveau currently has no HDMI output
color-format selection path. YCbCr is not a one-line extension: it requires
connector format policy, AVI InfoFrame colorspace/range/colorimetry, and
format-specific bandwidth/packing. Record it as the next series, based on
the DRM connector color-format property work, rather than claiming this
series implements it. NVIDIA's existing NVKMS selection path does cover
RGB plus YCbCr 4:4:4/4:2:2/4:2:0, so the default-cap patch applies to its
existing chroma modes too.

Twelve-bit SDR transport is proven. **HDR is not proven**: the owner has no
HDR display or analyzer. The same deep-color transport is a prerequisite
and may resolve link-depth failures in HDR reports, but native nouveau HDR
also needs `HDR_OUTPUT_METADATA`, Colorspace, CTA-861.3 static metadata and
the DRM InfoFrame path that its current driver lacks. Say “HDR might benefit;
the transport mechanism is the same, but we do not have hardware to test or
claim it.”

Normative/source chain to cite from the repositories:

- HDMI Forum HDMI 2.0a and the HDMI Deep Color/GCP definitions;
- CTA-861.3-A plus CTA's official public preview;
- ITU-R BT.2100-3;
- Linux DRM EDID and HDR metadata uAPI;
- NVIDIA's public `nvtiming.h`, display-class headers and NVKMS source;
- `awesome-stereoscopy/standards.md` and `awesome-linux-hdr` for the curated
  public index; this repository for the reproducible bench evidence.

## Related-issue triage for the submissions

NVIDIA:

- **#1384 — direct.** Measured 10-vs-12 narrowing on this exact stack; the
  PR's primary issue.
- **#779 and #933 — possible HDR beneficiaries, not claimed fixed.** Retest
  after removing the depth cap; metadata/colorspace may still be causal.
- **#1285 — likely separate.** Atomic colorspace `EINVAL`, not merely depth.
- **#1101 — separate property-exposure precedent.** Useful architecture,
  not a claim that the cap fixes it.
- **#1348 — adjacent EDID/format-policy bug.** Forced YCbCr 4:2:2-limited
  from HF-VSDB parsing; not this root cause.
- DP-only or FRL-transition reports are not fixed by an HDMI TMDS default.

Nouveau:

- No direct public Deep Color issue was found in the first GitLab search.
- #488 is DP-only and demonstrates adjacent HDR/10-bpc demand, not a fix.
- #376 is bandwidth/mode-selection adjacent; do not claim causality.
- #267 and #383 are connector/EDID problems and unrelated.

Keep this triage in each description; do not mass-comment unrelated issues.

## Publication and cross-link order

1. Finish, verify and push both branches.
2. Open the nouveau MR and NVIDIA PR.
3. In the NVIDIA PR, call nouveau the “open-source counterpart.”
4. In the nouveau MR, call NVIDIA the “closed-source counterpart.”
5. Post one cross-link comment on each after both stable URLs exist.
6. Add both URLs, exact revision IDs and test state to
   `docs/upstream/issue-tracker.md`, `docs/project-status.md`,
   `awesome-linux-hdr`, and `awesome-stereoscopy` where the normative chain
   is indexed; commit and push each repository immediately.

## Provenance

Daniel Campos Ramos directed the work, owns the hardware, made the physical
observations and is the submitting author. Kimi K3, working inside Claude
Code CLI, found and tested the decisive late HDMI-audio GCP clobber and
prepared v4. GPT/Codex independently audited the handoff, extended the clean
upstream series and traced the NVIDIA Linux default cap and cross-format
scope. Credit this collective work in the public evidence/provenance links;
do not invent code authorship or sign-offs for either AI partner.
