# ApplicaCast Origin-Enumeration Rescue Report

**Origin CDN:** `http://applicast.ga.sony.net/` (pinned to CloudFront edge `13.225.205.93` for all fetches)
**Date:** 2026-09-13 · **Sweep scope:** 64 bundle names x 14 canonical URLs = **896 probes**, plus 8 manifest-driven deep fetches
**Archive root:** `/tmp/acig-/applicast-archive/` · **Sweep logs:** `/tmp/acig-/sweep/fetch-*.log.log`, `verify-CrossSearchUtil.log.log`
No probe or fetch touched the LAN TVs (192.168.0.21/22); nothing was written outside `/tmp/acig-/`.

---

## 1. Rescue tally

### 1.1 Direct probe saves (36 files)

| Bundle | Files saved | Bytes (where recorded) |
|---|---|---|
| WidgetBundles/AppDataSourceAddon | info.xml, digest.txt, digest.sig | 200, sizes unrecorded |
| WidgetBundles/AppDataSourceAddon_FY14 | info.xml, digest.txt, digest.sig | 200, sizes unrecorded |
| WidgetBundles/AppDataSourceAddon_FY14_tmp | info.xml, digest.txt, digest.sig | 200, sizes unrecorded |
| WidgetBundles/AppDataSourceAddon_tmp | info.xml, digest.txt, digest.sig | 200, sizes unrecorded |
| WidgetBundles/BgmSearch-2ndDisp_FY13 | info.xml, digest.txt, digest.sig | 200, sizes unrecorded |
| WidgetBundles/BgmSearchService_FY14 | digest.txt, digest.sig | (info.xml 403) |
| WidgetBundles/CrossSearchUtil | info.xml, digest.txt, digest.sig | 302 B, 1,038 B, 384 B |
| WidgetBundles/CsxLog | info.xml, digest.txt, digest.sig | 249 B, 1,076 B, 384 B |
| WidgetBundles/CsxLog_FY14 | info.xml, digest.txt, digest.sig | 249 B, 688 B, 384 B |
| WidgetBundles/RecommendationSettings | digest.txt, digest.sig | 311 B, 384 B (info.xml 403) |
| WidgetBundles/SEN_AppList | info.xml, digest.txt, digest.sig, icon.png | 439 B, 706 B, 384 B, 2,839 B |
| WidgetBundles/SocialViewing_Secure | digest.txt, digest.sig | 2,427 B, 384 B (info.xml 403) |
| WsBundles/XMB_AppliCast_AZ1_EU | info.xml | 139 B |
| WsBundles/PHT_PhotoMap_AZ1_EU | info.xml | 231 B |

**Total: 36 files.**

### 1.2 Deep-fetch rescues (8 bundles, 67 files, 67 hash-verified)

Every file listed in every open `digest.txt` was fetched from origin and **its base64 SHA256 digest matched the manifest exactly — 67/67, zero mismatches**.

| Bundle | Files fetched / verified | Key contents (sizes from fetch notes) |
|---|---|---|
| AppDataSourceAddon | 8 / 8 | info.xml, server.xml, util.js, plugins/local/localapps.js, plugins/kamaji/kamajiapps.enc.js (21,056 B), addon.js, server.js, **common.key (384 B)** |
| AppDataSourceAddon_FY14 | 10 / 10 | info.xml (267 B), server.xml (585 B), util.js (955 B), plugins/local/localapps.js (6,846 B), **plugins/android/androidapps.js (4,117 B)**, plugins/kamaji/kamajiapps.enc.js (23,872 B), json2.min.js (3,337 B), addon.js (1,995 B), server.js (4,288 B), common.key (384 B) |
| AppDataSourceAddon_FY14_tmp | 10 / 10 | same shape as FY14; kamajiapps.enc.js (23,952 B), common.key (384 B) |
| AppDataSourceAddon_tmp | 8 / 8 | same shape as base; kamajiapps.enc.js (23,104 B), common.key (384 B) |
| BgmSearch-2ndDisp_FY13 | 3 / 3 | info.xml (181 B), server.xml (195 B), server.js (9,510 B) |
| BgmSearchService_FY14 | 2 / 2 | BgmSearchServiceWidget.xml (211 B), BgmSearchServiceWidget.js (13,292 B) |
| CrossSearchUtil | 12 / 12 | info.xml (302 B), CrossSearchUtil.xml (1,155 B), CrossSearchUtil.js (4,459 B), TvMetaSupportedCountry.js (2,121 B), lib/{csxUtil,commonFunction,commandWrapper,errorHandler}.js (3,739/1,295/2,076/959 B), Util/{commandBase,csxCommandEngine,csxRankingCommands,registryUtil}.js (6,130/7,524/589/1,996 B) |
| CsxLog | 14 / 14 | info.xml (249 B), main.xml (830 B), languageCountryMap.js (5,541 B), util.js (3,305 B), json2.js (17,554 B), UUID.js (8,667 B), cdn.js (2,007 B), scalarWebApi.js (5,671 B), csx.js (33,512 B), regutil.js (1,383 B), blacklist.js (839 B), main.js (18,534 B), **server.enc.js (912 B)**, common.key (384 B) |

