# sony-bravia-linux

Reverse-engineering and software porting for **Sony BRAVIA KDL-era TVs** — the
pre-Android, Linux-based BRAVIA platform (~2005–2015). Goal: understand the
platform well enough to run third-party software on it (e.g. VLC) and unlock
more internet content than the stock firmware allows.

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

## Why bother (the right-to-repair angle)

These late-KDL sets are phenomenal hardware — the KDL-46HX855 has
X-Reality PRO with 12-bit color processing and active 3D, and picture
quality that still embarrasses many modern budget panels. Sony EOL'd the
platform: smart services shut down, firmware downloads removed (Jan
2022), even the GPL source downloads were deleted from Sony's site. The
owner is now the only party with any incentive to keep this hardware
alive. This project is right-to-repair work: document, control, and
eventually run owner-chosen software on owner-owned hardware. See
[docs/right-to-repair.md](docs/right-to-repair.md) (includes the Louis
Rossmann / repair.wiki / FULU Foundation sharing plan).

## Test hardware (both on the LAN, DHCP-pinned by MAC)

| Model | Year | Chassis | LAN IP |
|---|---|---|---|
| KDL-46HX855 | 2012 | AZ3F (main SoC codename "ATREYU") | 192.168.0.21 |
| KDL-46EX725 | 2011 | AZ2-F ("BATV" board) | 192.168.0.22 |

## Hardware this applies to

### Televisions

**Verified by us** — every claim in this repository was tested on these
two sets:

| Model | Year | Chassis |
|---|---|---|
| KDL-46HX855 | 2012 | AZ3F (SoC codename "ATREYU") |
| KDL-46EX725 | 2011 | AZ2-F ("BATV" board) |

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

So the compatibility unit here is the **generation**:

| Generation | Year | Covers |
|---|---|---|
| `AZ1` | 2010 | the earlier line — its `/WidgetCatalogs/AZ1_*` tree still answers, in 24 languages |
| `AZ2` | 2011 | EX/CX/NX/HX 2011 sets — our EX725's generation |
| `AZ3` | 2012 | HX/EX 2012 sets — our HX855's generation |

We happen to own two sets; the work applies to three generations of
them. What we can state as *tested* is two models — what we can state
as *distributed identically by Sony* is every set in those generations.
Reports from other models are welcome and will sharpen this table.

### Sony audio systems (HDMI-CEC)

The `SNY_AudioControlApp` widget ("Home Theatre Control") is a full
remote for a Sony audio system over HDMI-CEC — sound field, speaker
configuration, speaker levels, tone, audio mode — not merely volume. It
identifies the attached system by CEC vendor ID against a table Sony
shipped inside the bundle: **102 entries, 81 distinct products**.

That table is reproduced here because it is the compatibility list for
this widget, and because it documents which hardware a recovered Sony
control protocol can drive:

| Family | Models |
|---|---|
| **RHT-G** (sound bases) | RHT-G5, RHT-G10, RHT-G10EX, RHT-G11, RHT-G15 |
| **HT-CT** (soundbars) | HT-CT150, HT-CT350, HT-CT370, HT-CT380, HT-CT381, HT-CT550W, HT-CT660, HT-CT770, HT-CT780, HT-CT790, HT-CT800 |
| **HT-ST** | HT-ST3, HT-ST5, HT-ST7, HT-ST9, HT-ST5000 |
| **HT-XT / HT-XF / HT-X** | HT-XT1, HT-XT2, HT-XT3, HT-XF9000, HT-X9000F |
| **HT-NT / HT-MT / HT-RT / HT-Z / HT-ZF** | HT-NT3, HT-NT5, HT-MT500, HT-RT5, HT-Z9F, HT-ZF9 |
| **HT-S / HT-SF / HT-SS / HT-FS / HT-AS** | HT-S200F, HT-SF200/201, HT-SS370/SF470, HT-SS380, HT-FS30, HT-AS5/AF5 |
| **STR-DH** (receivers) | STR-DH520, STR-DH530, STR-DH540, STR-DH550, STR-DH590, STR-DH710, STR-DH720, STR-DH730, STR-DH740, STR-DH750, STR-DH770, STR-DH790, STR-DH820, STR-DH830 |
| **STR-DN** | STR-DN840, STR-DN850, STR-DN860, STR-DN1020, STR-DN1030, STR-DN1040, STR-DN1050, STR-DN1060, STR-DN1070, STR-DN1080, STR-DN2030 |
| **STR-DA (ES)** | STR-DA1800ES, STR-DA2800ES, STR-DA3700ES, STR-DA5700ES, STR-DA5800ES |
| **STR-ZA (ES)** | STR-ZA810ES, STR-ZA1000ES, STR-ZA1100ES, STR-ZA2000ES, STR-ZA2100ES, STR-ZA3000ES, STR-ZA3100ES, STR-ZA5000ES |
| **TA-DA (ES)** | TA-DA3600ES, TA-DA5600ES, TA-DA5700ES, TA-DA5800ES |
| **Headphones** | MDR-HW700DS |

