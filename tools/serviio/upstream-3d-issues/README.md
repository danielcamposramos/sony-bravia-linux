# Upstream 3D-signalling campaign — issue drafts and posted links

One draft per upstream target, built from the four verified research
lanes (2026-09-15). Every draft follows the campaign framing: we bring
the **diagnosis + a working fix**, not just a feature request.

**Status: all 9 targets engaged (2026-09-16).** 1 merged (HandBrake
PR #8100), 6 posted/filed on trackers/forums, 1 skipped by owner decision
(mkvmerge/Codeberg), and — first audience-facing target of the campaign —
the LTT forum post (target #9): the guide the theater video promised in
its description and the thread spent two weeks asking for. The videohelp post cleared moderation 2026-09-16
(post #2803756); the mpv player-side pair (issue #18489 + PR #18490,
from a parallel Opus session) completes the pipeline end to end:
encode → remux → robustness → player → DLNA. PR #18490 is in review
(hostile start, then 8 technical threads — all answered same day in
the owner's own words, no apology; see the mpv review section below).
Per campaign doctrine,
the drafts here are raw material — the owner approves/rewords and
posts; no AI-drafted text goes out without owner approval.

| # | Draft file | Target | Where it goes | Priority |
|---|---|---|---|---|
| 1 | `ffmpeg-eexist-bug.md` + `ffmpeg-eexist-facts.md` | FFmpeg | code.ffmpeg.org tracker (bug) | **POSTED 2026-09-16** — [issue #24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530) (owner's own reworded text + reproducer attached) |
| 2 | `handbrake-issue.md` | HandBrake | comment on open issue #5826 (galad87 invited a patch) | **RESOLVED — PR #8100 MERGED 2026-09-16** ([b0145ad](https://github.com/HandBrake/HandBrake/pull/8100)); #5826 closed by the merge |
| 3 | `staxrip-issue.md` | StaxRip | comment on open issue #1873 (answers a stranded user) | **POSTED 2026-09-15** — [#issuecomment-5685902578](https://github.com/staxrip/staxrip/issues/1873#issuecomment-5685902578) |
| 4 | `x265-issue.md` | x265 | github.com/Multicorewareinc/x265 (issues enabled) | **POSTED 2026-09-15** — [issue #970](https://github.com/Multicorewareinc/x265/issues/970) |
| 5 | `ffmpeg-bsf-feature.md` | FFmpeg | code.ffmpeg.org tracker (enhancement) | **POSTED 2026-09-16** — [issue #24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531) (owner's own reworded text) |
| 6 | `mkvtoolnix-issue.md` | mkvmerge | codeberg.org/mbunkus/mkvtoolnix (keep it SHORT — maintainer closes verbose reports) | **SKIPPED 2026-09-16 (owner decision)** — Codeberg signup paywalled; unfilled, draft retained in case an account is ever created or another channel opens |
| 7 | `bd3d2mk3d-forum-post.md` | BD3D2MK3D (r0lZ) | forum.videohelp.com thread 395498 | **POSTED + ANSWERED + CLOSED 2026-09-16** — [post #2803756](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803756); r0lZ replied same day ([#2803762](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803762)): suggestion 1 accepted (custom-encoder warning dialog), suggestion 2 needs clarification, cross-brand confirmation (his Samsung behaves the same), zero corrections to the diagnosis; his #604 (CLI = maybe, no promises — mountains win) answered by the owner's closing reply (POSTED 2026-09-16, pending moderation): no pressure, six-plus-years callback to his May 2020 Doom9 diagnosis, Linux gap already covered (bravia_sei3d.py + ffmpeg #24531), end-of-summer wishes from Brazil. **Friendship request sent to r0lZ** (he had 0 friends) |
| 8 | *(Opus session)* mpv issue + PR — drafts and patch archived at `/K3D/GitHub/EchoSystems_Stereo3D/` | mpv (player side) | github.com/mpv-player/mpv | **FILED 2026-09-16, IN REVIEW** — [#18489](https://github.com/mpv-player/mpv/issues/18489) (stream-signalled stereo 3D ignored) + [PR #18490](https://github.com/mpv-player/mpv/pull/18490) (2 commits, Fixes #18489); review round 1 answered 2026-09-16 — 8 threads, owner's own words, 3 follow-ups offered (see below) |
| 9 | `ltt-3d-theater-post.md` | LTT forums (**first audience-facing target**) | [linustechtips.com/topic/1589907](https://linustechtips.com/topic/1589907-i-built-a-3d-theater-in-my-basement/) (reply to the 3D-theater video thread) | **POSTED 2026-09-16** — [comment 16936161](https://linustechtips.com/topic/1589907-i-built-a-3d-theater-in-my-basement/?do=findComment&comment=16936161) — the guide the video promised and the thread begged for; hooks: the never-delivered guide complaint + WeeemRCB's MakeMKV→BD3D2MK3D→HandBrake VR pipeline (their x265 gap = our x265 #970); iZ3D origin story as the human footnote. Pre/post snapshots in the private repo (`docs/research/`, "…after my comment.html") |

Not separately drafted: the ffmpeg `libx265.c` stereo3d wiring — fold
it into #5 as a secondary bullet if the tracker prefers one report, or
file it standalone after x265 (#4) lands. VidCoder needs no issue: its
maintainer already stated (RandomEngy/VidCoder#1318) that all asks
belong upstream in HandBrake; VidCoder inherits the fix via the
HandBrake core DLLs it ships.

## mpv PR #18490 — review round 1 (2026-09-16)

Hostile start: CounterPillow answered the owner's scope note with a
"mucho texto" meme image and closed a review thread with "Thanks for
the slop"; llyyr invoked the contribution guidelines over the AI
disclosure ("AI-slop written commit messages"). Once the replies went
purely factual and human-written, llyyr posted 8 technical review
threads (18:03–18:16Z) and the owner answered every one
(18:14–18:33Z, own words per doctrine). No apology was made; none was
needed — the thread converted to engineering on its own.

The one code objection — that the mapping switch "pointlessly
duplicates `STEREOMODE_STEREO3D_MAPPING`" — is refutable on facts:
the macro lives in `libavformat/matroska.h`, an FFmpeg-internal header
that is not installed, so mpv cannot include it (mpv consumes installed
headers only; `demux_mkv.c` vendors its own Matroska constants for the
same reason), and it maps Matroska → AVStereo3D (muxer direction, plus
half-width/height and WebM fields) while the patch needs the inverse,
which FFmpeg does not export as a table. mpv's `params.stereo3d` has
always used the Matroska StereoMode numbers, so the switch maps
straight into mpv's own vocabulary.

Follow-ups offered in-thread, pending maintainer decision:

1. shared mapping helper in `csputils.c` next to `mp_stereo3d_names[]`
   (also offered in the PR description);
2. export `AV_FRAME_DATA_STEREO3D` from `mp_image_to_av_frame()`
   (encode mode / lavfi symmetry);
3. read `AV_PKT_DATA_STEREO3D` in `demux_lavf.c` — the container tag
   currently dies at the demux layer there (`demux_lavf` frees the
   AVPacket without reading side data; it handles only replaygain,
   displaymatrix, DOVI config), and this becomes the second caller of
   the shared helper.

Raw material for the owner's replies:
`/K3D/GitHub/EchoSystems_Stereo3D/mpv-review-replies-draft.md` — the
posted replies are the owner's own rewording, per doctrine.

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