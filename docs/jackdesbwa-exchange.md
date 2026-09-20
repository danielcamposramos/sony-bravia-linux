# JackDesBwa's reply — what it settles and what it opens

**2026-09-20.** [PhereoRoll3D #2](https://github.com/JackDesBwa/PhereoRoll3D/issues/2)
was three questions: an offer to test StereoWebViewer's interleaved output on the
four 3D devices here, how to do better than grey when converting anaglyph back to a
pair, and which online galleries a viewer should target. All three are answered, by
the author of the code, and two of the answers change what we should build.

## Settled: do not run the interleaved test

The offer is declined, and correctly. StereoWebViewer is abandoned in favour of
[threejs-StereoscopicEffects](https://github.com/JackDesBwa/threejs-StereoscopicEffects),
which is what [Stereopix](https://stereopix.net) runs, and its interleaved modes are
therefore already exercised by real users. The "Not tested on actual device yet"
marker that prompted the offer is stale rather than open.

`PhotoRoll3D` is frozen too, with no plan to resume. Both corrections are now in
`awesome-stereoscopy`, where this list had been presenting an abandoned viewer as a
tool and a frozen rewrite as work in progress.

## He confirmed the finding that matters most to this project

On running any of these viewers on 2011 hardware:

> "I agree that all the programs you cited use too recent technologies to be run on a
> system designed in 2011."

A plain canvas 2D viewer could work for static images, and Stereopix carries such a
fallback, but he adds the sentence that closes the question:

> "it would probably not solve the problem of activating the 3D on the TV set anyway."

That is the whole argument for rendering server-side, stated independently by someone
with no stake in our conclusion. The set does not switch because a page asks it to; it
switches because the bitstream carries the signal.

## Opened: the gstreamer renderer

His suggestion, and it generalises our tool rather than duplicating it:

> "You could maybe create a tool which takes a video input through gstreamer and
> transforms it for the TV. I specifically suggest gstreamer because then the user
> could input many kind of sources like a regular file, a 3D webcam, a screen (or
> window) capture, a HDMI input device, etc."

The point is the input side. Our injector works on files that already exist. A
gstreamer front end would make **any application that can output side by side** usable
on these televisions: a game, a video call, a desktop capture, a 3D camera, an HDMI
capture device. The output half is what we already do, which is frame-pack and write
the SEI. GStreamer is also the one project in the whole survey that already writes the
SEI correctly on its own (`h264parse` to caps to `x264enc`), so the pieces meet.

Worth noting as scope: this is a live pipeline, not a remux, so it is a different
tool from `bravia_sei3d.py` and not a replacement for it.

## Anaglyph, beyond grey

He pointed at [a2sbs.py](https://gist.github.com/JackDesBwa/f86eb3fcdf3a0be1734bcdb4f535a52a)
and described the three tricks in it: rebuild chroma with an anisotropic blur, relying
on the eye tolerating low chroma resolution; recover better colour from the optical
flow where both views match, with a blur fallback where they do not (occlusion, edges)
which the script does not yet implement; and undo the anti-ghosting some creators burn
into an image before applying the anaglyph matrix.

That maps onto `tools/bravia_anaglyph.py`, which already found by measurement that a
pointwise operator cannot create disparity and that naive channel-borrowing makes the
two eyes identical. The optical-flow path is the direction his script points, and the
fallback he says is missing is exactly the case our corpus is full of.

Note for anyone reading his comment and the script together: the comment names
`-color_flow` and `-xtalk_delta`, the script has `-colors_flow` and `-ghosting_delta`.
Read the script.

## Dubois, in practice

We had asked whether a true Dubois conversion needs the panel's primaries and the
filters of the actual glasses. He confirms it does in principle, and that in practice
people apply the published matrices and rely on sRGB calibration. His own observation
is the useful part: he saw one screen go from "impossible to look at an anaglyph image"
to "depth is present with a bit of annoying remaining ghosting" purely from
calibration. So a calibration switch in a server-side renderer is worth having, for
users who have not applied their screen profile at the OS level, while accepting that
active glasses beat anaglyph on these sets anyway.

## Sources, and a correction to our own measurement

His map of what a gallery client should target: Phereo (more than 200,000 images, but
it lost everything published between roughly January 2019 and October 2022 and some
functions such as search are gone), Stereopix (more than 3,000, growing), Flickr
(large community, stereo groups, **the only one of these with a documented API**), and
the family of personal galleries exported by StereoPhoto Maker, which share a
structure because one tool generated them all.

On our measurement that `api.phereo.com` returned 504 twice at 60 s, he measured from
France and did not reproduce it:

| | time to first byte | download | total |
|---|---|---|---|
| Phereo, one image (1190x768) | 406 ms | 291 ms | 697 ms |
| Phereo, recent-images list | 182 ms | 315 ms | 497 ms |
| Stereopix, one image (7680x2160) | 90 ms | 73 ms | 163 ms |

Phereo is hosted in the eastern United States and Stereopix in Germany, which accounts
for some of the gap. Our 504 stands as what we measured from Brazil on that endpoint on
that day, and his numbers stand as what he measured from France on his. Both belong in
the record, and the honest summary is that Phereo is slow and lossy rather than dead.

## What this changes

- The interleaved-device test comes off the backlog. It was our only concrete
  contribution offer to this project, and it is not wanted because it is not needed.
- The gstreamer front end goes on the list as a real design, credited to him.
- The anaglyph work has a direction: optical flow with a blur fallback.
- Flickr moves to the front of any gallery work, because it is the only source with an
  API that will not move under us.


## Closed, 2026-09-20

Answered and closed as
[comment 5751443461](https://github.com/JackDesBwa/PhereoRoll3D/issues/2#issuecomment-5751443461),
in the owner's words. His opening line was feedback worth acting on, "Your messages
are quite dense, and I'm not sure to have understood everything", so the reply is
about a third the length of our earlier ones and says so.

The reply leads with his corrections to our list rather than with our own findings,
links the list with an open invitation to cite it, reports the MPO typing fix and the
four-way probe, credits his canvas-fallback sentence as the line that settled our
architecture question, and records the gstreamer suggestion as a design. His five
stereoscopy repositories and both gists were starred from the owner's account.

The owner's own edit changed the acceptance of the declined test from "I will not take
your time with the interleaved test" to "I will move the investigation up the ladder
you suggested as the projects that went on", which is the better sentence: it says
what happens next instead of only conceding.

**Open, not promised.** A friend of the owner has a Sony Android-era set from the
following generation. Those sets may not carry the same gates on the browser and the
photo viewer. It was deliberately left out of the reply, because it is a plan and not
a result; it goes upstream only when there is a measurement.
