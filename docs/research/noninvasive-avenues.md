# Non-invasive avenues — synthesis of the six-lane research workflow — 2026-09-13

Sources: workflow `wf_d1975936-491` (six research lanes: ext:board-photos,
sec:opera-hbbtv, sec:cers-upnp, proto:port9784, ginga:isdb-tb,
svc:jig-noninvasive), combined with the live-recon artifacts already in
`docs/research/liverecon/`. Confidence tags as reported by the agents;
live-confirmed items are marked **[LIVE]** (proven against our own TVs).

Safety note: the workflow diagnostics warned the safety classifier was
unavailable while several agents ran — everything below was re-checked
against our own repo data before being recorded here.

## Headline results, ranked by yield-per-effort

1. **IRCC-over-LAN is a full remote replacement — and it is UNAUTHENTICATED
   [LIVE]**. `POST /IRCC` with `X_SendIRCC` accepts arbitrary keypress codes
   on both TVs with no registration, no device-ID, no auth (benign "Up"
   code accepted, HTTP 200, both sets). Service mode on this generation is
   entered purely with remote keys (standby → DISPLAY → Ch 5 → Vol+ →
   Power), so the entire read-only service-mode diagnostics surface (error
   history, MID/PID, boot count, watchdog classes) is reachable over the
   LAN with zero cover removal. **Test on the EX725 first.**
2. **Ginga (ISDB-Tb interactivity) is a realistic code-execution path —
   with precedent that commercial receivers ran Lua apps as root with no
   sandboxing** (CPqD "Hacking Ginga", SBSeg 2010; independent UNICAMP/UNISAL
   PoC 2013). BUT on our Profile A sets the only delivery channel is the
   **broadcast chain**: author NCL/Lua app → OpenCaster ISDB-Tb fork packs a
   DSM-CC object carousel → low-cost modulator (osmo-fl2k ~USD 15 or HackRF
   + gr-isdbt) → **coax injection** into the antenna input (no RF emission,
   no opening; standard Ginga developer test methodology). Unsigned apps
   were never enforced in the field. Same investment unlocks HbbTV
   AIT-injection for the Opera engine.
3. **Port 9784 (EX725) = best hypothesis: Sony "Callisto Debug Server"**
   renderer-push family (2007–2008 DMX-NV1 precedent: unauthenticated
   HTTP `renderer.php?method=play&url=…`, play/pause/stop/addbookmark).
   Architectural handoff visible in our own data: the EX725 (CERS gen 1.0,
   no sendContentUrl) keeps 9784 open; the HX855 (gen 1.1, sendContentUrl
   on port 80) has it closed. Behavior differs (silent + RST vs chatty
   HTTP) — identification is one cheap experiment set away.
4. **CERS surface mapped and largely unauthenticated [LIVE]** — see
   section "CERS/UPnP attack surface" below. The two generations run TWO
   INDEPENDENT 2011-era IRCC implementations (EX725: CERS-style stack;
   HX855: `Server: Linux/2.6 UPnP/1.0 DMR/1.7` headers) — a
   differential-audit opportunity.
5. **Opera Presto foothold (Track B-alt)**: CVE-2011-2628 (Exploit-DB
   17936) is a public RCE PoC hitting exactly the EX725's Presto 2.7.61
   band (heap spray at 0x0c0c0c0c — no-ASLR MIPS era is favorable), plus
   a corpus of post-freeze Presto CVEs (2012-3561, 2012-6468, 2012-6465,
   2012-6470, 2012-1003, 2013-1637/1638). The only network path that
   renders our own content in the HX855's Opera 2.10 engine is CERS
   `sendContentUrl` (registration-gated, one-time on-screen approval);
   for the EX725, DLNA push + HbbTV/Ginga injection cover the rest.

## Lane digests

### svc:jig-noninvasive — ways to touch service/debug interfaces without covers

