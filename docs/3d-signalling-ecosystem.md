# The frame-packing SEI: the missing piece everyone suffered, no one named

A cross-brand, cross-software map of why file-based 3D playback fails, and
why the fix is one standard signal. Assembled 2026-09-18 from the
BD3D2MK3D community thread (Internet Archive), the DLNA-server support
forums, the H.264 specification, and this project's own hardware testing.
Compiled here because, as far as we can find, **this map exists nowhere
else in one place.**

## The two signals, and which one was missing

3D stereoscopic video can be flagged two ways:

1. **The container tag** — Matroska's `StereoMode` element. It sits in
   the MKV wrapper. Encoders, rippers, players and mpv have read it for
   years. It was never the problem.
2. **The in-stream signal** — the H.264 `frame_packing_arrangement` SEI
   message (payload type 45), carried inside the video elementary stream
   itself.

The missing piece, that everyone suffered and no one pinpointed, is the
second one. When a file is delivered by any path that keeps only the
elementary stream and drops the container — a DLNA server remuxing MKV to
MPEG-TS, most notably — the `StereoMode` tag is gone and **only the SEI
survives**. If nothing wrote the SEI into the stream, the set has nothing
to read, and 3D plays flat.

## Why the SEI is the universal one, not a per-set quirk

The `frame_packing_arrangement` SEI is not a manufacturer feature. It is
part of the H.264/AVC standard, added in **Amendment 1 (October 2009)**,
the same amendment that added the Stereo High Profile. It defines the
frame-compatible arrangements every 3D pipeline uses: side-by-side,
top-and-bottom, checkerboard, column and row interleave.

It is also the signal DVB made **authoritative** for frame-compatible 3D
broadcast. DVB's spec ETSI TS 101 547-2 (DVB A154-2), clause 6.4.1,
requires ("shall") a frame-compatible 3DTV service to carry the H.264
`frame_packing_arrangement` SEI **with every frame**, and clause 6.5
states the SEI signalling "takes precedence over other signalling as
regards video format" — over the DVB-SI descriptors (PMT/SDT/EIT), which
the same spec limits to a presence flag and EPG hints, not the actual
stereo format. The HEVC variant (DVB A154-4) repeats the design word for
word. So the in-stream SEI is not one option among several; in the DVB
broadcast standard it is the definitive carrier of the 3D arrangement.

Two honest limits on how far that reaches:

- It is a normative requirement on a **DVB-compliant frame-compatible
  receiver** decoding a live broadcast. It is not, by itself, proof that
  every "3D-ready" set of 2010-2013 implemented it — real FC-3DTV
  broadcasts were rare and short-lived, and a spec "shall" binds
  conformant implementations, not every shipped firmware.
- Much era 3D content reached TVs over **HDMI** from a Blu-ray player or
  console, a path governed by HDMI 1.4a's own frame-packing 3D
  signalling, separate from the in-stream SEI. Projectors are the clean
  carve-out here: typically HDMI-fed, no broadcast tuner.

What makes the SEI the right target regardless is the combination: it is
the **H.264-standard** tool (payload 45, Annex D, added to the spec in
2010), it is the **authoritative broadcast** signal per DVB, and — the
part this project proved directly — real hardware reads it from files.
Our two BRAVIA sets auto-engage 3D on exactly this SEI and ignore the
container tag, demonstrated with single-variable clips. The spec says it
should be read; the panels in front of us do read it.

## 3D Blu-ray is a different mechanism (and why tools convert it)

3D Blu-ray does not use the frame-packing SEI. It uses **MVC (Multiview
Video Coding)**, the other H.264 3D extension, carrying two full views.
Frame-compatible 3D (SBS/TAB) and MVC are cousins from the same era but
distinct. This is exactly why authoring tools like BD3D2MK3D exist: they
take an MVC 3D Blu-ray and produce a frame-compatible SBS/TAB file, in
which the `frame_packing_arrangement` SEI is the flag that makes it
auto-engage. BD3D2MK3D has written that SEI (via x264 `--frame-packing`)
for years, alongside the Matroska tag.

## The symptom is ecosystem-wide, and old

The "3D SBS/TAB file plays flat" problem is documented for years across
every major DLNA/media solution, each thread describing the same
behaviour without naming the root cause:

