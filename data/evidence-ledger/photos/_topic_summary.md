# Run-34 visual evidence

These are Daniel Campos's original phone photographs from the Sony
KDL-46HX855 run-34 window on 2026-09-23. They are representative evidence,
not a photograph of every tested mode. Daniel observed every one of the 22
attempted run-34 steps display properly; modes the TV does not accept were not
counted as successful test cases.

The originals retain capture time and camera make/model so their relationship
to the contemporaneous log can be audited. `exiftool` reports no GPS latitude
or longitude in any file.

| File | EXIF time (-03) | Run-34 correlation | Visible content | SHA-256 |
|---|---:|---|---|---|
| `IMG-20260923-WA0030.jpeg` | 23:21:17 | `deep12 fmt=rgblimited`, begun 23:20:58 | `RGB LIMITED 12-BIT` test frame | `26e2959a324a10049ed68aea842f469014825287dc68194d8e513c8cd768def6` |
| `IMG-20260923-WA0033.jpeg` | 23:21:36 | `deep12 fmt=rgbauto`, begun 23:21:28 | BRAVIA OSD `[1080p HD] [12bit]` | `40c8c26058cd8f2307210340eeb4e7a85e2695b7eadceaf28ae1fe64d46dabe5` |
| `IMG-20260923-WA0037.jpeg` | 23:27:18 | `sbs bpc12 fmt=yuv444`, begun 23:26:58 | BRAVIA OSD `[1080p HD] [12bit] [3D]`; 3D menu says `3D: Sim` | `4d416db6004c384887b8f898a2428cfd9504b7c7a3a8cbcdd101e648dd0205f2` |

The time correlation identifies the active harness step; the photograph alone
does not expose the wire's chroma encoding. The canonical machine record is
`tools/stereo-modeset/run34-mohamed-branch-ycbcr-poc-hx855-2026-09-23.log`
(SHA-256
`60a204731237caceaa511b4b51f779b08282c26c9d7c6814c4084a7f382ca124`).