**Total: 67 files fetched, 67 verified.** Seven of these were re-fetches of probe-saved `info.xml` files (verified identical to manifest), so this sweep's distinct rescue is **36 + 60 = 96 files**.

### 1.3 Current on-disk state of this sweep's rescued bundles (filesystem-verified)

| Bundle directory | Files | Bytes |
|---|---|---|
| WidgetBundles/AppDataSourceAddon | 10 | 38,899 |
| WidgetBundles/AppDataSourceAddon_FY14 | 12 | 47,852 |
| WidgetBundles/AppDataSourceAddon_FY14_tmp | 12 | 48,139 |
| WidgetBundles/AppDataSourceAddon_tmp | 10 | 37,690 |
| WidgetBundles/BgmSearch-2ndDisp_FY13 | 5 | 10,498 |
| WidgetBundles/BgmSearchService_FY14 | 4 | 14,072 |
| WidgetBundles/CrossSearchUtil | 14 | 33,767 |
| WidgetBundles/CsxLog | 16 | 100,848 |
| WidgetBundles/CsxLog_FY14 | 3 | 1,321 |
| WidgetBundles/RecommendationSettings | 3 | 1,463 * |
| WidgetBundles/SEN_AppList | 4 | 4,368 |
| WidgetBundles/SocialViewing_Secure | 4 | 6,931 * |
| WsBundles/XMB_AppliCast_AZ1_EU | 1 | 139 |
| WsBundles/PHT_PhotoMap_AZ1_EU | 1 | 231 |
| **Sweep subtotal** | **99** | **346,218 (~338 KiB)** |

\* includes 3 files predating this sweep (RecommendationSettings/widget.xml 768 B; SocialViewing_Secure/canvas.xml 2,201 B + Weibo/), so the sweep's own contribution is 96 files.

The full archive (`/tmp/acig-/applicast-archive/`) now holds **428 files / 2,594,338 bytes**, the remainder coming from earlier phases (SNY_WidgetGallery 55 files/170,110 B, SNY_Facebook 24/385,467 B, SNY_Twitter 19/262,428 B, SNY_RSSReader 26/152,348 B, SNY_AudioControl 18/239,936 B, SNY_AudioControlApp 14/224,430 B, plus catalog/index snapshot dirs WsCatalogs, WidgetCatalogs, WidgetContents, WsIndexes, WidgetInfos, and dev-site captures).

**High-value captures this sweep:** four generations of `plugins/kamaji/kamajiapps.enc.js` (the encrypted Kamaji app-store list: 21,056 / 23,104 / 23,872 / 23,952 B) **together with `common.key` (384 B) in all four AppDataSourceAddon variants plus CsxLog**, and CsxLog's `server.enc.js` (912 B) — the key material and encrypted payloads that drive the TV's widget decryption path, all SHA256-verified against Sony's own signed manifests.

---

## 2. CDN access map — what Sony still leaves open

Aggregate of all 896 probes. **HTTP 200: 33 (3.7%) · HTTP 403: 863 · HTTP 404: 0.** The origin never returns 404 — denial is uniformly 403, so 403 is ambiguous between "exists, blocked" and "absent" (existence is only provable where a digest-signed 200 was recovered).

### 2.1 By first path segment

| Prefix | Probes | 200 | 403 | 200 rate | What is open |
|---|---|---|---|---|---|
| `WidgetBundles/<name>/…` | 320 (64x5) | 31 | 289 | 9.7% | only info.xml / digest.txt / digest.sig (+1 icon.png) |
| `WsBundles/<name>/info.xml` | 64 | 2 | 62 | 3.1% | XMB_AppliCast_AZ1_EU, PHT_PhotoMap_AZ1_EU |
| `WidgetInfos/<name>/<area>/<file>` | 512 (64x8) | 0 | 512 | 0% | **nothing** |

### 2.2 Within WidgetBundles, by file

| File | 200 | 403 | Open for |
|---|---|---|---|
| info.xml | 9 | 55 | AppDataSourceAddon, AppDataSourceAddon_FY14, _FY14_tmp, _tmp, BgmSearch-2ndDisp_FY13, CrossSearchUtil, CsxLog, CsxLog_FY14, SEN_AppList |
| digest.txt | 12 | 52 | the 9 above **plus** BgmSearchService_FY14, RecommendationSettings, SocialViewing_Secure |
| digest.sig | 12 | 52 | same 12 as digest.txt |
| icon.png | 1 | 63 | SEN_AppList only |
| icon-tiny.png | 0 | 64 | none |

