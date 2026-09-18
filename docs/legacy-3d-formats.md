# Legacy 3D formats — the enablement umbrella (act three)

The 3D-signalling campaign has two completed acts. **Act one: the
signalling itself** — the H.264 frame-packing SEI was missing from the
encode → remux → player chain, and now HandBrake writes it, mpv has a
patch to read it, and the gap is mapped
([3d-signalling-explainer.md](3d-signalling-explainer.md),
[3d-signalling-ecosystem.md](3d-signalling-ecosystem.md)). **Act two:
the serving side** — the DLNA servers that strip the container tag got
the same finding (Jellyfin, UMS, Gerbera). Act three is the content
itself: the 3D material made before and beside the SBS/TAB era, in
formats nothing modern signals for. The umbrella goal is the owner's
phrase: **enable all 3D content ever made, on modern displays.**

## The legacy formats never left the standard

The frame-packing SEI that act one restored carries the legacy formats
as first-class vocabulary. `frame_packing_arrangement_type` (H.264
Annex D):

| Type | Arrangement | Era use |
|---|---|---|
| 0 | checkerboard | DLP rear-projection 3D TVs |
| 1 | column interleaved | early interlaced displays |
| 2 | **row interleaved** (line-interlaced) | polarized CRT overlays, FPR passive panels |
| 3 | side by side | frame-compatible broadcast, our sets |
| 4 | top and bottom | frame-compatible broadcast, our sets |
| 5 | temporal interleaving (alternating fields) | field-sequential shutter systems |

Type 2 is the standard, not a hack: row-interleaved 3D is
standardized packing, merely unwritten by modern encoders — the same
"the signal exists, nobody writes it" shape as act one. And the
format is not dead: every passive-polarized 3D monitor (FPR) is
row-interleaved *at the panel level* today.

**Anaglyph is a different class.** It packs nothing — the two views
are multiplexed into the color channels, so it is outside the SEI's
scope by design. It is a colorimetry problem, which makes it the
sibling of the iZ3D's best-known flaw (below), and it is the one
legacy format that plays on *any* modern display unchanged, because
the 3D is in the pixels and the glasses are the display.

## Two fronts (owner's framing)

**Front A — play as-is on modern outputs (live remux).** Serve the
content with zero or minimal pixel processing. Anaglyph is the poster
child: it plays flat as ordinary 2D and the glasses do the work; the
improvement lane is *display-side color conditioning*, not
conversion. Row-interleaved content can play as-is only on displays
with a matching native mode (passive FPR monitors); our active-shutter
BRAVIAs cannot accept it over HDMI, which is why front B exists.

