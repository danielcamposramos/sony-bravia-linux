# OTA capture 1 — internet content ("Descarregar o conteúdo da internet") 2026-09-13

Owner re-ran the update on the EX725 (.22): **Rede → "Atualizar o Conteúdo
da Internet" → "Descarregar o conteúdo da internet disponível"**. Screen
result: content downloaded, "O conteúdo da internet está pronto".

## Vantage (the story of this capture)

- Attempt 1 (tcpdump on workstation enp6s0) was **blind**: the switched
  LAN delivers to the workstation only traffic addressed to it; the
  TV→WAN unicast never crossed our port (28 packets, all broadcast;
  sole fingerprint = the TV's ARP for gateway 192.168.0.1). This
  invalidated the earlier "zero egress" claim (FINDINGS obs. 6).
- The gateway is the owner's **OPNsense firewall (FreeBSD 15.1) at
  192.168.0.1** — DHCP + DNS (Unbound) + PPPoE WAN. A dedicated SSH key
  (~/.ssh/id_ed25519_bravia_lan on the workstation) was authorized on
  root; LAN interface = `bce0`. Capture run ON the firewall:
  `tcpdump -i bce0 -s0 -w /tmp/tv-ota-internetcontent.pcap 'host
  192.168.0.22 and not udp port 7776'` — this sees everything.
- Artifacts: `ota-internetcontent-wan.pcap` (firewall vantage, the real
  capture) + `ota-internetcontent-full.pcap` (workstation vantage,
  kept as the blind negative control).

## The three Sony endpoints (all DNS via OPNsense Unbound, round-robin)

| Host | IP(s) seen | CDN | Scheme | What the TV fetched |
|---|---|---|---|---|
| `ssm.internet.sony.tv` | 54.202.39.217, 35.167.179.43, 54.186.129.7 (3 A records, round-robin) | AWS (classic ELB class) | **:80 plain HTTP + :443 TLS** | `GET /DTV/index.xml` (4×, retry loop) + TLS auth sessions |
| `static.internet.sony.tv` | 23.46.244.177 | Akamai | **:80 plain HTTP** | `GET /bivl-ww/static/service/icons/service_120/x.png` (4×), `.../Registration/XmbRegistration.png` (2×) |
| `applicast.ga.sony.net` | 13.225.205.87 | AWS CloudFront | **:80 plain HTTP** | `GET /WidgetBundles/SNY_WidgetGallery/icon-tiny.png`, `.../SNY_AudioControlApp/icon.png` → **304 Not Modified** |

**User-Agent on all plain-HTTP requests** (URL-encoded, truncated by
tcpdump display at the wire fragment):
`User-Agent: SONY%20DTV%2F2010%3B%20PKG4` — decodes to
`SONY DTV/2010; PKG4…` (PKG4.027BRA firmware family).

## THE FINDING: the service manifest is a tombstone

`GET /DTV/index.xml` on `ssm.internet.sony.tv:80` → **200 OK**, nginx,
`Content-Type: text/xml`, `Last-Modified: 2026-05-04`, body verbatim:

```xml
<?xml version="1.0" encoding="utf-8"?>
<rule>We must use time as a tool, not as a crutch.</rule>
```

A JFK quote where the service manifest used to be — a deliberate
decommission marker someone placed (touched 2026-05-04). The TV fetched
it 4× (one per round-robin IP — it retries the next A record when the
result doesn't parse), then moved on. The "update succeeded" screen
comes from what still works: the BIVL service icons on
`static.internet.sony.tv` (Akamai, still serving) and the widget-bundle
icon revalidations on `applicast.ga.sony.net` (CloudFront, 304s = the
TV has the bundles cached locally and is just revalidating).

## TLS auth sessions (ssm:443) — era TLS still works

- TV ClientHello: `16 03 01` = **TLS 1.0**, era OpenSSL cipher list
  (AES128/256-SHA, 3DES, etc.), 86-byte hello.
- Server: full ServerHello + certificate chain (~1.4 KB) — **the AWS
  endpoints still accept TLS 1.0 for this TV**; sessions ran ~5–6 KB
  bidirectional and closed with clean FINs (both sides). The
  authentication traffic is encrypted and was NOT intercepted (nor
  needs to be for the applet lane).
- The 443 retry cycling (resolve → connect → next IP) matches the
  tombstone manifest failing to parse, not a TLS failure.

## Consequences for the plan

1. **The applet-insertion lane is real and 2/3 unencrypted.** The
   manifest, the BIVL static content, and the AppliCast WidgetBundles
   paths are all plain HTTP port 80. With the owner's OPNsense we can
   point any of these hostnames at a LAN server via a Unbound host
   override — no ARP games, no TLS MITM. This is the clean testbed for
   a portal-serving experiment (with the standing rule: DRM
   license/key endpoints stay sink-holed).
2. **The feature is orphaned, not merely EOL** — the live manifest is a
   farewell quote. Any portal we serve wouldn't compete with Sony's;
   we would be *resurrecting* a feature the vendor has already
   replaced with a tombstone. Right-to-repair framing at its purest.
3. **Widget bundle namespace confirmed live**: `/WidgetBundles/
   SNY_<AppName>/…` on `applicast.ga.sony.net`. The bundle/catalog
   protocol (how the TV discovers and installs bundles) is the next
   research target — if the widget gallery fetches a bundle list we can
   host, our own applet runs in the Opera engine without even the
   browser lane.
4. **UA for all our LAN-served content**: `SONY DTV/2010; PKG4…` — add
   to the UA fingerprint set alongside the Presto browser UA.

## Open questions

- **Autonomous background polling unresolved**: the captured traffic
  was user-triggered (the owner acted as soon as the capture armed).
  An idle-window capture (hours, no one at the remote) settles whether
  the widget client phones home on its own.
- What the TLS auth sessions carry (encrypted; not needed for the
  lane, and intercepting auth is out of scope).
- The full `/DTV/` and `/WidgetBundles/` namespace on the live hosts
  (fetch the same URLs the TV fetches, from the workstation — plain
  GETs, no probing beyond what the TV itself does).
- Whether the HX855 (.21) does the same dance — capture when we do the
  firmware-check round.

## Next steps queued

- Capture 2: the firmware update check (same rig, fresh window).
- Idle-window capture on the firewall (settles autonomous polling).
- Live-endpoint exploration + AppliCast bundle-format research
  (workflow) → then the Unbound-override portal experiment design.