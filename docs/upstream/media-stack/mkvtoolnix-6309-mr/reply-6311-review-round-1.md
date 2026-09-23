All seven points are in, force-pushed as two commits.

The static two dimensional array replaces the case cascade in `parse_frame_packing_arrangement`, indexed by `frame_packing_arrangement_type` and then by whether frame 0 is the right view. The types without a StereoMode equivalent are simply not listed and a bounds check catches them. Much more slim and simple, thank you for the tip.

`verify_avc_video_track` now exists in the Matroska reader and is dispatched from the same `if`/`else` chain as the other codec types, next to `verify_theora_video_track`. It returns `bool` like the rest of the family, always true for now, since a missing SEI is not a track error.

The identification helper is set before the whole `info.add`/`info.set` cascade, so the cascade is intact again. The `?` are aligned, the `:` sit under the `=`, and the last value lines up with the other two. It really makes things easier to spot on code.

The MP4 packetizer hookup moved out of `create_video_packetizer_avc` into `qtmp4_demuxer_c::set_packetizer_stereo_mode`, called right after `set_packetizer_display_dimensions` and `set_packetizer_color_properties` in `create_packetizer`, in the same shape as the other shared video track properties. Neat design!

`derive_track_params_from_avc_bitstream` absorbed the stereo mode detection, so the bitstream is read and parsed once and `derive_stereo_mode_from_avc_bitstream` is gone. No twice the work anymore.

About `verify_avc_video_parameters` needing no changes, I built it your way first and measured it, so you do not have to spend time on it yourself. It does not hold, and the reason is narrow. That function is the only caller of `derive_track_params_from_avc_bitstream`, and it calls it in the second branch, which is reached only when the avcC is missing. With the early `return true` still in place, an ordinary MP4 that has an avcC never reaches the merged function, so nothing ever parses the bitstream. On that build all four MP4 identification cases report no stereo mode and the remux writes no `StereoMode` element at all, while the AVC elementary stream, MPEG TS and Matroska cases stay correct because they do not pass through this function.

Dropping that early branch is the entire change. The function is now the `derive_track_params_from_avc_bitstream` call plus the existing warning, which keeps the avcC decision inside the function that actually owns it. With that, the suite is 22 of 22 again.

The MPEG TS hookup is at the end of `create_packetizer`, just before `show_packetizer_info`, so it covers every codec.

The `=` alignment is a separate `cosmetics: alignment` commit, as you suggested.

On the HEVC side you are right that this makes the corresponding TS change unnecessary there, and the same turns out to be true of both MP4 hookups. I will rebase !6312 onto this once the shape here is settled rather than now, so I am not chasing a moving target.

While testing I went after the corner where the container and the bitstream disagree, and it turned into a fix rather than a question, so there is now a third commit.

`mkvmerge --stereo-mode 0:0` never actually recorded the choice. StereoMode's default value is 0, mkvmerge renders its track headers without defaults, so the element was dropped and the track read back as if nothing had been said about the stereo mode. mkvpropedit does not behave that way, because it only ever holds the elements that were really in the file, so `mkvpropedit --edit track:v1 --set stereo-mode=0` does write it. The two tools disagreed about whether mono can be expressed at all.

This merge request does not introduce that. I checked against the stock v101.0 packaged by Debian and it behaves identically, with no patch involved. What the SEI detection changes is the consequence. Before, a discarded mono left the track merely unset, and now the bitstream fills the gap, so an explicit mono comes back as side by side on the next read. The same thing happens to a mono set with mkvpropedit: it does not survive a single remux, because mkvmerge cannot write it back.

The fix takes the default away from that one element, the same way `kax_block_add_id_c` already does for the block addition ID, so nothing else in the headers changes. After it: `--stereo-mode 0:0` writes mono and still reads back as mono after three remux rounds, an ordinary 2D file gains no StereoMode element at all, and the SEI derived and command line values are unaffected.

It is a separate commit on purpose. If you would rather have it as its own merge request, or not at all, drop that one commit and the rest still stands.

I did also look at whether the bitstream should simply outrank the container for this property, since on the televisions this came from the SEI is the only stereo signal the sets act on. I am not proposing it. A mono set with mkvpropedit is a deliberate statement by the user and flipping the order would quietly override it, and the case that actually matters, a rip carrying the SEI with no StereoMode element, already works under your ordering. The real problem in that corner was the one above, that mkvmerge could not record the choice in the first place.

One last thing worth putting on the record about why this SEI is worth reading at all. For side by side and top and bottom the frame geometry corroborates it: split the frame the way the arrangement says, compare the per eye aspect against the container, and you get full against half. For checkerboard and the two interleaved modes it does not corroborate anything, because both eyes occupy the same pixels and the frame is indistinguishable from 2D by any measurement you can make on it. For those three arrangements the SEI is not the best signal, it is the only one that exists.

Verified on the patched build, 23 of 23: identification and remux across MP4, Matroska, AVC elementary stream and MPEG TS, left first and right first, 2D files reporting nothing, command line over container over bitstream, and the mono round trip that used to fail. The 256 unit tests pass, including the six for the mapping helper.
