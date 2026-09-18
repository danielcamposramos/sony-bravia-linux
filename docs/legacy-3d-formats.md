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

Steps 1 to 3 are one filter, not three, which is worth stating plainly
because it shrinks the lane. Verified on ffmpeg 9.0.1 (2026-09-18):
`stereo3d` reads the legacy packings directly (`in=irl` interleave
rows, `in=icl` interleave columns) and writes the modern one
(`out=sbsl`). So the conversion body is **`-vf stereo3d=irl:sbsl`**,
and act three's own code is only the packaging and the SEI around it.

**Honest scope, unlike acts one and two:** this is a *transcode* lane,
not a remux — the pixels genuinely change (that is what deinterleaving
is). Act one was signalling-only; act two was detection-only; act
three re-arranges pixels to move content between standardized
packings. The missing piece is packaging: a one-command "legacy-3D
modernizer" (legacy in, SBS + SEI out) — small, standard-based code
in this repo, on the same ethos as the 42-line mpv patch.

**Anaglyph runs in both directions (owner's call, 2026-09-18).**

The display direction, SBS in and anaglyph out for any screen with
glasses, is the practical one, and the reference code already exists.
PhereoRoll3D renders it client-side, and that MIT implementation is
the reference for our server-side chain.

**The inverse is the one the owner wants enabled too**: anaglyph in,
SBS out, the modern format. It splits into three honest sub-lanes:

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

One honest shortcut, for the community corpus specifically.
Those anaglyphs are *derived renditions*, so the SBS original exists
wherever the platform still stands, and "the inverse" there is
fetch-the-original, not extraction.

**Extraction is for the anaglyphs whose stereo source is gone**:
YouTube-era rips, scanned material, community anaglyphs whose pair
never survived, and, increasingly, files whose host went dark. That
is exactly the material this act exists for, and the phereo
measurement below is why the pile keeps growing.

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

**Correction, measured 2026-09-18: the Dubois half is already
shipped.** Stock ffmpeg's `stereo3d` filter carries Dubois anaglyph
as output modes (`arcd` red/cyan, `agmd` green/magenta, `aybd`
yellow/blue), and `arcd` is in fact its *default* output. Verified
on ffmpeg 9.0.1 here. So this lane does not have to implement Dubois
at all, and the reference implementations in JackDesBwa's clients
are confirmation rather than source material.

**What actually remains custom is the panel correction layer**, and
only that: Dubois was solved for a colorimetry that WLED does not
have, so the work is a per-panel adjustment (`colorchannelmixer`,
per-channel curves, `lut3d`) stacked *on top of* `arcd`, measured
against our own two sets. That is a much smaller and much more
honest piece of work than "build a Dubois chain".

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

## The 3D-photo lane — the gallery these sets never got

The community behind the corpus is **phereo** (phereo.com), the
stereo-photo sharing platform whose members' photos make up the test
archive above. It was described here at charter time as "still
active". **The measurements below say otherwise**, and that changed
this lane's design more than anything else in it.

One person, **JackDesBwa**, wrote most of the open-source tooling
that documents how to talk to that world, across four repos. Nothing
here is reverse-engineered; his code is the map:

- **[PhereoRoll3D](https://github.com/JackDesBwa/PhereoRoll3D)** (MIT,
  2018–2019, "Status: Working") — the phereo client: browse by
  category/user/album with search, comments, and 3D display modes
  including column-interleaved for autostereoscopic screens and — the
  detail that matters to act three — **anaglyph monochrome and
  anaglyph Dubois rendered client-side** from the SBS pair. The MIT
  source *is* the API map, and the Dubois conversion in it is
  reference code for our colorimetry chain.
- **[PhotoRoll3D](https://github.com/JackDesBwa/PhotoRoll3D)** — the
  same author's generalization, "stereo photo player inspired by
  PhereoRoll3D but for more online sources", still marked WIP.
  **Verified 2026-09-18 by reading it:** the multi-source part is the
  stated goal, not shipped code. The repo holds one commit ("Add base
  structure for the application"), a QML page shell plus an OpenGL
  shader renderer for the display modes, and **no source adapter at
  all**. Nothing to reuse yet beyond the structure, and PhereoRoll3D
  stays the only working API map.
  **But read it next to the section below and it stops being an idle
  generalization.** The author wrote a dedicated phereo client, and
  then started rewriting it to not depend on phereo. That is what a
  preservation response looks like from the client side, and it is
  the same move this lane makes from the TV side.
- **[StereoWebViewer](https://github.com/JackDesBwa/StereoWebViewer)**
  (MIT, 2018) — the same author again, and this time in a browser:
  a drop-in `<img data-swv-auto="1">` replacement that renders one
  SBS source into parallel, cross, **anaglyph (Dubois)**, interleaved,
  left-only or right-only, by keypress. Marked *proof of concept* and
  *abandoned* in favour of
  [threejs-StereoscopicEffects](https://github.com/JackDesBwa/threejs-StereoscopicEffects).
  Two things in it matter to us more than the code does:

  1. **It needs WebGL** (`canvas.getContext("webgl")`, GLSL vertex and
     fragment shaders), and so does its three.js successor. The 2011
     BRAVIA browser has no WebGL. **So even his *web* viewer cannot
     run on the set**, which closes the question below for good: not
     one of the four repos can render on this hardware, and that is
     precisely why our lane renders server-side.
  2. **`interleaved (i) [Not tested on actual device yet]`** — his
     own README, still unchanged. He wrote the output mode for
     autostereoscopic and passive panels and never had one to point
     at it. **The owner has four**: two active-shutter BRAVIAs, the
     parallax-barrier LG Optimus 3D (column-interleaved is its native
     format), and the glasses-free Gadmei T883-3D. That is a real
     contribution to offer, and it costs us one afternoon.

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

### Measured 2026-09-18: phereo is failing, and the successor is alive

Two hosts, same afternoon, same workstation, polite single requests.

| Host | Result |
|---|---|
| `phereo.com` static assets | **200**, seconds, nginx, http 301 → https |
| `api.phereo.com` API path | **504 gateway timeout at 60 s**, both attempts |
| `stereopix.net` | **200 in 2.5 s**, nginx, live site |

The reading at charter time was "the site is up, the backend is
struggling today".
That was too kind, and the owner's follow-up research says why.
Third-party reports going back years describe phereo as down, flaky
or abandoned: the [DPReview "Phereo website is down"
thread](https://www.dpreview.com/forums/threads/phereo-website-is-down.4483928/)
and the [photo-3d groups.io
topic](https://photo-3d.groups.io/g/main/topic/freevi_or_phereo_problem/34928125).
Those are reports, not our measurements, and they are cited as
reports. Our own number is the one that matters: **the API answers
nothing, for 60 seconds, twice.**

**[Stereopix](https://stereopix.net/) is the live one.** It serves
stereo photos in the same formats (`.mpo`, `.jps`), browses by
Highlights / Fresh / Random, still takes signups, and it answered in
2.5 seconds. Whether it has an open API like phereo's is **not yet
measured** and is the next thing to check before anything is built
against it.

**What this changes, concretely:**

1. **The corpus on the owner's disks stops being only test material.**
   If the platform that hosted it is dying, a private archive of
   community photos is preservation, held for study, still never
   republished. The provenance rule does not loosen because the
   source is failing. It matters more.
2. **The gallery is built source-agnostic from the first line.** No
   phereo-shaped code paths. A source is an adapter: list, page,
   fetch a rendition. Local library first because it cannot 504,
   then whichever remote source is actually answering.
3. **Nothing in this lane may depend on phereo being alive.** Cache
   what we fetch, degrade to the local library, and treat every
   remote source as temporary. That was already the defensive
   instruction. It is now the expected case.

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

### Does the set's Opera know what that software needs?

The owner's question, and it has a clean answer.

**The clients themselves: no, and not one of the four.** PhereoRoll3D
and PhotoRoll3D are compiled Qt/QML applications with an OpenGL
shader renderer, and the AppliCast browser has no plugin path and no
download path, which is this project's origin wall rather than a new
one. The interesting case is the web one, because it is the case that
should have worked: **StereoWebViewer is plain HTML and JavaScript
and still cannot run here, because it needs WebGL** and the era
browser has none. Its three.js successor needs WebGL twice over.

That is a clean finding rather than a disappointment. **Every viewer
this community built assumes a GPU the browser can reach.** Our sets
have the 3D panel and no such browser, so the panel has sat unused by
every one of these tools for fifteen years.

**But the set is never asked to.** The decisive fact is one layer
down: **the TV does not talk to phereo, or stereopix, or any modern
host at all.** Its browser speaks an era TLS stack that today's
certificates and ciphers already defeated, which is why this whole
project serves the TV from an era-TLS vhost on our own box. So the
TV talks to us, we talk to the internet, and every fetch is the
server's job by construction. The API proxy is not an optimization
here. It is the only way any of this reaches the panel.

That leaves a short list of what our own pages actually need from
the browser, and every item on it is already measured on these sets:

| Need | Status |
|---|---|
| render images | **measured** — the probe pages render them |
| paginate by plain links | **measured** — every live lane browses this way, no JS |
| the small inline JS our pages use | **measured** — key beacons and the native-controls player run on it |

Everything heavy in his clients, JSON parsing, Dubois pixel math,
shader display modes, happens **server-side** in our design, next to
ffmpeg.

Two things stay **unmeasured, and are deliberately not depended on**:
`JSON.parse` (probably native in the Presto lineage, but our pages
never call it) and large-image scaling on the panel (avoided by
requesting the `m`-size rendition rather than full). If client-side
rendering is ever wanted, those are one probe page on the EX725.

**The honest verdict: the TV does not know what Qt knows, and does
not need to. It knows everything our lane asks of it, and what it
does not know is the server's job.**

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

## The 3D catalog — the library has to know what it is serving

Conversion is half the charter.
The other half is the owner's, and it is the half everything else
waits on: **the serving side has to know the contents.**

The gap is narrower than it looks, because detection is not missing.
**It already exists here, and it is already running in the live
stack.** `ffmpeg-3d-wrapper.sh` decides on every Serviio transcode
whether the input is 3D, from filename tokens (`sbs`, `hsbs`,
`side-by-side`, `lado-a-lado`, `tb`, `tab`, `htb`, `top-bottom`,
`cima-e-baixo`, `[3D]`) and from `ffprobe -show_entries
stream_tags=stereo_mode`, then writes `--frame-packing` and logs why.

**The flaw is that the answer is thrown away.** It decides one file's
encode and forgets. Nothing accumulates, so nothing can be browsed.

That is the whole cataloger: **the same detection, lifted out of the
transcode path and written down.** Walk the library, type every file,
emit an index (JSON, keyed to the paths Serviio already serves):
item → type → evidence → confidence → owner override.

And what Serviio is missing is narrower than "no 3D concept", which
would be wrong. Serviio hands us enough to detect with, and our own
wrapper proves it. What its ContentDirectory has no notion of is a
**3D dimension to browse**: there is no node that means "all of it,
by type", so the content act three exists for stays scattered across
the folder tree that happens to hold it.

So the portal grows **an entire top-level 3D category**: *All 3D
photos*, *All 3D movies / series / videos*, each browsable by type.
The app already has the three parts this needs. `render_root()` draws
the root menu, `render_list()` already sorts items into `videoItem` /
`audioItem` / `imageItem`, and `render_image()` already displays
photos. The category is one more root row plus an index lookup at
list time.

| Flag | Photos | Video | Detection |
|---|---|---|---|
| `sbs` | squished SBS image, `_L`/`_R` pair | frame-compatible SBS | extension/naming + aspect heuristics; ffprobe `stereo_mode`; SEI side-data (act-one tooling) |
| `jps` | JPEG Stereo | — | extension (JPEG SOI + `.jps`, the community's native exchange format) |
| `mpo` | multi-picture object (Fuji W1/W3 lineage) | — | extension + MPO markers |
| `tab` | top-bottom image | frame-compatible TAB | aspect/naming; `stereo_mode`; SEI |
| `row`/`col` | interleaved legacy photos | row-interleaved legacy video (act three's type 2) | naming + measurement (odd/even row correlation); manual flag |
| `anaglyph` | color-multiplexed | anaglyph-encoded video | channel-correlation heuristic; **manual override always wins** |

**Honest scope on detection, per row.** `.jps` and `.mpo` are
certain from the file itself. SBS/TAB by tag and the SEI are certain,
and they are certain because act one built the tools that read them.
Interleaved and anaglyph detection are **heuristics and will be wrong
sometimes**, which is exactly why every entry carries an owner
override. A guess must never outvote the person who owns the content.

**The Serviio side of "both ends" needs no Serviio changes.** The
index enriches its browse results at the portal layer, keyed by path,
which is where we already reshape everything else the TV sees. The
deeper ask, native 3D metadata inside the servers themselves, is the
same finding already carried to Jellyfin, UMS and Gerbera in act two,
and it waits for the same reason as always: **results on our own
stack first, the upstream filing after the demonstration works.**

## The tools — built and measured 2026-09-18

Two tools, both in `tools/`, both with their numbers stated rather than
claimed.

### `bravia_3dcatalog.py` — the index

Detection lifted out of `ffmpeg-3d-wrapper.sh` and written down, exactly
as chartered. It walks the library, types every file, and emits one JSON
index keyed by path, with **evidence and confidence on every row**:
`certain` (the file declares it: `.jps`/`.mpo`, `stereo_mode`, an SEI, or
an owner override), `likely` (a filename token the wrapper already trusts
in production), `guess` (measured from pixels). An owner override always
wins, because a guess must never outvote the person who owns the content.

**First run on the corpus: 140 files scanned, 122 indexed — 81 anaglyph,
30 SBS, 11 JPS.** The anaglyph detector is a red-vs-cyan channel
decorrelation test, which is a guess by construction and labelled one.

### `bravia_anaglyph.py` — the inverse, and the end file

The owner's case for this is the whole point: **old anaglyph movies and
photos that survive only in that format**. There is no stereo original to
go back to, so either the anaglyph is converted or the content stays
locked to red/cyan glasses forever.

**What works, and the measurement behind it.** The stereo is recoverable
because the red channel carries the left eye and green/blue carry the
right. Reconstructing each eye *only* from the channels that carry it
recovers the true disparity **exactly on 11 of 11 corpus JPS pairs**
(+70/+70, +69/+69, +20/+21, −48/−48 …), with left-eye luminance at
23–37 dB PSNR against ground truth.

**Two traps, both hit and both measured, because they would have shipped
silently:**

1. **A pointwise operator cannot create disparity.** The first attempt
   fused the channels to recover colour properly, and it worked
   beautifully as colour — while measuring **0 px of disparity on every
   image**. Left and right differ by *where* content sits, and no
   function of a single pixel can move content sideways. A "reverse
   Dubois colour chain" that looks perfect can be a 2D photo.
2. **Naive channel-borrowing is the same trap wearing a disguise.** Left
   supplies 1 channel, right supplies 2, total 3. If both eyes are
   allowed all three, the two outputs are **byte-identical**. Colour
   without disparity-aware warping is not colour; it is a flat image.

**So the modes are honest about what they are.** `--mode mono` is the
default: both eyes greyscale, nothing invented, and robust on *any*
red/cyan anaglyph because the channel assignment is universal.
`--mode color` estimates a dense disparity map, warps the missing
channels across, and iterates to remove the right eye's own red from its
green (a 0.378 coefficient that contaminates the naive 2×2 inverse). It
**beats mono where matching is solid and loses on repetitive texture**,
which is the classic stereo-matching failure, so it is off by default.

**The caveat that matters most in the wild:** the round-trip test proves
the inverse against anaglyphs *we* encoded with Dubois. Found material
often is not Dubois at all — plain, optimised or half-colour red/cyan
were all common — and inverting the wrong matrix gives wrong colour.
Mono does not care. Colour does.

**The end file.** `bravia_anaglyph.py video in.mkv out.mkv` converts an
anaglyph movie to SBS and writes the frame-packing SEI (`x264
frame-packing=3`), verified present in the output. So the material that
only ever existed as anaglyph comes out the other side as a first-class
modern 3D file, on the same signal act one restored.

**And the campaign's own finding turned up inside our own tool.** ffmpeg
writes the SEI but does **not** derive the Matroska StereoMode tag from
it, so the output satisfies the TV and leaves software players blind —
the exact asymmetry this campaign documented, met from the other
direction. The tool now says so and prints the lossless `mkvmerge
--stereo-mode 0:1` fix-up, which is precisely what
[Codeberg #6309](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309)
asks mkvmerge to do automatically.

**On-the-fly.** `bravia_anaglyph.py filter` emits the whole reverse
chain as a pure ffmpeg filtergraph (`split` → two `colorchannelmixer` →
`hstack`), so the media app can convert per request through the ffmpeg
it already shells out to, and `server.py` stays stdlib-only.

### Staged and measured: the test set, and what reached the TV

The set is on the server at `/mnt/arquivos2/Fotos3D/`, added to Serviio
as an `IMAGE` shared folder ("Zion Fotos 3D") through the console REST
API — `GET`/`PUT` on `:23423/rest/repository`, config backed up first to
`~/serviio-backups/`. One practical note for anyone repeating it: a new
folder must be sent **without** an `id`. Supplying one returns `200` and
is silently ignored, which looks exactly like success.

Four folders, four separate experiments, built from the 11 ground-truth
JPS pairs plus five anaglyphs put through our own inverse:

| Folder | What | Why |
|---|---|---|
| `01-sbs-full` | full-width SBS `.jpg` | both views at native size |
| `02-sbs-half` | half-width (squished) SBS `.jpg` | frame-compatible shape, the one broadcast 3D used and the likeliest to auto-engage |
| `03-mpo` | two-view `.mpo` | the format Sony's own 3D cameras wrote |
| `04-de-anaglifo` | our anaglyph→SBS output, `.jpg` + `.mpo` | greyscale, honest mode |

**The measured outcome, after the scan:**

| On disk | Indexed by Serviio |
|---|---|
| 27 `.jpg` | **27 — all of them** |
| 16 `.mpo` | **0 — none** |

And Serviio does not even log a skip. The `.mpo` extension is not media
to it, so the files are simply invisible — the same failure the
extension survey predicted, now confirmed end to end on the live
server. **So the MPO half of the experiment cannot be run over DLNA at
all; it has to go to the set on a USB stick.** That is worth stating
plainly because MPO is the one format with a real chance of triggering
the set's own 3D-photo handling, and the network path silently cannot
carry it.

The `LEIA-ME.txt` beside the files carries the test procedure in
pt-BR, including which folders go over the network and which need the
pendrive.

### RESULT — owner-tested on the EX725, 2026-09-18 (DLNA photo path)

The inherited open test is answered, and the answer is more precise
than a yes or no.

| Tested over DLNA | Result |
|---|---|
| full-width SBS `.jpg` | opens **flat**, no 3D |
| half-width (frame-compatible) SBS `.jpg` | opens **flat**, no 3D |
| our anaglyph→SBS output `.jpg` | opens **flat**, no 3D |
| the 3D button, with a photo on screen | **menu opens** — but offers **only 2D→3D conversion** |

Two findings, and the second is the one that matters.

**First: the 3D menu is not blocked on the photo path.** That is a real
difference from the browser input, where the menu is blocked outright
([3d-blocked-in-browser.md](3d-blocked-in-browser.md)). The photo viewer
lets the menu open over the image.

**Second: the menu has no side-by-side entry for stills at all.** Only
the synthetic 2D→3D upconversion is offered. So this is not a case of
the set failing to *detect* a frame-packed photo — **the option to
unpack one does not exist in that menu**. No JPEG will ever become real
3D on this path, no matter how it is packed or named, because there is
nothing to select.

That also explains why full-width and half-width behaved identically:
aspect ratio was never a candidate trigger. And it is consistent with
the campaign's core finding rather than a departure from it. Video
auto-engages because the H.264 stream *declares* itself through the
frame-packing SEI. **Baseline JPEG has no equivalent declaration** — no
frame-packing field, no container stereo flag — so a SBS JPEG is a wide
2D photo as far as any conforming reader is concerned. The panel can do
it; nothing tells it to, and here nothing *can*.

**What is left, and it is a narrow door:** the set must recognise the
**file itself** as a stereo pair rather than be told what to do with a
flat one. Among still formats only MPO carries that declaration in a
standard, machine-readable way (CIPA DC-007, the Multi-frame Disparity
type code), which is exactly what Sony's own 3D cameras wrote for these
televisions. JPS is worth trying beside it purely because era firmware
sometimes knew the community formats.

Both need USB, because Serviio carries neither extension. The stick set
is staged at `/mnt/arquivos/Fotos3D-USB/` (28 files): 11 `.MPO`, the 11
original `.jps`, upper/lower-case extension probes for both — era
firmware is sometimes case-sensitive — and three plain-JPEG controls so
a blank listing can be told apart from a bad stick. `LEIA-ME.txt`
carries the procedure and what to note.

### Can Serviio be made to "see" these formats? Yes — by renaming, not converting

The owner's question, and his reasoning was the right one: *JPS is part
of the JPEG standard.* Close enough to be decisive. A `.jps` **is** a
valid JPEG whose stereo meaning rides in a standard `COM` marker (the
convention is the community's, the container is the standard's), and an
`.mpo` **is** a valid JPEG too — its first view is an ordinary JPEG
carrying an extra `APP2` segment. Neither needs a new decoder. **Only
the extension was ever in the way.**

Two things had to be checked before that could work.

**What the TV will accept at all.** From its own advertised
`GetProtocolInfo` (`docs/research/liverecon/ex725_GetProtocolInfo.xml`),
the EX725 offers exactly four image entries, all JPEG:
`image/jpeg:*`, plus `JPEG_LRG`, `JPEG_MED`, `JPEG_SM`. **There is no
MPO profile and no 3D image profile at all.** So no new MIME type will
ever reach this set over DLNA — but `image/jpeg` will, and MPO bytes
are legal JPEG bytes.

**An error in our own first staging.** Folders 01/02/04 were written
through PIL, which **re-encodes** and therefore strips exactly the
markers that carry the stereo meaning. Measured on the corpus: only
`curtin10.jps` of the eleven carries `_JPSJPS_` at all (the other ten
are plain JPEG bytes where the extension is the only signal), and our
re-encoded copies carried nothing. A test of re-encoded files could
never have answered the question.

So `05-renomeado/` holds **byte-identical copies with only the name
changed**: `MPORAW01..11.jpg` (MPO bytes) and `JPSRAW01..11.jpg` (JPS
bytes). Verified end to end from the workstation, before the set was
touched:

| Check | Result |
|---|---|
| Serviio indexes them | **yes, all 22** |
| served MIME / DLNA profile | `image/jpeg`, **`DLNA.ORG_PN=JPEG_LRG`** — a profile the EX725 advertises |
| delivered size | **1,129,097 bytes = the MPO exactly** — not re-encoded |
| `MPF` APP2 in the delivered bytes | **preserved** |

**So the answer to "can we make Serviio see and talk these formats" is
yes, and it needed no patch, no property and no new decoder.** The set
now receives a genuine stereo pair over the network, wearing a label it
accepts. The one thing still outside our control is whether its decoder
inspects the `MPF` segment when the MIME says JPEG. If it does, 3D
photos work over DLNA. If it does not, USB remains the only route, and
the stick set is already staged for that.

### Measured: Serviio will not index the corpus at all

Asked of the live server's own database, not assumed: the indexed
extensions are `.mp3 .jpg .flac .wma .mkv .avi .mp4 .m4a .flv .wav`.
**No `.jps`, no `.mpo`, not even `.png`.** So the stereo formats the
community actually exchanges are invisible to the DLNA layer — a
`.jps` is a JPEG that no library will admit is a JPEG, purely because
of its extension. For the native-photo 3D test on the set, the material
has to be handed over as `.jpg` (and `.mpo`, which is what Sony's own
3D cameras wrote), not as `.jps`.

## Ordering and doctrine

The owner's rule, same as every act of this campaign: **results on
our own stack first; upstream after, across the system where it
belongs** — ffmpeg filter chains, player-side conversion profiles,
DLNA transcode presets — once the conversion lane is measured and
produces a demonstration no one can argue with. No premature upstream
filings; bring the diagnosis + a working fix, in that order.

**Status: charter (2026-09-18). Prepared, and held for the owner's
go. Nothing is built yet.**

Nothing in this lane is measured beyond the facts above. First steps,
in the order they unblock each other:

1. **The 3D cataloger.** Lift the detection out of
   `ffmpeg-3d-wrapper.sh`, scan the photo corpus, emit the index.
   Photos first, because the corpus is a ready-made test bed that
   needs no encoding at all. Video after, on the SEI/tag tooling act
   one already built.
2. **The portal's 3D category**, browsing that index. *All 3D
   photos*, *All 3D movies / series / videos*, by-type views.
3. **Front B on one JPS pair.** Deinterleave → SBS → SEI → does the
   EX725 switch. One pair answers the whole conversion lane.
4. **The anaglyph color chain on one corpus photo.** Private test
   use, as always.
5. **The remote source, last and separately.** Check whether
   stereopix exposes an open API, re-check phereo from the LAN, and
   build against whichever answers. The gallery must already work
   on the local library before any of that.

Then, and only then, decide what becomes a tool and what goes
upstream.

## Related

- [3d-signalling-explainer.md](3d-signalling-explainer.md) — the two
  signals, short form
- [3d-signalling-ecosystem.md](3d-signalling-ecosystem.md) — acts one
  and two, the ecosystem map
- [3d-origin-story.md](3d-origin-story.md) — the iZ3D license and the
  road here
- `tools/bravia_sei3d.py` — the SEI injector act one built, reused as
  step 4 of the conversion pipeline