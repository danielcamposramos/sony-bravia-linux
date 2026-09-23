<!-- POSTED 2026-09-18 as discussion comment 18496283:
     https://github.com/danielcamposramos/sony-bravia-linux/discussions/1#discussioncomment-18496283
     The accurate "symptom-level, not mechanism" framing was preserved.
     Follow-up comment for github.com/danielcamposramos/sony-bravia-linux/discussions/1
     Drafted 2026-09-18. A NEW comment on the discussion, reporting the first
     cross-brand data point (Samsung) plus the ecosystem movement that makes
     the community test trivial now. Owner reviews and posts in his own voice.
     ACCURACY: r0lZ confirmed the SYMPTOM (his Samsung fails the same way),
     not the controlled with/without-SEI test — the draft says exactly that. -->

## Update — first cross-brand data point (Samsung), and testing just got easier

Two developments since this went up.

**A cross-brand confirmation, from someone who would know.** r0lZ, the author of BD3D2MK3D (the reference tool for authoring 3D MKVs, maintained for about twenty years), replied on his tool's support thread that the disappointing 3D behaviour is not a Sony quirk: *"this is common among most major brands. My Samsung TV has exactly the same problem."* ([BD3D2MK3D support thread, post #602](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread)).

To be precise about what that is and is not: it is a symptom-level confirmation from an expert, that a Samsung 3D set fails to engage 3D on the same content, not yet the controlled two-file test below run on that Samsung. So it does not isolate the *mechanism* on Samsung. But it is exactly the signal you would expect if the cause generalises, and it is consistent with the whole premise here: frame-packing SEI is standard H.264 stereoscopic signalling, not a Sony mechanism, so any era set that auto-detects from the elementary stream would behave the same way. It moves "plausibly other brands too" to "at least one other brand, reported by a credible source."

**Producing a test file is now trivial.** When this was written, making a with-SEI clip meant an x264 command line. That changed: HandBrake merged support for writing the frame-packing SEI ([PR #8100](https://github.com/HandBrake/HandBrake/pull/8100)), so a current HandBrake build now produces the *with-SEI* half of the test directly from the GUI. Reports on the player side were also filed with mpv ([#18489](https://github.com/mpv-player/mpv/issues/18489) / [PR #18490](https://github.com/mpv-player/mpv/pull/18490)) and FFmpeg, and mpv's own 3D users have independently reported the panel detecting the signal but the display path refusing to switch, so the finding is being looked at from several directions at once.

**The ask still stands, and the Samsung case is now the most valuable one to close.** If you have an era 3D set from any brand, the two-file test is unchanged:

1. Serve an SBS/TAB clip remuxed **without** the SEI — expect flat.
2. Serve the same clip **with** the SEI (HandBrake with frame packing, `bravia_sei3d.py`, or any x264 `--frame-packing 3`).

If it flips only in case 2, it reads the SEI. Report brand / model / year here and I will keep the list. A Samsung owner running exactly this would turn r0lZ's report into a confirmed mechanism, and would be the first entry on that list from outside Sony.
