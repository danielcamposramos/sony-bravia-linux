<!-- DRAFT — NOT POSTED. Prepared 2026-09-18, held for the owner's go.
     Target: JackDesBwa (author of PhereoRoll3D / PhotoRoll3D).
     Channel suggestion: GitHub issue on PhereoRoll3D is the natural
     public place — but see the note at the bottom before choosing.
     Doctrine: the owner reviews, rewords in his own voice, and posts;
     drafts are raw material. Factual and additive, no pitch; connect
     the work, ask the questions his experience can actually answer.
     No AI disclaimer (GitHub has no policy expecting one; the owner
     signs and owns every claim). Timing per act-three doctrine:
     ideally after the first measurements exist, so the message can
     link a working thing instead of a plan — but the owner decides. -->

Hi — I write as a long-time 3D user (the Optimus 3D / Gadmei /
anaglyph-gaming era, and the phereo community) who has spent the last
weeks fixing the *video* side of the 3D stack, and your two repos
kept coming up as the reference for the photo side. I followed you
here to say the connect out loud, and to ask two things only someone
with years in the stereo-photo community can answer.

What happened on our side: 2011-era Sony BRAVIA 3D TVs (and it turns
out most hardware 3D displays) auto-engage 3D from exactly one signal
— the H.264 frame_packing_arrangement SEI — and ignore the Matroska
stereo_mode tag that every standard rip carries, so 3D DLNA playback
silently fails on good hardware and has for a decade. We took the
diagnosis upstream through the whole chain: HandBrake merged writing
the SEI (PR #8100), there is an mpv patch to read it, and the DLNA
servers (Jellyfin, UMS, Gerbera) got the same finding. The pattern
that made me think of your work: the ecosystem failed not because 3D
was impossible, but because nobody wrote the flag the display was
listening for — which is exactly the wall your display-mode
implementation in PhereoRoll3D climbs from the other direction, for
photos: the panel can show stereo, the stock software just never
bothered to speak to it.

We are now building the photo lane on the same hardware: a 3D-photo
gallery the sets never got (Sony's stock slideshow ran 2D-only on a
3D panel). Server-rendered pages, two sources — the local library and
the phereo open API your MIT client documents — anaglyph Dubois done
server-side once for the whole room, your implementation as the
reference. And we are taking the legacy content seriously as its own
lane: row-interleaved and line-interlaced material converted to
SBS+SEI (the packing never left the H.264 standard —
frame_packing_arrangement types 0/1/2 are checkerboard, column- and
row-interleaved), and anaglyph in both directions — SBS to anaglyph
for display, and the inverse, anaglyph back to SBS, the modern
format, for material whose stereo source no longer exists anywhere.

The two questions:

1. Anaglyph → SBS extraction. The general problem is ill-posed, and
   the published disparity-aware methods are research-grade. But you
   have seen more real community anaglyphs than anyone — in practice,
   what actually works on real material: monochrome extraction and
   live with gray, palette/borrowed-color tricks, or is there a tool
   or approach from the stereo-photo world you would actually trust?

2. PhotoRoll3D's "more online sources". Your WIP names the idea —
   stereo content scattered across platforms that keep closing. Which
   sources do you see as still reachable and worth an adapter, beyond
   phereo? We are deciding what our gallery's source list should be,
   and your map of that landscape would steer it better than ours.

Everything on our side is public if useful:
https://github.com/danielcamposramos/sony-bravia-linux — the photo
lane and the legacy-format charter are in docs/legacy-3d-formats.md.

<!-- Channel note (for the owner, not for posting): a GitHub issue on
     PhereoRoll3D is public and durable, but check the repo for an
     issues-welcome signal first — its README is minimal (WIP), so if
     in doubt, a mention/email via the profile is the lower-noise
     route. Whichever channel: post only after rewording, per
     doctrine. -->