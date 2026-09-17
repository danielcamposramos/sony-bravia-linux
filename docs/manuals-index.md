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

**Verified in a browser, 2026-09-17.** Two different things live at
Sony, and it matters which one you link:

**1. The direct PDF (what you want).**

```
https://www.sony.com/electronics/support/res/manuals/<FIRST-4-OF-DOCID>/<DOCID>.pdf
```

e.g. `42730121M` → `.../manuals/4273/42730121M.pdf`. These resolve to the
actual file. The operating instructions for the KDL-46EX725 are listed
there at **4.25 MB, release date 15/02/2019** — Sony was still publishing
revisions seven years after the set shipped, and the size matches our
offline copy (4 452 072 bytes) exactly.

**2. The per-model support page (the human entry point).**

```
https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/<model>/manuals
https://www.sony.com/electronics/support/televisions-projectors-lcd-tvs/<model>/manuals
```

Confirmed loading for both `kdl-46ex725` and `kdl-46hx855`, **URL stable
— no redirect**, each listing its PDFs with release dates.

**A warning for anyone automating this.** Sony's WAF blocks non-browser
clients, and it does so with **HTTP 200 and a 63 KB "Access Denied"
body** — not a 403, not a 404. An earlier pass here probed exactly the
correct `res/manuals/4273/…` URL and recorded it as dead, because the
status code said success and only a human with a browser could tell the
difference. Check the *content*, not the status, and confirm anything
important in a real browser.

(`docs.sony.com/release/<DOCID>.pdf` also answers for these document
numbers, but it is **RefLib**, a Blazor single-page app — a browser
renders a viewer there; a fetcher gets the app shell. Prefer the
`res/manuals/` route above for linking.)

## Sony-published documents — link to these

Sony's own document numbers. **Link here; do not redistribute.** Our
copies exist only so the repair information survives a takedown.

