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
3. In the NVIDIA PR, call nouveau the "open-source counterpart."
4. In the nouveau MR, call NVIDIA the "closed-source counterpart."
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
  `a7315e24` tree): Lyude Paul, Danilo Krummrich
 ; lists `dri-devel@lists.freedesktop.org` (to) and
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
- **Sashiko reviewed 1/3 too** (`<20260922193903.DE3BB1F000FF@smtp.kernel.org>`,
  19:39Z; no mail on 3/3 as of the lore mbox pull): two more findings.
  (a) **[High] SCDC gate uses pixel clock, not TMDS character rate** —
  `high_tmds_clock_ratio = mode->clock > 340000` ignores the deep-color
  multiplier, so 4K30@12bpc (297 MHz pixel → 445.5 MHz char) would skip
  mandatory scrambling/1:40 ratio (HDMI 2.0 340 MHz char-rate rule). Real
  spec gap, zero impact on the bench passes (1080p60@36bpp = 222.75 MHz,
  HDMI 1.4 sink, no SCDC). (b) **[Medium] `max bpc` attached to HDMI-A
  connectors only** — DVI/DP connectors driving an HDMI sink through a
  passive adapter stay 8 bpc. Design-scope point; HDMI-only attach matches
  the conservative mainline precedent (i915), amdgpu is looser. v2 plan:
  (a) scale the SCDC threshold by the selected depth, (3/3-mail absence
  noted), plus the 30-bpp GCP arm; (b) answered as scope, extension left to
  maintainers. Both mails live in `/K3D/temp/thread.mbox` (lore pull,
  descriptive UA).
- **v2 BUILT 2026-09-22 evening (owner: "build v2 before the ack").**
  Fresh blobless drm-misc-next clone at `/K3D/temp/ndc-v2` (tip still
  base `73ef663c`, no rebase noise); v1 bundle applied, fixes folded into
  patch 2 (`5f86153c`) via fixup+autosquash: series now
  `ec385c04`→`5f86153c`→`a01857bb`, 14 files +144/-21.
  Fixes: (a) GCP block in `nv50_hdmi_enable()` gains the 30-bpp arm
  (CD=5, PP = pixels&3 of hdisplay+back-porch, wire 0 = phase 4 per
  NVIDIA's nvtiming.h numbering; closes Sashiko 2/3 [High]); (b) SCDC
  gate now thresholds `mode->clock * bpc / 8` (TMDS character rate) per
  the HDMI 2.0 340 MHz rule, while the NVIF khz argument deliberately
  stays the pixel clock — measured: link trained at the correct
  222.75 MHz char rate, sequencer scales internally (closes Sashiko 1/3
  [High]). HDMI-A-only max-bpc attach kept per i915 precedent=Sashiko
  1/3 [Medium] answered as scope. checkpatch --strict clean x3;
  incremental module rebuild clean, `cmp $0xa/$0xc/$0x10` opcodes
  verified in nouveau.ko disasm of nv50_sor_atomic_enable.
  Series files: `/K3D/temp/nouveau-deep-color-series-v2-fixed/`
  (v2-0000..v2-0003). Cover letter subject filled
  ("[PATCH v2 0/3] drm/nouveau: HDMI Deep Color link depth (30/36/48
  bpp)"); blurb = v1 text + "Changes in v2" (three findings closed,
  honest 30-bpp bench note: clamp run being prepared) + the owner's
  citation round (NVIDIA #1382/#1384/PR #1386 context; HDMI 1.4b §6.5.3,
  HDMI 2.0a, CTA-861-G, nvtiming.h, dw-hdmi precedent; sony-bravia-linux
  + awesome-stereoscopy + awesome-linux-hdr URLs).
- **NVIDIA PR #1386 RETITLED** per owner ("cite the specs now", REST
  PATCH; then corrected again on his review: the "max_output_color_depth
  to 12" half singled out one depth beside the three VSDB capabilities
  and the parentheses went): final title "nvidia-modeset: raise default
  output color depth for HDMI 1.4 Deep Color, EDID VSDB DC_30/DC_36/DC_48".
