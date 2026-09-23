!6312 is rebased on this one and is a good deal smaller now.

The change you pointed at on !6311 removed three hunks rather than one. The MPEG TS hookup went, as you said it would, and so did both MP4 ones, `create_video_packetizer_mpegh_p2_es` and `create_video_packetizer_mpegh_p2`, because `set_packetizer_stereo_mode` in the shared video track handling covers them as well. Three codec specific calls replaced by the two generic ones in this renewed merge request.

What is left over there is the part that genuinely is HEVC: the frame packing SEI parsing in `common/hevc/util.cpp` on top of the shared helper, the HEVC elementary stream reader, the first frame probes in the Matroska and MP4 readers, and the unit tests.

The same review points are applied there too, so you do not have to repeat yourself. The Matroska probe is now `verify_hevc_video_track`, dispatched from the same `if`/`else` chain right next to the AVC one. The MP4 side is `derive_track_params_from_hevc_bitstream`, named after the AVC function you pointed me at in #6309. The `=` alignment in `new_stream_v_hevc` is a separate `cosmetics: alignment` commit.

Verified on the rebased build: 26 of 26 for HEVC across MP4, Matroska, HEVC elementary stream and MPEG TS, left first and right first, 2D files reporting nothing, and command line over container over bitstream. The AVC side of this merge request still passes 23 of 23 on that same build, and the unit tests are 263 of 263 with the seven HEVC ones included.
