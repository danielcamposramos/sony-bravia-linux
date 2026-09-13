# Senior-partner review: AZ3F/AZ2-F BRAVIA roadmap

**Bottom line:**
- **Stage 2 is the weak point.** As written, it most likely ends in a headless MIPS box that's worse than a $15 single-board computer.
- **The decoder assumption is your weakest.** Nothing in the repo supports the idea that the GPL sources document the decoder.
- **You already have a decoder API.** The quickest path to VLC-class playback is a network interface the TV already exposes.
- **Rooting is still worth it**, but for different reasons than the roadmap gives.

## 1. Roadmap critique

1. **Add a "Stage −1" inventory gate before anything else.** The first root shell should answer:
   - `lsmod`: are the decoder, display, PEM and tuner drivers binary `.ko` files?
   - `/proc/cpuinfo`: core type, whether there's an FPU, whether it has DSP extensions.
   - `/proc/mtd`, `dmesg` (reserved video memory), and `/proc/config.gz` if it exists.
   - Then take a full flash dump including OOB and store it off the TV.

   Write the go/no-go rules for Stages 1 and 2 against these answers now.
2. **Stage 2 is probably a dead end.** TV vendors of that era shipped the video path as proprietary modules built for one exact kernel. On 3.x/4.x you lose the panel/PEM path, the demux and the decoder, so the TV shows no picture.
   - The benefits you list (newer ath9k_htc, filesystems, buildroot) mostly come from an older compat-wireless/backports release built against the stock 2.6.35, plus your Stage 0 userland.
   - Rename Stage 2 to "backports on the stock kernel". Keep a real forward-port only if the Stage −1 inventory shows the AV drivers are GPL.
3. **Stage 1 is not as brick-proof as it claims.**
   - **Module CRCs:** if `CONFIG_MODVERSIONS` is on, Sony's binary modules won't load unless your build reproduces the exact symbol CRCs. The pass test should be "stock `.ko` files load and the panel shows a picture", not "it boots".
   - **Flash writes:** a TFTP-booted kernel still attaches the flash, and UBI attach and JFFS2 mount both write to it. A wrong partition map corrupts real partitions. Put the rootfs on USB or NFS and keep the flash read-only or unattached.
   - **Watchdogs:** the manual lists four watchdog classes, including HOST_WDT, plus a `BINT/PEM_WDT` line on the panel cable. A kernel that doesn't feed the watchdog gives you reset loops that look like crashes.
   - **Fallback:** Stage 1 assumes a boot monitor with TFTP exists. Write down the plan if it doesn't (EJTAG, or reading the flash chip off a donor board).
4. **Stage 0 risks:**
   - Check for an FPU or kernel FPU emulation before shipping hard-float binaries. Static musl or uClibc-ng with soft-float is safer. If you use glibc, stay below 2.26, which needs kernel 3.2.
   - RAM is the real ceiling. Killing Sony's main app to free memory will probably trip a watchdog or blank the panel.
5. **Do hands-on work on a donor main board or the EX725, not the HX855.** The HX855 is your workstation's monitor. Used main boards are cheap and make destructive experiments routine.
6. **Drop the keyring goal in B3.** With root you already have the rootfs, so decrypting old update images buys little. That keyring holds PlayReady, Marlin and CI+ keys next to the update key, which is close to your own DRM line. Decide now never to extract or publish those, and redact per-device keys from any dump you share.

## 2. UART and root acquisition

1. **Probe the connectors before hunting pads.** I checked your service manual:
   - The 40-pin BAP–H harness carries `RF Rx` (pin 14), `RF Tx` (pin 16) and `RF UART_SEL` (pin 18), all unconnected on the far side for this model. That is very likely a muxed SoC UART on a connector; probe it at the BAP end.
   - The panel cable carries `PEM_LOG_TX/RX` (pins 45 and 50). That's the T-CON micro's log: useful as a sanity check, not a way to root.
   - The block diagram shows **TL-JIG** next to UARTA, UARTC and Reset, so the factory jig probably uses one of those.
