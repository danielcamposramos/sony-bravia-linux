# LAN media playback MVP — proven live 2026-09-13 ~23:27

**The project's media-player goal is functionally achieved on the browser lane,
zero firmware work:** a 20-second H.264/AAC MP4 served from the workstation
played on the EX725's built-in browser, streamed from our own LAN HTTP server,
URL delivered by CERS `sendText`.

## The working chain (all steps live-verified 2026-09-13)

1. CERS `sendText` types `http://192.168.0.4:8080/` into the browser's
   URL field (Options → Inserir URL) — established earlier the same day
   (browser-lane-test.md).
2. EX725 browser (InettvBrowser/2.2, Presto 2.7.61, Opera 11.00) fetches the
   page over plain HTTP. Page contains JS → era "insecure content" prompt →
   owner accepts once.
3. **Sony-path player recipe (extracted verbatim from the Digital Concert Hall
   TV app source, karajan v4.3.7 — see below):**
   ```html
   <video id="player_object" width="0px" height="0px" preload="none"></video>
   <script>
     var v = document.getElementById('player_object');
     var s = document.createElement('source');   // Sony profile: URL+type on a
     s.type = 'video/mp4';                        // SOURCE child
     s.src  = 'http://192.168.0.4:8080/test-clip.mp4';
     v.appendChild(s);
     v.style.display = 'block'; v.setAttribute('width','100%'); v.setAttribute('height','100%');
     v.load(); v.play();                          // exact karajan order
   </script>
   ```
4. Native player pulls the file with `Range: bytes=0-` → server must answer
   `206 Partial Content` (our 60-line python range server suffices).
   Wire evidence (server log):
   ```
   23:27:06 "GET /"            200 -
   23:27:07 "GET /test-clip.mp4" 206 -   <- native player, byte-range stream
   ```
5. Video rendered on screen; owner confirmed playback of a 1280x720 H.264
   Main@L4.0 + AAC stereo, `+faststart` remux.

**Test clip**: 20 s cut from the owner's `[3D].47.Ronin.2013.mp4` — a 3D SBS
source, which played as plain side-by-side frames. **Bonus finding: the 3D
catalog is playable through this lane** (engage the set's SBS display mode for
stereoscopic rendering) — no special serving needed, it is the same progressive
MP4.

## Negative result that completed the picture

First attempt used `<object type="application/avplayer" data="URL">`: the
browser FETCHED the clip (object data URL prefetch) but rendered nothing —
**avplayer objects are the Samsung Tizen profile** (`player/samsung_tizen`
template, driven by the `webapis.avplay` bridge). For Sony the app uses the
HTML5 `<video>`+source path (`useVideoSourceObject=true` → URL and type set on
a `<source>` child, never on `video.src` directly). CE-HTML object path
(`<object id="video_player" type="video/mp4" data=...>` + `play(1)`,
`playState`/`playPosition`/`playTime`, `onPlayStateChange`) exists in the app
as the LG-NetCast-style fallback; untested on our sets (test page served at
`cehtml.html` if ever needed).

## Where the recipe came from: the DCH "karajan" app

The HX855's Digital Concert Hall service was captured in full plaintext
(pcap `tv-hx855-dch.pcap`, firewall vantage):

- App: **`dch.tv.html5` v4.3.7**, `app_distributor: "sen"`, `affiliate: "sony"`,
  actively maintained (live build timestamp 2026-09-07), served from
  `tv.digitalconcerthall.com/karajan/index.html5` (entry), `js/v4.3.7_*_{app,
  config,lib}.js`, `css/v4.3.7_*_all.css` — all plain HTTP, all fetched and
  archived locally (v4.3.7 live + v4.1.0 via Wayback 2024-10-09 snapshot).
- API: `api.digitalconcerthall.com/v2` over plain HTTP — `/v2/related/concert/
  <id>`, `/v2/client_info` (401 token-gated), **`/v2/streams/<product_id>`**
  (returns the video URL), `/v2/manifest`, `/v2/vod-concerts`, `/offers/en.json`.
- Analytics: `POST /v2` to usage host with JSON events (`playback_started`,
  `buffering` 3.4 s, `current_position`), TV duid as api_token.
- **Video delivery: progressive MP4 over plain HTTP** —
  `GET /dlkey/<key>/dch/<id>/h264_HIGH.mp4` with `Range: bytes=0-` to
  `world-vod.dchdns.net` → `206 Partial Content`, `Content-Type: text/plain`
  (MIME ignored by the player), ~24 MB preview in ~4 s, openresty CDN.
- Era browser memory ceiling observed live: a 2025 concert page refused with
  "page too big to display" while a 2023 preview played — **keep our app pages
  lean**.

UA of the 855's service browser:
`Opera/9.80 (Linux mips; U; Model/Sony-KDL-46HX855 SonyCEBrowser/1.0
(KDL-46HX855; PKG2.120BRA; BRA; pt); pt) Presto/2.10.250 Version/11.60`

The karajan source is Berliner Philharmoniker copyrighted code: kept in the
local evidence archive (`/tmp/acig-/dch-lane/karajan/`), NOT committed; the
recipe above documents the mechanism.

## New archive lane discovered during the session

`bravia.dl.playstation.net/bravia/WidgetBundles/...` — the BIV-era widget
bundle lane on the playstation download host. The 855 itself fetched
`/bravia/WidgetBundles/SocialTV/EmotionPost/img/NUX_Share.png` (200, rescued)
and `/bravia/WidgetBundles/Ext/WsCatalogs/otvs_icon_77x58.png` (200, rescued).
Bundle-shaped paths under it are 404; exact asset paths 200 — same
path-dependent-ACL pattern as applicast origin. Systematic enumeration of this
lane is a next-phase task (curl-only, no DNS overrides ever).

