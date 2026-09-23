# DRAFT — HandBrake issue comment
**Where:** comment on the open issue
https://github.com/HandBrake/HandBrake/issues/5826 (galad87 already
invited a patch there; the master fix landed as the container half of
exactly that request)
**Do NOT frame as MVC support** — that is what got #1467 closed. This
ask is only: preserve the in-stream SEI for already-SBS/TAB inputs.

**RESOLVED — PR #8100 MERGED 2026-09-16** (merge commit `b0145ad`,
"libhb: signal stereo 3d frame packing in the x264 encoder", closes
this ask; #5826 closed by the merge):
https://github.com/HandBrake/HandBrake/pull/8100

Outcome notes: galad87 approved the scope in-thread ("That seems ok,
even if it will work only in x264") and asked that further messages
not be AI-written; the patch was then submitted in the owner's own
voice and merged same-day. **Campaign doctrine from this thread: the
drafts here are raw material — the owner rewrites posts in his own
words before posting; no AI-drafted text goes out verbatim, no
disclaimer line on future posts.**

For the record, the timestamps on PR #8100 (from the GitHub API):
opened 2026-09-16T05:45:34Z, merged 2026-09-16T07:06:47Z — an
interval of 81 minutes, which is just the time the repo's CI checks
needed to run. Noted without comment; make of it what you will.

Original comment (posted 2026-09-15):
https://github.com/HandBrake/HandBrake/issues/5826#issuecomment-5685776464

---

*AI-assistance disclaimer: this comment was written with the assistance of an AI coding agent (Claude Code CLI, running the GLM 5.3 model), under the direction — and with the live on-hardware verification — of the owner of the TVs involved.*

Great to see commit 1d20876 ("libhb: preserve the stereo 3d metadata")
land on master for 1.12.0 — that fixes the container-tag half of this
issue (and NEWS confirms: "Stereo 3D and spherical video mapping
metadata are now preserved").

There is a second half, and for a class of real hardware it is the
only half that matters: **the H.264 bitstream itself still carries no
3D signalling.** Players that *auto-engage* 3D — era 3D TVs (we proved
it live on 2011/2012 Sony BRAVIA sets, single-variable tests) — read
the `frame_packing_arrangement` SEI (payload type 45) from the
elementary stream and ignore the Matroska `StereoMode` tag. The
background with the hardware proof is here:
https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md

Concretely: a HandBrake re-encode of an SBS source still plays flat on
those sets, because no encoder path writes the SEI. In a real-world
44-title 3D MKV library we surveyed, 43/44 carried the container tag
and 0/44 carried the SEI — every one plays flat on SEI-only hardware.

**The fix is small and the data already flows.** `title->stereo_3d`
now reaches the job (`common.c:4970`), so in `libhb/encx264.c` when
`job->stereo_3d.type` is set, map it to the x264 param:

```c
if (job->stereo_3d.type == HB_STEREO3D_SIDEBYSIDE)
    param.i_frame_packing = 3;   /* side-by-side */
else if (job->stereo_3d.type == HB_STEREO3D_TOPBOTTOM)
    param.i_frame_packing = 4;   /* top-bottom */
```

x264 writes the SEI itself before every keyframe — no new dependency,
a few lines in one file. ffmpeg's libx264 wrapper has done exactly
this mapping since 2013 (commit 09cb75cd), so the pattern is
well-established upstream of you.

Notes:
- The SEI is ignorable metadata — players that don't understand it
  are unaffected (it's standard H.264 stereoscopic signalling, the
  same mechanism DVB standardized for frame-compatible 3D broadcast).
- HEVC/x265 has no equivalent param today (x265 defines the payload
  type but has no writer) — that one genuinely needs upstream x265
  work; the ask here is only the x264 mapping.
- This is deliberately NOT an MVC-decode request (the subject of the
  closed #1467) — it only concerns inputs that are already SBS/TAB.

Happy to submit the PR if the approach sounds right.