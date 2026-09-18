# Upstream 3D-signalling campaign — issue drafts and posted links

One draft per upstream target, built from the four verified research
lanes (2026-09-15). Every draft follows the campaign framing: we bring
the **diagnosis + a working fix**, not just a feature request.

**Status: all 9 original targets engaged + 4 more filed 2026-09-18 (see
the ecosystem section below).** 1 merged (HandBrake PR #8100), the rest
posted/filed — including mkvmerge, whose Codeberg signup had read as a
paywall but turned out to be the donate page wearing the same layout
(account created; issue filed). First audience-facing target: the LTT
forum post (target #9): the guide the theater video promised in its
description and the thread spent two weeks asking for. The videohelp
post cleared moderation 2026-09-16 (post #2803756); the mpv player-side
pair (issue #18489 + PR #18490, from a parallel Opus session) completes
the pipeline end to end: encode → remux → robustness → player → DLNA.
PR #18490 is in review (hostile start, then 8 technical threads — all
answered same day in the owner's own words, no apology; see the mpv
review section below). Per campaign doctrine, the drafts here are raw
material — the owner approves/rewords and posts; no AI-drafted text
goes out without owner approval.

| # | Draft file | Target | Where it goes | Priority |
|---|---|---|---|---|
| 1 | `ffmpeg-eexist-bug.md` + `ffmpeg-eexist-facts.md` | FFmpeg | code.ffmpeg.org tracker (bug) | **POSTED 2026-09-16** — [issue #24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530) (owner's own reworded text + reproducer attached) |
| 2 | `handbrake-issue.md` | HandBrake | comment on open issue #5826 (galad87 invited a patch) | **RESOLVED — PR #8100 MERGED 2026-09-16** ([b0145ad](https://github.com/HandBrake/HandBrake/pull/8100)); #5826 closed by the merge |
| 3 | `staxrip-issue.md` | StaxRip | comment on open issue #1873 (answers a stranded user) | **POSTED 2026-09-15** — [#issuecomment-5685902578](https://github.com/staxrip/staxrip/issues/1873#issuecomment-5685902578) |
| 4 | `x265-issue.md` | x265 | github.com/Multicorewareinc/x265 (issues enabled) | **POSTED 2026-09-15** — [issue #970](https://github.com/Multicorewareinc/x265/issues/970) |
| 5 | `ffmpeg-bsf-feature.md` | FFmpeg | code.ffmpeg.org tracker (enhancement) | **POSTED 2026-09-16** — [issue #24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531) (owner's own reworded text) |
| 6 | `mkvtoolnix-issue.md` | mkvmerge | codeberg.org/mbunkus/mkvtoolnix (keep it SHORT — maintainer closes verbose reports) | **FILED 2026-09-18 as [Codeberg issue #6309](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309)** (account: capitain_jack) — the owner reworded the draft as himself and filed it, no AI disclaimer per the mbunkus doctrine (understand every claim; the two source-file references are owned, not pasted). The earlier "signup paywalled" reading was a mix-up: the page in question was Codeberg's donate page, not a paywall. Codeberg ToU §2(1)7 verified first: it bans hosting AI-generated code *projects*, not human-authored issues — the repo is not mirrored there, the issue is |
| 7 | `bd3d2mk3d-forum-post.md` | BD3D2MK3D (r0lZ) | forum.videohelp.com thread 395498 | **POSTED + ANSWERED + CLOSED 2026-09-16** — [post #2803756](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803756); r0lZ replied same day ([#2803762](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803762)): suggestion 1 accepted (custom-encoder warning dialog), suggestion 2 needs clarification, cross-brand confirmation (his Samsung behaves the same), zero corrections to the diagnosis; his #604 (CLI = maybe, no promises — mountains win) answered by the owner's closing reply (POSTED 2026-09-16, [post #2803796](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803796)): no pressure, six-plus-years callback to his May 2020 Doom9 diagnosis, Linux gap already covered (bravia_sei3d.py + ffmpeg #24531), end-of-summer wishes from Brazil. **Friendship request sent to r0lZ** (he had 0 friends) |
| 8 | *(Opus session)* mpv issue + PR — drafts and patch archived at `/K3D/GitHub/EchoSystems_Stereo3D/` | mpv (player side) | github.com/mpv-player/mpv | **FILED 2026-09-16, IN REVIEW** — [#18489](https://github.com/mpv-player/mpv/issues/18489) (stream-signalled stereo 3D ignored) + [PR #18490](https://github.com/mpv-player/mpv/pull/18490) (2 commits, Fixes #18489); review round 1 answered 2026-09-16 — 8 threads, owner's own words, 3 follow-ups offered (see below) |
| 9 | `ltt-3d-theater-post.md` | LTT forums (**first audience-facing target**) | [linustechtips.com/topic/1589907](https://linustechtips.com/topic/1589907-i-built-a-3d-theater-in-my-basement/) (reply to the 3D-theater video thread) | **POSTED 2026-09-16** — [comment 16936161](https://linustechtips.com/topic/1589907-i-built-a-3d-theater-in-my-basement/?do=findComment&comment=16936161) — the guide the video promised and the thread begged for; hooks: the never-delivered guide complaint + WeeemRCB's MakeMKV→BD3D2MK3D→HandBrake VR pipeline (their x265 gap = our x265 #970); iZ3D origin story as the human footnote. Pre/post snapshots in the private repo (`docs/research/`, "…after my comment.html") |
| 10 | `jackdesbwa-message.md` | JackDesBwa (PhereoRoll3D / PhotoRoll3D / StereoWebViewer / threejs-StereoscopicEffects — the stereo-photo side) | his GitHub; check for an issues-welcome signal first, else profile contact | **POSTED 2026-09-18** as [PhereoRoll3D issue #2](https://github.com/JackDesBwa/PhereoRoll3D/issues/2) ("Thank you! And some other things...") by the owner; email-trigger watch, never poll — not an issue report. Opens with a **contribution offer, not a question**: StereoWebViewer's README has said `interleaved (i) [Not tested on actual device yet]` since 2018, and the owner has four devices that can test it (two active-shutter BRAVIAs, the parallax-barrier Optimus 3D, the Gadmei glasses-free tablet). Then the connect: our video-side SEI campaign is his photo-side wall from the other direction, and **not one of his four viewers can run on the set** because they all need WebGL the era browser lacks — which is exactly why our lane renders server-side. Two questions: practical anaglyph→SBS extraction on real community files, and which sources are still worth an adapter (with our measurement offered as the reason to ask: phereo API 504 at 60 s, stereopix 200 in 2.5 s, and the read that PhotoRoll3D is his own answer to phereo dying). Owner rewords and posts; re-check the 504 before sending, since being wrong about someone's community in a first message is expensive |
| 11 | `kodi-issue.md` | Kodi (player + DLNA server, 21k★) | github.com/xbmc/xbmc | **POSTED 2026-09-18 as [#29337](https://github.com/xbmc/xbmc/issues/29337); v1 WRONG, EDITED same day** into the DLNA profile report, with an edit note saying plainly that v1 was wrong. We claimed Kodi never reads the SEI, from `gh search code` finding no stereo side-data symbols. Minutes later a Docker test (Kodi 21.2, Debian trixie, Xvfb, `--debug`) with a neutrally named SEI-only MP4 logged `autodetected stereo mode for movie mode left_right`: `DVDVideoCodecFFmpeg.cpp:1043` reads `stereo_mode` from the decoded frame's **metadata**, which FFmpeg's H.264 decoder fills from the SEI. Code search does not index everything; the lesson is in memory (verify by running before filing). The DLNA side, measured the same way through Kodi's own UPnP server as a TV would see it: files served **byte-exact** (SEI and Matroska tag intact), but **every MP4 is advertised as `DLNA.ORG_PN=MPEG4_P2_SP_AAC`** (MPEG-4 Part 2) from a static table, `lib/libUPnP/Platinum/Source/Core/PltProtocolInfo.cpp:95`, which has no `AVC_MP4_*` entries; confirmed on a plain H.264+AAC MP4; unreported. Harmless for the BRAVIAs (they advertise `video/mp4:*`); MKV is served as `video/x-matroska`, which the sets do not accept and Kodi never transcodes — which is why Kodi's server failed the owner years ago and Serviio won. **Hardware result, EX725, 2026-09-18: through Kodi's server an SEI-only MP4 auto-engages 3D, the same file minus its SEI plays flat, the MKV is not listed** — the mislabel is harmless to this set, as the edited issue says. Harness: `tools/kodi-dlna-test/`. Email-trigger watch, never poll |

## Follow-ups, 2026-09-18 — posted where AI assistance is not gated, drafted where it is

New measurements this day: a second, independent DLNA server (Kodi's,
which never transcodes) reproduces the 3D result byte-exact, and the
audio half turns out to be the same story — these sets decode **Dolby
Digital Plus internally, 7.1 included**, from MP4, while a remux to TS
forces it down to AC-3.

**Posted:**

| Target | Comment |
|---|---|
| Gerbera #3937 | [issuecomment-5731131092](https://github.com/gerbera/gerbera/issues/3937#issuecomment-5731131092) — the SEI alone is sufficient (second server, byte-exact), and the remux costs the soundtrack as well as the 3D flag |
| Universal Media Server #6329 | [issuecomment-5731131343](https://github.com/UniversalMediaServer/UniversalMediaServer/issues/6329#issuecomment-5731131343) — measured renderer capabilities for their Sony BRAVIA configs; **E-AC3 should not be transcoded for these sets in MP4** |
| Jellyfin PR #18060 | [issuecomment-5731138084](https://github.com/jellyfin/jellyfin/pull/18060#issuecomment-5731138084) — FFmpeg exposes the SEI as `stereo_mode` frame metadata, which is how Kodi detects it in one line |
| repo Discussion #1 | [discussioncomment-18501864](https://github.com/danielcamposramos/sony-bravia-linux/discussions/1#discussioncomment-18501864) — the Surround profile and the second-server confirmation, for the Serviio community |

**Drafted, held for the owner** (each says why in its header):

| Draft | Target | Why it is not posted from here |
|---|---|---|
| `mpv-followup-kodi-precedent.md` | mpv #18490 / #18489 | AI-written text was objected to on that PR; owner's words only |
| `ffmpeg-24531-followup.md` | FFmpeg #24531 | no credentials for code.ffmpeg.org in this session |
| `mkvtoolnix-6309-followup.md` | Codeberg #6309 | the owner filed it as himself; short, and fine to send nothing |

Not followed up, deliberately: x265 #970 and StaxRip #1873 (nothing new
to add), HandBrake (merged), videohelp (left alone — our polling once
tripped its anti-bot), LTT (audience posts, owner's voice).

Not separately drafted: the ffmpeg `libx265.c` stereo3d wiring — fold
it into #5 as a secondary bullet if the tracker prefers one report, or
file it standalone after x265 (#4) lands. VidCoder needs no issue: its
maintainer already stated (RandomEngy/VidCoder#1318) that all asks
belong upstream in HandBrake; VidCoder inherits the fix via the
HandBrake core DLLs it ships.

## repo Discussion #1 — Samsung cross-brand follow-up posted (2026-09-18)

Posted the Samsung data-point update on the project's own Serviio-community
discussion: https://github.com/danielcamposramos/sony-bravia-linux/discussions/1#discussioncomment-18496283
Kept the honest framing (r0lZ's Samsung is a symptom-level confirmation,
not the controlled two-file mechanism test). On the email-trigger watch
like the rest; no polling.

## DLNA-server ecosystem — SEI finding filed on three projects (2026-09-18)

The campaign's second wave: the servers that *serve* the files, not the
tools that make them. A DLNA server that remuxes MKV → TS drops the
Matroska StereoMode tag, and a file that carries only the SEI is the one
hardware reads — so the finding applies to the serving side too. All
three filed by the owner from here after he confirmed no AI gate
existed; disclosure block kept where the project's norms expect it.

- **Jellyfin** — comment on PR #18060 ("Flatten frame packed 3D video",
  the layout-detection point): [#issuecomment-5726381078](https://github.com/jellyfin/jellyfin/pull/18060#issuecomment-5726381078).
  Draft + posted log: `docs/jellyfin-18060-comment-draft.md`
- **Universal Media Server** — feature request: [issue #6329](https://github.com/UniversalMediaServer/UniversalMediaServer/issues/6329)
- **Gerbera** — issue #3937, framed as an *optional no-remux SEI
  injection* step after the owner's correction (they can keep "no
  remux" and still inject the signal): [issue #3937](https://github.com/gerbera/gerbera/issues/3937).
  The initial hold ("direct-serves so the bug doesn't apply") was wrong
  — the SEI must be present regardless of remux.

**Watch (email-trigger only, never poll — owner's rule):** all three
threads are the owner's, so GitHub emails him on every reply. Baselines
2026-09-18: Jellyfin #18060 (7 comments), UMS #6329 (0), Gerbera #3937
(0). When a reply lands he pastes it; the technical answer is drafted
together. mkvmerge #6309 joins the same rule on Codeberg's own
notifications.

## LTT forums — Steam Frame cross-comment posted (2026-09-18)

Second audience-facing post, chronological companion to the 3D-theater
comment: [findComment-16936512](https://linustechtips.com/topic/1642726-the-steam-frame-changes-everything-full-review/?do=findComment&comment=16936512)
— the Steam Frame review thread, posted because that video *does*
discuss 3D content (~21:10); the "first 30 minutes" video does not, so
its thread was deliberately skipped (campaign rule: only where 3D
content is actually discussed). Cross-cites the earlier projector
comment; the two posts now reference each other chronologically.
Draft: `docs/ltt-steamframe-forum-comment.md`

## mpv issue #18489 — cross-brand / ecosystem follow-up (2026-09-18)

Posted a context comment on the issue (not the PR):
https://github.com/mpv-player/mpv/issues/18489#issuecomment-5726271480

It reframes the change as fixing a standardized, ecosystem-wide gap
rather than a two-TV special case: the frame_packing SEI is H.264 (2010)
and DVB's authoritative frame-compatible carrier (ETSI TS 101 547-2 cl
6.4.1/6.5, stated with honest scope — binds DVB receivers; HDMI 1.4a is a
separate path); the "3D file plays flat" symptom is documented for years
across Plex/Jellyfin/Serviio/MakeMKV/AVS; and it is cross-brand (r0lZ's
Samsung, with the BD3D2MK3D-writes-both caveat). Full basis in
docs/3d-signalling-ecosystem.md. Owner posted in his own words.

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

Runnable evidence for the second commit:
[mpv-sei-frequency-repro.md](mpv-sei-frequency-repro.md) — four commands
against stock ffmpeg, no patched mpv needed, that show the side data
landing on keyframes and nothing else (frames 1/49/97/145/193 at `-g 48`),
with a no-SEI negative control. Verified on two hosts spanning FFmpeg
6.1.6 and 9.0.1 on 2026-09-17.

Raw material for the owner's replies:
`/K3D/GitHub/EchoSystems_Stereo3D/mpv-review-replies-draft.md` — the
posted replies are the owner's own rewording, per doctrine.

## Issue #18489 — the quiet reading (noted 2026-09-17)

Worth keeping because it is the only signal in the episode that came
from neither side of the argument.

[#18489](https://github.com/mpv-player/mpv/issues/18489) (filed
2026-09-16T10:08:09Z) carries **two 👍 reactions and zero comments**:

| reaction | account | timestamp (UTC) | after filing |
|---|---|---|---|
| 👍 | netExtra | 2026-09-16T12:26:59Z | 2 h 19 min |
| 👍 | fakelok76 | 2026-09-17T06:49:26Z | 20 h 41 min |

Both arrived while the PR thread was still arguing about authorship.
Neither account took part in that thread.

**netExtra is not a passing reader.** The same account filed
[#17632](https://github.com/mpv-player/mpv/issues/17632) in March 2026
(OSD misplaced on 3D content in fullscreen, watched through a VR headset)
and it is still open. The 3D surface in mpv has few users filing bugs, and
this is one of them reading ours. The map is in
[mpv-3d-landscape.md](mpv-3d-landscape.md).

No claim is being made about what a 👍 means — it is not a review, and
two is not a groundswell. It is recorded because the reactions are the
only datapoint in the exchange that speaks to the *bug* rather than to
who wrote the text about it, and reactions are silently editable
afterwards, so the counts and timestamps are captured here as read on
2026-09-17 via `gh api repos/mpv-player/mpv/issues/18489/reactions`.

The episode's doctrine proverb is recorded in
[docs/judging-by-the-cover.md](../../../docs/judging-by-the-cover.md):
"Não julgue um livro pela capa" / "Don't judge a book by its cover" —
judge the artifact, not the authorship.

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