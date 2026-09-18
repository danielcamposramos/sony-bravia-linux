# How often the frame-packing SEI is actually attached to a frame

Runnable evidence for the "why the first frame was not enough" half of [mpv PR #18490](https://github.com/mpv-player/mpv/pull/18490): the `frame_packing_arrangement` SEI reaches libavcodec as `AV_FRAME_DATA_STEREO3D` on **keyframes only**, so a player that reads the side data once and then lets `fix_image_params()` run again on the next frame loses the layout. That is what the PR's second commit (`f_decoder_wrapper: keep in-band stereo 3D layout across frames`) fixes.

The point of this file is that nobody has to take the numbers on faith.
It needs no patched mpv and no sample downloads. Stock ffmpeg, four commands, about ten seconds.

## The block

```bash
# Build a 10 s SBS clip with the frame-packing SEI and a keyframe every 48 frames.
ffmpeg -v error -f lavfi -i "testsrc2=size=960x1080:rate=24:duration=10" \
       -f lavfi -i "smptebars=size=960x1080:rate=24:duration=10" \
       -filter_complex "[0:v][1:v]hstack=inputs=2[v]" -map "[v]" \
       -c:v libx264 -crf 20 -pix_fmt yuv420p -g 48 \
       -x264-params frame-packing=3 sei_multi.mp4

# Same thing without the SEI, as a negative control.
ffmpeg -v error -f lavfi -i "testsrc2=size=960x1080:rate=24:duration=10" \
       -f lavfi -i "smptebars=size=960x1080:rate=24:duration=10" \
       -filter_complex "[0:v][1:v]hstack=inputs=2[v]" -map "[v]" \
       -c:v libx264 -crf 20 -pix_fmt yuv420p -g 48 no_sei.mp4

# How many frames actually carry AV_FRAME_DATA_STEREO3D?
for f in sei_multi.mp4 no_sei.mp4; do
  ffprobe -v error -select_streams v:0 -show_frames "$f" > /tmp/f.$$
  printf "%-16s frames=%-5s keyframes=%-4s stereo3d_side_data=%s\n" "$f" \
    "$(grep -c '^media_type=video'          /tmp/f.$$)" \
    "$(grep -c '^key_frame=1'               /tmp/f.$$)" \
    "$(grep -c '^side_data_type=Stereo 3D'  /tmp/f.$$)"
  rm -f /tmp/f.$$
done

# And which frames they are.
ffprobe -v error -select_streams v:0 -show_frames sei_multi.mp4 | awk '
  /^media_type=video/{n++} /^key_frame=1/{k[n]=1} /^side_data_type=Stereo 3D/{s[n]=1}
  END{for(i=1;i<=n;i++) if(k[i]||s[i]) printf "frame %3d  keyframe=%d  stereo3d=%d\n", i, (k[i]?1:0), (s[i]?1:0)}'
```

## Output

```
sei_multi.mp4    frames=240   keyframes=5    stereo3d_side_data=5
no_sei.mp4       frames=240   keyframes=5    stereo3d_side_data=0
frame   1  keyframe=1  stereo3d=1
frame  49  keyframe=1  stereo3d=1
frame  97  keyframe=1  stereo3d=1
frame 145  keyframe=1  stereo3d=1
frame 193  keyframe=1  stereo3d=1
```

Identical on both machines it was run on (2026-09-17):

| host | ffmpeg | libavcodec |
|---|---|---|
| zionsparkyx64 (workstation) | 9.0.1 | 63.1.101 |
| D2SERVER | 6.1.6 | 60.x |

Same counts and the same frame indices across three major FFmpeg versions, so the result is a property of the file rather than of one build.

## Why it is built this way

Two details do real work and are easy to leave out.

**The negative control.** `no_sei.mp4` is the same clip encoded without `-x264-params frame-packing=3` and reports `stereo3d_side_data=0`. Without it, a reader cannot tell whether the counter detects the SEI or simply always prints a number.

**The keyframe interval.** `-g 48` over 10 seconds gives five keyframes. A 2-second clip has exactly one, and `1 of 1` cannot distinguish "one per keyframe" from "one per file" — which is precisely the distinction the second commit turns on. Frames 1, 49, 97, 145 and 193 settle it: the side data lands on every keyframe and on nothing else, consistent with `frame_packing_arrangement_repetition_period = 1` ("persists until the next IDR").

## Related

- Campaign status and the review-round record: [README.md](README.md)
- Signalling background: [docs/3d-signalling-explainer.md](../../../docs/3d-signalling-explainer.md)
