# Feasibility roadmap

Goal, in the owner's words: port software like VLC to the TVs, unlock more
internet content, and **update the kernel and userspace to newer versions —
not current, but newer than 2011–2012**. This document is the honest ladder
from zero to that goal, ordered by (risk × payoff).

**Owner constraint (2026-09-13): the TVs will NOT be opened** — both are
heavy and hard to open, and the owner is not comfortable doing so. All
hardware work is therefore last-resort, and board documentation must come
from *external* sources (parts-dealer photos of the same boards, other
people's teardowns) rather than opening our own sets. Priority order:
network/software avenues first (Track A, Track B-alt, LAN probing),
published-documentation research second, opening a set only if everything
else is exhausted AND on a donor board, not these two.

## Track A — zero-mod content paths (works today, no root needed)

| Step | What | Status |
|---|---|---|
| A1 | DLNA transcoding server (Serviio/UMS/Jellyfin) on the LAN with Sony 2011/2012 BRAVIA profiles: MP4/H.264 ≤ L4.1, MPEG2-TS ≤ ~20–25 Mbps + AC3, WMV/VC-1; MKV → transcode. The owner already runs Serviio 2.5 at 192.168.0.3 | available now |
| A2 | xupnpd-style IPTV-over-DLNA bridge → live internet streams appear as a DLNA channel list on the stock player | proven pattern in the SamyGO community |
| A3 | **IRCC remote control from scripts — no registration needed** (live-proven 2026-09-13: `POST /IRCC` X_SendIRCC accepts arbitrary keypresses unauthenticated on both TVs; `/cers/command/MuteOn/MuteOff` URL commands also ungated). **Registration DONE on the EX725 2026-09-13**: the TV's own authoritative 85-command table is captured (`liverecon/cers_remoteCommandList_KDL-46EX725.xml`) and merged into the driver (90 named codes; colors = dev 0x97 on this gen, 0x9c is Android-gen). Live negative: **service-mode entry cannot be armed over LAN IRCC** — physical remote required (standby arming ignores network keys), so the LAN path also cannot write service NVM. See `docs/research/liverecon/service-mode-ex725-session.md` | control path proven; registration done |
| A4 | HbbTV 1.1.1 apps: any HTTP page the stock Opera engine can render; also the (unexplored) Nimue-issue-#4 class of port-80 attack surface | research only |
| A5 | **Ginga broadcast-chain content** (and code-execution candidate): locally-authored NCL/Lua app → OpenCaster ISDB-Tb → DSM-CC carousel → low-cost modulator → **coax injection** into the EX725 antenna input (standard Ginga developer methodology, no RF emission, no opening). Same gear unlocks HbbTV AIT injection into the Opera engine |
| A6 | **Web remote / second-screen served from the rd1 portal** &mdash; a phone-friendly LAN page that drives playback and browses the library, reaching the set via the proven A3 IRCC path. Reimplements what Sony's discontinued **Video & TV SideView** companion did (TV-programme/video functions ended 24 May 2017, Sony notice S1Q2517). Pairs with the Phase-2 console lane | designed, not built | research done; build the chain |

Track A makes the TVs genuinely more useful this week and every step is
reversible. It is also the fallback if the hardware tracks stall.

## Track B — getting in (root without breaking anything)

**Hands-on rules (from partner review):** experiment on the EX725 or a
cheap donor main board, never the HX855 (it is the workstation's monitor);
treat opening a mains-powered set as the real risk step it is (ground
reference, isolation); photograph the board before probing.

| Step | What | Depends on |
|---|---|---|
| B0 | **Inventory ("Stage −1") on first root access**: `lsmod` (are decoder/display/tuner drivers binary `.ko`?), `/proc/cpuinfo` (core, FPU), `/proc/mtd`, `dmesg` reserved-memory, `/proc/config.gz` if present. These answers set the Stage 2 go/no-go. | any root |
| B1 | **UART hunt** — now possible without opening our sets: **donor boards are for sale** (exact HX855 board 1-885-388-52, tested, R$329.90 at GTVShop; EX725 BATV boards 1-884-915-11 / 1-883-753-72 in stock ~R$154–180), and photos of both exact boards exist online (tel-spb.ru, Shopify sellers ~2048px — URLs in `docs/research/noninvasive-avenues.md`). On the bench unit: (a) probe the BAP end of the BAP–H harness `RF Rx`/`RF Tx`/`RF_UART_SEL` (pins 14/16/18) — likely the muxed missing UART; (b) logic-analyzer boot capture on candidates (sigrok + fx2 clone; 115200/57600/38400/9600; check idle voltage — 1.8 V possible); (c) match the SM's connector pin tables to silkscreen designators (CN8001 pins 42/44/45/50 = PEM UARTs); (d) TL-JIG jig connector as likely debug breakout. UARTA first, UARTC next, JTAG only as fallback. | donor board purchase (owner decision) |
| B2 | Capture boot log; determine whether an ABK-Monitor-class boot monitor exists on AZ3F (banner before kernel messages; try Space/Enter/Ctrl-C in the first 2 s). If yes: memory dump → **full NAND flash dump incl. OOB (the first thing to save)** → root console. **This is the "unbrickable" gate** — until confirmed, no custom-kernel boot without touching flash. | B1 |
| B3 | With root: rootfs RE for the middleware player API (decoder path, see Track C). Keyring extraction **dropped by decision** — the keyring sits next to PlayReady/Marlin/CI+ keys; we will not extract or publish those, and per-device keys are redacted from any shared dump. | B2 |
| B4 | Test `unixtract` (Rust, MTK PKG formats) against our `sony_dtv0FA1/0FA2` bins — one cheap experiment, likely negative | nothing (can run today) |
| B5 | Sony OSS inquiry form → request the exact 2.6.35-era kernel tarballs for both model groups (GPL obligation; add evidence: the archived "common" kernel2635.tar.gz has NO board/SoC/decoder files → arguably incomplete corresponding source, and the binary `.ko` AV modules are absent too). Parallel: archived sibling tarball already surveyed (`docs/research/kernel2635-survey.md`) | nothing (can run today) |
| B6 | **EX725 port 9784 — ANSWERED (2026-09-13 live session)**: accept-then-close stub; the handler exits without ever reading a byte (idle → FIN in 10 ms; data → ACK then RST; identical during active playback). Callisto hypothesis unrefuted but untestable from the wire. Remaining: post-root `ps`/`netstat` identification, or a used DMX-NV1 (~USD 20) as ground truth. De-prioritized. | any root |
| B7 | ~~Download the AZ2-F service manuals~~ **DONE (2026-09-13)**: all four SMs + the chassis-level AZ2-F schematic (incl. BATV board schematics) in `manuals/KDL-46EX725/` | — |
| B8 | **UDP 7776 beacon (EX725-only, NEW discovery 2026-09-13)**: high-entropy 6–15-byte broadcast every 1.25 s since boot; socket bound but silent to probes; publicly undocumented (one forum anecdote). Next: longer captures, correlate with CERS registration, post-root process identification (`netstat -ulnp`). New Track B-alt audit surface on the 2011 generation. | nothing (passive) |

### Track B-alt — the exploit chain (no soldering; owner's addition)

Leverage the era's known flaws as an alternate entry:

1. **Foothold**: memory-safety bug in reachable 2011-era userspace —
   ranked audit targets (2026-09-13 update, evidence in
   `docs/research/noninvasive-avenues.md`):
   - **CVE-2011-2628 / Exploit-DB 17936** — **studied in depth
     2026-09-13, see `docs/research/presto-cve-2011-2628.md`** (workflow
     wf_12f70c4e-2c1, adversarially verified). Trigger is pure content
     (badly nested XHTML frameset/iframe + 333em CSS at page unload);
     band = all desktop Opera 10.00–11.10, fixed only in desktop 11.11 —
     the Devices/mobile line NEVER got the fix, and our Presto 2.7.61 is
     an SDK build of the 2.7 core (desktop 11.00 "Kjevik" generation;
     corrected mapping: Presto 2.7.62 = Opera 11.00/11.01, 11.10/11.11
     ran 2.8.131), so strong-inference vulnerable, unproven on SDK
     builds. MIPS retarget required: `0x0c0c0c0c` decodes as `jal` on
     MIPS and the deterministic no-ASLR mmap base is **0x2aaa8000**
     (TASK_SIZE/3, bottom-up); no NX on this kernel (no ROP needed) but
     I/D caches need a `cacheflush` (syscall 4147) stub; spray budget is
     tens of MB on 512 MB RAM. **Delivery SOLVED 2026-09-13 (evening):
     lane #1 is now the built-in "Navegador da Internet" browser + CERS
     sendText + plain-HTTP LAN server — LIVE-PROVEN end-to-end with JS
     execution (`liverecon/browser-lane-test.md`); the live UA
     self-declares Presto/2.7.61, no HbbTV token.** The HbbTV-over-coax
     lane was killed the same day by a five-model partner review
     (`research/partner-review-presto-kimi.md` + `-panel.md`): ISDB-Tb
     firmware parses ARIB/Ginga signalling, not DVB AIT; zero dollars to
     that lane (any future RF gear targets Ginga/NCL-Lua, the CPqD root
     precedent). Panel-hardened ladder (replace the old one): positive-
     control crash page to calibrate the oracle (HOST_WDT counts system
     hangs, not process deaths; add ARP-ping loss + JS phase beacons as
     real-time signals) → unmodified-trigger falsifier run served as
     `application/xhtml+xml`, ≥3 unload mechanisms, quiescent windows,
     WAN quarantine → measured spray ladder (Presto's own heap arenas
     dominate the geometry — landing address from a /proc/self/maps
     beacon, never from 0x2aaa8000+n arithmetic; no flash writes) →
     UDP-beacon canary. Server-side hedges stockpiled: 2012-6468/3561
     fire from any fetch we control, no URL-entry UI needed. JS in the
     browser is gated by Opera's standard "insecure code" accept prompt
     — fold the accept into the run procedure or find the settings
     toggle. https URLs are refused on-screen ("outdated keys"-class
     local error) — plain-HTTP LAN is the working transport (NOTE: the
     earlier "zero egress" packet claim was withdrawn 2026-09-13: our
     tcpdump vantage is blind to TV→WAN unicast on this switched LAN —
     proven during the internet-content OTA capture, FINDINGS obs. 6;
     TV WAN capture needs a gateway or ARP-MITM vantage). Post-freeze
     Presto CVEs 2012-3561/6465/6468/6470 and 2013-1637/1638 are
     band-plausible but introduction-unknown; 2012-1003 definitively
     excluded (typed arrays did not exist before Presto 2.10).
     Crash-oracle rig: 8-blink Software Error state / service-mode error
     history, **EX725 only — never the HX855 monitor**. Baseline captured
     2026-09-13 (read-only service session,
     `liverecon/service-mode-ex725-session.md`): SELF CHECK shows
     **HOST_WDT=21** lifetime watchdog trips on a healthy, heavily-used
     set (25758 panel h, 11498 boots) — watchdog resets accumulate
     recoverably, so probe trips just increment a counter; `103 HOST_WDT`
     and the boot count are the rig's before/after tripwires. Note:
     reading them needs the physical remote (service screens can't be
     entered over LAN), and the 8-blink LED state is observable without
     entering anything.
   - **X_SendIRCC dispatch** (port 80) — unauthenticated (live-proven),
     hand-rolled, proven-sloppy dispatch (mis-routes X_GetStatus to the
     IRCC path; garbage base64 silently 200s), TWO independent
     implementations across our TVs to diff-audit.
   - **AVTransport `SetAVTransportURI` URI parser** (52323, unauthenticated
     by DLNA design) — long attacker-controlled strings into the 2011-era
     URI parser feeding the HW player.
   - **UPnP SUBSCRIBE CALLBACK-URL parser** (CallStranger class) on
     `/upnp/event/*`.
   - **libmicrohttpd 0.4.6** (2008-era, in the GPL package list, never
     audited) if it fronts CERS — confirm after root.
   - **CERS `sendContentUrl`** URL handling (HX855, registration-gated)
     — test scheme acceptance (https, file://, oversized). (No longer
     framed as the HTML delivery path: the EX725 browser + `sendText`
     lane is live-proven, and it may exist on the HX855 too — same
     Home-menu browser family per the manuals.)
   - Delivery into the engines without registration: IRCC keypresses
     are unauthenticated (drive the browser + URL-entry UI the way we
     did on the EX725; `sendText` itself is registration-gated);
     EX725's proven chain documented in `liverecon/browser-lane-test.md`.
2. **Privesc**: a stock 2.6.35 kernel falls to a decade of public LPEs
   (Dirty COW and the whole 2010+ set) from any local code execution.
3. **Caveats**: Sony's PKG updates may have patched some of this
   (patch-diffing our multiple same-platform builds, if decryption ever
   happens, would show exactly which); the attack surface may be thinner
   than it looks (custom minimal handlers, not full servers). Crash risk
   is watchdog resets, generally recoverable. **Guardian is known now**
   (`drivers/mod_guardian/guardian.c` — see
   `docs/research/kernel2635-survey.md`): the stock LSM only blocks
   `mount -o remount,rw` of the rootfs; it does NOT block USB mounts,
   `pivot_root`, `chroot`, or module loading — so the entire Stage-0
   userland plan works with guardian active, and root additionally gets
   `rmmod guardian` as an option.
4. **Scope**: our own sets on our own LAN. Findings stay in this repo.

No step in Track B (main) modifies the TVs' flash. Read-only observation
of hardware we own; the caveat about powering/opening the set applies from
B1 onward.

## Track C — modernization ladder (the "newer than 2012" goal)

**Gate — "Stage −1" inventory (B0)**: from the first root shell, `lsmod`
and friends decide everything below. If the AV (decoder/panel/tuner)
drivers are binary `.ko` modules — the era-typical case — there is no
forward-port to 3.x that keeps a picture; the ladder then ends at
"backports on the stock kernel".

**Stage 1 — toolchain + bootable custom kernel + initramfs (the new
first step).** Build a mipsel toolchain (crosstool-ng/Buildroot; static
musl/uClibc-ng soft-float userland, or glibc ≤ 2.26 since 2.26 needs
kernel 3.2; QEMU user-mode test everything before touching hardware).
Then build the *exact* stock kernel from GPL sources and TFTP-boot it via
the ABK path. The exact source is already on disk: the archived
`kernel2635.tar.gz` is **Linux 2.6.35.14** — BUT it is a "common"
release with no board/SoC platform files (see
`docs/research/kernel2635-survey.md`); whether a bootable kernel can be
assembled from it + on-device module extraction is a Stage-1 experiment,
and the gap is itself GPL-compliance evidence for the B5 packet. Brick risks to manage: `CONFIG_MODVERSIONS` symbol CRCs
(pass test = "stock `.ko` modules load AND the panel shows a picture", not
"it boots"); keep internal flash unmounted or read-only (UBI/JFFS2 mounts
**write**) — rootfs on USB/NFS; feed the watchdogs (HOST_WDT, PEM_WDT) or
get reset loops that look like crashes. Until the ABK/TFTP gate (B2) is
confirmed, custom-kernel experiments write flash and are NOT unbrickable.

**Stage 0 — pivot the modern userland into the initramfs (the new second
step).** The modern userland is built *for the custom initramfs*, then
used from whatever shell root yields. Risk wording: "no risk to internal
flash" — a wedged userland can still hang the running system, and RAM is
the real ceiling (killing Sony's main app risks watchdog trips).

**Stage 2 — backports on the stock kernel (default), forward-port only if
the inventory allows.** Default plan: compat-wireless/backports for newer
ath9k_htc on the stock 2.6.35 + the Stage 0 userland gives most of the
"newer" value. A true forward-port (DuckBox-style, to a 3.10/3.14-class
LTS) only proceeds if the GPL sources show the AV drivers are
source-available — expect headless-first (network/USB), panel/tuner last,
and treat it as a multi-year research track, not a linear step.

**The decoder — reframed (partner consensus).** The stock renderer is
already a decoder API:
1. **No root needed**: UPnP `SetAVTransportURI` + (HX855) CERS
   `sendContentUrl` driven by a LAN **remux** proxy (MKV → TS container,
   no transcode, no quality loss) → HD hardware decode in days.
2. **After root**: drive the same renderer from localhost (our own UI +
   HTTP server in the chroot; the stock player decodes).
3. **Middleware hooking** (LD_PRELOAD / strace / ltrace into the player,
   SamyGO exeDSP-style) for seek/subtitles/tracks. GPL sources help here
   mainly by pinning exact glibc/DirectFB versions for ABI matching.
4. **Kernel-driver RE of the decoder**: **answered 2026-09-13 — the GPL
   tarball contains no SoC/decoder/panel drivers at all** (see
   `docs/research/kernel2635-survey.md`): the AV path ships as binary
   `.ko` modules outside the release. This option is last resort /
   likely impossible from GPL sources alone.
5. **Software decode**: audio (mpd) and SD content only; "720p" removed —
   not realistic on this core class.

## Milestones worth sharing externally

1. Platform map complete (this repo, now) → repair.wiki page for the
   AZ3F/AZ2-F chassis (board-level debug: service mode, blink codes,
   UART names, module firmware versions).
2. GPL source recovery (B5) → the Rossmann/fulu "manufacturer deleted the
   downloads" story with a concrete outcome.
3. First TFTP-booted custom kernel (Stage 1) → Repair Bounty Program
   material.
4. Working VLC/mplayer with HW decode (Track C endgame) → the headline.

## What we will NOT do

- No DRM circumvention for protected media (PlayReady/WMDRM in the license
  list is out of scope — we build players, not pirates).
- No attacking devices we don't own; everything here targets our two sets.
- No destructive flashing until TFTP/UART boot is proven (Stage 1 first).