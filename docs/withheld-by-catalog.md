# Withheld by catalog, not by cost

**Finding, 2026-09-17:** the widgets Sony never offered Brazilian
BRAVIA owners were already fully localized into Portuguese. The
translation was written, paid for, and shipped inside the bundles on
Sony's own CDN. What separated a Brazilian TV from a calculator was a
single catalog XML listing two widgets instead of eight.

This page records that as evidence, not as opinion. Every claim below
is a file still being served by Sony's infrastructure today and can be
re-checked by anyone in a few minutes.

## Why this is a right-to-repair document

The usual defence for a dead smart-TV feature is cost: markets are
small, localization is expensive, support has to end somewhere. That
defence is testable, and here it fails. The cost had already been
paid. The feature was withheld at the distribution layer, after the
work was done — and then the servers that made the distinction were
left running for over a decade while the features stayed dark on the
sets that were never offered them.

An owner cannot repair what a catalog denies. That is the whole
argument for owner-controlled service endpoints in one sentence.

## The evidence

### 1. The CDN is still live (2026-09-17)

`applicast.ga.sony.net` still serves. `SNY_RSSReader/widget.js` returns
HTTP 200 with 60 581 bytes — byte-identical to the copy in this
project's offline archive. Sony ended the platform; the servers were
never switched off.

### 2. Europe was offered eight widgets. Brazil was offered two.

Both catalogs are live, on the same host, for the same chassis
generation (AZ3 = our KDL-46HX855; AZ2 = our KDL-46EX725 behaves the
same):

| Catalog | Widgets offered |
|---|---|
| `Catalog_EU_ALL_eng.xml` | **8** |
| `Catalog_US_ALL_eng.xml` | 2 |
| `Catalog_LA_ALL_eng.xml` | 2 |
| **`Catalog_LA_BRA_por.xml`** | **2** — Facebook, Twitter |

The five Europe-only widgets: **World Clock, Analogue Clock, Calendar,
Alarm, Calculator, RSS Reader** (six titles across the two tiers;
`SNY_BasicClock`, `SNY_WorldClock`, `SNY_BasicCalendar`,
`SNY_BasicAlarm`, `SNY_BasicCalculator`, `SNY_RSSReader`).

Path: `/WidgetContents/SNY_WidgetGallery/{AZ2,AZ3}/Catalog_<area>_<country>_<lang>.xml`.

### 3. Four of the withheld widgets need no translation at all

`SNY_BasicCalculator`, `SNY_BasicAlarm`, `SNY_BasicCalendar` and
`SNY_BasicClock` ship **no dictionary file whatsoever**. They are
language-independent by construction — a calculator has no words, a
clock has hands. Their only localized strings are their names, and
`info.xml` carries **30 of them**, Portuguese included:

```xml
<name lang="por">Calculadora</name>
<name lang="por">Alarme</name>
```

There is no localization cost to recover on a widget that contains no
language.

### 4. The fifth was translated into Portuguese down to the city list

`SNY_WorldClock` does carry a dictionary: `dic.txt`, **31 languages**,
with Portuguese complete — summer-time label, weekday abbreviations,
error strings, and the timezone city list:

```
por:"Hora de Verão"
por:["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"]
por:[ … "Nova Iorque", "São Domingo", "Rio de Janeiro", … ]
```

**Rio de Janeiro is in the timezone list of a widget that was never
offered in Brazil.**

### 5. The platform was designed to do this correctly

The runtime exposes `getLanguage()` to widget JavaScript, and a single
`dic.txt` holds every language at once — the widget selects at runtime
from the TV's own setting. One codebase, localization resolved on the
device: exactly the way the web and ordinary software work. Sony
engineered the mechanism properly and then gated it one layer above,
in a per-country catalog file.

### 6. The dictionaries are outside the signed set

Bundles are signed: `digest.txt` is a per-file SHA-256 manifest and
`digest.sig` is a 384-byte RSA-3072 signature over it (enforced —
see [appliwidget-programming.md §4](research/appliwidget-programming.md)).

`SNY_WorldClock/digest.txt` lists exactly six entries — `info.xml`,
`widget.js`, `layout.xml`, `bg.png`, `widget_fullscreen.js`,
`layout_fullscreen.xml`. **`dic.txt` is not among them.** The
localization data was deliberately left outside the signature, which
is what makes correcting or extending it a legitimate operation rather
than a forgery.

## What the repair actually is

Not a port. Not a translation project. Not a patched binary.

