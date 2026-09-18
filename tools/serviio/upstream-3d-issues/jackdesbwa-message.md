<!-- POSTED 2026-09-18 10:51 UTC by the owner as PhereoRoll3D issue #2,
     "Thank you! And some other things...":
     https://github.com/JackDesBwa/PhereoRoll3D/issues/2
     Watch: email trigger only (GitHub notifies the author) — never poll.
     If JackDesBwa answers, the owner pastes it and the reply is drafted
     together; a question from him needs the owner's own answer.
     What follows is the draft as prepared, kept for the record. -->

Hi JackDesBwa,

I went through PhereoRoll3D, PhotoRoll3D and StereoWebViewer while building a 3D photo gallery for a pair of 2011 Sony BRAVIA TVs, and I came out with one offer and two questions.

**The offer first, because it is the part that is useful to you.**
StereoWebViewer's README still says `interleaved (i) [Not tested on actual device yet]`.
I have the devices.
Two active-shutter 3D BRAVIAs, an LG Optimus 3D whose parallax barrier makes column-interleaved its native format, and a Gadmei T883-3D glasses-free tablet.
If that mode is still worth anything to you, or to the three.js viewer that replaced it, **I am happy to test it on all four and send you what I see**, photographs of the screens included.
It costs me an afternoon and you have been waiting on it since 2018.

**My half is video.**
These TVs auto-engage 3D from exactly one signal, the H.264 `frame_packing_arrangement` SEI.
They ignore the Matroska `stereo_mode` tag that every standard 3D rip carries.
So a correctly authored 3D file plays flat on perfectly good hardware, and that has been reported as a mystery across Plex, Jellyfin, Serviio and MakeMKV forums for a decade, with nobody naming the cause.

The cause is that **almost nothing on the software side ever wrote the flag the display was listening for**.
That part is mostly fixed now.
HandBrake merged writing the SEI (PR #8100), there is an mpv patch in review to read it, and the same finding went to Jellyfin, Universal Media Server and Gerbera.

**Your half is photos, and it is the same wall from the other side.**
The panel can show stereo, the stock software just never talks to it.
Sony's own photo slideshow on these 3D sets is 2D only, on a 3D panel, because the photo path was never wired to the 3D switch.
Your display modes are what that software should have been.

One thing I found while checking whether any of your viewers could run on the TV directly, in case it is useful to know.
None of them can, and the blocker is the same one every time: **StereoWebViewer needs WebGL, and the 2011 browser has none.**
The three.js viewer that succeeded it needs it twice over, and the Qt ones were never going to run there at all.
So the set has a working 3D panel that every stereo viewer ever written has been unable to reach, purely because they all assume a GPU the browser can talk to.
That is why I render server-side and send the TV a finished image.
It is your display modes, done one layer further back, for a client that cannot do them itself.

So I am building the gallery these sets never got, on two sources: my own library, and whichever community platform is actually answering.
Nothing reverse engineered, your code is the map, which brings me to the second question.
Your Dubois implementation sent me looking, and it turns out stock ffmpeg has carried the same conversion for years (`stereo3d=sbsl:arcd`), which saved me writing it.
What I still owe the old panels is the correction on top, since Dubois was solved for colorimetry a 2012 WLED does not have.

Alongside that I am taking the legacy formats seriously as their own lane.
Row-interleaved and line-interlaced content converted to SBS plus SEI, which is standard speaking to standard: **`frame_packing_arrangement` types 0, 1 and 2 are checkerboard, column-interleaved and row-interleaved**, so the legacy packings never actually left H.264.
And anaglyph in both directions, SBS to anaglyph for display, and the inverse back to SBS for material whose stereo original no longer exists anywhere.

**Now the two questions**, which I would rather ask someone with real years in stereo photography than guess at.

**1. Anaglyph back to SBS, in practice.**
The general problem is ill-posed, and the published disparity-aware methods are research grade.
My honest fallback is monochrome extraction, recovering both eyes' luminance and emitting a gray SBS, which is at least real stereo in the modern packing.
You have seen far more real community anaglyphs than I have.
Is there anything from the stereo photo world you would actually trust on real files, or is gray the honest ceiling?

**2. PhotoRoll3D's "more online sources", and where they are now.**
I read the repo, so I know the adapters are not written yet and the multi-source part is still the plan.
The plan is what interests me, because I think I know why you started it.

On 2026-09-18 I measured both hosts from here, twice, politely.
The phereo API path returned **504 after 60 seconds**, while its static assets and images answered fine in seconds.
**Stereopix answered in 2.5 seconds.**
So the pattern I read into your two repos is: you wrote a client for phereo, and then started rewriting it to not depend on phereo.

If that is right, you have already done the thinking I am about to do badly on my own.
**Which sources do you consider still reachable and worth an adapter today?**
Is stereopix the one you would build against, and does it expose an open API the way phereo's did?
I am deciding my own source list right now, and your map of that landscape is worth more than my guessing.

Everything on my side is public, if any of it is useful to you: https://github.com/danielcamposramos/sony-bravia-linux
The photo lane and the legacy format charter are in `docs/legacy-3d-formats.md`.

<!-- Notes for the owner, not for posting:
     - Mentioning "I followed you" is optional; it reads warmer in
       person than in text.
     - The phereo 504 is our own measurement, twice, and it is the
       one number in here that is ours. Re-check it before posting:
       if the API answers by then, cut that paragraph and ask
       question 2 without the diagnosis, because being wrong about
       someone's community in the first message is expensive.
     - The "you wrote a client for phereo, then started rewriting it
       to not depend on phereo" line is an inference, offered as one
       ("the pattern I read"). If he corrects it, that answer is
       worth more than the guess was.
     - Unverified and deliberately left as a question, not a claim:
       whether he is himself involved in stereopix. Asking is fine.
       Assuming would be embarrassing. -->
