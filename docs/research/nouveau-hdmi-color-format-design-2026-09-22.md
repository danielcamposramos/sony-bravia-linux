# nouveau HDMI output colour format and quantization range: design (2026-09-22)

Follow-on to the HDMI Deep Color series (v2, benched run25/run26). v2 is RGB
full-range only. This note designs the next series: limited/full RGB and
YCbCr 4:4:4, 4:2:2 and 4:2:0, at every depth the Deep Color work enabled.
Owner's directive: port the SDR deep-colour chroma formats from the open AMD
and proprietary NVIDIA examples; RGB is proven, the spec table carries the
other formats.

Evidence classes follow the awesome-linux-hdr ladder: **normative**,
**implemented** (readable source), **measured** (this bench), **proposed**.

## 1. uAPI: already upstream, nothing new to invent

- **`color format` connector property** (drm-misc-next): request enum
  `DRM_CONNECTOR_COLOR_FORMAT_{AUTO,RGB444,YCBCR444,YCBCR422,YCBCR420}`,
  attached with `drm_connector_attach_color_format_property(connector,
  supported_mask)`; core already forces a modeset when it changes
  (`drm_atomic_helper.c:742`). HDMI "AUTO" = RGB, falling back to 4:2:0 only
  for 4:2:0-only modes or when RGB bandwidth is unavailable. **Implemented** in
  amdgpu (`amdgpu_dm_connector.c` `amdgpu_dm_create_validate_stream_for_sink`,
  EDID-gated encoding mask) and in the bridge helpers.
- **`Broadcast RGB`** (`drm_connector_attach_broadcast_rgb_property`):
  Automatic / Full / Limited 16:235. Mainline policy
  (`drm_hdmi_state_helper.c` `hdmi_is_limited_range`): YCbCr is always
  limited; RGB Automatic = limited on CE video formats
  (`drm_default_rgb_quant_range`), full otherwise.
- **`max bpc`**: already attached by the Deep Color series.
- **TMDS rate**: `drm_hdmi_compute_mode_clock(mode, bpc, fmt)` — 4:2:2 is
  carried at the 8-bpc rate for any depth up to 12; 4:2:0 at half the pixel
  clock; RGB/4:4:4 scale by bpc/8 (**normative**: HDMI 1.0 §6.5, HDMI 2.0
  §7.1, both cited in the helper).
- **AVI**: `drm_hdmi_avi_infoframe_quant_range()`, `..._colorimetry()`, and
  `frame->colorspace = HDMI_COLORSPACE_{RGB,YUV444,YUV422,YUV420}`.

The running bench kernel (Debian 7.0.10) has `Broadcast RGB` and the rate
helper but **not** `color format`; the bench module therefore takes a
bench-only module parameter for the format request. The upstream series uses
the real property.

## 2. Hardware: the fields exist, nouveau never programs them

Nouveau today (`dispnv50/headc57d.c headc57d_procamp`, under a `//TODO:`)
hardcodes `PROCAMP COLOR_SPACE=RGB, DYNAMIC_RANGE=VESA` and never touches the
output CSC or clamp ranges. Result: always full-range RGB.

NVIDIA's open NVKMS (615.71.09, **implemented**, MIT) programs the same head
on Turing (C57D) / Ampere (C67D) / Ada:

| step | method | RGB full | RGB limited | YCbCr (444/422/420) |
|---|---|---|---|---|
| procamp | `HEAD_SET_PROCAMP` (0x2000+h·0x400) | COLOR_SPACE=RGB, DYNAMIC_RANGE=VESA | RGB, CEA | YUV_601/709/2020, CEA |
| 4:2:0 only | PROCAMP `CHROMA_LPF`=1, `CHROMA_DOWN_V`=1 (C67D bit 4); `HEAD_SET_CONTROL` `YUV420PACKER`=1 (C67D bit 3) | – | – | 4:2:0 |
| conversion | `HEAD_SET_OCSC1CONTROL` (0x229C) + 12 coeffs `OCSC1COEFFICIENT_C00..C23` (0x22A0..0x22CC) | disabled | `RGBToLimitedRangeRGB` | `RGBToLimitedRangeYCbCrRec601/709/2020` |
| clamp | `HEAD_SET_CLAMP_RANGE_GREEN/RED_BLUE` (0x2238/0x223C) | 0x000..0xFFF | 0x100..0xEB0 | Y 0x100..0xEB0, C 0x100..0xF00 |
| depth | `HEAD_SET_CONTROL_OUTPUT_RESOURCE.PIXEL_DEPTH` | 24/30/36/48_444 | same | 444 & 420: 24/30/36_444; 422: 16/20/24_422 for 8/10/12 bpc |