**Front B — convert to the modern format (SBS + SEI). The proper
path (owner's call).** One conversion and the content becomes a
first-class citizen everywhere: every player, every DLNA server, every
hardware 3D display — the same standard every act-one file already
speaks. The pipeline is clean and every component already exists:

1. deinterleave: extract odd/even rows into two half-height views
   (stock ffmpeg `stereo3d` filter, `irl` input format; `icl` for
   columns, checkerboard similarly);
2. rescale each view to full height;
3. repack side-by-side (`sbs` output);
4. encode with the SEI written: `x264 --frame-packing 3`, or
   HandBrake (merged, act one), or inject with
   `bravia_sei3d.py` after a plain encode.

**Honest scope, unlike acts one and two:** this is a *transcode* lane,
not a remux — the pixels genuinely change (that is what deinterleaving
is). Act one was signalling-only; act two was detection-only; act
three re-arranges pixels to move content between standardized
packings. The missing piece is packaging: a one-command "legacy-3D
modernizer" (legacy in, SBS + SEI out) — small, standard-based code
in this repo, on the same ethos as the 42-line mpv patch.

**Anaglyph's front B — extraction to true stereo — is parked.**
Recovering two full-color views from two color channels is
ill-posed; disparity-aware methods exist in the literature but are
research-grade and lossy. Not promised. Front A (colorimetry) is the
practical anaglyph lane.

## The anaglyph colorimetry lane

Classic anaglyph was tuned for CRT phosphors. A modern WLED panel's
spectral response shifts the red/cyan channel overlap, and the
symptom is ghosting — the same failure class the iZ3D monitor was
reviewed for, where RGB rotated polarization differently and the fix
was better glasses. The software descendant of that fix: a per-channel
filter chain (gain/gamma per channel, Dubois-style optimization)
computed for the *target panel* instead of a 1998 tube, carried by
stock ffmpeg (`colorchannelmixer`, per-channel curves/`lut3d`), and
packaged as ordinary video. The owner's formulation is the charter:
clever color filtering plus color adjustment plus clever packaging —
the old result, on a modern display, possibly better than it ever
looked new.

## The iZ3D sidebar (verified 2026-09-18)

The origin of this project's 3D thread
([3d-origin-story.md](3d-origin-story.md)) was an iZ3D license key
earned from the developers. The hardware, confirmed from the
contemporary reviews:

- 22" widescreen (1680×1050), dual stacked LCD panels — rear matrix
  carries intensity, front matrix carries polarization — passive
  polarized glasses, lightweight enough that they were the praised
  part ([Ubergizmo, Mar 2008](https://www.ubergizmo.com/2008/03/iz3d-22-lcd-monitor-review/));
  demonstrated at CES 2008 with Unreal Tournament 3
  ([Ars Technica](https://arstechnica.com/gaming/2008/01/ces-eyes-on-with-the-iz3d-monitor/)).
  **Not glassless** — the glasses-free display in this story is the
  LG Optimus 3D (below).
- Vendor-neutral for its era: worked on AMD and NVIDIA alike, when
  the shutter-glass ecosystems were locking to GPU vendors
  ([PC Perspective, Oct 2008](https://pcper.com/2008/10/2-matrices-equals-3-dimensions/)).
- The recurring criticism: crosstalk/ghosting and muddy color, caused
  by RGB colors rotating polarization differently, eye strain in long
  sessions, dull 2D-mode color
  ([Digital Reviews Network](https://www.digitalreviews.net/reviews/reviews-archives/iz3d-gaming-monitor-reviewed/));
  addressed in 2009 with redesigned glasses
  ([MTBS3D](https://www.mtbs3d.com/articles/editorial/2868-new-iz3d-glasses-preview.html)).

## Test material — the owner's stereo corpus

`/media/Arquivos/Pictures/3D` (owner's archive, not the repo): 140
files from 2010–2011. **11 `.jps`** — JPEG Stereo, the native
stereo-pair format of that camera generation — plus SBS PNG pairs and
a full anaglyph set. Provenance is mixed: the owner's own photos and
period-collected samples; **public work uses the owner's own photos
only.**

The camera origin is the **LG Optimus 3D (P920, 2011)** — dual 5MP
stereoscopic cameras, and a glasses-free parallax-barrier screen: the
actual autostereoscopic display in this lineage. The owner has two
exemplars. The corpus is the ideal first test for this lane: small,
own-copyright, ground-truth SBS pairs (JPS/`stereo3d` decode) with
matching anaglyphs for A/B-testing the colorimetry chain — and photos
are the cheapest place to prove both fronts before touching video.

## Ordering and doctrine

The owner's rule, same as every act of this campaign: **results on
our own stack first; upstream after, across the system where it
belongs** — ffmpeg filter chains, player-side conversion profiles,
DLNA transcode presets — once the conversion lane is measured and
produces a demonstration no one can argue with. No premature upstream
filings; bring the diagnosis + a working fix, in that order.

**Status: charter (2026-09-18).** Nothing in this lane is measured
yet beyond the campaign-era facts above. First steps, in order:
prove front B on one JPS pair (deinterleave → SBS → SEI → the EX725
switches), then prove the anaglyph color chain on one owner photo,
then decide what becomes a tool.

## Related

- [3d-signalling-explainer.md](3d-signalling-explainer.md) — the two
  signals, short form
- [3d-signalling-ecosystem.md](3d-signalling-ecosystem.md) — acts one
  and two, the ecosystem map
- [3d-origin-story.md](3d-origin-story.md) — the iZ3D license and the
  road here
- `tools/bravia_sei3d.py` — the SEI injector act one built, reused as
  step 4 of the conversion pipeline