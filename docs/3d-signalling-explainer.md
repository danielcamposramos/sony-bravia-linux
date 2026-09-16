# 3D-signalling in MKV/H.264: why disc rips play flat on hardware — and the exact fix

> **Audience:** developers of rippers, converters, muxers and encoder
> front-ends. This is the tool-agnostic companion to
> [serviio-3d-explainer.md](serviio-3d-explainer.md) (same findings,
> written for the media-server side). Everything here is
> live-hardware-proven on two TV generations (KDL-46EX725/2011,
> KDL-46HX855/2012), single-variable tests, 2026-09-13.

## TL;DR for pipeline authors

1. Hardware players that auto-engage 3D read the **H.264
   `frame_packing_arrangement` SEI** (payload type 45) — *standard,
   in-stream signalling*, not a vendor mechanism.
2. Your output almost certainly does not carry it. In a real-world
   44-title 3D MKV library (web rips + disc conversions), **43/44
   files carry the Matroska `StereoMode` tag, 0/44 carry the SEI.**
   Every one of them plays flat on hardware that would otherwise
   auto-flip.
3. The fix at the source is tiny:
   - **encode path:** pass the stereo layout to the encoder —
     x264 `--frame-packing 3|4` (SBS|TAB) — ffmpeg's libx264 wrapper
     has auto-injected it from Matroska stereo side data since 2013;
   - **video-copy/remux path:** inject the SEI losslessly into the
     existing stream (16 bytes before every IDR, ~0.002% growth,
     no re-encode — reference implementation below);
   - either way, **write the Matroska `StereoMode` tag** on output
     so software players and the injection tools have a container
     source of truth.

**Campaign status:** the first source-producer fix has landed —
HandBrake merged PR
[#8100](https://github.com/HandBrake/HandBrake/pull/8100)
(2026-09-16), which maps the detected stereo layout to x264's
`i_frame_packing` on encode. HandBrake 1.12.0 is therefore the first
mainstream ripper whose 3D output carries **both** signals.

## The two signals

| Signal | Where | Who reads it |
|---|---|---|
| Matroska `StereoMode` (e.g. 1 = side-by-side-left, 2 = top-bottom…) | container track element | software players (StereoScopic/MPC/ffmpeg/Kodi…), our injector |
| H.264 `frame_packing_arrangement` SEI (payload 45; `frame_packing_type` 3 = side-by-side, 4 = top-and-bottom) | elementary stream, before each IDR | **hardware** DLNA/USB players that auto-engage 3D (proven: two generations of Sony BRAVIA; standard signalling other era 3D sets likely read — untested on them) |

Rips typically have the first, never the second. Remuxing MKV → TS
(for DLNA delivery) drops the container tag by design, so the SEI is
the only thing that survives the chain that ends at hardware.

**This is not a Sony quirk.** Frame-compatible stereoscopic delivery
(half-SBS / half-TAB inside a normal 2D frame) was standardized for
DVB 3D broadcast with the H.264 `frame_packing_arrangement` SEI as
*the* in-stream signaller (ETSI frame-compatible stereo; DVB
tooling exposes e.g. an AVC descriptor
`frame_packing_SEI_not_present_flag`). Every era 3D TV shipped that
broadcast decoder stack — file/USB/DLNA playback runs on the same
silicon. We proved the SEI read on two Sony generations; we cannot
test other brands' sets, but they implemented the same standard for
broadcast, so rips missing the SEI very plausibly play flat on them
too. Community testing wanted — with our injector
(`tools/bravia_sei3d.py`) any owner can produce the single-variable
A/B pair in minutes.

## The proof (single-variable)

Byte-identical SBS clips, the only difference a 16-byte x264-verbatim
frame-packing SEI NAL before every IDR:

- with SEI → TV announces "Foi detectado um sinal 3D" and engages,
  no remote press;
- without SEI → same frames play flat.

Proven on both the 2011 entry line (AZ2 silicon) and the 2012 high-end
line (AZ3), across three codec families on the encode path (MPEG4-ASP
AVI, VC-1/WMV, full-SBS MPEG4 MOV) and on the lossless remux path.

## Reference implementation (MIT-adjacent, use freely)

`tools/bravia_sei3d.py` in this repo: lossless SEI injector for
existing files — mkvextract → insert NAL before every IDR → mkvmerge
(restore `StereoMode`) → verify (SEI + stream counts + duration) →
replace in place. Idempotent (skips files already carrying the SEI);
batch/recursive; layout detection cascade (tag → filename tokens →
2× geometry). `tools/ffmpeg-3d-wrapper.sh` shows the encode-path
variant (appends `-x264-params frame-packing=3|4` when any input is
3D-flagged).

## What we are asking pipeline authors for

Not "add 3D support" — the decoding/authoring side is not your
problem. The ask is only: **when the layout is known, don't throw the
signalling away**:

1. If you re-encode SBS/TAB video with libx264/libx265 and know the
   layout (from source MVC/SSIF, container tag, or a user checkbox),
   pass it to the encoder so the SEI lands in the stream.
2. If you copy the video stream, either inject the SEI yourself or
   warn loudly when a 3D-flagged file leaves your pipeline without
   in-stream signalling.
3. Always write the Matroska `StereoMode` tag on output (mkvmerge
   `--stereo-mode`, or copy it from the source).

With those three habits, rips would auto-play 3D on hardware the day
they are made — instead of every downstream owner rediscovering why
their TV shows two pictures side by side.

## Prior art (and why we believe this diagnosis is new)

To our knowledge, the mechanism below — era hardware reads the SEI,
rips carry only the container tag, hence flat playback — has not
been published as a diagnosis with a fix before. The community's
standing answer to "why doesn't my TV auto-engage 3D on my MKV?" was
always *manual*: press the 3D button and pick SBS/TAB (still the
correct fallback for un-fixable files). Search today for the symptom
surfaces only manual-mode guidance and per-brand forum threads, no
root-cause writeup. Ecosystem pieces existed scattered — x264 grew
`--frame-packing`, ffmpeg ≥ 9 auto-injects on encode — but nothing
connected them to the hardware behavior, and no public tool
addressed the remux path. We publish the full chain: live hardware
proof (single-variable, two TV generations), the lossless remux-path
injector, the encode-path wrapper, and this ask to the source
producers. If prior art exists, we'd genuinely like the pointer —
but we could not find it.

## The evidence base

Full test log, sink matrices (live `GetProtocolInfo` captures), and
the media-server-side story: [serviio-3d-explainer.md](serviio-3d-explainer.md).
Repo: https://github.com/danielcamposramos/sony-bravia-linux