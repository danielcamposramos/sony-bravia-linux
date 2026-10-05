# x265: `--frame-packing` (issue #970)

Material for the pull request that answers [Multicorewareinc/x265#970](https://github.com/Multicorewareinc/x265/issues/970): a dedicated `--frame-packing` option that writes the frame packing arrangement SEI (H.265 D.2.16), as x264 does for H.264.

- `0001-Add-frame-packing-option-to-emit-the-frame-packing-a.patch`: the change, on x265 master d97872539.
- `hevc-sbs-capture.png`: an HEVC clip encoded with `--frame-packing 3`, played on a Linux stereo desktop. The player reads the SEI and declares the video as stereo; the capture holds the two eyes side by side: LEFT in the left eye, RIGHT in the right eye, the same frame number in both.
- `hevc-tb-capture.png`: the same for a top-and-bottom clip encoded with `--frame-packing 4`.

The request itself is in [`../x265-issue.md`](../x265-issue.md).
