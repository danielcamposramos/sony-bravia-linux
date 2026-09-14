# BIV (BRAVIA Internet Video) lane — live recon 2026-09-13

Context: owner opened `Conteúdo de Internet` → `BRAVIA Internet Video` →
`Serviços e conteúdo da internet` on both TVs (EX725 = 192.168.0.22, HX855 =
192.168.0.21). Everything below was observed on our own hardware/LAN.

## 1. Headline findings

1. **Digital Concert Hall is LIVE and executing on the HX855 (2026-09-13).**
   The Berliner Philharmoniker service client loaded end-to-end: the set's
   era Opera-based browser app fetched live content from DCH's own servers,
   presented a 7-day-trial/login wall. The provider being alive is what keeps
   an era service alive — the TV's client stack is fully functional.
2. **The registration portal is ALIVE.** https://internet.sony.tv (Apache/AWS)
   302s to /customer/ serving the real pt-BR "Essentials" portal
   ("Cadastre seus produtos habilitados para o Sony IP…"). The EX725 was
   registered through it tonight (fresh Essentials account + code `CZKJE`);
   the TV confirmed registration within minutes.
3. **The BIV service grid still fetches icons live over plain HTTP from
   Akamai** (`static.internet.sony.tv` → `static-internet-sony-tv.edgekey.net`
   → `e2188.d.akamaiedge.net`, GET `/bivl-ww/static/service/icons/service_N/h.png`
   → 200). 12 of 30 probed icon slots rescued; the lane's content dates to
   ~2008 (a "Hancock — in theatres July 3" promo icon sits in it).
4. **Service lists are local, not fetched.** Opening the service menu causes
   no new DNS lookups; only the grid render pulls the icon lane. The
   provisioning backend is `ssm.internet.sony.tv` (AWS round-robin; one IP,
   52.39.176.193, identified from TLS sessions + current DNS).

## 2. Registration gate and outcome

- EX725 (pre-registration): `Ativar Funções Avançadas` gate with EULA pointing to
  https://internet.sony.tv + registration code `CZKJE`. Netflix absent.
- HX855 (owner-registered years ago): lists **Netflix, Digital Concert Hall**
  and the registration form; DCH loads after accepting a mixed-content prompt.
- **EX725 registered 2026-09-13, outcome: UNLOCKED NOTHING.** Registration
  completed mechanically (fresh Essentials account, TV confirmed "registered"
  within minutes), but the advanced-content library rendered empty. Wire
  proof: the whole post-registration window (pcap `tv-ex725-reg.pcap`,
  684 packets) is TLS-only to `ssm.internet.sony.tv` — zero port-80, no icon
  lane, no service list, no content endpoints. The gate machinery is alive;
  the catalog behind it is gone.
- Interpretation (right-to-repair framing, live-proven): era services are
  **server-side killable and killed**. The HX855 still shows Netflix/DCH
  because those entries were written to the set's local storage while Sony
  still provisioned them; a set registering in 2026 receives an empty
  provision. Same hardware, same gate — the difference is purely Sony-side.
  The 855's surviving local service entries are therefore preservation-
  valuable (firmware-lane extraction candidate).

## 3. Digital Concert Hall endpoint map (HX855 DNS, 22:56–22:57 local)

```
tv.digitalconcerthall.com      api.digitalconcerthall.com
images.digitalconcerthall.com  usage.digitalconcerthall.com
errors.digitalconcerthall.com
certs.opera.com  xml.opera.com  crl3.digicert.com   (browser cert machinery)
ssm.internet.sony.tv                              (provisioning poll)
```

The mixed-content prompt is the era browser's certificate/content check
(Digicert CRL fetch) — and the user's accept shows the browser lane will
render plain-HTTP assets alongside TLS pages. DCH playback session itself
was not captured (we sniff the EX725, not the workstation monitor set);
a 30-second HX855 capture during DCH playback remains a to-do.

## 4. Rescued BIV icon lane

`/tmp/acig-/bivl-archive/static/service/icons/` — 12 PNGs (86x36 RGBA):
service_0,1,6,8,9,10,11,14,15,19,26,28 `_h.png`; only `h.png` exists
(f/m/l/n probes: 0 hits). Vision-model readings (2 consistent passes) with
era-record cross-check:

