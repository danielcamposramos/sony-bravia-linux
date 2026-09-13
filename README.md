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

- `firmware/` — official Sony update packages (encrypted, `*_auth.zip`)
  - `KDL-46HX855/` — `sony_tvupdate_2012_2120_bra_auth.zip` (PKG2.120BRA,
    95 MB image, `sony_dtv0FA20A02A0A2_00001400`) and
    `sony_tvupdate_2011_4027_bra_auth.zip` (PKG4.027BRA, 68 MB image,
    `sony_dtv0FA10A01A0A1_00000400` — the EX725's package)
  - `siblings/` — 4 regional sibling builds from Wayback (BRB/GAA/AAA)
    forming a 6-image differential corpus
  - `extracted/` — uncompressed copies of the images (gitignored, regenerable)
- `manuals/` — service manual (AZ3F chassis), user manual, iManual, OSS license
  agreements, unit photos
- `docs/` — [platform map](docs/platform-map.md),
  [feasibility roadmap](docs/feasibility-roadmap.md),
  [right-to-repair context](docs/right-to-repair.md),
  research notes (`docs/research/`, incl. live LAN recon artifacts)
- `tools/` — extraction/analysis tooling and notes

## Current status

Raw materials imported and attributed. Platform identified (MIPS mipsel
"ATREYU" SoC, glibc 2.7 userland, DirectFB/Qt/Opera, Linux 2.6.35-era
kernel). Firmware containers confirmed whole-file encrypted (no public
decryptor). Live CERS/IRCC + UPnP API documented. Full analysis in
`docs/platform-map.md`; staged plan (zero-mod content → UART root → kernel
modernization) in `docs/feasibility-roadmap.md`.

## Legal note

This project studies devices the author owns. Firmware images are Sony
copyright material kept here for personal research; nothing here bypasses or
redistributes DRM-protected content.