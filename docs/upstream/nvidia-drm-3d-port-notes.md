# nvidia-drm stereo port — recon notes (2026-09-20, source: /usr/src/nvidia-615.71.09)

Status: [inferred from local 615.71.09 kernel-open source — the exact tree behind the
installed driver] — patch not yet written, blob-property userspace path not yet tested.

## What the source says

1. `nvidia-drm/nvidia-drm-connector.c:737` `drm_connector_init()` — `stereo_allowed`
   is never set → zero 3D-flagged modes are ever exposed. (Same defect shape as
   amdgpu DC pre-patch, except amdgpu had the flag explicitly false.)
2. The kernel-open tarball ships only 2 .c files for nvidia-modeset (OS glue); the
   display core is kapi-only. Closed side, not patchable from the repo.
3. BUT the kapi already carries the VSIF plumbing:
   `common/inc/nvkms-kapi.h:403` `modeSetConfig.hdmiVsifMetadata`
   (struct at `nvkms-api-types.h:821`: `NvU8 payloadSize; NvU8 payload[27];`,
   3..27 bytes enables VSIF emission) + `flags.hdmiVsifMetadataChanged` (:436).
4. And the open glue ALREADY exposes it end-to-end as a userspace DRM property:
   `nvidia-drm-connector.c:582-603` copies a connector blob
   (`struct drm_nvidia_hdmi_vsif_metadata { length, payload[] }`, min/max 3/27)
   verbatim into `modeSetConfig.hdmiVsifMetadata` at modeset time.

## Port shape (two independent deltas)

A. **Mode exposure [one line]**: after `drm_connector_init()` at
   `nvidia-drm-connector.c:737`, `nv_connector->base.stereo_allowed = true;`.
   That alone surfaces the sink's EDID 3D alternates to STEREO_3D-cap clients.
B. **VSIF emission, two options**:
   - B1 (driver-side, amdgpu-patch-style): in the modeSetConfig fill path, when
     `mode->flags & DRM_MODE_FLAG_3D_MASK`, synthesize the CTA-861 VSIF payload
     (OUI 00:0C:03, HDMI_Video_Format=2, 3D_Structure from the flag: FP=0,
     TaB=6, SBS-half=8) into `hdmiVsifMetadata` and set the changed flag when
     no userspace blob overrides it. Needs care vs the existing blob path
     (blob should win if both present).
   - B2 (userspace, zero kernel patch): a client sets the existing
     `hdmi_vsif_metadata` blob property + modesets a hand-built stereo timing
     (the modes are the same CEA timings; legacy SetCrtc does not require the
     mode to be in the probed list). Needs runtime verification that the
     property exists in the installed 615 build and that atomic check accepts
     a non-listed stereo-flagged mode.

## Immediate runtime checks (stock driver, no rebuild)

- `modetest -c -p` (or drm_info): does the HDMI connector of the RTX 3060
  expose the nvidia VSIF blob property? Name/presence decides B2 viability.
- nouveau verification run (front 2) also doubles as a working-reference for
  what a correct VSIF emission looks like on this exact sink+cable.

## Upstream conversation target

NVIDIA/open-gpu-kernel-modules. Delta A is trivially reviewable; B1 vs B2 is
the design question to raise in the issue — NVIDIA may prefer the already-shipped
userspace blob (B2) over driver-side synthesis (B1). Evidence from the amdgpu
leg (KDL-46HX855 autoswitching, [proven]) demonstrates both the mechanism and
the consumer demand.

## Live check 2026-09-20 23:5x UTC-3 — blob property PRESENT on stock 615

[proven, live read-only check] `drm_info /dev/dri/card1` on the running
615.71.09 stack (desktop up, no master needed) shows
`NV_HDMI_VSIF_METADATA` as a connector blob property on the HDMI-A
connector, alongside `HDR_OUTPUT_METADATA` and `Colorspace` (BT2020 options).
Exactly the property the open glue (`nvidia-drm-connector.c:582-603`) copies
verbatim into `modeSetConfig.hdmiVsifMetadata` at modeset time.

This promotes path B2's first precondition from source-read to verified on
the installed build: userspace CAN attach a 3..27-byte VSIF payload with no
kernel patch. What B2 still needs to demonstrate (a modeset attempt, so a
future desktop-down run):

1. atomic check accepts the hand-built blob (no driver-side VSIF veto), and
2. a hand-built FP timing can replace the absent stereo modes (nvidia-drm
   prunes them: the KMS arm probes 22/0 — userspace must construct the
   1920x1080@24 FP modeline itself, e.g. via a custom modeline in
   test_only/commit, since no flagged alternate exists to pick).

## Clarification — 2026-09-21 (corrects the owner-test claim added earlier today)

"nvidia was also already tested, both types worked" refers to the NVIDIA
GPU itself (GA106 RTX 3060) on stock nouveau: run 4 (SBS-half modeset pass,
20:26-20:28 UTC-3) and run 5 (frame-packing pass, 21:37-21:39 UTC-3), logs
already in tools/stereo-modeset/. Those are the "both types" records — no
new nvidia-drm run exists. The closed-kernel nvidia-drm B2 modeset above
remains the open item: the NV_HDMI_VSIF_METADATA property presence is
live-verified on 615.71.09, the atomic blob modeset still needs a
desktop-down run at Daniel's timing.
