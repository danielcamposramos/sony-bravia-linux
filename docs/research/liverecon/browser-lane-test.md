# Browser lane live test — "Navegador da Internet" + CERS sendText (2026-09-13)

The panel's Lane 1 (docs/research/partner-review-presto-panel.md), executed
live the same day it was proposed. Result: **the full content-delivery lane
into the EX725's Presto engine is PROVEN, zero new hardware.**

## Chain, all steps live-verified

1. IRCC `home` (0x60) → Home menu on screen.
2. Owner navigated (physical remote) to the built-in browser:
   **"Navegador da Internet"** exists on BRA firmware of this family, under
   the Aplicativos area — the manual (42730121M.pdf) and all five partner
   reviewers were right.
3. Browser opened showing its homepage URL `https://rd1.sony.net:443/tv1/`.
4. URL entry exists: **Options → "Inserir URL"** opens a text field with the
   current URL pre-selected.
5. CERS `sendText` types into the focused field and **replaces** its content.
6. Confirm → the browser fetches the URL over plain HTTP from our LAN server.
7. Page rendered on screen ("LAN delivery OK" and "JS executed at load"
   both read by the owner); the `<img>` beacon AND the `<script>`-created
   JS beacon were both fetched → **JavaScript executes** in this Presto
   build. **Caveat: JS execution was gated behind an on-screen acceptance
   the owner had to confirm — Opera's standard "this page contains
   insecure code" prompt** (fires on plain-HTTP pages with scripts; era
   Opera behavior, not Sony-specific). For automated ladder runs: either
   the acceptance becomes a scripted manual step per run, or a browser
   settings toggle quiets it.

## The set's real User-Agent (live, from its own request)

```
Opera/9.80 (Linux mips; U; InettvBrowser/2.2 (00014A;SonyDTV115;0002;0100) KDL46EX725; CC/BRA; en) Presto/2.7.61 Version/11.00
```

- **Presto 2.7.61 live-confirmed** — the CVE study's version premise is now
  the browser's own declaration, not firmware-string inference.
- `Version/11.00` — matches the corrected Presto↔Opera mapping (desktop
  11.00 shipped core 2.7.62; this Devices SDK build is 2.7.61, one build
  below desktop final of the same generation).
- **No `HbbTV/1.1.1` token** (the EUA sibling UA carries one) — first live
  evidence for the panel's "HbbTV dormant/absent on BRA firmware" verdict.
- `CC/BRA; en`, model KDL46EX725, `SonyDTV115` build tag.

## CERS sendText wire format (established empirically)

- `GET /cers/api/sendText?text=<urlencoded>` with the registered
  `X-CERS-DEVICE-ID: MediaRemote:CLAUDE-CODE-01` header → **HTTP 200 and
  the text lands in the focused field, replacing its content**.
- Works ONLY while a text field is actively focused: returns **406 Not
  Acceptable** otherwise (same for `getText`). This is the Remote Keyboard
  engage/disengage signal, not an error to retry blindly.
- `POST` → 405 Method Not Allowed (GET-only endpoint).
- Registration (done 2026-09-13, session doc) **survived a TV power cycle**
  — getRemoteCommandList/getStatus still 200 after off/on.

## sony.com.br observation (the pun, and a finding)

`https://www.sony.com.br` was typed via sendText and confirmed; the browser
**refused to render ("outdated keys"-class error)** — and the packet capture
shows **zero network egress**: no DNS query, no TCP SYN, nothing left the
TV. The refusal is pre-flight (browser-side TLS capability check or a dead
configured path), not a server handshake failure. Era browsers cannot do
modern TLS regardless; plain-HTTP LAN URLs are the working transport.

## Artifacts

- `/tmp/acig-/wwwserver.log` — full request log incl. UA (copied below)
- `/tmp/acig-/browser_step0.pcap` — 15-min LAN capture of the whole session
- LAN test server: python http.server on the workstation 192.168.0.4:8080,
  `/tmp/acig-/wwwroot/index.html` (heading + img beacon + JS beacon)

```
GET / [UA: Opera/9.80 (Linux mips; U; InettvBrowser/2.2 (00014A;SonyDTV115;0002;0100) KDL46EX725; CC/BRA; en) Presto/2.7.61 Version/11.00]
GET /phase-img-beacon.png [same UA]
GET /phase-js-beacon.png [same UA]   <- JavaScript executed
GET /favicon.ico [same UA] -> 404
```

## Consequences for the plan

- **Lane re-ranking is now settled empirically**: browser + sendText + LAN
  HTTP server is Rank 1 by demonstration. The panel's unanimous next-6
  step 2 ("reach the cheapest HTTP lane") is DONE.
- The CVE-2011-2628 falsifier run is unblocked: the trigger can be served
  as `application/xhtml+xml` from this server to this browser with zero
  delivery risk — but the **JS-execution acceptance gate** must be handled
  (manual accept per run, or find the settings toggle). Per the panel, the
  mandatory pre-step is the **positive-control crash page + oracle
  calibration** (HOST_WDT delta / 8-blink LED / ARP ping loss / phase
  beacons), quiescent windows, WAN quarantine.
- Server-side hedge CVEs (2012-6468 etc.) can be prepared on the same
  server; same-origin is under our control (we are the origin).