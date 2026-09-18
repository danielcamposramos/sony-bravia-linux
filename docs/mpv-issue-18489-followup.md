<!-- Draft follow-up COMMENT for mpv issue #18489 (the issue, not PR #18490).
     Drafted 2026-09-18. Owner reviews and posts in his own words (doctrine:
     no AI-written text verbatim; factual, no meta-fight).
     DVB claim is the softened/sourced version verified against ETSI TS
     101 547-2 directly. Keep it short, maintainers value brevity. -->

Some context that has come together since I filed this, in case it helps weigh the change: the signal this issue is about is not a Sony niche, and the gap around it is ecosystem-wide and long-standing.

**It is a standard signal, and in one place an authoritative one.** The `frame_packing_arrangement` SEI (payload type 45) is defined in H.264 Annex D, added to the standard in 2010 alongside the Stereo High profile. DVB's frame-compatible 3DTV spec then made it the definitive carrier: ETSI TS 101 547-2 clause 6.4.1 requires the SEI to be sent with every frame of a frame-compatible 3D service, and clause 6.5 says it "takes precedence over other signalling as regards video format" over the DVB-SI descriptors, which only flag presence. (Scope, to be fair: that binds DVB broadcast receivers; a lot of era 3D also arrived over HDMI 1.4a, a separate frame-packing path. But as an in-stream signal, the SEI is the standardized, precedence-taking one, not a vendor invention.)

**The "3D file plays flat" problem is not specific to these TVs.** The same symptom, a correctly-authored SBS/TAB file that will not auto-engage 3D, is documented for years across the media-server ecosystem without the root cause being named: [Plex](https://forums.plex.tv/t/some-3d-sbs-and-up-under-mkv-files-not-recognised/51445), [Jellyfin](https://forum.jellyfin.org/t-3d-full-sbs-video-detection-and-playback), the Serviio and MakeMKV forums, [AVS](https://www.avsforum.com/threads/properly-playing-back-a-3d-mkv.3235394/). The recurring tell in those threads, files that carry a container stereo flag playing flat while ones without it work, is consistent with the player reading the in-stream SEI rather than the container tag.

**It is cross-brand.** r0lZ, the author of BD3D2MK3D (the long-standing 3D-MKV authoring tool), notes his own Samsung 3D set has the same problem; the frame-compatible 3D file era spanned brands. (Honest caveat: BD3D2MK3D writes both the SEI and the MKV tag, so its files show compatibility, not which signal a given device read; the clean per-device test is separate.)

None of this changes what PR #18490 does, it just speaks to why reading `AV_FRAME_DATA_STEREO3D` is worth doing: it is a standardized, still-encountered signal that the surrounding ecosystem has been missing for a decade, not a fix for two specific televisions. Happy to fold any of these references into the PR if useful.
