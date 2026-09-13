# sony-bravia-linux

Reverse-engineering and software porting for **Sony BRAVIA KDL-era TVs** — the
pre-Android, Linux-based BRAVIA platform (~2005–2015). Goal: understand the
platform well enough to run third-party software on it (e.g. VLC) and unlock
more internet content than the stock firmware allows.

## Test hardware (both on the LAN, DHCP-pinned by MAC)

| Model | Year | Chassis | LAN IP |
|---|---|---|---|
| KDL-46HX855 | 2012 | AZ3F | 192.168.0.21 |
| KDL-46EX725 | 2011 | (TBD) | 192.168.0.22 |

## Repository layout

- `firmware/` — official Sony update packages (encrypted, `*_auth.zip`)
  - `KDL-46HX855/` — `sony_tvupdate_2012_2120_bra_auth.zip` (95 MB image,
    `sony_dtv0FA20A02A0A2_00001400`) and `sony_tvupdate_2011_4027_bra_auth.zip`
    (68 MB image, `sony_dtv0FA10A01A0A1_00000400` — attribution to be confirmed,
    may target the EX725)
  - `extracted/` — uncompressed copies of the images (gitignored, regenerable)
- `manuals/` — service manual (AZ3F chassis), user manual, iManual, OSS license
  agreements, unit photos
- `docs/` — platform map, feasibility analysis, research notes
- `tools/` — extraction/analysis tooling and notes

## Current status

Raw materials imported. Platform identification and feasibility research in
progress — see `docs/` once written.

## Legal note

This project studies devices the author owns. Firmware images are Sony
copyright material kept here for personal research; nothing here bypasses or
redistributes DRM-protected content.