# Generations, models and the AZ1 harvest

**2026-09-17.** Two questions this page answers: *which TVs does this work
apply to*, and *what did the oldest generation actually get*. Plus a
standing rule about declaring things dead.

## Why generation, not model

Sony distributed AppliCast widgets **per chassis generation**. Their own
CDN layout is the evidence: catalogs live at
`/WidgetContents/SNY_WidgetGallery/{AZ2,AZ3}/…` and
`/WidgetCatalogs/AZ1_*`, one bundle set per generation, and nothing in
`info.xml` or any manifest restricts a bundle to a model. Every set in a
generation was handed the same files.

| Generation | Year | Widget namespace | Signed? |
|---|---|---|---|
| `AZ1` | 2010 | `/WidgetCatalogs/AZ1_*`, `/WsIndexes/`, `/WsBundles/` | **no signature files served** |
| `AZ2` | 2011 | `/WidgetContents/SNY_WidgetGallery/AZ2/`, `/WidgetBundles/` | yes — `digest.txt` + RSA-3072 `digest.sig`, enforced |
| `AZ3` | 2012 | `/WidgetContents/SNY_WidgetGallery/AZ3/`, `/WidgetBundles/` | yes — same |

That difference matters: the signature wall documented in
[appliwidget-programming.md §4](research/appliwidget-programming.md)
applies to AZ2/AZ3. For every `WsBundles/` item probed, `digest.txt` and
`digest.sig` both return 403 — so either the AZ1 generation's bundles are
unsigned, or their signatures live somewhere not yet found. Stated as an
observation, not a conclusion; nobody has tried installing one.

## Model coverage, from Sony's own service manuals

The service manuals name every model they cover, which makes them the
authoritative mapping. From the owner's archive:

**AZ2-F (SEGM.3A-2, "BATV")** — one manual covers
**KDL-32EX725, KDL-40EX725, KDL-46EX725, KDL-55EX725**, with a separate
schematic for **KDL-60EX725**. Five sizes, one chassis, one set of
widgets.

**AZ3F (SEGM 3A-G)** — the archive holds the `KDL-46HX855` manual;
coverage of the other sizes in that line is not yet documented here.

**Same board family**, from board census in
[platform-map.md](platform-map.md): KDL-46EX724, KDL-40HX853,
KDL-55HX753.

**Still to establish:** the full AZ1 and AZ3 model rosters. The
authoritative sources are service-manual coverage lists and Sony's
support pages; see the re-check list at the bottom.

## Tier differences within a generation — worth mapping

Same chassis and same widget set does **not** mean same TV. Owner-observed
differences between the two sets here, both 46-inch:

| | KDL-46EX725 (AZ2-F, 2011) | KDL-46HX855 (AZ3F, 2012) |
|---|---|---|
| Panel size | 46" | 46" |
| Front glass | standard | **anti-glare glass in front of the panel** |
| Audio | conventional | **embedded subwoofer** |
| Opera TV Store | **absent** | **present** |
| 3D | yes | yes (12-bit panel) |

The Opera Store difference is the interesting one for this project: it is
a whole app surface the EX725 never had, and it is a separate lane
(`sony.tvstore.opera.com`) from AppliCast. That host is on the project's
research list and has not been characterised yet.

The general shape — one chassis spanning 32"–60", with premium features
(local dimming, subwoofer, anti-glare, extra app stores) distinguishing
tiers rather than generations — is worth completing into a proper table.
Sizes share the chassis; tiers differ in hardware.

## What AZ1 actually got

Harvested 2026-09-17. The AZ1 tree is still live and still answers in
**24 languages** (including Estonian and Latvian, which AZ2/AZ3 never
got).

**Its catalog offers exactly one widget.** `AZ1_EU_ALL_eng.xml` is 527
bytes, dated **2010-04-21**, and contains a single entry: *Home Theatre
Control* (`SNY_AudioControl`). A sixteen-year-old file, still served.

The AZ1 index also points at two bundles in the older `WsBundles/`
namespace, both recovered:

- **`XMB_AppliCast_AZ1_EU`** — `xMB_Plugin_AppliCast`, profile
  **`PAC2.0`**. This is the AppliCast engine delivered as an XMB
  (XrossMediaBar) plugin. `PAC2.0` appears nowhere in the profile ladder
  this project had documented.
- **`PHT_PhotoMap_AZ1_EU` / `_AZ1_US` / `_AZ2`** — `GPSPhotoWidget`,
  profile `AC1.0`, 920×520, with preferences. A geotagged-photo map
  viewer that appears in no project document and in no AZ2/AZ3 catalog —
  yet an **AZ2 build exists**, so it would run on the EX725.

### The PhotoMap's dependency problem

It draws its maps from three third-party services, none of them Sony:

```
http://local.yahooapis.com/MapsService/V1/mapImage?appid=
http://maps.google.com/staticmap?
http://api.pmx.proatlas.net/PESWebService/v1/drawMap?appid=h684_0121
```

Current probe results: `local.yahooapis.com` does not resolve;
`api.pmx.proatlas.net` resolves but the request fails to connect;
`maps.google.com` resolves but the Static Maps **v1** endpoint the widget
uses was retired years ago.

**Not yet declared dead** — see the rule below. The Internet Archive was
offline at the time of writing, so the one source that could show cached
responses, parameters and replies could not be consulted.

If they are gone, this widget is repairable in a way the others are not:
its API shape is plain (`latitude`, `longitude`, `scale`, `width`,
`height`, `format`, `center`), so a small shim on the LAN server could
answer `drawMap` from a modern tile source. And because no signature
files are served for `WsBundles/`, repointing the widget may not even
require the DNS-override route — which matters, since the override list
is a closed two-host set (rule 6).

## Rule: check the archive before declaring a service dead

A `NXDOMAIN` or a failed connection means *not reachable now*. It does
not establish what the endpoint returned, what parameters it accepted, or
whether a mirror survives. Before writing "dead" into a document:

1. Query the Internet Archive (CDX + snapshots) for the host and path.
2. Look for cached responses, not just cached pages — a single archived
   API reply documents the response format permanently.
3. Record the check date, because "dead" is a claim with a timestamp.

This page follows its own rule: the three map endpoints above are
**unverified-unreachable as of 2026-09-17**, pending an Archive query.

### Re-check list (Internet Archive was offline 2026-09-17)

- `local.yahooapis.com/MapsService/V1/mapImage` — response format and
  parameters
- `api.pmx.proatlas.net/PESWebService/v1/drawMap` — same, plus whether
  the `appid=h684_0121` key appears in any capture
- `maps.google.com/staticmap` v1 — parameter set the widget relies on
- Sony support/eSupport pages listing models per firmware release — the
  authoritative AZ1/AZ3 model rosters
- `sony.tvstore.opera.com` — the Opera Store lane the HX855 has and the
  EX725 does not
