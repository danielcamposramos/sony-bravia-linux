# Project status & partner guide — 2026-09-15, updated through 2026-09-18

This is the one document a **cold-start partner — AI or human — reads
first**. It maps everything the project has done, what is live and
verified today, how to operate and extend it, and where the deep
documentation lives. Everything here is shareable; material we keep
private (Sony-copyrighted archives, credentials) is *not* documented
here — it lives in a sibling offline folder with the owner (see
[Private material](#private-material)).

If you are an AI partner: read this file end-to-end, then the doc map
at the bottom, then the *Rules of engagement* section twice. Those
rules are hard constraints, not suggestions.

## The mission

Port a VLC-class media experience onto pre-Android, Linux-based Sony
BRAVIA TVs — right-to-repair work on owner hardware. The sets are
phenomenal panels (X-Reality PRO, active 3D) that Sony EOL'd: smart
services dead, firmware downloads pulled. The goal is an owner-run
LAN stack that gives these TVs capabilities Sony's dying cloud never
delivered, plus the longer arc of understanding the platform well
enough to run owner-chosen software on it (see
[feasibility roadmap](feasibility-roadmap.md)).

## Test hardware (both on the LAN, DHCP-pinned by MAC)

| Model | Year | Chassis | LAN IP | Role |
|---|---|---|---|---|
| KDL-46EX725 | 2011 | AZ2-F ("BATV") | 192.168.0.22 | **live test target** |
| KDL-46HX855 | 2012 | AZ3F ("ATREYU") | 192.168.0.21 | **never crash-test** — it is the workstation's HDMI monitor |
| d2server | — | Debian 12 | 192.168.0.60 | media server (Serviio 2.5, all app services, media disks) |

The EX725 is the test bed for everything. The HX855 is the better
set (12-bit, active 3D) and gets changes only after they are
owner-verified on the EX725.

## Where the project stands (2026-09-18)

**The media experience is DONE and owner-verified live.** Both TVs
browse the full Serviio library on d2server via an era-lean web app
and play:

- **Every audio format in the library** — mp3 native; flac/wma/m4a/
  wav/ogg through a live transcode pipe; mpc/wv (which Serviio cannot
  serve at all — no DIDL `res`) resolved by title/duration and piped
  too. Owner-verified per-format on the TV.
- **Every video format that matters** — MP4/H.264 direct (up to
  1080p High@L4.0 SBS 3D); MKV/AVI/WMV/WebM/RMVB via an on-demand
  cached faststart-MP4 transcode lane; mpg/mpeg direct. Dolby AC-3/
  E-AC3 bit-exact through the set's own decoder. Owner-verified.
- **Player UX (rewritten 2026-09-18 for the era's real limits)** — the
  player is now the set's own native transport, enlarged ~3x with
  `-o-transform:scale()` for couch distance, cover art as the poster.
  Our JS owns only what the native bar cannot do: prev/next in folder
  (wrap-around), repeat-this-track persisted in a dated cookie (the
  browser dies on every input change, so state must survive page
  reloads), and back. A `/manual` page on the TV documents the keys
  and codecs in the user's language. Design history and the measured
  platform facts behind it: `era-media-element.md`,
  `era-key-vocabulary.md`, and the public method guide
  `build-your-own-bravia-portal.md`.
- **The remote's real key model is now measured, not guessed** (see
  the key section below) — the multimedia keys do not exist as
  keydowns on this platform; the on-screen native transport is the
  only transport an app can have.

All of it runs as **systemd services on d2server** under a single
bucket target, surviving reboots, with a config file making the
install portable. That is the "VLC on a 2011 TV" milestone: reached.

Alongside it, research lanes continue: firmware analysis, the
widget/applicast lane, Presto engine CVEs, kernel survey, and the
right-to-repair sharing plan.

## The live media stack

```
   EX725 (.22) / HX855 (.21) — era Presto browser
        │  plain HTTP, arrow-key nav, CERS sendText delivery
        ▼
   d2server (192.168.0.60)
   ├── :8090  tv-mediabrowser (bravia-mediabrowser.service)
   │            ├─ UPnP SOAP browse ──> Serviio :8895
   │            ├─ /stream/  Range/206 proxy (same-origin trick)
   │            ├─ /atr/    live audio transcode pipe (ffmpeg → MP3 320k/48k)
   │            ├─ /tr/     on-demand video transcode → cached faststart MP4
   │            └─ /keys    remote keyCode probe (logs KEYPROBE lines)
   ├── :8443  rd1 HTTPS portal (bravia-rd1-probe.service, TLS1.0-era)
   ├── :8895  Serviio 2.5 media server (serviio.service, /opt/serviio)
   ├── :23423 Serviio console REST (renderer profile assignment — scriptable)
   └── :80    Apache (portal pages; era-TLS vhost for the TV homepage lane)
   media:     /mnt/arquivos2 (Música + Vídeos, CIFS-shared)
```

Key architectural facts a partner must not re-learn the hard way
(all live-proven, see `tools/serviio/tv-mediabrowser/README.md`):

- The era browser can't run SPAs (no CORS, tiny JS heap, "page too
  big to display") — everything is **server-rendered HTML** with
  small inline JS.
- The era player accepts exactly **progressive faststart MP4**; live
  TS (what stock DLNA transcode serves) is refused — that's why the
  transcode lane lives app-side, not in Serviio.
- Serviio binds `res` URLs to the browsing client's IP → the app
  **proxies media through itself** (`/stream/`), browse client ==
  fetch client.
- Serviio's own MediaBrowser is Pro-walled (errorCode 554) and
  unusable on the era browser anyway; we keep its structure and swap
  the delivery to plain UPnP ContentDirectory (port 8895, no auth).
- The era player sends `Range: bytes=0-` and expects **206** on the
  video lane.

### Files

| Path | What |
|---|---|
| `tools/serviio/tv-mediabrowser/server.py` | the whole app (one file, stdlib only) |
| `tools/serviio/tv-mediabrowser/config.ini.example` | config template — copy to `config.ini` |
| `tools/serviio/tv-mediabrowser/README.md` | app deep-doc: architecture, lanes, formats |
| `tools/serviio/tv-mediabrowser/tests/` | 4 regression batteries (see below) |
| `tools/systemd/` | the two bravia units + the bucket target + deploy README (serviio.service and apache2.service are stock distro units, deliberately not rewritten here) |
| `tools/serviio/user-profiles-3d.xml` | Serviio renderer profiles (see Serviio side) |
| `tools/bravia_ircc.py`, `tools/bravia_sei3d.py` | remote control + SEI 3D injector |

## How to operate

### Deploy layout (d2server)

App code lives at `/home/pvpgn/tv-mediabrowser/` (server.py,
config.ini, README, cache/, server.log), rd1 portal at
`/home/pvpgn/rd1-portal/`. Serviio at `/opt/serviio` (profile at
`/opt/serviio/config/user-profiles.xml`). Units are in
`/etc/systemd/system/` — `tools/systemd/README.md` is the deploy and
migration procedure.

### Service control

```bash
systemctl status bravia-stack.target        # the bucket
sudo systemctl restart bravia-mediabrowser.service
```

`bravia-stack.target` wants `bravia-mediabrowser.service`,
`bravia-rd1-probe.service`, `serviio.service`, `apache2.service` —
one handle that pulls up the whole TV lane at boot.

**Restart safety rule (hard):** before restarting anything that
serves the TVs, check nobody is streaming — the stack serves on
:8090/:8443 (app + portal), :8895 (Serviio, both TV render paths and
the app's browse), and :80/:443 (Apache):

```bash
ss -tn state established '( sport = :80 or sport = :443 or sport = :8090 or sport = :8443 or sport = :8895 )'
```

**Kill/start rule (migration-era, hard):** under systemd use
`systemctl restart <unit>` and this rule mostly doesn't apply — but
if you ever must kill a process by pattern (manual migration runs,
nohup-era processes), the kill and the start must be TWO separate
SSH calls, and the plain process pattern must not appear anywhere in
the same command line — `pkill -f "server.py 8090"` in a command
whose own text contains "server.py 8090" kills your SSH session
mid-command (this happened; exit 255). Use bracket patterns
(`pkill -f "[s]erver.py 8090"`) and even then verify the string
isn't in your own command line. Also note a pkill against a
systemd-managed process just triggers Restart=on-failure in 3 s —
restart through systemd, not the pattern kill.

### Config surface

Everything host- and install-specific is in `config.ini` next to
`server.py` (see `config.ini.example`), overridable with
`BRAVIA_CONFIG=/path`. Precedence per option: **env var > config
file > built-in default**. Sections: `[app]` bind_host/port,
`[serviio]` host/port, `[library]` roots/cache_dir, `[keys]` the
measured key table (see the key section above — the era media keys do
not exist as keydowns, so the block maps what does arrive). A CLI port
arg still wins over the file (the systemd unit passes 8090). On
startup the app prints the resolved config path, media roots and
keymap to `server.log` (the unit runs Python unbuffered so this appears
immediately).

### The remote's real key codes — measured, not guessed

The original `[keys]` defaults were Android-TV-family **guesses**. The
`/keys` probe page plus glyph/font/cookie probe pages settled it on
the EX725 (2026-09-18): **the multimedia keys produce no keydown at
all** — PLAY, PAUSE, STOP, PREV, NEXT are simply not delivered to the
page. What arrives is `13` OK, `37` left (and REW), `39` right (and
FF), `38` up, `40` down; the four colour keys belong to Opera (GREEN/
YELLOW = history back/forward, RED/BLUE = page bottom/top) and are not
bindable. The `[keys]` block in `config.ini.example` now carries the
**measured** table, and the full map — keys, glyph coverage, the
Medium-font caveat — lives in
[era-key-vocabulary.md](era-key-vocabulary.md). The on-screen native
transport is the only transport this platform can give an app; that is
why the player was rewritten around it. `/keys` stays: run it on any
*other* set before trusting these numbers there.

### Regression batteries

Four batteries cover the app's live-proven behaviors. Run from the
`tv-mediabrowser` directory:

```bash
BRAVIA_SKIP_INDEX=1 python3 tests/test-config-keys.py    # config surface + keymap + /keys
BRAVIA_SKIP_INDEX=1 python3 tests/test-player-ux.py      # prev/next/repeat player UX
BRAVIA_SKIP_INDEX=1 python3 tests/test-mpcwv-fix.py     # mpc/wv resolve + relative URLs
BRAVIA_SKIP_INDEX=1 python3 tests/test-verify-fix.py     # rmvb/webm index + mime table
```

They monkeypatch the UPnP browse so they run offline; each prints
`RESULT: ALL PASS`. Run them after any server.py change. They are
also the fastest way for a new partner to understand the app's
contract: each check names a live-proven behavior.

## Serviio side

- **Renderer profiles** (`tools/serviio/user-profiles-3d.xml`,
  deployed at `/opt/serviio/config/user-profiles.xml` — `/opt/serviio`
  is a symlink to the current install, `serviio-2.5/`):
  - `sony2011x` (extends stock `sony2011`, which extends `sony2012`):
    the daily driver for both
    TVs — raw delivery for everything the sets play natively, LPCM
    for the lossless oddities, and the **3D fix** — H.264 SEI frame
    packing insertion so MVC 3D titles play (the reason the repo
    exists; see `tools/serviio/serviio-3d-explainer.md` and the
    forum-post drafts in the same dir).
  - `tvbox-vlc` (deployed 2026-09-15, verified by a 6-agent adversarial
    workflow, 0 findings): direct-pass profile for the two Android TV
    boxes on the LAN (.24/.25) that run modified VLC — everything
    deliverable raw, Audio→lpcm only for mpc/wv/ape. Assigned to both
    boxes via the console REST API after a full Serviio restart; the
    TVs' sony2011x assignments survived untouched.
- **Console REST API** (found by reading serviio-web-console.jar):
  `GET/PUT http://127.0.0.1:23423/rest/status` with an
  `Accept: application/json` header returns/accepts the renderer
  registry — `PUT` with `renderers[].profileId` changed is exactly
  Console > Status > Devices > Save. `POST /rest/action {name,
  parameter}` for RPC (stopServer/startServer). This makes renderer
  assignment scriptable — no GUI needed. (Port 23423 is the console
  REST listener; 23424 is the API/mediabrowser listener.)
- **Force a library refresh** (after adding files):
  `POST /rest/action` with `name: forceLibraryRefresh`.

## Research lanes — state of each

| Lane | State | Docs |
|---|---|---|
| Platform identification | DONE — MIPS mipsel "ATREYU", glibc 2.7, DirectFB/Qt/Opera, Linux 2.6.35-era | `platform-map.md` |
| Live CERS/IRCC remote API | DONE, tool `tools/bravia_ircc.py` | platform-map |
| UPnP DMR playback | DONE — Serviio renders to both sets | liverecon notes |
| LAN media MVP → full app | DONE — this stack, owner-verified | tv-mediabrowser README |
| 3D lane (SEI injector) | DONE — `bravia_sei3d.py`, ffmpeg wrapper, profile fix; batch conversion runs server-side | serviio-3d-explainer |
| 3D-signalling campaign | **Pipeline end-to-end + serving side engaged.** Encode→remux→player chain (2026-09-16): HandBrake **PR #8100 merged** (x264 frame-packing SEI, closes their #5826); ffmpeg [#24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530) + [#24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531) filed; StaxRip #1873, x265 #970 posted; mpv [#18489](https://github.com/mpv-player/mpv/issues/18489) + [PR #18490](https://github.com/mpv-player/mpv/pull/18490) **in review** (hostile start → 8 technical threads answered same day in the owner's own words; CI still never ran — first-time-contributor gate; follow-up context comment posted on #18489); BD3D2MK3D videohelp thread [closed out](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803796) with r0lZ's cross-brand confirmation; two LTT audience posts (3D-theater [16936161](https://linustechtips.com/topic/1589907-i-built-a-3d-theater-in-my-basement/?do=findComment&comment=16936161), Steam Frame [16936512](https://linustechtips.com/topic/1642726-the-steam-frame-changes-everything-full-review/?do=findComment&comment=16936512)). Second wave (2026-09-18), the serving side: mkvmerge [Codeberg #6309](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309) **filed as the owner** (no AI disclaimer per mbunkus doctrine); Jellyfin [PR #18060 comment](https://github.com/jellyfin/jellyfin/pull/18060#issuecomment-5726381078), UMS [#6329](https://github.com/UniversalMediaServer/UniversalMediaServer/issues/6329), Gerbera [#3937](https://github.com/gerbera/gerbera/issues/3937) (no-remux SEI injection). **All upstream threads are email-trigger watch only — never poll.** Ecosystem evidence base: `3d-signalling-ecosystem.md` | `tools/serviio/upstream-3d-issues/`, `docs/3d-signalling-ecosystem.md` |
| rd1 portal / homepage lane | DONE — Unbound DNS override on the LAN points `rd1.sony.net` at d2server; era-TLS vhost serves the TV's homepage with a media link | liverecon notes |
| BIV / Bravia video lanes | DEAD (server-side) — registration unlocks nothing; documented so nobody retries | liverecon/biv-video-lane.md |
| Applicast widget lane | ACTIVE — **Sony's CDN is still live (2026-09-17)**: preservation sweep recovered 5 never-archived bundles + a second namespace (`/WsIndexes`, `/WsCatalogs`, `/WidgetCatalogs` incl. AZ1) across 3 hosts, 137/168 URLs answering. Key finding in `withheld-by-catalog.md`; programming model documented publicly. **Fronts archived (2026-09-17):** the load-bearing Sony fronts (AZ3 EU/BR catalogs, AZ1 catalog, bundle manifests, OSS service) now have Internet Archive snapshots beside the live URLs — table in the repo README; archive links must use `https://` (the `http://` form returns 503) | `research/appliwidget-programming.md`, `withheld-by-catalog.md`, README "Live fronts and archive snapshots" |
| Firmware decrypt | STALLED — whole-file AES, no public decryptor; 6-image corpus offline for differential work | platform-map, roadmap |
| Presto engine CVEs | NOTED — 2011-2628 and era-adjacent, no exploit built; not the current focus | `research/presto-cve-2011-2628.md` |
| Kernel survey | DONE — 2.6.35 era privesc surface mapped | `research/kernel2635-survey.md` |
| Senior-partner reviews | DONE — 3 external reviews (Opus/DeepSeek/Kimi) folded into the roadmap | `partner-review.md` |
| Right-to-repair sharing | **Wiki update POSTED 2026-09-18** — consumerrights.wiki (FULU) product-line page now carries the five dated Sony end-of-service notices (each naming both models, archived), the regional-documentation asymmetry, the browser-3D incident, the corrected firmware-removal claim (an overclaim of ours, narrowed to exactly what Sony's page supports), and a Brazil CDC context section flagged not-legal-advice. Noticeboard follow-up post drafted paste-ready alongside. Rossmann/repair.wiki outreach drafts queued, grounded in his own live Sony campaign (quotes pinned to source) | `right-to-repair.md`, `rossmann-outreach.md`, `wiki/`, `sony-end-of-service-statements.md` |
| Era browser & media element | DONE 2026-09-18 — the platform's input/render/storage model measured end to end: no media-key keydowns, colour keys are Opera's, glyph coverage (Arrows block = tofu), the `<video>` element's context rules, native controls + transform scaling, dated cookies, `timeupdate` only. The probe pages that produced it ship in the app (`/probe`, `/keys`) | `era-key-vocabulary.md`, `era-media-element.md`, `build-your-own-bravia-portal.md` |
| Browser 3D blocked | DOCUMENTED, one open lead — the panel detects the 3D signal in browser video but cannot switch (auto or manual) although the same panel switches from other inputs; i-Manual documents the feature with no input restriction. Filed as a wiki incident. Open test: does the TV's *native DLNA* player switch 3D for the same file? (that lane is not browser-gated) | `3d-blocked-in-browser.md` |
| TrackID / BGMSearch | DOCUMENTED, NOT REVIVABLE without a spare set — the buttons emit zero packets (firmware-local tombstone); the Gracenote path (SMRP → playstation.net) and the client bundle are mapped from Wayback. Deferred, not dead: an older firmware might carry the code | `trackid-bgmsearch-recovered.md` |
| Judge-by-the-cover record | DONE — the AI-policy landscape survey across the video-tooling industry (mpv, mkvtoolnix, HandBrake, Codeberg): everyone gates on owned/understood/reviewed, no one on "was AI used"; our 42-line standard-based patch is the case study | `judging-by-the-cover.md` |
| Legacy 3D formats (act three) | **CHARTERED 2026-09-18** — enable all 3D content ever made: row-interleaved/column/checkerboard are standardized `frame_packing_arrangement_type` values (0/1/2), so conversion to SBS+SEI is standard-speaking-to-standard (`stereo3d` deinterleave → repack → SEI; transcode lane, pixels change — honest scope vs acts 1–2); anaglyph is colorimetry (CRT-tuned content on WLED panels → per-channel filter chain, plays as-is + glasses). Proper path per owner: convert (front B). First corpus: the 3D-photography community (**phereo**) material (11 JPS + SBS + anaglyph set, **private test use, community's copyright — never republished**; the owner contributes two Optimus 3D exemplars + the Gadmei T883-3D tablet and archive, and the subject depth). Also documents the YouTube 3D player withdrawal — the pattern at platform scale, silently. Results on our stack first; upstream after, same doctrine | `legacy-3d-formats.md` |
| 3D-photo gallery lane | **CHARTERED 2026-09-18, reframed same day** — the 3D photo player these sets never got (Sony's stock slideshow was 2D-only on a 3D panel). **Measured: phereo is failing** (`api.phereo.com` 504 at 60 s, twice; static assets 200 in seconds) while **[stereopix.net](https://stereopix.net/) answered 200 in 2.5 s** — so the lane is built source-agnostic, local library first (it cannot 504), remote adapters second, nothing depending on phereo being alive. Third-party reports (DPReview, photo-3d groups.io) describe phereo as long down/abandoned — cited as reports, our 504 is the measurement. Consequence: the corpus is **preservation material**, not just test material (provenance rule tightens, never loosens). Four JackDesBwa repos read: PhereoRoll3D (the working API map), PhotoRoll3D (multi-source is goal not code — one commit, no adapters; it reads as *his own* preservation response to phereo dying), StereoWebViewer + threejs-StereoscopicEffects (**both need WebGL — the era browser has none, so not one of the four can render on the set**; that closes the era-Opera question and is exactly why we render server-side). His `interleaved` output is marked "Not tested on actual device yet" since 2018 — **we own four such devices**: the contribution offer in the draft. Inherited open test **answered 2026-09-18 on both sets**: the native DLNA photo path opens the 3D menu but offers only 2D→3D, no side-by-side for stills; MPO bytes renamed `.jpg` also stay flat; the remaining door is a real `.MPO` on USB (staged). **ANSWERED 2026-09-19: MPO works from USB on both sets** — auto-engages 3D once the file is spec-correct (both views typed Disparity `0x020002`; our writer had typed view 0 Baseline Primary, which is why every earlier MPO stayed flat). **Network stays flat** (HX855 measured; EX725 was off, inferred from its identical declaration): correct MPO served byte-exact as `image/jpeg` → 2D. Both sets' GetProtocolInfo declare `image/jpeg` JPEG_LRG/MED/SM only, no MPO profile; Serviio does not index `.mpo` at all. **Software gate, proven by probe 2026-09-19** — `tools/mpo_dlna_probe.py` served the same MPO bytes four ways: `image/jpeg`+`.jpg` (control) and `image/jpeg`+`.mpo` are **listed and flat**; `image/mpo` with and without `DLNA.ORG_PN=MPO_LRG` are **not listed at all**. So the set filters its browser against its own GetProtocolInfo (profile, not capability), and the URL extension is not the dispatcher. **No DLNA-server change can fix these sets** (UMS has indexed `.mpo` since 2008, Gerbera indexes it via libmagic; both announce it as plain JPEG). Same board, same file, 3D from USB, hidden or flat over the network: a firmware target — see `3d-photos-on-bravia.md` | `legacy-3d-formats.md`, `3d-photos-on-bravia.md` |
| 3D catalog + the anaglyph inverse | **BUILT 2026-09-18** — two tools, both measured. `tools/bravia_3dcatalog.py`: detection lifted out of `ffmpeg-3d-wrapper.sh` (which already types every live transcode, then throws the answer away) and written to a JSON index with evidence + confidence + owner override per row; **first run 140 files → 122 indexed (81 anaglyph, 30 sbs, 11 jps)**. `tools/bravia_anaglyph.py`: the inverse the owner asked for, for material preserved only as anaglyph — red carries left, green/blue carry right, each eye rebuilt **only** from its own channels; **disparity recovered exactly on 11/11 corpus JPS pairs**, left luma 23–37 dB. Two traps hit and measured rather than shipped: a pointwise operator **cannot** create disparity (first attempt: perfect colour, **0 px** stereo), and naive channel-borrowing makes the two eyes **byte-identical** (1 channel + 2 channels = 3). So `--mode mono` is default and robust on any red/cyan source; `--mode color` is disparity-warped with iterative red removal, beats mono on good matches, loses on repetitive texture, off by default. Found anaglyphs are often not Dubois at all, which mono survives and colour does not. **End file**: `video` subcommand converts anaglyph movies to SBS + frame-packing SEI (verified present). Also emits a pure-ffmpeg filtergraph so the app can convert on the fly and `server.py` stays stdlib-only. Campaign loop closed: ffmpeg writes the SEI but **not** the Matroska StereoMode — our own tool hit the exact gap, and prints the `mkvmerge --stereo-mode 0:1` fix-up that [Codeberg #6309](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309) asks to be automatic. **Measured blocker for the native-photo test: Serviio indexes `.mp3 .jpg .flac .wma .mkv .avi .mp4 .m4a .flv .wav` only — no `.jps`, no `.mpo`, no `.png`**, so the corpus is invisible to DLNA and the set must be handed `.jpg`/`.mpo`. Still to build: the portal's 3D category browsing the index | `legacy-3d-formats.md`, `tools/bravia_3dcatalog.py`, `tools/bravia_anaglyph.py` |
| Audio: what the sets really accept | **MEASURED 2026-09-18** — three paths, three different capability lists, in `audio-capabilities.md`. **HDMI** (from the sets' own ELD, read while the HX855 was the workstation's monitor): LPCM 2ch at 32/44.1/**48 kHz** in 16/20/**24-bit**, AC-3 6ch ≤640 kbps, nothing else; the driver agrees (`RATE: [32000 48000]`), so **48 kHz is the ceiling, measured twice**. **DLNA**: `audio/L16` (16-bit by definition), MP3, WMA, plus AAC on the HX855 only — no FLAC, **no 24-bit path over the network at all**. **Inside MP4 over DLNA, the sets do more**: AC-3 5.1/2.0 → "Dolby Digital", **E-AC3 5.1 and 7.1 → "Dolby Digital Plus"**, AAC 5.1 plays, **DTS silent on both sets**, TrueHD cannot even be muxed into MP4. Owner's library sampled: ~1 file in 5 is hi-res (24/96, some 24/192), and **Serviio downconverts it twice** (depth and rate) because L16 is all the renderer takes | `audio-capabilities.md` |
| Serviio Surround profile | **BUILT + LIVE 2026-09-18** — `user-profiles-3d.xml` now ships two profiles: `sony2011x` (unchanged, everything normalised to AC-3 in TS) and **`sony2011xs` "3D Enhanced, Surround"**, which serves **MP4 + h264 ≤L4.1 + {AC-3, E-AC3, AAC} native** so the original Dolby arrives untouched, transcoding only what the set cannot decode in MP4 (DTS, TrueHD, FLAC, MP3, LPCM), now at **640 kbps** (the ELD's declared max, was 384). Both TVs reassigned via the console REST; **owner-verified: E-AC3 clips replay through Serviio showing "Dolby Digital Plus", and the log shows no transcoding session** — native delivery. MKV cannot benefit: Serviio has **no `mp4` target container**, so Matroska must still go to TS, which is why the lossless MKV→MP4 conversion is the answer for the 3D library | `serviio-3d-explainer.md`, `tools/serviio/user-profiles-3d.xml` |
| Kodi: second server + upstream | **DONE 2026-09-18** — the 3D fix reproduced through a different maker's server (Kodi's UPnP, never transcodes, byte-exact): SEI-only MP4 → 3D engages; same file minus 791 bytes of SEI → flat; MKV → not listed. Harness committed (`tools/kodi-dlna-test/`) with the three traps it cost (`--init`, a free X display, neutral filenames). Upstream: [xbmc/xbmc#29337](https://github.com/xbmc/xbmc/issues/29337) — **our first claim was wrong** (Kodi *does* read the SEI, via FFmpeg frame metadata; caught by running it, see memory `verify-by-running-before-filing`) and was corrected in place into the real finding: every MP4 advertised as `MPEG4_P2_SP_AAC`, wrong about video **and** audio codec | `3d-signalling-ecosystem.md`, `tools/kodi-dlna-test/` |
| UMS: issue became code | **MERGED 2026-09-19** (`bd032ab0f8e6`, by SubJunk; CI green on Lint, Linux 22.04/24.04, Windows, macOS ARM/Intel) — the campaign's **second merge**, after HandBrake. Filed at the maintainer's request — SubJunk asked "do you have any interest in providing code for these improvements?" on [#6329](https://github.com/UniversalMediaServer/UniversalMediaServer/issues/6329), so it was converted into [PR #6330](https://github.com/UniversalMediaServer/UniversalMediaServer/pull/6330) the same day, carrying **both** halves: `-x264-params frame-packing=N` on libx264 transcodes whose output is frame-packed (Output3DFormat-aware, anaglyph/2D skipped, defers to CustomFFmpegOptions), and the Bravia profiles for the generation (`EX725`, `HX`, `HX75`) — the **EX725 profile had no `f:mp4` line at all**, so every MP4 was transcoded on a set that plays it directly, and E-AC3 is now declared for MP4 (decoded to 7.1, shown as "Dolby Digital Plus"). #6329 answered in the owner's words and closed onto the PR; two triage comments sweep 14 search terms and conclude honestly that **only #6329 is closed by it**, with #1775/#5974 flagged as same-family-different-mechanism and #6099 ruled out (2017 Android-era set, v15 regression). Limits stated in the PR, not left for review: **no local build** (no Maven, Java 25 vs the project's 17) so the Java change has a syntax check only, and the profile edits stop at the measured chassis generations | `tools/serviio/upstream-3d-issues/README.md` |
| Player/framework survey + Media3 + VLC | **2026-09-19** — every open project in the chain read from source (`docs/3d-signalling-ecosystem.md`). **GStreamer and MPC-BE already do it correctly** (GStreamer's `h264parse`→caps→`x264enc` auto-write loop is the reference to cite everywhere else). **VLC has a measured gap**: 3.0.23 decodes the SEI and renders stereo from it, then drops it on re-encode unless `--sout-x264-frame-packing` is passed by hand; its chromecast module never sets it either (though the cast path cannot carry automatic 3D regardless — the device decodes to HDMI). **Media3/ExoPlayer never parses the SEI at all**; filed [androidx/media#3419](https://github.com/androidx/media/issues/3419), reviving [ExoPlayer#7869](https://github.com/google/ExoPlayer/issues/7869) whose 2020 rejection was literally "you are the first one to ask" — owner will sign Google's CLA if they take the patch. **Chromecast is not contributable** (closed receiver/SDK; Cast docs never mention 3D). **VLC goes to the owner to submit**: VideoLAN bans AI-generated contributions in its GSoC programme (wider scope unconfirmed, wiki 502) | `docs/3d-signalling-ecosystem.md`, `tools/serviio/upstream-3d-issues/README.md` |
| Campaign follow-up round | **POSTED 2026-09-18** — seven live threads. From this session (not gated): Gerbera #3937, UMS #6329, Jellyfin PR #18060, repo Discussion #1. By the owner in his own words (gated targets): mpv PR #18490, FFmpeg #24531, Codeberg mkvtoolnix #6309. All email-trigger watch, never polled | `upstream-3d-issues/README.md` |
| Consumer Rights Wiki, reviewer follow-up | **2026-09-19, the pt-BR argument was adopted** — after the talk-page reply, another editor created the missing CS1 language categories including Brazilian Portuguese and Russian, and reviewer **Sojourna** switched the article's eight Portuguese citations from `pt` to `pt-br` and replaced all 28 `&mdash;` entities with the symbol. The live wikitext is saved as the new baseline (`wiki/consumerrights-wiki-entry-live-2026-09-19.txt`): future edits must start from it, never from our local copies, or they would revert another editor's work. Update 9 changed one line against that baseline, tagging the Russian source `lang=ru`; **POSTED 2026-09-19 by the owner in the browser.** The `pt-br` category page was created, but `Category:CS1 русский-language sources (ru)` still does not exist, so it renders red for now. Left on purpose as early adoption: the tag is correct, and the link turns blue by itself when anyone creates the category page, with no further edit to the article. Thank-you note posted to Sojourna on the talk page | `wiki/consumerrights-wiki-entry-2026-09-update-9.txt` |
| Consumer Rights Wiki, update 8 | **POSTED 2026-09-19** — citation language codes restored as ISO 639 codes after reviewer **Sojourna** answered the talk-page question (MediaWiki does not distinguish pt-BR from pt for CS1). Measured against the wiki's own category list before editing: `pt`, `de`, `it`, `es`, `ja` category pages **exist**; `pt-br` and `ru` **do not** — which is exactly what produced the red-link category in update 6. Ten citations tagged (8 pt, 1 de, 1 it); the Russian source left untagged rather than red-link it. Talk-page reply asks the maintainers to create both missing categories, arguing pt-BR on substance (the module already renders the *português do Brasil* autonym, so the code is supported; and on a consumer-rights wiki a Sony Brasil page and a Sony Portugal page are different products, policies and legal regimes) | `wiki/consumerrights-wiki-entry-2026-09-update-8.txt` |
| Consumer Rights Wiki, update 7 | **POSTED 2026-09-19** — the 3D incidents rewritten from the new measurements. The still-photo incident is **corrected, not extended**: MPO from USB works on both sets, so the old "no stereoscopic option" claim was wrong; what is true is narrower and worse — the sets accept **only** MPO, **only** from USB, and show every other valid stereo photograph (JPS from a 3D phone, side-by-side JPEG, community pairs) flat, with no message explaining why. Adds the set's own on-screen **"Sinal 3D foi detectado"** notification to the internet/app incident plus the USB contrast, the four-variant probe result (items the set never declared are hidden), and Brazilian price context — minimum wage cited to Decreto 7.655/2011, the television's price deliberately **approximate** (owner's recollection and circulating figures disagree; archive.org was offline for the retail captures) | `wiki/consumerrights-wiki-entry-2026-09-update-7.txt` |
| Consumer Rights Wiki, update 6 | **POSTED 2026-09-18, cleanup notice answered** — reviewer flagged "some citations not formatted"; the article was rebuilt to the `ProductPreload` outline with all 37 refs converted to `{{Cite web}}` (36 templates), Sony's source-code obligation wrapped in `{{Quote}}`, incident headings dated, "Products" → "Affected models", and the firmware incident narrowed further (the support route is untested — stated as such). Two traps found by measurement: the paste path **breaks source lines at 4096 chars** mid-token (that, not a bad paste, caused the first round of "CS1 errors"), and CS1's `|language=` / bare `|url-status=` add tracking categories **that do not exist on this wiki** and render as red links — both removed, language moved into the visible note. Final categories: only the two from `{{Incomplete}}` | `wiki/consumerrights-wiki-entry-2026-09-update-6.txt` |
| Consumer Rights Wiki, update 3 | **POSTED 2026-09-18** — the whole article pasted in source mode, built from the live page. Adds the **3D still-photograph incident** (five archived Sony sources contradicting each other across regions) and strengthens the DLNA 3D incident with the independent second-server reproduction; eleven-language docs added to See also | `wiki/consumerrights-wiki-entry-2026-09-update-3.txt` |
| awesome-stereoscopy | **CREATED 2026-09-18** — [the field had no curated list](https://github.com/danielcamposramos/awesome-stereoscopy); searches under every wording returned nothing. 200+ verified entries organised by one argument: 3D means depth, and depth is what two eyes are for. Prehistory (Mohist camera obscura, Euclid, Ibn al-Haytham, Sushruta), Victorian stereoscopes, Hollywood and the theme parks where 3D never stopped, anaglyph colour codes, the glasses-free phones, headsets as worn stereoscopes, depth capture and 2D-to-3D conversion, generated views, and an explicit **known-gaps** section. Cross-linked with this repo | — |

## Rules of engagement (hard constraints)

These apply to any partner working on this project:

1. **Own hardware, own LAN only.** Both TVs, the TV boxes and the
   server are the owner's property on his LAN.
2. **No DRM circumvention.** PlayReady/WMDRM/Marlin/CI+ are out of
   scope. We serve the owner's own media to the owner's own sets.
3. **Never open the TVs.** Non-invasive lanes only (unless the owner
   explicitly drives a UART adventure — see the roadmap's gates).
4. **Never port-scan the TVs.** Ever. We know their addresses; we
   talk to documented endpoints only.
5. **EX725 (.22) first, always.** Never crash-test the HX855 (.21) —
   it is the workstation's monitor. Changes land on .22, get
   owner-verified, and only then touch .21.
6. **No firmware/update host is ever pointed at us.** The DNS-override
   list on d2server's Unbound is a **closed, owner-approved set of
   exactly two hosts**: `applicast.ga.sony.net` → 192.168.0.60 and
   `rd1.sony.net` → 192.168.0.60. Nothing else is ever overridden;
   adding a host means the owner says so first. `ssm`/`ssm1`/
   `playstation`/`static.internet.sony.tv` are never MITM'd and never
   overridden.
7. **Heavy media jobs run on d2server**, never the workstation
   (ffmpeg/mkvmerge/SEI batches go to .60 over SSH).
8. **Kill and start are two separate SSH calls** (see above).
9. **Nothing Sony-copyrighted enters this repo** — firmware images,
   widget packages, third-party app sources stay in the owner's
   offline archive. See below.
9b. **The preservation archive stays private; distribution is not ours
   to decide.** The AppliCast/BRAVIA material recovered from Sony's
   still-live CDNs (2026-09-17: three hosts, the widget bundles, their
   catalogs and assets) is held offline by the owner. The plan is to
   **share it with the right-to-repair movement** — and if they judge
   that it should be distributed, that call is theirs, not this
   project's. What this repo publishes is the analysis, the paths, the
   method and our own reconstructions; never the recovered bundles.
   Contributing the map back to the Internet Archive is a separate
   decision on the same terms.
10. **Check for live streams before restarting a serving service.**
11. **Pre-publish sweep (hard):** before publishing this repo or any
   part of it anywhere (repair.wiki, a fork, a tarball), sweep for
   key/credential material: `git grep -l "BEGIN.*KEY" $(git rev-list
   --all)`, check no `*.key` or `creds.json` is tracked, and confirm
   the .gitignore tripwires are intact (firmware/, manuals/, widget
   trees, creds.json, `tools/rd1-portal/*.key`). Key material lives
   only in the owner's private archive and on the server.

## Private material

A sibling folder (`sony-bravia-linux.private`, offline, not in this
repo — ask the owner) holds: the Sony-distributed archives (firmware
images, the era widget bundles fetched from Sony's dead servers),
third-party copyrighted app sources, and credentials/key material.
The **public/private split rule**: research notes, protocol
knowledge, our own code, and anything needed to *operate* the stack
are public; Sony-distributed material, credentials, and anything
that identifies other parties' copyrighted code are private. LAN
addresses appear in this repo by the owner's choice (RFC1918,
unroutable, needed for the docs to make sense).

## What's next (pick-up menu)

**Media stack polish** (low risk, high value):
- thumbnails on list pages (poster art is already in the players; the
  list pages still have none)
- audio-track selection for direct-playable MP4s
- receiver pass-through test (HDMI 5.1 advertised, no AVR on the
  verified setup yet)
- album art on top of the music list in album view (instead of
  beside it)
- cookie power-cycle survival check on the set (dated cookies
  persisted across a browser relaunch; a full AC power cycle is
  unconfirmed)

**Closed out of this menu 2026-09-18:** auto-advance/repeat on `ended`
(now built — cookie-persisted repeat, auto-advance to next; the reload
flash is acceptable inside the native-controls player) and the real
key harvest (done on the EX725; the answer is that the media keys
produce no keydowns at all — see the key section).

**Verification tests on the sets** (owner's timing, EX725 first):
- the native-DLNA 3D hypothesis: does the TV's *own* DLNA player
  switch 3D for the same SEI-carrying file the browser cannot switch?
  (the browser-input block is documented; the DLNA lane may not be)
- HX855 promotion of the restored widgets (verified on EX725 only so
  far)

**Pending deploys**: (none — tvbox-vlc renderer profile was deployed
and assigned 2026-09-15; verify on the boxes by browsing mpc/wv and
confirming LPCM delivery)

**Bigger lanes** (see the roadmap for gates and ordering):
- widget lane: run owner-built applicast widgets on the sets
- sony.tvstore.opera.com revival attempt (era Opera store host)
- UART/TFTP boot path confirmation (the unbrickability gate)
- custom kernel + initramfs (Stage 1 of the roadmap, post-gate)

## Document map

| Doc | Content |
|---|---|
| `platform-map.md` | The hardware/software platform in depth |
| `feasibility-roadmap.md` | Staged plan: content → widgets → root → kernel |
| `oss-source-recovery.md` | Sony's 2014 OSS listing **did** include KDL-46EX725 and KDL-46HX855 (archived proof); today it lists 798 KDL models and none from this generation. Recovers the 23-package manifest for our model group and 83 packages KDL-era-wide (incl. the MIPS toolchain); files themselves are 404 live, unarchived, and unmirrored — the kernel survives only in the owner's archive |
| `licence-basis.md` | **Evidence file, not legal advice**: the sets run GPL Linux and Sony shipped the source with its licence; Sony's Source Code Distribution Service is live in 2026 and lists 798 `KDL-` models — **zero** from the 2010–2012 EX/HX/NX/CX generation. Separates what the GPL grants an owner (does not lapse) from the distribution offer (three-year term), and marks the line the widget bundles sit on |
| `right-to-repair.md` | Context + Rossmann/repair.wiki/FULU sharing plan |
| `hdmi-cec-audio-system.md` | **Parked lane, documented**: 26 Sony vendor CEC opcodes + the 102-model audio compatibility table recovered from the AudioControl bundle; why the widget reports unavailable; the untried `device_type=4,5` direction and the zero-risk experiment that would justify it |
| `worldclock-schema-reconstruction.md` | **First reverse-engineered solution**: World Clock's `preference.xml` no longer exists on any Sony server; reconstructed from the widget's own code (Item1=GMT offset, Item2=DST, Item3=AM/PM) and deployed. Includes the reusable method for any dead settings screen |
| `build-your-own-bravia-portal.md` | **The public method guide** — how to give these sets a working portal + media browser on your own LAN with your own hardware: the two (and only two) DNS overrides, era-TLS vhost, the media app, the widget-restore catalog edit, and every measured platform gotcha |
| `era-key-vocabulary.md` | The measured remote/key model: no media-key keydowns, colour keys are Opera's, the glyph coverage table (the whole Arrows block is tofu), the Medium-font caveat |
| `era-media-element.md` | The measured `<video>` element rules: `<source>`+type or nothing loads, never clip an ancestor (silences audio), `-o-transform` scaling + table sizing, `timeupdate` only, dated cookies, the codec canPlayType table behind the transcode lanes |
| `3d-signalling-explainer.md` | The short explainer linked in every upstream post: two signals, which side reads which, the fix |
| `3d-signalling-ecosystem.md` | **The nowhere-else map**: the DVB mandate with honest scope (ETSI TS 101 547-2), the decade of ecosystem symptom threads (Plex/Jellyfin/Serviio/MakeMKV), the cross-brand survey (18/20 videohelp pages, Samsung/LG), recorded-broadcast history (Sky 3D), the fix chain end to end, with timed LTT/Rossmann video citations |
| `3d-blocked-in-browser.md` | The panel detects 3D in browser video but cannot switch (auto or manual) while the same panel switches from other inputs; i-Manual documents the feature with no input restriction; the native-DLNA test that would close it |
| `legacy-3d-formats.md` | **Act three charter** — enable all 3D content ever made: the legacy packings never left the standard (`frame_packing_arrangement_type` 0/1/2/5), conversion to SBS+SEI is the proper path, the anaglyph colorimetry chain, the verified iZ3D sidebar (passive polarized dual-LCD, not glassless — the glasses-free device in the lineage is the Optimus 3D), the YouTube 3D-player withdrawal (the pattern at platform scale, no announcement ever), and the community 3D-photo corpus as first test material (private test use — the photos are the community's) |
| `3d-photos-on-bravia.md` | **3D photos on the set, measured and sourced** — both sets open SBS / half-SBS / anaglyph-derived / MPO-renamed-`.jpg` photos flat over DLNA, and the photo 3D menu offers only 2D→3D (no side-by-side entry for stills); Sony's own support pages contradict each other across DE/RU/IT/BR/JP/UK (archived by the owner, snapshot table inside); Italian owners report MPO stills *did* work from USB on the KDL generation and stopped on Android, and AVForums' 2012 review of the KDL-55HX753 (our board family) states "JPEG over the network, 3D MPO from USB" — **answered 2026-09-19: a spec-correct MPO from USB engages 3D on both sets; over DLNA it stays 2D (HX855 measured), because the network path declares JPEG only — a software gate;** the unmet L/R eye-swap need across ES/BR forums |
| `audio-capabilities.md` | **What these sets accept, audio, by path** — HDMI (from the sets' own ELD: 24-bit LPCM but 48 kHz max), DLNA (L16, 16-bit only, no FLAC), and inside MP4 where they decode Dolby Digital Plus 7.1 natively; why FLAC cannot be "encoded to 24-bit AC-3" (lossy codecs have no bit depth and stop at 48 kHz); and the practical recipe for a hi-res library |
| `i18n/*.md` | **The project in eleven languages** (ja, zh-TW, ko, de, fr, it, es, pt-BR, ru, pl, nl) — the problem and the fix phrased for owners searching in their own words, with the product names; linked from the top of the README. Translated 2026-09-18, native-speaker corrections invited; keep the claims in step with the English docs |
| `judging-by-the-cover.md` | The AI-policy-landscape record: mpv, mkvtoolnix, HandBrake, Codeberg all gate on owned/understood/reviewed, never on "was AI used"; the 42-line standard-based patch as the case study — the "não julgue pela capa" campaign's proof |
| `legal-eula-analysis.md` | Three pillars from Sony's own documents: GPL source (non-disclaimable), 3D display as a function not a "Service", services discontinuation expressly reserved — consumer-rights framing, not a breach claim |
| `regional-documentation-asymmetry.md` | The same product, "different" by region: US i-Manual/EULA/warranty vs BR marketing tips; the CDC framework (art. 18/26/30/32/51), flagged not-legal-advice |
| `sony-end-of-service-statements.md` | Sony's five dated end-of-service notices (Facebook, Skype, SideView, TrackID, Twitter), each naming both models, plus the firmware-removal page — all archived at the Internet Archive with regional copies (Canada/LatAm) |
| `trackid-bgmsearch-recovered.md` | TrackID/BGMSearch: what the service was, the Gracenote SMRP path mapped from Wayback, why the buttons emit zero packets (firmware-local tombstone), and the deferred older-firmware path |
| `manuals-index.md` | Where Sony's own documents live (RefLib doc numbers + links, hosting nothing) and the **provenance split** that decides what may be shared: four Sony-published documents vs. six third-party service manuals, with SHA-256s and the coverage proof that one AZ2-F manual spans 32/40/46/55" |
| `generation-model-map.md` | Which TVs this applies to: AZ1/AZ2/AZ3 generations, service-manual model coverage (32–60" EX725 on one chassis), tier differences (subwoofer/anti-glare/Opera Store), the AZ1 harvest (one widget, dated 2010-04-21; `PAC2.0` XMB plugin; GPSPhotoWidget), and the **check-the-archive-before-declaring-dead** rule |
| `withheld-by-catalog.md` | **The evidence document**: Sony localized the widgets Brazil never got — Portuguese complete, Rio de Janeiro in the city list — and withheld them at the catalog layer. Plus the 2026-09-17 preservation sweep (3 live hosts, 137/168 URLs) |
| `3d-origin-story.md` | Author's 3D history: the 2011 iZ3D license gift (Vadim Asadov) → the SEI campaign; the hologram line that seeded Knowledge3D |
| `rossmann-outreach.md` | Outreach draft to Louis Rossmann, grounded in his own live Sony campaign: quotes pinned to source (Parker Hartline, ASA, the 2023 House hearing — verified, no lawsuit claim), the five Sony videos with timed jump-links |
| `partner-review.md` | 3-partner senior review of the roadmap (2026-09-13) |
| `wiki/` | repair.wiki + consumerrights.wiki page drafts (public versions) — incl. the 2026-09-18 wiki update as posted: five archived Sony notices, the browser-3D incident, the Brazil CDC section, the corrected firmware claim |
| `research/` | Live recon, protocols, CVE notes, kernel survey |
| `research/liverecon/` | Wire captures + analysis from the live sets |
| `tools/serviio/` | Serviio profiles, 3D fix, forum posts, app |
| `tools/serviio/tv-mediabrowser/README.md` | The media app deep-doc |
| `tools/systemd/README.md` | Deploy + service-migration procedure |
| `wiki/` | repair.wiki page drafts (public versions) |

*Status doc written 2026-09-15, updated 2026-09-17 and 2026-09-18. Keep
it current: when a lane changes state, update this file in the same
commit.*