# DRAFT — LTT forum reply, thread "I built a 3D theater in my basement" (topic 1589907)

Raw material per campaign doctrine — Daniel rewords in his own words and posts from his account (Daniel Ramos BR). Review notes from the saved HTML are below the draft. POST BODY IS SINGLE-LINE PARAGRAPHS — do not re-wrap when editing; copy each paragraph as one line.

## Draft post (single-line paragraphs, plain URLs — Invision does not render markdown links)

This thread's running complaint was the guide the video promised in the description and never delivered, so here is the guide — and it comes with the bug fixes merged upstream. I spent the last weeks reverse-engineering why 3D rips play flat on hardware, and the answer is a broken signalling chain that hits the exact pipelines discussed in this thread.

A 3D file can declare its layout in two places: the Matroska StereoMode container tag, which software players read, and the H.264 frame_packing_arrangement SEI inside the stream itself (payload type 45, the standardized signaller from the DVB 3D broadcast era), which is what hardware players that auto-engage 3D actually read — only. In my real-world 44-title 3D library, 43 files carried the tag and 0 carried the SEI, so every one of them played flat on two generations of Sony 3D TVs, proven with single-variable tests: the SEI alone flips the TV into 3D, the tag alone does nothing. r0lZ, the author of BD3D2MK3D, confirmed his Samsung behaves the same, so this is not a Sony quirk, it is the broadcast decoder stack every era 3D TV shipped with.

@WeeemRCB — your MakeMKV → BD3D2MK3D → HandBrake H.265 pipeline for VR is exactly where this bites: x265 currently cannot write the SEI at all, which is the gap I filed here (https://github.com/Multicorewareinc/x265/issues/970), while the x264 side is now fixed in HandBrake master (PR #8100, it maps the detected layout to the encoder's frame-packing: https://github.com/HandBrake/HandBrake/pull/8100).

The full writeup with a lossless SEI injector (16 bytes per keyframe, no re-encode) is here: https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md — repo: https://github.com/danielcamposramos/sony-bravia-linux — related: an ffmpeg CLI bug when both signals are present (https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530), a feature request for a lossless injector bsf (https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531), and the player-side detection in mpv currently in review (https://github.com/mpv-player/mpv/pull/18490).

The end goal is that the 3D library just works on anything — a 2011 TV or a Quest through SteamVR — with no per-player settings and no filename guessing. Today even VR players ignore the proper signalling, so every headset owner redoes the same manual SBS/TAB selection by hand; fix the detection end to end and that stops being anyone's job.

For anyone who was into 3D gaming back in 2011, how this started for me is a one-page story about a gifted iZ3D license and Max Payne in anaglyph: https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-origin-story.md

Happy to answer any of the technical bits.

## Review notes from the saved HTML (2026-09-16)

1. Thread state: opened by Elijah Horner (LTT staff) Nov 22, 2024, for the video; last activity Dec 14, 2024 — a ~21-month necro. Replies are open (the editor loads for your account). LTT does not auto-lock old threads, but a brand-new account reviving an old thread with a link-heavy post is the exact shape mods pattern-match as spam. Options: (a) post the reply as drafted (it answers the thread's own standing complaint, which is the best possible cover), (b) new thread in a more fitting subforum linking the theater thread — owner's call.
2. Account rank: Daniel Ramos BR is "Newbie" — first post. If it gets mod attention anyway, the iZ3D paragraph is what proves a real person with a real history wrote it. Keep it.
3. The two in-thread hooks are load-bearing: the never-delivered guide complaint (Mighty_Dork, darwin006, starsmine, AbsoluteWoo argued about it for two weeks) and WeeemRCB's VR pipeline. If you trim anything, trim the upstream-campaign link paragraph, not the hooks.
4. Formatting: Invision auto-embeds pasted plain URLs — paste as plain text, let the editor embed. Do not paste markdown. Paragraphs as single lines (already done). Quote-reply WeeemRCB's post through the forum UI so they get notified — the @name alone may not.
5. Do not mention the pirated-release comment (Annika102001); the work is about your own rips and there is nothing to gain.
6. SteamVR/Quest paragraph is from conversation, not repo docs — Daniel verifies the framing before posting.