| Document | Sony doc no. | Model | Direct PDF (verified pattern) |
|---|---|---|---|
| Operating instructions (pt-BR) | `42730121M` | KDL-46EX725 | [res/manuals/4273/42730121M.pdf](https://www.sony.com/electronics/support/res/manuals/4273/42730121M.pdf) |
| Manual (pt-BR) | `W0012720M` | KDL-46HX855 | [res/manuals/W001/W0012720M.pdf](https://www.sony.com/electronics/support/res/manuals/W001/W0012720M.pdf) |
| i-Manual | `W0005743M` | KDL-46HX855 | [res/manuals/W000/W0005743M.pdf](https://www.sony.com/electronics/support/res/manuals/W000/W0005743M.pdf) |
| Licence agreement | `44119961M` | KDL-46HX855 | [res/manuals/4411/44119961M.pdf](https://www.sony.com/electronics/support/res/manuals/4411/44119961M.pdf) |

Per-model support pages (browser-verified, URL stable):

- KDL-46EX725 — [sony.com.br/…/kdl-46ex725/manuals](https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-46ex725/manuals)
- KDL-46HX855 — [sony.com.br/…/kdl-46hx855/manuals](https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx855/manuals)

Entry points, if a document number is ever withdrawn:

- Brazil — `https://www.sony.com.br/electronics/support`
- Global — `https://www.sony.com/electronics/support`
- Open-source licence notices — `https://oss.sony.net/`

## Per-model support pages (all regions)

One row per model, one column per region — the centralised entry point.
Pattern, confirmed in a browser for the two marked **✔**:

```
https://<region-host>/electronics/support/televisions-projectors-lcd-tvs/<model-slug>/manuals
```

Region hosts: `www.sony.com.br` (BR) · `www.sony.com` (US) · `www.sony.co.uk` (UK) · `www.sony.de` (DE) · `www.sony.fr` (FR) · `www.sony.es` (ES).
Not every model was sold in every region, so some combinations will 404 —
that is a distribution fact, not a broken pattern.

### AZ2-F generation (2011) — one chassis, five sizes

| Model | Support pages by region |
|---|---|
| `KDL-32EX725` | [BR](https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-32ex725/manuals) | [US](https://www.sony.com/electronics/support/televisions-projectors-lcd-tvs/kdl-32ex725/manuals) | [UK](https://www.sony.co.uk/electronics/support/televisions-projectors-lcd-tvs/kdl-32ex725/manuals) | [DE](https://www.sony.de/electronics/support/televisions-projectors-lcd-tvs/kdl-32ex725/manuals) | [FR](https://www.sony.fr/electronics/support/televisions-projectors-lcd-tvs/kdl-32ex725/manuals) | [ES](https://www.sony.es/electronics/support/televisions-projectors-lcd-tvs/kdl-32ex725/manuals) |
| `KDL-40EX725` | [BR](https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-40ex725/manuals) | [US](https://www.sony.com/electronics/support/televisions-projectors-lcd-tvs/kdl-40ex725/manuals) | [UK](https://www.sony.co.uk/electronics/support/televisions-projectors-lcd-tvs/kdl-40ex725/manuals) | [DE](https://www.sony.de/electronics/support/televisions-projectors-lcd-tvs/kdl-40ex725/manuals) | [FR](https://www.sony.fr/electronics/support/televisions-projectors-lcd-tvs/kdl-40ex725/manuals) | [ES](https://www.sony.es/electronics/support/televisions-projectors-lcd-tvs/kdl-40ex725/manuals) |
| `KDL-46EX725` ✔ | [BR](https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-46ex725/manuals) | [US](https://www.sony.com/electronics/support/televisions-projectors-lcd-tvs/kdl-46ex725/manuals) | [UK](https://www.sony.co.uk/electronics/support/televisions-projectors-lcd-tvs/kdl-46ex725/manuals) | [DE](https://www.sony.de/electronics/support/televisions-projectors-lcd-tvs/kdl-46ex725/manuals) | [FR](https://www.sony.fr/electronics/support/televisions-projectors-lcd-tvs/kdl-46ex725/manuals) | [ES](https://www.sony.es/electronics/support/televisions-projectors-lcd-tvs/kdl-46ex725/manuals) |
| `KDL-55EX725` | [BR](https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-55ex725/manuals) | [US](https://www.sony.com/electronics/support/televisions-projectors-lcd-tvs/kdl-55ex725/manuals) | [UK](https://www.sony.co.uk/electronics/support/televisions-projectors-lcd-tvs/kdl-55ex725/manuals) | [DE](https://www.sony.de/electronics/support/televisions-projectors-lcd-tvs/kdl-55ex725/manuals) | [FR](https://www.sony.fr/electronics/support/televisions-projectors-lcd-tvs/kdl-55ex725/manuals) | [ES](https://www.sony.es/electronics/support/televisions-projectors-lcd-tvs/kdl-55ex725/manuals) |
| `KDL-60EX725` | [BR](https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-60ex725/manuals) | [US](https://www.sony.com/electronics/support/televisions-projectors-lcd-tvs/kdl-60ex725/manuals) | [UK](https://www.sony.co.uk/electronics/support/televisions-projectors-lcd-tvs/kdl-60ex725/manuals) | [DE](https://www.sony.de/electronics/support/televisions-projectors-lcd-tvs/kdl-60ex725/manuals) | [FR](https://www.sony.fr/electronics/support/televisions-projectors-lcd-tvs/kdl-60ex725/manuals) | [ES](https://www.sony.es/electronics/support/televisions-projectors-lcd-tvs/kdl-60ex725/manuals) |

### AZ3F generation (2012)

| Model | Support pages by region |
|---|---|
| `KDL-46HX855` ✔ | [BR](https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx855/manuals) | [US](https://www.sony.com/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx855/manuals) | [UK](https://www.sony.co.uk/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx855/manuals) | [DE](https://www.sony.de/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx855/manuals) | [FR](https://www.sony.fr/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx855/manuals) | [ES](https://www.sony.es/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx855/manuals) |
| `KDL-40HX853` | [BR](https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-40hx853/manuals) | [US](https://www.sony.com/electronics/support/televisions-projectors-lcd-tvs/kdl-40hx853/manuals) | [UK](https://www.sony.co.uk/electronics/support/televisions-projectors-lcd-tvs/kdl-40hx853/manuals) | [DE](https://www.sony.de/electronics/support/televisions-projectors-lcd-tvs/kdl-40hx853/manuals) | [FR](https://www.sony.fr/electronics/support/televisions-projectors-lcd-tvs/kdl-40hx853/manuals) | [ES](https://www.sony.es/electronics/support/televisions-projectors-lcd-tvs/kdl-40hx853/manuals) |
| `KDL-55HX753` | [BR](https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-55hx753/manuals) | [US](https://www.sony.com/electronics/support/televisions-projectors-lcd-tvs/kdl-55hx753/manuals) | [UK](https://www.sony.co.uk/electronics/support/televisions-projectors-lcd-tvs/kdl-55hx753/manuals) | [DE](https://www.sony.de/electronics/support/televisions-projectors-lcd-tvs/kdl-55hx753/manuals) | [FR](https://www.sony.fr/electronics/support/televisions-projectors-lcd-tvs/kdl-55hx753/manuals) | [ES](https://www.sony.es/electronics/support/televisions-projectors-lcd-tvs/kdl-55hx753/manuals) |
| `KDL-46HX750` | [BR](https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx750/manuals) | [US](https://www.sony.com/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx750/manuals) | [UK](https://www.sony.co.uk/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx750/manuals) | [DE](https://www.sony.de/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx750/manuals) | [FR](https://www.sony.fr/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx750/manuals) | [ES](https://www.sony.es/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx750/manuals) |

**✔ = browser-verified 2026-09-17** (page loads, URL stable, PDFs listed and
resolving). The rest follow the same pattern; the AZ3F rows beyond the HX855
are from the board-census sibling list in [platform-map.md](platform-map.md)
and their generation assignment is inferred, not confirmed from a manual.

## Audio-system support pages

The same treatment as the televisions, for the 81 products the Home
Theatre Control widget can drive ([full list in the README](../README.md#sony-audio-systems-hdmi-cec)). Sony, to their credit, kept
this documentation online: manuals for hardware from 2009 are still
published, and the KDL-46EX725 instructions carry a **2019** revision
date. The criticism in [withheld-by-catalog.md](withheld-by-catalog.md)
is narrow and deserves to stay narrow — it is about a catalog that gated
finished, already-localized features by country, not about Sony
documentation practice, which has held up better than most.

Support-page pattern, same shape as the TVs:

```
https://<region-host>/electronics/support/<category-slug>/<model-slug>
```

Category slugs below were recovered from archived Sony support URLs
(their WAF blocks direct probing). The model slug is the model name
lowercased — e.g. `speakers-home-speakers/apm-22es` is a real archived
example of the shape.

### Sound bars

Category: `sound-bars-home-theater-systems-sound-bars` — **slug confirmed from archived URLs**

| Model | BR | US |
|---|---|---|
| `HT-CT150` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct150) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct150) |
| `HT-CT350` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct350) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct350) |
| `HT-CT370` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct370) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct370) |
| `HT-CT380` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct380) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct380) |
| `HT-CT381` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct381) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct381) |
| `HT-CT550W` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct550w) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct550w) |
| `HT-CT660` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct660) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct660) |
| `HT-CT770` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct770) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct770) |
| `HT-CT780` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct780) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct780) |
| `HT-CT790` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct790) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct790) |
| `HT-CT800` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct800) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-ct800) |
| `HT-ST3` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-st3) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-st3) |
| `HT-ST5` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-st5) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-st5) |
| `HT-ST7` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-st7) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-st7) |
| `HT-ST9` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-st9) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-st9) |
| `HT-ST5000` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-st5000) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-st5000) |
| `HT-XT1` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-xt1) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-xt1) |
| `HT-XT2` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-xt2) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-xt2) |
| `HT-XT3` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-xt3) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-xt3) |
| `HT-XF9000` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-xf9000) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-xf9000) |
| `HT-X9000F` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-x9000f) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-x9000f) |
| `HT-NT3` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-nt3) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-nt3) |
| `HT-NT5` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-nt5) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-nt5) |
| `HT-MT500` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-mt500) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-mt500) |
| `HT-RT5` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-rt5) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-rt5) |
| `HT-Z9F` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-z9f) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-z9f) |
| `HT-ZF9` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-zf9) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-zf9) |
| `HT-S200F` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-s200f) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-s200f) |
| `HT-SF200/201` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-sf200-201) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars/ht-sf200-201) |

