# x265: `--frame-packing` (issue #970)

**2026-10-21:** [x265 #999](https://github.com/Multicorewareinc/x265/pull/999) merged into master as `a62f37cff920789eb96ffb39e729176351d08cb3`, by kirithika7. Akilan Sivakumar implemented the `--field`/`--b-adapt 0` restriction fix, regression tests and documentation after Daniel reported the restriction while reviewing #986. Our [48-encode combined validation](https://github.com/Multicorewareinc/x265/pull/999#issuecomment-6278374499) supported the fix. **#986 remains open**; this merge does not land the proposed `--frame-packing` option.

Material for the pull request that answers [Multicorewareinc/x265#970](https://github.com/Multicorewareinc/x265/issues/970): a dedicated `--frame-packing` option that writes the frame packing arrangement SEI (H.265 D.2.16), as x264 does for H.264.

- `0001-Add-frame-packing-option-to-emit-the-frame-packing-a.patch`: the change, on x265 master d97872539.
- `hevc-sbs-capture.png`: an HEVC clip encoded with `--frame-packing 3`, played on a Linux stereo desktop. The player reads the SEI and declares the video as stereo; the capture holds the two eyes side by side: LEFT in the left eye, RIGHT in the right eye, the same frame number in both.
- `hevc-tb-capture.png`: the same for a top-and-bottom clip encoded with `--frame-packing 4`.

The request itself is in [`../x265-issue.md`](../x265-issue.md).