- **TL-JIG** is a factory bench fixture (board-level, FFC-connected —
  "TL-EX1 JIG board" in sibling chassis connector diagrams), NOT an
  external connector. No external 'COVER, ECS(S) (TL Jig)' part exists on
  AZ3F (that was the older W5500/W5800 generation); all board access
  requires rear-cover removal.
- **No RS-232 of any kind** on either set (grep of both user manuals +
  AZ3F SM: zero hits). Rear compartments carry only
  antenna/LAN/USB/HDMI/component/composite/VGA/audio.
- **Hotel mode has no wired external interface**: all HOTEL_* signals are
  muxed onto the internal BAP-H harness (shared with WiFi module and RF
  lines — WIFI GND/HOTEL_CL_GND, WIFI VBUS/HOTEL_CL_I2CA_SDA, RF
  Tx/HOTEL_VOL_Down, RF Rx/HOTEL_VOL_UP, RF RST/HOTEL_SP_MUTE, …). Hotel
  wiring is an optional internal harness, configured from the menu/service
  mode.
- **No Sony LAN service tool exists for this generation** (era tooling =
  service remotes, TL-JIG, USB updates). The only LAN control plane is
  CERS/IRCC + UPnP DMR.
- **AZ2-F service manuals located** (Elektrotanya): dedicated
  "SONY KDL-46EX725 Chassis AZ2F SM" (26.3 MB, 160 pp) + multi-model
  AZ2-F VER.1.0/2.0 SEGM.3A-2 + AZ2-F REV.0 LEVEL3. These are the missing
  primary sources for the BATV board (connector views, parts lists) —
  downloading them is a to-do (external docs, no opening).
- **HX855 has no USB service feature** beyond firmware update (no USB
  save/load of adjustment data on this generation; the service workflow
  is RM-ED047-remote-driven — which is exactly why LAN IRCC injection of
  the key sequence matters).
- **HDMI-CEC**: no auth, any HDMI device can inject frames (DEF CON 23
  "High-Def Fuzzing", HDMI-Walk WiSec 2019; tooling: cec-ctl, CECester,
  Pulse-Eight). No public research on Sony mapping CEC to service
  features/HbbTV — would be novel. Lower priority than IRCC (which is
  already proven open).
- **Service-mode entry (AZ3F SM, for the LAN-injection plan)**: standby →
  DISPLAY > Ch 5 > Vol+ > Power; self-diagnostic Vol−; categories cycle
  Digital/Chassis/VPC; writes via Mute+0. All keyed on the RM-ED047
  remote → a LAN/CEC path synthesizing those codes gets the whole
  read-only diagnostics surface.
- **CERS sendText** = the "Teclado Remoto" (Remote Keyboard) input
  surface — LAN text injection into browser/HbbTV text fields.

### ginga:isdb-tb — broadcast-chain code execution

- **CPqD "Hacking Ginga" (SBSeg 2010, full text read)**: Lua command
  injection via `loadstring()`/`os.execute`, code injection via
  `dofile()`, stored XSS, race conditions, weak crypto (56-bit DES
  LuaCrypto). On commercial receivers: root active with Ginga apps running
  **as root** on at least one model, NO isolation between NCL/NCLua/Lua
  apps. Independent confirmation: UNICAMP/UNISAL LACCEI 2013 PoC
  (`os.remove`, `io.read/write`, `loadfile`).
- **Our profile confirmed from our own iManual**: HX855 Ginga = ABNT
  NBR-15606 **Profile A** (NCL/Lua only, no Ginga-J Java apps, no MPEG-1
  videoclips). Settings: [Aplicativo Interativo] on/off only.
