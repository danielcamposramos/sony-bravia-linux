# Build your own BRAVIA Serviio portal

A pre-Android Sony BRAVIA (2011–2012, chassis AZ2-F / AZ3F and their
generation) shipped a smart-TV portal that Sony has since shut down —
services dead, apps withheld, firmware downloads pulled. The set is
otherwise fine. This is how to give it a working portal again on your own
LAN, using nothing but your own hardware and Sony's own signed files as
they already exist on your set.

Everything here is method: what we reverse-engineered about how these TVs
reach the network and render pages. It reproduces no Sony code. Where a
step needs Sony's signed widget bundles, those come from your own set or
your own backup — see **Rule of the road** at the end.

## What you get

- The TV's start page (`rd1.sony.net`) served from your own box on the LAN.
- A media browser over your Serviio library: folders, audio, video,
  images, cover art, live transcode for formats the set cannot play.
- The withheld regional widgets (Calculator, World Clock, Alarm, etc.)
  restored to the gallery, where you still hold the signed bundles.
- A player that uses the TV's own native transport, scaled to be readable
  from the sofa.

## Ingredients

| role | what we used | why |
|---|---|---|
| DNS you control | Unbound / OPNsense on the LAN gateway | to point two Sony hostnames at your box, and nothing else |
| a small server | any always-on Linux host on the LAN | serves the portal, Serviio, and the media app |
| Serviio (free) | the free tier | the UPnP media server the app browses over `:8895` |
| a TLS cert | self-signed for `rd1.sony.net` | the era browser will accept it (see the cipher note) |
| the media app | `tools/serviio/tv-mediabrowser/server.py` in this repo | stdlib-only Python, one file |

## 1. Two DNS overrides, and only two

On your LAN resolver, override **exactly these two hosts** to your server:

```
applicast.ga.sony.net  ->  <your server IP>
rd1.sony.net           ->  <your server IP>
```

`rd1.sony.net` is the TV's homepage host; `applicast.ga.sony.net` is the
widget/applicast host. **Override nothing else.** In particular leave
`ssm.internet.sony.tv`, `ssm1.*`, the `playstation.net` hosts and every
firmware/update host resolving normally. Those are the set's update and
auth paths; pointing them at yourself risks the TV writing to itself. The
whole design is: spoof the two content hosts, touch no update host.

The TV picks up the override within seconds of a menu action — no reboot
needed.

## 2. Era-TLS vhost for the homepage

The 2011 browser (Opera/Presto 11, InettvBrowser 2.2) speaks TLS 1.0 with
old ciphers. A modern web server rejects that handshake by default, so
you must lower the floor for this one vhost:

```apache
<VirtualHost *:443>
    ServerName rd1.sony.net
    DocumentRoot /var/www/rd1-portal
    SSLEngine on
    SSLCertificateFile /etc/apache2/ssl/rd1.crt
    SSLCertificateKeyFile /etc/apache2/ssl/rd1.key
    SSLProtocol +TLSv1 +TLSv1.1 +TLSv1.2 +TLSv1.3
    SSLCipherSuite AES128-SHA:AES256-SHA:DES-CBC3-SHA:@SECLEVEL=0
    SSLHonorCipherOrder on
</VirtualHost>
```

`@SECLEVEL=0` is what lets the era ClientHello through. Keep it scoped to
this vhost; do not lower your whole server's TLS policy.

The TV requests `/tv1/` on this host, so put your start page at
`/var/www/rd1-portal/tv1/index.html`. Keep it plain: big fonts, black
background, a list of links. This page is the insertion point — every
lane below hangs off it.

## 3. Serviio + the media app

Run Serviio (free tier) on the same box; its UPnP ContentDirectory is on
`:8895` and its console REST is on `:23423`, both unauthenticated on the
free tier. Then run the media app:

```
python3 tools/serviio/tv-mediabrowser/server.py 8090
```

It browses Serviio over UPnP, proxies media so the TV streams from you,
and transcodes on the fly what the set cannot play. Point the start page's
media link at `http://<your server IP>:8090/`.

The app is one stdlib-only file. It reimplements MediaBrowser's structure
over the free UPnP and REST surfaces — it does not touch Serviio's license
gate.

## 4. Restore the withheld widgets

The widget gallery is a catalog the TV fetches from the applicast host you
now serve. Each entry has a `status`: empty means shown, `Deleted` means
hidden. Sony finished the regional localisation and then withheld the apps
by catalog — so restoring them is an edit, plus the signed bundle.

Serve, under your applicast docroot, `WidgetContents/SNY_WidgetGallery/
<gen>/Catalog_<region>.xml`, with the widget you want carrying
`status=""`:

```xml
<Widget name="Calculadora" status="" registration="dock">
  <id>http://applicast.ga.sony.net/WidgetBundles/SNY_BasicCalculator/</id>
  ...
</Widget>
```

Two gotchas we found the hard way:

- **The engine reads files nothing references.** A widget needs
  `preference.xml` present in its bundle even though no page links it, or
  its configuration screen silently does nothing.