**We have verified none of these** — there is no Sony audio system on
the test LAN, and the widget correctly reports "unavailable" when no
CEC audio device answers. The list is Sony's, recovered from their own
`model/model.json`; the 26 Sony vendor CEC opcodes the widget speaks
(`0xF000`–`0xF21F`) are documented in
[hdmi-cec-audio-system.md](docs/hdmi-cec-audio-system.md).

## Repository layout

- `docs/` — **[project status & partner guide](docs/project-status.md)**
  (read this first), [platform map](docs/platform-map.md),
  [feasibility roadmap](docs/feasibility-roadmap.md),
  [right-to-repair context](docs/right-to-repair.md),
  research notes (`docs/research/`, incl. live LAN recon artifacts),
  repair.wiki page drafts (`docs/wiki/`)
- `tools/` — extraction/analysis tooling and notes: the
  [tv-mediabrowser](tools/serviio/tv-mediabrowser/README.md) media app
  (live on the owner's LAN), Serviio renderer profiles + 3D fix,
  the SEI 3D injector, the rd1 portal, the [upstream 3D-signalling
  campaign drafts](tools/serviio/upstream-3d-issues/), and the [systemd
  stack](tools/systemd/README.md) that runs it all
- `certs/` — CA + leaf certificates for the era-TLS lanes

Firmware images, service manuals, and Sony-distributed widget
packages are **not hosted here** — they live in the owner's offline
private archive (see the scope note above and the private-material
section of the partner guide).

## Current status

**The media experience is live and owner-verified (2026-09-15):** both
TVs browse the full library on the LAN media server and play every
audio format and every major video format, via a systemd-managed stack
with a config file. See
[docs/project-status.md](docs/project-status.md) — the single partner
entry point, kept current.

Research continues: platform identified (MIPS mipsel "ATREYU" SoC,
glibc 2.7 userland, DirectFB/Qt/Opera, Linux 2.6.35-era kernel),
firmware containers confirmed whole-file encrypted (no public
decryptor), live CERS/IRCC + UPnP API documented. Full analysis in
`docs/platform-map.md`; staged plan (zero-mod content → UART root →
kernel modernization) in `docs/feasibility-roadmap.md`.

## The 3D-signalling campaign

These sets auto-engage 3D from exactly one signal — the H.264
frame-packing SEI (payload 45) — and ignore the Matroska StereoMode tag
every standard rip carries, so 3D DLNA playback silently fails on
perfectly good hardware. The diagnosis plus a working fix was taken
upstream to every tool in the encode → remux → player pipeline. Full
drafts, per-target status, and links live in
[tools/serviio/upstream-3d-issues/](tools/serviio/upstream-3d-issues/).

| Front | Outcome (all engaged 2026-09-16) |
|---|---|
| HandBrake | **[PR #8100 merged](https://github.com/HandBrake/HandBrake/pull/8100)** — encoder now writes the missing SEI; closes their #5826 |
| FFmpeg | [bug #24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530) + [enhancement #24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531) filed |
| StaxRip | [answered stranded user on #1873](https://github.com/staxrip/staxrip/issues/1873#issuecomment-5685902578) |
| x265 | [issue #970](https://github.com/Multicorewareinc/x265/issues/970) filed |
| mpv | [issue #18489](https://github.com/mpv-player/mpv/issues/18489) + [PR #18490](https://github.com/mpv-player/mpv/pull/18490) in review — completes the pipeline end to end |
| BD3D2MK3D (r0lZ) | [videohelp thread](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803756) — answered, closed out, cross-brand confirmed |
| LTT forums | [the guide the 3D-theater video promised](https://linustechtips.com/topic/1589907-i-built-a-3d-theater-in-my-basement/?do=findComment&comment=16936161) — first audience-facing post |
| mkvmerge | skipped by owner decision (Codeberg signup paywall) — draft retained |

No DRM or copy-protection mechanism is involved anywhere in the chain.

## Legal note

This project studies devices the author owns. Sony-distributed material
(firmware images, service manuals, widget packages) referenced by older
research notes is kept in the owner's offline private archive — never in
this repository. Nothing here bypasses or redistributes DRM-protected
content.