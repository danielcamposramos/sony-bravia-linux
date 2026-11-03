# Sony's GPL sources for our two model groups: recovered

**2026-11-03.**
Everything Sony published as GPL and LGPL source for the BRAVIA EX725 and HX855 groups is recovered, including the patched packages [oss-source-recovery.md](../oss-source-recovery.md) had written off as lost.
[uyjulian](https://github.com/uyjulian) found it in [issue #27](https://github.com/danielcamposramos/sony-bravia-linux/issues/27): the Internet Archive collection [sony-gpl-source](https://archive.org/details/sony-gpl-source) keeps Sony's old download area, `TV/Download/common/` included.

**In this repository:** [`gpl-sources/`](../../gpl-sources/) (262 MB, 30 files, with `SHA256SUMS`, `MD5SUMS` and a README).

## How the files were found

- Our model group's page names 23 packages ([`oss-manifests/ex725-hx855-group.txt`](oss-manifests/ex725-hx855-group.txt)).
- The collection holds every one of the 23 names under `TV/Download/common/`.
- Every file there sits in a folder named after its own MD5, in base64 with `/` written as `_`. All 30 files below match their folder names and the hashes the Internet Archive publishes.
- Where Sony published more than one version of a file, all of them are kept: that is 30 files for 23 names.

## Which group each file belongs to

- **Linked from our group pages** (recorded in [webfindings.md](webfindings.md)): the two kernels.
- **EX725 group, very likely:** Sony published exactly our 23 names a second time for the VAIO SVL24 (`VAIO/Download/SVL24/` in the same collection). Its kernel is byte for byte the EX725 group's, so its other 22 files are very likely the EX725 group's set too.
- **Not yet known:** six other versions of six of the names, most likely the HX855 group's. The HX855 group page on the Wayback Machine will settle it; the Wayback Machine was offline when this was written.

| File | Folder | Bytes | Model group |
|---|---|---|---|
| `cairo-1.8.6.tar` | [`_v1eBbguvwrSf1a5QRTUSA`](../../gpl-sources/common/_v1eBbguvwrSf1a5QRTUSA/cairo-1.8.6.tar) | 7,204,802 | EX725 group, very likely (the VAIO SVL24 set) |
| `crypto.tgz` | [`Js4ht2FvzsPFbUtFDgkHiA`](../../gpl-sources/common/Js4ht2FvzsPFbUtFDgkHiA/crypto.tgz) | 4,239 | not yet known (another version) |
| `crypto.tgz` | [`thFpsfgEXdyCtRkiAeI+Xg`](../../gpl-sources/common/thFpsfgEXdyCtRkiAeI%2BXg/crypto.tgz) | 4,320 | EX725 group, very likely (the VAIO SVL24 set) |
| `directfb_modules.zip` | [`M5OfDH01kJeGu3l6XW+kfw`](../../gpl-sources/common/M5OfDH01kJeGu3l6XW%2Bkfw/directfb_modules.zip) | 62,462 | not yet known (another version) |
| `directfb_modules.zip` | [`cH8dXykF4tLyVXIXbOGBZw`](../../gpl-sources/common/cH8dXykF4tLyVXIXbOGBZw/directfb_modules.zip) | 67,111 | EX725 group, very likely (the VAIO SVL24 set) |
| `directfb_modules.zip` | [`sI3zLmD7114uRCSCR1OlxQ`](../../gpl-sources/common/sI3zLmD7114uRCSCR1OlxQ/directfb_modules.zip) | 16,354 | not yet known (another version) |
| `em.tgz` | [`PjLq+PrAXd_GtY+GcYLuaQ`](../../gpl-sources/common/PjLq%2BPrAXd_GtY%2BGcYLuaQ/em.tgz) | 139,876 | EX725 group, very likely (the VAIO SVL24 set) |
| `em.tgz` | [`vJTDoXLUfaKTjU_xk4kvZQ`](../../gpl-sources/common/vJTDoXLUfaKTjU_xk4kvZQ/em.tgz) | 175,641 | not yet known (another version) |
| `JavaScriptCore.tar` | [`4W+3ot_FcTEPKuZ93MAxDQ`](../../gpl-sources/common/4W%2B3ot_FcTEPKuZ93MAxDQ/JavaScriptCore.tar) | 11,912,192 | EX725 group, very likely (the VAIO SVL24 set) |
| `JavaScriptCore.tar` | [`FAhS_p+qtlaFoSjqPQDGhQ`](../../gpl-sources/common/FAhS_p%2BqtlaFoSjqPQDGhQ/JavaScriptCore.tar) | 11,857,920 | not yet known (another version) |
| `libiconv-1.13.1.tar.gz` | [`erM+vSZofHRKNyZKMwu+mg`](../../gpl-sources/common/erM%2BvSZofHRKNyZKMwu%2Bmg/libiconv-1.13.1.tar.gz) | 4,716,070 | EX725 group, very likely (the VAIO SVL24 set) |
| `libjs-1.5.tar` | [`lx3wrnHF8u9G8lkn2p18uw`](../../gpl-sources/common/lx3wrnHF8u9G8lkn2p18uw/libjs-1.5.tar) | 1,002,561 | EX725 group, very likely (the VAIO SVL24 set) |
| `linux-kernel.tgz` | [`qNe4FQvq2i_B0gV8BTteCw`](../../gpl-sources/common/qNe4FQvq2i_B0gV8BTteCw/linux-kernel.tgz) | 49,654,174 | HX855 group: its page links this file |
| `linux-kernel.tgz` | [`zBiusZMzHFG8SB4KDXDP3A`](../../gpl-sources/common/zBiusZMzHFG8SB4KDXDP3A/linux-kernel.tgz) | 49,652,119 | EX725 group: its page links this file |
| `pango-1.24.2.tar` | [`7EMu1Ad+AwVjM4TdPZTu9w`](../../gpl-sources/common/7EMu1Ad%2BAwVjM4TdPZTu9w/pango-1.24.2.tar) | 2,175,128 | EX725 group, very likely (the VAIO SVL24 set) |
| `pump-autoip-0.8.15-5_0_DTV10_20090911.tar.tar` | [`JAsrJBwGW2I6LNigL+WA1g`](../../gpl-sources/common/JAsrJBwGW2I6LNigL%2BWA1g/pump-autoip-0.8.15-5_0_DTV10_20090911.tar.tar) | 57,556 | EX725 group, very likely (the VAIO SVL24 set) |
| `sony-cross-gcc-for-dev-4.1.2-05000301.src.rpm` | [`gG6xJTMPZiiciiIv3jrW1Q`](../../gpl-sources/common/gG6xJTMPZiiciiIv3jrW1Q/sony-cross-gcc-for-dev-4.1.2-05000301.src.rpm) | 39,734,258 | EX725 group, very likely (the VAIO SVL24 set) |
| `sony-target-dev-alsa-lib-1.0.19-05000301.src.rpm` | [`Y37Joy8x4bDAYv9jf4OVsw`](../../gpl-sources/common/Y37Joy8x4bDAYv9jf4OVsw/sony-target-dev-alsa-lib-1.0.19-05000301.src.rpm) | 794,856 | EX725 group, very likely (the VAIO SVL24 set) |
| `sony-target-dev-busybox-1.4.2-05000301.src.rpm` | [`S1Q3UxiyKlV_YkQGc_shcg`](../../gpl-sources/common/S1Q3UxiyKlV_YkQGc_shcg/sony-target-dev-busybox-1.4.2-05000301.src.rpm) | 1,572,973 | EX725 group, very likely (the VAIO SVL24 set) |
| `sony-target-dev-directfb-1.3.0-05000309.src.rpm` | [`SMwDh42rl+4TvrFsbHZUGw`](../../gpl-sources/common/SMwDh42rl%2B4TvrFsbHZUGw/sony-target-dev-directfb-1.3.0-05000309.src.rpm) | 2,843,081 | EX725 group, very likely (the VAIO SVL24 set) |
| `sony-target-dev-dosfstools-2.11-05000301.src.rpm` | [`wCMfaMd7HI_G86T4uCzhGw`](../../gpl-sources/common/wCMfaMd7HI_G86T4uCzhGw/sony-target-dev-dosfstools-2.11-05000301.src.rpm) | 75,249 | EX725 group, very likely (the VAIO SVL24 set) |
| `sony-target-dev-fuse-2.7.4-05000302.src.rpm` | [`+Svbp2m3Vhz5U_xMI3UWXw`](../../gpl-sources/common/%2BSvbp2m3Vhz5U_xMI3UWXw/sony-target-dev-fuse-2.7.4-05000302.src.rpm) | 520,028 | EX725 group, very likely (the VAIO SVL24 set) |
| `sony-target-dev-glib-2.22.5-05000302.src.rpm` | [`7fc_nfy5IVGjwvgLJ8ym1A`](../../gpl-sources/common/7fc_nfy5IVGjwvgLJ8ym1A/sony-target-dev-glib-2.22.5-05000302.src.rpm) | 4,981,425 | EX725 group, very likely (the VAIO SVL24 set) |
| `sony-target-dev-glibc-for-dev-2.7-05000303.src.rpm` | [`uS4fWOHv_ohP_2iCemOmXg`](../../gpl-sources/common/uS4fWOHv_ohP_2iCemOmXg/sony-target-dev-glibc-for-dev-2.7-05000303.src.rpm) | 15,848,945 | EX725 group, very likely (the VAIO SVL24 set) |
| `sony-target-dev-iptables-1.4.0-05000201.src.rpm` | [`b33phV7VKoW0Ca1TrqdgoQ`](../../gpl-sources/common/b33phV7VKoW0Ca1TrqdgoQ/sony-target-dev-iptables-1.4.0-05000201.src.rpm) | 184,747 | EX725 group, very likely (the VAIO SVL24 set) |
| `sony-target-dev-libmicrohttpd-0.4.6-05000301.src.rpm` | [`oQSnNsHpnyUwS6Mcp6ccbw`](../../gpl-sources/common/oQSnNsHpnyUwS6Mcp6ccbw/sony-target-dev-libmicrohttpd-0.4.6-05000301.src.rpm) | 884,017 | EX725 group, very likely (the VAIO SVL24 set) |
| `uvcvideo-r104.tar.gz` | [`rpdjdy55iXrkyJXHTreKXw`](../../gpl-sources/common/rpdjdy55iXrkyJXHTreKXw/uvcvideo-r104.tar.gz) | 76,898 | EX725 group, very likely (the VAIO SVL24 set) |
| `v4l2spec-0.24.tar.bz2` | [`Br55iqPIJG40yGB7CJfIAQ`](../../gpl-sources/common/Br55iqPIJG40yGB7CJfIAQ/v4l2spec-0.24.tar.bz2) | 248,999 | EX725 group, very likely (the VAIO SVL24 set) |
| `WebCore.tar` | [`1X8xysjJSCfoYzKwMhW4cA`](../../gpl-sources/common/1X8xysjJSCfoYzKwMhW4cA/WebCore.tar) | 33,935,360 | not yet known (another version) |
| `WebCore.tar` | [`uNBw2L1jqMLZJKibDyGztQ`](../../gpl-sources/common/uNBw2L1jqMLZJKibDyGztQ/WebCore.tar) | 33,994,240 | EX725 group, very likely (the VAIO SVL24 set) |

## What the patched packages hold

Sony's `sony-target-dev-*` and `sony-cross-*` source RPMs are each the upstream release plus Sony's patches and build spec. A first look:

- **Cross compiler** (`sony-cross-gcc-for-dev-4.1.2`): GCC 4.1.2 with 51 files, among them MIPS patches (`mips-enable-vr5500-condmov`, RDHWR reordering, `-mxgot` for crtstuff and libgcc); its spec notes "Add Vr5500 conditional move support".
- **C library** (`sony-target-dev-glibc-for-dev-2.7`): glibc 2.7 with 142 files, including MIPS fixes (GNU hash, `-mxgot`, high-precision timing) and `*_reltime_np` relative-timeout additions to NPTL.
- **DirectFB 1.3.0:** big-endian fixes for NV12, NV16, YUY2 and UYVY, a GPU access flag for preallocated surfaces, a `GetAcceleration` fix and a `gettimeofday` hook; `directfb_modules.zip` adds Sony's image provider and, in one version, a `dtv` system module.
- **BusyBox 1.4.2:** 13 patches and Sony's `dotconfig`.
- **FUSE 2.7.4:** the CVE-2009-3297 fix, compatibility switched off, a `gettimeofday` hook.
- **glib 2.22.5:** a `gettimeofday` time hook.
- **dosfstools 2.11:** three fixes.
- **alsa-lib, iptables, libmicrohttpd:** the upstream release and Sony's spec, no patches.

A rebuild of the sets' userland can now start from Sony's own packages instead of from upstream alone.

## The kernels

Both kernels are surveyed in [gpl-kernels-2623-survey.md](gpl-kernels-2623-survey.md): Linux 2.6.23.17 with Sony's MIPS board support.

## Credits

- **uyjulian**, who found the collection and showed us, twice, that our groups' files are in it.
- **The Internet Archive** and whoever assembled `sony-gpl-source`, which kept Sony's download area after Sony removed it.
- **Sony**, which published these sources under the GPL and LGPL in the first place.
