# AppliCast widget lane — gallery capture + CDN map (2026-09-13)

Owner opened the widget gallery on the EX725; on-screen result:
**"Erro de dados — Não foi possível adquirir dados. Tente novamente
mais tarde."** Capture: firewall vantage (`widgetgallery-wan.pcap`,
602 packets). Then the live CDN was explored by fetching exactly the
URLs the TV fetches (plain GETs, TV's own UAs) — artifacts under
`/tmp/acig-/applicast/`, key ones committed here.

## The widget system has its own fingerprint

The gallery client speaks with UA **`WidgetSystem/3.0.9`** (distinct
from the DTV `SONY DTV/2010; PKG4…` UA — separate subsystem, version
now known). All traffic plain HTTP :80 to `applicast.ga.sony.net`
(AWS CloudFront → AmazonS3 origin), DNS-cached (no lookups during the
round), dozens of parallel one-connection-per-file fetches.

## Why the gallery errors — per-stream correlation (port-paired)

Everything the gallery needs to draw its UI still serves:

- 200: `canvas.xml`, `canvas.js` (61 KB — the gallery's full source),
  `canvas-common/fhd/wxga.css`, `info.xml`, `digest.txt`,
  `digest.sig`, `dic/US/por.txt`
- 304: all cached `img/fhd/*.png` UI assets, `icon.png`

The ONLY failing request is the catalog:
`GET /WidgetBundles/SNY_WidgetGallery/../../WidgetContents/
SNY_WidgetGallery/AZ2/Index.xml` → **403 Forbidden** (16-byte body
"Access Forbidden", `X-Cache: Error from cloudfront`, S3 version-id
present — a POLICY block on a live object, not a missing file). That
single 403 = "Erro de dados". (The same URL served 200 to curl
minutes later from the same LAN — the full mechanism is cracked
below: origin deletion on 2026-03-17 + CloudFront cache-node
lottery, NOT a UA or client-identity block.)

## The CDN map (reconstructed by following the TV's own hops)

```
WidgetContents/SNY_WidgetGallery/{AZ2,AZ3}/Index.xml      (router)
  └─ <gallery country="BRA" src="Gallery_{_area_}_{_country_}_{_lang_}.xml"/>
WidgetContents/.../Gallery_US_BRA_por.xml    → 403 (BRA catalog BLOCKED)
WidgetContents/.../Gallery_US_ALL_eng.xml    → 200 (help-screen XML → points at catalog)
WidgetContents/.../Catalog_US_ALL_eng.xml    → 200 — THE WIDGET LIST
WidgetBundles/SNY_<Name>/{info.xml, canvas.xml, canvas.js, *.css,
                          digest.txt, digest.sig, dic/, img/}
WidgetInfos/SNY_<Name>/{WW_ALL_ALL/poster.png, US_ALL_eng/description.xml}
```

Template variables: `{_area_}` (US for BRA sets — the dic path is
`dic/US/por.txt`), `{_country_}`, `{_lang_}`, `{_panel_}` (fhd/wxga —
asset resolution variants). **AZ2/AZ3 chassis-keyed** — the HX855
would walk the AZ3 tree.

## The catalog (verbatim schema — the insertion format)

```xml
<Catalog updated="2011-04-01T00:00:00">
  <Category>
    <Widget name="Facebook" status="Deleted" updated="2011-04-01T00:00:00"
            registration="dock">
      <id>http://applicast.ga.sony.net/WidgetBundles/SNY_Facebook/</id>
      <description>Get updates from friends while watching TV</description>
      <provider>Sony Electronics</provider>
      <image>http://applicast.ga.sony.net/WidgetInfos/SNY_Facebook/WW_ALL_ALL/poster.png</image>
      <information>http://applicast.ga.sony.net/WidgetInfos/SNY_Facebook/US_ALL_eng/description.xml</information>
    </Widget>
    <!-- Twitter, same shape, status="deleted" -->
  </Category>
</Catalog>
```

The store's entire remaining inventory: Facebook + Twitter, both
flagged **Deleted 2011-04-01**. `registration="dock"` — widgets dock
on the side of the screen **while watching TV**.

## The bundle format (from info.xml + digest of both bundles)

- `info.xml`: `<profile spec="WAA1.0"/>`, layout
  `<layout view="canvas" type="xgml" src="canvas.xml" mode="HD_HALF"/>`,
  **`<registry path="dtv/X2WS"/>` (widgets get persistent storage)**,
  multilingual `<name>`.
- Bundle = XGML canvas markup + JS logic + CSS (per-panel-resolution
  variants) + `dic/` dictionaries + `digest.txt` (per-file **SHA256
  manifest**) + `digest.sig` (**384-byte signature** over the digest).
- Gallery bundle: fully served (we hold the complete code, incl. 61 KB
  `canvas.js`). SNY_Facebook bundle: `info.xml`/`digest.txt`/`digest.sig`
  serve, the CODE files are 403-blocked.

## Consequences

1. **The applet lane is concretely insertable**: a single Unbound
   override on `applicast.ga.sony.net` → our LAN server serves
   Index.xml → Gallery_BRA_por.xml (ours) → Catalog with our widget →
   our bundle. The TV's own retry/error behavior proves it proceeds
   on whatever it gets.
2. **Widgets are HTML/JS-class code** (XGML + JS + CSS) with a
   registry and network access — a custom widget is an applet in the
   Opera-era engine, docked over live TV.
3. **The open gate is `digest.sig`**: per-bundle SHA256 manifest +
   384-byte signature. Whether the WidgetSystem/3.0.9 runtime enforces
   it against a Sony key (and what happens on mismatch) is THE
   research question for serving our own bundle.
4. The era store died 2011-04-01 (inventory Deleted); the BRA catalog
   is hard-blocked; the code-class objects are blocked — everything
   else still serves. We hold the complete gallery bundle as the
   reference implementation.

## Correction + the rescue: the CDN map after the full archival grab

**Correction to the first-pass note above:** the Facebook bundle's
"blocked code files" were never blocked — the bundle's code lives in
`canvas/` and `dock/` subdirectories, and S3's policy answers
wrong-path requests with 403 instead of 404. The digest-driven grab
walked the real structure and retrieved the **full Facebook widget**
(193 KB canvas.js, param.js, popup.js, util.js, sha1.js,
`encryption.enc.js`, and a 384-byte `common.key` in both canvas/ and
dock/ — per-bundle key material consumed by the widget's own JS,
distinct from digest.sig).

A systematic archival grab (`applicast-fetched/grab_applicast.sh`,
full log in `applicast-fetched/MANIFEST.tsv`; UA WidgetSystem/3.0.9;
URL sources: every URL the TVs requested in our pcaps + digest-driven
enumeration + chassis/locale/candidate sweeps) retrieved **150 live
objects (126 files, 2.2 MB); 422 URLs hard-blocked**. Alive bundles:

| Bundle | Profile | What we hold |
|---|---|---|
| `SNY_WidgetGallery` | WAA1.0 | complete (54 objects) — the platform's own UI, 61 KB JS |
| `SNY_Facebook` | WAA1.0 | **complete** incl. dock+canvas code, crypto utils, common.key |
| `SNY_Twitter` | WAA1.0 | info.xml + digest + icons (code under subpaths not enumerated before sweep end) |
| `SNY_RSSReader` | **AC2.1** | complete — 60 KB widget.js + fullscreen variant + layout.xml |
| `SNY_AudioControlApp` + `SNY_AudioControl` | SAX1.0/SWA1.0 | complete — dock/canvas/common structure incl. `ceccommandcontrol.js` (**widgets can drive HDMI-CEC**) |

`SNY_AudioControl/info.xml` still carries **Sony developer comments
(Japanese)** — these are the development copies, not sanitized
production builds. One comment names the spec ladder:
`<profile spec="SAX1.0"/> // AZ2以降ではSWA1.0` ("on AZ2+ it's SWA1.0").

Three widget profiles are therefore documented from real code:
WAA1.0 (canvas XGML + JS + CSS), AC2.1 (declarative layout.xml +
widget.js — the simplest authoring target, AZ2-era), SAX/SWA
(docked system widgets).

## The 403 on the catalog — mechanism cracked (2026-09-13, controlled tests)

Both TVs get 403 on `../../WidgetContents/…/Index.xml` (AZ2 and AZ3)
while curl from the same LAN gets 200 on the same URL. Killed
hypotheses, each by experiment:

- **UA-based?** No — exact replay with `WidgetSystem/4.0.4`,
  `WidgetSystem/3.0.9`, curl UA, and the DTV UA all return 200.
- **Path form (`../../`)?** No — raw and normalized forms both 200.
- **Edge IP?** No — same edge IP (52.85.78.49) that 403'd the TV
  serves 200 to replay.
- **WAF rate rule (the TV bursts dozens of parallel connections)?**
  No — a 41-request TV-like parallel burst all 200s; and in the real
  capture 30 × 200 responses arrive AFTER the first 403.

What the responses actually show: the TV's 403 is origin-sourced
(S3, negative-cached by CloudFront, `X-Cache: Error from cloudfront`,
`Cache-Control: max-age=86400`); our 200s are `X-Cache: Hit from
cloudfront` with `Age` ~16 min and a **different `Via` cache-node hash
on every hit** — one edge IP fronts many cache nodes. Decisive
timestamps: the 403 carries `Last-Modified: 2026-03-17 04:26:07 GMT`
and the cached 200 carries `Last-Modified: 2026-03-17 05:04:26 GMT` —
**Sony changed the bucket twice on 2026-03-17**; the origin now 403s
the catalog objects, and the 200s we receive are pre-change cache
entries that still live on some edge nodes.

Consequences:

1. **The 200s we fetched are potentially the last retrievable
   copies** — when those cache entries expire, the BRA/por catalogs
   and everything else 403-at-origin is gone. A rescue sweep
   (every 403'd URL retried across 6 edge IPs) ran to recover any
   node-cached survivors; results in MANIFEST.tsv.
2. The TVs' consistent 403s vs our consistent 200s is a cache-node
   lottery weighted by client behavior (era clients hit the
   negative-cached entries) — not a deliberate anti-TV block. Either
   way the gallery is dead on live Sony infra for real TVs.
3. For the spoof experiment nothing changes: we replace the whole
   host via DNS.

## HX855 round (same evening, 16:11–16:12 local, `hx855-menus-wan.pcap`)

Owner ran the same menus on the HX855 (normal usage, not a
crash-test). Same "Erro de dados" on the gallery — the AZ3 catalog
403s identically (and the 855 also fetches the AZ2 Index). New
fingerprints and endpoints the EX725 never shows:

- **UA ladder**: `SONY DTV/2012; PKG2.120BRA;` (vs 2010/PKG4 on the
  725) and **`WidgetSystem/4.0.4`** (vs 3.0.9) — two widget-runtime
  generations, both speaking plain HTTP to the same namespace.
- **`ssm1.internet.sony.tv`** — the 2012 gen's numbered ssm host.
  `GET /DTV/index.xml` there returns the SAME tombstone (200 OK,
  nginx, `Last-Modified 2026-05-04`, `Cache-Control: max-age=31536000`
  — cached for a year; Sony planted it to stay). Plus the usual
  `ssm.` TLS-1.0 auth sessions. **Firmware/content manifest dead on
  both service hosts, both TV generations.**
- **`bravia.dl.playstation.net`** (Akamai, 2.20.182.71 /
  23.45.127.32) — a 2012-gen-only endpoint, serving
  `/bravia/WidgetBundles/SocialTV/EmotionPost/img/NUX_Share.png`
  (200/304; the owner reports this SocialTV app "died recently" —
  it's the last thing still limping on cache). Bundle metadata under
  that path 404s (thin Akamai slice; a proper sweep of that namespace
  needs a capture of the 855 opening its SocialTV menu). The one live
  asset is archived. This is a **fourth host** the Unbound plan can
  own, and evidence the 2012 chassis has a second widget system
  (SocialTV) beyond AppliCast.
- BIVL icon fetches include service_55/sub_1, service_41/sub_4,
  service_30 — richer service-icon taxonomy than the 725 requested.

## Artifacts

- `widgetgallery-wan.pcap` — the EX725 gallery round (firewall vantage)
- `hx855-menus-wan.pcap` — the HX855 menus round (new endpoints above)
- `applicast-fetched/` — the archival grab: four complete widget
  bundles, catalog/Gallery/Index XMLs, WidgetInfos, digests+sigs,
  MANIFEST.tsv (every URL, status, size), and the grab script