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

**Anaglyph runs in both directions (owner's call, 2026-09-18).**
The display direction — SBS in, anaglyph out for any screen with
glasses — is the practical one, and the reference code already exists
(PhereoRoll3D renders it client-side; the MIT implementation is the
reference for our server-side chain). The inverse — anaglyph in, SBS
out, the modern format — is what the owner wants enabled too, and it
splits into three honest sub-lanes:

1. **Monochrome extraction — well-posed.** Each eye's luminance
   survives the color multiplex; recover two grayscale views, emit a
   monochrome SBS. Not the original color, but real stereo in the
   modern packing.
2. **Re-color by borrowing — heuristic.** Borrow chroma from the
   anaglyph's own channels or a palette/reference; better than gray,
   never faithful. A refinement, not a promise.
3. **Disparity-aware reconstruction — research-grade.** Published
   methods recover color via depth-guided propagation; lossy,
   heavyweight, kept as the literature lane.

And one honest shortcut for the phereo corpus specifically: its
anaglyphs are *derived renditions* — the SBS original exists
server-side, so "the inverse" there is fetch-the-original, not
extraction. Extraction is for anaglyphs whose stereo source is gone:
YouTube-era rips, scanned comics, community anaglyphs with no pair
surviving. That is exactly the material this act exists for.

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

## Test material — the 3D-photography community corpus

`/media/Arquivos/Pictures/3D` (owner's private archive, not the repo):
140 files from 2010–2011 — **11 `.jps`** (JPEG Stereo, the
community's native stereo-pair exchange format), SBS PNG pairs, and a
full anaglyph set. **Provenance: these are NOT the owner's photos.**
They are shared material from the 3D-photography community — which
is still active — held in the archive for study and testing. They are
never republished by this project; test use only. What the owner
contributes is the hardware and the knowledge: two LG Optimus 3D
(P920) exemplars — the dual-5MP stereo camera of that generation,
and the actual glasses-free (parallax-barrier) display in this
lineage — plus years of hands-on depth on these formats. The corpus
is still the ideal first test: ground-truth SBS pairs with matching
anaglyphs for A/B-testing the colorimetry chain, and photos are the
cheapest place to prove both fronts before touching video.

## The YouTube 3D player — the platform-scale instance

The largest single corpus of legacy 3D is YouTube, and its history is
this project's pattern at platform scale:

- **~2009:** the YT3D player — a 3D dropdown with anaglyph, cross-eye
  side-by-side, row-interleaved, checkerboard, and NVIDIA 3D Vision
  output modes, driven by `yt3d:` tags.
- **2011:** standardized on frame-compatible squished SBS; full-res
  3D upload support dropped.
- **Oct 2014:** the HTML5 player switch silently removed the 3D
  options; ~2015–2016 the player decayed to anaglyph-only. No official
  announcement was ever made — users still note they cannot find one.
- **Today:** an SBS upload survives on the backend but is exposed
  only as anaglyph; the community workaround is to upload plain SBS
  "2D" video and let 3D hardware detect it natively — which is act
  one of this campaign, arrived at independently. YouTube's own upload
  guidance names our signals (Matroska `stereo_mode`, x264
  `--frame-packing 3`): the platform reads the SEI on ingest and then
  declines to show 3D.

The contrast with the sets this repo serves is worth stating: Sony
documented its end-of-service — five dated notices naming the models
([sony-end-of-service-statements.md](sony-end-of-service-statements.md)).
YouTube removed a working 3D capability without a word. The ecosystem
gap this campaign mapped was not only never fixed by the tools —
where it existed, it was silently withdrawn.

Contemporary record: the MTBS3D forum threads
([2011](https://www.mtbs3d.com/phpBB/viewtopic.php?f=3&t=12840),
[2014](https://www.mtbs3d.com/phpBB/viewtopic.php?t=20301)) and the
[2015 Stack Exchange question](https://webapps.stackexchange.com/questions/88182/what-happened-to-the-option-to-cross-your-eyes-whilst-watching-youtube)
that has no restore answer.

## The phereo lane — the portal gets a 3D-photo gallery

The community behind the corpus is **phereo** (phereo.com) — a
stereophoto sharing community, still active, whose members' photos
make up the test archive above. Two open-source clients by
JackDesBwa document how to talk to it, so nothing needs reversing:

- **[PhereoRoll3D](https://github.com/JackDesBwa/PhereoRoll3D)** (MIT,
  2018–2019, "Status: Working") — the phereo client: browse by
  category/user/album with search, comments, and 3D display modes
  including column-interleaved for autostereoscopic screens and — the
  detail that matters to act three — **anaglyph monochrome and
  anaglyph Dubois rendered client-side** from the SBS pair. The MIT
  source *is* the API map, and the Dubois conversion in it is
  reference code for our colorimetry chain.
- **[PhotoRoll3D](https://github.com/JackDesBwa/PhotoRoll3D)** — the
  same author's in-progress generalization ("stereo photo player
  inspired by PhereoRoll3D but for more online sources", WIP).
  **Verified 2026-09-18:** the "other sources" is the stated goal, not
  shipped code — the repo holds one commit ("Add base structure for
  the application"): a QML page shell plus an OpenGL shader renderer
  for the display modes, with no source adapter implemented. Nothing
  to reuse yet beyond the structure; PhereoRoll3D remains the only
  working API map. The multi-source idea itself is the valuable
  signal — it says the author already sees the same wall we do:
  stereo content scattered across dying or closed platforms.

**The open API, as documented by the MIT client** (no authentication,
JSON with `Accept: application/vnd.phereo.v3+json`):

| Call | Endpoint |
|---|---|
| photos by category | `api.phereo.com/api/open/<popular\|latest\|featured\|…>?offset=N&count=100&adultFilter=2` |
| user search | `api.phereo.com/api/open/search_users/?ss=<kw>&offset=0&count=500` |
| albums | `api.phereo.com/api/open/albums/?user=<id>&offset=0&count=500&adultFilter=2` |
| followed users | `api.phereo.com/api/open/userfollows/?id=<id>&offset=0&count=500` |
| comments | `api.phereo.com/images/<imgid>/comments?offset=0&count=100` |
| SBS rendition | `api.phereo.com/imagestore2/<id>/sidebyside/<l\|m>/` |
| thumbnail | `api.phereo.com/imagestore/<id>/thumb.square/280/` |
| avatar | `api.phereo.com/avatar/<uid>/100.100` |

**Measured status at charter time (2026-09-18):** the host answers
(nginx, http 301 → https); static assets over https return 200 in
seconds; the API path returned **504 (gateway timeout, 60 s)** on
both polite attempts from the workstation. The site is up, the
backend is struggling today. Re-verify from the LAN before building —
and build defensively: the portal lane must cache and tolerate the
API being slow or briefly down.

**The lane itself — the 3D photo player the set never got.** Sony's
own stock photo slideshow on these sets never touched the panel's 3D
capability: a 3D display with a 2D-only photo player, because the
photo path was never wired to the 3D switch. This lane is that
player, with **two sources on one server-rendered gallery**:

1. **Serviio (the owner's library)** — the UPnP ContentDirectory
   already serves `imageItem`s, browsed by the same pattern as the
   media lanes; the corpus above lives on the media disks, so it
   serves straight through. No new plumbing.
2. **phereo (the community)** — era-lean pages over the open API,
   images proxied through the app (browse client == fetch client).

Front A in its purest form: phereo serves the SBS pair, the glasses
render the 3D, **zero pixel conversion server-side** — the anaglyph
colorimetry chain later becomes the enhancement layer on top, doing
client-side-in-PhereoRoll3D's job once, server-side, for the whole
room. `adultFilter` stays on by default: it is a living-room set.
And the same lane gives the restored 3D phones/tablets a shared
target — the Gadmei and the Optimus are the community's own
hardware lineage.

**Does the set's Opera "know" what the phereo brother's software
needs? Measured answer.** The Qt/QML clients cannot run on the TV at
all — they are compiled OpenGL applications, not browser apps, and the
AppliCast browser input has no plugin or download path (that wall is
the project's origin story). But that was never the question that
matters: our lane *reimplements* what they do, and what the
reimplementation needs from the browser is already measured. The
server-rendered design needs exactly three client capabilities —
render images (measured: the probe pages validate this), paginate by
links (measured: every lane browses this way, no JS needed), and run
the small inline JS our pages already use (measured: the key beacons
and native-controls player run on it). The heavy parts of the MIT
clients — JSON API parsing, Dubois/anaglyph pixel math, shader-based
display modes — all happen **server-side** in our design, where
ffmpeg and the API proxy live. Two capabilities remain unmeasured and
are *deliberately not depended on*: `JSON.parse` (native in the
Presto lineage, but our pages never need it) and large-image scaling
(avoided by requesting the API's `m`-size renditions). If client-side
rendering is ever wanted, those become probe-page items — one page
on the EX725 answers both. The honest verdict: the TV does not know
what Qt knows, but it knows everything our lane asks of it, and
everything it doesn't is our server's job.

**One open test this lane inherits:** the sets' manual 3D menu is
blocked on the browser input
([3d-blocked-in-browser.md](3d-blocked-in-browser.md)) — but does
the *native* DLNA/USB photo path allow the 3D switch for an SBS
photo? Era marketing suggests these sets advertised 3D photo
playback; if the native player switches, front B for photos is
serve-SBS-and-the-set-does-it; if not, anaglyph front A carries
photos the same way it carries everything.

**The owner's device archives** (private, the hardware lineage this
lane serves): `/mnt/arquivos/Android/0 LG P920` — the Optimus 3D
phone archive (KDZ firmwares, root guides, XBSAVR3D, 36 files) — and
`/mnt/arquivos/Android/Gadmei T883-3D` — the glasses-free Gadmei
tablet archive: 2,989 files of custom ROMs, 3D players, boot-card
instructions, roots. Two more glasses-free displays in the lineage,
and two more communities' worth of preservation work this project's
method applies to.

## The 3D catalog — the library has to *know* what's 3D (owner's framing: both ends)

Conversion is half the charter; the other half is that **the serving
side must know the contents**. Nothing in the chain carries the
knowledge today: Serviio's ContentDirectory has no 3D concept, photos
disclose their packing only by extension at best, and the video
stereo signal lives where act one found it — in-band (SEI) or in the
container tag a DLNA remux strips. A library that cannot say "this is
3D" cannot serve a 3D category, cannot route anaglyphs to the
colorimetry chain, and cannot queue row-interleaved material for
front-B conversion. So act three gets a catalog:

**A scanner ("3D cataloger") walks the library and emits a 3D index**
(JSON manifest, keyed to the same paths Serviio serves): item →
type → detection evidence → confidence → owner override. Then the
portal gains **an entire top-level 3D category** — *All 3D photos*,
*All 3D movies/series/videos* — each browsable by type, so the
content this act exists for is one click from the couch, not
archaeology in the folder tree.

| Flag | Photos | Video | Detection |
|---|---|---|---|
| `sbs` | squished SBS image, `_L`/`_R` pair | frame-compatible SBS | extension/naming + aspect heuristics; ffprobe `stereo_mode`; SEI side-data (act-one tooling) |
| `jps` | JPEG Stereo | — | extension (JPEG SOI + `.jps`, the community's native exchange format) |
| `mpo` | multi-picture object (Fuji W1/W3 lineage) | — | extension + MPO markers |
| `tab` | top-bottom image | frame-compatible TAB | aspect/naming; `stereo_mode`; SEI |
| `row`/`col` | interleaved legacy photos | row-interleaved legacy video (act three's type 2) | naming + measurement (odd/even row correlation); manual flag |
| `anaglyph` | color-multiplexed | anaglyph-encoded video | channel-correlation heuristic; **manual override always wins** |

Honest scope on detection: `jps`/`mpo` are certain from the file
itself; SBS/TAB and the SEI are certain from tools we already built;
interleaved and anaglyph detection are heuristics, which is why the
index carries an owner-override flag — a wrong guess must never
outvote the person who owns the content. And the Serviio side of
"both ends": the index enriches Serviio's existing browse results at
the portal layer, keyed by path, requiring zero changes to Serviio
itself; the deeper ask — native 3D metadata in the servers — is the
same finding we already carried to Jellyfin, UMS and Gerbera in act
two, and follows the same doctrine: results on our stack first, the
upstream filing after the demonstration works.

## Ordering and doctrine

The owner's rule, same as every act of this campaign: **results on
our own stack first; upstream after, across the system where it
belongs** — ffmpeg filter chains, player-side conversion profiles,
DLNA transcode presets — once the conversion lane is measured and
produces a demonstration no one can argue with. No premature upstream
filings; bring the diagnosis + a working fix, in that order.

**Status: charter (2026-09-18), prepared and held for the owner's go
— nothing built yet.** Nothing in this lane is measured yet beyond
the campaign-era facts above. First steps, in order: **the 3D
cataloger** (scan the photo corpus → type the flags → emit the
index; photos first because the corpus is the ready-made test bed,
then videos on the SEI/tag tooling act one already built), **the
portal's 3D category** browsing that index (*All 3D photos*, *All 3D
movies/series/videos*, by-type views), then prove front B on one JPS
pair (deinterleave → SBS → SEI → the EX725 switches), then the
anaglyph color chain on one corpus photo (private test use), then
the phereo gallery lane (re-verify the API from the LAN first), then
decide what becomes a tool and what goes upstream.

## Related

- [3d-signalling-explainer.md](3d-signalling-explainer.md) — the two
  signals, short form
- [3d-signalling-ecosystem.md](3d-signalling-ecosystem.md) — acts one
  and two, the ecosystem map
- [3d-origin-story.md](3d-origin-story.md) — the iZ3D license and the
  road here
- `tools/bravia_sei3d.py` — the SEI injector act one built, reused as
  step 4 of the conversion pipeline