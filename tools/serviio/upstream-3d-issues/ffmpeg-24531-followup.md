<!-- DRAFT — NOT POSTED. For FFmpeg issue #24531 (bsf to write the
     frame-packing SEI), at code.ffmpeg.org.
     NOT GATED by policy, but this session has no credentials for that
     tracker, so the owner posts it. New, checkable observation found
     while building tools/bravia_anaglyph.py. -->

A related gap found while writing a converter, in case it belongs with this request.

When x264 writes the frame-packing SEI and the result is muxed to Matroska, **the container's `StereoMode` element is not derived from the stream**. The file then carries the in-stream signal that hardware 3D displays read, and no container tag at all, so software that only looks at the container sees a 2D file:

    ffmpeg -i in.mp4 -c:v libx264 -x264opts frame-packing=3 -c:a copy out.mkv
    ffprobe -v error -select_streams v:0 -read_intervals %+#3 -show_frames out.mkv | grep -c "Stereo 3D"
    # 3  -> the SEI is there
    ffprobe -v error -show_entries stream_tags=stereo_mode -of default=nw=1:nk=1 out.mkv
    #    -> empty, no StereoMode

The reverse is not done either: a Matroska input with `stereo_mode` set does not produce the SEI on a re-encode unless `-x264opts frame-packing=` is passed by hand.

Today the only way to get both signals into one file is a second pass (`mkvmerge -o out.mkv --stereo-mode 0:1 in.mkv`). Since the decoder already exposes the SEI as `AV_FRAME_DATA_STEREO3D` and as a `stereo_mode` frame-metadata entry, the Matroska muxer deriving `StereoMode` from stereo3d side data when the container has none would close the loop from the other end, and would pair naturally with the bsf proposed here.
