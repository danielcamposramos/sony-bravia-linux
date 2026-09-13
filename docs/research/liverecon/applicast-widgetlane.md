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
   **Sweep closed 2026-09-13: 422 URLs × 6 edges → zero rescues.**
   The 150 objects in `applicast-fetched/` are confirmed the last
   retrievable copies — this repo's archive is the surviving record
   of everything 403-at-origin.
2. The TVs' consistent 403s vs our consistent 200s is a cache-node
   lottery weighted by client behavior (era clients hit the
   negative-cached entries) — not a deliberate anti-TV block. Either
   way the gallery is dead on live Sony infra for real TVs.
3. For the spoof experiment nothing changes: we replace the whole
   host via DNS.

## EX725 powerup round (16:49, `tv-ex725-powerup.pcap` — user power-cycled with 10 s down-time)

The armed idle writer caught the boot. One burst of 21 unique GETs
(~16:49:17, seconds after power-up), all **200 OK**, all UA
`WidgetSystem/3.0.9` — a full **bundle-integrity sweep** of every
installed widget, digest-first:

- `bravia.dl.playstation.net/bravia/WidgetBundles/{LogGate,
  BgmSearch-2ndDisp}/` — digest.sig/txt, info.xml, then
  **resident.xml/resident.js** (LogGate) and **server.xml/server.js**
  (BgmSearch-2ndDisp). **This revises the "2012-gen-only endpoint"
  claim: the EX725 (AZ2) talks to the playstation host too — at
  boot, not in menus.**
- `applicast.ga.sony.net/WidgetBundles/{SNY_WidgetGallery,
  VCServiceUtil}/` — digest/info plus **notification.xml +
  notification.js** (a widget push-notification system) and
  **`VCServiceUtil/common.key` + `main.enc.js`** — the same
  key+encrypted-JS pattern as SNY_Facebook's bundle.
