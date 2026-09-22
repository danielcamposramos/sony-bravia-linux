# nouveau HDR gap — source-level investigation (2026-09-22)

Owner's question: "since nouveau does not have HDR — investigation time?"

Base tree: Linux 7.3-rc4, cross-checked against the locally built 7.0.10
(+deb14) tree. Scope: `drivers/gpu/drm/nouveau` and the DRM/HDMI helpers it
would consume. This is a source audit, not an HDR-output test: the bench has
no HDR sink. File and symbol names are recorded so every claim can be rerun
against another checkout.

## Verdict

nouveau currently exposes no public KMS HDR control surface and has no path
that emits the CTA-861.3 Dynamic Range and Mastering InfoFrame. This is an
implementation gap, not a measured claim about picture quality.

| surface | nouveau status (7.3-rc4) | reference implementation(s) |
|---|---|---|
| `HDR_OUTPUT_METADATA` connector property | **not attached** | amdgpu, i915 and several HDMI bridges attach it in-tree |
| `Colorspace` connector property | **not attached**; nouveau's other `colorspace` tokens describe scanout-surface conversion, not the connector property | amdgpu and i915 |
| `max bpc` connector property | **not attached**; the existing bpc uses are DP link math and dithering depth | amdgpu and i915; proprietary `nvidia-drm` also exposes it |
| Dynamic Range and Mastering InfoFrame | **not constructed or emitted** | amdgpu and i915 emit it; proprietary `nvidia-drm` hands the blob to closed NVKMS |

### Deep colour is a second, earlier gap

The same audit found a testable prerequisite below HDR metadata. On HDMI,
`nouveau_connector_detect_depth()` falls back to 8 bpc when the EDID base
field does not supply a depth; it does not turn the HDMI VSDB's `DC_30` and
`DC_36` flags into an HDMI depth choice. `nv50_outp_atomic_check()` then uses
that value rather than `max_requested_bpc`, and `nv50_sor_atomic_enable()`
leaves TMDS pixel depth at its default. Nouveau also exposes no `max bpc`
property.

This is not evidence of an 8-bpc hardware limit. The display class headers
define explicit 36-bpp RGB 4:4:4 values at both SOR and head level. The nearby
“we don't support more than 10 anyway” comment is confined to DisplayPort
link reduction. The old open question — whether selecting those existing
36-bpp values also makes GA106 emit the required HDMI General Control Packet
deep-colour indication — was first answered by negative measurement (run 2:
the experimental 36-bpp modeset committed cleanly and the HX855 refused the
wire), then by construction and register evidence: patch v2 added the GCP
programming bit-for-bit from NVIDIA's own public recipe, patch v3 proved via
readback during run 4 that the GCP subpack `0x00002610` and its enable bit
land and hold in the SF aperture under GSP, matching the proprietary driver's
MMIO route — yet the sink still refused. The remaining missing half is
therefore the **TMDS character-rate derivation**: nothing in the open halves
raises the link from 148.5 to 222.75 MHz for deep colour; that derivation
lives inside closed RM/GSP and evidently does not trigger from the state
nouveau supplies [inferred from sink behaviour plus register readbacks; no
wire analyzer]. The measurement chain, the two remaining candidate levers,
and the partner handoff are recorded in the plan document and
[`nouveau-deep-colour-handoff-to-codex-2026-09-22.md`](nouveau-deep-colour-handoff-to-codex-2026-09-22.md).

The owned HX855 declares a 225 MHz TMDS maximum; 1080p60 at 12-bpc RGB needs
148.5 × 1.5 = 222.75 MHz. That makes the existing bench a narrow but valid
deep-colour probe. The complete source map, safety transaction, and acceptance
table are in
[`nouveau-hdmi-deep-colour-plan-2026-09-22.md`](nouveau-hdmi-deep-colour-plan-2026-09-22.md).

`nouveau_conn_attach_properties()` in `nouveau_connector.c` attaches the
legacy scaling, underscan, dithering, vibrance and hue surfaces. Searches for
`drm_connector_attach_hdr_output_metadata_property()`, the Colorspace attach
helpers, and `drm_connector_attach_max_bpc_property()` return no nouveau call
site in either audited tree.