## Next steps toward the real app

1. Directory-browse page (remote-navigable with arrow keys — the browser gets
   remote keys as key events) over the media library, transcoding-on-demand or
   pre-transcoded H.264/AAC faststart MP4s.
2. Playback controls: pause/resume via `v.pause()/v.play()`, seek via
   `currentTime`, status via `timeupdate` (all standard; karajan uses exactly
   these on Sony).
3. The era prompt acceptance per page load — find the browser settings toggle
   (browser-lane-test.md caveat) or keep it as a per-session manual step.
4. Port the same page to the 855's BIV browser lane once service injection
   (or the same built-in browser, if present on AZ3 firmware) is available;
   the standalone-browser chain is already proven on the EX725.

## Update 2026-09-14 — the full app is live (tools/serviio/tv-mediabrowser)

The next-step list above is now built: `server.py` (:8090) browses Serviio's
UPnP ContentDirectory and renders the whole library for the era browser.
Owner-verified on the EX725 in a live session (~00:14–00:22):

- **Navigation** with the stock remote (arrows/OK) through category →
  folder → item trees, including the 1248-title movie root and the Curtas
  3D folder.
- **MP4 direct playback through the app**, owner-confirmed across multiple
  titles (playback events in serviio.log, e.g. item 84489 "3D BONSAI …
  FULL HD 3D SBS" started → stopped at 34%). ffprobe of the played files:
  **1920x1080 H.264 High@L4.0 + AAC** — upgrades the verified codec
  ceiling from the 720p Main@L4.0 clip to 1080p High.
- **Format probe result (decides the transcode lane):** AVI, MKV and other
  non-MP4 containers are **refused by the era player itself, client-side**
  (owner-confirmed; unrelated to the Serviio res-URL client-binding 500,
  which the `/stream/` proxy already fixed). They need server-side
  transcoding.
- **Serviio profile-matching experiment — negative result, reverted same
  night:** switching the app host's renderer profile to the Sony profile
  (via the console's own REST path, `GET`/`PUT /rest/status`, port 23423)
  makes Serviio serve **everything** — even direct-playable MP4s — as
  live-transcoded MPEG-TS (`AVC_TS_MP_HD_AC3_ISO`, `video/mpeg`, CI=1).
  The browser player refused all of it: zero `/stream/` fetches, "no one
  plays now" (owner report). Reverted to Generic DLNA; direct MP4 playback
  restored immediately. Lesson: the era browser player accepts exactly
  one delivery — progressive faststart MP4 — and Serviio has no MP4
  transcode target (its live targets are mpegts/mpeg/m2ts/lpcm/mp3/flv/
  asf/applehttp).
- **fMP4 probe — refused:** a 30 s fragmented-MP4 clip
  (`+frag_keyframe+empty_moov+default_base_moov`, streams untouched) was
  fetched by the player (206 ×2 in the server log) but rendered nothing;
  the faststart control cut from the same source played fullscreen.
  Live MP4 streaming is out → the transcode lane is **cached faststart
  MP4**, transcoded app-side (shares are CIFS-mounted on the app host).
- Era prompt: accepted once per session, did not re-fire across many page
  loads. Era-browser quirk: it decodes `%2A` to a literal `*` in browse
  URLs — harmless, the handler unquotes.
- Player pages render the video as a fixed full-viewport element with a
  slim overlay strip that auto-hides on first playing frame (owner
  request: match the DCH app's fullscreen playback; also removes the
  scrollbar the embedded layout caused; the strip is the diagnostic
  surface on errors).

## Update 2026-09-14 (late) — transcode lane live-verified incl. Dolby

The app-side transcode lane (server.py) is owner-verified live end-to-end
on the EX725:

- **Audio-track selection page** on the set: an MKV item opens
  "Choose the audio track" (e.g. War of the Worlds: AC3 5.1 por/eng);
  OK on a track starts the conversion.
- **Progress page** with live percentage, auto-refreshing — owner
  confirmed "it's converting on the fly and even shows a progress
  percentage"; on completion the page itself becomes the fullscreen
  player.
- **Dolby decodes bit-exact:** AC-3 and E-AC3 tracks copied unchanged
  into the faststart MP4 are decoded by the set's own Dolby decoder
  (probe clips `/t/ac3` re-encoded AC-3 5.1, `/t/eac3` lossless E-AC3
  remux; then a full movie). Center-channel dialog present on the
  2.2 TV speakers — the classic "voices vanish" failure of a device
  that cannot decode 5.1 did not occur, confirming decode (with proper
  downmix) rather than track refusal. HDMI 5.1 pass-through to a
  receiver is advertised by the set but untested (no AVR on the LAN).
- With era-compatible H.264 (the library's rips mostly are:
  1080p High@L4.0), a Dolby-audio movie is a **pure remux**: original
  video, original theatrical Dolby track, chosen audio language, new
  container. Non-Dolby audio converts to AAC 5.1 48 kHz, channel
  layout preserved. >1080p / HEVC / 10-bit sources re-encode
  (NVENC h264_nvenc on the app host's RTX 3060, High@L4.1 yuv420p —
  NVENC emits no weighted prediction, EX7xx-safe; libx264
  weightp=0:weightb=0 fallback), scaled down to 1080p when wider.
- The lane survived a multi-agent code review before deployment: the
  confirmed findings (start_job double-spawn race, ffmpeg orphans
  surviving restart, stale part-file sweep at startup, terminal
  failed-job state, NVENC global poisoning, a resolve_source
  normalization bug, unclickable no-res items) were all fixed in the
  deployed build.