- The catalog `../../WidgetContents/SNY_WidgetGallery/AZ2/Index.xml`
  returned **200 at boot** (a different CloudFront edge than the
  menu round's 403) — cache-node lottery, and proof the boot sweep
  refreshes bundles while any node still serves them.

**The update phone-home did NOT fire at powerup** — zero ssm
contact in the whole boot window. Combined with the idle-window
silence, the enabled phone-home setting is **timestamp-gated**:
the TV checked hours earlier (our OTA menu rounds), so boot skipped
it ("checks the last check"). An overdue-check powerup (the "or do
it anyway" half) remains untested — needs a boot after the check
interval lapses.

Zero DNS lookups anywhere in the capture — with a 10 s down-time
the set resumed from standby state with its resolver cache intact
(not a cold boot).

**7776 beacon cycle:** stopped while the set sat powered on the
HDMI input with no signal (70 s listen, zero), **back at 1.25 s
cadence immediately after the power cycle**. The beacon is gated by
something that changed during no-signal idle — a calibratable
remote state oracle.

## Wayback lane (17:00) — what the Internet Archive holds

- **applicast.ga.sony.net: zero captures ever.** The 422 blocked
  objects have no Wayback copies — the repo archive is the only
  surviving record of that CDN.
- **bravia.dl.playstation.net: mapped by a previous explorer** (CDX
  captures 2011–2024, ~60 URLs). 18 status-200 objects fetched
  (`wayback-playstation/`): real SocialTV-system widget code —
  `SocialTV/EmotionPost_FY13/EmotionPostWidget.xml`,
  `SocialUX/SocialFriends/FriendListWidget.xml`, the complete
  `Zapping` manager/player/selector set (FY13 + FY14 + six version
  dirs 6.0.8–6.1.4), `MyChannel_Bundles/6.1.4/Keyword/widget.xml`,
  `BgmSearch/2.0.1/MediaExplorerCommon.img` (123 KB) — plus a
  **`KiOhJ/` chassis-generation tree** (FY2013 gen) and FY13/FY14
  bundle variants. The 404s in the CDX list map the rest of the
  namespace.
- **sony.tvstore.opera.com: archived 2015** — root page, `jsi18n/`,
  `m/d/Y` fetched (`wayback-tvstore/`); the store's front-end IDs
  and i18n exist for the revival lane.
- **ssm.internet.sony.tv: `DASH/updates/themes/20120127/themes_dl.xml`**
  fetched — the XMB **theme catalog** (themes distributed as SWF +
  md5, thumbnail/theme URLs under the same path). A further content
  lane the Unbound override can serve with our own files.
- Since the boot sweep proved LogGate/BgmSearch-2ndDisp still serve
  200 live, a digest-driven live enumeration sweep of the whole
  playstation-host bundle namespace was launched from the Wayback
  hit-list (`grab_playstation.sh`).

## EX725 idle window — first facts (armed 16:36, firewall vantage)

The 725 sat at the XMB home menu, untouched. Firewall writer
(`/tmp/tv-ex725-idle.pcap`, `host .22 and not udp 7776 and not udp
1900`) captured **zero packets in the first 7+ minutes** —
independently confirmed by a direct 8 s live listen (only 2 ARP
frames). Findings:

- **True AZ2 idle is silent.** No ssm, no applicast, no DNS, no
  icon revalidations from the home menu. This refines the 855's
  "autonomous ~30 s XMB polling": that loop ran while the owner
  was actively navigating menus (menu-state-independent, not
  idle-independent). Genuine idle on AZ2 sends nothing.
- **Consequence for the phone-home/update setting:** no
  short-cycle check timer fires from the home menu — the update
  check is powerup- and/or menu-triggered, not a minutes-scale
  idle poll. A long-interval (hours) timer is not excluded.
- **The UDP 7776 beacon STOPPED** (70 s listen, zero packets)
  while the set is powered and displaying — the beacon is
  state-dependent, not a simple "powered" indicator. It stopped
  around the same time as the menu exit. Once the driving
  condition is pinned down, this becomes a free remote
  state/presence oracle (Track B-alt).
- **The set exited the home menu on its own** — cause was HDMI-CEC,
  not network: the connected Android TV box asserted active-source
  (one-touch-play) and the TV switched to the HDMI input. The wire
  showed zero inbound network activity that could have caused it.
  Symmetry note: `ceccommandcontrol.js` proved widgets can *drive*
  CEC from JS; this event is the same channel in reverse — CEC
  moving the TV's UI state.
- The TV's IP stack stays alive and active while otherwise silent
  (it ARPed for the workstation, `.4` — likely CERS-controller
  related, registration survives power cycles).

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

## HX855 extra systems round (16:30–16:33, `hx855-extramenus-wan.pcap`)

The 855's menus hold three app systems the 725 lacks: **Opera TV
Store**, **Compartilhar/SNS** (SocialTV), and **Netflix**, plus
Wi-Fi Direct. Owner opened each (Wi-Fi Direct wizard viewed only, not
activated — it can reconfigure the set's radios). All three showed
connection errors; the wire gives each a distinct cause:

| System | Wire evidence | Verdict |
|---|---|---|
| Opera TV Store | `certs.opera.com` still ALIVE (resolve + full TLS-1.0 session, bidirectional data — it serves modern Opera too). `sony.tvstore.opera.com` → **NXDOMAIN, confirmed globally** (1.1.1.1 + 8.8.8.8) — domain deleted; the TV never attempts a connection | **Dead domain, revivable via Unbound override** — we must serve TLS; whether era Opera Devices validates certs is the open question |
| Netflix | `nccp-nrdp-31.cloud.netflix.net` → CNAME `nccp-nrdp-31.dradis.netflix.com` → **NXDOMAIN**; zero SYNs | era control plane deleted; not worth reviving (DRM-wrapped, out of scope) |
| SNS/Share | EmotionPost icons still serve (200/304); app loads its NUX then dies on its missing backend | cosmetically half-alive |

New facts:

- **The XMB home screen polls autonomously**: the icon-refresh loop
  (`applicast.ga.sony.net` + `bravia.dl.playstation.net`, ~every
  30 s: SNY_WidgetGallery/icon-tiny, SNY_AudioControlApp/icon,
  SocialTV/EmotionPost/img/NUX_Share.png,
  **Ext/WsCatalogs/otvs_icon_77x58.png**) ran continuously
  regardless of which menu was open — settles the autonomous-polling
  question for the 855 (idle-window capture still worthwhile for the
  725). Practical consequence: a Unbound override is noticed within
  seconds, no menu action needed.
- **`/bravia/WidgetBundles/Ext/WsCatalogs/`** — a new
  playstation-host namespace holding external-catalog icons
  (`otvs_icon_77x58.png` = the Opera TV Store's XMB icon, archived;
  the namespace is a thin Akamai slice — XML siblings 404).
  bravia.dl.playstation.net is the 2012 chassis's external-app
  catalog host, not just SocialTV.
- **Real infra CNAMEs exposed by DNS answers**:
  `applicast.ga.sony.net` → `tv-applicast-ga.update.me.sony.com` →
  `dn81zjgsnqw3k.cloudfront.net` (CloudFront);
  `bravia.dl.playstation.net` → `generichttp.dl.playstation.net.
  edgesuite.net` → `a908.d.akamai.net` (Akamai).
- Era resolver quirk on display: unqualified-lookup retries append
  the LAN search domain (`…casacampos.lok`) for every failing name.

## Widget-programming reference complete (workflow wf_3282b9e4-4f5)

Full authoring reference: **`docs/research/appliwidget-programming.md`**
(16 agents, adversarial verify, confidence-tagged [V]/[C]/[I] throughout).
Headlines:

- **Engine API reconstructed and adversarially verified** from the held
  bundles: ~30 engine globals (`widget`, `system`, `System`, `KeyEvent`,
  `Debug`, `document` XGML DOM with `getElementByName`…), the AC2.1
  declarative layout vocabulary, XGML/CSS dialect, registry/persistence
  semantics, chassis-branching by `system.version` (3 = AZ2, 4 = AZ3).
- **A sanctioned develop-mode backdoor exists in the gallery**:
  `widget.uri` can carry `?mode=develop&url=<catalog-url>` — the
  gallery's option menu "Change Catalog" (native `prompt()`, persisted
  in registry `developCatalogSrc`) redirects the catalog fetch,
  bypassing WidgetContents entirely. Signature-independent for the
  CATALOG (bundle install still gated by digest.sig). Whether we can
  control `widget.uri`'s query string at launch is the open probe.
- **Signature verdict: UNKNOWN, leaning enforced-at-install-time** —
  digest.sig is one RSA-3072 block over SHA-256(digest.txt), key
  firmware-pinned, zero verification logic in any bundle JS. The
  decisive on-LAN A/B/C experiment (original sig / foreign sig /
  garbage-absent) is designed in §4 of the reference.
- **First-widget target: AC2.1 "LAN_Hello"** (RSSReader-shaped;
  SAX1.1 proven-installed fallback), full bundle layout + engineering
  rules in §5.
- **Unbound override experiment design** in §6 — one-host override
  (applicast.ga.sony.net only), firmware/ssm/playstation hosts left
  resolving normally, conditional-GET-honoring LAN server, 5 phases
  from transparent baseline to custom-widget install.
- The research pass also grew the live mirror to **30 bundles** plus
  `ga-dev/`, `cn-dev/`, geekpage.jp tutorial mirror (incl. verified
  HelloWorld.zip), the one public GitHub AppliCast widget, and a
  dev-site Wayback copy — all under `/tmp/acig-/applicast-archive/`.

## Certificate lane (Opera trust anchors, 2026-09-13 evening)

Why it matters: the 855's Opera TV Store revival needs TLS the era
browser accepts, and `certs.opera.com` (still ALIVE on the wire, full
TLS sessions) is Opera's root-CA distribution server — the TV's
trust-anchor update path.

- **The entire root store is archived in Wayback** (1,831 objects).
  `certs.opera.com/02/repository.xml` = the root inventory manifest;
  era-relevant set (2013 captures, matching our 2011–2012 TVs) = 302
  root certs, fetched to `certs-opera/roots/`.
- **`repository.xml` is cryptographically signed** — a base64
  signature block sits above the `<repository>` tree. The
  "override certs.opera.com to inject our own CA" chain is therefore
  signature-gated: a forged root list should fail verification (if
  the era client verifies). Remaining TLS strategies: serve the
  store a cert chaining to an already-trusted root, or empirically
  test era-Opera's validation strictness.
- **Live certs.opera.com** serves a 2026 `*.opera.com` wildcard
  (Trust Provider B.V.) — alive and current, so the TV's root-update
  path still functions against the real host.
- **CT logs for the store domain**: no era cert recoverable — the
  only CT entries are 13 Let's Encrypt certs 2018–2019 for
  `alibaba.tvstore.opera.com` (a SAN sibling; an Alibaba-partnership
  store variant that survived on LE until 2019).

## Artifacts

- `widgetgallery-wan.pcap` — the EX725 gallery round (firewall vantage)
- `hx855-menus-wan.pcap` — the HX855 menus round (new endpoints above)
- `applicast-fetched/` — the archival grab: four complete widget
  bundles, catalog/Gallery/Index XMLs, WidgetInfos, digests+sigs,
  MANIFEST.tsv (every URL, status, size), and the grab script
  — per the closed rescue sweep, the last retrievable copies of
  everything 403-at-origin
## Cold boot round (17:13, `tv-ex725-coldboot.pcap`) — WsIndexes discovery

Wall unplug 15s → full cold boot. Sequence: DHCP (17:13:32) → fresh
DNS (resolver cache gone) → **ssm STVgetTime** clock sync → applicast
DNS → **HEAD `/WsIndexes/AZ2_LA.xml`** revalidation → ssm TLS ×3 →
`upbookmark.ww.np.community.playstation.net` DNS. **No bundle digest
sweep** — confirmed absent by a 75s live listen. So: warm resume =
digest sweep, cold boot = clock+index revalidation. Two different boot
agendas; neither fetches an ssm update manifest (timestamp-gated
confirmed for both boot classes; the overdue-check powerup remains
the untested half).

The HEAD revalidation exposed a namespace the rescue sweep never
probed — **`/WsIndexes/`** (region×chassis widget-system indexes):

- **AZ2_LA (our EX725) & AZ3_LA (our HX855)**: 200, 1712B / 2443B —
  the authoritative installed-widget inventory. AZ2_LA: PHT_PhotoMap,
  BgmSearch/2.0.1, VideoExplorer/2.0.1, MusicExplorer/2.0.6, LogGate,
  BgmSearch-2ndDisp, VCServiceUtil. AZ3_LA adds SEN_Portal_DV
  ("Portal"), SEN_Portal ("HePortal"), SocialTV/EmotionPost,
  SocialTV/WatchingContent, MediaSearch/1.0.0/?from=GUIDE, and a
  PortalConfig. US/EU variants 200; GB/BR/XLA + bare Index = 403
  (never existed).
- **`/WsCatalogs/`** (locale-keyed catalogs): 13 fetched 200 incl.
  `AZ2_LA_ALL_por.xml` / `AZ3_LA_ALL_por.xml` — the live route to
  BRA/por catalog content the gallery path 403s on. Schema: Category
  Widgets/Applications; Application entries use `pack:VideoExplorer/`
  icons, `data='{"mode":"text_search","from":"NUX"}'`, `filter="hotel"`,
  `{MvCatalog::STRING}` i18n refs.
- **`/WsBundles/`**: PHT_PhotoMap_AZ2 info.xml 200 (profile **AC1.0**,
  first live AC1.0 sighting) — digest 403 (origin-gated, unlike the
  playstation host).

## ws-lane enumeration (17:20) — four live bundles, fully archived

Digest-driven enumeration of every file the digests name —
`applicast-fetched/ws-lane/` (46×200, MANIFEST.tsv):

- **MediaSearch/1.0.0** complete: widget XML + `MediaExplorerCommon.txt`
  (112KB) + `MediaSearch.txt` (**1.2MB**). Both .txt are
  `JAVA_SCRIPT_BUNDLE_VERSION_1.0.11` concatenated-JS bundles mounted
  via XGML `<bigfile>` (`mediaCommonRes:` / `mediaSrhRes:` mountpoints)
  — 69+13 modules incl. the full `MSSrv*` service stack.
  **MediaSearch is search/metadata only** (Kamaji = Sony's metadata
  service): `MEDIASEARCH_KAMAJI_URL =
  portal.store.sonyentertainmentnetwork.com/kamaji/api/haku/00_0…`,
  `MEDIASEARCH_SPGS_URL = guide.np.ac.playstation.net`. This is the
  source of the cold-boot `upbookmark` DNS (bookmark service).
  No player-launch API in it — `_doExecuteWidget` is internal-only.
- **SEN_Portal** ("HePortal") complete, 13/13 files incl.
  **`encryption.enc.js` (304B, binary — encrypted JS, same pattern as
  VCServiceUtil's main.enc.js)** and **`common.key` (384B raw)** —
  the widget-preference crypto material, in-scope (not DRM).
- **SEN_Portal_DV** ("Portal") complete: canvas.xml/dicutil.js/canvas.js.
- **SocialTV/WatchingContent** complete: server.xml + server.js (22KB).
- **VideoExplorer/2.0.1 and MusicExplorer/2.0.6: gone from the CDN**
  (every layout variant 404s) — the TVs' installed copies and the
  Wayback `MediaExplorerCommon.img` (123KB) are what remains.

## Media-player lane opened (user goal)

The user's actual playback pain: Serviio-served videos fail on
newer HDR/high-res content even with transcoding enabled; no audio
stream selection (dual-audio + dual-SRT library). Findings so far:

- The widget runtime cannot add codecs — 2011 AZ2/AZ3 silicon has a
  hard decode ceiling (AVC ≤ ~High L4.1, MPEG-2, no HEVC/10-bit/HDR).
  Failures with "transcoding on" point at Serviio remuxing instead of
  transcoding (codec matches → profile/level/pixel-format over spec)
  or transcode targets above the decoder.
- Track selection must be **server-side**: era players ignore DLNA
  track-selection extensions. Serviio per-stream audio selection +
  subtitle burn is the workable fix; a proper "Sony BRAVIA 2011
  (AZ2/AZ3)" Serviio profile is the upstream contribution candidate.
- Plan: firewall capture of a **failing** play attempt (TV ↔ Serviio)
  → exact DLNA profile string + where playback dies → craft profile →
  contribute upstream. Widget lane complements as the better front-end
  (browse, pick audio/sub before play, hand native player a
  track-preselected URL).

## Artifacts (this round)

- `tv-ex725-coldboot.pcap` — cold boot (DHCP→STVgetTime→WsIndexes
  HEAD→TLS; no sweep)
- `applicast-fetched/WsIndexes/` — 6 live system indexes (.xml) +
  7×403 bodies (.403body)
- `applicast-fetched/ws-lane/` — 13 catalogs + 4 complete bundles +
  digests + MANIFEST.tsv (2.0MB)
- `certs/opera-rootstore/roots/` — **complete era root store,
  302/302 certs** (paced Wayback retry landed)
