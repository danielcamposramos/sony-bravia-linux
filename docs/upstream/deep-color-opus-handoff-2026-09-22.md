# Deep Color — handoff to Claude Opus (2026-09-22, from Kimi K3 running inside Claude Code CLI)

You are continuing the HDMI Deep Color campaign lane. Kimi K3 (this writer) built
and benched v2 tonight; GPT/Codex built the clean series and traced the NVIDIA
default cap before that. Daniel directs every outward act. The ollama/cloud
partner budget is nearly exhausted for the day, which is why the continuation
lands here.

Read first, in this order:
1. `docs/research/deep-color-dual-upstream-handoff-2026-09-22.md` — full
   measured history, both lanes, completion logs (Kimi's evening entries at
   the bottom are today's source of truth).
2. `docs/upstream/issue-tracker.md` rows 1, 12, 13 — live thread state.
3. This file's queues below.

## Where everything is

- **v2 series (benched, unsent):** `/K3D/temp/nouveau-deep-color-series-v2-fixed/`
  (`v2-0000-cover-letter.patch` FILLED — subject, blurb with Changes-in-v2,
  citation round, bench paragraph updated to post-bench truth — plus
  `v2-0001..v2-0003`). Mirror: `/K3D/temp/dual-upstream-preserve-2026-09-22/nouveau-deep-color-series-v2-benched/`.
  Base = drm-misc-next `73ef663c` (unchanged, no rebase needed). Commits:
  `ec385c04` → `5f86153c` (patch 2, both fixes folded) → `a01857bb`.
  checkpatch --strict clean ×3; module rebuild clean; opcodes verified.
- **v2-bench module (running kernel 7.0.10):** `/K3D/temp/k317/nouveau-hdmi-deep-colour-v2-experimental.ko`,
  sha256 `89ced700ae4da204dd5d82014b3b01b20d57b2c3607b8b8979379fbfb7405b79`.
  Tree: `/K3D/temp/k317/linux-source-7.0` (dispnv50/disp.c carries the ported
  fixes; rebuild: `make -j8 KBUILD_MODPOST_WARN=1 M=drivers/gpu/drm/nouveau modules`).
- **Bench evidence:** run23 (v1 12-bpc first pass), run24 (NVIDIA param=12 pass),
  run25 (v2 deep12 regression), run26 (v2 deep10 clamp, 30-bpp arm) — all
  `tools/stereo-modeset/run2*-*.log`, committed.
- **Harness:** `tools/stereo-modeset/run-nouveau-test.sh [deep12|deep10|...]`
  (gained deep10 + on-frame big yellow run labels today; connector picked by
  EDID sha; docker pause/restore; /run modprobe guard). Tool:
  `stereo-modeset.c` (deep10 = max bpc 10 clamp; label overlay).
- **List thread truth:** `/K3D/temp/thread.mbox` (lore pull, 6 messages: our 4,
  Sashiko ×2 — `<20260922192921.BA4471F000FF@smtp.kernel.org>` on 2/3,
  `<20260922193903.DE3BB1F000FF@smtp.kernel.org>` on 1/3; nothing on 3/3).
  Cover archive: https://lore.kernel.org/dri-devel/20260922192132.114546-1-Capitain_Jack@yahoo.com/
  (Anubis-blocks datacenter web fetches; t.mbox endpoint works with a
  descriptive UA. Never bypass bot-walls; Daniel in the UA is fine).
- **NVIDIA lane:** PR https://github.com/NVIDIA/open-gpu-kernel-modules/pull/1386
  OPEN, CLA signed by Daniel, final title "nvidia-modeset: raise default output
  color depth for HDMI 1.4 Deep Color, EDID VSDB DC_30/DC_36/DC_48".
  Watch = GitHub email notifications only. Refs (not Fixes) #1384 by design.

## Queue 1 — the ack mail (GATED on Daniel's word)

Sashiko's automated review fired before any human; the v2 series closes all
three findings and is now bench-proven. Daniel dictated the framing — quote
him verbatim, do NOT soften it into thanks:

> "And a fair ack is not 'thank you', is 'the current implementation is the
> one breaking HDMI specs' / 'we're attemting to medicine to that disease'"

Structure (draft for his review, then send):
- Reply in-thread to BOTH Sashiko mails (In-Reply-To the two Message-IDs
  above; cc the list and the patch recipients).
- Point 1 (2/3 High, 30-bpp arm): v1's selection could pick bpc=10 while the
  GCP block had no 30-bpp arm — real, fixed in v2 patch 2 (CD=5, PP =
  pixels&3 per HDMI 1.4b §6.5.3 and NVIDIA's own phase numbering), and now
  measured: with max bpc clamped to 10 the DC_30 sink links at 30 bpp and
  renders (run26 log linked), plus a 36-bpp regression pass (run25).
- Point 2 (1/3 High, SCDC): threshold moved to the TMDS character rate
  (pixel clock × depth), with the measured note that the NVIF khz argument
  stays the pixel clock on purpose — link trained at the correct 222.75 MHz.
- Point 3 (1/3 Medium, HDMI-A-only attach): answered as scope; i915
  precedent; extension is a maintainer call for a follow-up.
- His medicine sentence as the close. AI-disclosure line. Signed Daniel.

## Queue 2 — the v2 send (GATED on Daniel's word, after he okays the ack)

- Runbook: from `/K3D/GitHub/sony-bravia-linux` (git-email config lives in
  this repo: Yahoo SMTP, user capitain_jack — credential in his
  `~/.git-credentials`, never print it):
  `git send-email --reroll-count 2 --to dri-devel@lists.freedesktop.org
   --cc nouveau@lists.freedesktop.org --cc "<Lyude Paul, see MAINTAINERS>"
   --cc "<Danilo Krummrich, see MAINTAINERS>" /K3D/temp/nouveau-deep-color-series-v2-fixed/v2-00*.patch`
  DRY-RUN first (`--dry-run`) and show him; then fire on his word.
- After lore archives v2: update issue-tracker row 13 (v2 cover Message-ID),
  then the index pass: `docs/project-status.md`, awesome-linux-hdr, and
  awesome-stereoscopy where the normative chain is indexed (publication-order
  list in the dual-upstream handoff). Commit+push each repo immediately.

## Queue 3 — the chroma part (your design/build; Daniel green-lights any test)

v2 is deliberately RGB-only; the cover letter declares YCbCr "the next
series, building on the DRM connector color-format property work". That is
now your lane. Measured constraints from this bench: HX855 = HDMI 1.4 sink,
EDID DC_30/DC_36 (no DC_48), 225 MHz TMDS ceiling; no HDR sink exists.

Design questions to answer with sources before writing code:
1. What mainline currently offers userspace for output format selection
   (DRM `Colorspace` property state; any HDMI output-format property work on
   dri-devel — search lore; dw-hdmi/sunxi and i915 YCbCr 4:2:0/4:2:2 paths
   are the in-tree precedents).
2. nouveau plumbing shape: where `nv50_outp_atomic_check()` (disp.c ~408)
   would pick bpc×format jointly against `mode_rate`, how head/OUTP program
   YCbCr (NVKMS `nvkms-hdmi.c` programs 444/422/420 + deep color over them —
   read its format handling as the oracle), AVI InfoFrame Y1Y0 + Q bits
   (`drm_hdmi_avi_infoframe...` helpers), and the GCP rule per spec: 4:2:2
   is always 12-bit packed and takes NO GCP; 4:4:4/4:2:0 deep color use the
   same CD table as RGB.
3. EDID capability matrix: `drm_edid.h` DC flags per format (RGB444 DC_*,
   Y444 DC_*, 420 support bits) — verify exact member names in the header
   before citing.
4. Bench plan: only formats this sink declares; OSD does not show chroma, so
   define a measurable criterion BEFORE any run (nvkms does it how?).
5. Scope wording inherits the house rule: HDR stays "might benefit, no
   hardware to test or claim it" until an HDR sink exists.

Prototype on the running-kernel bench tree (`/K3D/temp/k317/linux-source-7.0`);
upstream series on `/K3D/temp/ndc-v2`. checkpatch --strict, module rebuild,
disasm-verify, then Daniel fires the bench run.

## Queue 4 — parked items that may wake during your watch

- VLC MR !10366 escalation draft: `docs/upstream/media-stack/vlc-mr.md`,
  trigger ~2026-09-29, ONLY on Daniel's explicit ask. Verified policy facts
  are in that file.
- mpv PR #18490 CI rerun needs a maintainer's first-time-contributor approve —
  kasper93's move. mkvtoolnix !6312 is mbunkus's move. Adrian Betschart's ack
  stays OFF-LIST/private. All threads: email-trigger only, never polled.
- NVIDIA PR #1386: watch email; if reviewed, Daniel decides replies.

## Standing constraints (all active, verbatim-critical)

- No online posts or hardware tests without Daniel's explicit per-act
  approval. Drafts in his voice: plain text, one sentence per line, no hard
  wraps, kill mid-sentence em dashes, bold hard, quote his lines verbatim.
- git author `Daniel Campos Ramos <Capitain_Jack@yahoo.com>` +
  `Co-Authored-By: Claude Code <noreply@anthropic.com>`. Disclosure line on
  every public artifact: "AI partners were leveraged in the production of
  this work." PR descriptions end with the 🤖 Claude Code line.
- Tokens (never echo): `~/.config/code.videolan.org/token`,
  `~/.config/code.ffmpeg.org/token`, `~/.config/github` token,
  `~/.git-credentials`.
- Verify-by-running before any upstream claim. Max 2 subagents, cheap models
  (Opus for synthesis). `/K3D/temp` not `/tmp` (wiped at boot). `sync` after
  builds (ext4 commit=600). Own hardware/LAN only. Heavy media on d2server
  via ssh.
- Credit Daniel for the SEI discovery; never invent AI code authorship or
  sign-offs.

## Today's deltas (2026-09-22 evening, newest first)

- run25 + run26 passed on the v2-bench module; logs committed; frame labels
  added so depth identification is on-picture, not memory.
- v2 cover letter final (subject `[PATCH v2 0/3] drm/nouveau: HDMI Deep
  Color link depth (30/36/48 bpp)`; Tested paragraph reports both new runs).
- PR #1386 retitled twice under Daniel's pass; final form cites HDMI 1.4
  Deep Color + VSDB DC_30/36/48 with no parentheses and no fixed "to 12".
