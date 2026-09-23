# ffmpeg EEXIST bug — FACT LIST for the owner's report (bug + repro ready)

> Raw facts only — per campaign doctrine, the owner writes and posts
> the actual report on code.ffmpeg.org in his own voice. Everything
> below is verified (workstation ffmpeg 9.0.1 + d2server 6.1.6,
> 2026-09-16). The 424 KB reproducer file is at
> `/tmp/acig-/ffmpeg-eexist-repro/tag-only.sei3d.mkv` — attachable
> directly to the Forgejo issue.

## Suggested title (rewrite freely)

`ffmpeg CLI aborts with error -17 (EEXIST) when an input carries both a Matroska StereoMode tag and a frame_packing_arrangement SEI`

## One-paragraph version

When an H.264 MKV carries BOTH 3D signals — the Matroska `StereoMode`
container tag AND an in-stream `frame_packing_arrangement` SEI
(payload type 45) — the ffmpeg CLI aborts every decode/encode with
`Task finished with error code -17 (File exists)`. Each signal alone
is fine; only the combination fails. This state is not exotic: it is
the *correct* end state for stereoscopic MKVs (hardware 3D players
read only the SEI, software players read the tag) and is what
lossless SEI injectors produce.

## Verified facts

**Versions.**
- Affected: ffmpeg **9.0.1** (Debian) — reproduced; all three cited
  code sites **identical on master** (checked 2026-09-15), so master
  is presumably affected too.
- NOT affected: **6.1.6** — verified live: all three repro states
  decode rc=0 (d2server, 2026-09-16). The breakage is in the newer
  threaded-filtergraph fftools side-data path.

**Exact error** (decode and encode alike):

```
[vf#0:0] Task finished with error code -17 (File exists)
[vost#0:0] Could not open encoder before EOF
[out#0/null] Nothing was written into output file...
```

**Reproduction matrix** (same 2-second 640×360 testsrc2 clip, three
states; commands below):

| Input state | `ffmpeg -i f -f null -` | real encode |
|---|---|---|
| tag only (stereo_mode=1, no SEI) | rc=0 | rc=0 |
| SEI only (no tag) | rc=0 | rc=0 |
| **tag + SEI** | **rc=239, -17 EEXIST** | **rc=239, 0-byte output** |

**Side-data duplication** (the mechanism, visible in ffprobe):
on frames whose access unit carries the SEI (keyframes in practice)
`ffprobe -show_entries frame_side_data` lists **`Stereo 3D` twice** —
one entry mapped from the container tag (decoder
`ff_decode_frame_props` via the `coded_side_data` map) plus one added
by the SEI handler. Later frames list it once.

**Root cause chain** (three code sites, all verified identical in
release/9.0 and master):
1. `libavcodec/h2645_sei.c:532` — the FPA SEI handler calls
   `av_stereo3d_create_side_data(frame)` **unconditionally**, no
   check whether the frame already carries `AV_FRAME_DATA_STEREO3D`
   from the container tag.
2. `fftools/ffmpeg_filter.c` — `ifilter_parameters_from_frame()`
   clones each global side data with **`flags = 0`** (9.0 line 2263,
   master line 2367); note the buffersink path at 2175/2279 correctly
   uses `AV_FRAME_SIDE_DATA_FLAG_REPLACE`.
3. `libavutil/side_data.c:273` — `av_frame_side_data_clone` without
   REPLACE returns `AVERROR(EEXIST)`, and the filtergraph thread
   treats it as fatal instead of merging.

**Suggested fixes** (any one of; offer, don't demand):
- dedupe in `h2645_sei.c` (check `av_frame_get_side_data` before
  creating), or
- pass `AV_FRAME_SIDE_DATA_FLAG_REPLACE` in
  `ifilter_parameters_from_frame`, or
- make the CLI merge instead of abort.
Owner can offer to work on a patch once a direction is indicated.

**Prior art check.** Tracker searches (2026-09-15) for
`packing arrangement` and `"File exists"` → zero results. Unreported.

**Why it matters / affected consumers.** Any ffmpeg-CLI-based
consumer of SEI-injected files, including media servers that shell
out to ffmpeg (e.g. Serviio) and the whole class of lossless 3D
repair tools. The both-signals state is the recommended end state
for 3D MKVs.

**Background link** (audience-neutral, live-hardware-proven):
https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md

## Reproducer — how the sample was made (also the regeneration recipe)

```
ffmpeg -f lavfi -i "testsrc2=s=640x360:d=2:r=24" -c:v libx264 -preset ultrafast -pix_fmt yuv420p base.h264
mkvmerge -o tag-only.mkv --stereo-mode 0:1 base.h264          # tag-only state
python3 bravia_sei3d.py --mode sbs tag-only.mkv                 # -> tag-only.sei3d.mkv (tag+SEI)
mkvextract tag-only.sei3d.mkv tracks 0:sei-only.h264 && mkvmerge -o sei-only.mkv sei-only.h264   # SEI-only state
```

(`bravia_sei3d.py` is the repo's lossless injector; it adds a 16-byte
payload-45 SEI NAL before each keyframe and keeps the tag. The same
bug reproduces with real movie files — 44-title-library samples —
not just the synthetic clip.)

---

# APPENDIX — second report for the same tracker (feature request, file after the bug)

Same account, separate issue. **Facts only:**

- **Ask:** a `frame_packing` option on the `h264_metadata` (and
  `hevc_metadata`) bsf — insert/remove/extract semantics like the
  existing `display_orientation` — so a lossless one-liner works:
  `ffmpeg -i in.mkv -map 0 -c copy -bsf:v h264_metadata=frame_packing=3 out.mkv`
  (3=SBS, 4=TAB).
- **Why small, not new plumbing:** cbs_sei already has full
  read/write support for the FPA SEI message — commit `826f55d5`
  (2024-06-26), `cbs_sei_syntax_template.c` — and `h264_metadata`
  already inserts SEI via that machinery (display orientation).
  Verified: no bsf in the tree writes payload 45 today
  (`h264_metadata` offers only `sei_user_data`, payload type 5).
- **Use case:** tag-only 3D libraries are the common real-world state
  (43/44 titles in ours); this turns whole-library lossless repair
  into one command with no re-encode (~0.002% size growth).
- **Optional secondary bullet:** wire `AV_FRAME_DATA_STEREO3D` input
  into `libx265.c` via x265's generic user-SEI payload API —
  `libx264.c` has done the equivalent since 2013 (`09cb75cd`).
- Keep `mkvmerge`'s separate Codeberg ask out of this report.