# DRAFT — MKVToolNix feature request
**Where:** https://codeberg.org/mbunkus/mkvtoolnix/issues
**HARD NOTE:** maintainer mbunkus "will outright close & ignore
overly verbose & meandering issue requests" (his words, issue #6278).
Keep this SHORT and state which files were checked. This draft is
already at the upper length bound — trim further if possible.

---

**Title:** mkvmerge: derive the stereo mode from the bitstream
frame-packing SEI when --stereo-mode isn't given

mkvmerge sets the stereo mode from exactly two sources today: the
command line and, on MKV input, an existing container tag
(`src/input/r_matroska.cpp`, `set_video_stereo_mode`). The AVC parser
in `src/common/avc/es_parser.cpp` structurally reads SEI NALs but
only interprets payload type 6 and skips the rest — including
`frame_packing_arrangement` (payload 45), which is the standard
in-stream stereoscopic signaller.

**Request:** when `--stereo-mode` is not given, parse the FPA SEI on
the first keyframe and derive the track's stereo mode from it
(3 = side-by-side, 4 = top-and-bottom), so that e.g. a raw H.264 or
MP4 input carrying the SEI muxes with a correct tag. When both a
container tag and the SEI exist and disagree, keep the tag and print
a warning.

**Why:** hardware 3D players read the SEI, software players read the
Matroska tag; files that carry only one of the two play "wrong" for
the other class. Deriving the tag from the bitstream is parity with
what mkvmerge already derives from parsing (aspect ratio, fps). We
verified the current behavior against the source (r_matroska.cpp,
generic_packetizer.cpp, src/common/avc/) and the tracker has no prior
request for it.

Background (hardware behavior, live-tested):
https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md