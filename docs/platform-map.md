# Platform map — KDL-era BRAVIA Linux (AZ3F / AZ2-F)

Synthesis of: AZ3F service manual (9-888-487-03), Sony OSS license documents,
live LAN recon, and web research. Confidence markers: **[C]**onfirmed (read
from primary source or live device), **[W]**eb-researched (secondary source),
**[I]**nferred.

## 1. The machines

| | KDL-46HX855 | KDL-46EX725 |
|---|---|---|
| Year | 2012 | 2011 |
| Chassis | AZ3F ("Segment 3a-G") **[C:SM]** | AZ2-F (SEGM.3A-2 "BATV" board) **[W]** |
| Service-mode chassis name | "WYVERN" **[C:SM]** | TBD |
| Main board | BAP board ("B*" board), SoC heatsink part labeled "ATREYU" **[C:SM]** | BATV board **[W]** |
| Final firmware | PKG2.120BRA (`sony_dtv0FA20A02A0A2_00001400`) | PKG4.027BRA (`sony_dtv0FA10A01A0A1_00000400`) |
| LAN IP | 192.168.0.21 | 192.168.0.22 |
| 3D | Active (FRC via T-CON "PEM" micro) | Active (some models) |
| Ginga middleware (Brazil) | ByYouTV (TOTVS) — Lua + LuaJava + Boost + OWB/WebKit **[C:license-PDF]** | Astro TV (TQTVD) **[C:manual]** |

### Unit identity (HX855 rating sticker, transcribed by vision model)

- Serial: **1006472** — no manufacture date or date code printed on the sticker
- Made in Polo Industrial de Manaus, Brazil (Sony Brasil Ltda, CNPJ
  43.447.044/0001-77)
- Power: 110–220 V ~ 60 Hz, 120 W
- WiFi module marking: **Wlan - J20H049** (ANATEL 2858-11-6740) — Sony's
  internal module ID; external attribution still says DWM-W046/AR9271
- GS1 barcode: (01) 07898943613189; document/part ref 4-418-393-01

## 2. SoC and board (AZ3F, from service manual block diagram p.129–130)

- **Main SoC: Sony codename "ATREYU"** — integrates video/TS processing, HDMI
  TMDS handling, DDR3 controller, NAND controller, USB host, Ethernet MAC,
  LVDS panel output, audio, SPDIF, SIRCS IR, I2C A/B/C, and **four UARTs**.
  The manual never prints a CXD part number or CPU architecture **[C:SM]** —
  **confirmed visually** by a vision model reading the block-diagram image
  (PDF p.130): no CXD#### anywhere on the page; UARTA/C/D TX/RX, JTAG
  (TCK/TMS/TDI/TDO), "One NAND" and DDR3 "1333 2Gb" / "Muxed 2Gb 4Gb"
  labels all verified **[C:SM+vision]**.
- Part number **CXD4727GB** ("X-Reality Processor", IC9000) is attributed via
  board censuses of sibling models (KDL-46EX724, KDL-40HX853, KDL-55HX753) —
  **medium confidence, not yet confirmed on our board** **[W]**. Verify by
  photographing the BAP board / reading the chip marking.
- CPU: **MIPS little-endian** — confirmed by the TVs' own Opera user agents
  (`Linux mips; … InettvBrowser/2.2 … SonyDTV115`) **[C:live]**. The manual
  states neither core count nor clock **[C:SM]**.
- RAM: DDR3-1333, chip labels "1333 2Gb" and "1333 Muxed 2Gb 4Gb" (device
  capacities; exact vendor parts and total not printed) **[C:SM]**.
  Proxy-board census: Samsung K4B2G1646C-HCH9; AZ2F has 2× = 512 MB **[W]**.
- Flash: "One NAND" device (OneNAND class, likely Samsung KFM2GN6Q2B-class)
  **[C:SM]**, part number not printed.
- Ethernet: Realtek **RTL8201F** 10/100 PHY (MAC inside Atreyu) **[C:SM]**
  (proxy census said RTL8201E — F is what our manual shows).
- USB: Genesys Logic **GL850G** USB 2.0 hub feeding USB1–3 + internal WiFi;
  2× TI TPS2553DBV current-limit switches **[C:SM]**.
- WiFi (HX855): internal USB module, Sony P/N **FX0049221**, 5-pin connector
  (GND/5V/D+/D−/GND). Chipset not in the manual; external attribution says
  Mitsumi DWM-W046 = Atheros AR9271 (ath9k_htc) **[W]**. EX725: UWA-BR100
  dongle (AR7010+AR9280, also ath9k_htc) **[W]**. Everything is USB-attached
  Atheros — good news for mainline ath9k_htc.
- Tuner chain: Sony ASCOT2SR tuner → Sony "JUNO" demod (terrestrial),
  "Luxor" demod (sat) + Allegro A8298 LNB driver; HDMI via Silicon Image
  **Sil9287B** switch; audio: TPA6138A2/NJU72011RB opamps, 2× YDA175 amps;
  LM75B temp sensor **[C:SM]**.
- T-CON side: "PEM" micro with FRC; fed by Atreyu over **SPI_B ("PEM DL"),
  UARTD ("PEM CTRL"), UART_PEM_LOG**; panel-ID EEPROM on I2C (P_ID_ERR →
  5 blinks) **[C:SM]**.

## 3. Software stack (license PDFs + Sony GPL pages + live headers)

