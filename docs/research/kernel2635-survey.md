# GPL kernel2635.tar.gz survey — 2026-09-13

Source: Wayback capture of
`sony.net/Products/Linux/TV/Download/common/xWJNYIdpxDBtyrtSrz_vLA/kernel2635.tar.gz`
(2013-08-26). 228 MB uncompressed-tar (NOT gzipped despite the name — Wayback
served it plain; `tar tf` reads it directly). 28,105 files, 459 MB unpacked.
Kept at `firmware/gpl-sources/kernel2635.tar.gz` (gitignored).

## What it is

- **Linux 2.6.35.14** ("Yokohama") — Sony tracked upstream stable up to
  2.6.35.14. Confirms the 2.6.35-era inference for this generation (this is
  the "common" TV OSS tarball; our exact groups' tarballs used different
  hash-dirs and are still unrecovered).

## What it does NOT contain (the important part)

- **No TV SoC platform support**: `arch/mips/` has only stock mainline
  platforms (emma, alchemy, bcm47xx, …). No CXD/Atreyu board directory
  anywhere in the tree.
- **No decoder, demux, panel/PEM, tuner or Sony-video drivers**: the only
  "sony" files are mainline laptop/peripheral drivers (sonypi.c, sony-laptop,
  hid-sony, ir-sony-decoder, a go7007 staging tuner).
- **Conclusion (Opus's prediction confirmed)**: the AV/video path ships as
  binary `.ko` modules outside the GPL release. The old claim "GPL sources
  are on the HW-decoder's critical path" is **false** — decoder option 4
  (kernel-driver RE from GPL sources) drops to last resort/likely-impossible,
  and a Stage-2 forward-port of AV drivers is dead on arrival. Stage 2 =
  backports on the stock kernel, exactly as the partner review concluded.
- **GPL-compliance angle**: a kernel tree without the target's board files
  cannot produce the shipped binary. The release is arguably *incomplete*
  corresponding source — worth adding to the B5 evidence packet (the binary
  `.ko` modules are also absent, and they are kernel-linked derivative works
  of GPL code unless Sony claims they are independent works).

## What it DOES contain — `guardian.ko` (the lockdown, in source)

`drivers/mod_guardian/guardian.c` — a Sony LSM (Linux Security Module),
NOT in mainline. Fully documented now:

- Registers `security_operations.guardian` with a single hook,
  `sb_mount`.
- A `/proc/protected` proc entry: writing `'1'` sets `protected = 1`
  (there is **no code path to set it back to 0** — write only handles '1').
- When `protected == 1`, any `mount(…, flags)` where
  `!(flags & MS_RDONLY) && (flags & MS_REMOUNT)` → `-EPERM`.
  I.e. it blocks **exactly one thing**: remounting the root filesystem
  read-write.
- `panic()` if `register_security()` fails; silent no-op if
  `security_module_enable()` says another LSM is active.

### Exploit-chain implications

- It does **not** block: mounting a USB stick read-write (new mount, no
  MS_REMOUNT), `pivot_root`, `chroot`, loading modules, or writing to
  already-rw filesystems.
- Therefore, **Stage 0 (modern userland from USB) works even with guardian
  active** — it only protects the *internal* rootfs from modification.
- Defeats from root, in increasing invasiveness: run everything from USB
  (guardian never notices); `rmmod guardian` if it is a module and module
  loading is not otherwise restricted; boot a custom kernel without it
  (TFTP path). The guardian source also gives us the exact `security=`
  boot-parameter mechanics to research for the stock cmdline.
- Narrative value: this module *is* the "GPL software, but locked down"
  complaint in ~100 lines of kernel C — ideal repair.wiki/FULU material.

## Follow-ups

1. Check the rest of the tree for other non-mainline additions (diff against
   vanilla 2.6.35.14) — `drivers/mod_guardian` was found by eye; there may be
   more Sony patches (audit `fs/`, `security/`, `init/`).
2. Extract the kernel `.config`-style defaults if any ship (or wait for the
   B0 inventory on-device `/proc/config.gz`).
3. Cross-reference `guardian` strings against the TVs' running system later
   (`lsmod | grep guardian` at B0).
4. Keep the tarball for Stage 1's toolchain bring-up: even without board
   files it is the exact source to build *against*.