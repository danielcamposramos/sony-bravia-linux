# DRAFT — StaxRip issue comment
**Where:** comment on the open issue
https://github.com/staxrip/staxrip/issues/1873 (noblemd00's mk3d
re-encode question; maintainer Dendraspis couldn't help — this draft
answers the user *and* anchors the feature ask)

**POSTED 2026-09-15:**
https://github.com/staxrip/staxrip/issues/1873#issuecomment-5685902578

---

*AI-assistance disclaimer: this comment was written with the assistance of an AI coding agent (Claude Code CLI, running the GLM 5.3 model), under the direction — and with the live on-hardware verification — of the owner of the TVs involved.*

Answering the question in this issue, then a feature request.

**Workaround today (x264 encodes):** the 3D info can be kept, but
StaxRip needs to be told twice, by hand:

1. **Video panel → x264 options → "Frame Packing"**: set it to
   *Side By Side* (or *Top Bottom*). This emits `--frame-packing 3|4`,
   which makes x264 write the `frame_packing_arrangement` SEI into
   the elementary stream — the GUI option already exists
   (`x264Enc.vb`), it's just never set by default and nothing
   auto-detects the source.
2. **Muxer → additional general switches**: add `--stereo-mode 0:1`
   (side-by-side left) or `--stereo-mode 0:3` (top-bottom), so
   mkvmerge writes the Matroska `StereoMode` tag. There is no GUI
   field for it today.

Why both: software players (MPC, Kodi, ffmpeg…) read the **container
tag**; hardware players that *auto-engage* 3D — era 3D TVs; we proved
it live on 2011/2012 BRAVIA sets — read **only the in-stream SEI** and
ignore the tag. Miss either one and some class of player shows you a
flat or double picture. Background with the hardware proof:
https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md

Note the x265/NVEnc paths can't do step 1: x265 has no frame-packing
option at all (the SEI payload type is defined in its headers but
there's no param/writer — filed upstream separately).

**Feature request** (this is the general fix, and would have prevented
this issue): StaxRip already reads the source with MediaInfo /
mkvmerge — when the source's stereo mode is known (Matroska
`StereoMode`, or the mk3d extension), it could:

- auto-set the x264 "Frame Packing" option (SBS→3, TAB→4),
- auto-add `--stereo-mode` to the mkvmerge command,
- and warn loudly when a stereo-flagged source is about to be
  flattened (neither signal written).

All three are small touches on data the tool already has in hand at
encode time. That would make re-encoded 3D files auto-play 3D on
hardware, instead of every user rediscovering this issue.