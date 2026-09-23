# JackDesBwa — follow-up comment on PhereoRoll3D #2 (correction + MPO finding)

Target: https://github.com/JackDesBwa/PhereoRoll3D/issues/2 (comment, owner posts
in his own words). No reply from him yet; this goes first because our first
message contains a claim the 2026-09-19 test proved wrong.

---

A correction to my first message, because I got something wrong and it touches your side.

I wrote that Sony's photo slideshow on these sets is 2D only because the photo path was never wired to the 3D switch.
**It is wired, for MPO, from USB.**
I tested it today on both sets: a correct MPO on a USB stick engages 3D by itself, no menu.

That was never settled, not even by Sony.
Its own support pages contradict each other by region: the German and Russian ones say 3D photos cannot play from USB at all, the Brazilian one says MPO is the format, with per-model variation.
The owner reports I found were Italian, on European firmware.
Nobody had shown it on the Brazilian firmware these two sets run (PKG2.120BRA and PKG4.027BRA).
Now it is measured there.

Every MPO I had tried before stayed flat, and the cause was my own writer.
It typed the first view as Baseline MP Primary Image (`0x030000`).
CIPA DC-007 §6.1 defines that as one photo plus preview thumbnails, not a stereo pair, so the TV did exactly the right thing and showed the first image in 2D.
With **both views typed Multi-frame Disparity (`0x020002`)**, numbered from the leftmost viewpoint, the same pixels come up in 3D.
If anything of yours writes MPO, that type field is the whole difference, and I did not find it stated plainly anywhere outside the spec.

What still does not work:
Over the home network the same file stays flat.
The TV's own DLNA declaration lists JPEG only, no MPO, and Serviio does not even index `.mpo` files.
Side-by-side JPEG and JPS stay flat on both paths.
So on these sets the only 3D photo format is MPO, and only from USB.
The hardware clearly can do it; the network path just never hands it over.

The interleaved test offer stands, and so do the two questions.
