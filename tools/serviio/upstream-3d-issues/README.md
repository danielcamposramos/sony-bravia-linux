# Upstream 3D-signalling campaign — issue drafts and posted links

One draft per upstream target, built from the four verified research
lanes (2026-09-15). Every draft follows the campaign framing: we bring
the **diagnosis + a working fix**, not just a feature request.

**Status: all 9 original targets engaged + 4 more filed 2026-09-18 (see
the ecosystem section below).** **2 merged** (HandBrake PR #8100;
UMS PR #6330, merged 2026-09-19 by SubJunk as `bd032ab0`), the rest
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
| 6 | `mkvtoolnix-issue.md` | mkvmerge | codeberg.org/mbunkus/mkvtoolnix (keep it SHORT — maintainer closes verbose reports) | **FILED 2026-09-18 as [Codeberg issue #6309](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309)** (account: capitain_jack) — the owner reworded the draft as himself and filed it, no AI disclaimer per the mbunkus doctrine (understand every claim; the two source-file references are owned, not pasted). The earlier "signup paywalled" reading was a mix-up: the page in question was Codeberg's donate page, not a paywall. Codeberg ToU §2(1)7 verified first: it bans hosting AI-generated code *projects*, not human-authored issues — the repo is not mirrored there, the issue is **MAINTAINER ENGAGED 2026-09-19**: mbunkus asked for sample files carrying the SEI, and four synthetic ones were built and uploaded to `/6309/` on his SFTP server (`sbs-frame-packing-3.mp4` type 3, `tb-frame-packing-4.mp4` type 4, `remuxed-by-mkvmerge.mkv` showing the SEI surviving while StereoMode is absent, plus a README with the mapping and the generation commands). Under 60 KB total, generated with ffmpeg and x264 so there is no footage licensing question. Reply posted as [comment 23287171](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309#issuecomment-23287171), offering a patch rather than sending one, and noting a concrete finding from reading `src/common/avc/es_parser.cpp`: `handle_sei_nalu` already walks the payload loop but **returns as soon as it sees payload type 6**, so a frame-packing payload after a recovery point in the same NAL would never be reached. Self-caught before sending: the first README mapped row-interleaved to StereoMode 5; the correct value is 7 (5 is checkerboard). Verified against matroska.org and the file was replaced on the server. Codeberg's July 2026 rule restricts LLM-generated *projects*, autonomous agent activity and contributions that breach a project's own policy; mkvtoolnix has no *written* policy by choice, but the maintainer stated his position on meta-issue #6278 (skeptical, does not use LLMs, not fundamentally against them, requires that the human understands every change and can explain why it is correct), which this meets: the samples were generated, verified and explained here, and sent by the owner. **PATCH ACCEPTED IN PRINCIPLE 2026-09-19**: mbunkus replied "Absolutely, thanks for offering & for asking first", set the precedence rule (command line > container > elementary stream > default) and explained that MP4/MKV input uses the framed packetizer `output/p_avc.cpp`, not the ES parser, which only runs for inputs such as MPEG-TS; HEVC is the same. Design reply posted before any code as [comment 23288164](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309#issuecomment-23288164): one shared payloadType 45 parser for H.264 and H.265 (the leading fields are identical); `handle_sei_nalu` keeps walking past type 6; the framed path reuses the NALU walk `process_nalus` already does and parses only SEI NALUs until the first frame-packing message; results applied via `set_video_stereo_mode(..., option_source_e::bitstream)`, whose existing priority (10, below container 20 and command line 30) enforces his rule unchanged; one `rerender_track_headers()` as in `p_av1.cpp`; mapping per RFC 9559 Table 5. Asked two questions: bounded scan vs first packet only, and HEVC in the same PR or after. Standards cited: ITU-T H.264 and H.265 Annex D (payloadType 45), RFC 9559 §5.1.4.1.28.3, FFmpeg `decode_frame_packing_arrangement()`. **PAUSED awaiting his answer.** Then: patch, PR, and a closing message on the issue citing the PR. Source cloned at /K3D/GitHub/mkvtoolnix (submodules initialised); host build blocked by a Boost 1.90 header vs 1.74 library mismatch, so a Debian trixie container `mkvbuild` is set up, idle, with the tree and samples mounted read-only. |
| 7 | `bd3d2mk3d-forum-post.md` | BD3D2MK3D (r0lZ) | forum.videohelp.com thread 395498 | **POSTED + ANSWERED + CLOSED 2026-09-16** — [post #2803756](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803756); r0lZ replied same day ([#2803762](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803762)): suggestion 1 accepted (custom-encoder warning dialog), suggestion 2 needs clarification, cross-brand confirmation (his Samsung behaves the same), zero corrections to the diagnosis; his #604 (CLI = maybe, no promises — mountains win) answered by the owner's closing reply (POSTED 2026-09-16, [post #2803796](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803796)): no pressure, six-plus-years callback to his May 2020 Doom9 diagnosis, Linux gap already covered (bravia_sei3d.py + ffmpeg #24531), end-of-summer wishes from Brazil. **Friendship request sent to r0lZ** (he had 0 friends) |
| 8 | *(Opus session)* mpv issue + PR — drafts and patch archived at `/K3D/GitHub/EchoSystems_Stereo3D/` | mpv (player side) | github.com/mpv-player/mpv | **FILED 2026-09-16, IN REVIEW** — [#18489](https://github.com/mpv-player/mpv/issues/18489) (stream-signalled stereo 3D ignored) + [PR #18490](https://github.com/mpv-player/mpv/pull/18490) (2 commits, Fixes #18489); review round 1 answered 2026-09-16 — 8 threads, owner's own words, 3 follow-ups offered (see below) |
| 9 | `ltt-3d-theater-post.md` | LTT forums (**first audience-facing target**) | [linustechtips.com/topic/1589907](https://linustechtips.com/topic/1589907-i-built-a-3d-theater-in-my-basement/) (reply to the 3D-theater video thread) | **POSTED 2026-09-16** — [comment 16936161](https://linustechtips.com/topic/1589907-i-built-a-3d-theater-in-my-basement/?do=findComment&comment=16936161) — the guide the video promised and the thread begged for; hooks: the never-delivered guide complaint + WeeemRCB's MakeMKV→BD3D2MK3D→HandBrake VR pipeline (their x265 gap = our x265 #970); iZ3D origin story as the human footnote. Pre/post snapshots in the private repo (`docs/research/`, "…after my comment.html") |
| 10 | `jackdesbwa-message.md` | JackDesBwa (PhereoRoll3D / PhotoRoll3D / StereoWebViewer / threejs-StereoscopicEffects — the stereo-photo side) | his GitHub; check for an issues-welcome signal first, else profile contact | **POSTED 2026-09-18** as [PhereoRoll3D issue #2](https://github.com/JackDesBwa/PhereoRoll3D/issues/2) ("Thank you! And some other things...") by the owner; email-trigger watch, never poll — not an issue report. Opens with a **contribution offer, not a question**: StereoWebViewer's README has said `interleaved (i) [Not tested on actual device yet]` since 2018, and the owner has four devices that can test it (two active-shutter BRAVIAs, the parallax-barrier Optimus 3D, the Gadmei glasses-free tablet). Then the connect: our video-side SEI campaign is his photo-side wall from the other direction, and **not one of his four viewers can run on the set** because they all need WebGL the era browser lacks — which is exactly why our lane renders server-side. Two questions: practical anaglyph→SBS extraction on real community files, and which sources are still worth an adapter (with our measurement offered as the reason to ask: phereo API 504 at 60 s, stereopix 200 in 2.5 s, and the read that PhotoRoll3D is his own answer to phereo dying). Owner rewords and posts; re-check the 504 before sending, since being wrong about someone's community in a first message is expensive. **Correction drafted 2026-09-19** (`jackdesbwa-followup-mpo.md`): our line "the photo path was never wired to the 3D switch" is wrong — a spec-correct MPO engages 3D from USB on both sets; our writer's MP type was the bug, and it was never settled on the Brazilian firmware (Sony's own pages contradict by region). **POSTED 2026-09-19** as [comment 5739761627](https://github.com/JackDesBwa/PhereoRoll3D/issues/2#issuecomment-5739761627), owner-authorised (no AI policy on the repo) |
| 12 | `wiz3d-offer.md` | **wiz3D** (effcol/wiz3D) — the living continuation of the MIT-released iZ3D source (bo3b/iZ3D, "generously provided to us by Vadim and crew") | github.com/effcol/wiz3D | **POSTED 2026-09-19** as [issue #32](https://github.com/effcol/wiz3D/issues/32), owner-authorised (no AI policy in the repo). Offers what their CONTRIBUTING asks for and almost nobody has: working active-shutter 3D TVs, both GPU vendors in one machine (RTX 3060 + 5600G iGPU, Win11), and the swappable GTX 970/550 as a **genuine 3D Vision reference** to measure their output against — framed as a ruler, not a requirement, since wiz3D exists precisely so no legacy driver is needed (425.31 is Win10/8.1/7 only). Carries a measurement made while drafting: the TV's EDID declares `3D present`, SBS-half, top-and-bottom and frame-packing VICs, and **neither Windows nor Linux offers any desktop path to use it**. Suggests treating Proton as a headline (their #6 already has Steam Deck users) and Steam Frame (shipped 2026-09-14) as an output target (their #9 VR roadmap). States limited capacity plainly. Owner's stated goal: become a contributor there. Watch, never poll |
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

**Drafted here, then POSTED BY THE OWNER in his own words, same day** —
the three gated targets, where AI-written text either was objected to or
could not be sent from this session:

| Draft | Posted to |
|---|---|
| `mpv-followup-kodi-precedent.md` | [mpv PR #18490](https://github.com/mpv-player/mpv/pull/18490#issuecomment-5731208155) — the Kodi precedent: FFmpeg exposes the SEI as `stereo_mode` frame metadata, and Kodi reads it in one line |
| `ffmpeg-24531-followup.md` | [FFmpeg #24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531#issuecomment-63296) — the Matroska muxer never derives `StereoMode` from the stream, so a file can carry the SEI and no container tag |
| `mkvtoolnix-6309-followup.md` | [Codeberg #6309](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309#issuecomment-23228848) — the same gap from the other side, kept short |

All three are now on the email-trigger watch like everything else: never
poll, the owner pastes any reply.

Not followed up, deliberately: x265 #970 and StaxRip #1873 (nothing new
to add), HandBrake (merged), videohelp (left alone — our polling once
tripped its anti-bot), LTT (audience posts, owner's voice).

Not separately drafted: the ffmpeg `libx265.c` stereo3d wiring — fold
it into #5 as a secondary bullet if the tracker prefers one report, or
file it standalone after x265 (#4) lands. VidCoder needs no issue: its
maintainer already stated (RandomEngy/VidCoder#1318) that all asks
belong upstream in HandBrake; VidCoder inherits the fix via the
HandBrake core DLLs it ships.

## Universal Media Server — issue became code, PR #6330 (2026-09-19)

**The second project to ask for a patch, and the first to ask for it
unprompted.** After the measured-capabilities comment on
[#6329](https://github.com/UniversalMediaServer/UniversalMediaServer/issues/6329),
maintainer **SubJunk** replied: *"thanks for these details, do you have
any interest in providing code for these improvements?"* — so the issue
was converted into a patch the same day.

**[PR #6330](https://github.com/UniversalMediaServer/UniversalMediaServer/pull/6330)
— APPROVED by SubJunk and MERGED 2026-09-19T03:16Z as `bd032ab0f8e6`, CI
green (Lint, Linux 22.04/24.04, Windows, macOS ARM/Intel) — carries both
halves of the finding:**

- **The 3D signal.** `FFMpegVideo.getVideoTranscodeOptions()` now passes
  `-x264-params frame-packing=N` on libx264 transcodes whose output is
  frame-packed: side-by-side 3, top-bottom 4, row-interleaved 2. It reads
  `Output3DFormat` when the renderer sets one (that is the layout actually
  leaving the encoder) and falls back to the source layout; anaglyph and
  2D output are skipped, and it defers to an existing `-x264-params` in
  `CustomFFmpegOptions`. Same shape as the merged HandBrake change.
- **The audio and container profiles**, for the generation rather than one
  model: `Sony-BraviaEX725.conf`, `Sony-BraviaHX.conf`,
  `Sony-BraviaHX75.conf`. The EX725 profile **had no `f:mp4` line at all**,
  so every MP4 was transcoded on a set that plays H.264 in MP4 directly;
  E-AC3 is now declared for MP4 on all three (decoded up to 7.1, shown as
  "Dolby Digital Plus"); DTS-silent and Matroska-not-advertised are
  recorded as comments so the next person does not rediscover them.

**Issue #6329 answered in the owner's words and closed**, pointing at the
PR ([issuecomment-5738661601](https://github.com/UniversalMediaServer/UniversalMediaServer/issues/6329#issuecomment-5738661601)).

**Two triage comments posted** so the maintainer does not have to search
([5738663407](https://github.com/UniversalMediaServer/UniversalMediaServer/pull/6330#issuecomment-5738663407),
[5738674855](https://github.com/UniversalMediaServer/UniversalMediaServer/pull/6330#issuecomment-5738674855)).
Swept `3D`, `stereoscopic`, `frame packing`, `SBS`, `Output3DFormat`,
`anaglyph`, `Dolby`, `AC3`, `E-AC3`, `passthrough`, `5.1`,
`transcode audio`, `Bravia`, `KDL`. Honest result: **only #6329 is closed
by the PR.** #1775 (transcodes video when only the audio is unsupported)
and #5974 (no per-resolution level limits in a profile) are the same
family, different mechanism. **#6099 ruled out explicitly** — same brand
and the same word "MP4", but a 2017 Android-era KDL-43WF665 and a v15
regression, so conflating them would waste the maintainer's time. The old
3D tickets (#587, #878, #893, #745, #3486, #3723) are subtitles and
2D-to-3D requests, not the in-stream signal.

**Two limits stated in the PR itself, not left for review to find:** the
test suite could not be run here (no Maven on this machine, Java 25
against the project's 17), so the Java change has had a **syntax check
only** and needs CI; and the profile changes are applied to the configs
matching the two measured sets' chassis generations, leaving
`Sony-BraviaEX.conf`, `Sony-BraviaNX70x.conf` and `Sony-BraviaNX800.conf`
untouched because that hardware is not here to measure.

## Media3 / ExoPlayer — the second asker, five years later (2026-09-19)

**Google's own 2020 reply is the opening.** The request already existed:
[google/ExoPlayer#7869](https://github.com/google/ExoPlayer/issues/7869),
filed 2020-09-08, answered two days later by a Google engineer — *"As you
are the first one to ask for it, we will probably not look into it in the
near future. Feel free to make a pull request if you want the change to be
added soon."* — and labelled **low priority**. That reply makes demand the
deciding factor, and in five years nobody asked twice.

**Filed on the active tracker: [androidx/media#3419](https://github.com/androidx/media/issues/3419)**,
with [a comment on #7869](https://github.com/google/ExoPlayer/issues/7869#issuecomment-5738919730)
connecting the two so they do not drift apart.

The gap, read from their source rather than assumed: `MatroskaExtractor`
reads `ID_STEREO_MODE = 0x53B8`, `BoxParser` reads Apple's `vexu` box and
`HevcConfig` the 3D-reference-display SEI (both MV-HEVC spatial video),
but `H264Reader`'s SEI reader is documented as closed-captions only and
**`frame_packing` appears nowhere in the repository**. A frame-packed
stream with no container tag — the normal case for MPEG-TS and for any
MKV→TS remux — is invisible to ExoPlayer as 3D. One adjacent find:
`WebmConstants` defines `STEREO_MODE` but the muxer never writes it.

What the issue brings that 2020 did not: prior art in GStreamer (the full
read→caps→auto-write loop), FFmpeg's `AV_FRAME_DATA_STEREO3D`, VLC's
parser, HandBrake merged and UMS merged; a mapping table onto the
`C.STEREO_MODE_*` constants Media3 already gained for MV-HEVC; and the
791-byte hardware measurement. **Owner will sign Google's individual CLA**
if they accept the patch — his reasoning: the Steam Frame wave makes this
matter to Android the way the Steam Deck made Linux gaming matter, and
they will be glad of it later.

## VLC — gap measured, but the owner files it (2026-09-19)

**Measured, not assumed:** VLC 3.0.23 decodes the SEI (its H.264
packetizer maps payload 45 to `multiview_mode`, and the OpenGL renderer
draws stereo from it) and then **throws it away on re-encode** — default
transcode loses it, `--sout-x264-frame-packing=3` keeps it. GStreamer's
`x264enc` derives exactly that parameter from its input caps
automatically, so the patch is mechanical. VLC's chromecast module never
sets it either, though the cast path cannot deliver automatic 3D anyway
(the device decodes to HDMI). Full table and method in
`docs/3d-signalling-ecosystem.md`.

**Why this one is not ours to send.** VideoLAN publishes an explicit
ban on AI-generated contributions for its GSoC programme — scope beyond
GSoC could not be confirmed, because `wiki.videolan.org` returned 502 on
both attempts — and VideoLAN's president is on record criticising
AI-written merge requests from contributors unfamiliar with the codebase.
Repo README and the contribution guidelines contain no AI policy. Under
the standing rule, that is enough: **the owner writes and submits this
one in his own words**, with the patch, the measurement and the VLC
file/line references prepared as raw material. Open feature request to
attach it to: [videolan/vlc#29582](https://code.videolan.org/videolan/vlc/-/issues/29582).

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

## mpv PR #18490 — their AI rule, and how it was answered (2026-09-19)

**The rule.** mpv's `DOCS/contribute.md` allows AI-assisted code with
disclosure in the PR description, but since commit `e76a35ec9`
("disallow LLM in commit messages", **2026-09-17 — the day after this PR
was opened on 2026-09-16**) states: *"AI/LLM must not be used to write
commit messages or pull request descriptions. Clearly vibe-coded patches
will not be considered."* The disclosure rule itself dates from
`7ce58f7a0` (2026-01-12, "address the AI menace"). Dates recorded as
facts; no claim is made about whether the change was prompted by this PR.

**What was done, in order, all visible on the PR timeline:**
1. The owner reworded the two commit messages and force-pushed
   (`71c983c`, `baaf79f`). On comparison they were 95% and 99% word-for-word
   the original AI-written text with the `Co-Authored-By` trailer removed —
   the one state that could be read as hiding AI authorship.
2. **Reverted to honesty rather than disguise:** the original messages
   were restored **with their disclosure trailers** (`25ddd6b`, `1c5c04f`),
   code trees byte-identical to before (`466f490…`, `8bca494…`), pushed
   with a lease. Two accuracy fixes only, both in commit 2: the "repeated
   per IDR" claim scoped to x264 output and the files tested (DVB requires
   the SEI on every frame of a broadcast service), and the norm cited
   where it supports the code — the in-band signal's precedence, ETSI TS
   101 547-2 V1.2.1 clause 6.5, on the commit where the stream wins.
3. **The owner asked in his own words**
   ([issuecomment-5739297100](https://github.com/mpv-player/mpv/pull/18490#issuecomment-5739297100)):
   that he is not good with words in English and therefore disclosed the
   AI assistance, that the new rule landed a day after he filed, and asked
   them to judge the content for what it is. `maintainer_can_modify` is on,
   so the maintainers can reword at merge.

4. **Asked the project's most active maintainer for a technical read**
   ([issuecomment-5739342145](https://github.com/mpv-player/mpv/pull/18490#issuecomment-5739342145),
   2026-09-19 04:27): *"@kasper93 urging for a neutral technical review
   here."* Context from the project's own data: the PR had been reviewed
   by llyyr (author of the 2026-09-17 commit-message rule) and
   CounterPillow; kasper93 authored 193 of mpv's last 300 commits and had
   not yet engaged. mpv's founder, Vincent "wm4" Lang, left the project
   around 2020 (contested circumstances, see
   [#8254](https://github.com/mpv-player/mpv/issues/8254)), before the
   LLM era; no statement of his on AI was found.

**Declined along the way, recorded so the reasoning survives:** writing
deliberately broken English to pass AI text off as the owner's own. The
campaign's argument ("don't judge by the cover") only works while every
claim in the record is honest and checkable; a disguised message is the
one thing that would hand the "AI menace" framing real evidence.

**If it stalls from here**, the owner's position is a fully disclosed,
measured, reviewed patch waiting on the maintainers. The fallback is a
maintained **patched build** (the two commits rebased on upstream, CI
releases) rather than a hard fork, framed by who it serves — 3D and
Steam Frame users — not as an answer to mpv.

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