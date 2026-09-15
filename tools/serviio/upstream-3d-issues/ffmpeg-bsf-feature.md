# DRAFT — FFmpeg enhancement request
**Where:** https://code.ffmpeg.org/FFmpeg/FFmpeg/issues (enhancement;
the GitHub mirror has issues disabled)

---

**Title:** h264_metadata/hevc_metadata bsf: option to insert (and
remove/extract) the frame_packing_arrangement SEI

**Use case.** Hardware players that auto-engage 3D read the
`frame_packing_arrangement` SEI (payload type 45) from the elementary
stream and ignore the Matroska `StereoMode` container tag — we proved
this live on era 3D TV sets, and the mechanism is the DVB-standard
in-stream signaller for frame-compatible stereo (background:
https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md).
A very common real-world state is a 3D MKV that carries *only* the
container tag — 43 of 44 titles in our library. Today, fixing such a
file losslessly through ffmpeg is impossible: no bitstream filter can
write SEI type 45 (`h264_metadata` offers only `sei_user_data`, the
unregistered-UUID payload 5, which SEI-reading hardware ignores for
3D detection).

**The ask.** Add a `frame_packing` option to the `h264_metadata` (and
`hevc_metadata`) bsf, with the same insert/remove/extract semantics
as the existing `display_orientation` handling:

```
ffmpeg -i in.mkv -map 0 -c copy -bsf:v h264_metadata=frame_packing=3 out.mkv
```

(type 3 = side-by-side, 4 = top-bottom; `remove`/`extract` modes for
the inverse.)

**Why this is a small change, not new plumbing:** full read/write
support for the FPA SEI message already landed in cbs_sei
(commit 826f55d5, `cbs_sei_syntax_template.c` — the
`frame_packing_arrangement` function has complete bidirectional
ue/flag/u macros), and `h264_metadata` already inserts SEI via that
machinery for display orientation. The option is the missing piece.

**Impact.** This single option turns library-wide lossless repair into
a one-liner for any user or media-server, with no re-encode and
~0.002% size growth — the SEI is a 16-byte NAL before each keyframe.
(We built a standalone mkvextract-based injector to do this today;
having it in ffmpeg would make that tool unnecessary and would reach
every ffmpeg-based pipeline for free.)

**Secondary, related:** once the bsf exists, `libx265.c` could also
map `AV_FRAME_DATA_STEREO3D` input to an FPA SEI via x265's generic
user-SEI payload API — `libx264.c` has done the equivalent since 2013
(09cb75cd), while `libx265.c` currently drops the side data entirely.