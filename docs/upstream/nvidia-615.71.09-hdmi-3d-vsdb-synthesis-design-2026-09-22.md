# NVIDIA glue-side VSDB stereo-mode synthesis — design (2026-09-22)

Companion to `nvidia-615.71.09-hdmi-3d-community.patch` (v1, the six-line
`stereo_allowed` enablement — measured necessary-but-not-sufficient in run18).
This document designs and records v2: synthesizing `DRM_MODE_FLAG_3D_*` mode
variants in the open GPL glue, from the HDMI VSDB 3D fields of the EDID that
NVKMS already fetched and cached into `nv_connector->edid`.

## Why this lane exists

Run18 (this repo, `tools/stereo-modeset/run18-*.log`) measured on the
KDL-46HX855 sink, same boot, same EDID:

| driver | total modes | stereo-flagged |
|---|---|---|
| nouveau (DRM core EDID parse) | 51 | 29 |
| nvidia-drm stock 615.71.09 | 17 | 0 |
| nvidia-drm + v1 (`stereo_allowed`) | 17 | 0 |

Root cause chain, all in open code except the last hop:

1. `nv_drm_connector_get_modes()` (kernel-open) lists modes ONLY from
   `nvKms->getDisplayMode()` (`nvidia-drm-connector.c:419+`).
2. `NvKmsKapiDisplayMode` has no stereo members; `nvkms_display_mode_to_drm_mode()`
   (`nvidia-drm-utils.c:106+`) maps interlace/doublescan/sync only. No 3D-flagged
   mode can ever exist in the list.
3. v1's `stereo_allowed = true` therefore passes DRM core's MODE_NO_STEREO gate
   (`drm_probe_helper.c:460-461` + `drm_mode_validate_flag()`), but there is
   nothing to admit.

Two repair lanes were put to aritger on NVIDIA/open-gpu-kernel-modules#1382:
NVKMS-side (closed source; surfaces VSDB variants as display modes) and
glue-side (kernel-open only; this document). The glue lane is the one we can
prototype and measure today.

## Reference implementation (what we mirror)

`drivers/gpu/drm/drm_edid.c` in kernel 7.0 — the exact code that produced
nouveau's 29 stereo modes on this same EDID:

- `do_hdmi_vsdb_modes()` (line 4829): HDMI VSDB 3D parsing.
- `add_hdmi_mandatory_stereo_modes()` (line 4711) + `stereo_mandatory_modes[]`
  (line 4686): the 8 CTA-mandatory stereo timings any 3D_present sink gets.
- `add_3d_struct_modes()` (line 4765): structure bitmask bits 0/6/8 →
  FRAME_PACKING / TOP_AND_BOTTOM / SIDE_BY_SIDE_HALF.
- `drm_display_mode_from_vic_index()` (line 4586): resolves a vic_index into the
  EDID's VDB VIC list to a canonical CTA mode. **static; not available to
  nvidia-drm** — this drives the main design deviation below.

Structure→flag mapping (HDMI 1.4 3D_Structure values): 0 →
`DRM_MODE_FLAG_3D_FRAME_PACKING`, 6 → `3D_TOP_AND_BOTTOM`, 8 with
`3D_Detail_X == 1` (horizontal subsampling) → `3D_SIDE_BY_SIDE_HALF`. Other
structures have no DRM flag and are skipped, exactly as DRM core does.

## Byte-level verification of the parse against our sink

HX855's CTA extension, HDMI VSDB bytes (from `hx855-edid-decode.txt`, OUI
00-0C-03, payload length 20):

```
db[0]=0x74 header            db[8]=0x2f  HDMI_Video_present=1, latency=0, imgsz=11
db[1..3]=03 0c 00 OUI        db[9]=0xd0  3D_present=1, 3D_Multi_present=0b10
db[4..5]=10 00 phys 1.0.0.0  db[10]=0x0a HDMI_VIC_LEN=0, HDMI_3D_LEN=10
db[6]=0xb8 AI, DC_36,DC_30   db[11..12]=01 40  3D_Structure_ALL = 0x0140 (TaB+SbS-H)
db[7]=0x2d maxTMDS 225MHz    db[13..14]=00 7f  3D_MASK = 0x007F (VIC indices 0..6)
                             db[15..20]=20 30 70 80 90 76  detail entries
```

