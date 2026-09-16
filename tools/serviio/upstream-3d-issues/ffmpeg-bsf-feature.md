# DRAFT — FFmpeg feature request (ready to reword and file)
**Tracker:** https://code.ffmpeg.org/FFmpeg/FFmpeg/issues (Forgejo)
**File as a SEPARATE issue** from bug #24530 — feature requests get
their own thread. Pick the enhancement/feature type if the form offers
one; if it shows the bug template ("Summary of the bug / Steps to
reproduce"), the structure below maps onto it directly — the
"reproduce" part is the command every user wants to run and the error
it gives today.
**Reproducer:** no attachment needed — every command below is
copy-pasteable and was verified on 9.0.1 (2026-09-16).
**Note:** per campaign doctrine — reword in your own voice, no
AI-assistance disclaimer, file after the bug report.

---

**Title:** h264_metadata (and hevc_metadata) bsf: option to insert the frame_packing_arrangement SEI

# Summary

No bitstream filter can write the H.264 `frame_packing_arrangement`
SEI (payload type 45) — the standard in-stream stereoscopic
signalling. That makes the single most useful lossless operation on a
3D MKV impossible: adding in-stream 3D signalling during a `-c copy`
remux, without re-encoding.

`h264_metadata`'s only SEI-insertion options are `sei_user_data`
(payload type 5, unregistered UUID — ignored by SEI-reading hardware
for 3D detection) and `display_orientation`. Nothing in the bsf list
writes payload 45.

# Steps to reproduce

The command a user wants to run, verified on ffmpeg 9.0.1:

```
$ ffmpeg -i in.mkv -map 0 -c copy -bsf:v h264_metadata=frame_packing=3 out.mkv
[h264_metadata_bsf @ ...] Option 'frame_packing' not found
[vost#0:0/copy @ ...] Error parsing bitstream filter sequence 'h264_metadata=frame_packing=3': Option not found
Error opening output files: Option not found
```

And the filter's option list (`ffmpeg -h bsf=h264_metadata`) confirms
there is no SEI payload-45 write anywhere:

```
  -sei_user_data     <string>     ...V....B.. Insert SEI user data (UUID+string)
  -display_orientation <int>      ...V....B.. Display orientation SEI (from 0 to 3) (default pass)
     pass            0            ...V....B..
     insert          1            ...V....B..
     remove          2            ...V....B..
     extract         3            ...V....B..
```

`display_orientation` is exactly the pattern this request asks to
replicate for stereoscopic signalling.

# The request

Add a `frame_packing` option to `h264_metadata` (and the
`hevc_metadata` sibling), with the same pass/insert/remove/extract
semantics as `display_orientation`, inserting the
`frame_packing_arrangement` SEI with `frame_packing_type` 3
(side-by-side) or 4 (top-and-bottom) before each keyframe:

```
ffmpeg -i in.mkv -map 0 -c copy -bsf:v h264_metadata=frame_packing=3 out.mkv
```

This is an option-add, not new plumbing: full read/write support for
the FPA SEI message already landed in cbs_sei (commit 826f55d5, 2024 —
`cbs_sei_syntax_template.c`), and `h264_metadata` already inserts SEI
through that machinery for display orientation.

# Use case

Real-world 3D MKV libraries overwhelmingly carry only the Matroska
`StereoMode` container tag — 43 of 44 titles in mine — while hardware
players that auto-engage 3D (era 3D TVs) read only the in-stream SEI
and ignore the tag. With this option, repairing an entire library
becomes one command per file: lossless copy, ~16 bytes per keyframe
(~0.002% growth), no re-encode. Background on the two-signal
situation (live-hardware-proven):
https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md

# Secondary suggestion (optional to include)

While at it, `libx265.c` could map incoming `AV_FRAME_DATA_STEREO3D`
side data to an FPA SEI via x265's generic user-SEI payload API
(payload type 45) — `libx264.c` has done the equivalent since 2013
(commit 09cb75cd). Today the wrapper drops the side data entirely, so
HEVC encodes never signal 3D even when the input is flagged.

I can supply reference streams (a verified, hardware-proven FPA SEI
NAL and the files it was extracted from) and test any implementation
against real SEI-reading hardware.