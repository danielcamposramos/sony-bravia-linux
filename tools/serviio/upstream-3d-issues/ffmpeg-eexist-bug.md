# DRAFT — FFmpeg bug report
**Tracker:** https://code.ffmpeg.org/FFmpeg/FFmpeg/issues (Forgejo; the
GitHub mirror has issues disabled)
**Type:** bug — decode/encode aborts on files carrying both Matroska
StereoMode tag and frame_packing_arrangement SEI
**Priority: post first.** Real, reproduced, unreported; tracker search
for "packing arrangement" and "File exists" returns zero prior reports.

**Operational note for our own stack:** d2server runs ffmpeg 6.1.6,
which is NOT affected (verified live: both SEI-carrying library files
decode clean). But if the host ffmpeg is ever distro-upgraded to
7+/9+, Serviio's transcode lane would abort on every SEI-injected
file with this bug — another reason to watch the upstream fix and to
pin/verify ffmpeg version on upgrade.

---

**Title:** ffmpeg CLI aborts with error -17 (EEXIST) on MKV files that
carry both a Matroska StereoMode tag and an in-stream
frame_packing_arrangement SEI

**Version:** reproduced on 9.0.1 (Debian, Lavc63.1.101); the three
relevant code sites are unchanged on master. ffmpeg 6.1.6 is NOT
affected (older fftools side-data path) — verified on our own 6.1.6
install.

## Summary

An H.264 MKV that carries **both** 3D signals — the Matroska
`StereoMode` track element *and* an in-band `frame_packing_arrangement`
SEI (payload type 45) — makes the ffmpeg CLI abort any decode or
encode:

```
[vf#0:0] Task finished with error code -17 (File exists)
Could not open encoder before EOF
Nothing was written
```

Neither signal alone breaks anything; only the combination does. This
matters because the combination is exactly the state toolchains are
converging on: the SEI is what hardware 3D players auto-detect, the
tag is what software players read, and lossless SEI injectors (e.g.
https://github.com/danielcamposramos/sony-bravia-linux —
`tools/bravia_sei3d.py`) intentionally produce both.

## Reproduction

Files tested (both real-world, ffmpeg-remuxed copies behave
identically; synthetic controls built with mkvmerge + a 16-byte FPA
SEI):

| Input state | `ffmpeg -i in.mkv -t 5 -f null -` |
|---|---|
| Matroska StereoMode tag only | rc=0 |
| FPA SEI only (no tag) | rc=0 |
| **tag + SEI** | **aborts, -17 EEXIST** |

`ffprobe -show_entries frame_side_data=side_data_type` on the
tag+SEI file lists **two** `Stereo 3D` entries on the first frame
(one from the container tag mapped via `ff_decode_frame_props`, one
added by the SEI handler); on the SEI-only control it lists one.

## Cause

1. `libavcodec/h2645_sei.c:532` calls
   `av_stereo3d_create_side_data(frame)` unconditionally when an FPA
   SEI is parsed — no check whether the frame already carries
   `AV_FRAME_DATA_STEREO3D` mapped from the stream's
   `coded_side_data` (libavcodec/decode.c side_data_map).
2. `fftools/ffmpeg_filter.c` `ifilter_parameters_from_frame()` then
   clones each global side data with `flags = 0` (9.0 line 2263;
   master line 2367) — while the buffersink path at 2175/2279
   correctly uses `AV_FRAME_SIDE_DATA_FLAG_REPLACE`.
3. `av_frame_side_data_clone` without REPLACE returns
   `AVERROR(EEXIST)` (`libavutil/side_data.c:273`), and the
   filtergraph thread treats it as fatal instead of merging.

## Suggested fix

Any of: dedupe in `h2645_sei.c` (check `av_frame_get_side_data`
before creating), pass `AV_FRAME_SIDE_DATA_FLAG_REPLACE` in
`ifilter_parameters_from_frame`, or make the CLI merge instead of
abort. Happy to work on a patch if the preferred direction is
indicated.

## Why we care

This aborts any ffmpeg-CLI-based consumer of SEI-injected files —
including media servers that shell out to ffmpeg for transcoding. The
"both signals" state is the *correct* end state for stereoscopic MKVs
(hardware reads the SEI, software reads the tag), so the CLI should
handle it, not die on it.

Background on the two-signal situation (audience-neutral write-up,
live-hardware-proven):
https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md