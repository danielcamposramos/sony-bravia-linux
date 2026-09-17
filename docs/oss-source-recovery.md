# The GPL source Sony used to offer — recovering what is left of it

**2026-09-17.** A follow-up to [licence-basis.md](licence-basis.md),
which established that Sony's Source Code Distribution Service is live
in 2026 and that **no 2010–2012 EX/HX/NX/CX model appears in it**. This
page asks the next question — *was it ever there, and can any of it be
recovered* — and answers both with evidence.

**Not legal advice.** Facts and dates; conclusions belong to people
qualified to draw them.

## It was there. Here is the proof.

The Internet Archive's earliest capture of Sony's OSS TV listings is
**2014-10-09/10**. Those pages list **709 `EX`/`HX`/`NX`/`CX` models**
across the four regional categories — including, by exact model number:

```
KDL-32EX725  KDL-37EX725  KDL-40EX725  KDL-46EX725  KDL-55EX725  KDL-60EX725
KDL-40HX855  KDL-46HX855  KDL-55HX855   KDL-40HX853  KDL-46HX853  KDL-55HX853
```

**Both of this project's televisions are in that listing.** Sony
published the source for them, exactly as the licence requires, and the
Archive preserved the page.

Today the same listings carry **798 `KDL-` models and zero from this
generation**. The delisting is documented; only its date is not — the
Archive's coverage of that tree is thin between 2016 and 2024.

## What Sony shipped for our model group

The 2014 listing links each model group to a download page. The one
covering `KDL-46EX725` (group page `KDL-32CX520.html`, snapshot
2015-07-27) lists **23 source packages** — the complete platform:

| Component | Package |
|---|---|
| Kernel | `linux-kernel.tgz` |
| **Cross-toolchain** | `sony-cross-gcc-for-dev-4.1.2-05000301.src.rpm` |
| C library | `sony-target-dev-glibc-for-dev-2.7-05000303.src.rpm` |
| Graphics | `sony-target-dev-directfb-1.3.0-05000309.src.rpm`, `directfb_modules.zip`, `cairo-1.8.6.tar`, `pango-1.24.2.tar` |
| Browser engine | `WebCore.tar`, `JavaScriptCore.tar`, `libjs-1.5.tar` |
| Userland | `sony-target-dev-busybox-1.4.2`, `-alsa-lib-1.0.19`, `-iptables-1.4.0`, `-dosfstools-2.11`, `-fuse-2.7.4`, `-glib-2.22.5`, `-libmicrohttpd-0.4.6` (all `.src.rpm`) |
| Media / misc | `uvcvideo-r104.tar.gz`, `v4l2spec-0.24.tar.bz2`, `libiconv-1.13.1.tar.gz`, `pump-autoip-0.8.15`, `crypto.tgz`, `em.tgz` |

This is not a token gesture — it is **the build environment**, including
the cross-compiler. It corroborates [platform-map.md](platform-map.md)
independently: glibc 2.7, DirectFB, a WebKit-derived browser engine,
exactly as the firmware analysis found.

Across all archived KDL-era pages, **83 distinct source packages** were
recovered, including Sony's MIPS toolchain
(`mips-ce3m-linux-gcc-4.1.2`, `-binutils-2.17`, `-gdb-6.6`,
`-glibc-2.5.1`) — the architecture these sets use. Full lists:

- [`research/oss-manifests/ex725-hx855-group.txt`](research/oss-manifests/ex725-hx855-group.txt)
- [`research/oss-manifests/all-kdl-era-packages.txt`](research/oss-manifests/all-kdl-era-packages.txt)

## Can the files themselves be recovered? Mostly no.

Four avenues, all checked on 2026-09-17:

| Avenue | Result |
|---|---|
| **Sony live server** — the tokenised `Download/common/<token>/<file>` URLs from the archived page | **404.** Delisted *and* deleted. |
| **Internet Archive** — the binaries behind those URLs | **Not archived.** The Wayback Machine captured the HTML pages, never the payloads. |
| **GitHub mirrors** — repo and code search for `sony-target-dev`, BRAVIA GPL drops, the oss.sony.net paths | **None found.** Only incidental references. |
| **Our own archive** | **The kernel survives** — 35 727 files, with `COPYING` at the tree root, fetched while it was still offered. |

