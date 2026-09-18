# sony-bravia-linux

Reverse-engineering and software porting for **Sony BRAVIA KDL-era TVs** — the
pre-Android, Linux-based BRAVIA platform (~2005–2015). Goal: understand the
platform well enough to run third-party software on it (e.g. VLC) and unlock
more internet content than the stock firmware allows.

**In your language** — the problem and the fix, for owners searching in their own words:
[日本語 · ブラビア 3Dテレビで3D映像・3D写真をもう一度](docs/i18n/ja.md) ·
[繁體中文 · BRAVIA 3D 電視重新播放 3D 影片與照片](docs/i18n/zh-TW.md) ·
[한국어 · 브라비아 3D TV에서 3D 영상과 사진 다시 보기](docs/i18n/ko.md) ·
[Deutsch · 3D-Filme und 3D-Fotos wieder abspielen](docs/i18n/de.md) ·
[Français · relire les films et photos 3D](docs/i18n/fr.md) ·
[Italiano · rivedere film e foto 3D](docs/i18n/it.md) ·
[Español · volver a ver películas y fotos 3D](docs/i18n/es.md) ·
[Português (BR) · assistir de novo a filmes e fotos 3D](docs/i18n/pt-BR.md) ·
[Русский · снова смотреть 3D-фильмы и 3D-фото](docs/i18n/ru.md) ·
[Polski · znowu oglądaj filmy i zdjęcia 3D](docs/i18n/pl.md) ·
[Nederlands · weer 3D-films en 3D-foto's afspelen](docs/i18n/nl.md)

**If you searched for** *"Sony Bravia 3D side by side USB not working"*,
*"3D mode in Sony Bravia"*, *"Bravia 3D photos MPO USB"*, *"is 3D only via
HDMI?"* or *"how to view JPS on a Sony 3D TV"*: the video answer is the
[3D signalling explainer](docs/3d-signalling-explainer.md), the photo answer
is [3D photos on a BRAVIA](docs/3d-photos-on-bravia.md).

## What's working today

**The full media experience is live and owner-verified on both TVs (through
2026-09-18):**

- Both sets browse the whole Serviio library on the LAN and play every audio
  format in it (native + live transcode) and every major video format, with
  Dolby AC-3/E-AC3 bit-exact through the sets' own decoders.
- The player is the set's **own native transport**, enlarged ~3x for couch
  distance, with cover art, prev/next, cookie-persisted repeat, and a `/manual`
  page on the TV in the user's language. The era platform's input and render
  rules behind that design are measured, not guessed:
  [era-key-vocabulary.md](docs/era-key-vocabulary.md),
  [era-media-element.md](docs/era-media-element.md).
- The TV's start page (`rd1.sony.net`) is served from our own box, and the
  withheld regional widgets are restored to the gallery from the owner's
  signed bundles.
- Everything runs as systemd services with a config file —
  **"VLC on a 2011 TV" is reached.**
- **The whole method is published** for anyone with one of these sets:
  [build-your-own-bravia-portal.md](docs/build-your-own-bravia-portal.md) —
  two DNS overrides, the era-TLS vhost, the media app, the widget-restore
  catalog edit, and every platform gotcha we hit.

The single partner entry point, kept current, is
[docs/project-status.md](docs/project-status.md) — read it first.

## Repository scope — what is and isn't here

This public repo contains **only our own work**: research notes, protocol
captures from our own TVs, analysis, and tooling (the Serviio 3D fix, SEI
injector, ffmpeg wrapper). **No Sony-distributed material is hosted here** —
no firmware images, service manuals, widget packages, or Sony-server
sweeps. Those resources were gathered for research and are kept offline by
the owner; the right-to-repair plan for that material is in
[docs/right-to-repair.md](docs/right-to-repair.md). Some older research
notes may still reference those filenames — they refer to the owner's
offline archive, not to anything in this repository.

## Why bother (the right-to-repair angle)

These late-KDL sets are phenomenal hardware — the KDL-46HX855 has
X-Reality PRO with 12-bit color processing and active 3D, and picture
quality that still embarrasses many modern budget panels. Sony EOL'd the
platform: smart services shut down (five dated end-of-service notices name
both of our models — [the archive](docs/sony-end-of-service-statements.md)),
firmware downloads removed, even the GPL source downloads were deleted from
Sony's site. The owner is now the only party with any incentive to keep
this hardware alive. This project is right-to-repair work: document,
control, and eventually run owner-chosen software on owner-owned hardware.
See [docs/right-to-repair.md](docs/right-to-repair.md) (includes the Louis
Rossmann / repair.wiki / FULU Foundation sharing plan) and the
consumer-rights documentation
([legal analysis](docs/legal-eula-analysis.md),
[regional asymmetry](docs/regional-documentation-asymmetry.md)).

## The 3D-signalling campaign

These sets auto-engage 3D from exactly one signal — the H.264
frame-packing SEI (payload 45) — and ignore the Matroska StereoMode tag
every standard rip carries, so 3D DLNA playback silently fails on
perfectly good hardware. The diagnosis plus a working fix was taken
upstream to every tool in the encode → remux → player pipeline, and then
to the DLNA servers that serve the files. Full drafts, per-target status,
and links live in
[tools/serviio/upstream-3d-issues/](tools/serviio/upstream-3d-issues/);
the ecosystem evidence base (DVB mandate with honest scope, a decade of
symptom threads, cross-brand survey, timed video citations) is
[docs/3d-signalling-ecosystem.md](docs/3d-signalling-ecosystem.md); the
short form linked in every upstream post is
[docs/3d-signalling-explainer.md](docs/3d-signalling-explainer.md).

| Front | Outcome |
|---|---|
| HandBrake | **[PR #8100 merged](https://github.com/HandBrake/HandBrake/pull/8100)** (2026-09-16) — encoder now writes the missing SEI; closes their #5826 |
| FFmpeg | [bug #24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530) + [enhancement #24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531) filed |
| StaxRip | [answered stranded user on #1873](https://github.com/staxrip/staxrip/issues/1873#issuecomment-5685902578) |
| x265 | [issue #970](https://github.com/Multicorewareinc/x265/issues/970) filed |
| mpv | [issue #18489](https://github.com/mpv-player/mpv/issues/18489) + [PR #18490](https://github.com/mpv-player/mpv/pull/18490) in review — completes the pipeline end to end; ecosystem follow-up posted on the issue |
| BD3D2MK3D (r0lZ) | [videohelp thread](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803756) — answered, closed out, cross-brand confirmed (Samsung) |
| mkvmerge | [Codeberg #6309](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309) **filed 2026-09-18** — derive stereo mode from the SEI; the earlier "signup paywall" was the donate page wearing the same layout |
| Kodi | [issue #29337](https://github.com/xbmc/xbmc/issues/29337) — first version was wrong (Kodi's player *does* read the SEI) and was corrected in place; now reports the DLNA side, the only side these TVs see: every MP4 advertised as MPEG-4 Part 2 (`MPEG4_P2_SP_AAC`), SEI served byte-exact |
| Jellyfin | [comment on PR #18060](https://github.com/jellyfin/jellyfin/pull/18060#issuecomment-5726381078) (layout-detection point) |
| Universal Media Server | [issue #6329](https://github.com/UniversalMediaServer/UniversalMediaServer/issues/6329) filed |
| Gerbera | [issue #3937](https://github.com/gerbera/gerbera/issues/3937) filed — the no-remux SEI-injection step |
| LTT forums | two audience posts: [3D-theater guide](https://linustechtips.com/topic/1589907-i-built-a-3d-theater-in-my-basement/?do=findComment&comment=16936161) + [Steam Frame cross-comment](https://linustechtips.com/topic/1642726-the-steam-frame-changes-everything-full-review/?do=findComment&comment=16936512) |

No DRM or copy-protection mechanism is involved anywhere in the chain.

**Act three is the legacy formats**, chartered in
[docs/legacy-3d-formats.md](docs/legacy-3d-formats.md): row-interleaved,
checkerboard and anaglyph material, on the goal of enabling *all* 3D
content ever made rather than only the well-signalled rest. Those
packings never left the standard (`frame_packing_arrangement` types 0,
1 and 2), so conversion to SBS+SEI is standard speaking to standard,
and stock ffmpeg already carries both the conversion and Dubois
anaglyph. Two additions the owner set in 2026-09-18:

- **the library has to know what it is serving** — a 3D cataloger
  lifting the detection our live transcode wrapper already performs,
  writing it to an index, and giving the portal **an entire 3D
  category** (*All 3D photos*, *All 3D movies / series / videos*);
- **the 3D-photo gallery these sets never got** — Sony shipped a
  2D-only slideshow on a 3D panel. Measured on the way in: the phereo
  community platform's API times out while
  [stereopix](https://stereopix.net/) answers in seconds, so the lane
  is built source-agnostic and the private photo corpus is
  preservation material, not just test material.

First results on the owner's own stack, before any upstream ask, as
in both earlier acts.
The episode's authorship-politics record — who gated on what, and the
42-line standard-based patch at the center of it — is
[docs/judging-by-the-cover.md](docs/judging-by-the-cover.md).

## Test hardware (both on the LAN, DHCP-pinned by MAC)

| Model | Year | Chassis | LAN IP |
|---|---|---|---|
| KDL-46HX855 | 2012 | AZ3F (main SoC codename "ATREYU") | 192.168.0.21 |
| KDL-46EX725 | 2011 | AZ2-F ("BATV" board) | 192.168.0.22 |

## Hardware this applies to

**Verified by us** — every claim in this repository was tested on those
two sets.

**Same board family**, attested by board census in
[platform-map.md](docs/platform-map.md) but not tested here:
KDL-46EX724, KDL-40HX853, KDL-55HX753.

**Generation coverage — this is the real scope.** Sony distributed
these widgets **per chassis generation, not per model**. Their own CDN
layout says so: the catalogs live at
`/WidgetContents/SNY_WidgetGallery/{AZ1,AZ2,AZ3}/…`, one set of bundles
per generation, and nothing in `info.xml` or the bundle manifests
restricts a widget to a particular model. Every AZ2 set received the
same files as our EX725; every AZ3 set received the same files as our
HX855.

| Generation | Year | Covers |
|---|---|---|
| `AZ1` | 2010 | the earlier line — its `/WidgetCatalogs/AZ1_*` tree still answers, in 24 languages |
| `AZ2` | 2011 | EX/CX/NX/HX 2011 sets — our EX725's generation |
| `AZ3` | 2012 | HX/EX 2012 sets — our HX855's generation |

We happen to own two sets; the work applies to three generations of
them. What we can state as *tested* is two models — what we can state
as *distributed identically by Sony* is every set in those generations.
Reports from other models are welcome and will sharpen this table.

**Also mapped, same repo:** the `SNY_AudioControlApp` widget speaks 26
Sony vendor HDMI-CEC opcodes and carries Sony's own compatibility table
for **81 Sony audio products** (sound bases, soundbars, receivers, ES
line). We have verified none of them — no Sony audio system is on the
test LAN — but the opcode set and the full model table are documented
in [hdmi-cec-audio-system.md](docs/hdmi-cec-audio-system.md).

## Live fronts and archive snapshots

Sony's own servers still serve this platform's material in 2026 — what
was switched off was the catalog layer that told the TVs it exists, not
the files. Every front below is also snapshotted at the Internet
Archive, so the evidence survives even if Sony withdraws it. (Archive
links must use `https://` — the `http://` form returns 503.)

| Front | Live (2026-09) | Internet Archive snapshot |
|---|---|---|
| AppliCast catalog, AZ3, EU region — 8 apps | [Catalog_EU_ALL_eng.xml](https://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_EU_ALL_eng.xml) | [2026-09-17](https://web.archive.org/web/20260917210301/https://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_EU_ALL_eng.xml) |
| AppliCast catalog, AZ3, Brazil region — 2 apps | [Catalog_LA_BRA_por.xml](https://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_LA_BRA_por.xml) | [2026-09-17](https://web.archive.org/web/20260917204700/https://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_LA_BRA_por.xml) |
| AppliCast catalog, AZ1 (2010 generation) | [AZ1_EU_ALL_eng.xml](https://applicast.ga.sony.net/WidgetCatalogs/AZ1_EU_ALL_eng.xml) | [2026-09-17](https://web.archive.org/web/20260917210817/https://applicast.ga.sony.net/WidgetCatalogs/AZ1_EU_ALL_eng.xml) |
| Calculator widget manifest — localized names in 30 languages | [info.xml](https://applicast.ga.sony.net/WidgetBundles/SNY_BasicCalculator/info.xml) | [2026-09-17](https://web.archive.org/web/20260917204708/https://applicast.ga.sony.net/WidgetBundles/SNY_BasicCalculator/info.xml) |
| World Clock dictionary — 31 languages | [dic.txt](https://applicast.ga.sony.net/WidgetBundles/SNY_WorldClock/dic.txt) | [2026-09-17](https://web.archive.org/web/20260917204715/https://applicast.ga.sony.net/WidgetBundles/SNY_WorldClock/dic.txt) |
| Source Code Distribution Service (search page) | [oss.sony.net](https://oss.sony.net/Products/Linux/common/search.html) | [2026-09-01](https://web.archive.org/web/20260901004026/https://oss.sony.net/Products/Linux/common/search.html) |
| Same service, EU TV category — this generation **was** listed | *(removed from the live server)* | [2014-10-10](https://web.archive.org/web/20141010061250/https://oss.sony.net/Products/Linux/TV/category03.html) |
| Source download page, group incl. KDL-46EX725 — 23 packages | *(returns 404 today)* | [2015-07-27](https://web.archive.org/web/20150727011435/https://oss.sony.net/Products/Linux/TV/KDL-32CX520.html) |

The last two rows are the evidence for the GPL-removal incident: the
generation's listing and its source packages exist only in the archive
now. Analysis in
[docs/withheld-by-catalog.md](docs/withheld-by-catalog.md) and
[docs/oss-source-recovery.md](docs/oss-source-recovery.md).

The **end-of-service paper trail** is archived the same way: Sony
Brasil's five dated per-service shutdown notices (Facebook, Skype,
Video & TV SideView, TrackID, Twitter), each naming both of our models,
plus the firmware-downloads-removed page — with English regional
copies confirming they were global communications.
[docs/sony-end-of-service-statements.md](docs/sony-end-of-service-statements.md).

## Where this was written up

The public record of the investigation, in the order it was published.
Snapshotted for the same reason as everything above — a post is not a
record while it lives only on someone else's server.

| Piece | Live | Snapshot |
|---|---|---|
| Consumer Rights Wiki (FULU) — product-line page with the incidents and their sources; updated 2026-09-18 with the five archived end-of-service notices, the browser-3D incident, the Brazil consumer-code section, and the corrected firmware claim | [Sony BRAVIA pre-Android Linux TVs (2011-2012)](https://consumerrights.wiki/index.php?title=Sony_BRAVIA_pre-Android_Linux_TVs_%282011-2012%29) | — |
| TabNews (pt-BR) — the investigation as a first-person account | [Em 2011 um CEO me deu de presente uma licença de 3D…](https://www.tabnews.com.br/danielramos/em-2011-um-ceo-me-deu-de-presente-uma-licenca-de-3d-em-2026-eu-devolvi-o-favor-consertando-o-3d-de-todo-o-mundo) | [2026-09-17](https://web.archive.org/web/20260917232833/https://www.tabnews.com.br/danielramos/em-2011-um-ceo-me-deu-de-presente-uma-licenca-de-3d-em-2026-eu-devolvi-o-favor-consertando-o-3d-de-todo-o-mundo) |
| TabNews (pt-BR) — essay: what slop is, where it came from, and the hacker precedent | [Essa é a história da relação de a gente não banir o nmap…](https://www.tabnews.com.br/danielramos/essa-e-a-historia-da-relacao-de-a-gente-nao-banir-o-nmap-porque-criminoso-usa-ele-e-o-maior-evento-de-slop-da-historia-do-open-source) | saved 2026-09-17 |
| TabNews (pt-BR) — the Zig fork, and a closed door respected | [cgm-zig: o fork do Zig que nasceu no lixão](https://www.tabnews.com.br/danielramos/cgm-zig-o-fork-do-zig-que-nasceu-no-lixao-e-compila-o-que-o-original-nao-compilava) | saved 2026-09-17 |

Drafts and publication notes for these live in
[docs/tabnews-post-pessoal.md](docs/tabnews-post-pessoal.md),
[docs/tabnews-post-slop.md](docs/tabnews-post-slop.md) and
[docs/tabnews-post.md](docs/tabnews-post.md) (a neutral-register
variant of the same case, written to be quotable by someone who is not
the owner). The wiki update as posted (and its noticeboard follow-up)
is in [docs/wiki/](docs/wiki/).

## Repository layout

- `docs/` — **[project status & partner guide](docs/project-status.md)**
  (read this first, kept current), the **public method guide**
  ([build-your-own-bravia-portal.md](docs/build-your-own-bravia-portal.md)),
  the **era platform facts** ([keys](docs/era-key-vocabulary.md),
  [media element](docs/era-media-element.md)),
  [platform map](docs/platform-map.md),
  [feasibility roadmap](docs/feasibility-roadmap.md),
  [right-to-repair context](docs/right-to-repair.md), the
  **3D signalling set** ([explainer](docs/3d-signalling-explainer.md),
  [ecosystem](docs/3d-signalling-ecosystem.md),
  [browser block](docs/3d-blocked-in-browser.md),
  [legacy formats — act three](docs/legacy-3d-formats.md),
  [3D photos on a BRAVIA](docs/3d-photos-on-bravia.md),
  [origin story](docs/3d-origin-story.md)), the
  **consumer-rights set** ([legal analysis](docs/legal-eula-analysis.md),
  [regional asymmetry](docs/regional-documentation-asymmetry.md),
  [end-of-service archive](docs/sony-end-of-service-statements.md),
  [TrackID recovery](docs/trackid-bgmsearch-recovered.md)), the
  **campaign record**
  ([judging by the cover](docs/judging-by-the-cover.md),
  [Rossmann outreach](docs/rossmann-outreach.md)), research notes
  (`docs/research/`, incl. live LAN recon artifacts), and wiki page
  drafts (`docs/wiki/`)
- `tools/` — extraction/analysis tooling and notes: the
  [tv-mediabrowser](tools/serviio/tv-mediabrowser/README.md) media app
  (live on the owner's LAN), Serviio renderer profiles + 3D fix,
  the SEI 3D injector, the rd1 portal, the [upstream 3D-signalling
  campaign](tools/serviio/upstream-3d-issues/), and the [systemd
  stack](tools/systemd/README.md) that runs it all
- `certs/` — CA + leaf certificates for the era-TLS lanes

Firmware images, service manuals, and Sony-distributed widget
packages are **not hosted here** — they live in the owner's offline
private archive (see the scope note above and the private-material
section of the partner guide).

## Legal note

This project studies devices the author owns. Sony-distributed material
(firmware images, service manuals, widget packages) referenced by older
research notes is kept in the owner's offline private archive — never in
this repository. Nothing here bypasses or redistributes DRM-protected
content.