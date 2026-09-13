# Live network recon — 2026-09-13

Both TVs are on the LAN, DHCP-pinned by MAC. The KDL-46HX855 is also the
main monitor of the workstation this research runs on (HDMI on the iGPU).
Raw artifacts (dmr.xml etc.) are saved alongside this file.

## Port map (nmap full TCP scan + verification)

| Port | HX855 (192.168.0.21) | EX725 (192.168.0.22) | Service |
|---|---|---|---|
| 80/tcp  | open | open | Sony CERS / IRCC HTTP API |
| 9784/tcp | **closed** | **open** | Unknown Sony service (tcpwrapped; no HTTP; on the 2008 "Bravia Internet Link" box this port ran a "Callisto Debug Server", relevance unconfirmed) |
| 52323/tcp | open | open | UPnP MediaRenderer (dmr.xml) |
| 20677 | advertised (RDIS entry port) | — | Remote Display; not open on scan |

Hostnames via reverse DNS: `Sony3D.casacampos.lok` (HX855),
`SonyCast.casacampos.lok` (EX725). UPnP `friendlyName`: "Sony3d".

## UPnP / DLNA (port 52323)

Both expose an identical `MediaRenderer:1` device — this is a DLNA
**renderer** (DMR, Digital Media Renderer) controlled by push, not a server:

- `Server: Linux/2.6 UPnP/1.0 KDL-46HX855/1.7` / `...KDL-46EX725/1.7`
  → **kernel 2.6 confirmed live**, Sony UPnP AV stack av=5.0
- Services: `RenderingControl`, `ConnectionManager`, `AVTransport`
  (standard DLNA), plus **`urn:schemas-sony-com:service:IRCC:1`**
  (Sony's IR remote-control-over-IP)
- `X_StandardDMR 1.1` on the HX855 (EX725 presumably 1.0), `DMR-1.50`
- UDN tails = MAC: HX855 `3C:07:71:8B:6B:A9`, EX725 `30:F9:ED:4D:61:DB`
- HX855 dmr.xml additionally advertises:
  - `X_RDIS` (Remote Display) entry port 20677
  - `X_S2MTV` at `http://IP:80/s2mtv` (returns 501)
  - IRCC codes exposed as base64: `Power`, `Power ON`, `Power OFF`
    (e.g. `AAAAAQAAAAEAAAAVAw==`)

## CERS HTTP API (port 80)

`/cers/ActionList.xml` (both TVs) — the interface the "Media Remote"
smartphone apps used:

- `register` (mode "2" — pops a dialog on the TV screen, yields a
  `X-CERS-DEVICE-ID` header used for the other actions) — **DONE on the
  EX725 2026-09-13**: `GET /cers/api/register?name=...&registrationType=initial&deviceId=...`
  with matching `X-CERS-DEVICE-ID` header, accepted on-screen by the
  owner; procedure in `service-mode-ex725-session.md`
- `getText` / `sendText` (HX855 also supports the Notification function)
- `getSystemInformation` — **works unauthenticated via GET**:
  - EX725: `generation 1.0`, area BRA
  - HX855: `generation 1.1`, area BRA, language por, country BRA,
    modelName KDL-46HX855, supports `Notification`
- `getRemoteCommandList`, `getStatus` — empty/403 without registration;
  **post-registration the EX725 served its full authoritative 85-command
  IRCC table** — saved as `cers_remoteCommandList_KDL-46EX725.xml`,
  merged into `tools/bravia_ircc.py` (this generation: colors/media
  family device 0x97; Android-gen 0x9c)
- HX855 only: `getContentUrl`, `sendContentUrl` (remote "throw" a URL to
  the TV), `cersEx/api/getContentInformation`
- `BgmSearch::search`

IRCC control endpoint: `POST http://IP/IRCC` with SOAP `X_SendIRCC`
(SCPD at `/IRCC/IRCCSCPD.xml` on both).

Auth-gate behavior differences: HX855 returns `501 Not Implemented` for
unregistered POSTs; EX725 returns `405 Method Not Allowed` (GET on some
actions works). Both send `ACCESS-CONTROL-ALLOW-ORIGIN: *`.

## Other LAN context

- 192.168.0.3 (the WiFi AP, has its own USB port) runs MiniDLNA/ReadyMedia 1.1.4
- 192.168.0.60 runs Serviio 2.5 (DLNA MediaServer with transcoding)
- EX725 firmware per its user agent family: PKG4.0xx; HX855: PKG2.1xx

## Observations / leads

1. The two TVs share the same middleware stack (CERS/IRCC/UPnP) despite
   being different platform generations (AZ2F 2011 vs AZ3F 2012) —
   consistent with both running the same-generation Linux platform
   (SonyDTV115 device token).
2. Port 9784 open **only** on the EX725 — worth protocol identification
   (raw TCP probe; nmap calls it tcpwrapped).
3. ~~`register` mode 2 will pop an on-screen dialog~~ — DONE (EX725,
   2026-09-13) and used to capture the authoritative command list;
   read-only service-mode session also completed
   (`service-mode-ex725-session.md`): chassis codename WYVERN shared
   with AZ3F, MID 3D65E205 / PID 0E050000 / panel LTY460HJJ0501,
   SELF CHECK baseline HOST_WDT=21, boot count 11498. Service-mode
   arming requires the physical remote — LAN IRCC cannot arm it.
4. `sendContentUrl` (HX855) may allow pushing arbitrary content URLs —
   potential lever for serving our own content/apps if its URL schemes
   are permissive.
5. **BROWSER DELIVERY LANE LIVE-PROVEN (2026-09-13,
   `browser-lane-test.md`)**: the EX725's built-in "Navegador da
   Internet" (Home → Aplicativos, URL entry via Options → Inserir URL)
   + CERS `sendText` (GET, replaces focused-field text; 406 when no
   field focused) + plain-HTTP LAN server = full HTML render **and JS
   execution** in Presto. Live UA captured:
   `Opera/9.80 (Linux mips; U; InettvBrowser/2.2 (00014A;SonyDTV115;0002;0100) KDL46EX725; CC/BRA; en) Presto/2.7.61 Version/11.00`
   — first live UA of this set; no HbbTV token; Presto 2.7.61
   self-declared. https URLs fail pre-flight with zero egress; JS gated
   by Opera's standard "insecure code" accept prompt. Registration
   survives power cycles.