So the position is: *the manifest is recovered, the kernel is held, and
Sony's patched userland packages appear to be gone.*

### What is still obtainable elsewhere

Many manifest entries are **stock upstream releases** and remain
available from their own projects — `cairo-1.8.6`, `pango-1.24.2`,
`libiconv-1.13.1`, `busybox-1.4.2`, `directfb-1.3.0`, `alsa-lib-1.0.19`,
`iptables-1.4.0`, `dosfstools-2.11`, `glib-2.22.5`, `fuse-2.7.4`,
`libmicrohttpd-0.4.6`, `uvcvideo`, `v4l2spec`. A rebuild can start from
upstream for those.

What is **not** replaceable that way is anything carrying Sony's patches
— the `sony-target-dev-*` and `sony-cross-*` RPMs specifically, whose
whole value is the delta from upstream. Those are the losses.

## On hosting the source here

GPL-licensed source is explicitly redistributable — that is the point of
the licence, and it is the one category of recovered material this
project may share freely (contrast rules 9/9b, which exist because
Sony's *widget bundles* are copyright, not GPL).

Practical position:

- **Manifests: published here**, in `research/oss-manifests/`. They are
  our own extraction from public archived pages, they are small, and
  they are the part with lasting documentary value.
- **The kernel tree: not committed to git.** 401 MB of source does not
  belong in a repository, and git is the wrong transport for it. It stays
  in the owner's archive and can be supplied on request — which is
  precisely the arrangement the GPL contemplates, and the one Sony's own
  page describes for physical media.
- **If anyone holds the missing `sony-target-dev-*` packages**, they are
  the gap worth filling. A single surviving mirror would restore the
  patched userland for an entire TV generation.

## What would it have cost to keep?

The stated term is three years after last shipment. That was written when
hosting was a line item. It is worth asking what the obligation actually
weighs today, because the answer changes how "we no longer offer this"
should be read.

**Measured, not guessed:**

- The kernel tree we hold is **401 MB uncompressed**; compressing a
  sample gives a ratio of **0.24**, so roughly **~96 MB** as a normal
  `.tar.gz`.
- Our model group's manifest is **23 packages**. The kernel dominates;
  the `src.rpm` userland components of that era run from under a
  megabyte to a few tens of megabytes each.
- Across every archived KDL-era page, **83 distinct packages** appear in
  total — and they are shared across model groups, which is why 709
  models needed nothing like 709 source drops.

Put together, the complete GPL source corpus for this entire television
generation is **low single-digit gigabytes**.

**What that costs to host, at 2026 prices:**

| Option | Cost for ~5 GB |
|---|---|
| Object storage (S3-class, standard tier) | **≈ US$0.10–0.15 per month** |
| Internet Archive | **free**, and explicitly wants this material |
| GitHub Releases | **free**; 2 GB per file, so only the kernel needs splitting |
| A git repository | wrong tool — but `git-lfs` or a release asset solves it |

So the honest framing of the delisting is not "Sony could no longer
afford to host this". It is that **an obligation with a three-year term
was allowed to lapse on schedule**, at a point when continuing to meet it
would have cost roughly the price of a cup of coffee per year, on
infrastructure that did not exist when the term was written.

**And the asymmetry is the point.** The same company still operates the
distribution service — for 798 other `KDL-` models, plus thousands of
products across audio, camera and professional lines. The capability is
running. The generation was simply removed from it.

This is not a legal argument; the three-year term is Sony's to rely on.
It is a **proportionality** argument, and it is the one worth putting in
front of policymakers: a rule that made sense when source distribution
meant pressing and posting physical media now retires documentation
whose storage cost has fallen by four orders of magnitude, for hardware
that is still in people's homes and still working.

## Why this matters beyond our two sets

The 2014 listing covered **709 models**. Those sets are all still out
there, all still running GPL software, and the source Sony once
published for them is no longer offered by anyone. Recovering the
manifest does not fix that, but it does establish what existed, for whom,
and when — which is the difference between "the source is gone" as a
rumour and as a documented fact with a date and a snapshot URL.

Checked 2026-09-17. Every claim here is re-checkable from the Wayback
Machine and Sony's own live site.
