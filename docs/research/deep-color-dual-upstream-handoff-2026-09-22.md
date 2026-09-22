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

### Last checkpoint before Codex stopped

The commit-message wrap was fixed and the series regenerated. `checkpatch.pl
--no-tree` reports **0 errors and 0 warnings on all three patches**. Current
drm-misc-next commit IDs are:

- `ec385c04` — select HDMI deep-color link depth;
- `78827bdb` — pass HDMI GCP state through NVIF;
- `a7315e24` — program GCP fields.

The submission-target audit found an important wrinkle. Current
`MAINTAINERS` names the live code tree as
`https://gitlab.freedesktop.org/drm/misc/kernel.git` and separately names
`https://gitlab.freedesktop.org/drm/nouveau/-/merge_requests` as an accepted
queue. That GitLab project's `nouveau-next` tip is `775b8212` from 2023 and
does not contain the modern files the series changes (including
`headca7d.c`); patch 1 cannot apply there. The active base here is
drm-misc-next `73ef663c` from 2026. The public API shows only old MRs (#16,
#23, #24, #25, #27), and the drm/misc MR API returned 403. Do **not** rebase
onto the stale 2023 branch or open a misleading MR. Verify the maintainers'
current intake convention. The technically correct fallback is the
signed-off three-patch email series to `dri-devel` and `nouveau`, copying
Lyude Paul and Danilo Krummrich, because that is the live tree/list
combination in `MAINTAINERS`.

An attempted shallow checkout remains at `/tmp/nouveau-next`; it has no
changes. The authoritative branch remains `/tmp/nouveau-drm-misc`. The new
16-bpc-expanded series has not yet been rebuilt in the configured kernel
tree; the earlier 12-bpc series did build and pass on hardware. Next safe act
is to apply `/tmp/nouveau-deep-color-series-v2/` to a clean configured current
kernel tree and build `M=drivers/gpu/drm/nouveau`.

## NVIDIA series state

Working tree: `/tmp/nvidia-open`, branch
`fix-hdmi-deep-color-default`, official 615.71.09 base `61dcc937`.
One uncommitted line changes
`kernel-open/nvidia-modeset/nvidia-modeset-linux.c` from
`max_output_color_depth = 10` to `12`. A complete `make modules -j8` passed.
The change was deliberately **not committed, pushed or published** before
Codex stopped. No Linux 12-bpc proprietary-driver hardware run has yet been
performed. Continue from the uncommitted diff; do not use the public success
phrase for NVIDIA until its own parameter/default test passes.

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

## Completion log (Kimi K3, evening 2026-09-22)

- **Preservation.** All of the above trees lived in `/tmp` (wiped at boot);
  mirrored to `/K3D/temp/dual-upstream-preserve-2026-09-22/`: series-v2
  patches + cover letter, a `73ef663c..nouveau-hdmi-deep-color` git bundle,
  the NVIDIA branch bundle (`61dcc937..fix-hdmi-deep-color-default`), the
  pre-commit diff and base notes.
- **Cover letter written.** The `0000` skeleton's placeholders are filled:
  subject "drm/nouveau: HDMI Deep Color link depth (30/36/48 bpp)", run-5
  evidence, the audio-clobber mechanism, and explicit scope paragraphs —
  RGB-only with YCbCr as the declared next series (owner's chroma directive
  lands there and in the HDR wording, since HDR10's baseline transport is
  10-bpc YCbCr 4:2:2 in a 12-bpc container), the 16-bpc "might enable"
  wording, the HDR "might benefit ... no hardware to test or claim" wording,
  the NVIDIA counterpart context, and the AI-assistance disclosure line.
  Verified first that nouveau has zero connector color-format/colorspace
  infrastructure on drm-misc-next (`nouveau_connector.c`), so YCbCr cannot
  honestly ride along in this series.
- **NVIDIA one-liner committed** as `bbfc670` on
  `fix-hdmi-deep-color-default` (Daniel's Signed-off-by, AI co-author
  trailers), citing #1384. Not pushed; the PR is gated on the module
  parameter (`max_output_color_depth=12`) hardware test, which itself is
  gated on Daniel's explicit go.
- **7.0.10 apply audit.** Against the pristine 7.0.10 source: patch 1
  applies with line offsets, patch 2 clean, patch 3 partially — `gb202.c`
  does not exist yet on 7.0 and the `tu102.c` hunk fails because
  `tu102_sor_hdmi_gcp` (the `.gsp.hdmi_gcp` hook, called from
  `nvkm/subdev/gsp/rm/r535/disp.c:567`) only exists after the post-7.0
  refactor. Conclusion: v4 *is* the correct 7.0.10 backport of the same
  logic; the series' proper verification target is drm-misc-next itself.
- **Build verification on the real target (done, clean).** Full tree
  materialized at series tip `a7315e24` (the drm-misc clone is blobless +
  sparse; `git archive` fetched the rest), bench config + gcc-15. Entire
  `drivers/gpu/drm` subtree compiles with **zero errors**; `vmlinux` links;
  `drm.ko` and `nouveau.ko` are produced. Scripted import closure:
  `nm -u nouveau.ko` reduces to 11 undefined symbols, all stock nouveau
  optional deps satisfied elsewhere in this config's module set
  (`acpi_video`, `i2c-algo-bit`, `mxm_wmi`, `wmi` — unchanged by the
  series). Artifacts: `/K3D/temp/k317/ndc-series-build/drivers/gpu/drm/`
  (`nouveau.ko` 250 MB with debug info).
- **freedesktop GitLab:** no account/credentials found locally, so the
  technically correct route stands per the checkpoint above: signed-off
  email series to dri-devel + nouveau, CC Lyude Paul and Danilo Krummrich.
  Daniel sends (or explicitly green-lights) any outward act.

### Completion log addendum (Kimi K3, later evening 2026-09-22)

- **NVIDIA parameter test: PASS.** Owner green-lit the hardware run; the
  v4 harness (`tools/stereo-modeset/run-nvidia-deepcolor-param12.sh`,
  three honest no-test aborts before it) unloaded the full proprietary
  stack and reloaded `nvidia_modeset max_output_color_depth=12
  hdmi_deepcolor=1` — post-reload readback confirmed both live in the
  running session. With the desktop mirrored to both TV inputs, the
  HX855 OSD reported **12-bit** on the NVIDIA link, owner-verbatim:
  "OSD says 12-bit! ... the same desktop at both inputs". The default-cap
  thesis is now measured on this exact card/sink/cable: lifting the
  default 10→12 alone is sufficient. Evidence log:
  `tools/stereo-modeset/run24-nvidia-deepcolor-param12-pass-2026-09-22.log`.
  The NVIDIA PR is unblocked (still Daniel's per-act go for push+
  PR creation), and the public "staged companion" claim made on VLC MR
  !10366 (note 582109) is now backed by the bench.
- **Send CC list resolved from MAINTAINERS** (drm-misc-next
  `a7315e24` tree): Lyude Paul `<lyude@redhat.com>`, Danilo Krummrich
  `<dakr@kernel.org>`; lists `dri-devel@lists.freedesktop.org` (to) and
  `nouveau@lists.freedesktop.org` (cc), per the "DRM DRIVER FOR NVIDIA
  GEFORCE/QUADRO GPUS" entry.
- **SERIES SENT 2026-09-22 16:21 -03.** Daniel's standing conditional
  authorization ("with a pass, you can use git-email send") fired on the
  run-24 PASS; cover letter was reviewed in-channel before the test with
  no edits requested. `git send-email` via Yahoo SMTP (his stored app
  credential), all four parts 250-accepted, threaded under the cover:
  cover `<20260922192132.114546-1-Capitain_Jack@yahoo.com>`, patches
  `-2`/`-3`/`-4` same base. lore permalink of the cover:
  `https://lore.kernel.org/dri-devel/20260922192132.114546-1-Capitain_Jack@yahoo.com/`.
  From here: email replies only, never polled.
- **NVIDIA PR FILED the same evening:** fork `danielcamposramos/open-gpu-kernel-modules`
  created, `fix-hdmi-deep-color-default` (bbfc670) pushed, PR opened as
  <https://github.com/NVIDIA/open-gpu-kernel-modules/pull/1386> on his
  explicit go ("then go, fork and PR"). Body: run24 PASS evidence + the
  nouveau series as open-source counterpart (lore cover link) + Refs-not-Fixes
  on #1384 (its mode-prune and 3D symptoms stay open) + SDR-only scope + dual
  disclosure lines. Reviewed draft: `docs/upstream/nvidia-deep-color-pr-draft.md`.
  CLAassistant gate appeared; **owner signed the NVIDIA CLA the same evening**
  (his browser act, recorded from his report; check state to settle on its own).
- **First review feedback on the series (Sashiko AI review, patch 2/3, same
  evening):** flagged that `nv50_hdmi_enable()` only encodes GCP CD/PP for
  12 and 16 bpc while patch 1's selection can pick **10 bpc** (DC_30-only
  sinks, or `max bpc` clamped to 10) — leaving CD=0 ("default 24 bpp") on a
  30-bpp wire. **Verified real in the series tree:** selection at
  `dispnv50/disp.c:424-428` reaches bpc=10; the GCP block (`disp.c:834-840`)
  has no bpc==10 arm; all three writers (gv100.c:152 CPU path, tu102.c:43 and
  gb202.c:79 GSP hooks via uoutp.c:271) consume the single value computed
  there, so one arm fixes every path. Our 12-bpc bench result is unaffected
  (the HX855 declares DC_36, so 12 is what gets selected and measured). v2
  will add the 30-bpp arm (CD=5 + the four-pixel-group packing phase, HDMI
  1.4b section 6.5.3 — the same spec dw-hdmi.c cites for its GCP rules) and
  can bench-verify 10 bpc on the same sink by clamping `max bpc` to 10
  (OSD reports the received depth). Reply text drafted for the owner's go;
  nothing answered yet.
- **Remaining:** after lore archives the series, the index pass per the
  publication order above (issue-tracker/project-status/awesome-linux-hdr);
  VLC escalation draft parked in `tools/serviio/upstream-3d-issues/vlc-mr.md`
  for ~2026-09-29 at the owner's call.
