# Feasibility roadmap

Goal, in the owner's words: port software like VLC to the TVs, unlock more
internet content, and **update the kernel and userspace to newer versions —
not current, but newer than 2011–2012**. This document is the honest ladder
from zero to that goal, ordered by (risk × payoff).

## Track A — zero-mod content paths (works today, no root needed)

| Step | What | Status |
|---|---|---|
| A1 | DLNA transcoding server (Serviio/UMS/Jellyfin) on the LAN with Sony 2011/2012 BRAVIA profiles: MP4/H.264 ≤ L4.1, MPEG2-TS ≤ ~20–25 Mbps + AC3, WMV/VC-1; MKV → transcode. The owner already runs Serviio 2.5 at 192.168.0.3 | available now |
| A2 | xupnpd-style IPTV-over-DLNA bridge → live internet streams appear as a DLNA channel list on the stock player | proven pattern in the SamyGO community |
| A3 | CERS `register` + full IRCC remote control from scripts/home automation (one-time on-screen dialog on the TV) | API already documented; dialog deliberately not yet triggered |
| A4 | HbbTV 1.1.1 apps: any HTTP page the stock Opera engine can render; also the (unexplored) Nimue-issue-#4 class of port-80 attack surface | research only |

Track A makes the TVs genuinely more useful this week and every step is
reversible. It is also the fallback if the hardware tracks stall.

## Track B — getting in (root without breaking anything)

| Step | What | Depends on |
|---|---|---|
| B1 | **Find UARTA (LOG) pads on the BAP board.** The service manual gives the signal names but no locations. Board tracing / high-res photos of our own board. 3.3 V TTL USB adapter. | hands-on session |
| B2 | Capture boot log; determine whether an ABK-Monitor-class boot monitor exists on AZ3F (precedent: LX900 CN5502). If yes: memory dump → NAND flash dump → root console | B1 |
| B3 | From a flash dump: locate the named keyring (commonkey, kkey, frzkey…) and the update-decryption path; optionally decrypt our six-image corpus (CRC-32 oracles available) | B2 |
| B4 | Test `unixtract` (Rust, MTK PKG formats) against our `sony_dtv0FA1/0FA2` bins — one cheap experiment, likely negative | nothing (can run today) |
| B5 | Sony OSS inquiry form → request the exact 2.6.35-era kernel tarballs for both model groups (GPL obligation). Parallel: pull the archived sibling `kernel2635.tar.gz` (92 MB) from Wayback | nothing (can run today) |
| B6 | Probe EX725 port 9784 (unknown tcpwrapped service) | nothing |

No step in Track B modifies the TVs. Everything is read-only observation
of hardware we own.

## Track C — modernization ladder (the "newer than 2012" goal)

**Stage 0 — newer userspace on the stock kernel (no risk to the TV).**
Build a mipsel toolchain and a self-contained modern-ish userland
(glibc ~2.17-era, busybox, dropbear, mpd/ffmpeg CLI), ship it on a USB
stick, and run it via chroot/pivot from whatever shell Track B yields.
The stock 2.6.35-era kernel ABI is enough for userspace of that vintage.
This alone turns the set into a controllable Linux box.

**Stage 1 — rebuild the stock kernel from GPL sources (unbrickable).**
Once B5 delivers sources: build the *exact* stock kernel first, boot it via
the ABK/TFTP path (over UART/LAN — the internal flash is never touched), and
verify it matches. This validates the whole toolchain while the TV's own
boot remains intact: a failed experiment just means power-cycle and boot
the internal image again. This is the "training wheels" stage.

**Stage 2 — forward-port the kernel.** Port Sony's out-of-tree CXD4727GB/
Atreyu drivers (panel/PEM, tuner/demod, NAND, USB glue, ethernet) forward to
a 3.x/4.x kernel, starting from the closest mainline equivalents. Precedent:
DuckBox/STLinux communities did exactly this for other TV SoCs. Each ported
driver is one small, testable, publishable unit — ideal FULU/repair.wiki
material. Realistic target: 3.x–4.x, not 6.x; the value is newer ath9k_htc,
newer filesystem/networking, modern buildroot, and long-term maintainability,
not latest-and-greatest.

**The independent hard problem — HW video decode.** VLC-class *useful*
playback needs the Atreyu hardware decoder. No public documentation exists;
the SamyGO experience says software decode of HD on a TV-class MIPS core
does not work. Options in order of likely effort:
1. Talk to Sony's middleware player API from our own process (needs root +
   rootfs RE — Stage 0/1 deliverables).
2. Reverse the decoder's kernel driver interface from the recovered GPL
   sources and reuse the DSP firmware blobs from the flash dump.
3. Accept SW decode for SD/720p content only, use DLNA/HW player for HD.

A newer kernel does NOT unlock the decoder — but the GPL sources are the
only place the driver interface is written down, which is why B5 is on the
critical path for both Stage 1 and the decoder.

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