- **Delivery is broadcast-only on our sets**: neither manual documents USB
  or internet app delivery (no StickerCenter/portal — that TOTVS portal
  is dead anyway; TOTVS's TV-middleware business is gone). DTVi return
  channel is outbound-only (gives a running app TCP sockets; delivers
  nothing). Internet-delivered Ginga (Ginga-C 2016 / Ginga-D 2018)
  postdates Profile A. USB NCL execution exists in the ecosystem on STBs,
  but no evidence any Sony KDL ever supported it — a cheap negative test
  on the EX725 (FAT32 stick with a probe app) closes the question.
- **App signing never enforced in the field**: the ABNT NBR 15605-2
  signing/sandbox model was "in preparation" in 2010 and receivers ran
  unsigned broadcast NCLua apps throughout the era.
- **ByYouTV stack composition** (license PDF): Lua + LuaJava + Boost +
  OWB/WebKit → attack surface beyond Lua: the NCL (XML) parser, C++ NCL
  formatter, OWB/WebKit for HTML media objects, and a bridged JVM.
  LuaBot (2016) proved Lua-malware-on-MIPS is viable in the wild.
- **Buildable delivery chain (standard Ginga developer workflow)**:
  OpenCaster ISDB-Tb fork (0xalen/opencaster_isdb-tb, LIFIA patch) → TS
  with DSM-CC object carousel; gr-isdbt TX or osmo-fl2k (~USD 15,
  GRCon20-proven DTV TX); **validate off-TV first with a cheap ISDB-Tb USB
  dongle**, then coax-inject into the EX725 antenna input (attenuator, no
  over-the-air emission).
- **Bonus**: the broadcast gear also unlocks HbbTV AIT injection into the
  Opera engine on the same sets — plan both as one "broadcast input"
  sub-track.

### proto:port9784 — the EX725's mystery port

- **Callisto Debug Server v0.2** (DMX-NV1 "BRAVIA Internet Video Link",
  2007–2008): HTTP server on 9784, no landing page, unauthenticated
  `renderer.php?method=play&url={URL}` (+pause/stop/addbookmark); plays
  raw mp4/avi/mov/divx from arbitrary LAN servers. Proprietary (absent
  from the DMX's GPL list; Sigma SMP8634LF MIPS platform).
- Port 9784 open across the whole 2010–2011 Linux BRAVIA generation
  (EX403/EX600/HX805/EX720/NX715/EX709/EX725 — Hackaday 2012 thread), the
  generation that absorbed BIVL into the TV ("renderer function").
- **Our CERS-generation correlation**: EX725 (gen 1.0, NO sendContentUrl)
  keeps 9784 open; HX855 (gen 1.1, sendContentUrl over HTTP/80) has it
  closed → the push-to-renderer function likely migrated from 9784 into
  CERS between 2011 and 2012.
- **Red herring corrected**: "Guide did not accept password" reports in
  the Hackaday thread concern nimue.py's Gemstar TVGOS console (hardcoded
  port 12345, variant 8963, password 'gemstar') — NOT 9784. (Consistent
  with our own scans: 12345 closed on both sets.)
- **Behavior mismatch**: our EX725's 9784 accepts the connection, sends
  no banner, resets on data (nmap `tcpwrapped`) vs the DMX's chatty
  "Media Renderer does not implement this method". Candidates:
  access-control gate, binary-handshake variant, or inetd-style
  accept-then-close wrapper.
- **Probing hazards (era-typical)**: full TCP scans crashed/rebooted
  2010-era sets (one report: ports 1–46000 safe, 1–46001+ crashed the
  TV). **Single-port, single-connection, spaced ≥5 s, EX725 only,
  never a scan sweep.**
- Safe probe ladder: (1) idle-timeout discrimination (connect, send
  nothing vs one 0x0A); (2) half-close trick (send HTTP request then
  SHUT_WR); (3) DMX-era HTTP probe set (GET/POST renderer.php, GET /,
  bare 'TEST\r\n'), one per fresh connection; (4) re-probe DURING active
  UPnP playback (renderer-busy correlation); (5) **passive tcpdump
  during boot / BgmSearch::search / Media Remote use — if the TV's own
  processes ever connect to 9784, we get the real handshake for free**;
  (6) low-priority magic probes (gemstar\r\n, zmodem CAN, SSDP NOTIFY,
  length-prefixed binary).
- Optional ground truth: a used DMX-NV1 (~USD 20) is a live Callisto
  reference; Shodan shows no internet-exposed 9784 banners.

### sec:cers-upnp — the unauthenticated control/attack surface [LIVE-verified]

Live-confirmed unauthenticated (both TVs): `getSystemInformation`,
`/cers/ActionList.xml`, `/IRCC/IRCCSCPD.xml`, `dmr.xml` (52323),
**`POST /IRCC` X_SendIRCC (arbitrary keypresses)**,
`/cers/command/MuteOn|MuteOff` (actually muted the EX725 — restored),
DLNA DMR SOAP on 52323 (by design), SSDP M-SEARCH.

- **EX725-only unauthenticated leak**: `GET /s2mtv/SSDgetDeviceInfo/` →
  build PKG4.027BRA, DRM types (MARLINBB, SSL, WMDRM10), stream/codec
  lists, UI resolution 960x540, referrer_id = MAC. Saved at
  `docs/research/liverecon/s2mtv_SSDgetDeviceInfo_KDL-46EX725.xml`.
- **Registration gate is server-side**: forged X-CERS-DEVICE-ID → 403 on
  `/cers/api/*` (getRemoteCommandList, getText, …); the gate differs per
  generation (HX855 501 vs EX725 405 on other unregistered posts). The
  gate does NOT cover IRCC or URL-type commands.
- **IRCC wire format decoded**: base64 of 13 bytes = 3 BE32 words
  [manufacturer][device][function] + 0x03 trailer; standard codes
  manu=1/device=1 (Power 0x15, Up 0x74); MDF variant manu=2 (HDMI1–4
  0x5a–0x5d). Sony's official modern table (pro-bravia.sony.net) is
  byte-identical → full public code table usable, generation-stable.
- **Two independent implementations** (live): HX855 /IRCC answers with
  DMR-stack headers (`Server: Linux/2.6 UPnP/1.0 DMR/1.7`), EX725 with
  CERS-style headers; EX725 dispatch is hand-rolled (X_GetStatus
  mis-dispatches to the IRCC-code path; garbage base64 returns 200
  silently; empty code → SOAP fault 800) — a proven-sloppy, unauthenticated
  parser that is the #1 Track B-alt audit target.
- **sendContentUrl** (HX855, registered): navigates the built-in Opera
  browser to a URL — the only network path to render our own HTML in the
  engine. Scheme acceptance untested publicly (file://?).
- **Probable CERS frontend: libmicrohttpd 0.4.6** (in the GPL package
  list, 2008-era, never security-audited) — confirm after root.
- **Only published attack on this platform generation**: CVE-2012-2210
  (Exploit-DB 18705) — SYN-flood DoS against KDL-32CX525 (same 2011
  platform/GPL group as the EX725): watchdog crash-loop then power-off.
  Zero parser exploits published; zero CVEs on the 2011-era HbbTV/Opera
  engines; CVE-2019-11890 is a generic later SYN-flood, CVE-2019-11889 a
  crafted-HbbTV hang.
- **Audit ranking (Track B-alt)**: (1) X_SendIRCC dispatch (unauth,
  hand-rolled, two impls to diff); (2) AVTransport SetAVTransportURI URI
  parser on 52323 (unauth by design, long attacker strings into the HW
  player); (3) UPnP SUBSCRIBE CALLBACK-URL parser (CallStranger class);
  (4) libmicrohttpd 0.4.6 parsing if it fronts CERS; (5) sendContentUrl
  URL handling.

### ext:board-photos — external board documentation (text-only lane, completed)

No teardown needed — photos of our **exact** boards exist online, and a
Brazilian shop currently sells the exact HX855 main board as a donor:

- **Exact HX855 board photo**: tel-spb.ru (Russian repair DB) has a
  dedicated KDL-46HX855 page with the MainBoard photo of board
  **1-885-388-52**: `https://tel-spb.ru/remont-tv-lcd/main/1-885-388-52.jpg`
  (single overview shot, ~600–1000px). Sibling **1-885-388-51** photo at
  `https://tel-spb.ru/remont-tv-lcd/main/1-885-388-51.jpg` (same AZ3F
  chassis, same FQLR460LT01 46-inch panel as ours).
- **SoC census upgrade**: tel-spb lists the MainBoard ICs for BOTH -52
  (HX855) and -51 (HX853) as **CXD4727GB (X-Reality)** + K4B2G1646C-HCH9
  DDR3, KFM4G16Q4B OneNAND, SIL9287BCNU, GL850G, D2826ER, TPA6138,
  PS54425. This extends the census to our exact board variant, not just
  proxies — medium-high confidence (forum-derived source).
- **Donor board for sale (Brazil)**: GTVShop sells "Placa Principal para
  TV KDL-46HX855 | 1-885-388-52", used/tested-working, **R$329.90, 1
  unit**, 3-month warranty — the ideal bench unit for UART tracing so the
  owner's HX855 is never opened. Mercado Livre has more -52/-51 listings
  (bot-walled; browse manually).
- **Highest-resolution photos**: Shopify part-sellers (ShortCircuitSolution,
  TVPartsToday) have click-to-zoom CDN images (~2048px originals) of BAPS
  boards A-1875-753-A / A-1868-413-A (both 1-885-388-51).
- **EX725/BATV boards**: Control Telas (1-884-915-11, in stock, R$153.98,
  5 images), GTVShop (1-883-753-72 / Y8287492A, R$179.90), Videoecia
  (1-883-753-72, 5 images). **CN2903** is a known visible designator on
  the 1-883-753-72 board (Brazilian repair forum) — a photo-matching
  reference.
- **T-CON flash dumps for our exact model** at televid-sib.org topic
  110894 ("Sony KDL-46HX855 1-885-388-52 FQLR460LT01"): 551 KB RAR with
  25Q32/25Q80/24C02 dumps — free registration required. Primary-source
  artifact for T-CON work later.
- **SM limitations confirmed**: the AZ3F SM exploded views (pp.137-145)
  show the BAP board only as a part number (FX00A1701/1801/1901/2201) —
  no pad locations; photos of a real board remain mandatory. BUT section
  4-2 CONNECTOR DIAGRAM (pp.130-132) gives pin-by-pin tables keyed to
  silkscreen designators: **CN8001 (51-pin panel FFC) pins 42/44 carry
  FE_PEM_TX/FE_PEM_RX and pins 45/50 carry PEM_LOG_TX/PEM_LOG_RX** (SoC
  UARTD/UART_PEM_LOG land here); **BAP-H harness (SHLDP-40V-S(B)) pins
  14/16/18 carry RF Rx / RF Tx / RF UART_SEL** (the likely muxed 4th
  UART); DEBUG_LED1/2/3 nets exist on the BAP board. A human with a good
  photo can match designators to these tables.
- **No boardview/schematic leaks exist** for this Sony TV generation in
  indexed sources.

### 9784 live probing — verdict (2026-09-13 session)

Probes run (single-connection, spaced, EX725 only): idle-timeout ×3,
single-byte ×2, DMX-era HTTP GET, POST+half-close, and the full set
repeated **during active renderer playback** (UPnP-pushed clip, verified
PLAYING). Packet-level results from tcpdump:

- Idle connect → the TV sends a **graceful FIN ~10 ms after the 3-way
  handshake** — without waiting to read anything.
- Data sent → kernel ACKs it, then the TV **RSTs ~8 ms later** — the
  handler closed without reading (close-with-pending-data → RST).
- **No behavior change while the renderer was busy** (idle/busy identical).

**Verdict**: the 9784 listener accepts, then the handler exits
immediately without ever reading a byte — a stub or ACL-dead daemon
(possibly the Callisto component stubbed when BIVL moved into the TV).
Blind protocol probing is **provably useless** — no magic byte can help
because nothing is ever parsed. Remaining identification routes:
(a) after root: `ps`/`netstat` to name the daemon binary; (b) a used
DMX-NV1 (~USD 20) as a live Callisto reference; (c) nothing else —
de-prioritize 9784.

### NEW discovery: UDP port 7776 beacon (EX725-only)

Captured during the 2026-09-13 boot traffic session — **not in any
earlier scan** (all previous scans were TCP-only):

- The EX725 broadcasts **high-entropy binary payloads of random length
  (6–15 bytes) to 255.255.255.255:7776 every ~1.25 s**, continuously from
  boot onward (never stops).
- **HX855 does not do this at all** (35-min passive check: zero packets)
  — EX725/2011-generation-specific.
- A single 4-byte UDP datagram probe produced **no reply and no ICMP
  port-unreachable** (socket is bound) and did not disturb the beacon
  cadence.
- Publicly undocumented: the only trace anywhere is one German
  Ubuntu-forum anecdote ("my Sony TV sends a few bytes every few seconds
  to port 7776"). No protocol name, no service attribution.
- Interpretation candidates: encrypted discovery/beacon of the
  BIVL-era middleware, a pairing channel for a Sony phone-app of the
  era, or RNG/telemetry leakage. The cadence (1.25 s) and random lengths
  suggest a keep-alive with nonce.
- **Next steps**: longer capture to check for periodicity/pattern in
  lengths; correlate with CERS registration activity (does the beacon
  change when a Media Remote app registers?); listen on 7776 from the
  workstation during TV boot (does the TV *listen* for replies?);
  identify the process after root (`netstat -ulnp`). New Track B-alt
  surface: an undocumented UDP parser on the 2011 generation.

## What this changes in the roadmap

- **B6 (9784) is now ANSWERED at the behavioral level** (2026-09-13 live
  session above): accept-then-close stub, never reads, no state
  dependence. De-prioritized; only post-root identification or a DMX-NV1
  reference remains. The Callisto *hypothesis* stands unrefuted but is
  untestable from the wire.
- **UDP 7776 becomes the new unknown surface** — the only live mystery
  port on the EX725, EX725-only, publicly undocumented, with a bound
  socket. Add to Track B-alt audit targets (post-root process
  identification is step 1).
- **B7 (AZ2-F manuals) DONE** — all four SMs + the chassis-level AZ2-F
  schematic downloaded to `manuals/KDL-46EX725/`.
- **Donor-board option is live**: the exact HX855 main board (1-885-388-52)
  is for sale in Brazil, tested, R$329.90 — the bench unit that makes the
  B1 UART hunt possible without ever opening the owner's sets. EX725
  BATV boards (1-884-915-11, 1-883-753-72) are also in stock (~R$154-180).
- **IRCC driver script** (no registration needed) becomes the default
  control path for everything: service-menu capture, state orchestration,
  probing. Replaces "register mode 2" as step 1. (`tools/bravia_ircc.py`.)
- **Broadcast-input sub-track added**: OpenCaster + low-cost modulator +
  coax injection serves BOTH the Ginga app path (code execution candidate
  with root-as-Lua precedent) AND HbbTV AIT injection (Opera foothold).
  EX725 first.
- **Service-mode-over-LAN** is now the top diagnostics avenue: IRCC keys
  → service menu (read-only surface: error history, MID/PID) with zero
  opening. Needs care (Mute+0 writes to NVM — avoid write keys).
- **USB negative test for Ginga**: minutes, zero risk, closes the
  cheapest delivery hypothesis empirically.
- **HDMI-CEC** kept as a lower-priority lane (IRCC already gives the
  same navigation without buying hardware).

## Standing safety envelope (unchanged, now with era evidence)

EX725 (192.168.0.22) only; never the HX855 monitor; **no port scans of
any kind** (era reports of full scans hard-crashing sets; CVE-2012-2210
shows the watchdog fragility), single-connection spaced probes, power
cycle available, watch for the 8-blink Software Error state after each
session.