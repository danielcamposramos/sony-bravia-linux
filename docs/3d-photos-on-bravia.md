# 3D photos on a BRAVIA — what Sony says, in five markets, and what the sets do

A focused research lane inside act three
([legacy-3d-formats.md](legacy-3d-formats.md)). The question is the one
a person actually types into a search box: **how do I view a
side-by-side or JPS 3D photo on my Sony BRAVIA 3D TV?**

It is asked in every market Sony sold these sets in, it has never had a
straight answer, and Sony's own support pages contradict each other
across regions and generations. Below is what the sets do here,
measured, and what the documentation claims, sourced.

## What our own sets do (owner-measured 2026-09-18)

Both sets. Not one, and not inferred from the other.

| Path | KDL-46EX725 (2011) | KDL-46HX855 (2012) |
|---|---|---|
| full-width SBS `.jpg` over DLNA | flat, no 3D | **same** |
| half-width (frame-compatible) SBS `.jpg` | flat, no 3D | **same** |
| anaglyph→SBS output `.jpg` | flat, no 3D | **same** |
| **MPO bytes renamed `.jpg`** over DLNA | **flat, no 3D** | **same** |
| 3D button with a photo on screen | menu opens — **only 2D→3D conversion** | **same** |

The MPO-renamed test is the sharpest of these, because the delivery was
verified before the test: Serviio served the file as `image/jpeg` with
`DLNA.ORG_PN=JPEG_LRG`, a profile the set advertises, at **byte-exact
size with the `MPF` APP2 segment intact**. So the set received a real
stereo pair and still showed one flat view. Either its decoder does not
inspect `MPF`, or it dispatches on something other than the content —
the file extension in the resource URL being the obvious candidate,
which is the one lead still untested.

**The decisive point is the menu.** There is no side-by-side entry for
stills at all, only the synthetic 2D→3D upconversion. A photo cannot be
told to unpack, so no packing and no naming can succeed on this path.

## What Sony says — and it does not agree with itself

**"Not supported at all."** Sony's own article, same number across
regions, states that 3D photos and films cannot be played from a USB
stick or the home network:
[DE 00129654](https://www.sony.de/electronics/support/articles/00129654),
[RU 00129654](https://www.sony.ru/electronics/support/articles/00129654).

**"MPO is the supported 3D photo format."** Other Sony pages describe
MPO (`.mpo`) as *the* 3D photo format for USB playback, with
per-model variation:
[RU S700023021](https://www.sony.ru/electronics/support/articles/S700023021),
[BR 00013979](https://www.sony.com.br/electronics/support/articles/00013979),
and the 2011-model USB compatibility charts
([MEA/AP 00180404](https://www.sony-mea.com/en/electronics/support/articles/00180404)).
The Japanese knowledge base has the most specific page of all, covering
exactly our generations:
[S1206199004299 — "which formats (extensions) does BRAVIA support over
USB? (2010–2012 models)"](https://knowledge.support.sony.jp/electronics/support/articles/S1206199004299).

**"Side-by-side is HDMI-only."** Sony customer care, relayed in the UK
community, says the side-by-side option is available only on an HDMI
input, and that early 3D sets could not play 3D video from USB at all:
[playing 3D movies from a USB stick](https://community.sony.co.uk/t5/other-tvs/playing-3d-movies-from-a-usb-stick/td-p/1506818).
This matches our measurement exactly, and it is the only one of the
three claims that does.

**"Not on Android TVs."** For the later generation Sony is explicit that
3D stills in `.mpo` cannot be viewed at all
([how to watch 3D on Android TV, 00172421](https://www.sony.co.uk/electronics/support/articles/00172421)),
and Italian owners report precisely that on newer hardware
([KD-65ZD9 does not read MPO](https://community.sony.it/t5/televisori/kd-65zd9-non-legge-immagini-3d-con-estensione-mpo/td-p/2534714)).
Italy also has the question asked in its purest form, as a support
article title: [*can my TV display "Side by side" and "Over under" 3D
content stored on a USB device?*](https://www.sony.it/electronics/support/articles/00069624)

**The community answer is a workaround, never a fix.** The recurring
advice across markets is to play the file from something else over
HDMI and let the TV's 3D menu unpack it there, or to rename JPS to JPG
and accept a flat 2D photo. The Sony US thread the owner archived is
titled, in its own words, *"is there any way to view 3D photos (JPS or
MPO) on a Sony BRAVIA"* — captured to the owner's private research
archive (Sony folder, HTML + PDF) rather than reproduced here.

## What this adds up to

**The capability was documented into existence and then never wired to
the photo path.** MPO is named as a supported format in Sony's own
compatibility material for 2010–2012 sets, including ours, while the
support article in two other languages says 3D stills do not play from
USB or the network at all, and the sets themselves offer no
side-by-side option for a photo in the 3D menu. All three statements
are Sony's. Only the third is testable here, and it is the one that
holds.

This is the same shape as the rest of this project, one layer further
in. The panel does stereo. The decoder can read the formats. **The
photo path was simply never connected to the 3D switch**, and the
documentation gap let that pass unnoticed for fifteen years in five
languages. Compare
[regional-documentation-asymmetry.md](regional-documentation-asymmetry.md)
— the pattern is not new, only newly pointed at photographs.

Worth keeping in proportion: stereo photography is not a modern
gimmick that the format war forgot. Wheatstone described the
stereoscope in 1838 and Daguerre announced photography in 1839, so
stereo is as old as the photograph itself. What broke is younger than
either.

## Still open, in order

1. **USB with a real `.MPO` extension.** Staged at
   `/mnt/arquivos/Fotos3D-USB/` — 11 `.MPO`, 11 original `.jps`,
   upper/lower-case probes, three JPEG controls. Sony's own 2011
   compatibility material claims MPO works over USB; the set has not
   been asked with the correct extension yet.
2. **The resource-URL extension hypothesis.** The DLNA test delivered
   correct MPO bytes under a `.jpg` URL. If the set dispatches on the
   URL's extension rather than the content, a `.mpo` resource URL might
   change the outcome — worth one probe through our own app, which
   controls its URLs completely, before concluding DLNA is closed.
3. **Pull the two WAF-blocked Sony pages by hand** (JP S1206199004299
   and 00180404) into the private archive. They are the closest thing
   to an authoritative format list for exactly these model years, and
   automated fetching is refused — deliberately not worked around.
