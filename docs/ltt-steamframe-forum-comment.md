<!-- POSTED 2026-09-18 as findComment-16936512:
     https://linustechtips.com/topic/1642726-the-steam-frame-changes-everything-full-review/?do=findComment&comment=16936512
     Second audience-facing post (companion to the 3D-theater comment
     16936161, which it cross-cites chronologically).
     Original draft note: cross-comment for the LTT forum thread on the
     Steam Frame review. Post here only because this video DOES discuss
     3D content (~21:10); the "first 30 mins" video does not, so that
     thread is skipped. Owner reviews and posts in his own words (drafts
     are raw material; keep it additive, not a pitch; no slop). -->

The bit at ~21:10 about "so little 3D content available" connects straight back to Linus's own 3D projector build a couple of years ago, where getting the content to actually play took, in his words, "more tinkering behind the scenes than anything else we've done so far" (ripping Blu-rays, following a Reddit thread to remux by hand).

Worth saying plainly, because it changes the framing: the 3D-movie problem is not really content scarcity. He said it himself in that projector video, dozens of 3D titles still ship on Blu-ray every year. It is a signalling problem, and it is fixable.

There are two 3D flags. The Matroska container tag, which everything writes and reads, and the in-stream H.264 frame_packing_arrangement SEI, which lives inside the video itself. The container tag gets dropped the moment a file is delivered by anything that keeps only the video stream (a DLNA server remuxing to TS, for instance), and the in-stream SEI is what hardware 3D displays actually read to auto-engage. It is the same signal DVB standardised for frame-compatible 3D broadcast. The catch: for years almost nothing on the software side wrote it into files, so the flag the hardware wants was simply missing. That is why a correctly-authored 3D file plays flat, and it is documented for a decade across Plex, Jellyfin, Serviio and MakeMKV forums without anyone naming the cause.

The chain to fix it is now mapped end to end: HandBrake merged writing the SEI, there is an mpv patch to read it, and fully automatic 3D over DLNA has been restored on stock free software. It is one 16-byte message, not new hardware.

Full write-up, evidence and tools, if useful to anyone here: https://github.com/danielcamposramos/sony-bravia-linux
