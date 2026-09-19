This implements the AVC part of #6309, following the design discussed there. HEVC will follow as a separate MR.

What it does:

- The AVC ES parser now parses the frame packing arrangement SEI (payloadType 45). It also keeps walking the SEI loop after a recovery point instead of returning, so a frame packing message after one in the same NAL unit is found.
- Detection is done in the readers, so the stereo mode is known during identification: MP4 probes the first frames even when the avcC is present (at most the first 10,000 bytes, as the existing avcC derivation does), Matroska looks at the first frame only when the track has no StereoMode element, and the AVC ES and MPEG TS readers keep the result of the parser pass they already make.
- The result is applied with option_source_e::bitstream, so the command line and the container keep precedence without new logic.
- Mapping per RFC 9559, table 5; content_interpretation_type 2 selects the right-eye-first values. Type 5 and cancel messages are ignored.
- The parser helper lives in common/xyzvc for the HEVC MR to reuse.

Testing:

- Six new unit tests in tests/unit/common/xyzvc_frame_packing_arrangement.cpp (all arrangement types in both view orders, unspecified interpretation, non-zero arrangement IDs, types without an equivalent, cancel). The common, merge and propedit suites pass (256, 22, 24).
- The samples from #6309 plus right-eye-first variants, cross-checked against FFmpeg's reading: identification and muxing give 1, 3 and 11 as expected for MP4, Matroska, AVC ES and MPEG TS input. Plain 2D gives nothing. Command line over container over bitstream verified.
- Built on Debian trixie (GCC 14, Boost 1.83) without the GUI.

References:

- Rec. ITU-T H.264 | ISO/IEC 14496-10, Annex D, frame packing arrangement SEI message (payloadType 45)
- RFC 9559, section 5.1.4.1.28.3 (StereoMode), table 5
- FFmpeg, libavcodec/h2645_sei.c, decode_frame_packing_arrangement()

Disclamer about how this was written: English is my second language (my first is Brazilian Portuguese), so I drafted the code, this description, the commit message and the NEWS entry with an LLM, then reviewed, tested and edited them. I know you said you would likely want no LLMs for documentation. I would rather tell you than hide it, and I am happy to rewrite the texts myself, or you can replace the NEWS line with your own. I understand every change and can explain any of it. I am a registered electrical engineer in Brazil, and I stand behind the work.

This is part of a wider effort to keep stereo 3D signalling intact from encoder to display, since that SEI is the signal 3D televisions act on:

- HandBrake #8100, merged: the x264 encoder writes the SEI
- Universal Media Server #6330, merged: transcodes signal it for Sony 3D televisions
- mpv #18490, in review: the player reads it
- reports to FFmpeg (#24530, #24531), x265 (#970), AndroidX Media3 (#3419), Gerbera (#3937) and Kodi (#29337), and a comment on Jellyfin #18060

The full record, with the measurements on the televisions:
https://github.com/danielcamposramos/sony-bravia-linux
