# Documentation index — where the manuals are, and where our copies came from

**2026-09-17.** Two jobs in one page:

1. **Point at Sony's own documents.** Linking to a manufacturer's public
   documentation is lawful and normal; this page does that and hosts
   nothing.
2. **Record provenance**, because it decides what may be shared. Our
   offline copies split cleanly into documents Sony published under their
   own document numbers, and service manuals that came from third-party
   archives — never from Sony. That distinction is the whole point of the
   table below.

Nothing is hosted here. Rule 9b stands: the offline library is the
owner's, it exists so that a Sony takedown does not erase a repair
document, and any decision to *distribute* belongs to the right-to-repair
movement, not to this project.

## How Sony serves these documents

Sony's document library is **RefLib** at `docs.sony.com`, a Blazor
WebAssembly single-page app. Every document has a Sony document number
(the `…M` identifier), and the app resolves it at:

```
https://docs.sony.com/release/<DOCID>.pdf
```

Those routes answer for all four of our Sony-numbered documents. Note the
path ends in `.pdf` but returns the SPA shell to a plain HTTP client —
**a browser renders it and downloads the document; `curl` gets the app,
not the file.** That is a property of their viewer, not a broken link.

Per-model support pages follow:

```
https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/<model>/manuals
https://www.sony.com/electronics/support/televisions-projectors-lcd-tvs/<model>/manuals
```

**Unverified from here:** Sony's WAF returns an "Access Denied" page — at
HTTP **200**, 63 KB, which is worth knowing because it looks like success
to a naive fetcher. These patterns need confirming in a real browser
before anyone trusts them. Flagged rather than asserted, per the
[check-before-declaring rule](generation-model-map.md#rule-check-the-archive-before-declaring-a-service-dead).

## Sony-published documents — link to these

Sony's own document numbers. **Link here; do not redistribute.** Our
copies exist only so the repair information survives a takedown.

| Document | Sony doc no. | Model | Sony link |
|---|---|---|---|
| Operating instructions (pt-BR) | `42730121M` | KDL-46EX725 | [docs.sony.com/release/42730121M.pdf](https://docs.sony.com/release/42730121M.pdf) |
| Manual (pt-BR) | `W0012720M` | KDL-46HX855 | [docs.sony.com/release/W0012720M.pdf](https://docs.sony.com/release/W0012720M.pdf) |
| i-Manual | `W0005743M` | KDL-46HX855 | [docs.sony.com/release/W0005743M.pdf](https://docs.sony.com/release/W0005743M.pdf) |
| Licence agreement | `44119961M` | KDL-46HX855 | [docs.sony.com/release/44119961M.pdf](https://docs.sony.com/release/44119961M.pdf) |

Entry points, if a document number is ever withdrawn:

- Brazil — `https://www.sony.com.br/electronics/support`
- Global — `https://www.sony.com/electronics/support`
- Open-source licence notices — `https://oss.sony.net/`

## Service manuals — NOT from Sony

Sony does not publish service manuals to the public. **Every file below
came from third-party technical archives**, which is precisely why they
are the material the right-to-repair movement cares about: schematics,
board layouts and part numbers are what make a set repairable, and they
are the first thing to disappear.

| File | Covers | Size |
|---|---|---|
| `sony_kdl-32ex725_40ex725_46ex725_55ex725_chassis_az2-f_rev.0_level3_sm.pdf` | KDL-32/40/46/55EX725 — AZ2-F, level 3 | 16 MB |
| `sony_kdl-32ex725_40ex725_46ex725_55ex725_chassis_az2-f_ver.1.0_segm.3a-2_sm.pdf` | same, SEGM.3A-2 v1.0 | 11 MB |
| `sony_kdl-32ex725_40ex725_46ex725_55ex725_chassis_az2-f_ver.2.0_segm.3a-2_sm.pdf` | same, v2.0 | 13 MB |
| `sony_kdl-46ex725_chassis_az2f_sm.pdf` | KDL-46EX725 — AZ2-F, full | 27 MB |
| `sony_kdl-60ex725_chassis_az2-f_sch.pdf` | KDL-60EX725 — AZ2-F schematics | 8.7 MB |
| `sony_kdl_46hx855_az3f_chassis_sm.pdf` | KDL-46HX855 — AZ3F | 26 MB |

**Coverage note, which is the useful part:** one AZ2-F service manual
covers **four sizes** (32/40/46/55) with a fifth (60) in its own
schematic set. This is the documentary proof behind the
[generation-level scope](generation-model-map.md) — Sony engineered and
documented by chassis, not by model.

Integrity, so a future copy can be checked against ours (SHA-256, first
16 hex):

```
77f1d708f7ddc45f  42730121M.pdf
80bb029593c97434  Manual W0012720M.pdf
d8c71a1362eae031  iManual W0005743M.pdf
031b6c5531cba044  Acordo de Licença 44119961M.pdf
c6e7c773acb29ffd  …az2-f_rev.0_level3_sm.pdf
ccb3cad1089dcdf4  …az2-f_ver.1.0_segm.3a-2_sm.pdf
d0efa2887273de35  …az2-f_ver.2.0_segm.3a-2_sm.pdf
16b70a8393d4a20f  sony_kdl-46ex725_chassis_az2f_sm.pdf
2f30ddd8a23415d9  sony_kdl-60ex725_chassis_az2-f_sch.pdf
331f128a43f2fb0d  sony_kdl_46hx855_az3f_chassis_sm.pdf
```

## What goes to the right-to-repair movement

Three buckets, and only one of them is ours to offer:

| Bucket | Contents | Disposition |
|---|---|---|
| **Sony-published** | the four `…M` documents above | **link only** — Sony hosts them; we keep copies purely as takedown insurance |
| **Third-party service manuals** | the six files above | **the movement's material** — already circulating outside Sony, and the documents that actually enable repair |
| **Recovered platform material** | AppliCast bundles, catalogs, assets ([withheld-by-catalog.md](withheld-by-catalog.md)) | held offline; distribution is the movement's call, per rule 9b |

## Gaps

- **AZ3F coverage beyond 46"** — we hold only the KDL-46HX855 manual. The
  AZ3F family certainly spans more sizes; their manuals are not in the
  library.
- **AZ1 (2010)** — no manual held at all, for a generation whose widget
  catalog is [still live](generation-model-map.md#what-az1-actually-got).
- **Support-page URLs** — pattern recorded, blocked from verification
  here, needs a browser check.
- **Firmware** — the archive holds update packages for 2011 and 2012
  platforms; their Sony download pages are not indexed on this page yet.
