# DRAFT — FFmpeg bug report (ready to reword and file)
**Tracker:** https://code.ffmpeg.org/FFmpeg/FFmpeg/issues (Forgejo)
**Type:** defect
**Reproducer to attach:** `/tmp/acig-/ffmpeg-eexist-repro/tag-only.sei3d.mkv` (424 KB)
**Companion fact list:** `ffmpeg-eexist-facts.md`
**Note:** per campaign doctrine — reword in your own voice, no
AI-assistance disclaimer, file the bug first, bsf feature second.

---

**Title:** ffmpeg CLI aborts with error -17 (EEXIST) on inputs carrying both a Matroska StereoMode tag and a frame_packing_arrangement SEI

**Version:** reproduced on ffmpeg 9.0.1 (Debian, Lavc63.1.101); the three relevant code sites are unchanged on master. ffmpeg 6.1.6 is NOT affected (tested: the same inputs decode fine there) — the failure is in the newer fftools threaded-filtergraph side-data path.

## Summary

An H.264 MKV that carries **both** stereoscopic signals — the Matroska `StereoMode` track element *and* an in-band `frame_packing_arrangement` SEI (payload type 45) — makes the ffmpeg CLI abort every decode and encode:

```
[vf#0:0] Task finished with error code -17 (File exists)
[vost#0:0] Could not open encoder before EOF
[out#0/null] Nothing was written into output file, because at least one of its streams received no packets.
```

Neither signal alone breaks anything; only the combination does. The combination is not exotic — it is the recommended end state for stereoscopic MKVs (hardware 3D players auto-detect from the SEI, software players read the container tag), and it is what lossless SEI injectors produce when repairing tag-only files.

## How to reproduce

A minimal reproducer is attached (`tag-only.sei3d.mkv`: 2 s, 640×360, testsrc2, x264). It was built like this, in case the attachment is inconvenient:

```
ffmpeg -f lavfi -i "testsrc2=s=640x360:d=2:r=24" -c:v libx264 -preset ultrafast -pix_fmt yuv420p base.h264
mkvmerge -o tag-only.mkv --stereo-mode 0:1 base.h264     # tag only, no SEI
# add a 16-byte frame_packing_arrangement SEI (payload 45) before each keyframe, keep the tag:
python3 bravia_sei3d.py --mode sbs tag-only.mkv           # -> tag-only.sei3d.mkv
```

Three states, same stream, on 9.0.1:

| Input | `ffmpeg -i f -f null -` | real encode (`-c:v libx264 out.mp4`) |
|---|---|---|
| tag only (stereo_mode=1) | rc=0 | rc=0 |
| SEI only (no tag) | rc=0 | rc=0 |
| **tag + SEI (attached sample)** | **rc=239, `-17 File exists`** | **rc=239, 0-byte output** |

The failure reproduces identically on real movie files (a 44-title 3D library), so it is not specific to the synthetic clip.

The mechanism is visible in ffprobe: on frames whose access unit carries the SEI (keyframes in practice), the frame has **two** `Stereo 3D` side data entries — one mapped from the container tag, one added by the SEI handler:

```
$ ffprobe -v error -select_streams v:0 -show_entries frame_side_data=side_data_type -of csv f.mkv | head -1
frame,Stereo 3D,Stereo 3D,H.26[45] User Data Unregistered SEI message
```

## Analysis

1. `libavcodec/h2645_sei.c:532` — the FPA SEI handler calls `av_stereo3d_create_side_data(frame)` unconditionally, without checking whether the frame already carries `AV_FRAME_DATA_STEREO3D` mapped from the stream's `coded_side_data` (the container-tag path in `libavcodec/decode.c`).
2. `fftools/ffmpeg_filter.c`, `ifilter_parameters_from_frame()` — clones each global side data with `flags = 0` (9.0 line 2263, master line 2367). The buffersink path at 2175/2279 correctly uses `AV_FRAME_SIDE_DATA_FLAG_REPLACE`; this site does not.
3. `libavutil/side_data.c:273` — `av_frame_side_data_clone` without REPLACE returns `AVERROR(EEXIST)`, and the filtergraph thread treats that as fatal instead of merging.

## Suggested fix (any one of)

- dedupe in `h2645_sei.c`: check `av_frame_get_side_data` before creating a new entry (keep the container-derived value, or let the SEI win — either resolves the abort);
- pass `AV_FRAME_SIDE_DATA_FLAG_REPLACE` in `ifilter_parameters_from_frame`;
- make the CLI merge duplicate global side data instead of aborting.

Happy to work on a patch once a preferred direction is indicated.

## Why this matters

Any ffmpeg-CLI-based consumer of SEI-injected files is affected — media servers that shell out to ffmpeg for transcoding among them. Since the both-signals state is the correct end state for 3D MKVs, the CLI should handle it rather than die on it. I could not find a prior report on the tracker for this (searched "packing arrangement", "File exists").

Background on why files end up carrying both signals (live-hardware-proven write-up): https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md