# Handoff to Codex partner: GA106 nouveau HDMI 12-bpc — clock question (2026-09-22)

> For GPT-5.6 Sol (Codex CLI). This briefing is standalone; no chat history
> is assumed. Everything below is either quoted from public sources with
> file:line, or measured on the local bench and labelled. Inferences are
> tagged [inferred]. Please keep that discipline in your reply.

## Mission

Get the Sony KDL-46HX855 (HDMI 1.4, EDID declares DC_30/DC_36 RGB, max TMDS
225 MHz) to accept a **12-bpc RGB 1080p60** stream from a GALAX RTX 3060
(GA106, 12 GB) running **nouveau** (kernel 7.0.10+deb14, GSP firmware RM
570.144). Required TMDS character rate: 148.5 × 1.5 = **222.75 MHz**, inside
the sink's 225 MHz ceiling with 1% margin. This is the deep-colour transport
prerequisite for the project's HDR lane; it must not be called HDR.

Controls already established on this bench: amdgpu drives this TV at 12-bit
1080p60 (different HDMI input on the set); stock proprietary NVIDIA drives
it at 10-bit (policy-capped: NVKMS gates 12-bpc behind a module parameter);
Windows on this very card reports 12-bit. So the wire, cable, port, and
panel can physically carry 222.75 MHz.

## Where things stand (measured, all today)

Four runs of a reversible harness
(`tools/stereo-modeset/run-nouveau-test.sh deep12`; pause desktop + docker,
blacklist-swap to nouveau, gate on EDID sha256 `4f6cc1c8…e69d5dc9` on
HDMI-A-2, set `max bpc=12`, modeset 1920x1080@60, 90-s hold, restore):

- **Run 2** (v1 patch): `max bpc` property 8–12 attached to HDMI-A, bpc
  selection with EDID + TMDS-budget validation, and depth programming
  committed cleanly end to end — zero kernel errors — but the sink refused
  with its "incompatible signal" OSD. Driver-side PASS, sink-side FAIL.
- **Run 3** (v2 patch): added the General Control Packet programming,
  bit-for-bit from NVIDIA's own public recipe (see below). Same refusal.
- **Run 4** (v3 patch = v2 + read-only register instrumentation): same
  refusal, but now the kernel log proves what was on the wire. Verbatim
  from `journalctl -k` during the deep modeset:

  ```text
  nouveau: disp: gcp: head 0 subpack w=0x00000010 r=0x00000010 ctrl=0x00000001 avi_ctrl=0x00000200 avi_sp0=0x0828121d
  drm: deep-colour probe: TMDS bpc=12 sor-depth=0x8 clock=148500 kHz
  nouveau: disp: gcp: head 0 subpack w=0x00002610 r=0x00002610 ctrl=0x00000001 avi_ctrl=0x00000200 avi_sp0=0x0828121d
  ```

Modules: v2 `nouveau-hdmi-deep-colour-gcp-experimental.ko` sha256
`1d2f3dc4…a81f`; v3 `nouveau-hdmi-deep-colour-gcp-dbg-experimental.ko`
sha256 `68768c48…ded4`. Both vermagic-matched. Patches:
`docs/upstream/nouveau-hdmi-deep-colour-experimental{,-v2,-v3}.patch`
(each cumulative, each round-trip verified against a reconstructed pristine
7.0.10 base). Narratives: `tools/stereo-modeset/run2{0,1,2}-*.log`.

## What the code actually does on GA106 (verified line by line)

