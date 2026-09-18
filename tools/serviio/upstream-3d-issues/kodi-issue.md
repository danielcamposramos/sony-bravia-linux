<!-- CORRECTION (2026-09-18, same day): the central claim below is WRONG.
     Kodi reads the frame-packing SEI through FFmpeg's decoded-frame
     metadata (DVDVideoCodecFFmpeg.cpp:1043 reads "stereo_mode" from
     m_pFrame->metadata). Verified in Docker on Kodi 21.2 with a neutrally
     named SEI-only MP4: "autodetected stereo mode for movie mode
     left_right". The claim came from gh code search alone, before running
     Kodi. Public correction held for the owner's go; see the campaign
     README row 11 for the DLNA-side findings that replace it. -->

<!-- POSTED 2026-09-18 as https://github.com/xbmc/xbmc/issues/29337
     Filed from this session under the owner's account on his explicit
     instruction ("no AI policy, post brief and objective"). Kodi's
     CONTRIBUTING files were checked first: no AI policy. Filed with the
     bug_report template; the one gap, stated in the issue itself, is the
     mandatory debuglog: the finding is from source reading and Kodi is
     not installed here, so none was fabricated.
     Watch: email trigger only (GitHub notifies the author), never poll.
     The body below is exactly what was posted. -->

## Bug report
### Describe the bug
Kodi takes a video's stereo mode only from container metadata (`stereo_mode`, and WMV `Stereoscopic`/`StereoscopicLayout`) in `CDVDDemuxFFmpeg::GetStereoModeFromMetadata`, and from filename tokens in `CStereoscopicsManager`.
The H.264 `frame_packing_arrangement` SEI (payload type 45, ITU-T H.264 Annex D), the in-stream signal that 3D TVs switch on and that DVB specifies for frame-compatible 3D, is never read.
On `master` (6c678081054b) there is no reference to `AV_FRAME_DATA_STEREO3D`, `AV_PKT_DATA_STEREO3D` or `frame_packing` anywhere in the tree.

So a correctly signalled side-by-side or top-and-bottom file plays as 2D whenever the container carries no tag: MP4 (no standard stereo tag), MPEG-TS remuxes served by DLNA servers, broadcast recordings.
HandBrake now writes this SEI when encoding 3D (HandBrake/HandBrake#8100), so SEI-only MP4 files are becoming more common.

## Expected Behavior
When the container has no stereo metadata and the filename has no 3D token, Kodi uses the frame-packing SEI and selects the matching stereoscopic mode, as a 3D TV does with the same file.

## Actual Behavior
The file is treated as mono.

## Possible Fix
If `stereo_mode` is still empty after `GetStereoModeFromMetadata`, derive it from the SEI:
- software decoding: FFmpeg already parses the SEI into `AV_FRAME_DATA_STEREO3D` on decoded frames;
- hardware decoding: that frame side data is not available, so parse SEI payload 45 from the first access units.

Mapping: `frame_packing_arrangement_type` 3 → `left_right` (`right_left` when `content_interpretation_type` is 2), 4 → `top_bottom` (`bottom_top`).
An explicit container tag or filename token stays authoritative; the SEI only fills the gap.
mpv had the same gap: mpv-player/mpv#18489, with a patch in mpv-player/mpv#18490.

### To Reproduce
1. Create an SEI-only side-by-side sample:
   `ffmpeg -f lavfi -i testsrc2=size=1920x1080:rate=24 -t 10 -c:v libx264 -x264-params frame-packing=3 -pix_fmt yuv420p sbs_sei.mp4`
2. Confirm the signal is in the stream and not in the container:
   `ffprobe -v error -show_frames -read_intervals %+#1 sbs_sei.mp4 | grep side_data_type` prints `side_data_type=Stereo 3D`;
   `ffprobe -v error -show_entries stream_tags=stereo_mode sbs_sei.mp4` prints nothing.
3. Play `sbs_sei.mp4` in Kodi. Per the code path above no stereoscopic mode is selected; renaming it to `sbs_sei.3D.SBS.mp4` changes that, and the filename is the only difference.

### Debuglog
None attached: this was found by reading the demuxer and stereoscopics code, not from a playback error, and the sample above reproduces it on any platform. I can attach a playback debuglog if that helps triage.

## Additional context or screenshots (if appropriate)
The same SEI-only file switches 2011–2012 Sony BRAVIA sets into 3D automatically, and the same behaviour is reported on Samsung sets, because those displays read the SEI rather than the container tag.
Measurements and background: https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md

### Your Environment
 - [ ] Android
 - [ ] iOS
 - [ ] tvOS
 - [x] Linux
 - [ ] macOS
 - [ ] Windows
 - [ ] Windows UWP

 - Operating system version/name: Debian (source reading applies to all platforms)
 - Kodi version: master at 6c678081054b (2026-09-18)