- **Bundles are integrity-checked.** Each carries `digest.txt` (a
  JAR-style SHA-256 manifest) and `digest.sig` (a 384-byte RSA-3072
  signature), and the set enforces the signature. You cannot hand-edit a
  bundle's files and re-serve it; the signature will fail. You serve the
  bundle **as Sony signed it**, which is why the bytes must come from your
  own set (below), not from a modified copy.

Icons and other assets are built from concatenated paths the code never
lists literally (e.g. `"./parts/flags/tz_" + (offset+11) + ".png"`), so a
bundle that is "complete" by its manifest can still show a loading icon
until you populate those. Expand the templates to get the assets on disk.

## The perks — everything we learned about this platform

Measured on a KDL-46EX725, 2026-09-18. Full detail in
[era-key-vocabulary.md](era-key-vocabulary.md) and
[era-media-element.md](era-media-element.md).

**The remote sends almost nothing.** PLAY, PAUSE, STOP, PREV and NEXT
produce no keydown at all. You get: `13` OK, `37` left (and REW), `39`
right (and FF), `38` up, `40` down. All four colour keys belong to Opera,
not to the page — it says so in its status line while a link loads. Green
and yellow navigate between pages (history back / forward); red and blue
scroll within a page (bottom / top). So GREEN is your reliable "back"
everywhere, but none of the four is bindable. **Build all transport
on-screen** — the media keys are not there to bind either.

**Fonts: build for the Medium size setting.** Only the Geometric Shapes
block, Latin-1, and a few scattered symbols (`♪` U+266A, `∞` U+221E)
render. The whole Arrows block is tofu — including codepoints that are
"Unicode 1.1" and look safe. If a glyph might be a box, test it on the
panel. And every size must be tuned for the browser's **Medium** font
setting; Large or Small break the layout and there is no media query to
adapt.

**The media element is picky about its context.** Audio must play in a
1px in-flow `<video>` — never `<audio>`, never `display:none`. You cannot
swap a `<source>` in place; each track is a full page load. Attach the
source as a `<source>` child with an explicit `type`, or nothing loads.
And **never clip an ancestor of the media element**: a wrapper with
`overflow:hidden` silences the audio, while the same wrapper without it
plays.

**Native controls work, and scale.** With `controls` set, the TV draws
its own transport (play/pause/seek/volume/time) and OK operates it. To
enlarge the fixed-height bar for couch distance, use
`-o-transform: scale(N)` — `zoom` does nothing here. A transform takes no
part in layout, so reserve the final size with a percentage-width
`<table>` around it rather than clipping. The bar fades; OK brings it
back. It shows time only for files that play directly.

**Codecs — what needs transcoding.** Plays natively: MP3, AAC, MP4 audio
and video. Live-converted by the app: FLAC, OGG, WAV and the rest. The
set cannot play WebM or Matroska at all, and refuses Serviio's own
TS-family transcode targets — which is why the app runs its own MP3/MP4
pipe rather than leaning on Serviio's transcoder for these.

**Cookies persist.** The browser stores dated cookies across a power
cycle (a session cookie would die, since the browser closes on every
input change). Use them for anything that must survive the per-track page
reload — repeat state, a play queue, resume position — and keep them
small, because they ride every request including the media stream.

**Almost no media events fire.** `loadstart`, `canplay`, `playing`,
`play`, `pause` do not arrive. `timeupdate` does. Drive any state the
page shows (a play/pause glyph, a clock) off `timeupdate`, and set it
optimistically when you issue a command rather than waiting for an event.

**The console lane.** Serviio's REST on `:23423` is scriptable and
unauthenticated on the free tier — it is how you assign renderer profiles
and trigger library refreshes. A plain server-rendered page over it gives
you a console the set can actually open (Serviio's own is 500 KB of JS
the era browser cannot run).

**Where you are in the library.** The app's duration index maps a DIDL
title back to its file path, so a player can show which album/disc/copy is
actually playing — reuse it, it costs nothing you are not already
computing for the transcode lane.

## Rule of the road

The **method** here is fair game — it is our reverse-engineering, and it
reproduces no Sony code. The **signed widget bundles** are Sony's, and the
signature means you serve them exactly as they exist on your own set: pull
them from your set or your own backup, not from a modified or third-party
copy. Whether a preservation archive of those bundles should be
redistributed is the right-to-repair movement's call, not something this
guide does. See [right-to-repair.md](right-to-repair.md) and
[withheld-by-catalog.md](withheld-by-catalog.md).

Do not point any firmware or update host at yourself. Do not open the set
to chase the deeper (firmware/UART) lanes on a unit you still use — that
is for a spare. The two DNS overrides and the content lanes above are the
whole safe surface.

## Related

- [withheld-by-catalog.md](withheld-by-catalog.md) — the evidence that the
  apps were finished then withheld
- [worldclock-schema-reconstruction.md](worldclock-schema-reconstruction.md)
  — the first reverse-engineered widget config, and the invisible-asset method
- [era-key-vocabulary.md](era-key-vocabulary.md),
  [era-media-element.md](era-media-element.md) — the measured platform facts
- [trackid-bgmsearch-recovered.md](trackid-bgmsearch-recovered.md) — a
  service that is documented but not revivable without opening the set
- `tools/serviio/tv-mediabrowser/` — the media app and its own README
