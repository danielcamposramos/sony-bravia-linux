# DRAFT — MKVToolNix feature request (ready to reword and file)
**Tracker:** https://codeberg.org/mbunkus/mkvtoolnix/issues
**Account:** https://join.codeberg.org/ — email + username signup
(Codeberg is a non-profit Forgejo instance; there is no GitHub login,
just email confirmation)
**Doctrine — read before filing:** mbunkus has stated publicly
(tracker meta-issue #6278) that he will "outright close & ignore
overly verbose & meandering issue requests", and that AI assistance
is acceptable only when the submitter demonstrably understands every
claim. So: keep it short, state which source files you checked, own
every sentence after rewording. No AI disclaimer — just write it as
yourself.
**Verified against:** a checkout of mkvtoolnix dev (configure.ac
v102.0) on 2026-09-15; local mkvmerge v101 behaves the same.

---

**Title:** mkvmerge: derive the video track's stereo mode from the bitstream frame-packing SEI when --stereo-mode is not given

mkvmerge currently sets the stereo mode from exactly two sources: the `--stereo-mode` command line option, and, for Matroska inputs, an existing `KaxVideoStereoMode` in the source file (`src/input/r_matroska.cpp`). The AVC parser in `src/common/avc/es_parser.cpp` reads SEI NALs structurally but only interprets payload type 6 (recovery point) — everything else, including `frame_packing_arrangement` (payload 45), is skipped.

**Request:** when `--stereo-mode` is not given, read the frame-packing SEI from the first keyframe of AVC (and HEVC) video and derive the track's stereo mode from it (frame_packing_type 3 → side-by-side, 4 → top-and-bottom). If the source carries both a container tag and a SEI and they disagree, keep the tag and print a warning.

**Why it matters:** an SEI-bearing raw H.264/H.265 elementary stream or MP4 currently muxes with no stereo mode at all. Hardware 3D players read the SEI from the stream, software players read the Matroska tag — mkvmerge already derives other track properties from bitstream parsing, so this is the same idea for stereo. Background on the two-signal situation (live-tested on hardware): https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md

I realize the AVC parser currently skips the payload, so this is a real feature and not a one-liner — happy to help test against SEI-reading hardware if it's of interest.