- VDB VIC order (19 VICs): 31 16 20 5 19 4 32 34 60 62 18 22 3 7 17 21 2 6 1.
  Mask 0x007F applies structure 0x0140 to indices 0..6 → VICs 31, 16, 20, 5,
  19, 4, 32, i.e. 1080p50/60/24, 1080i50/60, 720p50/60, each supporting
  **TaB + SbS-H**. Matches edid-decode exactly.
- Detail entries (2D_VIC_order<<4 | 3D_Structure): 0x20→VIC20 FP, 0x30→VIC5 FP,
  0x70→VIC34 FP, 0x80→VIC60 FP, 0x90→VIC62 FP, 0x76→VIC34 TaB. All six match
  edid-decode's "specific capabilities" list.
- Latency flags absent (db[8] bits 7/6 zero) and Image_Size_present=0b11 means
  "inherit base-EDID cm size, no extra bytes" — so the 3D flags byte sits at
  db[9] and the drm_edid offset arithmetic applies untouched. The mirror is
  bug-for-bug compatible with the reference parser (including its lack of
  explicit Image_Size handling, which is a non-issue here and matches how every
  in-tree driver parses this same EDID today).

## Design decisions (where/why the glue deviates from drm_edid)

1. **Clone only timings the driver itself listed.** drm_edid rebuilds canonical
   CTA modes from its static `edid_cea_modes[]` table (not exported). The glue
   instead carries a compact per-VIC `{width, height, vrefresh, interlaced}`
   table and matches those against modes ALREADY in `connector->probed_modes`
   (the NVKMS-produced list), duplicating the matched mode with the stereo
   flag added. Consequences, all intentional:
   - no timing is synthesized that NVKMS has not already surfaced (and thus
     validated) in 2D — every stereo variant inherits a timing the driver
     itself proved it can drive;
   - NVKMS's own base-list pruning stays authoritative (17 base modes here);
     the patch adds nothing outside the stereo semantics;
   - fractional-rate bases are covered twice when the driver lists both
     (1080p60 appears at 148.500 MHz and 148.352 MHz — both get cloned), with
     ±1 Hz refresh tolerance to absorb 1000/1001 rounding.
