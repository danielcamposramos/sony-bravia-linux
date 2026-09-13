# Senior-partner review — 2026-09-13

Three external senior partners reviewed the repo independently (same five
questions: roadmap critique, UART/root acquisition, decoder strategy, GPL
lever, red-team of our conclusions):

- **Opus** (Claude Opus, via `claude` CLI in tmux; read the repo itself)
- **DeepSeek v4-pro** (ACIG consult_partner, repo files injected)
- **Kimi K3** (ACIG kimi_swarm, repo files injected)

Owner addition after the consult: an exploit-chain track (userspace
foothold → 2.6.35-era kernel privesc) — see the end of this file.

## Consensus (≥2 partners, adopted into the roadmap)

1. **"Unbrickable" Stage 1 was conditional, not established.** The ABK
   boot-monitor hypothesis for AZ3F is unverified; until a TFTP/UART boot
   path is confirmed, custom-kernel boot means writing flash, which is not
   unbrickable. → the roadmap now treats "ABK/TFTP confirmed" as a **gate**.
2. **Stage 0 as written was unreachable** (DeepSeek's catch): Track B's
   realistic yield is a boot *monitor*, not a Linux shell you can chroot
   from. The modern userland should be built **for a custom initramfs**
   (Stage 1's deliverable), not for chroot on the stock system. Stage 0 and
   Stage 1 swap roles: toolchain → bootable kernel+initramfs → pivot into
   the modern userland.
3. **Stage 2 as "forward-port to 3.x/4.x" is over-scoped** for a 2-person
   team, and probably a dead end for the AV path: era-typical vendors ship
   the video path as binary `.ko` modules tied to one exact kernel, so a
   3.x kernel would boot a *headless* MIPS box. The realistic Stage 2 is
   **backports (compat-wireless etc.) on the stock 2.6.35**; a true
   forward-port only if the GPL sources show the AV drivers are source-
   available. A "Stage −1" **inventory** (`lsmod`, `/proc/cpuinfo`,
   `/proc/mtd`, flash dump with OOB) now gates this go/no-go.
4. **NAND backup before anything else.** The first root access should
   produce a full flash dump (incl. OOB) stored off the TV. This was
   missing from the original roadmap.
5. **UART before JTAG**, with a shared discovery sequence: high-res photos
   of the board → find candidate pads/connectors (unpopulated footprints,
   do-not-populate resistors on RX lines) → logic-analyzer boot capture
   (fx2 clone + sigrok; try 115200/57600/38400/9600; check idle voltage,
   1.8 V I/O possible) → then multimeter tracing. Boot-monitor-present
   sign: ASCII banner before kernel messages; absent sign: first output is
   a Linux banner within ~1 s, nothing reacts to Space/Enter/Ctrl-C/ESC.
6. **Decoder strategy**: the stock renderer is already a decoder API —
   UPnP `SetAVTransportURI` (+ HX855 `sendContentUrl`). A LAN **remux**
   proxy (MKV → TS container, no transcode) gives HD hardware decode with
   no root in days. After root: drive the same renderer from localhost.
   Middleware hooking (LD_PRELOAD/exeDSP-style) next; kernel-driver RE of
   the decoder is last and possibly impossible from GPL sources alone.
7. **GPL request should be evidence-dense**: exact models, PKG versions,
   platform IDs, serials, the printed package list verbatim, dead tarball
   URLs + Wayback captures, explicit request for complete corresponding
   source incl. kernel `.config` and build scripts. Escalation ladder if
   unresponsive: formal letter → Software Freedom Conservancy (they
   enforce for BusyBox, which is on our list; only copyright holders have
   standing) → public pressure (FULU/Rossmann) last.

## Opus's unique contributions (adopted)

- **CRC-32 oracle claim was wrong — our error, now fixed in
  `webfindings.md`.** The zip CRC-32 is computed over the *encrypted* bytes
  as stored; it verifies container integrity, not plaintext correctness.
  The filename 8-hex field is a platform ID (constant across regions), not
  a plaintext hash. Consequence: we have **no** correctness oracle for key
  guesses, and the 6-image corpus has almost no cryptanalytic value against
  CBC/CTR encryption (different regions likely share keys but the diff
  leaks nothing about plaintext structure).
- **Our service manual is the European AEP/UK/IT variant** (covers
  HX850/853/855 AEP/UK/IT). Our set is Brazilian ISDB-Tb: the satellite
  demod ("Luxor") + A8298 LNB driver may not be populated on our board,
  and connector/pad details may differ. Board photos of *our* unit remain
  mandatory.
- **"mipsel confirmed by UA" was overstated** — the UA says `Linux mips`,
  which does not encode byte order. Little-endian is likely (EMMA3TH-era
  Sony MIPS is LE) but strictly unconfirmed until we see an ELF header.
- **"Four UARTs" is a miscount**: UARTA, UARTC, UARTD + PEM log — UARTB is
  absent from the diagram, and the **RF Rx/Tx/RF_UART_SEL lines (pins
  14/16/18 of the BAP–H harness) are likely the muxed missing UART** —
  probe the BAP end of that connector. TL-JIG (next to UARTA/UARTC/Reset
  in the diagram) is probably the factory jig interface.
- **Stage 1 brick risks enumerated**: `CONFIG_MODVERSIONS` symbol-CRC
  mismatch would stop Sony's binary `.ko`s from loading (the pass test is
  "stock modules load and panel shows a picture", not "it boots"); TFTP-
  booted kernels still attach flash (UBI/JFFS2 mounts **write**) — keep
  flash unmounted/read-only, rootfs on USB/NFS; unfed watchdogs
  (HOST_WDT, PEM_WDT) cause reset loops that look like crashes.
- **Stage 0 userland caveats**: check FPU/emulation before shipping
  hard-float; static musl/uClibc-ng soft-float safest; if glibc, stay
  ≤2.26 (2.26 needs kernel 3.2). RAM ceiling is real — killing Sony's
  main app risks watchdog trips.
- **Drop the keyring goal from B3.** With root we have the rootfs anyway;
  old update-image decryption buys little, and the keyring sits next to
  PlayReady/Marlin/CI+ keys — decide now never to extract/publish those,
  and redact per-device keys from any shared dump. (Matches our no-DRM
  ethics line; now explicit.)
- **GPL framing fix**: don't claim "obligated as long as binaries ship" —
  the license PDF has a printed URL, not a §3(b) written offer. Request
  source on the printed-offer basis instead of a dismissible theory.
- **Better than any letter: Wayback CDX prefix query** on
  `sony.net/Products/Linux/TV/Download/*` matching tarballs by platform
  ID rather than model page — sibling regional builds share platform IDs.
- **Practical**: hands-on experiments on the EX725 or a cheap **donor main
  board**, never the HX855 (it is the workstation's monitor).
- **Safety**: "Track B modifies nothing" stops being true when you
  ground-reference a USB adapter to a mains-powered set — treat opening
  the set as the risk step it is.

## Kimi's unique contributions (adopted)

- Don't hard-code 2.6.35 in planning (inferred, not confirmed for our
  groups).
- Wayback CDX + Common Crawl + archive.today sweeps for captures outside
  the normal index; regional Sony OSS pages for sibling tarballs.
- Stage 0 risk wording: "no risk to internal flash", not "no risk to the
  TV".
- Nimue non-applicability should rest on our own scans — it does: our
  full-port scans show 12345 closed on both sets, which is primary
  evidence and settles it.

## Discarded / corrected inputs

- DeepSeek's follow-up "red-team" section was **discarded wholesale**: it
  critiqued claims that do not exist in this repo (Android CVEs, socketed
  eMMC, verified boot) — the follow-up call lost the original context and
  the model invented a project. Its part-1 review and the SFC ladder
  (point 4) survive, cross-checked.
- The vision model's invented connector list (CN102–CN115) remains
  discarded; its UART/JTAG/DRAM transcriptions were kept after
  cross-checking against the text layer.

## Owner addition: exploit-chain track (Track B-alt)

Leverage the kernel/era's known flaws as an alternate way in — adopted as
a parallel, no-solder route:

1. **Foothold**: any memory-safety bug in the reachable userspace — the
   Opera Presto 2.10/HbbTV engine (Nimue issue #4 territory, never
   audited), CERS HTTP handlers (port 80), the UPnP stack (52323), or the
   unknown 9784 service on the EX725. These are 2011-era network services
   that have never faced an audit.
2. **Privesc**: from any local code execution, a stock 2.6.35 kernel is
   vulnerable to a decade of public LPEs (Dirty COW and the whole 2010+
   set). One compiled MIPS binary turns a foothold into root.
3. **Why it can beat UART**: no physical opening, remotely repeatable,
   testable against the EX725 first. Why it may not: a decade of Sony
   patches shipped in PKG updates (unlikely to cover everything), and the
   userspace attack surface may be smaller than it looks (thin, custom
   handlers rather than full-featured servers).
4. **Ethics/scope**: our own sets, on our own LAN — standard owner-security
   research; any findings stay in this repo until coordinated disclosure
   if they touch other people's devices.

Firmware-diff opportunity: we hold multiple PKG builds of the same
platform (00000301/00000400, 00001400/00011400) — once decryption ever
happens, patch-diffing between builds directly reveals which flaws Sony
fixed (and thus which remain).

## Resulting changes to the roadmap

See `feasibility-roadmap.md` (updated in the same commit): Stage −1
inventory added; ABK gate added; Stage 0/1 reordered; Stage 2 reframed to
"backports first, forward-port conditional"; NAND backup promoted to
first post-root action; Track B-alt exploit chain added; decoder section
rewritten around the remux-proxy insight; legal framing corrected;
safety and donor-board rules added.