# DRAFT — x265 feature request
**Where:** https://github.com/Multicorewareinc/x265 (issues enabled;
bitbucket is the canonical repo but the GitHub org accepts issues)

**POSTED 2026-09-15:** https://github.com/Multicorewareinc/x265/issues/970

---

**Title:** Feature request: write the frame_packing_arrangement SEI
(x264 `--frame-packing` equivalent)

*AI-assistance disclaimer: this issue was written with the assistance of an AI coding agent (Claude Code CLI, running the GLM 5.3 model), under the direction — and with the live on-hardware verification — of the owner of the TVs involved.*

x265 defines the SEI payload type — `FRAME_PACKING = 45` in
`x265.h` — but there is no param, no CLI option, and no code path that
writes it: grepping `frame-packing`/`packing` across `x265cli.cpp`,
`param.cpp`, `encoder.cpp` finds nothing but the unused constant.
The result: **an HEVC encode of side-by-side / top-bottom 3D content
cannot carry in-stream stereoscopic signalling at all.**

Why that matters in practice: hardware players that *auto-engage* 3D
read the H.264/H.265 `frame_packing_arrangement` SEI from the
elementary stream and ignore the Matroska `StereoMode` container tag.
We proved this live on 2011/2012 Sony BRAVIA sets (single-variable
tests: byte-identical streams, only the 16-byte SEI differs; the TV
engages 3D only with it), and the signalling is the standard one DVB
defined for frame-compatible stereo broadcast, so era sets from other
brands very plausibly behave the same. Background:
https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md

Today this gap propagates downstream:

- **BD3D2MK3D** (the standard open 3D-BD ripper) warns its users that
  HEVC output cannot carry the 3D format info, and its author r0lZ
  has stated publicly: "h265 does not support the frame-packing
  property… Many hardware players support only the frame-packing and
  ignore the MKV stereo-mode."
- **ffmpeg's libx265 wrapper** has nothing to map its
  `AV_FRAME_DATA_STEREO3D` input into (libx264.c has done this since
  2013).

**The ask:** an `--frame-packing` CLI option + param like x264's
(`frame_packing_type`: 3 = side-by-side, 4 = top-bottom, 5 = frame
alternation), writing the SEI before each keyframe. x264's
implementation is a compact, well-understood reference
(`x264_sei_frame_packing_write` in `encoder/set.c`, emitted in
`encoder/encoder.c`). If the full param is too much, even exposing
the write through the existing generic user-SEI payload API with
documentation would let front-ends (BD3D2MK3D, ffmpeg's wrapper) wire
it up in one line each.

We can't contribute the encoder-side patch ourselves, but we can
supply reference byte streams (a verified, hardware-proven FPA SEI
NAL and the files it was extracted from) and test any build against
real SEI-reading hardware.