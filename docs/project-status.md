# Project status & partner guide — 2026-09-15

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

## Where the project stands (2026-09-15)

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
- **Player UX** — prev/next in folder (wrap-around, both lanes),
  repeat-this-track toggle, on-screen controls, album art.
- **Multimedia remote keys** — play/pause/stop/prev/next/rew/ff wired
  with a config-driven keyCode map plus an on-TV key probe page.

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
eight multimedia actions. A CLI port arg still wins over the file
(the systemd unit passes 8090). On startup the app prints the
resolved config path, media roots and keymap to `server.log`
(the unit runs Python unbuffered so this appears immediately).

### Discovering the TV remote's real key codes

The `[keys]` defaults are Android-TV-family **guesses**. To learn
the truth: open `http://192.168.0.60:8090/keys` on the TV, press
each remote media button — codes show on screen and beacon to
`/keylog/`, which appends `KEYPROBE code=<n>` lines to server.log.
Paste observed codes into `config.ini [keys]` (comma-list aliases,
`0` disables an action) and restart the service.

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
| Ripper/encoder upstream campaign | **ALL 8 TARGETS ENGAGED — pipeline end-to-end** — HandBrake merged PR #8100 (`b0145ad`, x264 frame-packing SEI, 2026-09-16, closes their #5826); ffmpeg [#24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530) (bug) + [#24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531) (bsf feature) filed; StaxRip #1873, x265 #970 posted; **mpv player side** — [#18489](https://github.com/mpv-player/mpv/issues/18489) + [PR #18490](https://github.com/mpv-player/mpv/pull/18490) **in review** (hostile start → 8 technical review threads answered same day in the owner's own words, no apology; duplication claim refuted on facts; 3 follow-ups offered — see campaign README; archive `/K3D/GitHub/EchoSystems_Stereo3D/`); BD3D2MK3D videohelp thread [fully closed out](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803796) (post #2803756 + r0lZ's reply + owner's closing reply #2803796, all 2026-09-16); mkvmerge ask skipped by owner decision (Codeberg signup paywall — draft retained); **LTT forum post live** (first audience-facing target) — [comment 16936161](https://linustechtips.com/topic/1589907-i-built-a-3d-theater-in-my-basement/?do=findComment&comment=16936161), 2026-09-16 — the 3D-theater video thread; delivers the guide the video promised and the forum asked for | `tools/serviio/upstream-3d-issues/` |
| rd1 portal / homepage lane | DONE — Unbound DNS override on the LAN points `rd1.sony.net` at d2server; era-TLS vhost serves the TV's homepage with a media link | liverecon notes |
| BIV / Bravia video lanes | DEAD (server-side) — registration unlocks nothing; documented so nobody retries | liverecon/biv-video-lane.md |
| Applicast widget lane | ACTIVE — **Sony's CDN is still live (2026-09-17)**: preservation sweep recovered 5 never-archived bundles + a second namespace (`/WsIndexes`, `/WsCatalogs`, `/WidgetCatalogs` incl. AZ1) across 3 hosts, 137/168 URLs answering. Key finding in `withheld-by-catalog.md`; programming model documented publicly | `research/appliwidget-programming.md`, `withheld-by-catalog.md` |
| Firmware decrypt | STALLED — whole-file AES, no public decryptor; 6-image corpus offline for differential work | platform-map, roadmap |
| Presto engine CVEs | NOTED — 2011-2628 and era-adjacent, no exploit built; not the current focus | `research/presto-cve-2011-2628.md` |
| Kernel survey | DONE — 2.6.35 era privesc surface mapped | `research/kernel2635-survey.md` |
| Senior-partner reviews | DONE — 3 external reviews (Opus/DeepSeek/Kimi) folded into the roadmap | `partner-review.md` |
| Right-to-repair sharing | PLANNED — Rossmann/repair.wiki/FULU outreach drafts | `right-to-repair.md`, `rossmann-outreach.md`, `wiki/` |

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
- thumbnails on list pages (Serviio serves cover art on :8895)
- audio-track selection for direct-playable MP4s
- auto-advance to next track on `ended` (deliberately not built —
  the era reload flash made manual prev/next feel better; revisit)
- receiver pass-through test (HDMI 5.1 advertised, no AVR on the
  verified setup yet)
- real keyCode harvest from the TV remotes via `/keys` (deployed
  2026-09-15, awaiting a session in front of the TVs)

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
| `right-to-repair.md` | Context + Rossmann/repair.wiki/FULU sharing plan |
| `hdmi-cec-audio-system.md` | **Parked lane, documented**: 26 Sony vendor CEC opcodes + the 102-model audio compatibility table recovered from the AudioControl bundle; why the widget reports unavailable; the untried `device_type=4,5` direction and the zero-risk experiment that would justify it |
| `worldclock-schema-reconstruction.md` | **First reverse-engineered solution**: World Clock's `preference.xml` no longer exists on any Sony server; reconstructed from the widget's own code (Item1=GMT offset, Item2=DST, Item3=AM/PM) and deployed. Includes the reusable method for any dead settings screen |
| `withheld-by-catalog.md` | **The evidence document**: Sony localized the widgets Brazil never got — Portuguese complete, Rio de Janeiro in the city list — and withheld them at the catalog layer. Plus the 2026-09-17 preservation sweep (3 live hosts, 137/168 URLs) |
| `3d-origin-story.md` | Author's 3D history: the 2011 iZ3D license gift (Vadim Asadov) → the SEI campaign; the hologram line that seeded Knowledge3D |
| `rossmann-outreach.md` | Outreach draft to Louis Rossmann |
| `partner-review.md` | 3-partner senior review of the roadmap (2026-09-13) |
| `research/` | Live recon, protocols, CVE notes, kernel survey |
| `research/liverecon/` | Wire captures + analysis from the live sets |
| `tools/serviio/` | Serviio profiles, 3D fix, forum posts, app |
| `tools/serviio/tv-mediabrowser/README.md` | The media app deep-doc |
| `tools/systemd/README.md` | Deploy + service-migration procedure |
| `wiki/` | repair.wiki page drafts (public versions) |

*Status doc written 2026-09-15. Keep it current: when a lane
changes state, update this file in the same commit.*