Key asymmetry: **3 bundles serve digest.txt + digest.sig while info.xml is 403** (BgmSearchService_FY14, RecommendationSettings, SocialViewing_Secure) — the manifest is reachable even when the metadata is not, so digest.txt/digest.sig must be probed unconditionally.

### 2.3 Within WidgetInfos, by area_region_lang directory

| Locale dir | Probes | 200 | 403 |
|---|---|---|---|
| WW_ALL_ALL (description.xml, poster.png, icon.png) | 192 | 0 | 192 |
| LA_BRA_por/description.xml | 64 | 0 | 64 |
| US_USA_eng/description.xml | 64 | 0 | 64 |
| EU_ALL_eng/description.xml | 64 | 0 | 64 |
| JP_ALL_jpn/description.xml | 64 | 0 | 64 |
| LA_ALL_spa/description.xml | 64 | 0 | 64 |

WidgetInfos is fully closed at origin for every bundle and every locale probed — 0 of 512. All SNY_* consumer widgets are 403 across the board; every 200 in the sweep belongs to a non-SNY system/service bundle or a WsBundles appliance entry.

---

## 3. Per-lost-bundle status (the 24 SNY widgets)

For each of the 24, the full 14-URL probe block (5 x WidgetBundles, 1 x WsBundles, 8 x WidgetInfos) returned **403 on every URL**. Nothing was recovered for any of them — no metadata, no manifest, no icon, no code.

| # | Bundle | info.xml | digest.txt/.sig | icons | WsBundles info.xml | WidgetInfos (all locales) | Recovered |
|---|---|---|---|---|---|---|---|
| 1 | SNY_Clock | 403 | 403 | 403 | 403 | 403 (WW/LA/US/EU/JP) | nothing |
| 2 | SNY_Dailymotion | 403 | 403 | 403 | 403 | 403 | nothing |
| 3 | SNY_Deezer | 403 | 403 | 403 | 403 | 403 | nothing |
| 4 | SNY_Ebay | 403 | 403 | 403 | 403 | 403 | nothing |
| 5 | SNY_Epilot | 403 | 403 | 403 | 403 | 403 | nothing |
| 6 | SNY_Flickr | 403 | 403 | 403 | 403 | 403 | nothing |
| 7 | SNY_HomeNetwork | 403 | 403 | 403 | 403 | 403 | nothing |
| 8 | SNY_Napster | 403 | 403 | 403 | 403 | 403 | nothing |
| 9 | SNY_News | 403 | 403 | 403 | 403 | 403 | nothing |
| 10 | SNY_PanelApp | 403 | 403 | 403 | 403 | 403 | nothing |
| 11 | SNY_PhotoFeed | 403 | 403 | 403 | 403 | 403 | nothing |
| 12 | SNY_Quality | 403 | 403 | 403 | 403 | 403 | nothing |
| 13 | SNY_Radio | 403 | 403 | 403 | 403 | 403 | nothing |
| 14 | SNY_RSS | 403 | 403 | 403 | 403 | 403 | nothing |
| 15 | SNY_SetupAssist | 403 | 403 | 403 | 403 | 403 | nothing |
| 16 | SNY_Shopping | 403 | 403 | 403 | 403 | 403 | nothing |
| 17 | SNY_Slacker | 403 | 403 | 403 | 403 | 403 | nothing |
| 18 | SNY_SonyChannel | 403 | 403 | 403 | 403 | 403 | nothing |
| 19 | SNY_SonyWidget | 403 | 403 | 403 | 403 | 403 | nothing |
| 20 | SNY_Sports | 403 | 403 | 403 | 403 | 403 | nothing |
| 21 | SNY_Stocks | 403 | 403 | 403 | 403 | 403 | nothing |
| 22 | SNY_TrackID | 403 | 403 | 403 | 403 | 403 | nothing |
| 23 | SNY_VideoUnite | 403 | 403 | 403 | 403 | 403 | nothing |
| 24 | SNY_Weather | 403 | 403 | 403 | 403 | 403 | nothing |

The deny is total and name-scoped: identical system paths (WidgetBundles/X/info.xml) return 200 for AppDataSourceAddon et al. and 403 for every SNY_ name, so the block is an ACL on the SNY_ namespace, not a global takedown. Rescue avenues for the 24 therefore lie outside this origin (LAN TV cache extraction, Wayback, third-party mirrors), not in further URL guessing on applicast.ga.sony.net.

---

## 4. Completeness verdicts from deep fetch

