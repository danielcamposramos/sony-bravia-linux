# Web research digest — 2026-09-13 (discovery workflow)

Condensed findings from the discovery research run, with sources. Confidence
notes as reported by the research agents.

## Firmware packages (attribution CONFIRMED)

- `sony_tvupdate_2012_2120_bra_auth.zip` = **PKG2.120BRA**, final firmware for
  the **KDL-46HX855** (and the whole HX75x/85x/95x + EX55x/65x 2012 Brazil
  family). Released 2014-12-09. Build `00001400`, platform `0FA20A02A0A2`,
  bin suffix `0689006e`. Sources: archived Sony Brazil page W0010136
  (web.archive.org/web/20190722093807/…kdl-55hx855/downloads/W0010136);
  Sony termination article 00269731.
- `sony_tvupdate_2011_4027_bra_auth.zip` = **PKG4.027BRA**, final firmware for
  the **KDL-46EX725** (EX72x family; also CX52x/EX52x/EX42x/HX82x/NX72x).
  Released 2014-12-12. Build `00000400`, platform `0FA10A01A0A1`, bin suffix
  `07e8046a`. Was misfiled in the HX855 folder — different platforms,
  incompatible. Sources: archived Sony Brazil page W0010147; EletrônicaBR
  file 41945.
- Both are the LAST versions ever; Sony terminated update distribution
  2022-01-31 (Brazil/LatAm notices). PKG2.120 added TLS 1.0 / SSL3
  reliability; PKG4.027 same, earlier versions added Skype/Twitter/Facebook,
  WMV/WMA for DLNA/USB, 3D via USB.
- Naming: `sony_tvupdate_<year>_<PKG version w/o dot>_<region>_auth.zip`
  (auth = USB manual-update package). The `sony_dtv<platform>_<build>` folder
  and `<build>_<platform ID>.bin` names confirmed by Sony's own instruction
  pages. The 8-hex bin suffix is constant per platform across regions — it is
  NOT a content hash (AAA build 00000301 vs BRA build 00000400 share
  `07e8046a` but zero identical 16-byte blocks).

## Firmware container (cryptanalysis facts)

- Whole-file encryption, byte 0 → EOF: flat 7.9998-bit entropy (1 MiB
  windows), zero duplicate 16-byte blocks (5.94M / 4.27M unique) → CBC/CTR or
  whitening, NOT ECB; no plaintext magics anywhere (aligned or not); binwalk
  only chance-level false positives; incompressible (zip stored at 0% ratio).
- Sizes: 95,079,200 (2012 BRA) and 68,295,040 (2011 BRA) — multiples of 16
  but not of 512 (remainders 288/384) → container sections/header layout not
  512-aligned; structure unknowable before decryption.
- No public decryptor exists for this generation. SamyGO thread
  "Decrypting Bravia Firmware BIN File" (forum.samygo.tv t=2430, 2011+)
  analyzed an LX900 (EMMA3TH MIPS) image: update bin encrypted, but on-device
  flash contains a PLAINTEXT "ABK Monitor" boot monitor (Copyright
  1999–2009 Sony, Aperios platform, /ms/mssony/abk paths) with a rich shell:
  memory dump/modify, MIPS assembler/disassembler, and **boot via
  -tftp/-serial/-elf/-srecord**, TFTP put/get. Flash also holds a NAMED
  keyring (commonkey, kkey, dlnakey, podkey, marlinkey, cipluskey, frzkey,
  `locked_by_rng`, …) — key VALUES never published.
- Community conclusion: bypass decryption via the UART debug console
  (EMMA3TH UART0/UART1 "DTT Log"/"PQC Log" on connector CN5502, 3.3 V TTL,
  TV must be fully powered on). AZ2F/AZ3F equivalent connector TBD — check
  our service manual.

## Platform identity

- **HX855**: chassis AZ3F (regional variant AZ3G), board family SEGM 3A-G.
- **EX725**: chassis AZ2-F, board SEGM.3A-2 ("BATV" board).
- **SoC: Sony CXD4727GB "X-Reality Processor"** (IC9000) on both, per board
  censuses of sibling models (KDL-46EX724, KDL-40HX853, KDL-55HX753 — main
  boards 1-883-753-13 / 1-885-388-51). Confidence: medium (proxy models, not
  our exact boards — to verify against our AZ3F service manual). Supporting
  ICs: Samsung K4B2G1646C-HCH9 DDR3 (2x on AZ2F = 512 MB; 1x on AZ3F
  census), KFM OneNAND flash (KFM2GN6Q2B / KFM4G16Q4B), Silicon Image
  Sil9287B HDMI switch, GL850G USB hub, Realtek RTL8201E PHY.
