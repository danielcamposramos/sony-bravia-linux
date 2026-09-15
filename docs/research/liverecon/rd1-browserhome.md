# rd1.sony.net browser-homepage lane (2026-09-14 designed; 2026-09-15 deployed on d2server)

**Status 2026-09-15: production home is live on d2server.** Apache vhost
`/etc/apache2/sites-available/rd1-lan.conf` (mirrored:
`tools/rd1-portal/rd1-lan.conf`) serves `https://rd1.sony.net:443/tv1/`
and the `:80` plain-HTTP namevhost, era-TLS verified from the LAN:
TLS 1.0 + AES128-SHA + SNI → CN=rd1.sony.net cert, `/tv1/` 200 over the
era profile. Content `/var/www/rd1-portal` (copy of `wwwroot/`), media
link points at `http://192.168.0.60:8090/` (the app now runs on d2server
too — local-disk probe pass, no LAN traffic). The standalone
`serve.py 8443 ip.crt ip.key` probe (CN=192.168.0.60) stays up as the
direct-IP probe path.

**Unbound override applied 2026-09-15 (owner-directed):**
`rd1.sony.net → A 192.168.0.60`. SCHEMA CORRECTION — the applicast
override lives in the LEGACY `<unbound><hosts>` section of
`/conf/config.xml` (NOT `<unboundplus>`): split
`<hostname>applicast</hostname>` + `<domain>ga.sony.net</domain>` +
`<server>192.168.0.60</server>` + `<addptr>1</addptr>` fields. The rd1
block mirrors it exactly (`hostname` `rd1`, `domain` `sony.net`, uuid
`ed254d96-a03d-45f4-bf38-637ae90561d8`, description "rd1 browser-homepage
LAN resurrection"), inserted after the applicast block via a guarded
python script (`/tmp/acig-/opnsense-rd1-override.py`; applied with
`ssh root@192.168.0.1 'python3 -' < script`). Applied
`configctl template reload OPNsense/Unbound/core` +
`configctl unbound restart`. Verified: `dig +short rd1.sony.net
@192.168.0.1` → `192.168.0.60`; applicast still `.60`; end-to-end
era-TLS GET https://rd1.sony.net/tv1/ → 200.
Backup: `/conf/config.xml.bak-rd1-20260915`. **Rollback = delete the
one rd1 `<host>` block + rerun the two configctl commands.**

**LIVE-VERIFIED 2026-09-15 (EX725, owner-confirmed "portal opened after
fresh start"):** with the Unbound override active, a fresh TV start →
"Internet" button → the hardcoded homepage lands on our portal with zero
typing. Access log: `GET /tv1/` **200** from 192.168.0.22 with the genuine
era UA (`Opera/9.80 … KDL46EX725 … Presto/2.7.61`). One wrinkle: the
browser recorded the page URL as `http://rd1.sony.net/tv1/` (plain
`:80` namevhost — 895B gzipped body), i.e. the https-default fell back to
or normalized to http; the self-signed-cert acceptance question stays
unanswered but is moot for the homepage goal — the page arrives either
way. Pre-reboot the TV showed "Web Address Blocked" with zero LAN hits —
that was the stale Akamai DNS cache, cured by the TV restart (owner's
instinct). `/favicon.ico` added to the wwwroot afterwards (was 404).
Probe-ladder verdict: closest to row 1 ("homepage renders our portal")
with an http-fallback footnote.

The built-in browser's hardcoded default homepage is
`https://rd1.sony.net:443/tv1/` (live-verified, browser-lane-test.md).
Goal: make that address ours — the TV's "Internet" button lands on our LAN
portal (the media app and, as they come up, our widget/app store entries)
instead of a dead manufacturer page. Same pattern as the applicast widget
lane: Unbound host override on OPNsense + a LAN server; rollback is one
config delete.

## Wire facts (all live-verified earlier)

- Homepage URL is hardcoded `https://...` — port 443, TLS mandatory, no
  evidence of an http fallback for the *default* page.
- Public `rd1.sony.net` still resolves (CNAME `rd.sony.net.edgekey.net` →
  Akamai 23.11.234.x) — the override diverts traffic that currently exists.
- The browser's TLS is 2010-grade: `https://www.sony.com.br` was refused
  with an "outdated keys"-class error (browser-lane-test.md). That is a
  *cipher/protocol capability* refusal, not necessarily a validation one —
  and since we terminate the TLS ourselves we can serve exactly the era
  profile: TLS 1.0 + `AES128-SHA`-class suites (OpenSSL 3 needs
  `@SECLEVEL=0`).
- Whether era Presto hard-fails an untrusted (self-signed) cert is the
  open question. Root-CA injection via `certs.opera.com` is signature-gated
  (applicast-widgetlane.md, certificate-lane section) — the empirical
  strictness probe is the documented remaining strategy, and this lane IS
  that probe.
- The applicast override already proves the Unbound mechanism end-to-end
  (applicast.ga.sony.net → 192.168.0.60, OPNsense `/conf/config.xml`
  `<unboundplus><hosts>`, `configctl template reload OPNsense/Unbound/core`
  + `configctl unbound restart`).

## Deployment runbook

1. `tools/rd1-portal/make-cert.sh` — self-signed `rd1.sony.net` cert
   (RSA 2048, SHA-1 if this OpenSSL still allows signing it, CN+SAN).
2. `python3 tools/rd1-portal/serve.py 443` — era-TLS server (+ a plain-HTTP
   mirror on :80 for sendText probes of `http://rd1.sony.net/tv1/`).
   Probe from the workstation first (fast iteration); production home is
   d2server .60 next to the applicast vhost.
3. OPNsense: add exactly one more Unbound host override
   `rd1.sony.net → A <server ip>`, description
   "rd1 browser-homepage LAN resurrection". This is a second host beyond
   the applicast phase-1 single-host rule — owner-directed (2026-09-14),
   same class: content lane, no firmware/update host, one-delete rollback.
   Never touched: ssm/ssm1, playstation hosts, static.internet.sony.tv.
4. EX725 live probe (owner): open the browser, watch the homepage.

## Probe ladder (what the browser does decides the next step)

| Browser behavior | Meaning | Next |
|---|---|---|
| Homepage renders our portal | self-signed accepted silently | wire the real portal list; migrate to .60 |
| Security-warning page with "continue/OK" | era warning, owner can accept | accept once, measure whether it re-fires per session; consider a JS-free portal always |
| Immediate TLS/refusal error page | hard validation or handshake gap | check serve.py handshake log: no ClientHello = DNS/port issue; ClientHello then abort = cipher mismatch; completed handshake then refusal = cert rejected → try SHA-256, shorter validity, 1024-bit key, and a plain-http redirect probe |
| Homepage unchanged (still Akamai content) | override not taken | `dig rd1.sony.net @192.168.0.1`, check host_entries.conf |

Positive control before any of this: `curl --tlsv1.0 --ciphers AES128-SHA -k https://<server>:443/tv1/` from the LAN must return the page — proves the era profile is actually being served before blaming the TV.

## Portal content (after the probe passes)

`wwwroot/tv1/index.html` — era-lean (no JS on the probe page; over HTTPS the
plain-HTTP insecure-content prompt does not apply), arrow-navigable link
list, first entry the media app (`http://192.168.0.4:8090/`). The widget
store stays on its own lane (TV widget gallery via applicast); this page
becomes the index of LAN apps as they appear.

## Rollback

Delete the single `<host>` block from `/conf/config.xml`, rerun the two
configctl commands (same as applicast). The TV is never modified; DNS
returns to public resolution (Akamai) instantly.