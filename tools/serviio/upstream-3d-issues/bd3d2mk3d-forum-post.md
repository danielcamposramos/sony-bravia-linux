# DRAFT — BD3D2MK3D forum post
**Where:** forum.videohelp.com thread 395498 (the official support
thread — r0lZ actively maintains there; no formal issue tracker
exists, GitHub user r0lZ has 0 public repos)
**Tone:** appreciation first, small asks, ally recruitment. r0lZ's
tool is the model citizen of this campaign — it already writes BOTH
signals by default on the x264 path and documents the hardware
behavior. The post should read as "your tool is the proof this
campaign is right", not as a bug report.

---

First: thank you for BD3D2MK3D — it is the one tool in the ecosystem
that gets 3D signalling right by default (frame-packing SEI in the
stream via x264 `--frame-packing`, stereo mode in the MKV header, and
the AVC3Dmodifier tool to fix existing files). I'm posting because we
spent the last weeks reverse-engineering *why* 3D rips play flat on
hardware, and BD3D2MK3D turns out to be the reference implementation
of the answer. Two small feature thoughts follow — and one thing we'd
like to share back.

**What we found (live hardware proof):** we reverse-engineered 3D
auto-detection on 2011–2012 Sony BRAVIA sets (own hardware, own LAN)
and proved by single-variable tests that they auto-engage 3D **only**
from the H.264 frame_packing_arrangement SEI — the Matroska stereo
mode tag is ignored by the hardware entirely. Same as your Doom9
statement: "many hardware players support only the frame-packing and
ignore the MKV stereo-mode." The signalling is the DVB-standard one
for frame-compatible stereo, so other era 3D brands very plausibly
read it too. In a real-world 44-title 3D library (web rips + disc
conversions), 43/44 carried only the MKV tag and 0/44 the SEI — all
flat on hardware. Full write-up, with a lossless SEI injector
(open-source, Linux/CLI — a cousin of your bundled h264Modify) here:
https://github.com/danielcamposramos/sony-bravia-linux

Two feature thoughts, both small:

1. **Custom-encoder path:** when the user supplies a custom encoder
   command (e.g. NVEncC) instead of x264/x265, the output today
   carries no frame-packing SEI and there's no warning — only the
   MKV tag survives, which the hardware ignores. Since the tool
   already bundles h264Modify/AVC3Dmodifier, could the custom path
   auto-run it on the output to inject the SEI (or at least pop the
   same loud warning the x265 path gets)?

2. **AVC3Dmodifier as CLI:** the "Modify 3D format tags in MKV or
   AVC" tool would be a great command-line entry point — it's
   exactly the operation ecosystem tools (media servers, library
   fixers) need to batch-repair tag-only files on other OSes. A
   Linux/CLI sibling would let non-Windows users fix whole libraries
   the way Windows users already can.

And the share-back: we couldn't find any published root-cause
writeup connecting "hardware reads SEI only" to "rips carry tag
only" — the community's standing answer to "why doesn't my TV
auto-engage 3D on my MKV?" has always been "press the 3D button
manually". You documented the mechanism in BD3D2MK3D's help years
ago; our contribution is the live-proven diagnosis, the remux-path
injector, and upstream asks to HandBrake/StaxRip/x265/ffmpeg/mkvmerge
so source producers stop emitting SEI-less files in the first place.
If you see anything we got wrong — you know this corner of the
ecosystem better than anyone — a correction on the thread would be
gold.