2. **Use a logic analyzer, not a multimeter.** A $10 fx2 clone with sigrok, clipped onto every candidate line during a cold boot, finds baud rates for you. Check the idle voltage first, since 1.8 V I/O is possible. Look at UARTA first and watch UARTC too.
3. **Only then photograph the board and hunt for pads.** Look for unpopulated 4–6 pin footprints and for missing (do-not-populate) resistors on RX lines. "TX works, RX left unpopulated" is the classic production trick.
4. **UART first, but map JTAG while you're tracing.** If the core is MIPS and debug isn't fused off, EJTAG with OpenOCD is the best brick-proof RAM and flash reader you'll get. Give it a weekend with JTAGenum, not a month.
5. **Signs there's no boot monitor:**
   - The first output is a Linux banner, or a short loader line followed by the kernel within about a second.
   - Nothing reacts when you spam Space, Enter, Ctrl-C or ESC at 115200 and 38400 baud during the first two seconds.
   - The RX path is physically open.

   Also check service mode for a log or debug toggle.

## 3. HW video decoder, ranked by effort × payoff

1. **Use the decoder you already reach:** UPnP `SetAVTransportURI`, plus `sendContentUrl` on the HX855. Pair them with a LAN proxy that remuxes MKV to TS rather than transcoding. That gives HD hardware decode in days, with no root. The roadmap files this under content; it's really your decoder answer.
2. **After root, drive the same renderer from localhost.** Your own UI and HTTP server run in the chroot and the stock player does the decoding. No decoder reverse-engineering at all.
3. **Hook the middleware** with strace, ltrace and `LD_PRELOAD` for seek, subtitles and track selection. The GPL release helps here only a little, by giving exact glibc and DirectFB versions for ABI matching.
4. **Software decode** is fine for audio (mpd) and SD content. Take "720p" out of the roadmap.
5. **Reverse-engineering the kernel driver** is months of work. The GPL tarball most likely contains only board glue (memory map, IRQs, reserved regions), not the decoder driver.
   - **Test this today:** fetch the archived sibling `kernel2635.tar.gz` and grep it for decoder drivers.
   - If there's nothing, the claim that the GPL sources are on the decoder's critical path is false.

## 4. GPL lever

1. **Your legal framing is off.** The license PDF has no three-year written offer under GPLv2 §3(b), only a printed URL. "Obligated for as long as the binaries ship" isn't in the text, and firmware distribution ended on 2022-01-31. Don't build the request on a theory Sony can dismiss.
2. **To make the request actionable, include:**
   - Exact models, firmware versions (PKG2.120BRA, PKG4.027BRA), platform IDs and your serial numbers.
   - The package list quoted word for word.
   - The dead tarball URLs, with Wayback captures of the pages that linked them.
   - An explicit request for complete corresponding source, including the kernel `.config` and build scripts.

   Send it through the form and by physical letter, and keep dated records.
3. **Escalate to Software Freedom Conservancy** (compliance@sfconservancy.org). SFC enforces for BusyBox, which is on your list, and for some Linux copyright holders. Only copyright holders have standing. SFC v. Vizio's third-party-beneficiary theory is relevant; check where that case stands now. Go public via FULU or Rossmann only after a documented non-response.
4. **Better odds than any letter:** run a Wayback CDX prefix query on `sony.net/Products/Linux/Download/*` and match tarballs by platform rather than model page. The BRA/BRB/GAA builds share platform IDs, so another region's page may link the same kernel.

## 5. Red-team findings

1. **Your service manual is the European AEP/UK/IT variant.** The "[C:SM]" tuner chain lists a satellite demod and LNB driver, which a Brazilian ISDB-Tb set wouldn't have. Board details and pad locations may not match your unit.
2. **"mipsel confirmed by the user agent" is wrong.** The user agent says `Linux mips`, which says nothing about byte order. Little-endian is likely but unconfirmed until you see an ELF header.
3. **The zip CRC-32 values are computed over the encrypted data**, so they're useless as a key-guess check. With CBC/CTR-class encryption, the "differential corpus" has almost no cryptanalytic value either.
4. **Several claims have no evidence behind them:**
   - "24Kc-class single core": nothing in the repo supports it.
   - Atreyu = CXD4727GB: "X-Reality Processor" is a picture-engine brand and could be a separate chip.
   - "Four UARTs": the diagram shows UARTA, UARTC, UARTD and a PEM log line. UARTB is missing, and may be the RF UART above.
5. **"No step in Track B modifies the TVs"** stops being true once you open a mains-powered set and ground-reference a USB adapter to it.
