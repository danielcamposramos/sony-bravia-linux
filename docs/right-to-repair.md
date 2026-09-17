# Right to Repair context

## Why this project exists

The KDL-era BRAVIAs (2005–2015) are among the best displays Sony ever
shipped. The two units this project studies are a KDL-46HX855 (2012,
X-Reality PRO, 12-bit color processing, active 3D, Opera/HbbTV smart
platform) and a KDL-46EX725 (2011). Their picture quality is still
excellent — arguably better in motion handling and 3D than many modern
budget panels.

Sony, however, has fully end-of-lifed them:

- **Smart services shut down** — BRAVIA Internet Video, the Opera widget
  store, Media Remote servers: dead. A TV with perfectly good networking
  hardware ships with apps that can never work again.
- **Firmware distribution terminated** (2022-01-31 per Sony's own
  notices; download links removed). Final firmware: PKG2.120BRA
  (HX855), PKG4.027BRA (EX725).
- **GPL source downloads removed** — the linux-kernel tarballs for these
  exact model groups (KDL-46HX750 / KDL-32CX520 pages) were deleted from
  Sony's Source Code Distribution Service and were never captured by
  web archives. Only a per-request inquiry form remains.
- **No parts/documentation channel** for the 2010s boards, and the
  platform is undocumented (in-house Sony CXD4727GB "X-Reality" SoC, no
  public datasheet).

This is the textbook right-to-repair situation: the owner is the only
party with any incentive to keep this hardware useful, and the
manufacturer has made that harder than it needs to be. This repo exists
to change that: document the platform, keep it usable as media
endpoints, and eventually run owner-chosen software on it.

## Repair-rights angle of each workstream

| Workstream | R2R relevance |
|---|---|
| Live CERS/IRCC API docs | The official remote apps are discontinued; our LAN control docs keep the TV controllable by its owner without any Sony infrastructure |
| GPL source recovery | Sony is legally obligated to provide GPL sources on request for as long as the binaries are offered; we pursue that (OSS inquiry form) — enforcement of GPL is consumer protection |
| Firmware container analysis | Post-EOL, the owner can't re-flash or verify a set without relying on downloaded copies; understanding the container (and Sony's key management) is repair knowledge, and is done on devices we own |
| Service manual + schematics | These are being preserved and shared as they should be for any owner-repairable device |
| VLC / media software port | Restoring functionality the manufacturer disabled by abandonment |

## The community we should share findings with

- **Repair Preservation Group / repair.wiki** (Louis Rossmann's 501(c)(3)) — concrete outreach plan now in [rossmann-outreach.md](rossmann-outreach.md) (verified contact paths, wiki entry points, archive handover offer)
  — https://repair.wiki — community-editable repair knowledge base;
  a good home for the board-level/service-mode findings
  (older mirror: https://old.repair.wiki)
- **Rossmann Repair Group** — https://rossmanngroup.com (and
  https://rossmanngroup.com/louis-rossmann); YouTube:
  https://www.youtube.com/@rossmanngroup
- **Fight to Repair** (501(c)(4) action fund) — https://fighttorepair.org
- **FULU Foundation** — https://consumerrights.wiki (with Rossmann
  Repair Group): documents bricked/abandoned products and runs a
  **Repair Bounty Program** paying developers to bypass anti-consumer
  locks on discontinued hardware. A dead smart-TV platform with
  encrypted EOL firmware is squarely in their scope — when this project
  produces results (platform map, decrypted container, or a working VLC
  port), share it there.

## Ethics / scope note

Everything in this repo is performed on hardware the contributors own,
for the purpose of repair, preservation, and interoperability — not
content piracy (no DRM circumvention for protected media) and not
attacking anyone else's devices. Sony firmware images stored here are
for archival/research purposes.

## Abandonment is the argument (2026-09-17)

The strongest form of the case, stated by the owner while we were mapping
Sony's still-live servers:

> *"If the 'owner' abandons something, it's abandoned."*

It is worth being precise about what that does and does not claim here,
because this project has now measured both sides of it.

**Where Sony did not abandon anything:** their documentation. Manuals for
2009 audio hardware are still published; the KDL-46EX725 operating
instructions carry a **2019 revision date**, eight years after the set
shipped. The AppliCast CDN is still serving widget bundles and catalogs
in 2026 — one AZ1 catalog is dated **2010-04-21** and still answers.
Credit where it is due: on paperwork and hosting, Sony has outlasted most
of the industry. See [manuals-index.md](manuals-index.md).

**Where the abandonment is real:** the services those files point at. The
smart portal is gone, the Opera Store lane is unreachable, the map APIs
a 2010 widget depends on have disappeared — and, worst of the set,
features that were **finished, localized and paid for** were withheld by
a per-country catalog and then simply left dark
([withheld-by-catalog.md](withheld-by-catalog.md)).

So the argument is not "Sony are bad stewards". It is narrower and
harder to answer: **a company that stops operating a service does not
thereby get to keep the functionality switched off on hardware someone
else owns.** A widget whose code, artwork and Portuguese translation all
still exist on the manufacturer's own CDN is not a discontinued product.
It is a working feature behind a file nobody is serving — and on a
private LAN, serving that file is repair.

Ten-plus years later, things change and companies move on. That is
expected, and it is precisely why the right to repair cannot depend on
the manufacturer still caring.