- Plex: [Some 3D SBS and up-under MKV files not recognised](https://forums.plex.tv/t/some-3d-sbs-and-up-under-mkv-files-not-recognised/51445)
- Jellyfin: [3D Full SBS video detection and playback](https://forum.jellyfin.org/t-3d-full-sbs-video-detection-and-playback)
- Serviio: multiple threads on MKV recognition and 3D delivery on the
  [serviio.org forum](https://www.serviio.org/forum/).
- MakeMKV: [Anyone have 3D movie success?](https://forum.makemkv.com/forum/viewtopic.php?t=36903)
- AVS Forum: [Properly Playing Back A 3D MKV](https://www.avsforum.com/threads/properly-playing-back-a-3d-mkv.3235394/)

A recurring, telling detail in those threads: files **without** the
container stereo flag sometimes play in 3D while files **with** it play
flat, and converting through HandBrake "fixes" it. Both are explained by
the same mechanism — what the set actually reads is the in-stream SEI, and
whichever delivery path happens to preserve or produce it is the one that
works. Nobody in those threads isolated that; the servers drop the tag
and none of them write the SEI.

## The cross-brand hardware seen in the BD3D2MK3D community

Compiled from the BD3D2MK3D support thread (videohelp #395498), read via
Internet Archive snapshots (survey covers 18 of the 20 pages; pages 15
and 20 did not return a usable snapshot). Source, per page, is the
archived thread. Categorised honestly, because the thread mixes displays,
disc players and projectors, and because BD3D2MK3D writes both the SEI and
the container tag, so a "works" report shows compatibility with a
correctly-authored 3D file, not which signal a given device read.

**3D televisions** (the two brands that recur across the thread)
- Samsung 3D TVs — the tool author (r0lZ) actively tests against his own
  "capricious" Samsung 3D set: his encodes "play correctly with 10
  different software players, and with my Samsung 3D TV", and he plays
  them by connecting a hard disc to the set directly. He also reports that
  Samsung set has "exactly the same problem" as the Sony sets this project
  documents. (Note: hard-disc/USB playback can read the Matroska tag, so
  this shows compatibility, not that the Samsung reads the SEI
  specifically.)
- LG 3D TVs — LG passive 3D panels are prominent enough that BD3D2MK3D
  added a dedicated Half-TAB option to keep full 1080p on them, and a user
  reports the built-in Plex app on an LG smart TV plays the files
  natively.
- Generic passive-LED and active-shutter sets discussed throughout.

**3D disc players (not TVs — recorded for completeness)**
- LG, Sony, Panasonic, Philips, Toshiba Blu-ray/DVD players appear by
  model across the thread as gear people fed BD3D2MK3D output to.

**Projectors**
- Active DLP projectors (the honest exception above: HDMI-fed, no
  broadcast-decode obligation).

This is the "nowhere-seen" list the compilation exists to start. It is a
compatibility record of the frame-compatible 3D file era across brands,
not a per-device SEI-reading proof; the clean mechanism test (serve one
clip with the SEI and one without, see which flips) is the open ask in
[repo discussion #1](https://github.com/danielcamposramos/sony-bravia-linux/discussions/1).

## Recorded 3D broadcasts — another SEI-carrying source, another stranded owner

The frame-packing SEI was not only an authoring choice, it was on the air.
Sky 3D, Europe's first dedicated 3D channel, launched 3 April 2010 and
broadcast **side-by-side frame-compatible** H.264 so it would work over
the existing Sky+ HD boxes; the channel closed 9 June 2015. Other DVB
frame-compatible 3D services and trials ran in the same window. By the DVB
spec above, every one of those services carried the `frame_packing`
SEI with every frame.

A DVB recorder captures the transport stream as broadcast, so **a
recording of one of those 3D broadcasts carries the SEI verbatim** — the
digital equivalent of taping a broadcast on a VCR, except the tape is a
`.ts` file that already contains the exact signal a 3D TV needs. Played
back on modern software that ignores the SEI, it shows flat, the same gap
as everywhere else in this document.

This adds another affected group with a clean right-to-repair shape: an
owner who time-shifted a 3D broadcast they were entitled to record now
holds the surviving copy of content whose channel no longer exists (Sky
3D has been off air since 2015), and software will not play it in 3D
although the recording carries the correct, standardized flag.

Two honest limits:
- **Encrypted PVRs are a separate problem.** Sky's own recordings are
  stored encrypted and locked to the box, so a Sky+ HD recording is not a
  portable file regardless of the SEI. The clean case is an
  **unencrypted / free-to-air** DVB 3D broadcast recorded on a generic
  DVB PVR or tuner card, which yields a plain `.ts` carrying the SEI.
- How much 3D broadcasting was recorded is niche, not mass-market. The
  point is that the recordings exist, they carry the standard signal, and
  the same software gap strands them.

Sources: [Sky 3D, launch and side-by-side format](https://en.wikipedia.org/wiki/Sky+_HD); community/technical detail on the side-by-side choice and Sky+ HD compatibility ([TV Forum thread](https://www.tvforum.co.uk/tvhome/sky3d-30917/page-2)). DVB SEI mandate as cited above (ETSI TS 101 547-2).

## The chain, now mapped end to end

The reason this went unsolved is that no single project owned the whole
path. This one does now:

- **Write the SEI** — HandBrake merged it ([PR #8100](https://github.com/HandBrake/HandBrake/pull/8100)),
  x264 has `--frame-packing`, x265 has an open request ([#970](https://github.com/Multicorewareinc/x265/issues/970)),
  FFmpeg has a bug and a lossless-injector request ([#24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530),
  [#24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531)), and this
  repo ships `bravia_sei3d.py` for lossless in-file injection.
- **Read the SEI** — mpv was ignoring it ([issue #18489](https://github.com/mpv-player/mpv/issues/18489),
  [PR #18490](https://github.com/mpv-player/mpv/pull/18490)); hardware 3D
  TVs already read it, by the DVB obligation above.
- **Deliver it** — a Serviio profile plus SEI injection restores fully
  automatic 3D over DLNA on stock free software (this repo,
  `tools/serviio/`).

## The player and framework survey (2026-09-19)

Where every open project in the chain actually stands, read from source
rather than assumed. Two of them already do it correctly, which is the
most useful finding: it makes the fix demonstrably mechanical rather
than novel.

| Project | Reads the SEI | Writes/keeps it on transcode | Verdict |
|---------|---------------|------------------------------|---------|
| **GStreamer** | yes — `gst_h264_parser_parse_frame_packing()` decodes payload 45; `h264parse` publishes `GstVideoMultiviewMode` on caps | **yes, automatically** — `x264enc` derives `i_frame_packing` from the input caps by default | **already correct — the reference implementation** |
| **MPC-BE** | yes — bundles FFmpeg's SEI decode, plus its own Matroska `StereoMode` read **and write**, and a real Stereo3D renderer transform | n/a (player) | **already correct** |
| **VLC** | yes — `hxxx_sei.h` defines type 45, `h264.c` maps it to `multiview_mode`, OpenGL renderer builds a stereo matrix from it, libVLC exposes it | **no** — `sout-x264-frame-packing` exists but is manual opt-in; nothing derives it from the decoded `multiview_mode`, and the chromecast module never sets it | **gap — measured below** |
| **Media3 / ExoPlayer** | **no** — Matroska `StereoMode` and Apple `vexu`/MV-HEVC only; `frame_packing` appears nowhere in the repo; `H264Reader`'s SEI reader is closed-captions only | no — `WebmConstants` defines `STEREO_MODE` but the muxer never writes it | **gap — filed** |
| **Chromecast** | — | — | **not contributable** — receiver and Cast SDK are closed, the public repos are sample apps, and the Cast media documentation never mentions 3D, stereo or frame packing at all |
| MPC-HC | no stereo subsystem in tree | — | skip — the feature already lives in its own more active fork (MPC-BE) |
| Emby | — | — | dead public repo (frozen at 2018, the code Jellyfin forked) |
| Plex | — | — | closed, no surface |

**VLC, measured on VLC 3.0.23 (owner's workstation, 2026-09-19).** A
three-second H.264 clip encoded with `-x264-params frame-packing=3`
(ffprobe confirms `side_data_type=Stereo 3D`), then re-encoded by VLC:

| VLC command | frame-packing SEI in the output |
|---|---|
| `--sout '#transcode{vcodec=h264}:std{...}'` | **gone** |
| same, plus `--sout-x264-frame-packing=3` | present |

So VLC decodes the signal, uses it to render stereo, and then discards
it at the encoder unless the user already knows the flag exists. The
fix is the one GStreamer already ships: derive the encoder parameter
from the layout the decoder just reported.

**The Chromecast answer, for the record.** The signal loss in VLC's cast
path is real in code, but even a perfect stream cannot deliver automatic
3D through a Chromecast: the device decodes the stream and outputs HDMI,
so the SEI is consumed at the decoder, and Cast has no frame-packing
signalling of its own. Manual side-by-side mode on the television is the
only route there. The contributable surface is VLC's sender module, not
anything of Google's.

## A second server, the same result (Kodi, owner-verified 2026-09-18)

The signalling fix was first proven through Serviio. The obvious
objection is that it could be a Serviio artefact. So the same experiment
was run through a different maker's server: Kodi's built-in UPnP/DLNA
server, from Debian main, in a throwaway container
([tools/kodi-dlna-test/](../tools/kodi-dlna-test/README.md)), to the
KDL-46EX725.

| File | Signal | On the set |
|---|---|---|
| *3D Bonsai*, as published | SEI, no container tag | **3D engaged automatically** |
| the same file minus its SEI (791 bytes, nothing else) | none | plays flat |
| *3D Maestro* (Joe Penna), MKV remuxed losslessly to MP4 | SEI | **3D engaged automatically** |
| *3D Maestro*, original MKV | SEI + Matroska tag | **not listed** by the set |

Two conclusions for the chain. **The SEI is sufficient on its own, from
any server that passes it through**: Kodi serves files byte-exact, so the
signal arrives, and the set switches. And **the container is the other
gate**: the set filters Matroska out of the list before playback, so a
3D MKV is invisible to it however it is signalled. That makes the
cheapest complete path for an existing 3D rip a lossless one: remux MKV
to MP4, add the SEI if it is missing (`tools/bravia_sei3d.py`), and serve
it from anything that does not transcode.

**The same issue, on audio (owner's framing, same day).** The original
audio tracks were tested the same way, each copied bit-exact into MP4:

| File (60 s, lossless cut, original track, SEI added) | Audio | On the set |
|---|---|---|
| E1 *Gravity* | AC-3 5.1 | **3D engaged**, OSD **"Dolby Digital"** |
| E2 *A Lenda do Rei Macaco* | AC-3 2.0 | **3D engaged**, **"Dolby Digital"** |
| E3 *Brahmastra* | E-AC3 5.1 | **3D engaged**, **"Dolby Digital Plus"** |
| E4 *Avatar: The Way of Water* | E-AC3 7.1 | **3D engaged**, **"Dolby Digital Plus"** |
| E5 *Predador* | AAC 5.1 | **3D engaged**, no Dolby indicator (AAC) |
| E6 *Gravity* | DTS 5.1 | 3D engaged, **no audio** |
| E7 *Gravity* | TrueHD 7.1 | cannot be put in MP4 (FFmpeg's TrueHD-in-MP4 is experimental and failed); as MKV, **not listed** |

The set decodes **Dolby Digital Plus natively** from MP4 — while this
project's own Serviio profile converts every E-AC3 track to 384k Dolby
Digital, because it remuxes to MPEG-TS and this set cannot take E-AC3 in
TS. The information is in the file, the TV can use it, and the delivery
throws it away: the container is the gate for audio exactly as it was
for 3D. And it matters beyond the TV's own speakers, since the set
passes Dolby on to a receiver over ARC; a converted track is what the
receiver would get. DTS is the one format that must be converted, and
TrueHD cannot even be carried in MP4.

It also closes a loop in the owner's own history: years ago Kodi's
server "did not work" for 3D on these sets. Measured now, it could not
have: the rips of the time were MKV, which never appeared, and no MP4
carried an SEI because nothing wrote one.

## Why this is worth spreading

The demand is current and the pain is on record from people who would
know. Linus Sebastian (LTT) built a home 3D projector setup specifically
because, to his surprise, "dozens of movies are still being released on
3D Blu-ray every single year" (''Home 3D Movie Projector Setup'', ~0:26),
while "no new hardware supports 3D anymore" (~0:53). The single hardest
part of the whole build was not the optics or the screen, it was getting
the content to play: he says the file side "required more tinkering
behind the scenes than believe it or not anything else we've done so
far" (~10:20), ending up ripping his own 3D Blu-rays and following a
Reddit thread to remux them into a working 3D file format by hand
(~10:34). That is exactly the gap this map is about: the signalling
exists, the discs exist, the hardware reads it, and the last mile,
getting the flag into the file, is left to hand-tooling.

The modern "answer" underlines it rather than closing it. In the Steam
Frame review ([LTT](https://www.youtube.com/watch?v=3PGKMwgjla0)) the 3D
question is met with "I'm as much of a 3D guy as I think anyone is these
days, but there's so little content available for it" (~21:10), and the
only comfortable 3D-movie path offered is a third-party VR app, in a
headset, rather than the 3D TV or projector the buyer already owns.

The through-line: the signal was standardised (H.264 Amendment 1),
adopted for broadcast, built into every 3D TV, and then abandoned by the
software layer that stopped writing it into files. The hardware never
stopped being able to read it. That is the wider right-to-repair point in
one domain, the sets, the discs and the standards outlived the vendors'
and toolmakers' willingness to keep the pipe honest: the capability is
owned by the buyer and stranded above it. The fix is not new hardware. It
is one 16-byte message, and this repo maps every place it needs to go.

## Sources

- H.264/AVC Amendment 1 (2009): frame packing arrangement SEI, and the
  Stereo/Multiview overview, [Vetro/Wiegand/Sullivan, "Overview of the
  Stereo and Multiview Video Coding Extensions of H.264/MPEG-4 AVC"](https://www.researchgate.net/publication/224216112_Overview_of_the_Stereo_and_Multiview_Video_Coding_Extensions_of_the_H264MPEG-4_AVC_Standard).
- DVB frame-compatible 3DTV: [ETSI TS 101 547-2 V1.2.1 (2012-11), clauses 6.4.1 and 6.5](https://www.etsi.org/deliver/etsi_ts/101500_101599/10154702/01.02.01_60/ts_10154702v010201p.pdf); HEVC variant [DVB A154-4 (2015)](https://dvb.org/wp-content/uploads/2019/12/a154-4_dvb-3dtv_hevc.pdf). The SEI itself: ITU-T H.264 Annex D (payload type 45).
- BD3D2MK3D support thread, videohelp #395498, via Internet Archive
  snapshots of pages 1-20 (2023-2026 captures).
- DLNA-server symptom threads: Plex, Jellyfin, Serviio, MakeMKV, AVS
  (linked inline above).
- Linus Tech Tips / ShortCircuit videos cited above (timestamped jump-links):
  - *My Most Unnecessary Home Project in YEARS - Home 3D Movie Projector Setup!* (2024-11-23),
    [full video](https://www.youtube.com/watch?v=_4Sz6J49jho). Timed moments:
    [0:26 "still being released on 3D Blu-ray every single year"](https://www.youtube.com/watch?v=_4Sz6J49jho&t=26s) ·
    [0:53 "no new hardware supports 3D anymore"](https://www.youtube.com/watch?v=_4Sz6J49jho&t=53s) ·
    [10:20 "more tinkering than anything else we've done so far"](https://www.youtube.com/watch?v=_4Sz6J49jho&t=620s) ·
    [10:34 ripping and hand-remuxing to a 3D file format](https://www.youtube.com/watch?v=_4Sz6J49jho&t=634s).
  - *Steam Frame Review - This Changes Everything*,
    [full video](https://www.youtube.com/watch?v=3PGKMwgjla0). Timed moment:
    [21:10 "so little content available for it"](https://www.youtube.com/watch?v=3PGKMwgjla0&t=1270s).
    Companion LTT forum thread (each LTT video links one in its description):
    [The Steam Frame Changes Everything - Full Review, topic 1642726](https://linustechtips.com/topic/1642726-the-steam-frame-changes-everything-full-review/).
  - *Our first 30 mins with the Steam Frame*,
    [full video](https://www.youtube.com/watch?v=u8R-bnz1MPU) — first-look context (note: LTT pulled and re-uploaded this; verify the canonical URL before citing publicly). Companion thread [topic 1626620](https://linustechtips.com/topic/1626620-valve-blew-away-my-expectations-steam-frame-first-look/) (owner-confirmed), but the video has no substantive 3D discussion, so it is not a comment target.

Cross-comment plan: each LTT video's description links its own forum
thread. The project comment on the older *3D Movie Projector Setup*
thread is already posted; the next, chronologically, was the Steam Frame
review thread (1642726 above), cross-referencing the projector one so the
two build a timeline. Posted 2026-09-18:
https://linustechtips.com/topic/1642726-the-steam-frame-changes-everything-full-review/#findComment-16936512
- This project: `docs/3d-signalling-explainer.md`,
  `docs/3d-blocked-in-browser.md`, `tools/serviio/`.
