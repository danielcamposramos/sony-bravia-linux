# The legal documents — what they actually let Sony do, and what they don't

Read from our own copies of the KDL-46HX855 legal set (Sony docs, US
region), 2026-09-18: the End User License Agreement (`44119951M` English,
`44119961M` pt-BR), the 12-month Limited Warranty (`41443860M` /
`W0012289M`), and the i-Manual (`W0005741M` / `W0005743M`). Nothing
copyrighted is reproduced here; this is analysis with document-ID
citations, the same basis as [licence-basis.md](licence-basis.md).

The point of reading them is discipline as much as ammunition: the
strongest right-to-repair claims survive the fine print, and the weak
ones die in it. Three pillars, ordered by how well they hold up.

## 1. The GPL source deletion — the strongest point, and it is not disclaimable

The EULA itself contains a **GPL/LGPL Licensed Software** section that
lists the copyleft packages in the product — linux-kernel, glibc,
busybox, directfb, iptables, fuse, Qt, WebCore, JavaScriptCore, WebKit,
libmicrohttpd and more — and states that source code for them **can be
obtained** at a named URL: `http://www.sony.net/Products/Linux/`.

That is Sony's own written representation, and GPLv2 independently
obligates source availability regardless of any contract Sony writes.
Our [oss-source-recovery.md](oss-source-recovery.md) established that the
sources for this generation are **gone** from Sony's distribution — not
Wayback'd, not served. So the document that ships with the TV points at a
source offer the copyright holder has since withdrawn.

Unlike the services (below), **this obligation cannot be disclaimed by
the EULA** — it flows from the upstream copyleft license, not from Sony's
grant. This is the pillar a lawyer cannot wave away with a
reserved-rights clause.

## 2. The 3D feature — a documentation-versus-behavior gap, not a "Service"

The i-Manual documents **Simulated 3D** (2D→3D conversion) as a display
mode that applies to any full-screen content, with the input/format
restriction scoped only to the *stereoscopic* modes, never to Simulated
3D (see [3d-blocked-in-browser.md](3d-blocked-in-browser.md)). It is a
**display/hardware function**, not one of the "Services" or "Content" the
EULA defines and reserves the right to kill. So the
service-discontinuation clause does not reach it.

The claim here is precise and evidenced: a documented display feature,
carrying no documented source restriction, is unavailable for the
platform's own browser-served video. State the manual quotes and the
observed behavior; assert nothing about intent.

## 3. The services shutdown — real for consumers, weak as a contract breach

The honest limit, so nobody builds the case on sand. The EULA **expressly
reserved** the right to discontinue: it says the network services the
software depends on "might be interrupted or discontinued" at Sony's or a
supplier's discretion, and, in the all-caps operative clause, that Sony
may add, change, discontinue, remove or suspend any of the services or
content, temporarily or permanently, **at any time, without notice and
without liability**.

So the death of AppliCast, BRAVIA Internet Video, TrackID and the rest
was **contractually permitted**. A "Sony broke the contract" argument
about the *services* loses on the document's own words. The
right-to-repair case on services is therefore the **consumer / moral**
one — the hardware is fully functional and owners should be free to
restore what they paid for — which is exactly what the existing wiki
page argues, and it does not need a breach claim to stand.

The warranty adds nothing in our favor and nothing against: software is
"AS IS", it covers hardware workmanship only, and services are out of
scope.

## How to use this

For the wiki and any Rossmann-facing write-up, lead with pillar 1 (GPL
source, non-disclaimable), support with pillar 2 (the 3D documentation
gap, hardware feature, Sony's own words), and frame pillar 3 as consumer
rights rather than breach. Attributing a motive to Sony is unnecessary
and refutable; the documents plus reproducible behavior carry it.

## Related

- [licence-basis.md](licence-basis.md) — the GPL package list and license basis
- [oss-source-recovery.md](oss-source-recovery.md) — the sources are gone
- [3d-blocked-in-browser.md](3d-blocked-in-browser.md) — the 3D feature gap
- [right-to-repair.md](right-to-repair.md)
