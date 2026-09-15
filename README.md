# sony-bravia-linux

Reverse-engineering and software porting for **Sony BRAVIA KDL-era TVs** — the
pre-Android, Linux-based BRAVIA platform (~2005–2015). Goal: understand the
platform well enough to run third-party software on it (e.g. VLC) and unlock
more internet content than the stock firmware allows.

## Repository scope — what is and isn't here

This public repo contains **only our own work**: research notes, protocol
captures from our own TVs, analysis, and tooling (the Serviio 3D fix, SEI
injector, ffmpeg wrapper). **No Sony-distributed material is hosted here** —
no firmware images, service manuals, widget packages, or Sony-server
sweeps. Those resources were gathered for research and are kept offline by
the owner; the right-to-repair plan for that material is in
[docs/right-to-repair.md](docs/right-to-repair.md). Some older research
notes may still reference those filenames — they refer to the owner's
offline archive, not to anything in this repository.

## Why bother (the right-to-repair angle)

These late-KDL sets are phenomenal hardware — the KDL-46HX855 has
X-Reality PRO with 12-bit color processing and active 3D, and picture
quality that still embarrasses many modern budget panels. Sony EOL'd the
platform: smart services shut down, firmware downloads removed (Jan
2022), even the GPL source downloads were deleted from Sony's site. The
owner is now the only party with any incentive to keep this hardware
alive. This project is right-to-repair work: document, control, and
eventually run owner-chosen software on owner-owned hardware. See
[docs/right-to-repair.md](docs/right-to-repair.md) (includes the Louis
Rossmann / repair.wiki / FULU Foundation sharing plan).

## Test hardware (both on the LAN, DHCP-pinned by MAC)

| Model | Year | Chassis | LAN IP |
|---|---|---|---|
| KDL-46HX855 | 2012 | AZ3F (main SoC codename "ATREYU") | 192.168.0.21 |
| KDL-46EX725 | 2011 | AZ2-F ("BATV" board) | 192.168.0.22 |

## Repository layout

- `docs/` — **[project status & partner guide](docs/project-status.md)**
  (read this first), [platform map](docs/platform-map.md),
  [feasibility roadmap](docs/feasibility-roadmap.md),
  [right-to-repair context](docs/right-to-repair.md),
  research notes (`docs/research/`, incl. live LAN recon artifacts),
  repair.wiki page drafts (`docs/wiki/`)
- `tools/` — extraction/analysis tooling and notes: the
  [tv-mediabrowser](tools/serviio/tv-mediabrowser/README.md) media app
  (live on the owner's LAN), Serviio renderer profiles + 3D fix,
  the SEI 3D injector, the rd1 portal, and the [systemd
  stack](tools/systemd/README.md) that runs it all
- `certs/` — CA + leaf certificates for the era-TLS lanes

Firmware images, service manuals, and Sony-distributed widget
packages are **not hosted here** — they live in the owner's offline
private archive (see the scope note above and the private-material
section of the partner guide).

## Current status

**The media experience is live and owner-verified (2026-09-15):** both
TVs browse the full library on the LAN media server and play every
audio format and every major video format, via a systemd-managed stack
with a config file. See
[docs/project-status.md](docs/project-status.md) — the single partner
entry point, kept current.

Research continues: platform identified (MIPS mipsel "ATREYU" SoC,
glibc 2.7 userland, DirectFB/Qt/Opera, Linux 2.6.35-era kernel),
firmware containers confirmed whole-file encrypted (no public
decryptor), live CERS/IRCC + UPnP API documented. Full analysis in
`docs/platform-map.md`; staged plan (zero-mod content → UART root →
kernel modernization) in `docs/feasibility-roadmap.md`.

## Legal note

This project studies devices the author owns. Sony-distributed material
(firmware images, service manuals, widget packages) referenced by older
research notes is kept in the owner's offline private archive — never in
this repository. Nothing here bypasses or redistributes DRM-protected
content.