| Bundle | Manifest entries | Fetched | SHA256-verified | Verdict |
|---|---|---|---|---|
| AppDataSourceAddon | 8 | 8 | 8/8 | **COMPLETE** — includes common.key + kamajiapps.enc.js |
| AppDataSourceAddon_FY14 | 10 | 10 | 10/10 | **COMPLETE** — adds androidapps.js + json2.min.js |
| AppDataSourceAddon_FY14_tmp | 10 | 10 | 10/10 | **COMPLETE** — pre-existing info.xml re-verified identical |
| AppDataSourceAddon_tmp | 8 | 8 | 8/8 | **COMPLETE** |
| BgmSearch-2ndDisp_FY13 | 3 | 3 | 3/3 | **COMPLETE** |
| BgmSearchService_FY14 | 2 | 2 | 2/2 | **COMPLETE** (fetched despite its info.xml being 403) |
| CrossSearchUtil | 12 | 12 | 12/12 | **COMPLETE** — one file needed a re-fetch (trailing-newline miss), then verified |
| CsxLog | 14 | 14 | 14/14 | **COMPLETE** — includes server.enc.js + common.key |

**8/8 bundles COMPLETE, 67/67 files hash-verified against Sony's signed manifests, 0 mismatches.** Not yet deep-fetched despite open digests: **CsxLog_FY14** (digest.txt 688 B + digest.sig on disk, no manifest walk yet), **RecommendationSettings** (digest.txt 311 B), **SEN_AppList** (digest.txt 706 B), **SocialViewing_Secure** (digest.txt 2,427 B) — these four are the immediate next deep-fetch targets.

---

## 5. Recommended next enumerations

Ranked by observed success rate; every recommendation follows from a 200 pattern in this sweep's data.

1. **Deep-fetch every open digest.txt (4 pending).** The manifest walk is the proven exploit: 8/8 bundles, 67/67 files HTTP 200 and hash-verified, including bundles whose info.xml is 403. Pending: CsxLog_FY14, RecommendationSettings, SEN_AppList, SocialViewing_Secure.
2. **Probe digest.txt/digest.sig unconditionally, independent of info.xml.** Three bundles opened only through their digests; an info.xml-first strategy would have missed them.
3. **Expand WidgetBundles name enumeration.** 12 of 40 probed non-SNY names had at least one 200. High-yield unprobed candidates: mined names **SNY_AudioControl, SNY_AudioControlApp, SNY_Facebook, SNY_RSSReader, SNY_Twitter, SNY_WidgetGallery** (rescued earlier via other sources, but their WidgetBundles digests were never probed on this origin), plus system names adjacent to the opens: VCServiceUtil (2 files already on disk from earlier phases), Discovery, DEV (9 files on disk), BgmSearch, CrossSearch, CsxAccessor, LogGate, AutoChannelMapping.
4. **Suffix variants on every open base name.** `_FY13`, `_FY14`, `_tmp` each produced opens (BgmSearch-2ndDisp_FY13, BgmSearchService_FY14, AppDataSourceAddon_FY14/_tmp, CsxLog_FY14); `_Secure`, `_Bundles`, `_CN` produced none in this probe set but only 2-4 names each were tried. Try CrossSearchUtil_FY14, SEN_AppList_FY14, CsxLog_FY13, AppDataSourceAddon_FY13, etc.
5. **Expand WsBundles with appliance-style names.** Both WsBundles 200s are appliance/XMB names (`XMB_AppliCast_AZ1_EU`, `PHT_PhotoMap_AZ1_EU`); the local archive already holds `PHT_PhotoMap_AZ1_US`, `_AZ2`, `_AZ3` info.xml from earlier phases, confirming the `_AZ<N>_<region>` family — enumerate more of it.
6. **Probe icon.png on every candidate bundle.** SEN_AppList returned 200 for icon.png while icon-tiny.png was 403; icon availability is per-file, not per-directory.
7. **Use the mined manifestPaths as the inner-file dictionary** for any newly opened digest: info.xml, widget.js, layout.xml, layout_fullscreen.xml, widget_fullscreen.js, sha1.js, util.js, dateFormat.js, tw.js, encryption.enc.js, common.key, main.enc.js, canvas.xml, canvas.js, canvas-*.css, notification.*, dock/*, canvas/*, dic/dicutil.js, common/data.js, common/ceccommandcontrol.js — the dock/../ and canvas/../ relative forms resolve to these after normpath.
8. **Deprioritize WidgetInfos.** 0/512 at origin across all probed bundles and locales; only remaining untested variants are `thumbnail.png` (mined, never probed) and the ~19 additional EU locale dirs beyond EU_ALL_eng (bul, cat, cze, dan, dut, est, fin, fre, ger, gre, hgb, hun, ita, lav, nor, pol, por, rum, rus, slo, slv, swe, tur) plus US_ALL_eng/US_BRA_por — cheap to try once on an open bundle, but the evidence says closed.