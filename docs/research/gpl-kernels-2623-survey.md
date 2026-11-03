# The GPL kernels of our two model groups, recovered: survey

**2026-11-03.**
Found by [uyjulian](https://github.com/uyjulian) in [issue #27](https://github.com/danielcamposramos/sony-bravia-linux/issues/27): the Internet Archive collection [sony-gpl-source](https://archive.org/download/sony-gpl-source/) holds the files of Sony's old OSS download area, including its `TV/Download/common/` folder.
Our September notes ([webfindings.md](webfindings.md)) had recorded both kernel links from our groups' archived listing pages and marked them dead, because the Wayback Machine had not kept the files.
The collection has them.

## Where they came from

| Group | Listing page (Wayback) | Sony's link | Archive copy |
|---|---|---|---|
| EX725 group | `KDL-32CX520.html` (2014-01-25, 2014-02-26) | `Download/common/zBiusZMzHFG8SB4KDXDP3A/linux-kernel.tgz` | [link](https://archive.org/download/sony-gpl-source/TV/Download/common/zBiusZMzHFG8SB4KDXDP3A/linux-kernel.tgz) |
| HX855 group | `KDL-46HX750.html` (2012-08-31) | `Download/common/qNe4FQvq2i_B0gV8BTteCw/linux-kernel.tgz` | [link](https://archive.org/download/sony-gpl-source/TV/Download/common/qNe4FQvq2i_B0gV8BTteCw/linux-kernel.tgz) |

| File | Bytes | MD5 | SHA-1 |
|---|---|---|---|
| EX725 group `linux-kernel.tgz` | 49,652,119 | `cc18aeb193331c51bc481e0a0d70cfdc` | `310c86d299ce86421337d3c08d9cba941b06396a` |
| HX855 group `linux-kernel.tgz` | 49,654,174 | `a8d7b8150beada2fc1d2057c053b5e0b` | `14a6244cfb2a0a1256d82ddf2d595318db451954` |

Both downloads match the hashes the Internet Archive publishes for them.
Both are in this repository, in [`gpl-sources/common/`](../../gpl-sources/common/) ([gpl-sources-mirror.md](gpl-sources-mirror.md)).

## The folder names are content hashes, not hiding

Each folder under `common/` is the file's own MD5, written in base64 with `/` replaced by `_`.
That holds for 269 of the 270 files in the collection's `common/` folder.
Sony stored each tarball once under its fingerprint, and every model page that used it linked to the same copy; that is why one tarball serves many models and why the links look cryptic.
The one exception, `WOwv7AiHK3L4_VJvLaIKng/samba-3.0.37.tar.gz`, does not match its own name, so that archived copy is probably not the file Sony published.

## What they are

- **Linux 2.6.23.17**, a Sony product base named `kernel26`, 14,127 files each.
- **The same base released twice.** Sony's file headers read "2010-12-14: File added by Sony Corporation" in the EX725 group's tree and "2012-01-13" in the HX855 group's; 954 files differ, mostly USB (114), kernel headers (94), the Freescale MXC drivers (84), video (42) and media (42).
- **One base for many Sony products, not a TV-only tree.** 1,484 files in each tree name Sony Corporation, and most belong to other platforms: Freescale MXC and TI OMAP drivers, NEC MP200 video, the `pgpf` drivers of a navigation device (`navu2`), USB gadget and wireless work.
- **The MIPS boards in it** (missing from the shared 2.6.35 tarball, [kernel2635-survey.md](kernel2635-survey.md)):
  - `arch/mips/ayu/` ("Support for Ayubrd", `ayubrd_defconfig`) with `ayubrd/` and `common/`: setup, PROM, interrupts (`irq_intc.c`, `irq_pcb.c`), GPIO, clocks, power management and suspend, reset, devices, memory windows (`uma.c`, `umem.c`), BDI; `include/asm-mips/ayu` and `mach-ayu`. A MIPS32 release 2 core.
  - `arch/mips/emma3/`: NEC's EMMA3 family, with Sony's `BDRE` and `BDP` series and the "Sony DTHD series" (`DTHD`, on the EMMA3T variant), plus an evaluation board; and `arch/mips/emma2rh/`.
  - `arch/mips/snsc/`, `include/asm-mips/snsc`, `drivers/block/snsc` and `arch/mips/Kconfig.snsc`: Sony's own kernel options (boot information from the loader, MIPS cache and DMA fixes, modules loaded into KSEG0, and more).
- **No decoder, demux, panel or tuner driver in source.** The Sony-marked media files are camera capture and output for the ARM platforms (MXC, MP200) and UVC; the 2.6.35 survey's conclusion, that the TV's video path ships as binary modules, still stands.
- **The exploit-chain notes still hold on 2.6.23:** MIPS has no execute-inhibit page bit here at all (`include/asm-mips/pgtable-bits.h`), no randomised mmap layout for MIPS, and the `randomize_va_space` switch exists (`kernel/sysctl.c`), as [presto-cve-2011-2628.md](presto-cve-2011-2628.md) assumed for 2.6.35.

## What is not settled

- **Which board our sets are.** `AYU` fits the name ATREYU, but no file in either tree says "Atreyu" or names a CXD part; [platform-map.md](../platform-map.md) identifies ATREYU from the service manual and the SoC label. `DTHD` is the other Sony MIPS series in the tree.
- **Byte order.** Every MIPS board here builds big-endian only: `AYUBRD` and the EMMA3 boards select `SYS_SUPPORTS_BIG_ENDIAN` alone, and `ayubrd_defconfig` sets `CONFIG_CPU_BIG_ENDIAN=y`. Our platform map calls the sets little-endian from their browser's user agent, which says only "Linux mips" and does not encode byte order ([partner-review.md](../partner-review.md) had already flagged this). If AYU is our board, the sets are big-endian; the sets' own binaries will settle it.
- **Which kernel the sets actually run.** These are the kernels Sony published for our groups' pages; our earlier "2.6.35" came from the shared `common` tarball and was an inference. The running version still has to come from the sets themselves (the boot console, or the firmware once it is readable).

## Next

1. Compare both trees with mainline 2.6.23.17 and list every file Sony added or changed.
2. Read the `ayu` board code against the platform map's ATREYU facts (UARTs, I2C buses, SIRCS, NAND, USB, Ethernet MAC), and `dthd` the same way.
3. Ask the sets: the kernel banner on the debug console answers which kernel runs, and any ELF binary from them answers the byte order.

## The rest of the sources

The other files of our groups' pages, Sony's patched userland, Qt and cross compiler included, are recovered too: [gpl-sources-mirror.md](gpl-sources-mirror.md).