| # | Reading | Confidence |
|---|---|---|
| 1 | Amazon Instant Video | confirmed era partner |
| 6 | Dailymotion | confirmed era partner |
| 26 | "Tube" → YouTube | confirmed partner (partial text) |
| 10 | "Hancock in theatres July 3" poster | Sony Pictures promo, dates lane to 2008 |
| 11 | Howcast | plausible (era channel) |
| 9 | Ford Models | plausible (era channel) |
| 19 | Slacker | plausible (era channel) |
| 0, 8 | blank/near-blank | possibly retired-service placeholders |
| 14 | "ustudio" | unverified reading |
| 15 | "PEARL" | unverified reading |
| 28 | red/gold swoosh, no text | unknown (candidates: blip.tv, FEARnet, C-Spot) |

Ground-truth cross-check against the on-screen grid names is pending.
Contact sheet: `service-icons-sheet.png` (+ 4x upscale `-4x.png`).

## 5. Origin enumeration sweep (same night)

Full report: `origin-sweep-2026-09-13.md` (this directory). Summary:

- 896 probes on `applicast.ga.sony.net` (64 names × 14 paths): 33×200, 863×403,
  **zero 404** — denial is uniformly 403 (ambiguous exists/absent).
- **The 24 lost SNY_ bundles are 403 on every path shape** while non-SNY names
  serve 200 on identical paths → an **ACL on the SNY_ namespace**. Their rescue
  lies off-origin (TV local cache, Wayback, mirrors).
- 12 open bundles fully rescued via manifest-guided deep fetch, **117 files
  SHA256-verified against Sony's own signed manifests, 0 mismatches**:
  AppDataSourceAddon (+_FY14, _tmp, _FY14_tmp), BgmSearch-2ndDisp_FY13,
  BgmSearchService_FY14, CrossSearchUtil, CsxLog, CsxLog_FY14,
  RecommendationSettings, SEN_AppList, SocialViewing_Secure.
- **Key material rescued:** 4 generations of `plugins/kamaji/kamajiapps.enc.js`
  (encrypted app-store list) each alongside `common.key` (384 B raw
  high-entropy), plus `server.enc.js` and `secretsenc.js`. The widget runtime
  decrypts `encrypted=` script includes natively — a firmware-lane study item.
- Evidence archive now: **474 files / ~2.98 MB** at
  `/tmp/acig-/applicast-archive/` (+26 BIV-lane files in `/tmp/acig-/bivl-archive/`).

## 6. App-list architecture (from rescued sources)

`AppDataSourceAddon` (2014 Sony source, FY14) merges three app sources into
the portal list — `plugins/local/localapps.js` (preset apps from
`preset.json` + URI mapping `mapping_WW.json`/`mapping_JP.json`),
`plugins/android/androidapps.js`, and the encrypted
`plugins/kamaji/kamajiapps.enc.js`. Special apps map to
`localapp://biv/<serviceId>` via `bivl.getServiceIdByType()`; service info
carries a `cacheable` flag (USB cache). `SEN_AppList` (SWA1.1 profile) is the
renderer, `localStorage key="portalStorage"`, registry `dtv/X2WS`.

## 7. Implication for the project goal (media player)

The DCH session is an existence proof that the service-app route can reach
the goal without writing a native player: a service client is an era Opera
app + provider media endpoints, and mixed plain-HTTP content is accepted.
A "Serviio-equivalent" service on 192.168.0.60 serving an era-compatible app
that streams from a LAN media library is therefore plausible IF (a) we learn
how service entries are provisioned (the 2026-09-13 EX725 registration
session is captured — pcap `tv-ex725-reg.pcap`, 11 TLS sessions to ssm,
payloads opaque), and (b) we identify the streaming pipeline the era browser
uses (DCH playback capture on the HX855 pending; era Opera has no reliable
HTML5 video, so Sony's service-player API is the likely mechanism).

## 8. Open items

- What the EX725's registration unlocked (behavioral delta on screen + pcap).
- DCH playback capture on HX855 (30 s) to identify the streaming protocol.
- Icon ↔ on-screen grid ground-truth mapping.
- `common.key` / `*.enc.js` decryption study (firmware lane).
- `CsxLog_FY14` (enclave.js 36 KB, main.js 55 KB) + `SEN_AppList` list.js
  (42 KB) source study for service provisioning details.