Sources: `nvkms-evo3.c` `EvoSetProcAmpC5` (:2015-2075), `EvoSetOCsc1C5`
(:1847-1884), `nvEvoGetOCsc1MatrixC5` (:1722-1757), `nvEvoGetOCsc1ClampRange`
(:1762-1800), `EvoSetHeadControlC3` YUV420PACKER (:2223-2230);
`nvkms-evo.c nvEvoDpyColorToPixelDepth` (:9595-9629), `nvChooseColorRangeEvo`
(:2626-2648). No SOR method changes per colour format on HDMI (SOR_SET_CONTROL
has no colour field; `COLOR_SPACE_OVERRIDE` is DP-only in NVKMS).

**Matrix provenance, verified here:** all 36 YCbCr coefficients and the
limited-RGB scale are the ITU-R luma coefficients (BT.601 0.299/0.114,
BT.709 0.2126/0.0722, BT.2020 0.2627/0.0593) at scale 219/256 (luma) and
224/256 (chroma), offsets 16/256 and 128/256, in 21-bit two's-complement with
16 fractional bits. Worst residual against NVIDIA's register values: 4 LSB of
2^-16 (a quarter of one 12-bit output code) — NVIDIA's own rounding. The patch
uses NVIDIA's exact values so output is bit-identical to the proprietary driver
on the same card. Derivation script: `/K3D/temp/chroma-port/derive_ocsc1.py`.
Clamp ranges are exactly 16..235 / 16..240 at 12-bit.

Class coverage: NVKMS has no Volta (C37D) display HAL, so there is no open
oracle for Volta; C37D keeps today's behaviour and does not get the new
properties. Blackwell (CA7D) has the same OCSC1/clamp methods at a 0x800 head
stride and a native `HEAD_SET_CONTROL_YUV420PACKER`: an identical-mechanism
follow-on patch, untested here.

## 3. Packets

- **GCP** (**normative** HDMI 1.4b §6.5.3; **implemented** NVKMS
  `SendHdmiGcp`, dw-hdmi): 4:4:4 and 4:2:0 use the same CD/PP table as RGB
  (already in v2 patch 2); **4:2:2 sends CD=0** (4:2:2 up to 12 bpc rides the
  24-bit container at the pixel clock — no deep-colour indication). NVKMS
  keeps the GCP but leaves CD/PP default for 4:2:2.