1. **Depth carrier.** On the C37D/C57D display cores (GA106),
   `SOR_SET_CONTROL` has **no** PIXEL_DEPTH field (clc37d.h:204-230: OWNER,
   PROTOCOL, DE_SYNC_POLARITY, PIXEL_REPLICATE only). NVIDIA's own evo3
   writer (`EvoSORSetControlC3`, nvkms-evo3.c:2282-2329) confirms. Nouveau's
   `sorc37d_ctrl()` (dispnv50/sorc37d.c) pushes owner+protocol only; the
   NV837D depth merge exists solely in `sor507d.c`, unused on this class.
   Depth reaches hardware via **head** `SET_CONTROL_OUTPUT_RESOURCE`
   PIXEL_DEPTH (=7, BPP_36_444), through the existing "dirty hack" table in
   headc37d/headc57d/headca7d — matching NVIDIA's `nvEvoGetPixelDepthC3`
   (nvkms-evo3.c:2331-2351) and `EvoHeadSetControlORC5`
   (nvkms-evo3.c:2446-2475).
2. **GCP.** v2 adds `gv100_sor_hdmi_gcp()`: writes
   `0x10 | CD<<8 | PP<<12` (= `0x00002610` for 1080p60 12-bpc: SB0
   Clear_AVMUTE, SB1 CD=6|PP=2, SB2 0) to `0x6f00cc + head*0x400`, enable
   bit at `0x6f00c0 + head*0x400` — the NVD5.x SF-HDMI aperture layout that
   bit-matches NVIDIA's cl9171.h `GCP_SUBPACK`/`INFO_CTRL(head, IDX_GCP=3)`.
   Called from both the direct gv100 ctrl and the GSP r535 ctrl **after**
   the RM `SET_HDMI_ENABLE` call. Payload construction mirrors NVKMS
   `SendHdmiGcp()` (nvkms-hdmi.c:412-470) exactly.
3. **RM call parity.** On this path NVKMS calls only `SET_HDMI_ENABLE`
   (nvkms-hdmi.c:1426 via `HdmiSendEnable`), `SET_HDMI_SINK_CAPS` (SCDC /
   scrambling / FRL caps only — no deep-colour bits, so not a hidden gate),
   and the audio/ELD calls. Nouveau matches the video-relevant ones.
   `CTRL_HDMI` (0x730274, "call prior to every modeset" per its header
   comment) is **not** referenced from nvkms-hdmi.c at all.
4. **Nothing rate-like anywhere open.** No TMDS character-clock programming
   exists in nvkms-hdmi.c, nvkms-modeset.c, nvkms-hw-states.c, or
   nvkms-evo3.c for deep colour; the only clock-touching structure is the
   IMP validation record (`NVValidateImpOneDispHeadParamsRec`, fed
   `pixelDepth` + timings at nvkms-modeset.c:1398-1476), and IMP itself is
   closed. The C37D/C57D core channel exposes no SOR clock method.
5. **GCP emission is provenly MMIO under GSP.** NVKMS's only call site for
   `SendHdmiGcp()` is the HDMI audio enable/mute flow
   (nvkms-hdmi.c:1381), and GSP firmware is mandatory on the proprietary
   stack — so register-slot writes at this aperture do reach the wire in
   production.

## The current diagnosis

By elimination: the GCP declaration was on the wire [inferred: register
landed + read back + production path identity], the depth state matched
NVIDIA's, and the sink's refusal is exactly what a compliant HDMI 1.4 sink
should say to a stream whose GCP declares 36 bpp while the measured link
runs at the 8-bpc character rate (148.5 MHz): it computes 148.5/1.5 = 99
MHz pixel clock, matches no mode, and refuses. **The missing piece is the
TMDS character-rate derivation inside closed RM/GSP** — what input makes it
program the SOR/link clock at pclk × 1.5 for deep colour, and what nouveau
isn't supplying to trigger that [inferred; no wire analyzer].

One run-4 anomaly worth your eyes: the AVI **payload** survived our write
(`avi_sp0=0x0828121d`) but the AVI **enable bit** read back clear
(`avi_ctrl=0x00000200`, reset-default CHKSUM_HW only) at GCP-write time,
moments after nouveau's AVI writer had set it — strong evidence that RM's
`SET_HDMI_ENABLE` handler rewrites/sanitizes slot control words in this
aperture from its own state under GSP. Our GCP ordering (after the RM call)
is load-bearing because of exactly this.

## Candidate levers to rank, poke holes in, or replace

