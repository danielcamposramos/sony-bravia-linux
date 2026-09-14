# Programming AppliCast Widgets on KDL-46EX725 / KDL-46HX855

**Widget-platform research reference for the sony-bravia-linux project**
Date: 2026-09-13 · Primary evidence: live-mirror of applicast.ga.sony.net at `/tmp/acig-/applicast-archive/` (30 bundles, ≥4 complete) and repo copy `/K3D/GitHub/sony-bravia-linux/docs/research/liverecon/applicast-fetched/` (126 files, 2.2 MB, MANIFEST.tsv); pcap wire research in `docs/research/liverecon/applicast-widgetlane.md`; external research in `docs/research/webfindings.md`.

Confidence legend: **[V]** = adversarially verified this project (refutation attempt failed, multi-bundle provenance proven); **[C]** = corroborated by ≥2 independent first-party bundles but not adversarially verified; **[I]** = inference, single-source or untested.

---

## 1. The widget platform

### 1.1 Two TVs, two runtime generations

| | KDL-46EX725 | KDL-46HX855 |
|---|---|---|
| Chassis generation | AZ2 (2011, "Zeus" family) | AZ3 (2012, "Phoenix" family) |
| Widget runtime (UA on wire) | `WidgetSystem/3.0.9` | `WidgetSystem/4.0.4` |
| Widget CDN | applicast.ga.sony.net (HTTP :80, plain) | same, plus a second widget system (SocialTV/EmotionPost) on bravia.dl.playstation.net |
| Chassis path in catalog | `AZ2` | `AZ3` (but see §7 Q4 — the gallery's notification view hardcodes AZ2) |

Both TVs speak plain HTTP :80 to applicast.ga.sony.net (CloudFront → S3, CNAME `tv-applicast-ga.update.me.sony.com`). The store's remaining catalog inventory is Facebook + Twitter, both `status='Deleted'` since 2011-04-01 — the era store is dead; the delivery lane is not.

### 1.2 Profile ladder

AppliCast had two platform families:

**Japan / AC profiles (AC1.0 → AC2.0 → AC2.1).** The publicly documented one. Developer program ran 2008–2012 (site: www.jp.sonystyle.com/Taiken/Original/Applicast/, later sony.jp); geekpage.jp tutorial series still live; SDK (emulator + 3 spec PDFs + sample zips) is **lost** from public archives. Japan sets officially ran unsigned USB widgets — **this does not apply to our Brazilian sets** (international platform, no USB widget path is known to exist). The AC2.1 profile is the simplest authoring surface observed anywhere (see §2, §5).

**International / "X2 widget system" profiles (SAX1.0/SAX1.1, SWA1.0, WAA1.0).** Registry namespace `dtv/X2WS` (hence "X2WS"). Never had a public SDK; semantics recoverable only from the bundle corpus — which our project holds. The unsanitized dev comment in SNY_AudioControl/info.xml names the ladder directly: `<profile spec='SAX1.0'/> // AZ2以降ではSWA1.0` ("on AZ2 and later it's SWA1.0").

Profile semantics as reconstructed from bundles:

| Profile | Seen in | Layout | Storage | Notes |
|---|---|---|---|---|
| **AC2.1** | SNY_RSSReader (served from the **GA** CDN — i.e., international TVs got it) | `layout.xml` + `layout_fullscreen.xml`, `<Widget>` tree: Component/Bitmap/Text/Memo2D/RichText/Prim | engine `getStoredValue`/`widget.preference` + `setRegistry/getRegistry` | fullscreen context via `changeToFullscreen()`; `<fullscreen>1</fullscreen>`, `<duplicable>1</duplicable>`, `<preference>1</preference>` |
| **SAX1.0 / SAX1.1** | SNY_AudioControl (AZ1) / SNY_Facebook, SNY_Twitter | XGML dock (280×165) + optional canvas | `widget.registry.getItem/setItem` (SAX) | dock+canvas dual view; `canvas.open()/close()` |
| **SWA1.0** | SNY_AudioControlApp (AZ2+) | XGML dock + canvas (HD_QUARTER 480×1080) | `registry.extension` under `dtv/X2WS`, packed ≤1024-char slots | runtime branch on `widget.profile.indexOf('SWA')==0` |
| **WAA1.0** | SNY_WidgetGallery, SNY_Facebook canvas view | XGML canvas, `mode='HD_HALF'` | `registry.extension` + `dock.*` + `canvas.*` integration | the gallery IS a WAA1.0 widget — the reference implementation of the whole install/store UI |

Chassis capability mapping (from bundle code, all [C]): `system.version` major 3 = AZ2-era runtime (EX725), major 4 = AZ3 (HX855); `system.version` can be undefined on 2010 Odyssey/AZ1 firmware. dicutil.js branches "Zeus 2011" (major 3) vs "Phoenix 2012" (major 4). The EX725 therefore runs a runtime that natively understands SAX1.1, SWA1.0, WAA1.0 — and demonstrably was served an AC2.1-profile bundle (RSSReader) by Sony's own GA CDN, so AC2.1 acceptance is likely but untested on the wire for our specific sets (§7 Q2).

---

## 2. The programming model

### 2.1 Markup vocabulary

**AC2.1 (layout.xml)** — declarative node tree, no CSS:
- `<Widget>` root; `<Component name visible>` containers (all mode switching done in JS via `setVisible`)
- `<Bitmap name x y w h scale>` — image node; PNG supplied at runtime via `loadImage(node, path)`
- `<Text>` single-line; `<Memo2D>` multi-line pane (`scroll`, `lines_max`, `exceed_dot`, `fade_frames`, `wordwrap_mode`, `buf_size` — an explicit string memory budget); `<RichText>` marquee (`scroll_speed_x`); `<Prim type='rect'>` vector rectangle
- Coordinates: origin at widget **center** (partscreen 280×165 → x −115..118; fullscreen ~960 wide → x −436..436)

**XGML (SAX/SWA/WAA)** — canvas/dock layouts, plus CSS:
- `<xgml>` root; `<meta>` with `<script src>` and `<style src>` includes (three CSS files loaded together: common + fhd + wxga); `<script encrypted='encryption.enc.js'>` for encrypted scripts
- Elements: `component` (nav_left/nav_right/nav_up/nav_down declarative focus graph), `image`, `image3x3` (nine-slice), `text`, `rich_text`, `bitmap`, `auto_layouter` (flow layout, `.lineCount`), `scroll_clip_pane`, `prim`
- CSS dialect: element/.class/#id selectors; properties x, y, width, height, alpha (0–255), visibility, color, font-size, text-align, spacing-v, scaleX/scaleY (WXGA panels are handled by scaling the whole widget by 768/1080 × 1366/1920)
- info.xml is **comment-tolerant** (Sony ships `//` comments after elements in it) and declares: `<profile spec>`, `<name lang>` ×30–40 locales, `<layout view='dock|canvas|notification' type='xgml' src mode width height>`, `<registry path='dtv/X2WS'/>`, and profile-specific flags (`duplicable`, `preference`, `fullscreen`, `width/height`)

### 2.2 JS API surface

**Adversarially verified engine globals [V]** (proven engine-provided: never defined in any bundle, consumed bare at top-level scope by ≥5 independently signed bundles):

- **`widget`** — host object. `widget.uri` (launch URI **including query string** — bundles do `widget.uri.split("?",2)[1]`; also base for OAuth helper pages), `widget.name`, `widget.mode` (read/write: 'HD_FULL'/'HD_THIRD'/'FULL'), `widget.profile` (e.g. 'SAX1.0'), `widget.preference.getItem/setItem/open`; callbacks `onload`, `onactivate`, `onunload`, `onkeydown(key)`, `onkeyup(key)` (boolean return; false = consumed), `onmodechange`; `widget.optionMenu.global` + `onselect` (develop mode only)
- **`system`** — `modelName` (full 'KDL-46HX855' string), `country` (ISO-alpha-3, 'BRA'), `language` (3-letter dic code, 'por'), `panelType` (compare `System.PANEL_TYPE_WXGA`), `version` (dotted; '3.0.0'/'3.0.1' special-cased for a dock-persistence bug workaround), `isFeliCaSupported` (may be undefined on old firmware — bundles regex-fake it from modelName)
- **`System`** — constants namespace: `PANEL_TYPE_WXGA`, `PANEL_TYPE_FHD`, `COLOR_KEYS_LAYOUT_BRGY/RGYB/YBRG`
- **`KeyEvent`** — `KEY_CODE_LEFT/RIGHT/UP/DOWN/CONFIRM/CANCEL/BLUE/RED/GREEN/YELLOW`
- **`Debug`** — `printInfo/printWarn/printError` (note: engine logs max ~1024 bytes/message, per a FIXME in gallery code)
- **`document`** — XGML DOM: `getElementByName(name)` (**singular**, name-not-id — zero getElementById anywhere), `createElement('image'|'text'|'rich_text'|'component'|'auto_layouter'|'scroll_clip_pane')`, `activeElement`, `addEventListener/removeEventListener/dispatchEvent`; nodes have `appendChild/removeChild/insertBefore/hasChildNodes`. Parsed data XML (xhr.responseXML) is a *separate* API: `getElementsByTagName`, `getAttribute`, `childNodes` — NOT W3C (no getElementById, no textContent, no querySelector)
- **Element/node API** — `loadAsync(url, new ImageLoadParam())` / `abortLoad()` / `destroyTexture()`, `setStr(str, flag)`, `.strW`, `.lineCount` (AZ2+ only), `.computedStyle`, `.style.{x,y,width,height,visibility,alpha,color,fontSize,textAlign,lineHeight,scaleX,scaleY,...}`, `scrollChildComponents(dx,dy,ScrollClipPane.ANIMATION_TYPE_LINEAR)`, `startScroll()/stopScroll()` on rich_text; engine classes `Element/Component/Text/RichText/Image/Image3x3/Document/XMLDOM` exist as globals (WidgetGallery patches their prototypes)

**Corroborated engine globals [C]** (multi-bundle, not adversarially verified):

- **`XMLHttpRequest`** — async GET (and POST in SAX1.1 Facebook) only; `readyState==4`, `status` 200; status 0 = "timeout or oversize response" per Facebook error handling; no ontimeout (manual watchdog timers everywhere), no header-set usage except one Range-trick; Facebook uses a proprietary 6-arg `open(method,url,true,null,null,false)`; AC2.1 uses `getResponseHeader("CONTENT-LENGTH")` for size caps; `eval()` of responseText is permitted (dictionaries, JSON)
- **`registry` / `Registry`** — `registry.extension.get/set(path, Registry.DATA_TYPE_STRING|DATA_TYPE_LONG)` under `dtv/X2WS`; serialization in gallery is Foo.freeze — **eval-able JS source, not JSON**
- **`canvas`** — `canvas.open(id)` / `canvas.close()` (dock↔canvas view switch)
- **`dock`** — `isAdded(id)`, `widgets` (cap 50), `open(id,name)`, `open()` (dock UI), `add(id,name,notify)`, `remove(id)` — widget-manager integration
- **`execBrowser(url)`** — hand URL to TV web browser
- **`hdmiCec` / `HdmiCec`** — the headline capability of the AudioControl bundle: `sendVendorCommand(dest, sonyOpcode16, operand[], flags, cb)`, `sendUserControlCommand`, `oncommandreceived` (every vendor frame with sender/isbroadcast/opcode/operand), `ondevicesupdated`, `isConnected(addr)`, `isControlEnabled()`. A docked widget can sniff and drive the CEC bus (Sony 0xF000–0xF244 sub-opcode space; power via User Control 0x6D/0x6C)
- **`Animator` / `KeyFrameMotion`** — tween engine: `motion.<prop>_goalValue/_duration/_durationType/_curveType/_interpolationType`, `animator.startMotion/finishMotion`; animated props observed: x, y, w, h, a (alpha), x2d, y2d, scaleX
- **`audibleFeedback.play(TYPE_KEY)`**, **`prompt(title, default, ?, callback)`** (native text dialog), **timers** (setTimeout/setInterval; engine does NOT clean them up on context switch — every bundle defensively clears), **`screen.setLayout/mute/onresize`**, **`videoPlayer`** (global, init/open/play/close/onstatechange — decode on a dedicated input path; call `extInput.selectLastInput()` after close), **`hostApp.getItem('code')`** (browser OAuth handoff, Facebook only), **`print()`** (AC-profile debug)
- **AC2.1-only node-handle API**: `getNode(name)`, `getChildNode`, `setVisible(node,0|1)`, `setStr`, `setRGB`, `loadImage(node, path[, cb, maxH, maxW])`, `destroyImage`, `setW/setH/getW/getH`, `lineUp/lineDown/getLines`, `setAutoScroll`, `playAnimA`, `getStoredValue`, `setRegistry/getRegistry`, `getLanguage()`, `changeToFullscreen()`, `execMusicPlayer/MusicContent` (documented in commented-out code)

### 2.3 Lifecycle

**XGML profiles:** no main() — top-level IIFE runs at script evaluation; `widget.onload` → dictionary XHR + catalog load → init; `widget.onactivate` on user select; `widget.onkeydown/onkeyup` for remote (engine delivers only raw transitions — **key repeat is synthesized in JS**: 1000 ms delay, 100 ms interval); default unhandled keydown = spatial focus move via nav_* attributes; `widget.onunload` persists registry. Dock view (280×165) ↔ canvas view via `canvas.open()/close()`. Headless `notification` view exists (gallery's dock-sync — no UI).

**AC2.1:** engine parses layout.xml, runs widget.js top-level, calls `onLoad()`; three-state modal lifecycle via named handlers `onFocus()/onUnfocus()/onActivate()`; keys via `onUpKey()/onDownKey()/onLeftKey()/onRightKey()/onConfirmKey(type)` (type==0 = press); `changeToFullscreen()` switches to the fullscreen script context — the registry is the ONLY bridge between the two scripts; exit from fullscreen is engine-driven (RETURN key).

### 2.4 Engine-robustness rules a custom widget must respect (hard-won from Sony's own code)

- Timers are not cleaned up on context switches — clear everything defensively in every path
- "to avoid OOM error": force materialization of possibly-null XML strings via `new String(v).length`
- "to avoid timer queue problem": make spinner nodes visible before starting their interval
- buf_size on Memo2D is a real memory budget (3072/5120 bytes)
- Debug messages cap at ~1024 bytes
- AC-profile documented limits (geekpage, Japan-era, treat as guidelines): ≤48KB total code+layout+info+bg.png, max 3 concurrent XHRs, 1 s timer resolution (max 3 outstanding callbacks), PNG8, 300 KB memory normal/focus, 1.3 MB active
- Image loads fail gracefully via error callbacks — missing assets degrade, they don't crash

---

## 3. The install path — what our LAN server must serve

### 3.0 The two-layer protocol (wire-verified 2026-09-13 — rewrites the SDK-era map)

The SDK-era reconstruction below (§3.1–3.7, from canvas.js reverse engineering) turned
out to be the **inner lane** of a two-layer system. Live traffic on the EX725 after
the DNS override showed the full chain:

**Outer lane (the TV's own widget-menu protocol):**
1. `HEAD/GET /WsIndexes/AZ2_LA.xml` — per-chassis, per-area index (**LA**, not US;
   the SDK docs never mentioned an area token). Drives the widget MENU itself:
   serving 404 here made the whole widget-menu entry vanish from the XMB within
   one ~30 s poll; byte-exact deploy restored it within one poll. No reboot needed.
   (Caveat: before a reboot, the widget process holds cached resolver state and
   ignores DNS changes — the boot sweep re-resolves.)
2. `GET /WsCatalogs/AZ2_LA_ALL_por.xml` — per-language catalog chosen by country
   (Brazil → por). Lists the widget inventory for the XMB widget menu: the
   "Galeria Widget" (SNY_WidgetGallery, activation="notification" — i.e. the
   gallery is itself just a widget), Resident widgets (VCServiceUtil), dock
   widgets (Controle do Home Theatre), `pack: applications` entries, and
   playstation-served widgets (BgmSearch/VideoExplorer/MusicExplorer/SEN_Portal —
   these point at bravia.dl.playstation.net, NOT our lane; never touch that host).
3. `GET /WidgetBundles/<id>/...` — the WsCatalog's listed bundles install/update
   directly, WITHOUT the gallery: digest.txt/digest.sig/info.xml first, then the
   per-widget tree. This is how VCServiceUtil (Resident, encrypted: main.enc.js +
   common.key) arrived.

**Inner lane (the gallery widget, nested):** the SNY_WidgetGallery bundle's canvas
then fetches `WidgetContents/SNY_WidgetGallery/AZ2/Index.xml` → `Gallery_LA_BRA_por.xml`
→ `Catalog_LA_BRA_por.xml` → the four store widgets' bundles — the §3.1–3.7 chain
below, exactly as reconstructed from canvas.js, but with area token **LA** and a
`Gallery_{area}_{country}_{lang}.xml` naming layer the SDK docs lack.

Practical consequence for our server: **both layers must be served**, and the WsIndex
gates everything — a missing WsIndex doesn't degrade gracefully, it removes the
widget menu. Also: "regional availability" of any widget is pure server-side XML
(catalog entries); the TV's installer validates bundle signatures, not region of
origin — so a widget shipped US/EU/JP-only can be re-offered to the LA catalog, and
per-locale `description.xml`/Dic files are our translation surface.

### Step 0 — TV polls the CDN
The TV notices catalog/DNS changes within ~30 s via the XMB autonomous icon poll (pcap-verified). Requests carry UA `WidgetSystem/3.0.9` or `4.0.4`, plain HTTP :80, and **conditional GETs — honor If-Modified-Since with 304**; the cached copy becomes the trust anchor, so a stale-served 200 with unchanged content does nothing.

### Step 1 — `WidgetContents/SNY_WidgetGallery/{AZ2|AZ3}/Index.xml`
Gallery canvas.js fetches `../../WidgetContents/SNY_WidgetGallery/` + chassis, chassis chosen as `AZ3` if `parseInt(system.version)===4` else `AZ2`. So:
- EX725 (3.0.9) → **`/WidgetContents/SNY_WidgetGallery/AZ2/Index.xml`**
- HX855 (4.0.4) → **`/WidgetContents/SNY_WidgetGallery/AZ3/Index.xml`**
- ⚠️ The gallery's notification view (dock-sync) **hardcodes AZ2** — on the HX855 the two views can disagree. Serve both trees identically, or at minimum AZ2 correctly, until behavior is observed on the wire.

Index.xml format (data XML, not markup):
```xml
<Index>
  <gallery country="BRA" lang="por" src="path/to/Gallery.xml"/>
  <gallery country="ALL" lang="ALL" src="..."/>
</Index>
```
Scoring per `<gallery>`: start 1; country contains `system.country` → +0x4 (else discarded unless 'ALL'); lang contains `system.language` → +0x2 (same rule); `type` may contain 'felica' (+0x8 if FeliCa supported, else discarded — **leave type off entirely for Brazil**). Highest score wins, first-best kept. `src` may contain `{_area_}/{_country_}/{_lang_}/{_dicarea_}` dictionary tokens; resolved relative to the Index.xml URL's directory.

### Step 2 — Gallery XML (the winning src)
```xml
<Gallery>
  <screen name="main" layout="multi">
    <catalog src="Catalog.xml"/>
    <message title="..." body="..." headline="..."/>        <!-- optional -->
    <banner image="..." text="..." link="..."/>              <!-- optional -->
  </screen>
</Gallery>
```
Resume logic: the screen whose first `<catalog src>` equals the registry's `lastCatalogSrc`, else screen[0]. catalog src resolved against the Gallery URL's directory unless absolute http(s).

### Step 3 — Catalog XML (this is where OUR widget gets offered)
```xml
<Catalog updated="2026-09-13T12:00:00">
  <Category name="LAN">
    <Widget name="HelloLAN" status="" registration="dock" updated="2026-09-13T12:00:00">
      <id>LAN_Hello</id>
      <image>http://applicast.ga.sony.net/WidgetBundles/LAN_Hello/icon128.png</image>
      <information>http://applicast.ga.sony.net/WidgetBundles/LAN_Hello/information.xml</information>
      <provider>sony-bravia-linux</provider>
      <description>LAN hello world</description>
    </Widget>
  </Category>
</Catalog>
```
Rules the gallery enforces client-side: `status='deleted'` filtered out (and force-removed from dock by the notification view); `status='closed'` blocks display and auto-unregisters; `updated` (ISO8601, local time) is compared as epoch seconds against registry `dtv/X2WS/LastUpdated` in the headless notification flow — **newer widgets auto-register into the dock**: `registration='notification'` → `dock.add(id,name,true)`, `registration='dock'` → `dock.add(id,name,false)`, then LastUpdated is written. Detail-list icon URL is conventionally **widget id + 'icon.png'** (e.g. `LAN_Helloicon.png`).

### Step 4 — Information XML (Details page)
```xml
<information><detail>Text with literal \\n escapes</detail>
<provider>sony-bravia-linux</provider><contact>...</contact>
<url>http://lan-server/</url></information>
```
`url` opens in the TV browser via execBrowser.

### Step 5 — The bundle itself: `/WidgetBundles/<WidgetId>/`
File-by-file for an AC2.1-style minimal bundle (RSSReader-shaped):

```
WidgetBundles/LAN_Hello/
  info.xml               ← <Info>: profile spec, localized <name>, layout declarations,
                            width/height, duplicable, preference, registry path
  layout.xml             ← part-screen XGML/Widget tree (280×165)
  layout_fullscreen.xml  ← only if <fullscreen>1</fullscreen>
  widget.js              ← part-screen logic
  widget_fullscreen.js   ← only with fullscreen
  bg.png, icon.png       ← PNG (PNG8 safest)
  contact.xml            ← AC-profile contact block (present in era bundles)
  digest.txt             ← Name:/SHA256-Digest: manifest (see §4) — REQUIRED file
  digest.sig             ← 384-byte signature — REQUIRED file (content is the experiment)
  dic/<area>/<lang>.txt  ← only if the widget is localized (tab-separated, 4-col, '@'-terminated)
```
For an XGML (SAX/WAA) bundle instead: `dock/dock.xml`, `canvas/canvas.xml`, per-view JS/CSS trees, `img/{fhd,wxga}/`, and — only if we used encrypted scripts — `common.key` + `encryption.enc.js` in each view root (we won't; no secrets to protect, and the encryption scheme is unresolved). Note the verifier resolves digest paths **relative to each layout XML root**, so shared files appear once per view (`dock/../util.js` AND `canvas/../util.js` as separate entries — copy this convention exactly).

Also observed on the CDN: a `/WidgetInfos/<id>/...` tree (in our archive). Role not fully established (§7 Q5) — mirror the original structure for any widget id we list until observed on the wire.

### Step 6 — Dock registration and launch
After fetch, the installer (native "WidgetContents" sync channel) validates and installs; the gallery/notification view registers via `dock.add` as above; the widget appears on the AppliCast/XMB dock and launches with `widget.uri` pointing at our served bundle directory. All subsequent relative fetches (dic files, images, XHRs) resolve against that URI — **so a launched widget's XHRs stay inside our vhost automatically if we use relative paths**, and absolute `http://<lan-host>/...` URLs give us the "fetch from LAN server" demo.

---

## 4. The signature question

### What is established
- `digest.txt` is a JAR-manifest-style list (`Name: <path>` / `SHA256-Digest: <base64>`, LF-separated) covering code/layout/info (+dic/img/icon in some bundles, **code-only in others**); format is platform-wide across all three profiles and both runtime generations. All 18 Facebook entries re-verify today (0 mismatches) — Sony's signing pipeline was real and maintained.
- `digest.sig` is always exactly **384 bytes** = one RSA-3072 block, unique per bundle, raw opaque binary (not PEM/DER/PGP — `file(1)` misreports it). Most plausible: raw RSA-3072 signature over SHA-256(digest.txt), verified against a firmware-pinned Sony public key. **No public key exists in any bundle or on the CDN.**
- `common.key` (384 bytes, per-bundle, duplicated per view root) is a separate object: most plausibly an RSA-wrapped AES content key for `encryption.enc.js` (16-byte-block cipher). **Confidentiality, not authentication.** Irrelevant to us — we have no secrets and will ship unencrypted scripts.
- **Zero verification logic exists in any widget JavaScript** — enforcement, if real, lives in the native WidgetSystem runtime inside the firmware, which is whole-file encrypted with no public decryptor (SamyGO t=2430 hit the same wall in 2011).
- The TV honors conditional GETs/304s — signatures are at most an **install/update-time** gate; cached bundles are never continuously re-checked.

### Verdict: **ENFORCED — live-proven 2026-09-13 (~22:36–22:38 local, EX725). The installer verifies digest.sig over digest.txt BEFORE downloading body files; a foreign signature aborts the install at the header trio. Confidence: high.**
The mechanism is now located on the wire, in a single catalog pass where all
three arms were processed by the same TV within the same minute:

- **Arm A (control: byte-exact SNY_RSSReader clone, original digest.sig)** — installer
  fetched icon + `digest.sig` + `digest.txt` + `info.xml`, **then downloaded the body**
  (`widget.js` 60 826 B, `layout.xml` 8 964 B, `bg.png` 3 060 B), installed it, and the
  AppliCast/4.0/DTV runtime *executed the clone* (runtime fetches from
  `ARMA_RSSReader/./DIC/…` and `./PARTS/…` paths). It still runs on the dock as
  "Teste Assinatura A".
- **Arm B (byte-exact clone, foreign sig = SNY_Facebook's 384-B digest.sig)** —
  installer fetched the header trio, **never any body file**, across repeated poll cycles.
- **Arm B2 (unique content + accurately-recomputed digest.txt + foreign sig)** — same
  result: header trio only (3 consecutive poll cycles: 22:36, 22:37, 22:38), body never
  fetched. Opening it on the dock *did* launch an RSS reader — but the runtime fetched
  everything from the already-installed `SNY_RSSReader/` paths and nothing from the
  ARMB2 path: the TV ran the **cached original**, not B2's unique content (which would
  have shown "Teste ArmB2"). B2's `widget.js` was never downloaded at all.

Arm B2 was the decisive control for the alternative explanations: its digest.txt was
recomputed to accurately match its own content (kills "hash mismatch"), its info.xml
name was unique (kills "name collision/dedup"), and its content differed from the
installed original in `widget.js` + `info.xml` (kills "byte-identical content-dedup",
the confound that made Arm B v1 inconclusive when the TV mapped the dock entry to the
stored SNY_RSSReader copy). The only surviving variable across A vs B/B2 is the
signature on the manifest.

**Installer algorithm (as observed):** fetch icon + `digest.sig` + `digest.txt` +
`info.xml` → verify RSA-3072 signature (firmware-pinned Sony key) over the manifest →
only then download `widget.js`/`layout.xml`/assets. Dock registration is independent:
`dock.add()` fires from catalog parsing *before* any signature check, which is why
rejected bundles still appear on the dock (and why opening them falls through to a
locally installed widget — the "widget ativado" false positive that initially made Arm
B look like it ran).

**Consequences:** the resurrection lane (original signed bundles served from our LAN
vhost) is fully open — that is the preservation library. Third-party authoring is
closed at this gate without the Sony signing key (no public key exists in any bundle,
on the CDN, or in any SDK). Arm C (garbage/absent sig) is now moot for the enforced
branch — the remaining routes for custom code are firmware-side (UART/ABK-monitor),
where the runtime's pinned key would live.

No community shortcut exists. Nobody anywhere has publicly loaded a custom widget, bypassed, or forged digest.sig on this platform (systematic negative result across DDG/Bing/GitHub/Wayback; the only adjacent community thread — SamyGO t=2430 — never followed up).

### The decisive experiment (cheap, on our LAN) — RUN 2026-09-13, verdict above
With the Unbound override live and a working baseline (§6 phase 2), list the SAME unmodified original bundle (e.g. re-offer SNY_RSSReader's exact bytes) plus one byte-modified variant, in three arms:

1. **Arm A (control):** original files + original digest.txt + original digest.sig → expect install (proves the lane end-to-end). **RAN — installed and running.**
2. **Arm B (foreign sig):** original digest.txt + a *different bundle's* digest.sig (valid 384 bytes, wrong signature). **RAN twice (v1 byte-exact → dedup-confounded; v2 = B2, unique content → rejected).**
3. **Arm C (garbage/absent):** digest.sig = 384 random bytes, then deleted entirely. **Moot — B2 already answered the question.**

Observe per arm: does the widget appear in the gallery, does Confirm install it, does it launch, does any error dialog appear, what do the HTTP access logs show (does the TV even *fetch* digest.sig — if it never requests the sig, enforcement may be digest.txt-hash-only or nothing)? Outcomes:
- A installs + B/C rejected → **enforced**; the only remaining routes are firmware-side (UART/ABK-monitor) or finding the Sony key.
- A installs + B or C installs → **unenforced or advisory** — full third-party authoring unlocked, proceed to §5 immediately.
- A fails → our catalog/lane emulation is wrong; debug server before concluding anything about signatures.

Watch the wire (the project already has the pcap rig): which files the TV pulls and in what order tells us the verifier's actual behavior regardless of UI outcome.

---

## 5. Recommended authoring target for a first custom widget

### Target: **K3D_Clock — AC2.1 floating clock, truth source = NTP.br official time** (owner-chosen 2026-09-13)
The first custom widget is now specified (replaces generic LAN_Hello), with two
owner-chosen properties: a floating overlay panel (dock-rail corner clock) and the
Brazilian Legal Time as the truth source.

- **Overlay form is proven native:** SAX1.1 dock widgets (Facebook/Twitter dock.xml
  panels) and AC2.1 `<fullscreen>0</fullscreen>` + `<width>/<height>` small panels
  both run on these TVs.
- **Time source:** widgets have HTTP XHR only (no UDP/NTP sockets) — use NIC.br's
  Brazilian Legal Time HTTP API (`a.api.braziltime.com.br`, JSON timestamp).
  Cross-origin HTTP GET is proven (RSSReader fetches arbitrary feed URLs; the TV
  reaches the internet directly, no DNS override involved).
- **Algorithm:** poll every ~10 min → `offset = official_time − tv_clock` → tick
  locally between polls (tv_clock + offset). Display the live offset in the options
  screen as a diagnostic.
- **DST is a non-problem by design:** Brazil abolished DST (2019); render UTC-3
  (UTC-4 option for far-west states) straight from the API's UTC. The TV's broken
  DST table (§8.4) never enters the loop — this *is* the clock fix.
- **Analog rendering:** no canvas in the RSSReader-shaped profile — pre-render hand
  positions as frame PNGs swapped in a `<Bitmap>` (frame-swap animation is native;
  Sony's own loading spinner is a 4-frame PNG cycle). Digital is a `Memo2D`.
- Digital/analog toggle via `<preference>1</preference>` options menu.
- **Gated behind the §4 verdict:** ENFORCED means this cannot install until the
  firmware lane (UART/ABK) opens the signature wall. Author and test NOW against
  the community PC emulator (geekpage `emulator.php`, archived) so it installs the
  day the gate falls.

### Profile rationale: **AC2.1 profile, RSSReader-shaped** — with SAX1.1 as fallback

- **Simplest surface observed anywhere**: ~30 engine globals, 6-element declarative markup, plain callbacks for remote keys, async GET XHR, two-string-key persistence. No canvas painting, no event-loop management, no per-view duplicated digest entries (single layout root).
- **Sony itself served an AC2.1 bundle (SNY_RSSReader) from applicast.ga.sony.net to international GA-region TVs** — and AC2.1 is now *proven executing* on the EX725 (§7 Q2).
- Full community-era documentation survives for AC-profile programming (geekpage.jp tutorial series, live; HelloWorld.zip verified downloadable at `/tmp/acig-/applicast-archive/geekpage/`; the only GitHub AppliCast widget, takus/js-tardy-prevention-timer, is AC2.0 and mirrored at `/tmp/acig-/applicast-archive/github-takus/`).
- Caveat: if the EX725 rejects AC2.1, fall back to **SAX1.1** (Facebook-shaped: dock.xml + canvas.xml XGML, no encryption needed) — that profile is *proven installed* on these TVs (Facebook/Twitter were the store inventory).

### Minimal "hello world + LAN fetch" design (AC2.1)

```
WidgetBundles/LAN_Hello/
  info.xml            ← <spec>AC2.1</spec>, <fullscreen>0</fullscreen> (keep it one-context),
                        <width>280</width><height>165</height>, <duplicable>1</duplicable>,
                        <preference>1</preference> with one string pref for the LAN URL (Item1),
                        <name lang="eng">LAN Hello</name> (provide por too)
  layout.xml          ← <Widget> tree: one <Component name="main" visible="1">,
                        one <Text name="title">, one <Memo2D name="body" scroll="1"
                        wordwrap_mode="auto" exceed_dot="1" buf_size="2048"/>,
                        one <Bitmap name="icon"> for a status glyph
  widget.js           ← onLoad(): getNode() handles; XHR GET the dictionary-less path —
                        skip dic entirely (hardcode strings) for v1;
                        onActivate(): async GET http://<lan-host>/hello.txt (from getStoredValue
                        pref, default set in the engine-generated settings UI);
                        readyState==4 && status==200 → setStr(body, responseText) with
                        new String() materialization; 28 s watchdog timer, CLEARED on
                        success and on every state change; onConfirmKey(type==0) → re-fetch;
                        onRedKey → help dialog Component
  bg.png, icon.png    ← PNG8, tiny
  contact.xml
  digest.txt          ← computed: SHA256-Digest of info.xml, layout.xml, widget.js, bg.png
  digest.sig          ← experiment arm per §4
```
Engineering rules to bake in from §2.4: clear every timer defensively; never exceed 3 concurrent XHRs; keep the bundle under 48 KB; 1 s timer resolution (never rely on sub-second setInterval precision); wrap XML reads in `new String(...).length`. Serve `hello.txt` from the same vhost (absolute `http://applicast.ga.sony.net/...` path or a second local name — the XHR follows absolute URLs fine, as RSSReader does with user-supplied URLs).

v2 escalation path (same bundle): add `<fullscreen>1</fullscreen>` + `layout_fullscreen.xml` + `widget_fullscreen.js`, passing state via `setRegistry("Item1")`/`getRegistry("Item1")` — the only bridge between contexts. v3: port to SAX1.1/WAA1.0 to gain registry.extension, dock/canvas integration and (the long-game prize) the `hdmiCec` API — CEC transmit/receive from widget JS, which only the XGML profiles exercise.

---

## 6. The Unbound override experiment design

### 6.1 DNS override (OPNsense → Unbound)

1. **Record ground truth first**: `dig applicast.ga.sony.net` from LAN before any change; log the resolved CloudFront IPs and a direct curl of `/WidgetContents/SNY_WidgetGallery/AZ2/Index.xml` status (the origin has 403-blocked many objects since 2026-03-17 — surviving 200s are cache-node lottery; our archive may be the last retrievable copies, which is exactly why we mirror).
2. **Add exactly one Unbound override**: `applicast.ga.sony.net → A <lan-server-ip>` (Unbound → Overrides, or a local-zone host entry). Nothing else.
3. **Do NOT touch**: firmware/update domains (sony.net update paths, bravia update hosts), `ssm1.internet.sony.tv`, `bravia.dl.playstation.net`, `static.internet.sony.tv`, NTP. Community blocklists confirm blocking ssm1/internet.sony.tv triggers "no internet connection" states — leave them resolving normally so the TV never enters an offline error path that changes widget behavior.
4. Reversibility: the override is one delete away; no TV-side change of any kind.

### 6.2 Server layout (plain HTTP :80 on the lan host; the TV does not use TLS on this lane)

```
/var/www/applicast/            ← vhost root for applicast.ga.sony.net
  WidgetContents/SNY_WidgetGallery/
      AZ2/Index.xml            ← per §3; AZ3/Index.xml served identically (notification-view
                                 hardcodes AZ2 even on HX855)
      <gallery-dir>/Gallery.xml, Catalog.xml, information trees
  WidgetBundles/
      LAN_Hello/…              ← our widget, §5
      SNY_RSSReader/…          ← byte-exact copy from /tmp/acig-/applicast-archive/ (control arm)
      SNY_Facebook/…           ← optional: re-list the original as catalog entries to test
                                 the deleted→update resurrection path
  WidgetInfos/…                ← mirrored structure for any listed id
  hello.txt                    ← fetch demo target
```
Server rules:
- **Honor conditional GETs** (If-Modified-Since → 304 when unchanged). The TV's cache semantics trust 304s; serving naive 200s for unchanged content may cause needless reinstalls or, worse, hide whether revalidation happens.
- Serve correct Content-Type and Content-Length; log **every** request with UA + full path + response code — the request order itself is reconnaissance data (which files the installer pulls, whether digest.sig is ever requested).
- Unknown paths: return 404 (mimic the CDN), not a directory index.
- Keep both TVs' traffic separated in logs (UA distinguishes 3.0.9 vs 4.0.4).

### 6.3 Safety rules (absolute)

- **No firmware path is ever pointed at us** — the override list stays at exactly one host. No flash writes, no update attempts, no TV-side settings changes beyond normal widget use.
- Everything served is content the TV already fetches in the normal widget lane (catalogs/bundles) — all changes are LAN-side and instantly reversible by deleting the DNS override.
- Keep the original applicast.ga.sony.net archive **read-only** as evidence (`/tmp/acig-/applicast-archive/`, repo `docs/research/liverecon/applicast-fetched/`); experiment from copies.
- If either TV shows any sign of an update/firmware flow over our vhost (unexpected large binary requests, version-check-like paths), drop the override immediately and re-examine.

### 6.4 Experiment phases

1. **Baseline (no override behavior change):** override live, serve mirrored original Index/gallery/catalog unchanged → TV should behave exactly as before. Confirms DNS interception is transparent.
2. **Lane test:** modified Catalog re-listing an original bundle (status cleared, newer `updated` timestamp) → gallery should offer it; Confirm should install. Proves catalog emulation end-to-end.
3. **Signature arms A/B/C** (§4) on the original bundle.
4. **If any modified-content arm installs:** serve `LAN_Hello` (§5) — first custom widget.
5. Throughout: pcap both TVs; diff request sequences per phase.

---

## 7. Open questions, ranked by importance

1. **Is digest.sig enforced?** NARROWED LIVE 2026-09-13: Arm A (control) passed — original sigs install fine from our LAN server (§4 verdict). Remaining: Arms B/C (foreign/garbage sig) — the single gating fact for custom-widget authoring. No community knowledge exists; only the on-hardware experiment answers it.
2. **Does WidgetSystem/3.0.9 (EX725) accept AC2.1-profile bundles?** **ANSWERED LIVE: YES.** SNY_RSSReader (AC2.1) installed via our catalog and its runtime (`AppliCast/4.0/DTV`) executed it on the EX725 — layout/widget/DIC/PARTS fetches observed 2026-09-13. §5's authoring target is confirmed.
3. **Exact revalidation/install triggers.** LARGELY ANSWERED LIVE: catalog `updated` bumped to a 2026 timestamp with `status` cleared and `registration="dock"` caused the TV to **auto-install all four listed widgets with NO user confirmation** (the 2011-era auto-register path). The TV re-polls digest.txt/digest.sig/info.xml periodically (observed re-fetch cascades every few minutes) and honors 304s.
4. **AZ2/AZ3 catalog divergence on the HX855.** canvas.js computes chassis (AZ3 for version 4), notification.js hardcodes AZ2 — what does the HX855 *actually* request on the wire? Serve both trees; observe.
5. **Role of `/WidgetInfos/`.** Present on the CDN and in our archive; exact function in install/registration unknown until observed. Mirror structure for listed ids.
6. **Whether the develop-mode backdoor is reachable.** The gallery supports `?mode=develop&url=<catalog-url>` (option-menu "Change Catalog" via native `prompt()`, persisted in registry `developCatalogSrc`) — a sanctioned catalog redirect that bypasses WidgetContents entirely. We cannot currently control `widget.uri`'s query string (it's set at launch/registration); worth probing whether a dock-registered gallery entry or a crafted URI can carry it. Would give a second, signature-independent injection lane **for the catalog only** (bundle install still gated by Q1).
7. **Engine resource ceilings on our exact sets** for AC2.1 (memory/timers/XHR limits are Japan-era documented; international runtime may differ). Empirically establish during LAN_Hello bring-up.
8. **common.key / encryption.enc.js scheme** (RSA-wrapped AES envelope is the leading hypothesis). Only relevant if we ever need at-rest secrets — low priority; unencrypted scripts are the norm (RSSReader, gallery, AudioControl ship none).
9. **Whether the HX855's second widget system (SocialTV on bravia.dl.playstation.net) offers another lane.** Out of scope until the primary lane is settled.
10. **IA/CDX sweeps unfinished** (Internet Archive flapped offline mid-research): sony.net/sony.jp/sony.com.br applicast paths, internet.sony.tv captures, SamyGO t=2430 pages 2–3, technopat.net "Project BraviaGo" — low probability of new SDK material, but the one 2011 "widget developer kit" URL was never preserved and might still surface.

---

## 8. Deployment log (2026-09-13, phase 1 live)

### 8.1 Server side (d2server 192.168.0.60)

- Apache vhost `applicast.ga.sony.net` on :80 → `/var/www/applicast/`
  (`/etc/apache2/sites-available/applicast-lan.conf`, a2ensite'd); dedicated logs
  `applicast-access.log` / `applicast-error.log` (combined format — client IP + UA
  distinguishes WidgetSystem/3.0.9 (EX725) vs 4.0.4 (HX855)).
- Content: byte-exact mirror of the archived CDN state — all `WidgetBundles/`
  (30, incl. partials), `WidgetInfos/`, and `WidgetContents/SNY_WidgetGallery/{AZ2,AZ3}/Index.xml`
  (live-fetched, byte-identical to origin's current 254/257 B responses).
- Phase-1 rules honored: unknown paths 404 (no indexes); Gallery/Catalog files
  deliberately ABSENT until phase 2 (origin 403s them since 2026-03-17, so absence
  matches what the TV has been receiving — transparent baseline).
- Phase-2 tree staged, not deployed: `/tmp/acig-/applicast-phase2/` (four-widget
  Catalog_US_BRA_por.xml re-listing the original RSSReader / Facebook / Twitter /
  AudioControlApp bundles, Gallery token aliases, description fills, icon aliases).

### 8.2 DNS side (OPNsense 192.168.0.1)

- Exactly one Unbound host override added (§6.3 respected — no other host touched):
  `applicast.ga.sony.net → A 192.168.0.60`, in `/conf/config.xml`
  `<unboundplus><hosts>`, description "ApplicaCast LAN resurrection - widget lane phase 1".
- Applied via `configctl template reload OPNsense/Unbound/core` + `configctl unbound restart`
  (renders into `/var/unbound/host_entries.conf` as
  `local-data: "applicast.ga.sony.net  IN A 192.168.0.60"`).
- Verified: `dig +short applicast.ga.sony.net @192.168.0.1` → `192.168.0.60`;
  end-to-end `curl http://applicast.ga.sony.net/...Index.xml` → 200, 254 B, via .60.
  Pre-override ground truth (CNAME chain to CloudFront 13.225.205.93/.20/.70/.87):
  `/tmp/acig-/dns-groundtruth-applicast.txt`.
- **Rollback = one delete**: remove that single `<host>` block from config.xml, rerun
  the two configctl commands. Backup taken: `/conf/config.xml.bak-applicast-20260913`.
- Other Sony hosts confirmed NOT overridden (sony.net / www.sony.com.br resolve
  publicly as before).

### 8.3 Recon bonus: the TVs' full phone-home map (Unbound stats DB)

Unbound's duckdb (`/var/unbound/data/unbound.duckdb`, stats enabled) holds per-client
DNS history — a passive, no-touch instrument (no port scans, no TV interaction).
Full query history per set:

- **KDL-46EX725 (.22)** — 179 queries: `ssm.internet.sony.tv` (74), **`applicast.ga.sony.net`
  (40 — autonomous polling confirmed, both idle and in use)**, `bravia.dl.playstation.net` (25),
  `bravia-e.dl.playstation.net` (17), `static.internet.sony.tv` (9),
  `upbookmark.ww.np.community.playstation.net` (4), one-shots: `certs.opera.com`,
  `rd1.sony.net`, `www.sony.com.br`, `xml.opera.com`, `crl3.digicert.com`.
- **KDL-46HX855 (.21)** — 642 queries: **`applicast.ga.sony.net` (276 — polls most actively)**,
  `bravia.dl.playstation.net` (162), `ssm.internet.sony.tv` (88), `www.sony.net` (62),
  `static.internet.sony.tv` (8), `ssm1.internet.sony.tv` (6), `sony.tvstore.opera.com` (2),
  `upbookmark.ww.np.community.playstation.net` (2), one-shots: `certs.opera.com`,
  `nccp-nrdp-31.cloud.netflix.net`.
- pf state table (passive) shows the EX725's live outbound as pure HTTP:
  CloudFront/AWS IPs on :80/:443 (the poll cadence) + DNS to .1:53. **No port-123
  (NTP) traffic and no time-related DNS from either set.**

### 8.4 The clock question (open — another broken feature)

The sets' clocks run ~1 h fast with "network time" selected (reported by owner
2026-09-13, post-Brazil-DST-abolition era). Given §8.3: no NTP DNS, no NTP states —
the "network" clock comes from the SSM/HTTP channel payloads (most likely), the
ISDB-Tb broadcast TOT (possible), or a hardcoded-IP source (can't be excluded until
a capture sees one). Consequence: **no quick DNS-style fix exists** — if it's SSM,
the clock is another candidate for the resurrection lane; if it's broadcast, the
era firmware's legacy Brazil DST handling is suspect and the TV menu
(System Settings → Clock: timezone = Brasília UTC-3, DST = Off) is the immediate
mitigation. To determine which: sniff the first minutes after a cold boot on the
EX725 (tcpdump on the firewall LAN interface, port 123 + the SSM IPs) — deferred
until the widget lane is settled to avoid conflating captures.

---

## 9. Deployment log (2026-09-13, phase 2 live — RESURRECTION)

### 9.1 The WsIndex discovery (and the menu-vanish incident)

Phase 1 baseline had a hole we didn't know about: our mirror never covered
`WsIndexes/` — because no SDK-era doc mentioned the outer lane (§3.0). When the
override went fully live the TV's first request, `HEAD /WsIndexes/AZ2_LA.xml`,
404'd — and within one ~30 s poll the **entire widget menu entry vanished from the
XMB** ("now no widget meny! interesting!" — owner, live). That single 404 proved
the WsIndex gates the whole widget subsystem. Byte-exact fetch from origin (still
live there: 1712 B AZ2, 2443 B AZ3) + deploy → menu back within one poll, no
reboot. Also learned: a pre-reboot widget process ignores DNS changes (cached
resolver state); the boot sweep re-resolves.

### 9.2 The protocol map that fell out (all from live traffic)

`WsIndexes/AZ2_LA.xml` (area **LA**) → per-language `WsCatalogs/AZ2_LA_ALL_por.xml`
(Brazil picks por) → bundle installs directly (digest.txt → digest.sig → info.xml →
tree). The WsCatalog lists "Galeria Widget" as a *widget* (SNY_WidgetGallery,
activation="notification"), the Resident VCServiceUtil, dock widgets, and
playstation-served widgets (BgmSearch etc. — bravia.dl.playstation.net, NOT ours).
The gallery widget's canvas then runs the inner lane: Index.xml →
`Gallery_LA_BRA_por.xml` → `Catalog_LA_BRA_por.xml`. Full map in §3.0.

### 9.3 The resurrection catalog

Sony's kill mechanism, observed byte-for-byte in the live
`Catalog_LA_BRA_por.xml`: Facebook and Twitter still listed but with
`status="Deleted"` — **flag-based deactivation, files still on the CDN**. Our
phase-2 catalog (deployed as `WidgetContents/SNY_WidgetGallery/{AZ2,AZ3}/
Catalog_LA_BRA_por.xml`) clears the status, bumps `updated` to a 2026 timestamp,
sets `registration="dock"`, and lists four original bundles:
Facebook, Twitter, Leitor RSS (SNY_RSSReader), Controle do Home Theatre
(SNY_AudioControlApp) — with `WidgetInfos/` poster/thumbnail/description trees
(LA_BRA_por) and Sony's own Brazilian marketing text (from WsCatalogs) reused for
the authored description.xml files.

Result: the TV **auto-installed all four with no user confirmation** (owner: "WOW!
as soon as I returned the apps were listed!"), pulled every original signature and
proceeded, and the dock now renders them. The gallery detail view fetches our
authored `WidgetInfos/.../LA_BRA_por/description.xml` → 200.

### 9.4 Live end-to-end proof (access log, 22:16–22:17 local)

- `WidgetSystem/3.0.9` UA: installer cascade — all four bundles' digest.sig/digest.txt/
  info.xml/dock files → 200; gallery canvas.js/css/xml → 200.
- `AppliCast/4.0/DTV` UA (the widget runtime, executing): Facebook/Twitter dock
  images + Dic_UTF8_por dictionaries + encryption.enc.js/common.key → 200;
  RSSReader DIC/dic_por.txt + PARTS/Blue loading-animation frames (loading_Icon01–04)
  → 200/304 — an animated loading sequence playing from our server.
- Gap-closing fetches during the run (all from still-live origin): gallery
  `img/fhd/border.png`, `registered_bg.png` (requested 4× — all four widgets show as
  REGISTERED), RSSReader `PARTS/Blue/loading_Icon02–04.png`. Missing-frame probes
  (loading_Icon05–08) → 403 at origin: the animation is exactly 4 frames.

### 9.5 Preservation state after the phase-2 run (2026-09-13 late)

- **7 bundles manifest-complete (0 missing files vs Sony's own digest.txt)**:
  SNY_AudioControlApp, SNY_AudioControl, SNY_Facebook, SNY_RSSReader, SNY_Twitter,
  SNY_WidgetGallery, VCServiceUtil. digest.txt (JAR-style Name:/SHA256-Digest:)
  is Sony's own signed file inventory — the preservation instrument, not grep.
- **24 bundles origin-denied** (403 on digest.txt AND info.xml — e.g. SNY_Clock,
  Dailymotion, Deezer, Flickr, Weather, Slacker, TrackID): lost at origin; not in
  the Wayback Machine either (domain CDX: 120 captures total, none for these).
  Only recovery routes left: other archives, firmware-extracted preload copies, or
  nothing. Logged as the known-loss list.
- **Wayback era-recovery in flight**: domain CDX holds an entire lane we never had —
  `WidgetCatalogs/` (AZ1 EU, 23 languages — a pre-WsCatalogs generation), more
  `WsIndexes/` (AZ1_EU, AZ1_US, AZ2_EN, AZ2_US, RB1/RB2 rebranding indexes),
  `AZ2_US/XLA` WsCatalog variants, `XMB_AppliCast_AZ1_EU` bundle,
  FY13/FY14-era bundles (CrossSearch, BgmSearch, Zapping, SocialViewing, Football,
  HomeMenu), `SNY_AudioControl/model/*.json`, and DEV-lane MyChannel files.
- The obsolete `Gallery_US_BRA_por.xml` variants (deployed in the US-token phase,
  now 403 at origin) recovered from staging into the archive — only copies anywhere.
- **Wayback era-recovery tally (2026-09-13/14):** 52 files saved so far in two passes
  (20 initial CDX loop + 32 on retry), incl. `WsIndexes/RB2_CH.xml`, `RB2_US.xml`,
  more AZ1_EU locale catalogs and DEV-lane trees.
  13 curl-000 throttle failures were re-queued (round 3, in flight); anything still
  000 after that is treated as archive-throttle, re-tryable, not 404-gone.

## 10. Deployment log (2026-09-13/14, phase 3 live — THE SIGNATURE VERDICT)

### 10.1 Design (pre-registered, adversarially reviewed)
Three arms, one catalog, appended LAST after the four working originals, deployed to
both AZ2 and AZ3 catalog trees with root + per-entry `updated` bumped past the
registry's `dtv/X2WS/LastUpdated` gate (design review caught four blockers: the root
gate, dock.add≠install, the `status="Deleted"`-only removal path, and the timestamp
format). Experiment tree: `/tmp/acig-/applicast-phase3/` (evidence archive stays
read-only at `/tmp/acig-/applicast-archive/`).

- **ARMA_RSSReader** — byte-exact SNY_RSSReader clone, original sig. Control: proves
  a *new catalog id/path* installs, so a body-less cascade elsewhere can only be the
  signature.
- **ARMB_RSSReader** — byte-exact clone + SNY_Facebook's sig (foreign, valid format).
- **ARMB2_RSSReader** — unique content (`info.xml` name → "ArmB2 Test"/"Teste ArmB2",
  marker comment appended to `widget.js`) + **digest.txt hashes recomputed to match**
  + SNY_Facebook's sig. Kills the dedup/hash-mismatch/name-collision confounds.

### 10.2 Wire chronology (EX725 .22, all -0300; vhost access log)
- 22:32:10 catalog deployed (6 then 7 entries); 22:32:30 gate passed (200).
- **Arm B v1 confound:** opening "Teste Assinatura B" showed "widget ativado" + a
  running RSS reader, but the runtime fetched everything from `SNY_RSSReader/` paths —
  byte-identical content maps to the already-stored copy. INCONCLUSIVE; led to B2.
- 22:35:55 7-entry catalog pulled; 22:36:01–04 **the decisive pass**:
  - ARMA: icon + digest.sig + digest.txt + info.xml → **widget.js + layout.xml +
    bg.png (200)** → installed.
  - ARMB + ARMB2: header trio only, no body.
- 22:37:06–22:37:12 second poll cycle: ARMA body re-fetched (200) + header trio again
  for ARMB/ARMB2 — still no body.
- 22:36:05–22:37:40 runtime executes ARMA (AppliCast/4.0/DTV: `./DIC/dic_por.txt`,
  4-frame loading animation loop, `list_NF_BG.png`, 304s on repeat) — **the control
  clone is genuinely installed AND running from its own path.**
- 22:38:02 third cycle: ARMB2 header trio again (icon 304) — no body. Negative
  sustained ≥3 cycles.
- On-screen corroboration (owner, live): "Teste Assinatura A" opens = real RSS reader
  from its own install. "Teste Assinatura B2" *also* opens "just like the others" —
  but with zero ARMB2-path fetches on the wire, that was the cached original
  RSSReader executing, not B2's unique content (which would have read "Teste ArmB2").

### 10.3 Verdict
**ENFORCED** (§4 has the mechanism). Signatures gate the *download* decision:
header trio (icon, digest.sig, digest.txt, info.xml) is fetched unconditionally,
body files only after the RSA-3072 signature over the manifest verifies against the
firmware-pinned key. Rejected bundles still dock-register (dock.add precedes
verification) and their dock entries fall through to locally-installed content when
opened — the two facts that made early "it ran!" reads false positives.

### 10.4 Cleanup state (pending decision)
Test entries remain dock-registered on both TVs: ARMA (installed, running, harmless
clone) and ARMB/ARMB2 (never installed — phantom dock entries). Removal requires
`status="Deleted"` in the catalog (the only `dock.remove()` path); a rollback catalog
is pre-staged at `/tmp/acig-/applicast-phase3/Catalog_ROLLBACK.xml`. Decision pending
with owner: keep ARMA as a living control / remove all three.

### 9.6 What this unlocks (owner's framing)

Region-gating is pure server-side XML: widgets shipped US/EU/JP-only can be listed
in the LA catalog; per-locale description.xml/Dic files give us a translation
surface; and once Arms B/C answer the signature question, fully custom AC2.1
bundles (§5 LAN_Hello) are the endgame. AC2.1 acceptance on the EX725 is already
proven (RSSReader executing, §7 Q2).

---

### Source artifacts (local, primary)

- 30-bundle live mirror: `/tmp/acig-/applicast-archive/WidgetBundles/` (+ `WidgetInfos/`, `ga-dev/`, `cn-dev/`, `geekpage/`, `github-takus/`, `wayback-devsite/`)
- Repo copy with fetch log: `/K3D/GitHub/sony-bravia-linux/docs/research/liverecon/applicast-fetched/` (MANIFEST.tsv, grab_applicast.sh)
- Wire/CDN behavior: `/K3D/GitHub/sony-bravia-linux/docs/research/liverecon/applicast-widgetlane.md`
- External research: `/K3D/GitHub/sony-bravia-linux/docs/research/webfindings.md`
- Community tutorial (live): geekpage.jp/web/AppliCast/ series incl. usb-memory.php, emulator.php, regulation.php