| Layer | Component | Evidence |
|---|---|---|
| Kernel | Linux 2.6.x (likely 2.6.35-era) | live `Server: Linux/2.6` **[C:live]**; sibling GPL group ships 2.6.35 **[W]** |
| Libc | **glibc** 2.7 (`glibc-for-dev`) — NOT uClibc | license PDF package list **[C]** + archived Sony GPL page **[W]** |
| Base userland | busybox 1.4.2, iptables 1.4.0, fuse 2.7.4, dosfstools, pump-autoip | license PDF **[C]** + GPL page **[W]** |
| Graphics | **DirectFB 1.3.0 + SaWMan** (no X11), cairo 1.8.6, pango 1.24.2, glib 2.22.5, Qt 4.7.0 | license PDF **[C]** + GPL page **[W]** |
| Web | Opera Devices "InettvBrowser/2.2" (Presto), WebCore/JavaScriptCore/WebKit, libmicrohttpd 0.4.6 | license PDF **[C]** + UA strings **[C:live]** |
| Media | alsa-lib 1.0.19, Linux UVC, V4L2; ffmpeg + gstreamer 0.10.22 exist in Sony's TV OSS tree | license PDF **[C]** + Wayback **[W]** |
| Crypto | OpenSSL (1998–2008 era per copyright), "crypto" GPL package | license PDF **[C]** |
| DRM/middleware | Opera (object code, RE-prohibited EULA), SkypeKit v3, PlayReady, WMDRM, Gracenote; Ginga as above | license PDF **[C]** |
| Device token | SonyDTV115 | UA strings **[C:live]** |
| Toolchain | cross-GCC 4.1.2 | archived GPL page **[W]** |

Full 24-package GPL/LGPL list (license PDF, verbatim): linux-kernel,
gcc-for-dev, alsa-lib, busybox, directfb, dosfstools, fuse, glib,
glibc-for-dev, iptables, libmicrohttpd, pump-autoip, libjs,
exceptionmonitor, crypto, cairo, pango, WebCore, JavaScriptCore, Linux UVC,
V4L2, iconv, Webkit, Qt.

The printed GPL offer points at `http://www.sony.net/Products/Linux/` — the
same portal whose tarballs for our exact model groups are now deleted
(see `right-to-repair.md`).

## 4. Debug / service surface (AZ3F)

- **UARTs on the SoC**: UARTA = main **LOG**, UARTC = **ECS/Hotel**,
  UARTD = PEM CTRL, plus UART_PEM_LOG; **JTAG** and a "TL-JIG" test-jig
  reference also appear **[C:SM]**. The manual gives **no physical connector
  or test-pad locations** — finding where UARTA lands on the BAP board is our
  #1 hands-on task (board tracing or the service jig docs).
- Precedent: on the EMMA3TH-era LX900 the debug console was CN5502, 3.3 V
  TTL, with the plaintext **"ABK Monitor"** boot ROM (TFTP/ELF/S-record
  boot, memory tools, MIPS disassembler) reachable at boot **[W]**. Whether
  AZ3F's boot ROM offers the same is unverified but is the working
  hypothesis for an unbrickable experimentation path.
- **Service mode** (RM-ED047): standby, then DISPLAY → Ch 5 → Vol+ → Power.
  Self-diagnostic screen: DISPLAY → Ch 5 → Vol− → Power. Categories cycle
  Digital/Chassis/VPC; chassis category is named "WYVERN"; write with
  Mute+0 **[C:SM]**. Diagnostics expose MAIN firmware module versions
  (DM/WF/DF/YM/DB/DD/WP…), board MID/PID, panel ID, error history with
  timestamps, boot count, and four watchdog classes (incl. HOST_WDT)
  **[C:SM]**.
- **8 blinks = "Software Error"** — manual says suspect the main board's
  memory or the WiFi module: a documented software-fault symptom **[C:SM]**.
- Firmware update: iManual documents network update only; the `_auth.zip`
  USB packages we hold are Sony's manual-update distribution for the same
  builds (per Sony's own download instructions) **[C:manual vs W]**.

## 5. Network surface (live, both sets)

| Port | Service | Notes |
|---|---|---|
| 80/tcp | Sony CERS/IRCC HTTP API | `getSystemInformation` unauthenticated **[C:live]**; `register` mode 2 pops an on-screen dialog (deferred — HX855 is the workstation's monitor); HX855 additionally advertises `sendContentUrl` + `Notification` actions |
| 52323/tcp | UPnP MediaRenderer + IRCC (X_SendIRCC SOAP) | full DMR XML captured in `docs/research/liverecon/` **[C:live]** |
| 9784/tcp | tcpwrapped (EX725 only) | resets on any data; protocol unknown **[C:live]** |

## 6. Firmware container (facts, see `docs/research/webfindings.md`)

Whole-file encrypted (flat 7.9998-bit entropy, zero duplicate 16-byte
blocks → CBC/CTR-class, not ECB), sizes 95,079,200 / 68,295,040 bytes,
no plaintext structure anywhere. No public decryptor for this generation.
Six-image regional corpus in `firmware/` for differential work. NOTE
(corrected after partner review, 2026-09-13): the zip CRC-32 values are
computed over the **encrypted** bytes as stored — they verify container
integrity, NOT plaintext correctness. The filename 8-hex field is a platform
ID (constant across regions), not a plaintext hash. There is therefore **no
known correctness oracle** for decryption key guesses, and against
CBC/CTR-class encryption the corpus has little cryptanalytic value.

## 7. What is NOT documented anywhere we looked

- Atreyu's CXD part number, CPU core count/clock (manual silent)
- Physical UART/JTAG pad locations (block diagram only)
- Bootloader/ABK details for AZ3F; the update-decryption keys
- HW video decoder programming interface (the prize for VLC-class playback)
- Exact kernel version for our two model groups (GPL tarballs deleted;
  2.6.35 inferred from sibling groups)