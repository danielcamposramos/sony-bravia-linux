# VLC merge request — x264: signal the input stereoscopic layout by default

**Status 2026-09-19: waiting on account approval.** The owner signed up at
code.videolan.org with his GitHub account; VideoLAN's GitLab holds new
accounts for administrator approval. **Before sending:** re-check VideoLAN's
AI policy with the account in hand (their wiki, which carries the GSoC-scoped
ban, was offline on every attempt) and respect whatever applies. Workflow as
usual: drafted here, owner reviews, owner authorises or sends.

Target: https://code.videolan.org/videolan/vlc (master). Patch:
`vlc-0001-x264-frame-packing-from-input.patch` (this folder), made against
master's `modules/codec/x264.c`, applies with `git am`. Owner submits.

## Title

x264: signal the input stereoscopic layout by default

## Description (paste as is)

The frame_packing_arrangement SEI (ITU-T H.264 Annex D, payload type 45) is already parsed by the H.264 packetizer (`modules/packetizer/h264.c`) and by the avcodec decoder into `video_format_t.multiview_mode`, and `transcode_encoder_new()` copies the decoder output format into the encoder `fmt_in` (`modules/stream_out/transcode/encoder/encoder.c`). **The layout reaches the x264 module intact and is discarded there**: `sout-x264-frame-packing` defaults to -1, and -1 leaves `param.i_frame_packing` unset, so any re-encode of a frame-packed stream, the chromecast sout chain included, drops the SEI unless the user already knows to pass the option by hand.

Frame-compatible 3D displays detect the layout from this SEI alone. ETSI TS 101 547-2 (DVB frame-compatible 3DTV) gives the in-stream SEI precedence over container signalling, and container signalling does not exist in MPEG-TS at all, so the result is a correct side-by-side or top-bottom picture that the display renders flat.

**This change maps `multiview_mode` onto the Annex D arrangement types when the option is left at -1**, now labelled "Same as input": checkerboard 0, column 1, row 2, side-by-side 3, top-bottom 4, frame alternation 5, 2D left unset. An explicit value still wins, and 6 still signals 2D output explicitly. GStreamer's x264enc behaves the same way by default, deriving `i_frame_packing` from its input caps (`gstx264enc.c`, `ARG_FRAME_PACKING_DEFAULT` "automatic (none, or from input caps)").

**Measured on VLC 3.0.23** with a 1080p clip encoded with frame-packing=3: `#transcode{vcodec=h264}` produces an output with no Stereo 3D side data under ffprobe; the same command with `--sout-x264-frame-packing=3` produces it. This patch makes the default case behave like the second. The mapping function was compiled against the `include/vlc_es.h` enum with `-Wall -Wextra -Werror` and exercised for all seven modes; the full tree was not built locally.

Related: #29582. The same signal is now written upstream by HandBrake (https://github.com/HandBrake/HandBrake/pull/8100) and Universal Media Server (https://github.com/UniversalMediaServer/UniversalMediaServer/pull/6330), both merged.

*AI partners were leveraged in the production of this work.*

## Steps to submit

1. Sign in at https://code.videolan.org (VideoLAN's own GitLab; new accounts may need approval) and fork `videolan/vlc`.
2. `git clone <your fork>` → `git checkout -b x264-frame-packing-from-input` → `git am vlc-0001-x264-frame-packing-from-input.patch` → `git push origin x264-frame-packing-from-input`.
3. Open the MR against `videolan/vlc:master` with the title and description above.