- **L1 — proprietary-oracle register diff.** The local `nvidia` module
  exposes `hdmi_deepcolor:bool` and `max_output_color_depth:uint` (modinfo
  verified; today it policy-caps at 10 bpc). If `hdmi_deepcolor=1` (+depth
  param as needed) makes proprietary emit a real 12-bpc stream to this sink
  on Linux, we can MMIO-dump the SF aperture (`0x6f00xx` + head*0x400,
  AVI/GCP/VSI) and any readable SOR/head state under both stacks and diff
  to isolate what's actually different. Also consider RM message tracing
  (`NVreg_RmMsg`) during that modeset. This is the fastest path from
  "structurally identical on paper" to "here is the byte that differs" —
  but it is a live-hardware run, so it is gated on Daniel's explicit go
  like everything else.
- **L2 — audit the GSP commit path.** Trace which RM ctrl/RPC calls nouveau
  makes around the core-channel commit (nvkm/subdev/gsp/rm/r535/disp.c,
  udisp paths) vs NVKMS's, hunting for the one that carries (or fails to
  carry) the info RM's clock derivation keys on. The IMP validation record
  contents on the proprietary side would tell us exactly what the closed
  layer consumes; on GSP the derivation likely runs in firmware at commit.
- **L3 — SET_OD_PACKET route (0x730288).** 36-byte generic SDP injection
  through RM (`ctrl0073specific.h:1766+`), with transmit control
  ENABLE/OTHER_FRAME/SINGLE_FRAME/ON_HBLANK/IMMEDIATE and a curious
  RESERVED_LEGACY_MODE bit31. If under GSP the streamed packets come from
  RM's shadow table rather than the raw aperture state, GCP may belong in
  that table. Proprietary evidence says MMIO works, so rank this below the
  clock question — but the avi_ctrl anomaly keeps it alive.
- **L4 — independent audit of the "states are identical" claim.** Fresh
  eyes on the diff between what our runs pushed (core channel + outp +
  aperture, all logged/tracable) and the proprietary recipe. If there's a
  hole in our equivalence argument, that's the cheapest find of all.
- **L5 — physical/sink-side rate proxy.** The HX855's service diagnostics
  may report received TMDS clock or error codes; if so, one glance tells us
  directly whether the wire ran 148.5 or 222.75 during run 4. Daniel knows
  the service menu; ask before assuming.

## Hard constraints (non-negotiable, from Daniel)

- No live hardware test and no online post without Daniel's explicit
  per-act approval. Code, analysis, and docs are free to produce.
- The HX855 at .21 and EX725 at .22 are the only sinks; no TV port scans,
  no opening sets, own LAN/hardware only.
- Evidence discipline: measurements vs source citations vs [inferred].
- Build artifacts and scratch go under /K3D/temp (never /tmp); sync after
  builds (ext4 commit=600 window).
- Commits: author Daniel Campos Ramos <Capitain_Jack@yahoo.com>, trailer
  `Co-Authored-By: Claude Code <noreply@anthropic.com>` style applied per
  the human's current convention.
- Kernel tree: /K3D/temp/k317/linux-source-7.0 (7.0.10, v1+v2+v3 applied,
  not git); builds `make -j8 M=drivers/gpu/drm/nouveau modules` with
  gcc-15; harness `tools/stereo-modeset/run-nouveau-test.sh`.
- Fetched NVIDIA public sources for this work live in /K3D/temp:
  nvkms-hdmi.c, nvkms-modeset.c, nvkms-evo3.c, nvkms-hw-states.c,
  nvkms-rm.c, nvhdmipkt_{class,9171,C671,C971}.c/h, hdmi_spec.h,
  nvtiming.h, cl9171.h, ctrl0073specific.h.

## Deliverable

Your ranked reading of L1–L5 (or better hypotheses), the exact experiment
or source audit you'd run next for each, and — if you find it — the
specific RM-visible input that gates the deep-colour TMDS clock derivation.
Everything else in this mystery is measured and pinned; the clock is the
last mask on the table.
