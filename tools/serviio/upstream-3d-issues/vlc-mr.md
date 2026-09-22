# VLC merge request — x264: signal the input stereoscopic layout by default

**MR OPENED 2026-09-22: https://code.videolan.org/videolan/vlc/-/merge_requests/10366**
(owner green-lit fork + branch + MR; the session permission gate held the MR
act until he switched to manual mode and said "retry"). Fork
`capitain_jack/vlc` created from here (id 5420, import finished, master
verified). Branch `x264-frame-packing-from-input` pushed as `0f3d63a`
(`git am` of the patch, committer set to the owner's identity, Co-Authored-By
trailer appended per the honesty doctrine — the mpv revert episode showed
why it must stay). Token at `~/.config/code.videolan.org/token` (600); git
via the SparkyLinux2026 SSH key (agent-loaded, `ssh -T` greeted
`@capitain_jack`). **Ecosystem-context comment posted as [note
582081](https://code.videolan.org/videolan/vlc/-/merge_requests/10366#note_582081)**,
linking both repositories (sony-bravia-linux measurements +
awesome-stereoscopy CC0 standards map) and listing the full encode→mux→
serve→play→drive arc. Email-trigger watch from here on; never polled.

**Maintainer feedback 2026-09-22:** Alexandre Janniaux asked whether the
MR page was an AI-written wall of text citing unrelated issues, and noted
he believed the feature was 4.1 material. Answered in [note
582107](https://code.videolan.org/videolan/vlc/-/merge_requests/10366#note_582107)
in the owner's own words: English is not his first language, AI assistance
is disclosed deliberately rather than hidden, the citations are the demand
trail (#29582 is this same feature on VLC's own tracker; mkvtoolnix !6311
merged the same default after review; mpv #18490 is in review with the
ETSI precedence norm cited; HandBrake and UMS already ship it), the patch
applies 1:1 to master and was verified end to end on hardware, and there
is no objection to the 4.1 milestone. The MR text itself stays unchanged
by the owner's explicit decision ("we're changing nothing"). For the
record, the owner then also posted the driver-lane cross-links as [note
582109](https://code.videolan.org/videolan/vlc/-/merge_requests/10366#note_582109):
the amd-gfx public test report (lore), NVIDIA issues #1382 and #1384,
and notice that the nouveau deep-color series and the NVIDIA
default-cap companion are being finalized.

**Maintainer feedback, round 2 (2026-09-22, evening):** Marvin Scholz sharpened the same complaint in [note 582115](https://code.videolan.org/videolan/vlc/-/merge_requests/10366#note_582115): gigantic AI-generated walls of text drive reviewers away, and why spend free time reading what the author did not write. Answered in [note 582119](https://code.videolan.org/videolan/vlc/-/merge_requests/10366#note_582119), deliberately short (the complaint was length): the premise is wrong — every message was written by the owner in Portuguese and translated into English and back twice to keep his voice; the disclosure is deliberate; the length is the research done up front so the reviewer does not have to repeat it; the diff is the part to review; and anything that reads as unchecked output gets fixed when pointed at. The note closes with the explicit ask, same wording family as the mpv side: a **technical review of the change itself**, citing that this exact default was already judged on its merits and merged by **mbunkus in mkvtoolnix (!6311)** and **the HandBrake maintainers (HandBrake#8100)**. The owner's dictated PS ("Only Nvidia and AMD had missing pieces, all other drivers are compliant to the HDMI 1.4 3D specs") remains his own browser post per his instruction. Draft on disk: `/K3D/temp/vlc-mr10366-marvin-reply.md`.

**Re-verified against master on 2026-09-22, after the mbunkus/mpv rounds:**

- The patch applies **1:1 to today's master** (`modules/codec/x264.c`,
  1535 lines; all five anchor regions byte-identical, zero fuzz) and the
  new function compiles clean against master's `include/vlc_es.h` enum
  with `-Wall -Wextra`.
- The packetizer's SEI-45 → `multiview_mode` map and its **container
  precedence guard** are unchanged (`modules/packetizer/h264.c:1219-1243`:
  the SEI only sets the mode when the container left it at
  `MULTIVIEW_2D`). Our encoder side mirrors the same precedence the other
  way: explicit option > input signal, and 2D input stays unsignalled —
  the exact rule mbunkus merged in mkvtoolnix !6311 (no forced "mono"
  write), so the design now matches the precedent on both sides of the
  ecosystem.
- The format copy into the encoder `fmt_in` survived the transcode
  refactor: `modules/stream_out/transcode/encoder/encoder.c:91,135`
  (`es_format_Copy`).
- The avcodec decoder still maps `AV_FRAME_DATA_STEREO3D` →
  `multiview_mode` (`modules/codec/avcodec/video.c:1261+`), so both
  demux-derived and decoder-derived paths feed the encoder the same way.
- No competing open MR on frame packing/stereo (checked 2026-09-22).
  Frame-packing cadence note: x264 itself emits the SEI per IDR — the
  standardized file-content behaviour; per-frame carriage is a broadcast
  (DVB) concern and is not this patch's business. Learned on the mpv
  review round; stated below so review does not have to discover it.
- Issue #29582 still open, `Type::feature`, last touched 2026-04-16.

Target: https://code.videolan.org/videolan/vlc (master). Patch:
`vlc-0001-x264-frame-packing-from-input.patch` (this folder), made against
master's `modules/codec/x264.c`, applies with `git am`. Owner submits.

## Title

x264: signal the input stereoscopic layout by default

## Description (paste as is)

The frame_packing_arrangement SEI (ITU-T H.264 Annex D, payload type 45) is already parsed by the H.264 packetizer (`modules/packetizer/h264.c:1219-1243`) and by the avcodec decoder (`modules/codec/avcodec/video.c:1261`) into `video_format_t.multiview_mode`, and the transcode encoder copies the decoder output format into the encoder `fmt_in` (`modules/stream_out/transcode/encoder/encoder.c:91`). **The layout reaches the x264 module intact and is discarded there**: `sout-x264-frame-packing` defaults to -1, and -1 leaves `param.i_frame_packing` unset, so any re-encode of a frame-packed stream, the chromecast sout chain included, drops the SEI unless the user already knows to pass the option by hand.

Frame-compatible 3D displays detect the layout from this SEI alone. ETSI TS 101 547-2 V1.2.1 clause 6.5 gives the in-stream SEI precedence over container signalling, and container signalling does not exist in MPEG-TS at all, so the result is a correct side-by-side or top-bottom picture that the display renders flat. I verified the precedence end to end on owned hardware: a Sony set auto-engages 3D from the SEI alone, and the same file plays flat with the SEI stripped.

**This change maps `multiview_mode` onto the Annex D arrangement types when the option is left at -1**, now labelled "Same as input": checkerboard 0, column 1, row 2, side-by-side 3, top-bottom 4, frame alternation 5. An explicit value still wins over the input signal, 2D input stays unsignalled rather than forcing a negative, and 6 remains available to signal 2D output explicitly. GStreamer's x264enc behaves the same way by default, deriving `i_frame_packing` from its input caps (`gstx264enc.c`, `ARG_FRAME_PACKING_DEFAULT` "automatic (none, or from input caps)").

Note on cadence: x264 re-emits the SEI per IDR, which is the standardized file-content behaviour; per-frame carriage is a broadcast (DVB) concern and is outside this patch's scope.

**Measured on VLC 3.0.23** with a 1080p clip encoded with frame-packing=3: `#transcode{vcodec=h264}` produces an output with no Stereo 3D side data under ffprobe; the same command with `--sout-x264-frame-packing=3` produces it. This patch makes the default case behave like the second. The patch applies 1:1 to master as of 2026-09-22 and its mapping function was compiled against the current `include/vlc_es.h` enum; the full tree was not built locally.

Related: #29582. The same default is now upstream in HandBrake (HandBrake/HandBrake#8100), Universal Media Server (UniversalMediaServer/UniversalMediaServer#6330) and mkvtoolnix (!6311 merged, !6312 in review); the encode/remux links of the pipeline now carry the signal by default, and the player side is catching up — mpv (mpv-player/mpv#18490, in review) and this one.

*AI partners were leveraged in the production of this work.*

## Steps to submit

1. At https://code.videolan.org (account approved), fork `videolan/vlc`.
2. `git clone git@code.videolan.org:capitain_jack/vlc.git` (SparkyLinux2026 SSH key, same as the other remotes) → `git checkout -b x264-frame-packing-from-input` → `git am vlc-0001-x264-frame-packing-from-input.patch` → `git push origin x264-frame-packing-from-input`.
3. Open the MR against `videolan/vlc:master` with the title and description above.