- **CPU: MIPS little-endian (mipsel)** — confirmed by the TVs' own Opera user
  agents: `Opera/9.80 (Linux mips; U; InettvBrowser/2.2 (00014A;SonyDTV115…)
  KDL46HX855… Presto/2.10.250` and `…HbbTV/1.1.1 (; Sony; KDL40EX725; PKG4.021EUA…) Presto/2.7.61`.
  Confidence: high.
- **Kernel: Linux 2.6.x** — live `Server: Linux/2.6 UPnP/1.0` headers on
  both; likely 2.6.35 or close (sibling 2012 GPL group ships
  linux-2.6.35.tar.gz; archived kernel2635.tar.gz exists). Exact version for
  our groups unconfirmed (GPL tarballs deleted, never archived).
- **Userspace (from Sony's own archived GPL pages for our exact groups)**:
  glibc 2.7 (NOT uClibc), busybox 1.4.2, DirectFB 1.3.0 + SaWMan (no X11),
  cairo 1.8.6, pango 1.24.2, glib 2.22.5, JavaScriptCore/WebCore, alsa-lib
  1.0.19, uvcvideo r104, fuse 2.7.4, iptables 1.4.0, libmicrohttpd 0.4.6,
  dosfstools, Qt 4.7.0, cross-GCC 4.1.2.
- **Browser/HbbTV**: Opera Devices "InettvBrowser/2.2", HbbTV 1.1.1;
  device token SonyDTV115 (2011-2012 generation).
- **WiFi**: HX855 built-in DWM-W046 (Mitsumi; Atheros AR9271, USB-attached,
  2.4 GHz 1x1, ath9k_htc); EX725 "Wireless LAN Ready" via UWA-BR100 dongle
  (AR7010+AR9280, also ath9k_htc). Everything is USB-attached Atheros.
- Marvell ARM toolchains found in Sony's TV OSS tree are red herrings for
  other product lines; BX low-end models used MediaTek ARM. The KDL mid/high
  range 2011-2012 is the in-house CXD47xx MIPS line.

## GPL sources (the legal lever)

- Sony's Source Code Distribution Service: now
  https://oss.sony.net/Products/Linux/ (TV category with regional pages).
  Historically www.sony.net/Products/Linux — our models' pages are archived
  (packages lists intact) but the tarballs are gone (404, not Wayback'd).
  - EX725 group page: "KDL-32CX520.html" (Wayback 2014-01-25/2014-02-26) —
    kernel tarball URL `Download/common/zBiusZMzHFG8SB4KDXDP3A/linux-kernel.tgz` (dead).
  - HX855 group page: "KDL-46HX750.html" (Wayback 2012-08-31) —
    `Download/common/qNe4FQvq2i_B0gV8BTteCw/linux-kernel.tgz` (dead).
- Archived downloads that DO exist on Wayback: kernel2635.tar.gz (92 MB,
  2.6.35 tree, capture 2013-08-26), kernel26.tgz (49 MB, 2.6-era MIPS),
  kernel2623-5.7.3.src.tgz, glibc-2.7, ffmpeg_20120709, gstreamer-0.10.22,
  directfb, wireless_tools.
- Request route: OSS inquiry form
  https://sonygroup.my.salesforce-sites.com/sony/OSS_Inquiry1?lang=en
  (linked from every live model page). Sony is GPL-obligated for as long as
  the binaries ship — worth a formal request for both groups.
- No GitHub mirror of the 2.6-era BRAVIA kernel exists (only 2015 KD-43X8301C
  mirrors: Bleeblun/Sony-Bravia-TV).

## Known hacks / exploit landscape

- **Nimue** (CFSworks, June 2012) — the ONLY public root exploit for
  pre-Android BRAVIA Linux: overflow in hidden Gemstar TVGOS service on TCP
  12345 (password 'gemstar'), uploads MIPS busybox, spawns root telnet;
  author booted Debian from USB. DOES NOT affect our sets: community reports
  list KDL-40EX725 as port-closed/not working; Sony force-patched via
  aa0206pf. https://github.com/CFSworks/nimue
- Nimue issue #4 (2013) asked about Opera-era sets with port 80 (ours) —
  never answered. Unexplored territory.
- No SamyGo-equivalent community for Sony; no CVEs for the 2011-2012
  HbbTV/Opera engines (the known Bravia CVEs are all 2015+ Android-era).
- HbbTV/broadcast injection (30C3 2013 Herfurt; Scheel 2017 root via DVB-T;
  DEF CON 27) works on this generation's architecture in principle — the
  HX855 has a DVB tuner — but requires an SDR/ATSC-DVB transmitter; Brazil
  uses ISDB-Tb (SBTVD), so the angle would be ISDB-Tb HbbTV injection. No
  published research for ISDB-Tb.
- Service mode (Display→5→Vol+→Power from standby): diagnostics/hotel mode
  only, no known code-execution path.
- **unixtract** (github.com/theubusu/unixtract, Rust): supports "MediaTek PKG
  (Old/New)" formats for other Sony-era TVs with bundled keys — NOT confirmed
  applicable to our sony_dtv 0FA1/0FA2 packages (likely NEC/Sony silicon, not
  MTK). Worth one test run. Also theubusu's sony_pkg.py gist documents the
  newer sony_dtv PKG header layout (magic 0x0010, 48-byte fw name, section
  sizes, SHA-1 footer) — our bins have NO such header (encrypted earlier in
  the pipeline or different generation).

## VLC / software porting feasibility

- VLC has an fbdev video-out (no X11 needed) and builds on uClibc-ng/musl
  embedded Linux; VLC 3.0 needs kernel > 2.6.26 and GCC 4.8+ (C11). VLC 2.2.x
  safer for this platform. Buildroot keeps a `package/vlc` recipe as the best
  build base.
- SamyGo precedent (Samsung, same era, MIPS 34Kc): software decode of HD
  video on TV main CPUs FAILED (their mplayer port: no sound, slideshow);
  the community pivoted to (a) hooking the stock HW player via .so injection
  into exeDSP, and (b) DLNA/IPTV bridges (xupnpd, vusb, nfsmount) feeding
  the stock player. Only on ST SH4 sets (STLinux/STAPI/DuckBox) did full open
  media centers (Enigma2/XBMC) achieve HW-accelerated playback.
- Consequence for us: a useful VLC/mplayer port on the CXD4727GB must talk to
  the SoC's undocumented HW decoder (or the Sony middleware's player API) —
  requires root + rootfs RE first. Pure-software 1080p decode on a
  24Kc-class single MIPS core is not realistic.
- Zero-mod content paths that already work (and are proven in the
  community): Serviio/UMS/Jellyfin DLNA with Sony BRAVIA year-profiles
  (2011/2012 profiles: MP4/H.264 ≤ L4.1, MPEG2-TS ≤ ~20-25 Mbps + AC3,
  WMV9/VC-1, DivX AVI (SD), NO MKV — transcode MKV → MPEG2-TS/AVC-TS);
  xupnpd-style IPTV-over-DLNA; HbbTV 1.1.1 apps.

## Additions from the non-invasive workflow (2026-09-13, full digest in
## noninvasive-avenues.md)

- AZ2-F / KDL-46EX725 service manuals are downloadable at Elektrotanya
  (4 PDFs: dedicated `sony_kdl-46ex725_chassis_az2f_sm.pdf` 26.3 MB/160 pp;
  multi-model AZ2-F VER.2.0 SEGM.3A-2 12.2 MB; VER.1.0 10.1 MB;
  AZ2-F REV.0 LEVEL3 15.3 MB) — the missing primary sources for the BATV
  board, no opening required. Elektrotanya download pages throttle
  (one download per waiting period).
- Port 9784 on the EX725: strongest hypothesis is Sony's proprietary
  "Callisto Debug Server" renderer-push family (DMX-NV1 2007–2008,
  unauthenticated HTTP `renderer.php?method=play&url=…`; open across the
  whole 2010–2011 Linux BRAVIA generation, closed on our 2012 HX855 whose
  CERS gen 1.1 gained sendContentUrl). No protocol docs, CVE, Shodan
  banner, or Japanese-language source exists anywhere.
- CVE-2012-2210 (Exploit-DB 18705): SYN-flood watchdog DoS on
  KDL-32CX525 — the ONLY published attack against this platform
  generation; full TCP port scans crashed 2010-era sets (one report:
  1–46000 safe, 46001+ hard-crash) → never scan our TVs.
- Negative results (verified against our own manuals/SM): no RS-232 or
  external service jack on either set; TL-JIG is a bench fixture, not
  externally reachable; hotel-mode lines are internal-harness only; no
  Sony LAN service tool exists for this generation; no USB
  adjustment-data save on AZ3F.

## Recommended next steps (from research)

1. UART/console: find the ABK-monitor/debug connector on AZ2F/AZ3F boards
   (service manual + board photos). This is the documented route to keys,
   flash dump, TFTP-boot — and to root without touching encryption.
2. Formal GPL source request for both model groups (Sony OSS inquiry form) —
   also a soft pressure/awareness channel.
3. Test unixtract against our sony_dtv bins (one cheap experiment).
4. Differential analysis across the six-package corpus (same platform,
   different regions/versions) — NOTE after partner review: against
   CBC/CTR-class whole-file encryption this has little cryptanalytic
   value and no plaintext oracle exists (zip CRC-32 covers the encrypted
   bytes; the filename hex field is a platform ID, not a hash). Keep the
   corpus for *after* any decryption breakthrough: patch-diffing PKG
   builds then reveals which flaws Sony fixed.
   different regions/versions).
5. CERS register (visible dialog) → full IRCC remote control from LAN.
6. Probe 9784 protocol on the EX725 (only open port beyond CERS/UPnP).