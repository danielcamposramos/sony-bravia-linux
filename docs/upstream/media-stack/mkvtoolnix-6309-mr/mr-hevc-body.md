This implements the HEVC part of #6309, following the same design as the AVC MR (!6311): detection in the readers so the stereo mode is known during identification, and the result applied at bitstream level so the container and the command line keep precedence.

What it does:

- The HEVC SEI walk now also reads the frame packing arrangement message (payloadType 45) using the shared AVC/HEVC helper, then rewinds so the existing user-data handling is unchanged.
- MP4 probes the first frames even when the hvcC is present (at most the first 10,000 bytes, as the existing avcC derivation does), Matroska looks at the first frame only when the track has no StereoMode element, and the HEVC ES and MPEG TS readers keep the result of the parser pass they already make.
- One implementation note: with a configuration record the parser must be fed with m_size_nalu_minus_one + 1 as the NAL length size, because hevcc_c::unpack() does not fill m_nalu_size_length. Both new call sites do this.

Testing:

- Seven new unit tests in tests/unit/common/hevc_sei_frame_packing.cpp (prefix SEI parsing, right-eye-first selection, cancel, the arrangement type without a StereoMode equivalent, suffix SEI rejection). The common, merge and propedit suites pass (263, 22, 24).
- HEVC companions for all four containers (ES, MP4, MPEG TS, Matroska without an element): identification and muxing give 1, 2, 3 and 11 exactly per RFC 9559 table 5, and plain 2D gives nothing.
- Command line over container over bitstream verified; "mono" writes no element, identical to the released version, because that is the Matroska default value.
- Built on Debian trixie (GCC 14, Boost 1.83) without the GUI.

Sample provenance: x265 does not offer frame packing (checked 3.5 and 4.1), so the samples carry a spec-exact SEI injected by a script, and the payload bytes were verified by hand against Rec. ITU-T H.265, annex D.2.7. I can upload the set (with the script and README) to your FTP area like the AVC ones if you want to try them.

References:

- Rec. ITU-T H.265 | ISO/IEC 23008-2, annex D, frame packing arrangement SEI message (payloadType 45)
- RFC 9559, section 5.1.4.1.28.3 (StereoMode), table 5

Same disclaimer as the AVC MR: LLM-assisted drafting, reviewed, tested and understood by me; happy to rewrite the documentation texts if you prefer.