- **Remaining:** 10-bpc clamp bench run (owner's hand); then ack mail in
  the owner's framing ("the current implementation is the one breaking
  HDMI specs" / "we're attempting to medicine to that disease") and the
  v2 send — both on his explicit go.
- **v2 BENCH PASSED the same evening (owner's hand, A then B).**
  v2-bench module `/K3D/temp/k317/nouveau-hdmi-deep-colour-v2-experimental.ko`
  (sha256 `89ced700ae4da204dd5d82014b3b01b20d57b2c3607b8b8979379fbfb7405b79`,
  vermagic 7.0.10+deb14-amd64) = the running-kernel v4 shape + the two v2
  fixes ported to `dispnv50/disp.c`. **run25** (deep12, regression): max
  bpc=12 accepted, 36-bpp link up, renders; **run26** (deep10, new arm):
  max bpc=10 clamp accepted, sink links at 30 bpp with CD=5 and renders —
  v1's "CD=0 on a 30-bpp wire" hole is now closed on hardware. Tools grew
  a `deep10` mode (`max bpc` clamp) and paint the run identity in big
  yellow text on the frame ("12-BIT RGB" / "10-BIT RGB CLAMP") so pictures
  and OSD reads can't be mixed up. Owner-verbatim: "Perfect run partner,
  Both tests rung, A then B, both perfectly displayed with proper text."
  Logs: `tools/stereo-modeset/run25-nouveau-v2-deep12-regression-pass-2026-09-22.log`,
  `run26-nouveau-v2-deep10-clamp-pass-2026-09-22.log`. Cover letter's
  Tested paragraph now reports both runs as done; benched series preserved
  at `/K3D/temp/dual-upstream-preserve-2026-09-22/nouveau-deep-color-series-v2-benched/`.
  Owner directive: repo gets the results now; the list/MR do NOT (ack + v2
  send stay gated); continuation handed to Claude Opus — see
  `docs/upstream/deep-color-opus-handoff-2026-09-22.md`.
- **Remaining (post-bench):** ack mail + v2 send on the owner's word;
  chroma/YCbCr next-series design (Opus lane); VLC escalation draft still
  parked for ~2026-09-29; the index pass once v2 is on the list.

### Completion log (Claude Opus, night 2026-09-22) — chroma lane

- **Design** (`docs/research/nouveau-hdmi-color-format-design-2026-09-22.md`):
  mainline already has the `color format` + `Broadcast RGB` uAPI; nouveau
  hardcoded full-range RGB under a TODO. NVKMS 615.71.09 shows the real
  C57D/C67D mechanism (PROCAMP + OCSC1 matrix + clamp; 4:2:0 adds
  YUV420PACKER/CHROMA_DOWN_V per-head-cap-gated on GA102+). All 36 matrix
  coefficients re-derived from ITU-R BT.601/709/2020 (max 4 LSB of 2^-16).
- **Bench: run27 16/16 + run28 9/9, owner-verified all green** — RGB
  full/limited/auto 8/10/12, YCbCr 4:4:4 and 4:2:2 8/10/12, BT.601 at
  576p/480p, BT.709 from 720p, VIC 1 held at 8 bpc, SBS/TaB/FP with
  non-default formats. Reading run27's driver lines found a latent bug in
  v2 itself: frame packing was rated at the per-eye clock (74.25 instead of
  148.5 MHz). Fixed (`nv50_outp_link_clock`, same doubling as
  `nouveau_connector_mode_valid`), folded into v2 patches 1/2, confirmed
  by run28 (FP RGB 12 at 222.75 MHz).
- **Series ready, unsent** (tree `/K3D/temp/ndc-v2`; bundle + patch files in
  `/K3D/temp/dual-upstream-preserve-2026-09-22/`):
  v2 deep colour `477df2bd → 1f9376eb → c3dddeb0` (cover updated: FP
  bullet, runs 25–28, DVI + YCbCr pointers to the follow-on); colour-format
  series 6 patches on top (`129dbaee … b8299fc5`: class header, head
  conversion, Broadcast RGB, YCbCr 4:4:4/4:2:2, 4:2:0 on GA102+ [untested,
  no sink], DVI connectors [untested, no port; Reported-by Sashiko + Closes]),
  `--base` with v2 as prerequisites. checkpatch --strict clean except the
  verbatim NVIDIA class-header subsets (same finding classes as upstream
  `clc37d.h`); both tips build.
- **Gated on the owner:** the ack mail, the v2 send, the colour-format
  series send (recommendation: two series, v2 first); awesome-linux-hdr +
  awesome-stereoscopy pass for DVI / DisplayPort / DP++ (DP carries stereo
  natively: MSA MISC1 / VSC SDP).
- **BOTH SERIES SENT 2026-09-22 ~18:53 -03** on the owner's go, 11/11
  messages 250-accepted, to dri-devel, cc nouveau + Lyude Paul + Danilo
  Krummrich (patch 6 also auto-cc'd sashiko-bot@kernel.org via Reported-by):
  v2 cover `<20260922215317.611388-1-Capitain_Jack@yahoo.com>` (patches -2..-4);
  colour-format cover `<20260922215336.612239-1-Capitain_Jack@yahoo.com>`
  (patches -2..-7). Channel: list + Patchwork only, per MAINTAINERS; no GitLab
  MR (MAINTAINERS lists the MR queue as an alternative door, not a mirror; a
  second channel would duplicate review). Accidental-MR check: drm/nouveau MR
  list has none of ours; drm/misc refuses anonymous API reads (403); this
  machine has no freedesktop GitLab credentials or CLI, so none could have been
  created from here. Ack reply to the v1 cover staged with both lore links at
  `/K3D/temp/ack/0001-ack-sashiko.eml`, awaiting the owner's final go.
- **Ack SENT** on the v1 cover thread, 250-accepted:
  `<20260922220723.649977-1-Capitain_Jack@yahoo.com>` — owner's framing (the
  HDMI-compliance gaps pre-existed in nouveau; the series patches exactly
  that; the 30-bpp arm was v1 not yet covering the whole gap), both lore
  links, disclosure line. From here: email-trigger only, never polled.
- **Late-arriving Sashiko 1/3 mail re-checked (owner request):** same
  message as the 19:39Z review already handled, but its second half was
  right and not fixed in v2: the `khz` argument to `nvif_outp_hdmi()` stays
  the pixel clock, and on non-GSP boards (`gm200_sor_hdmi_scdc`, GM20x..TU10x
  without GSP) it sets `tmds.high_speed` = SOR scrambler, 1/40 ratio and clock
  divider. GSP ignores it, so the GA106 bench could not show it; the v2 cover's
  "measured, pixel clock is correct" holds for GSP only. Fixed locally: khz =
  TMDS character rate (format-aware via `nv50_hdmi_char_rate` in the colour
  series). Branches rebased: deep colour `477df2bd → c93f4a77 → 0d1a9489`,
  colour format `ee885c41 … 27e91e45`; bundle
  `nouveau-deepcolor-v3-plus-colorformat-v2.bundle`. **Thank-you reply SENT**
  (owner: "we deny things we solved, but also recognize things he's right")
  `<20260922222618.709711-1-Capitain_Jack@yahoo.com>` to sashiko-reviews (its
  Reply-To) + dri-devel + nouveau + maintainers. **Deep colour v3 + colour
  format v2 wait** until maintainers have looked at v2 (a few days).
- **Next revisions drafted, held:** `/K3D/temp/nouveau-next-deepcolor-v3/`
  (Changes in v3 credits the Sashiko review + our reply, withdraws v2's
  GSP-only "pixel clock is correct" claim) and
  `/K3D/temp/nouveau-next-colorformat-v2/` (rebased on v3, format-aware
  khz). Send only on the owner's word, after maintainers have seen v2.
- **Index pass done:** awesome-linux-hdr `d2814fe` (DVI 1.0, VESA DP +
  DisplayHDR, DP++ helpers; both series in repair maps; Phase A measured)
  and awesome-stereoscopy `3346fd6` (DP native stereo, DVI/DP++ carry HDMI
  3D only to HDMI sinks; nouveau series in the HDR driver note). All links
  fetched and checked by content; awesome-lint unchanged at its 37
  pre-existing errors.
- **NVIDIA PR #1386 (owner asked):** CLA signed, mergeable, no reviews yet.
  The khz finding is nouveau-internal (nvkm non-GSP SOR path); NVKMS's open
  rate math is already depth/format-aware, so nothing to port. Open question
  kept unclaimed: NVKMS's open GCP only declares 36 bpp, yet the sink reported
  10-bit under the proprietary default; closed RM may rewrite it.