### Blu-ray home theatre systems

Category: `sound-bars-home-theater-systems-blu-ray-home-theater-systems` — **slug confirmed from archived URLs**

| Model | BR | US |
|---|---|---|
| `RHT-G5` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/rht-g5) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/rht-g5) |
| `RHT-G10` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/rht-g10) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/rht-g10) |
| `RHT-G10EX` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/rht-g10ex) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/rht-g10ex) |
| `RHT-G11` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/rht-g11) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/rht-g11) |
| `RHT-G15` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/rht-g15) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/rht-g15) |
| `HT-SS370/SF470` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/ht-ss370-sf470) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/ht-ss370-sf470) |
| `HT-SS380` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/ht-ss380) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/ht-ss380) |
| `HT-FS30` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/ht-fs30) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/ht-fs30) |
| `HT-AS5/AF5` | [BR](https://www.sony.com.br/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/ht-as5-af5) | [US](https://www.sony.com/electronics/support/sound-bars-home-theater-systems-blu-ray-home-theater-systems/ht-as5-af5) |

### Receivers & amplifiers

**Category slug not yet confirmed.** No archived URL for this
family surfaced in the searches run on 2026-09-17, and Sony's WAF
prevents probing candidates directly. Use the model search until
someone confirms it in a browser:

- BR — `https://www.sony.com.br/electronics/support` → search the model
- US — `https://www.sony.com/electronics/support` → search the model

Models in this family: `STR-DH520`, `STR-DH530`, `STR-DH540`, `STR-DH550`, `STR-DH590`, `STR-DH710`, `STR-DH720`, `STR-DH730`, `STR-DH740`, `STR-DH750`, `STR-DH770`, `STR-DH790`, `STR-DH820`, `STR-DH830`, `STR-DN840`, `STR-DN850`, `STR-DN860`, `STR-DN1020`, `STR-DN1030`, `STR-DN1040`, `STR-DN1050`, `STR-DN1060`, `STR-DN1070`, `STR-DN1080`, `STR-DN2030`, `STR-DA1800ES`, `STR-DA2800ES`, `STR-DA3700ES`, `STR-DA5700ES`, `STR-DA5800ES`, `STR-ZA810ES`, `STR-ZA1000ES`, `STR-ZA1100ES`, `STR-ZA2000ES`, `STR-ZA2100ES`, `STR-ZA3000ES`, `STR-ZA3100ES`, `STR-ZA5000ES`, `TA-DA3600ES`, `TA-DA5600ES`, `TA-DA5700ES`, `TA-DA5800ES`

### Wireless headphones

**Category slug not yet confirmed.** No archived URL for this
family surfaced in the searches run on 2026-09-17, and Sony's WAF
prevents probing candidates directly. Use the model search until
someone confirms it in a browser:

- BR — `https://www.sony.com.br/electronics/support` → search the model
- US — `https://www.sony.com/electronics/support` → search the model

Models in this family: `MDR-HW700DS`

**Region hosts** are the same as for the televisions (`sony.com.br`, `sony.com`, `sony.co.uk`, `sony.de`, `sony.fr`, `sony.es`); a model not sold in a region will 404 there.

**None of these links is browser-verified.** They are pattern-derived from
confirmed category slugs, and marked as such deliberately — the same
discipline that caught a valid Sony URL being recorded as dead earlier
today. One spot-check in a browser would promote the lot.
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
- **Firmware** — the archive holds update packages for 2011 and 2012
  platforms; their Sony download pages are not indexed on this page yet.
