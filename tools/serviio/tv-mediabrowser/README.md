# tv-mediabrowser — era-lean Serviio MediaBrowser for 2011-era Sony BRAVIA

A TV app that browses the Serviio library on the LAN media server
(192.168.0.60, Serviio 2.5) and plays items on the EX725's built-in browser,
**modeled on Serviio's own MediaBrowser web app** — same library, same
category containers (Audio/Image/Video), same 18-items-per-page structure —
re-rendered server-side so a 2011 Presto browser can use it.

## Architecture

```
TV browser ── plain HTTP ──> server.py :8090 ── UPnP SOAP ──> Serviio :8895
   <video><source src=┄── /stream/ proxy (Range/206 passthrough) ──> Serviio res URL
```

- **Data source: UPnP ContentDirectory** (plain HTTP, port 8895, FREE
  edition, no license gate, no auth). SSDP: `urn:schemas-upnp-org:service:
  ContentDirectory:1` → control URL `/serviceControl`. SOAP `Browse`
  (BrowseDirectChildren / BrowseMetadata) returns DIDL-Lite; item `res`
  URLs like `/resource/<id>/MEDIA_ITEM/<DLNA PN>-<ci>/ORIGINAL` stream
  Range/206 to any plain HTTP client (verified with curl).
- **Playback: the Sony-path `<video>`+`<source>` recipe** proven live on
  the EX725 (docs/research/liverecon/lan-media-mvp.md). Media fetches are
  not same-origin restricted, but Serviio binds res URLs to the browsing
  client's IP, so the app proxies media through itself (`/stream/`):
  browse client == fetch client, and the native player gets Range/206
  from the proxy.
- **Navigation: arrow keys** (up/down select, OK/right open, left back) —
  the era browser maps remote keys to keydown events.
- Non-MP4 formats are handed to the player with their real MIME and a
  format label on screen — the era player's response doubles as a
  format-support probe for the transcode lane (next phase).

## Why not Serviio's own MediaBrowser app

Serviio 2.5 ships one at `https://192.168.0.60:23524/mediabrowser/`
(AngularJS 1.x SPA, ~750 KB JS). Two blockers, both verified live:

1. **Pro wall:** the MediaBrowser backend (`/cds` REST on the console/API
   listener, plain HTTP on 23424) answers `/cds/login` with errorCode 554
   "MediaBrowser is only available in the Pro edition" — credentials never
   get checked. The full wire protocol was still reverse-engineered from
   the MediaBrowser 2.1.0 bundle (signed-request auth:
   `key=b64(HMAC-SHA1(user:pass, pass))`, `sig=b64(HMAC-SHA1(date, key))`,
   headers `X-Serviio-Date` + `Authorization: Serviio UserName=…,
   Signature=…`; browse `/cds/browse/<profile>/<oid>/BrowseDirectChildren/
   all/<start>/18?authToken=…`) — documented here because it drove the
   design and would unlock per-quality `contentUrls` on a Pro install.
2. **Era browser can't run it anyway:** no CORS, no usable ES5+, ~750 KB
   JS against a hard memory ceiling ("page too big to display" observed
   live on the HX855), HTTPS with a self-signed cert.

The UPnP lane serves the same library with none of those problems, so the
prototype keeps MediaBrowser's structure and swaps the delivery.

## Run

```
python3 server.py [port]     # default 8090
```

On the TV's browser open `http://192.168.0.4:8090/` (CERS `sendText`
delivery as usual), accept the era insecure-content prompt once per
session.

## Transcode lane — Serviio renderer profile matching

Serviio picks the delivery format (and whether to transcode) from the
renderer profile it matched for the **requesting client's IP**. Because the
app's `/stream/` proxy makes the workstation both the browsing and the
fetching client, the workstation's renderer profile governs what the TV
gets. The era player refuses MKV/AVI client-side (format probe,
2026-09-14), so those must arrive already transcoded.

Switching the app host's renderer to the Sony profile once makes Serviio
itself transcode refused containers to era-native MPEG-TS on the fly — no
app changes; `pick_video_res` already prefers `video/mp4`, then `video/mp2t`:

* **Console UI:** Status tab → the app host's IP → profile →
  "Sony Bravia EX7xx/HX8xx (3D Enhanced)".
* **Or the console's own REST path** (port 23423, plain JSON, the same
  write the UI makes): `GET /rest/status` with `Accept: application/json`,
  change that renderer's `profileId` to `sony2011x`, `PUT` the whole
  document back to `/rest/status`.

Done live on 2026-09-14 via the REST path (verified: `.4` shows
`profileId=sony2011x`; serviio.log shows the transcode engine engaging).
MKV/AVI playback through the app lane pending owner retest.

## Next steps

- [x] live test on the EX725 (arrow-key nav + direct MP4 playback) —
  owner-verified 2026-09-14 incl. 1920x1080 High@L4.0 SBS 3D titles
- [x] format probe — MP4/H.264+AAC direct-plays up to 1080p High@L4.0;
  MKV/AVI refused client-side by the era player → server-side transcode
  lane (see above)
- [ ] owner retest: MKV/AVI through the app after the profile switch
  (expect Serviio on-the-fly MPEG-TS)
- [ ] thumbnails on list pages (Serviio serves cover art over :8895)
- [ ] "next in folder" on `ended`