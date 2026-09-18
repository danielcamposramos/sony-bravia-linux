<!-- DRAFT ONLY — not posted. Target: jellyfin/jellyfin PR #18060 "Flatten
     frame packed 3D video to a single view when transcoding".
     Jellyfin has no written AI-content policy, so per repo doctrine this is
     the owner's to review and post in his own words; the provenance block
     is included per our own disclosure rule if he chooses to keep it.
     Angle: genuinely additive to their flatten work (layout detection),
     NOT a pitch. One reference link at the end only. -->

For the flatten step, one detail that may save a class of wrong-layout bugs: the SBS/TAB arrangement of frame-packed 3D is not always in the container. H.264 carries it in-stream as the `frame_packing_arrangement` SEI (payload type 45, Annex D), and libavcodec already decodes that into `AV_FRAME_DATA_STEREO3D` frame side data. Some sources — anything remuxed or authored without a Matroska `StereoMode` tag, which is common for frame-compatible files — carry the layout *only* there, with no container flag at all.

So if flattening reads the layout from the container tag (Video3DFormat) alone, files that only carry the in-stream SEI would either be missed or flattened with the wrong crop. Reading `AV_FRAME_DATA_STEREO3D` as a fallback (or as the authoritative source, per the frame-compatible broadcast specs where the SEI takes precedence) would cover both.

Not asking to expand this PR's scope — just flagging the second layout source so the detection side is complete for both flatten and any future keep-3D path.

<!-- Optional disclosure block if kept: -->
> Context/disclosure: this note draws on a right-to-repair project that
> mapped this signalling across hardware and tools (frame-packing SEI vs
> container tag), documented at
> github.com/danielcamposramos/sony-bravia-linux. Written with AI
> assistance; posting under my own name and taking responsibility for the
> content.