- **AVI**: Y1Y0 per format; Q per Broadcast RGB via
  `drm_hdmi_avi_infoframe_quant_range` (which already honours QS=0 sinks);
  YCbCr: YQ=limited, C = the matrix actually programmed. NVKMS default
  colorimetry = BT.709 on HD timings, BT.601 on SD (`nvkms-hdmi.c:108-149`,
  also CTA-861's rule for C=0); 4:2:0 always BT.709.
- **SCDC/character rate**: v2's char-rate gate generalises to
  `drm_hdmi_compute_mode_clock()`.

## 4. Selection policy (atomic check)

Extend the v2 `nv50_outp_atomic_fix_depth()` TMDS branch into a joint
format×bpc search, amdgpu-shaped:

1. Candidate formats from the `color format` request: AUTO → RGB (then 4:2:0
   for 4:2:0-only modes); an explicit request is honoured or rejected
   (-EINVAL), never silently substituted — the uAPI docs require an
   unsupported combination to fail.
2. EDID gates: `display_info.color_formats` (YCBCR444/422 bits),
   `edid_hdmi_ycbcr444_dc_modes` for deep 4:4:4 (DC_Y444 carries the RGB
   DC_30/36/48 bits over), 4:2:2 ≤ 12 bpc, `drm_mode_is_420_{only,also}` and
   `hdmi.y420_dc_modes` for 4:2:0, `ycbcr_420_allowed` only on GA102+ heads.
3. bpc high→low from `max_requested_bpc`, rate via
   `drm_hdmi_compute_mode_clock()` against the TMDS limit.
4. Store `asyh->or.format` + range + colorimetry; procamp/OCSC re-sent on
   modeset (head `set.mask = ~0` path) and when Broadcast RGB changes.

## 5. Proposed series

1. `drm/nouveau: add NVC57D output CSC and clamp range methods` (class header).
2. `drm/nouveau: program head output conversion for limited range and YCbCr`
   (C57D procamp + OCSC1 + clamp from head atom state; no uAPI yet —
   behaviour unchanged: RGB full).
3. `drm/nouveau: add the Broadcast RGB property` (limited/full RGB, AVI Q;
   default Automatic, fixing today's full-range-on-CE-formats mismatch for
   QS=0 sinks).
4. `drm/nouveau: add the color format property for HDMI YCbCr 4:4:4/4:2:2`
   (joint selection, 4:2:2 pixel-depth codes, GCP CD=0 for 4:2:2, AVI Y/C).
5. `drm/nouveau: support HDMI YCbCr 4:2:0 on GA102 and later` (packer,
   CHROMA_DOWN_V/LPF, 4:2:0 modes; untested — no 4:2:0 sink).
6. (follow-on) Blackwell CA7D output CSC.

## 6. Bench plan (owned hardware: GA106 → KDL-46HX855)

HX855 EDID (sha256 fbe6a3b4… for input 1; per-input PA differs): YCbCr 4:4:4
+ 4:2:2, DC_30/DC_36/**DC_Y444**, 225 MHz TMDS, ~~no VCDB (QS=0)~~ **VCDB present, RGB and YCbCr quantization selectable (QS=1)**, no 4:2:0.

> **Correction 2026-09-23:** "no VCDB (QS=0)" was wrong. `edid-decode` of this exact EDID (and of the KDL-46EX725's) shows a Video Capability Data Block with QS=1 and QY=1 (`tools/stereo-modeset/edid-2026-09-23/`). On this sink, stock nouveau declaring full range is honoured, so the full-range/limited mismatch this series targeted does not occur here; it applies to sinks without a VCDB. amdgpu reads the same bit (`rgb_quant_range_selectable` -> `qs_bit`) and declares full range correctly.

| run | format | bpc | rate @1080p60 | expectation |
|---|---|---|---|---|
| R-full | RGB full | 12 | 222.75 | = run25 (regression) |
| R-lim | RGB limited | 12 | 222.75 | OSD 12-bit; black/white levels correct with TV HDMI range on Auto |
| Y444 | YCbCr 4:4:4 | 8/10/12 | 148.5/185.6/222.75 | OSD format + depth |
| Y422 | YCbCr 4:2:2 | 12 | 148.5 | OSD format; GCP CD=0 |
| 3D | SBS/TaB/FP × one YCbCr format | 12 | ≤222.75 | 3D + format together (roadmap's combined gate) |

The frame label gains the format name. Windows 616 on the same card is the
behavioural oracle: set the same format/depth/range in NVIDIA Control Panel
first and read the OSD, so any nouveau failure is attributable to nouveau
rather than to the sink. 4:2:0 and 48 bpp stay "implemented, same mechanism,
not measured here".

Open question to settle on the bench before claiming the range fix: whether
the HX855 menu's HDMI range setting is on Auto (then today's full-range RGB on
1080p60 should visibly crush blacks/clip whites) or forced Full (masking it).
