# Sony's GPL sources for our two model groups: recovered

**2026-11-03, completed 2026-11-04.**
Everything Sony published as GPL, LGPL and other open source for the BRAVIA EX725 and HX855 groups is recovered, including the patched packages [oss-source-recovery.md](../oss-source-recovery.md) had written off as lost.
[uyjulian](https://github.com/uyjulian) found it in [issue #27](https://github.com/danielcamposramos/sony-bravia-linux/issues/27): the Internet Archive collection [sony-gpl-source](https://archive.org/details/sony-gpl-source) keeps Sony's old download area, `TV/Download/common/` included.

**In this repository:** [`gpl-sources/`](../../gpl-sources/) (313 MB, 36 files, with `SHA256SUMS`, `MD5SUMS` and a README).

## How the files were found

- Each group has its own page on Sony's old source site, and the Wayback Machine kept both:
  - EX725 group: [`KDL-32CX520.html`, captured 2014-02-26](https://web.archive.org/web/20140226165410/http://www.sony.net:80/Products/Linux/TV/KDL-32CX520.html), 23 files ([`oss-manifests/ex725-hx855-group.txt`](oss-manifests/ex725-hx855-group.txt); despite its name, that list is the EX725 page's).
  - HX855 group: [`KDL-46HX750.html`, captured 2013-05-25](https://web.archive.org/web/20130525060651/http://www.sony.net:80/Products/Linux/TV/KDL-46HX750.html), 26 files ([`oss-manifests/hx855-group.txt`](oss-manifests/hx855-group.txt)).
- Every link on both pages points into `Download/common/<folder>/<file>`, and the collection holds every one of them.
- Each folder name is the file's own MD5, in base64 with `/` written as `_`. All 36 files match their folder names and the hashes the Internet Archive publishes.
- Both pages link 13 of the same files, and two more with the same bytes under another name on the HX855 page (`pango-1.24.2.tar.gz`, `libjs-1.6.tar`); both names are kept.

## The files

| File | Folder | Bytes | Group pages that link it |
|---|---|---|---|
| `browser_plugin.rar` | [`EU_LLCMOT_ujIt8OcP69rA`](../../gpl-sources/common/EU_LLCMOT_ujIt8OcP69rA/browser_plugin.rar) | 26,109 | HX855 |
| `cairo-1.8.6.tar` | [`_v1eBbguvwrSf1a5QRTUSA`](../../gpl-sources/common/_v1eBbguvwrSf1a5QRTUSA/cairo-1.8.6.tar) | 7,204,802 | EX725 |
| `cairo-1.8.6.tar.gz` | [`TmQTnvb2aN8kRQ87gd0HcQ`](../../gpl-sources/common/TmQTnvb2aN8kRQ87gd0HcQ/cairo-1.8.6.tar.gz) | 6,616,544 | HX855 |
| `crypto.tgz` | [`thFpsfgEXdyCtRkiAeI+Xg`](../../gpl-sources/common/thFpsfgEXdyCtRkiAeI%2BXg/crypto.tgz) | 4,320 | EX725 and HX855 |
| `directfb_modules.zip` | [`cH8dXykF4tLyVXIXbOGBZw`](../../gpl-sources/common/cH8dXykF4tLyVXIXbOGBZw/directfb_modules.zip) | 67,111 | EX725 and HX855 |
| `em.tgz` | [`PjLq+PrAXd_GtY+GcYLuaQ`](../../gpl-sources/common/PjLq%2BPrAXd_GtY%2BGcYLuaQ/em.tgz) | 139,876 | EX725 and HX855 |
| `JavaScriptCore.tar` | [`4W+3ot_FcTEPKuZ93MAxDQ`](../../gpl-sources/common/4W%2B3ot_FcTEPKuZ93MAxDQ/JavaScriptCore.tar) | 11,912,192 | EX725 |
| `JavaScriptCore.tar` | [`FAhS_p+qtlaFoSjqPQDGhQ`](../../gpl-sources/common/FAhS_p%2BqtlaFoSjqPQDGhQ/JavaScriptCore.tar) | 11,857,920 | HX855 |
| `libiconv-1.13.1.tar.gz` | [`erM+vSZofHRKNyZKMwu+mg`](../../gpl-sources/common/erM%2BvSZofHRKNyZKMwu%2Bmg/libiconv-1.13.1.tar.gz) | 4,716,070 | EX725 and HX855 |
| `libjs-1.5.tar` | [`lx3wrnHF8u9G8lkn2p18uw`](../../gpl-sources/common/lx3wrnHF8u9G8lkn2p18uw/libjs-1.5.tar) | 1,002,561 | EX725 |
| `libjs-1.6.tar` | [`lx3wrnHF8u9G8lkn2p18uw`](../../gpl-sources/common/lx3wrnHF8u9G8lkn2p18uw/libjs-1.6.tar) | 1,002,561 | HX855 |
| `linux-kernel.tgz` | [`qNe4FQvq2i_B0gV8BTteCw`](../../gpl-sources/common/qNe4FQvq2i_B0gV8BTteCw/linux-kernel.tgz) | 49,654,174 | HX855 |
| `linux-kernel.tgz` | [`zBiusZMzHFG8SB4KDXDP3A`](../../gpl-sources/common/zBiusZMzHFG8SB4KDXDP3A/linux-kernel.tgz) | 49,652,119 | EX725 |
| `pango-1.24.2.tar` | [`7EMu1Ad+AwVjM4TdPZTu9w`](../../gpl-sources/common/7EMu1Ad%2BAwVjM4TdPZTu9w/pango-1.24.2.tar) | 2,175,128 | EX725 |
| `pango-1.24.2.tar.gz` | [`7EMu1Ad+AwVjM4TdPZTu9w`](../../gpl-sources/common/7EMu1Ad%2BAwVjM4TdPZTu9w/pango-1.24.2.tar.gz) | 2,175,128 | HX855 |
| `pump-autoip-0.8.15-5_0_DTV10_20090911.tar.tar` | [`JAsrJBwGW2I6LNigL+WA1g`](../../gpl-sources/common/JAsrJBwGW2I6LNigL%2BWA1g/pump-autoip-0.8.15-5_0_DTV10_20090911.tar.tar) | 57,556 | EX725 |
| `qt-src-4.7.0.tar.gz` | [`D7arSIEzKqtAREG60QEeaQ`](../../gpl-sources/common/D7arSIEzKqtAREG60QEeaQ/qt-src-4.7.0.tar.gz) | 39,975,417 | HX855 |
| `sony-cross-gcc-for-dev-4.1.2-05000301.src.rpm` | [`gG6xJTMPZiiciiIv3jrW1Q`](../../gpl-sources/common/gG6xJTMPZiiciiIv3jrW1Q/sony-cross-gcc-for-dev-4.1.2-05000301.src.rpm) | 39,734,258 | EX725 and HX855 |
| `sony-target-dev-alsa-lib-1.0.19-05000301.src.rpm` | [`Y37Joy8x4bDAYv9jf4OVsw`](../../gpl-sources/common/Y37Joy8x4bDAYv9jf4OVsw/sony-target-dev-alsa-lib-1.0.19-05000301.src.rpm) | 794,856 | EX725 and HX855 |
| `sony-target-dev-busybox-1.4.2-05000301.src.rpm` | [`S1Q3UxiyKlV_YkQGc_shcg`](../../gpl-sources/common/S1Q3UxiyKlV_YkQGc_shcg/sony-target-dev-busybox-1.4.2-05000301.src.rpm) | 1,572,973 | EX725 and HX855 |
| `sony-target-dev-directfb-1.3.0-05000309.src.rpm` | [`SMwDh42rl+4TvrFsbHZUGw`](../../gpl-sources/common/SMwDh42rl%2B4TvrFsbHZUGw/sony-target-dev-directfb-1.3.0-05000309.src.rpm) | 2,843,081 | EX725 and HX855 |
| `sony-target-dev-dosfstools-2.11-05000301.src.rpm` | [`wCMfaMd7HI_G86T4uCzhGw`](../../gpl-sources/common/wCMfaMd7HI_G86T4uCzhGw/sony-target-dev-dosfstools-2.11-05000301.src.rpm) | 75,249 | EX725 |
| `sony-target-dev-dosfstools-2.11-05000302.src.rpm` | [`ianUrKkaTacODum03NxWBA`](../../gpl-sources/common/ianUrKkaTacODum03NxWBA/sony-target-dev-dosfstools-2.11-05000302.src.rpm) | 77,782 | HX855 |
| `sony-target-dev-fuse-2.7.4-05000302.src.rpm` | [`+Svbp2m3Vhz5U_xMI3UWXw`](../../gpl-sources/common/%2BSvbp2m3Vhz5U_xMI3UWXw/sony-target-dev-fuse-2.7.4-05000302.src.rpm) | 520,028 | EX725 and HX855 |
| `sony-target-dev-glib-2.22.5-05000302.src.rpm` | [`7fc_nfy5IVGjwvgLJ8ym1A`](../../gpl-sources/common/7fc_nfy5IVGjwvgLJ8ym1A/sony-target-dev-glib-2.22.5-05000302.src.rpm) | 4,981,425 | EX725 and HX855 |
| `sony-target-dev-glibc-for-dev-2.7-05000303.src.rpm` | [`uS4fWOHv_ohP_2iCemOmXg`](../../gpl-sources/common/uS4fWOHv_ohP_2iCemOmXg/sony-target-dev-glibc-for-dev-2.7-05000303.src.rpm) | 15,848,945 | EX725 and HX855 |
| `sony-target-dev-iptables-1.4.0-05000201.src.rpm` | [`b33phV7VKoW0Ca1TrqdgoQ`](../../gpl-sources/common/b33phV7VKoW0Ca1TrqdgoQ/sony-target-dev-iptables-1.4.0-05000201.src.rpm) | 184,747 | EX725 and HX855 |
| `sony-target-dev-libmicrohttpd-0.4.6-05000301.src.rpm` | [`oQSnNsHpnyUwS6Mcp6ccbw`](../../gpl-sources/common/oQSnNsHpnyUwS6Mcp6ccbw/sony-target-dev-libmicrohttpd-0.4.6-05000301.src.rpm) | 884,017 | EX725 and HX855 |
| `sony-target-dev-procps-3.2.7-05000201.src.rpm` | [`vy+H1gDmvfTCwos+EDBRMw`](../../gpl-sources/common/vy%2BH1gDmvfTCwos%2BEDBRMw/sony-target-dev-procps-3.2.7-05000201.src.rpm) | 288,603 | HX855 |
| `sony-target-dev-pump-0.8.17-05000301.src.rpm` | [`w6lIMZiy_CX8M_YC3C0PKw`](../../gpl-sources/common/w6lIMZiy_CX8M_YC3C0PKw/sony-target-dev-pump-0.8.17-05000301.src.rpm) | 76,078 | HX855 |
| `sony-target-dev-util-linux-ng-2.13-05000201.src.rpm` | [`k3oVk5AMg8SodCaAb0ZocQ`](../../gpl-sources/common/k3oVk5AMg8SodCaAb0ZocQ/sony-target-dev-util-linux-ng-2.13-05000201.src.rpm) | 2,712,976 | HX855 |
| `uvcvideo-r104.tar.gz` | [`rpdjdy55iXrkyJXHTreKXw`](../../gpl-sources/common/rpdjdy55iXrkyJXHTreKXw/uvcvideo-r104.tar.gz) | 76,898 | EX725 |
| `uvcvideo.tar.gz` | [`hxmEfH5Ls_xteEEc71DWmg`](../../gpl-sources/common/hxmEfH5Ls_xteEEc71DWmg/uvcvideo.tar.gz) | 53,658 | HX855 |
| `v4l2spec-0.24.tar.bz2` | [`Br55iqPIJG40yGB7CJfIAQ`](../../gpl-sources/common/Br55iqPIJG40yGB7CJfIAQ/v4l2spec-0.24.tar.bz2) | 248,999 | EX725 |
| `WebCore.tar` | [`1X8xysjJSCfoYzKwMhW4cA`](../../gpl-sources/common/1X8xysjJSCfoYzKwMhW4cA/WebCore.tar) | 33,935,360 | HX855 |
| `WebCore.tar` | [`uNBw2L1jqMLZJKibDyGztQ`](../../gpl-sources/common/uNBw2L1jqMLZJKibDyGztQ/WebCore.tar) | 33,994,240 | EX725 |

## What the patched packages hold

Sony's `sony-target-dev-*` and `sony-cross-*` source RPMs are each the upstream release plus Sony's patches and build spec. A first look:

- **Cross compiler** (`sony-cross-gcc-for-dev-4.1.2`, both groups): GCC 4.1.2 with 51 files, among them MIPS patches (`mips-enable-vr5500-condmov`, RDHWR reordering, `-mxgot` for crtstuff and libgcc); its spec notes "Add Vr5500 conditional move support".
- **C library** (`sony-target-dev-glibc-for-dev-2.7`, both): glibc 2.7 with 142 files, including MIPS fixes (GNU hash, `-mxgot`, high-precision timing) and `*_reltime_np` relative-timeout additions to NPTL.
- **DirectFB 1.3.0** (both): big-endian fixes for NV12, NV16, YUY2 and UYVY, a GPU access flag for preallocated surfaces, a `GetAcceleration` fix and a `gettimeofday` hook; `directfb_modules.zip` adds Sony's image providers and a `dtv` system module. Neither has any stereo support.
- **Qt 4.7.0** (`qt-src-4.7.0.tar.gz`, HX855 page): Qt for Embedded Linux, `src` and `include` only, with QtWebKit. Eleven files name Sony or its SNSC and DTV markers: the DirectFB screen, pixmap and paint engine, the Linux framebuffer screen, the font database, threads, SSL, a video surface format and one WebCore file. Its newest file is dated 2012-03-22.
- **Browser plugins** (`browser_plugin.rar`, HX855 page): the NPAPI entry points of four plugins of the TV's browser: audio (AAC and WAV), `ceb` (Open IPTV Forum objects), `dtp` and `felica`. Sony's own files under the Netscape Public License; the plugins' back ends are not in it.
- **BusyBox 1.4.2** (both): 13 patches and Sony's `dotconfig`.
- **FUSE 2.7.4** (both): the CVE-2009-3297 fix, compatibility switched off, a `gettimeofday` hook.
- **glib 2.22.5** (both): a `gettimeofday` time hook.
- **dosfstools 2.11:** three fixes; the HX855 page has a later build (`-05000302`).
- **HX855 page only:** util-linux-ng 2.13, procps 3.2.7 and pump 0.8.17 as Sony builds.
- **alsa-lib, iptables, libmicrohttpd** (both): the upstream release and Sony's spec, no patches.

A rebuild of the sets' userland can now start from Sony's own packages instead of from upstream alone.

## Not ours

The collection also holds other versions of some of these names, linked from other models' pages, not from ours: two `directfb_modules.zip`, a `crypto.tgz` and an `em.tgz` (for a projector generation among others), and two more Qt 4.7.0 archives (`qt_src-4.7.0.zip`, 50 MB, and `qt-everywhere-opensource-src-4.7.0.tar.gz`, 208 MB). They are not kept here.

## The kernels

Both kernels are surveyed in [gpl-kernels-2623-survey.md](gpl-kernels-2623-survey.md): Linux 2.6.23.17 with Sony's MIPS board support.

## Credits

- **uyjulian**, who found the collection and showed us, twice, that our groups' files are in it.
- **The Internet Archive** and whoever assembled `sony-gpl-source`, which kept Sony's download area after Sony removed it; the **Wayback Machine** kept the two group pages that say which files are ours.
- **Sony**, which published these sources in the first place.