The kernel already supplies the format side of the missing link:
`drm_hdmi_infoframe_set_hdr_metadata()` creates an HDMI DRM InfoFrame from a
connector's HDR metadata blob, and `hdmi_drm_infoframe_pack()` serializes it.
The payload is 26 bytes (`HDMI_DRM_INFOFRAME_SIZE`), or 30 bytes including the
HDMI header and checksum.

## Normative chain

The implementation target is not inferred from one vendor's behaviour:

- [HDMI Forum's HDMI 2.0a announcement](https://hdmiforum.org/hdmi-forum-inc-release-2-0a-specification/)
  records the addition of HDR formats by reference to CEA-861.3.
- [CTA-861.3-A](https://shop.cta.tech/products/cta-861-3) defines the HDR
  Static Metadata Data Block and Dynamic Range and Mastering InfoFrame; CTA
  hosts a [free preview of the 2015 edition](https://standards.cta.tech/kwspub/published_docs/CEA-861.3-Preview.pdf).
- [ITU-R BT.2100-3](https://www.itu.int/rec/R-REC-BT.2100-3-202502-I/en)
  defines the current HDR television image parameters.
- Linux exposes the cross-driver userspace contract through
  [`struct hdr_output_metadata`](https://github.com/torvalds/linux/blob/master/include/uapi/drm/drm_mode.h).

The full standards map, including the boundary between licensed normative
text and public previews, is maintained in
[`awesome-stereoscopy/standards.md`](https://github.com/danielcamposramos/awesome-stereoscopy/blob/main/standards.md#hdr-over-hdmi-deep-colour-container-and-static-metadata).

## Where the real boundary is

nouveau already programs AVI and vendor-specific (VSI) HDMI InfoFrames, but
the public contract is limited to those two packet classes:

- `include/nvif/if0012.h` declares only
  `NVIF_OUTP_INFOFRAME_V0_AVI` and `NVIF_OUTP_INFOFRAME_V0_VSI`.
- `nvkm/engine/disp/uoutp.c` dispatches only those two types.
- `dispnv50/disp.c:nv50_hdmi_enable()` allocates a 17-byte flexible buffer.
- `nvkm/engine/disp/hdmi.c:pack_hdmi_infoframe()` deliberately truncates
  packets longer than 17 bytes.

That is sufficient for the current AVI/VSI users, but not for the 30-byte HDR
DRM InfoFrame. Adding the connector properties without completing this
last-mile transport would create a lying API: userspace could request HDR and
the display would never receive its metadata. This project will not do that.

## The new clue in 7.3-rc4: Valve's Blackwell work

Linux 7.3-rc4 adds `nvkm/engine/disp/gb202.c`, copyright 2026 Valve Corp. Its
comment records that Blackwell removed the legacy VSI unit and sends vendor
InfoFrames through shared generic units instead. The new
`gb202_sor_hdmi_infoframe_vsi()` writes a complete 36-byte slot and accepts up
to 31 raw bytes—large enough for the 30-byte HDR DRM InfoFrame.

This is important evidence, not a completed port:

- it proves current nouveau has an open, generic HDMI packet writer on GB20x;
- it identifies packet-slot layout and a programming sequence grounded in
  NVIDIA headers and NVIDIA's own `nvhdmipkt_C971.c`;
- it does **not** prove that the same register sequence applies to the bench's
  GA106/Ampere GPU.

On GV100/GA10x-shaped paths, the VSI bank at `0x6f0100` has room-looking
registers, but the current packer fills only 17 bytes and zeroes the rest.
That makes it a strong candidate for investigation, not permission to guess
at hardware programming.

The r535 GSP ABI exposes a second candidate:
`NV0073_CTRL_CMD_SPECIFIC_SET_OD_PACKET` accepts up to 36 bytes and can select
generic InfoFrame slot 0 or 1. nouveau currently uses that command for HDMI
audio packet control, not HDR. We still need to determine whether it is the
correct GA106 HDR route and how its slot ownership coexists with VSI before
writing an upstream-quality patch.

## Complete implementation shape

The work divides cleanly into a generic KMS half and a hardware-specific
packet half:

1. Attach `HDR_OUTPUT_METADATA`, `Colorspace`, and an honest `max bpc` range
   to capable HDMI connectors.
2. Validate the metadata blob and connector state during atomic check.
3. Build and pack the DRM InfoFrame with the existing DRM/HDMI helpers.
4. Extend NVIF and nvkm dispatch to carry a third packet class and at least
   30 bytes without truncation.
5. Implement packet emission per display generation. GB20x already has a
   generic slot; GA106 needs the register-bank-versus-GSP-command question
   resolved from code, traces, or maintainer knowledge.
6. Disable/clear the packet when metadata disappears and preserve AVI, VSI,
   audio, deep-colour and 3D signalling across transitions.

The upper half is straightforward plumbing. The GA106 last mile remains
hardware research. Calling the whole change "just hundreds of lines" before
that boundary is resolved would overstate what the source proves.

## Verification ladder

An honest patch series can advance without pretending this bench has an HDR
display:

1. build and static-check each supported display generation;
2. verify connector-property exposure and ranges with `modetest`;
3. exercise atomic acceptance, replacement and removal of valid/invalid HDR
   blobs;
4. trace the packed bytes and checksum delivered to the packet layer;
5. regression-test SDR, AVI, VSI/3D and audio paths on the existing BRAVIA;
6. obtain final on-wire/picture confirmation from an HDR sink, capture device
   or protocol analyzer before claiming working HDR output.

Steps 1–5 are locally actionable. Step 6 is a required external validation,
not a reason to leave the source gap unmapped.

## Research provenance

Daniel Campos Ramos directed the investigation, supplied the owned-hardware
measurements, and owns every public claim. The initial nouveau source survey
and draft were produced with LLM Kimi K3 (Claude Code CLI, Ollama provider).
LLM GPT-5.6 Sol (Codex CLI) audited that draft against Linux 7.3-rc4, found
the newer Valve GB20x generic-packet work and the r535 36-byte command, and
narrowed the claims and test boundary recorded here. The result is collective
research; the absence of an HDR sink is disclosed rather than filled by
model inference.

## Relationship to the proprietary NVIDIA finding

These are two related but distinct repair lanes:

- **Proprietary NVIDIA:** the open `nvidia-drm` glue already exposes
  `HDR_OUTPUT_METADATA`/Colorspace and translates connector state into an
  NVKMS request. The actual link-depth and output policy lives in closed
  NVKMS. Our measured 10-vs-12-bit narrowing and sibling HDR reports therefore
  give NVIDIA a reproducible ownership question, not an independently
  patchable open-glue fix.
- **nouveau:** the KMS surfaces and HDR packet route are absent in readable
  code. The standards, DRM helpers and increasingly capable packet machinery
  make this a community-addressable implementation project.

So this investigation does not claim that a proprietary fix can simply be
"ported." It establishes a shared standards contract and two different
ownership paths: press NVIDIA to correct NVKMS, and build the missing open
path in nouveau.

## Why this belongs in the campaign record

One sink and one EDID already produce three different, measured non-HDR
surfaces on the same workstation:

- **amdgpu** (Ryzen 5 5500G control head): full mode list and 12-bit link
  training reported by the TV OSD;
- **nouveau** (GA106): full mode list and the tested HDMI 1.4 3D modes, but no
  HDR/Colorspace/max-bpc KMS properties;
- **proprietary `nvidia-drm`** (same GA106): HDR-related KMS machinery exists,
  while the same TV reports 10-bit link training and NVKMS prunes modes and
  all stereo flags.

The HDR conclusion is deliberately narrower: source and property shape are
confirmed; HDR light on the wire is not. That boundary is also the roadmap.
The unified proprietary report is
[#1384](https://github.com/NVIDIA/open-gpu-kernel-modules/issues/1384).
