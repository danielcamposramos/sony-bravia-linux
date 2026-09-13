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
| A3 | **IRCC remote control from scripts — no registration needed** (live-proven 2026-09-13: `POST /IRCC` X_SendIRCC accepts arbitrary keypresses unauthenticated on both TVs; `/cers/command/MuteOn/MuteOff` URL commands also ungated). A registration (one-time on-screen dialog, EX725 first) only adds the full `getRemoteCommandList` code table + `getText/sendText`. See `docs/research/noninvasive-avenues.md` | control path proven; deliberate `register` still pending user OK |
| A4 | HbbTV 1.1.1 apps: any HTTP page the stock Opera engine can render; also the (unexplored) Nimue-issue-#4 class of port-80 attack surface | research only |
| A5 | **Ginga broadcast-chain content** (and code-execution candidate): locally-authored NCL/Lua app → OpenCaster ISDB-Tb → DSM-CC carousel → low-cost modulator → **coax injection** into the EX725 antenna input (standard Ginga developer methodology, no RF emission, no opening). Same gear unlocks HbbTV AIT injection into the Opera engine | research done; build the chain |

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
| B1 | **UART hunt**: (a) probe the BAP end of the BAP–H harness `RF Rx`/`RF Tx`/`RF_UART_SEL` (pins 14/16/18) — likely the muxed missing UART; (b) logic-analyzer boot capture on candidates (sigrok + fx2 clone; 115200/57600/38400/9600; check idle voltage — 1.8 V possible); (c) high-res board photos, unpopulated footprints, do-not-populate resistors on RX lines; (d) TL-JIG jig connector as likely debug breakout. UARTA first, UARTC next, JTAG (JTAGenum/OpenOCD+EJTAG) only as fallback. | hands-on session |
| B2 | Capture boot log; determine whether an ABK-Monitor-class boot monitor exists on AZ3F (banner before kernel messages; try Space/Enter/Ctrl-C in the first 2 s). If yes: memory dump → **full NAND flash dump incl. OOB (the first thing to save)** → root console. **This is the "unbrickable" gate** — until confirmed, no custom-kernel boot without touching flash. | B1 |
| B3 | With root: rootfs RE for the middleware player API (decoder path, see Track C). Keyring extraction **dropped by decision** — the keyring sits next to PlayReady/Marlin/CI+ keys; we will not extract or publish those, and per-device keys are redacted from any shared dump. | B2 |
| B4 | Test `unixtract` (Rust, MTK PKG formats) against our `sony_dtv0FA1/0FA2` bins — one cheap experiment, likely negative | nothing (can run today) |
| B5 | Sony OSS inquiry form → request the exact 2.6.35-era kernel tarballs for both model groups (GPL obligation; add evidence: the archived "common" kernel2635.tar.gz has NO board/SoC/decoder files → arguably incomplete corresponding source, and the binary `.ko` AV modules are absent too). Parallel: archived sibling tarball already surveyed (`docs/research/kernel2635-survey.md`) | nothing (can run today) |
| B6 | **Probe EX725 port 9784** — now evidence-backed hypothesis: Sony "Callisto Debug Server" renderer-push family (DMX-NV1 2007–2008 precedent: unauthenticated HTTP `renderer.php?method=play&url=…`; EX725 = CERS gen 1.0 keeps 9784 open, HX855 gen 1.1 moved the function into CERS `sendContentUrl` and closed 9784). Safe probe ladder in `docs/research/noninvasive-avenues.md`: idle-timeout, half-close, DMX-era HTTP probes, probe-during-playback, **passive tcpdump during boot/CERS use**. Single-port, spaced ≥5 s, EX725 only | nothing |
| B7 | Download the AZ2-F service manuals (Elektrotanya, 4 PDFs incl. a KDL-46EX725-specific SM) → BATV board connector views/parts lists without opening anything | nothing (can run today) |

### Track B-alt — the exploit chain (no soldering; owner's addition)

Leverage the era's known flaws as an alternate entry:

1. **Foothold**: memory-safety bug in reachable 2011-era userspace —
   ranked audit targets (2026-09-13 update, evidence in
   `docs/research/noninvasive-avenues.md`):
   - **CVE-2011-2628 / Exploit-DB 17936** — public Opera Presto RCE PoC
     hitting the EX725's Presto 2.7.61 band exactly (heap spray at
     0x0c0c0c0c; no-ASLR MIPS era favorable), plus post-freeze Presto
     CVEs (2012-3561, 2012-6468/6465/6470, 2012-1003, 2013-1637/1638).
     Crash-oracle rig: 8-blink Software Error state / service-mode error
     history, **EX725 only — never the HX855 monitor**.
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
   - **CERS `sendContentUrl`** URL handling (HX855, registration-gated) —
     also the only network path to render our own HTML in the Opera
     engine; test scheme acceptance (https, file://, oversized).
   - Delivery into the engines without registration: HX855 via
     `sendContentUrl` after one deliberate register; EX725 via DLNA
     push + the broadcast chain (Ginga NCL/Lua app or HbbTV AIT
     injection through coax — see Track A5).
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