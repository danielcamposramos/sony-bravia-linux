<!-- POSTED 2026-09-18 by the owner, in his own words, to Codeberg #6309:
     https://codeberg.org/mbunkus/mkvtoolnix/issues/6309#issuecomment-23228848
     Watch: email trigger only, never poll.
     The draft as prepared follows, kept for the record.
     (mkvmerge deriving the stereo mode from the SEI).
     The owner filed #6309 as himself and owns every claim there, so
     this only goes out in his words, and only if he judges it worth
     the maintainer's time — mbunkus closes verbose reports. It is
     short on purpose, and it is fine to send nothing. -->

Two things since filing, both checkable, in case they help the case.

FFmpeg does not close this loop from the other side: when x264 writes the frame-packing SEI and the result is muxed to Matroska, `StereoMode` is not derived from the stream, so the file has the SEI and no container tag.

    ffprobe -v error -select_streams v:0 -read_intervals %+#3 -show_frames out.mkv | grep -c "Stereo 3D"   # 3
    ffprobe -v error -show_entries stream_tags=stereo_mode -of default=nw=1:nk=1 out.mkv                   # empty

So `mkvmerge -o out.mkv --stereo-mode 0:1 in.mkv` by hand is currently the only way to get both signals into one file, which is what this request would make automatic.

And the hardware side is now confirmed through two independent DLNA servers rather than one: a file whose only 3D signal is the SEI switches a 2011 Sony BRAVIA into 3D by itself, and the identical file with the SEI removed plays flat.
