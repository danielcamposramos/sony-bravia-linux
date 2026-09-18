<!-- DRAFT — NOT POSTED. For mpv PR #18490 (or issue #18489).
     GATED: llyyr invoked the contribution guidelines over AI-written
     text on this very PR, so nothing here goes out as written. The
     owner rewrites it in his own words, or drops it. Value: it answers
     "is deriving stereo mode from the decoder an accepted approach"
     with a precedent a reviewer can check in one grep, plus a hardware
     measurement. Keep it short if used at all. -->

A data point on the approach, in case it is useful to the review: Kodi already does this, and has for years.

`CDVDVideoCodecFFmpeg` takes the stereo mode from the **decoded frame's metadata** — FFmpeg's H.264 decoder sets a `stereo_mode` entry from the frame-packing SEI, with the Matroska strings as values (`left_right`, `top_bottom`, …):

    xbmc/cores/VideoPlayer/DVDCodecs/Video/DVDVideoCodecFFmpeg.cpp:1043
    AVDictionaryEntry* entry = av_dict_get(m_pFrame->metadata, "stereo_mode", NULL, 0);

Verified by running Kodi 21.2 on a file whose only 3D signal is the SEI (neutral filename, no container tag): `autodetected stereo mode for movie mode left_right`.

Sample to check against:

    ffmpeg -f lavfi -i testsrc2=size=1920x1080:rate=24 -t 10 -c:v libx264 \
      -x264-params frame-packing=3 -pix_fmt yuv420p sbs.mp4
    ffprobe -show_frames -read_intervals %+#1 sbs.mp4 | grep side_data_type   # Stereo 3D
    ffprobe -show_entries stream_tags=stereo_mode sbs.mp4                     # nothing

And on why it matters outside players: on 2011–2012 Sony BRAVIA sets this SEI is the only signal that makes the display engage 3D by itself. Measured through two independent DLNA servers, byte-exact: the SEI-carrying file engages 3D, the identical file with the SEI removed plays flat.