2. **Mandatory stereo modes mirrored verbatim** (8-entry table). Under v1's
   `stereo_allowed` they validate because clone timings equal base timings and
   `nv_drm_connector_mode_valid()` passes only timing data to NVKMS
   (`drm_mode_to_nvkms_display_mode()` drops stereo bits — NVKMS never sees a
   3D request at validation time, which is precisely the semantic we want:
   "same timing the driver already accepted, 3D signalled at the link layer
   via the HDMI VSIF/`hdmi_vsif_metadata` property path").
3. **Gated on `stereo_allowed`.** Synthesis runs only when the connector has
   stereo enabled (v1 hunk) — no behavior change for any path that does not
   already opt into stereo admission, and v2 remains strictly a follow-up on
   v1.
4. **EDID source:** `nv_connector->edid` (allocated from
   `pDetectParams->edid.buffer`, exact EDID length). Extension count from base
   byte 126; CTA tag 0x02 scan; VIC collection across all Video Data Blocks;
   VSDB OUI 03-0C-00 detection with the same length guards as drm_edid.
5. **Deviate: no FP timing doubling, no infoframe work.** drm_edid's list-side
   behavior stops at flagging; NVKMS-side support (2x-vtotal scanout for FP,
   3D_Structure in the AVI/VSIF) is closed-source territory. We document FP
   modes as listable/flaggeable; whether a modeset actually drives FP is
   NVKMS's business, and the probe only measures enumeration + validation
   admission. TaB/SbS-H need no link-level timing change at all — only the
   VSIF 3D field at commit time (the `hdmi_vsif_metadata` connector property
   already exists in the open glue, `nvidia-drm-connector.c`).

## Expected probe delta on the HX855 (predict-before-run)

NVKMS's 17-mode base list (run18) contains: 1080p60 ×2, 1080p50, 1080p30,
1080p24; 720p60 ×2, 720p50, 720p30, 720p24; plus PC/SD modes. **1080i50 and
1080i60 are absent from the NVKMS list** (present for nouveau), so every
VSDB entry keyed to VIC 20 or VIC 5 resolves to zero clones — including the
TV's interlaced Frame Packing, the format broadcast 3D uses. That is a second
NVKMS-list gap the measurement will make concrete.

Predicted synthesis from those 17 (clones per matching base):

- mask (TaB+SbS-H on VICs 31,16,{20},{5},19,4,32): 1080p50 +2, 1080p60 ×2 bases
  +4, 720p50 +2, 720p60 ×2 bases +4, 1080p24 +2 → **+14** (1080i entries: 0)
- details: FP 1080p30, FP 720p24, FP 720p30, TaB 1080p30 → **+4** (FP 1080i: 0)
- mandatory: 1080p24 TaB+FP +2, 720p50 TaB+FP +2, 720p60 ×2 bases TaB+FP +4,
  1080i SbS-H ×2 → 0 (base absent) → **+8**

≈ **43 total / ~26 stereo-flagged** on HDMI-A-2 (vs 17/0 stock, 51/29 nouveau),
with possible exact timing+flag duplicates where mandatory and mask overlap —
same behavior as DRM core's reference implementation (no dedup there either).

Success criterion for the harness run: with STEREO_3D client cap set, stereo
count moves 0 → low 20s and total moves 17 → low 40s; stock remains 17/0.
A no-delta result would mean validation rejects stereo-flagged clones despite
identical timings — itself a reportable finding.

## Measured — run19 (2026-09-22, same boot style, KDL-46HX855 on HDMI-A-2)

Log: `tools/stereo-modeset/run19-nvidia-vsdb-synthesis-22-stereo-2026-09-22.log`.
Module under test: md5 32c1ffac28cdf0c7b08cc3506c95d01f (this design's build).

| client caps | stock 615.71.09 | v2 (stereo_allowed + synthesis) |
|---|---|---|
| none | 17 / 0 | 17 / 0 |
| ASPECT_RATIO only | 17 / 0 | 17 / 0 |
| STEREO_3D | 17 / 0 | **39 / 22** |
| both | 17 / 0 | **39 / 22** |

Unique stereo modes synthesized for this sink, by structure:

- frame packing: 1080p24, 1080p30, 720p24, 720p30, 720p50, 720p60 x2 (7)
- top-and-bottom: 1080p24, 1080p30, 1080p50, 1080p60 x2, 720p50, 720p60 x2 (8)
- side-by-side half: 1080p24, 1080p50, 1080p60 x2, 720p50, 720p60 x2 (7)

Prediction check (~43/~26): the four excess modes were exactly the
mandatory-table TaB clones that overlap the mask-derived ones (1080p24,
720p50, 720p60 x2).  The kernel probe collapses exact timing+flag
duplicates, so 26 synthesized -> 22 unique.  Everything else matched,
including the structural absence of all 1080i variants: the sink declares
Frame Packing on VIC 20/5 (1080i50/60, the broadcast 3D formats) but the
NVKMS base list carries no interlaced timing, so those six entries resolve
to zero clones.  That is the second NVKMS-list gap (mode pruning being the
first, deep-color training the third nearby symptom) that only the
NVKMS-side lane can reach.

Reference deltas, same EDID: nouveau 51/29; this patch 39/22
(the ~7-mode gap to nouveau is the entire missing 1080i family plus one
refresh-variant duplicate nouveau lists).

## Files

- Patch (v2 = v1 stereo_allowed + synthesis):
  `docs/upstream/nvidia-615.71.09-hdmi-3d-community-v2.patch`
- Harness (unchanged, re-run with the v2-built nvidia-drm.ko):
  `tools/stereo-modeset/run-nvidia-patched-probe.sh`

Build recipe (known-good, kernel 7.0.10+deb14 built with gcc-15):
`sudo IGNORE_CC_MISMATCH=1 CC=gcc-15 make -j"$(nproc)" modules` from
`/usr/src/nvidia-615.71.09/` (top level; kernel-open-only build misses the
binary cores); then `sync` (/K3D commit=600 window).
