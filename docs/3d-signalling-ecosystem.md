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
Internet Archive snapshots of pages 1-20 (partial: a first pass covered
about half the pages; the rest are pending). Source, per page, is the
archived thread. Categorised honestly, because the thread mixes displays,
disc players and projectors, and because BD3D2MK3D writes both the SEI and
the container tag, so a "works" report shows compatibility with a
correctly-authored 3D file, not which signal a given device read.

**3D televisions**
- LG passive 3D TVs (1080p) — prominent enough that BD3D2MK3D added a
  dedicated Half-TAB option to retain full 1080p on LG passive panels.
- Samsung active-shutter 3D TVs — including the tool author's own set,
  which he reports has "exactly the same problem" as the Sony sets this
  project documents.
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
- This project: `docs/3d-signalling-explainer.md`,
  `docs/3d-blocked-in-browser.md`, `tools/serviio/`.
