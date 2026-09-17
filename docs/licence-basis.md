# The licence basis — what the platform is built on, and what that grants

**2026-09-17.** These televisions run Linux. That is not incidental
trivia; it is the legal and practical ground this project stands on, and
Sony documented it themselves. This page records the facts and is
careful to stop where the facts stop.

**Not legal advice.** Nobody here is a lawyer. What follows is an
evidence file: what the software is, what licence it carries, what Sony
published about it, and what is verifiable today. Conclusions are for
people qualified to draw them.

## 1. The platform is GPL software

The sets run **Linux 2.6.35** with a GPL/LGPL userland (DirectFB, Qt,
glibc-era components — see [platform-map.md](platform-map.md)).

Sony's own source drop for this kernel is in the owner's archive:
**35,727 files**, with `COPYING` — the GNU General Public License — at
the root of the tree, plus per-component licences throughout
(`fs/jffs2/LICENCE`, `drivers/net/LICENSE.SRC`, and others). Sony
shipped the licence text with the source, as the licence requires.

## 2. Sony operates a Source Code Distribution Service — still, in 2026

`oss.sony.net` is live today. Its own description:

> *"This home page is prepared for the people who are interested in
> receiving source code for Sony products with Linux and other open
> source software whose license requires the provision of source code. A
> copy of such source code also can be obtained from us on physical
> media for a period of three years after our last shipment of this
> product…"*

Sony is explicit that the obligation exists and that they honour it.
The service indexes thousands of products across TV, Audio, A/V
Receiver, Blu-ray, Camera and professional lines.

## 3. The precise finding: our generation is no longer listed

Sony's live TV listings carry **798 `KDL-` models**. Counted by series:

| Present | Absent |
|---|---|
| `W6xxA`, `W8xxA`, `W9xxA`, `W6xxB`, `W8xxB`, `R3xxC`, `R5xxC`, `W8xxC`, `WD6xx`, `WD7xx`, `WE6xx`, `WF6xx`, `WG6xx` … (2013 onward) | **`EX`, `HX`, `NX`, `CX` — zero entries** |

**Zero models from the 2010–2012 EX/HX/NX/CX generation appear in Sony's
current source listings.** The oldest series present are 2013-era. By
Sony's own stated term — three years after last shipment — these have
aged out of the offer.

Stated plainly, without inference: *Sony still runs the service; our
sets are no longer in it.*

## 4. What the licence grants the owner, and when that lapses

This is the part that matters for repair, and it is worth separating
from the distribution question.

The GPL grants rights **to the person who received the software** — the
freedom to run it, study it, modify it, and run the modified version.
Those grants are made by the licence itself, on receipt, as a condition
of the distribution that already happened. They are not a service Sony
provides and can withdraw; they came with the television.

What *does* have a time limit is the **offer to supply source to third
parties** (the three-year written-offer term Sony's page describes).
That is a distribution obligation. Its expiry says nothing about what a
person who already owns the product may do with the software on it.

So the asymmetry this project keeps running into has a licence-shaped
explanation: the services died, the distribution offer aged out, and the
**rights that came with the hardware did not.**

## 5. Where the GPL does *not* reach — and why we respect that line

The licence argument covers the platform. It does **not** cover
everything on these sets, and conflating the two would discredit the
rest:

| Component | Licence | What we do |
|---|---|---|
| Linux kernel, GPL userland | GPL/LGPL | study, document, and (per the roadmap) run modified software on owner hardware |
| Sony's widget bundles (`widget.js`, layouts, artwork, dictionaries) | **Sony copyright, not GPL** | preserved offline, **never redistributed** from this repo (rules 9 / 9b); served only on the owner's own LAN to the owner's own TVs |
| Firmware images, service manuals | Sony copyright / third-party | offline archive only; manuals are **linked**, not hosted ([manuals-index.md](manuals-index.md)) |
| `digest.sig` signature scheme | Sony key material | never forged, never circumvented — documented and respected ([appliwidget-programming.md §4](research/appliwidget-programming.md)) |
| Our own code and reconstructions | ours | published openly, e.g. the [World Clock schema](worldclock-schema-reconstruction.md) |

That last row is why the signature wall gets documented rather than
attacked, and why a recovered bundle stays in a private archive while
the *analysis* is public. The GPL gives us the platform. It does not
give us Sony's widgets, and we have not claimed otherwise anywhere.

## 6. The infrastructure runs on it too

Worth noting for the symmetry: the servers that served these TVs — the
AppliCast CDN, the catalog trees, the distribution endpoints — are
themselves Linux infrastructure, as is the LAN server that now replaces
them. The stack that Sony switched off and the stack the owner runs in
its place are the same kind of thing. What changed is who operates it.

## 7. For the right-to-repair movement

The facts worth carrying forward, each independently checkable:

1. These televisions run GPL-licensed software, and Sony shipped the
   source with its licence text.
2. Sony maintains a Source Code Distribution Service to this day and
   states the obligation in their own words.
3. **No 2010–2012 EX/HX/NX/CX model remains in that service's listings**,
   while 798 later `KDL-` models do.
4. The services those sets depended on are gone, while the code and
   assets for some of those features are **still on Sony's own CDN**
   ([withheld-by-catalog.md](withheld-by-catalog.md)).
5. The owner's rights under the licence he received did not expire with
   any of it.

Checked 2026-09-17. Points 2 and 3 in particular are a listing away from
changing — if Sony re-adds the generation, that is worth recording as
readily as its absence.
