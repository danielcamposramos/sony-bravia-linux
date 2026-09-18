# Telling full SBS/TAB from half, without asking the user

In [mpv #17632](https://github.com/mpv-player/mpv/issues/17632) the OSD is
misplaced on 3D content, and the maintainer (kasper93) named the blocker
directly on 2026-03-25:

> "I tried to figure out how add compensation for OSD position/size/aspect
> ratio. But I don't know how to detect if it's half sbs or full sbs."

It is detectable, and not from the thing people reach for first.

## Measured, 2026-09-17

Four clips, each encoded with the H.264 `frame_packing_arrangement` SEI
(`-x264-params frame-packing=3` for side-by-side, `=4` for top-and-bottom):

| file | coded size | SAR | DAR | SEI present | per-eye DAR | verdict |
|---|---|---|---|---|---|---|
| `full_sbs.mp4` | 3840x1080 | 1:1 | 32:9 | yes | 1.778 | FULL |
| `half_sbs.mp4` | 1920x1080 | 1:1 | 16:9 | yes | 0.889 | HALF |
| `full_tab.mp4` | 1920x2160 | 1:1 | 8:9  | yes | 1.778 | FULL |
| `half_tab.mp4` | 1920x1080 | 1:1 | 16:9 | yes | 3.556 | HALF |

**All four carry the same side data.** The SEI says *which arrangement*
(side-by-side, top-and-bottom). It does not say full or half, and no
amount of reading it harder will make it.

## The rule

Split the frame the way the arrangement says, then ask whether one eye
came out at the display aspect the content was authored for:

```
SBS:  per_eye_dar = (width / 2) * SAR / height
TAB:  per_eye_dar =  width      * SAR / (height / 2)

per_eye_dar ~= container DAR   ->  FULL   (each eye is a whole frame)
per_eye_dar != container DAR   ->  HALF   (each eye is squeezed)
```

For 16:9 content that is `1.778 -> full`, and `0.889` (half SBS) or
`3.556` (half TAB) for the squeezed cases. The numbers above are that
arithmetic, measured rather than predicted.

The two signals are complementary, which is the point:

- the **SEI / `st3d` / Matroska `StereoMode`** gives the arrangement, and
  is what [PR #18490](https://github.com/mpv-player/mpv/pull/18490) makes
  mpv read from the stream;
- the **frame geometry** gives full vs half, and mpv already has it.

Neither alone is enough. Together they are sufficient, with nothing asked
of the user.

## Reproduce

```bash
mk() { # $1=out $2=eyeW $3=eyeH $4=stack $5=fp
  ffmpeg -v error -y -f lavfi -i "testsrc2=size=$2x$3:rate=24:duration=2" \
         -f lavfi -i "smptebars=size=$2x$3:rate=24:duration=2" \
         -filter_complex "[0:v][1:v]$4=inputs=2[v]" -map "[v]" \
         -c:v libx264 -crf 24 -pix_fmt yuv420p -x264-params frame-packing=$5 "$1"
}
mk full_sbs.mp4 1920 1080 hstack 3
mk half_sbs.mp4  960 1080 hstack 3
mk full_tab.mp4 1920 1080 vstack 4
mk half_tab.mp4 1920  540 vstack 4

for f in full_sbs half_sbs full_tab half_tab; do
  printf "%-9s " "$f"
  ffprobe -v error -select_streams v:0 \
    -show_entries stream=width,height,sample_aspect_ratio,display_aspect_ratio \
    -of csv=p=0 "$f.mp4"
done
```

Run on zionsparkyx64, ffmpeg 9.0.1, libavcodec 63.1.101.

## Caveat

This assumes the file is authored sanely: the container DAR describes how
one eye should end up on screen. Files that lie about their aspect exist,
and no metadata rule survives a file whose metadata is wrong. That is an
argument for reading the declared layout rather than guessing from the
filename, which is the same argument as #18490.

## Related

- [mpv-sei-frequency-repro.md](mpv-sei-frequency-repro.md)
- [mpv-3d-landscape.md](mpv-3d-landscape.md)
