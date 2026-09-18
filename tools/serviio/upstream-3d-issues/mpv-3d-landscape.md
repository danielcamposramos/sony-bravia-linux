# The 3D surface in mpv — open issues, 2026-09-17

Mapped while working [PR #18490](https://github.com/mpv-player/mpv/pull/18490),
to see what else is open and whether anything connects. Searching mpv for
"stereo" mostly returns audio tickets; these five are the actual 3D ones.

| # | filed | comments | subject | relation to our work |
|---|---|---|---|---|
| [18489](https://github.com/mpv-player/mpv/issues/18489) | 2026-09-16 | 0 (2 👍) | stream-signalled layout ignored | ours |
| [18380](https://github.com/mpv-player/mpv/issues/18380) | 2026-08-17 | 0 | MVC 3D (Blu-ray two-view) playback | different layer: decoding a second view, blocked upstream in libavcodec. Our work is detection within one view. Touch point: the reporter's workaround is "transcode to SBS first", and HandBrake now writes the SEI ([PR #8100](https://github.com/HandBrake/HandBrake/pull/8100)), so that workaround stopped losing the layout signal. |
| [18348](https://github.com/mpv-player/mpv/issues/18348) | 2026-08-07 | 4 | `sbsl`/`abl` removed, full treated as half | already cross-referenced in #18490. That ticket is about the layout *vocabulary*; ours is about the *detection source*. |
| [17632](https://github.com/mpv-player/mpv/issues/17632) | 2026-03-23 | 9 | OSD misplaced on 3D in fullscreen | **the live connection** — see below |
| [15225](https://github.com/mpv-player/mpv/issues/15225) | 2024-10-30 | 5 | `format:stereo-in` broken when encoding | plausibly related to follow-up #2 offered in #18490 (`export AV_FRAME_DATA_STEREO3D from mp_image_to_av_frame()`), but **unverified**. The reporter's own diagnosis points at the OSD subtitle renderer being bypassed in encode mode, which is a different mechanism from AVFrame side data. Test before claiming anything. |

## #17632 — the one with a real opening

Two things make it worth attention.

**It was filed by netExtra**, who is also one of the two accounts that 👍'd
our #18489. Not a passing reader: someone who watches 3D on mpv through a
VR headset and has had an open 3D bug since March.

**A maintainer stated a blocker we can answer.** kasper93, 2026-03-25:

> "I tried to figure out how add compensation for OSD position/size/aspect
> ratio. But I don't know how to detect if it's half sbs or full sbs."

That question has a measured answer — see
[mpv-full-vs-half-detection.md](mpv-full-vs-half-detection.md). The SEI
gives the arrangement, the frame geometry gives full vs half, and mpv
already has the second half of that.

## What #18490 actually fixes

Checked against the diff rather than from memory: 42 added lines, one
deleted, two files (`video/mp_image.c`, `filters/f_decoder_wrapper.c`).
It sets `params.stereo3d` from `AV_FRAME_DATA_STEREO3D` and keeps that
value alive across the frames between keyframes. There is no conversion,
no display change, no encode path and no new layout modes in it.

So the count is **one**.

| | issue | why |
|---|---|---|
| **fixes** | #18489 | the issue it was filed against |
| **enables** | #17632 | supplies *which arrangement*; frame geometry supplies full vs half; the OSD compensation itself is still unwritten |
| **enables** | #18348 | supplies detection, but the complaint is the removed full-width `sbsl`/`abl` vocabulary, and the patch restores no modes |
| **untouched** | #18380 | decoding a second view, blocked in libavcodec — a different layer |
| **untouched** | #15225 | encode-side; follow-up #2 would be the relevant change and is unverified |

The distinction between *fixes* and *enables* is the whole point of
writing this down. It is obvious today and will not be in six months,
and the temptation to collapse the second row into the first is exactly
what a reviewer would catch. A claim of four issues that checks out as
one would confirm every prior about the contribution; "closes one issue
and is the missing input for a cluster stalled since 2024" survives any
amount of scrutiny.

## Who is actually affected

The 3D surface has few users filing bugs, and the same names keep
appearing:

- **netExtra** — filed #17632, 👍'd #18489, took part in #17547
- **44vince44** — filed #17547 (closed as a duplicate of #17632), the
  same OSD complaint reported independently
- **647k41** — filed #18380 (MVC)
- **Arcitec** — filed #15225 (encoding), and dug into the source himself
- **fakelok76** — the second 👍 on #18489

Five identifiable people, all currently unserved. Worth remembering when
the work feels like it is for two televisions.

## What we contributed, 2026-09-17/18

Neither comment mentions PR #18490. Both answer a blocker the other
person stated in their own thread, which is the only reason either was
worth posting.

**[#17632, comment 5723281678](https://github.com/mpv-player/mpv/issues/17632#issuecomment-5723281678)**
— answering kasper93's "I don't know how to detect if it's half sbs or
full sbs" with the measured table and the per-eye DAR formula.

**[#15225, comment 5723430394](https://github.com/mpv-player/mpv/issues/15225#issuecomment-5723430394)**
(2026-09-18T01:04:21Z) — answering Arcitec's plan to add a manual
`anamorphic=true` option to `format:stereo-in`. He had written, two years
earlier and independently of kasper93, "mpv's stereo3d flags currently
make no distinction between those". Same blocker, reached twice, by two
people who never spoke to each other. The comment removes a user-facing
option from his design instead of adding one.

That both of them hit the identical wall is the finding worth keeping.
The arrangement and the anamorphic question are two separate signals, and
because mpv reads neither from the stream today, everyone who needs them
concludes the user must be asked.

## Note on how to use this map

This is a campaign and has been from the start — the folder is named for
it. The question is never whether to coordinate, it is what each post
carries.

The rule we use: **substance, not volume.** Every comment answers
something the thread itself asked, with a number or a command the reader
can check, and it stands on its own without reference to our PR. By that
test #17632 and #15225 qualified and were posted; #18348 does not,
because it is already cross-referenced and we would be adding nothing;
#15225's *fix* claim does not, which is why the comment there addressed
only the anamorphic question and stayed silent about #18490.

What would break it is the opposite shape: cross-linked "see also"
comments, or asking the people in this list to back each other publicly.
That manufactures the appearance of support instead of supplying
evidence, and it is the one accusation that would be true and quotable.
The distinction is not presentational. A campaign of measurements is
engineering carried across several trackers; a campaign of volume is the
thing the AI-slop guidelines were written for.

## Related

- [README.md](README.md) — campaign status and the review-round record
- [mpv-sei-frequency-repro.md](mpv-sei-frequency-repro.md)
