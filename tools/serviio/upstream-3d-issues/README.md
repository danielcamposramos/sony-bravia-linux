# Upstream 3D-signalling campaign — issue drafts and posted links

One draft per upstream target, built from the four verified research
lanes (2026-09-15). Every draft follows the campaign framing: we bring
the **diagnosis + a working fix**, not just a feature request.

**Status: all 7 targets engaged (2026-09-16).** 1 merged (HandBrake
PR #8100), 5 posted by the owner in his own voice, 1 skipped by owner
decision (mkvmerge/Codeberg). The videohelp post is awaiting
moderation. Per campaign doctrine, the drafts here are raw material —
the owner rewords and posts; no AI-drafted text goes out verbatim.

| # | Draft file | Target | Where it goes | Priority |
|---|---|---|---|---|
| 1 | `ffmpeg-eexist-bug.md` + `ffmpeg-eexist-facts.md` | FFmpeg | code.ffmpeg.org tracker (bug) | **POSTED 2026-09-16** — [issue #24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530) (owner's own reworded text + reproducer attached) |
| 2 | `handbrake-issue.md` | HandBrake | comment on open issue #5826 (galad87 invited a patch) | **RESOLVED — PR #8100 MERGED 2026-09-16** ([b0145ad](https://github.com/HandBrake/HandBrake/pull/8100)); #5826 closed by the merge |
| 3 | `staxrip-issue.md` | StaxRip | comment on open issue #1873 (answers a stranded user) | **POSTED 2026-09-15** — [#issuecomment-5685902578](https://github.com/staxrip/staxrip/issues/1873#issuecomment-5685902578) |
| 4 | `x265-issue.md` | x265 | github.com/Multicorewareinc/x265 (issues enabled) | **POSTED 2026-09-15** — [issue #970](https://github.com/Multicorewareinc/x265/issues/970) |
| 5 | `ffmpeg-bsf-feature.md` | FFmpeg | code.ffmpeg.org tracker (enhancement) | **POSTED 2026-09-16** — [issue #24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531) (owner's own reworded text) |
| 6 | `mkvtoolnix-issue.md` | mkvmerge | codeberg.org/mbunkus/mkvtoolnix (keep it SHORT — maintainer closes verbose reports) | **SKIPPED 2026-09-16 (owner decision)** — Codeberg signup paywalled; unfilled, draft retained in case an account is ever created or another channel opens |
| 7 | `bd3d2mk3d-forum-post.md` | BD3D2MK3D (r0lZ) | forum.videohelp.com thread 395498 | **POSTED 2026-09-16 — awaiting moderation** (owner's own reworded text; link to be added when it clears) |

Not separately drafted: the ffmpeg `libx265.c` stereo3d wiring — fold
it into #5 as a secondary bullet if the tracker prefers one report, or
file it standalone after x265 (#4) lands. VidCoder needs no issue: its
maintainer already stated (RandomEngy/VidCoder#1318) that all asks
belong upstream in HandBrake; VidCoder inherits the fix via the
HandBrake core DLLs it ships.

## Research basis (verified 2026-09-15)

- **HandBrake**: master commit 1d20876 (unreleased 1.12.0) preserves
  the Matroska StereoMode tag — but `libhb/encx264.c` never sets
  `x264_param_t.i_frame_packing`; no encoder path writes the SEI.
  Data already flows: `stream.c:6148` → `title->stereo_3d` →
  `common.c:4970` `job->stereo_3d`. One mapping remains.
- **StaxRip**: `x264Enc.vb:1181` already exposes `--frame-packing` in
  the GUI (never set by default, no auto-detection); muxer has no
  `--stereo-mode`; open issue #1873 is our exact symptom, maintainer
  couldn't help.
- **x265**: `FRAME_PACKING = 45` exists as an enum in `x265.h` but no
  param, no CLI, no writer — HEVC 3D encodes cannot carry the SEI.
- **FFmpeg**: no bsf writes SEI 45 (but cbs_sei FPA read/write landed
  in 826f55d5, so `h264_metadata` is a small option-add); libx264
  auto-injects since 2013 (09cb75cd); **unreported bug**: tag+SEI files
  abort the CLI with `-17 EEXIST` (9.0.1 and master; 6.1.6 unaffected
  — verified on our own Serviio host).
- **mkvmerge**: `--stereo-mode` purely manual; no input reader parses
  the bitstream for stereo (AVC es_parser skips payload 45).
- **BD3D2MK3D**: the model citizen — writes both signals by default
  on x264; real gaps are the custom-encoder path (silent SEI-less
  output) and x265 (upstream gap). r0lZ already stated publicly the
  core fact of this campaign ("many hardware players support only the
  frame-packing and ignore the MKV stereo-mode").

Linkable public artifact for every post:
https://github.com/danielcamposramos/sony-bravia-linux — specifically
`docs/3d-signalling-explainer.md`.