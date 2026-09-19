Samples for issue #6309 (frame_packing_arrangement SEI -> Matroska StereoMode)
=============================================================================

All three files are synthetic, generated with ffmpeg/x264 for this issue.
No third-party footage is involved, so they can be redistributed freely.
Total size is under 60 KB.

Files
-----

sbs-frame-packing-3.mp4   1280x720, 3 s. Side-by-side pair (left half says
                          LEFT, right half says RIGHT, with the orange square
                          offset between the halves so the disparity is
                          visible). Encoded with x264 --frame-packing 3.

tb-frame-packing-4.mp4    1280x720, 3 s. Top-and-bottom pair, same idea.
                          Encoded with x264 --frame-packing 4.

remuxed-by-mkvmerge.mkv   The first file remuxed with mkvmerge 9x.x, included
                          because it shows the gap this issue is about: the
                          SEI is still present in the H.264 stream, and the
                          Matroska track carries no StereoMode element.

What the SEI says
-----------------

The frame packing arrangement SEI is H.264 Annex D payload type 45. x264
writes it once per IDR when --frame-packing is given. The relevant field is
frame_packing_arrangement_type:

    0 = checkerboard          Matroska StereoMode 5 (left eye first)
    1 = column interleaved    Matroska StereoMode 9 (left eye first)
    2 = row interleaved       Matroska StereoMode 7 (left eye first)
    3 = side by side          Matroska StereoMode 1 (left eye first)
    4 = top and bottom        Matroska StereoMode 3 (left eye first)

The SEI also carries content_interpretation_type, which says which of the two
packed frames is the left eye: 1 means frame0 is the left view, 2 means frame0
is the right view. That field selects between the left-first and right-first
Matroska values above, for example StereoMode 1 against 11 for side by side.

FFmpeg already reads it and exposes it as stereo3d side data, which is an easy
way to check the samples:

    ffprobe -show_frames -select_streams v:0 -read_intervals "%+#1" \
        sbs-frame-packing-3.mp4 | grep stereo_mode
    TAG:stereo_mode=left_right

    ffprobe ... tb-frame-packing-4.mp4 | grep stereo_mode
    TAG:stereo_mode=top_bottom

And for the remux:

    mkvmerge -J remuxed-by-mkvmerge.mkv
    (no stereo_mode property on the video track)

Why it matters in practice
--------------------------

The SEI is the signal that 3D televisions of the 2011-2012 generation act on.
On a Sony KDL-46EX725 and KDL-46HX855, a file carrying it switches the set to
3D with no user action, and the same file without it plays flat. Those sets
ignore the Matroska StereoMode element entirely, and any remux to TS drops it,
so the SEI is the only signal that survives the path from file to panel.

Because mkvmerge does not currently read the SEI, a correctly authored 3D
source loses its stereo signalling at the Matroska layer, and tools that rely
on StereoMode downstream have nothing to work with.

Generated with
--------------

ffmpeg -f lavfi -i "color=...:s=640x720:d=3,drawtext=...,drawbox=..." \
       -f lavfi -i "color=...:s=640x720:d=3,drawtext=...,drawbox=..." \
       -filter_complex "[0:v][1:v]hstack=inputs=2[v]" -map "[v]" \
       -c:v libx264 -preset veryfast -crf 26 -g 30 -pix_fmt yuv420p \
       -x264-params "frame-packing=3" -t 3 sbs-frame-packing-3.mp4

(vstack and frame-packing=4 for the top-and-bottom file.)
