# tv-mediabrowser — era-lean Serviio MediaBrowser for 2011-era Sony BRAVIA

**LIVE-PROVEN 2026-09-15 (EX725): music lane works end-to-end.** Album art
displays at a decent size (512px CSS upscale of Serviio JPEG_TN), and **FLAC
plays** — the era native player accepted our responses (the 200-no-Range
concern on `/atr/` never bit; owner confirmed audio out of the TV). Deployed
and running on d2server (`:8090`, local-disk library, probe cache warm) —
all traffic stays on .60, none on the workstation.

**COMPLETE AUDIO ROSTER — owner-verified on the TV 2026-09-15:** every audio
format in the library plays: mp3 (era-native via `/stream/`), and flac/wma/
m4a/wav/ogg through the live `/atr/` pipe (ffmpeg → libmp3lame 320 kbps CBR
48 kHz, owner-directed). The two formats **Serviio itself cannot serve**
(musepack .mpc, wavpack .wv — it lists them as musicTracks with no `res`) are
routed through `/atr/` by DIDL title/duration resolve; both played on the TV
and label correctly (`audio/x-musepack` / `audio/x-wavpack`, derived from the
title extension since no DIDL mime exists). Stream URLs are RELATIVE
(`/stream/...`) — same-origin, immune to host moves.

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

## Transcode lane — cached faststart MP4 (app-side)

The era browser player accepts exactly one delivery: progressive faststart
MP4. Everything else is refused (format probe, 2026-09-14):

* **MKV/AVI/other containers** — refused client-side.
* **MPEG-TS** — refused; and it is the only family typical DLNA servers
  (incl. Serviio) transcode into live. Matching the app host's Serviio
  renderer profile to the Sony profile makes Serviio serve *everything*
  (even direct-playable MP4s) as live TS — tried, broke the whole lane,
  reverted the same night. Serviio has no MP4 transcode target.
* **Fragmented MP4** — fetched (206 in the server log) but not decoded:
  the era demuxer needs a real `moov`. Live MP4 streaming is out.

So the lane lives in the app: the library shares are mounted on the app
host (CIFS from the media server), the app ffprobes the source, offers
the audio tracks on the player page, and ffmpeg transcodes on demand —
video copied bit-exact when the H.264 is era-compatible, era-safe
re-encode otherwise (weightp=0:weightb=0, level ≤4.1, scaled down to
1080p for >1080p sources), AAC audio from the chosen track
(`-ar 48000`, channel layout preserved — 5.1 stays 5.1), `+movflags
faststart` — into a cache that plays like any direct MP4 from then on.

**Dolby plays bit-exact (live-verified 2026-09-14).** The era player
decodes AC-3 and E-AC3 tracks inside MP4: an E-AC3 5.1 lossless remux
(`/t/eac3`) and the dual-AC3 *War of the Worlds* both played on the
EX725, the set's own Dolby decoder handling the track (center-channel
dialog present on its 2.2 speakers — the classic "lost voices" failure
of a device that can't decode 5.1 did not occur). So the lane copies
AC-3/E-AC3 audio tracks unchanged (`-c:a copy`); with era-compatible
video the whole "transcode" is a pure remux — original picture, original
theatrical Dolby, chosen track, new container. Non-Dolby audio (DTS,
FLAC, MP3…) converts to AAC 5.1 48 kHz.

## Next steps

- [x] live test on the EX725 (arrow-key nav + direct MP4 playback) —
  owner-verified 2026-09-14 incl. 1920x1080 High@L4.0 SBS 3D titles
- [x] format probe — MP4/H.264+AAC direct-plays up to 1080p High@L4.0;
  MKV/AVI refused client-side; TS refused; fragmented MP4 fetched but
  not decoded → cached-faststart transcode lane (see above)
- [x] transcode lane — owner-verified live 2026-09-14: MKV → audio-track
  page → progress page → fullscreen playback (War of the Worlds, PT AC3
  5.1 bit-exact); later views instant from cache
- [x] Dolby probe — AC-3/E-AC3 in MP4 decode on the set (bit-exact copy
  lane, see above)
- [ ] thumbnails on list pages (Serviio serves cover art over :8895)
- [ ] "next in folder" on `ended`
- [ ] audio-track selection for direct-playable MP4s (multi-track MP4s
  currently play Serviio's chosen track)
- [ ] receiver pass-through test (HDMI 5.1 out is advertised; no AVR on
  the verified setup — TV speakers decode+downmix correctly)