The LAN already overrides `applicast.ga.sony.net` to the owner's own
server (one of exactly two owner-approved DNS overrides — see the
rules of engagement in [project-status.md](project-status.md)). The
catalog served from it is a plain XML file. Offering the full set to
these TVs is a matter of listing the widgets that were always
compatible, always localized, and always sitting on the same CDN.

The bundles install as genuine because they **are** genuine: fetched
byte-exact from Sony's own servers with their original signatures
intact. Nothing is cracked, nothing is forged, no DRM is touched. The
only thing that changes is which catalog the TV is handed — and on a
LAN, that is the owner's to decide.

A pt-BR pass over the shipped European Portuguese (`Moscovo` →
`Moscou`, `Helsínquia` → `Helsinque`) is a genuine improvement on top,
and it lands in the unsigned dictionary where it belongs.

## The repair, deployed (2026-09-17)

Done on the LAN, awaiting owner verification on the EX725:

- All five withheld bundles were fetched **byte-exact from Sony's own
  CDN** and re-verified locally: every entry in each `digest.txt`
  recomputes to its recorded SHA-256, and each `digest.sig` is the
  original 384-byte block. They install as genuine because they are.
- They now sit in the LAN AppliCast mirror's `WidgetBundles/`, with
  their `WidgetInfos/` posters and Details pages.
- The **AZ2 catalog only** (`Catalog_LA_BRA_por.xml`, the EX725's
  chassis) gained five entries — Calculadora, Relógio Analógico,
  Calendário, Alarme, Relógio Mundial. The AZ3 catalog (HX855, the
  workstation's monitor) is deliberately untouched until the EX725
  confirms: rule 5.
- pt-BR Details pages were written for each, since Sony only ever
  produced `description.xml` under `EU_ALL_eng` — another small
  artifact of the same gating. The widgets' own on-screen names come
  from `info.xml`, which was already Portuguese.
- The previous catalog is preserved beside it as `.pre-restore`.

The whole chain answers 200 from the TV's point of view: Index →
Gallery → Catalog → bundle `digest.txt`/`widget.js` → Details page →
poster.

## Scope of the preservation run

The same sweep that produced this finding mapped considerably more of
the platform than the widget gallery. Recorded here because the hosts
are one decommission away from taking it with them:

- **Three live hosts**, not one: `applicast.ga.sony.net`,
  `bravia.dl.playstation.net`, and `applicast.cn.sony.net` — the last
  appearing in no documentation the project has found.
- **A second namespace** absent from our earlier map: `/WsIndexes`,
  `/WsCatalogs`, `/WsBundles`, `/WidgetCatalogs` — including
  `/WidgetCatalogs/AZ1_*` for an **earlier chassis generation** in 24
  languages (Estonian and Latvian among them), and
  `/WsIndexes/AZ2_LA.xml`, the index for our own chassis and region.
- **A resident/system widget class** that never appears in any user
  gallery: `AutoChannelMapping`, `BgmSearch`, `BgmSearchService`,
  `CrossSearch`, `CrossSearchUtil`, `CsxAccessor`, `CsxAccessorNG`,
  `CsxLog`, `LogGate`, `MusicExplorer`, `VideoExplorer`,
  `SEN_AppList`, `SocialTV/WatchingContent`,
  `SocialUX/AccountManager`, `SocialUX/FriendsNotification`,
  `HomeMenu_FY14`, `MyChannel`, and a `DEV/` namespace.
- **137 of 168** referenced bundle URLs answered 200.
- The Internet Archive's index of these hosts is sparse — roughly 280
  rows — so most of this is not preserved anywhere else. Contributing
  the map back to the Archive is a natural follow-up.

Fetched material is Sony-copyrighted and stays in the owner's offline
archive, never in this repository (rule 9). What is public is this
analysis, the paths, and the method — which is all anyone needs to
verify the finding or repeat the preservation before the hosts go
quiet.

## How to re-check this yourself

```bash
# 1. Europe's catalog vs Brazil's, same host, same day
curl -s http://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_EU_ALL_eng.xml | grep -c '<id>'
curl -s http://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_LA_BRA_por.xml | grep -c '<id>'

# 2. The Portuguese name of a widget Brazil was never offered
curl -s http://applicast.ga.sony.net/WidgetBundles/SNY_BasicCalculator/info.xml | grep 'lang="por"'

# 3. Portuguese in the World Clock dictionary — and what is NOT signed
curl -s http://applicast.ga.sony.net/WidgetBundles/SNY_WorldClock/dic.txt | grep -m3 'por:'
curl -s http://applicast.ga.sony.net/WidgetBundles/SNY_WorldClock/digest.txt | grep -c dic
```

*If these commands stop returning data, the platform finally went
dark — and this page becomes the record of what was there.*
