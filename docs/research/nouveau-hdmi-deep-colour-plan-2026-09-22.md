# nouveau HDMI deep-colour hardware plan (2026-09-22)

## Question and bounded answer

Can the local GA106 running nouveau train the Sony KDL-46HX855 at 12 bits?

Yes, this is testable with the hardware already present. The test does not need
an HDR display: it asks only whether nouveau can carry ordinary SDR RGB over a
12-bpc HDMI link. The television's signal-information OSD is the acceptance
instrument, with amdgpu and proprietary NVIDIA on the same sink as measured
controls.

This result must not be called HDR. It establishes deep-colour transport, one
necessary part of both native HDR and high-precision HDR-to-SDR output.

## Fixed bench and controls

- motherboard: ASUS TUF GAMING X570-PLUS/BR;
- CPU/control GPU: Ryzen 5 5500G (Cezanne amdgpu);
- GPU under test: GALAX RTX 3060, GA106, 12 GB;
- sink: Sony KDL-46HX855;
- HX855 EDID identity on the AMD-connected TV input (HDMI source physical
  address 1.0.0.0):
  `fbe6a3b455e69eab37f36bd0e7b0084a4d105c2adba101e37f0d5309c0a8eadc`;
- HX855 EDID identity on the NVIDIA-connected TV input (source physical
  address 3.0.0.0):
  `4f6cc1c8b7ce1700f93ef13c76c490ea985752edadd05c64179ae169e69d5dc9`;
- kernel under test: `7.0.10+deb14-amd64`;
- existing controls on the same television: amdgpu reports 12-bit at
  1920x1080p60; proprietary NVIDIA reports 10-bit; Windows on the same NVIDIA
  card reports 12-bit.

The full control measurement is in
[`liverecon/nv-vs-amd-deepcolor-osd-2026-09-22.md`](liverecon/nv-vs-amd-deepcolor-osd-2026-09-22.md).

## Why 1080p60 at 12 bpc is a valid target

Both input-specific EDIDs have identical timing/capability payloads: their only
byte differences are the HDMI VSDB source physical address (1.0.0.0 versus
3.0.0.0) and the extension checksum that follows from it. The NVIDIA-input
hash is therefore the live-test gate; the AMD-input hash is the control. Their
HDMI VSDB declares `DC_30bit`, `DC_36bit`, `DC_Y444`, and a 225 MHz maximum
TMDS clock. For RGB 4:4:4 deep colour:

```text
1920x1080p60 pixel clock       = 148.500 MHz
12-bpc RGB multiplier          = 12 / 8 = 1.5
required TMDS character rate   = 222.750 MHz
sink-declared maximum          = 225.000 MHz
remaining margin               =   2.250 MHz (1.0%)
```

The mode fits, but only narrowly. The experiment therefore holds mode, cable,
sink input, and colour format fixed and changes only link depth. It must not
round either rate before comparison.

## Source findings

Audited locally in Linux 7.0.10 and cross-checked in 7.3-rc4:

1. `nouveau_connector_detect_depth()` uses `display_info.bpc` when the EDID
   supplies that base-field value, but otherwise defaults non-LVDS outputs to
   8 bpc. It never converts the HDMI VSDB deep-colour flags into the maximum
   usable HDMI depth.
2. `nouveau_conn_attach_properties()` does not attach the standard `max bpc`
   property.
3. `nv50_outp_atomic_check()` copies `display_info.bpc` to `asyh->or.bpc` and
   only performs depth/bandwidth reduction for DisplayPort. TMDS has no
   deep-colour selection or bandwidth validation.
4. `nv50_sor_atomic_enable()` leaves TMDS at
   `NV837D_SOR_SET_CONTROL_PIXEL_DEPTH_DEFAULT`; only its DP branch maps bpc
   to an explicit SOR depth.
5. The display class headers already define
   `NV837D_SOR_SET_CONTROL_PIXEL_DEPTH_BPP_36_444` and the C37D/C57D/CA7D
   `...BPP_36_444` head values. The C37D/C57D and CA7D translation switches
   currently cover 18-, 24-, and 30-bpp only.
6. Nouveau enables an HDMI General Control Packet in the generation-specific
   HDMI control path, but the public source does not label or select its
   deep-colour `CD`/`PP` fields. It is not yet proven whether the display
   engine derives them from SOR/head pixel depth.

The old “we don't support more than 10 anyway” comment belongs to the
DisplayPort depth-reduction branch. It is not an HDMI-wide clamp.

## Experimental patch shape

The first hardware probe is deliberately smaller than an upstream series:

1. attach `max bpc` with range 8–12 to HDMI-A connectors;
2. for HDMI TMDS, clamp the request to EDID-supported RGB depths (12, 10, 8);
3. reject or step down a depth whose exact TMDS rate exceeds the sink's
   declared maximum;
4. map 12 bpc to `BPP_36_444` in the SOR and C37D/C57D/CA7D head paths;
5. print one rate-limited debug record containing requested bpc, selected bpc,
   mode clock, and calculated TMDS rate.

This is a hardware-discovery patch, not yet an upstream submission. In
particular, a positive OSD result would show that the hardware derives the
General Control Packet correctly; a stable picture with an 8- or 10-bit OSD
would isolate the missing GCP programming instead of disproving the depth
register work.

The patch is additive to nouveau's existing, already hardware-proven HDMI 3D
implementation. It does not replace or bypass `stereo_allowed`, the HDMI VSIF,
or nouveau's frame-packing timing transform. The preserved experimental delta
is
[`nouveau-hdmi-deep-colour-experimental.patch`](../upstream/nouveau-hdmi-deep-colour-experimental.patch).

Prepared but not loaded on 2026-09-22:

```text
source tree: /K3D/temp/k317/linux-source-7.0
build:       make -j8 M=drivers/gpu/drm/nouveau modules
result:      clean compile
artifact:    /K3D/temp/k317/nouveau-hdmi-deep-colour-experimental.ko
vermagic:    7.0.10+deb14-amd64 SMP preempt mod_unload
SHA-256:     0da7edbe7dad4e9db30adaa460dbf6b41f7f5a2b5a40dc3d6766abe5d7f9f40d
state:       never loaded; hardware result pending
```

## Safe execution

Reuse the already proven nouveau module-swap transaction:

1. capture kernel, EDID hash, connector inventory, and stock property set;
2. verify the experimental module's vermagic equals the running kernel;
3. stop GPU-using containers and the desktop, install the temporary NVIDIA
   autoload guard, and release the proprietary modules;
4. load the experimental nouveau module and wait for its DRM card;
5. select only the NVIDIA-connected HDMI connector whose EDID hash matches the
   fixed 3.0.0.0 input identity above;
6. set the connector's `max bpc = 12`, then perform the 1920x1080p60 modeset
   and show a deterministic gradient for 90 seconds (the current smoke client
   uses the legacy property/modeset ioctls on nouveau's atomic-backed KMS;
   an upstream test should also cover one explicit atomic transaction);
7. Daniel reads and records the television OSD while the second AMD control
   head and remote shell remain available;
8. timeout or any exit unloads nouveau, removes the guard, restores NVIDIA,
   the desktop, services, and the prior Docker containers;
9. capture the post-restore state.

Do not run this unattended. The existing harness has already demonstrated
recovery from failed module loads and a pictureless output, but the human OSD
observation is part of the measurement.

Run 1 preflight (03:41–03:42 UTC-3) did not reach a modeset: the experimental
module loaded and exposed all four GA106 connectors, but the harness used
`test -s` on the sysfs EDID attribute. Sysfs reports `st_size=0` even when the
read returns all 256 EDID bytes, so the correct connector was skipped. The
same run also showed that this `modetest` build treats `-D /dev/dri/card1` as a
bus ID, not a device path. The harness now gates on readable bytes plus the
exact SHA-256 and inventories with `-M nouveau`. NVIDIA, the desktop, services,
and all six stopped containers restored normally. This run is harness evidence
only, not a deep-colour result.

Run 2 (deep12, 05:09:58–05:11:46 UTC-3) completed the full driver-side path
for the first time. The fixed harness worked end to end: the NVIDIA-input EDID
matched the gate hash exactly (`4f6cc1c8…e69d5dc9`), the inventory printed
connector 43 (HDMI-A-2) with the patch-attached `max bpc` property (id 44,
range 8–12), and the stock-nouveau stereo listing followed run19's proven
roster. The probe set `max bpc=12`, selected 1920x1080@60 (148.5 MHz pixel
clock, 222.75 MHz TMDS character rate at 36-bpp), and the modeset committed
with no driver-side error (`requested connector property max bpc=12`,
`modeset done (isolated)`). Sink testimony, recorded by Daniel at the set: the
HX855 displayed “incompatible signal detected, verify your output” — it saw
the changed wire and refused to frame it. At about 50 seconds into the
90-second hold Daniel ended the run deliberately (ctrl+alt+del) rather than
wait; the kernel/desktop restore ran during shutdown (`restored`), and the
journal shows a clean boot back onto the stock NVIDIA stack with zero
kernel-error lines from the experimental module (clean GSP bind under
RM 570.144, four planes, `fb1 = nouveaudrmfb`).

The restore was nevertheless **partial** and this is worth fixing before any
run 3: a `sh` process that dies to SIGTERM never runs its EXIT trap, and the
systemd-run unit received exactly that during the reboot. The module/desktop
half was restored by the reboot itself (nouveau is blacklisted at boot and the
guard lives in tmpfs `/run/modprobe.d`), but the docker half — which lives only
in the trap — was skipped. watchtower and open-webui recovered through their
own restart policies; n8n, mkvbuild, browserless and qdrant stayed down until
they were restarted manually post-boot from the harness's own recorded
container list (`/K3D/temp/nouveau-docker.containers`). No restore work may
live only in an EXIT trap for a run whose possible end is a reboot.

Measured finding: engaging the existing 36-bpp SOR/head values end to end is
necessary but **not sufficient**. The sink requires a correct General Control
Packet deep-colour indication to frame a 12-bit stream, and the current
experimental patch does not yet emit one [inferred from the sink refusal; no
wire analyzer]. This answers, by negative measurement, the exact open question
recorded in the source-findings section: the display engine does not derive a
valid GCP configuration from the SOR/head pixel depth on GA106. The matching
acceptance-matrix row is “sink loses picture → rollback”; kernel and desktop
came back clean, with the docker gap above recorded as a harness defect, not a
driver event.

Harness lesson: the home mirror is written only by the exit trap, so an
intentional reboot forfeits it. The live append target
`/var/log/nouveau-deep-colour-test.log` survived the reboot and is the run-2
narrative source; it is preserved in the repository as
[`tools/stereo-modeset/run20-nouveau-deep12-incompatible-2026-09-22.log`](../../tools/stereo-modeset/run20-nouveau-deep12-incompatible-2026-09-22.log)
(it contains the run-1 preflight and run-2 narratives in sequence). Future
iterations should tee or fsync continuously so an abrupt stop can no longer
cost a run's record, and move restore work out of the shell trap into a
systemd-managed path (an `ExecStopPost=` restorer on the run unit, or a
boot-triggered unit keyed on the state file) so the docker pause always gets
undone no matter how the run ends.

## GCP route: located end to end (2026-09-22)

The route chase commissioned after run 2 is complete. Every needed value is
public — NVIDIA's own open repository carries the full recipe — and the sink
refusal now has a fully sourced explanation.

**What the proprietary driver sends (readable code):**
`src/nvidia-modeset/src/nvkms-hdmi.c` `SendHdmiGcp()` builds the General
Control Packet as `{0x03, 0, 0, SB0, SB1, SB2, 0…}`:

- SB0 = `0x10` (Clear_AVMUTE) for an operating stream;
- SB1 = `CD | PP << 4`, with `CD = 0x6` (36 bpp) when the head's pixel depth
  is 36_444 RGB (not YCbCr 4:2:2, not FRL), and `PP` the pixel-packing phase:
  if (hActive + hBackPorch) is even → phase 2, else phase 1;
- SB2 = `0x0` (reset default pixel-packing phase each frame edge).

Field constants are in `src/common/modeset/timing/nvtiming.h`
(`NVT_HDMI_COLOR_DEPTH_36 = 0x6`, `NVT_HDMI_GCP_SB1_CD_SHIFT = 0`,
`NVT_HDMI_GCP_SB1_PP_SHIFT = 4`) and `src/common/inc/hdmi_spec.h`
(`HDMI_GENCTRL_PACKET_MUTE_ENABLE = 0x01`, `_DISABLE = 0x10`).
For 1080p60 the parity rule gives PP = 2, so SB1 = `0x26`.

**Where it lands on the silicon:**
`src/common/modeset/hdmipacket/` — the class table in `nvhdmipkt_class.h` maps
GA102/GA106 (Ampere) to class `NVHDMIPKT_C671`; `nvhdmipkt_C671.c` delegates
GENERAL_CONTROL writes to `hdmiPacketWrite9171()`, which stores SB0/SB1/SB2
into `NV9171_SF_HDMI_GCP_SUBPACK(head)` and enables the slot via
`INFO_CTRL(head, IDX_GCP=3)`. NVIDIA's own register header
`src/common/sdk/nvidia/inc/class/cl9171.h` grounds the layout:
`INFO_CTRL(i,j) = base + head*0x400 + j*64`, bit 0 = ENABLE;
`GCP_SUBPACK(i) = base + 0xCC + head*0x400`, SB0 bits 7:0, SB1 bits 15:8,
SB2 bits 23:16 (`SB0_CLR_AVMUTE = 0x10`).

**What nouveau already does with that same slot:**
`nvkm/engine/disp/gv100.c` `gv100_sor_hdmi_ctrl()` (inherited by GA10x as
`ga102.c: .hdmi = &gv100_sor_hdmi`) already emits this very GCP at the
generation's SF aperture base (0x6f instead of cl9171's 0x69 — the
block-internal layout is identical, and the working AVI at 0x6f0000 / VSI at
0x6f0100 prove the base on this hardware): it disables the slot at
`0x6f00c0 + head*0x400`, writes the **fixed constant `0x00000010`** to
`0x6f00cc`, and re-enables. That constant decodes (same bitfields) as
SB0 = Clear_AVMUTE, SB1 = CD-not-indicated / PP 0 — an 8-bpc-only GCP.
So on the direct path the GCP exists and declares nothing.

**What happens on our GSP path:** under GSP firmware, `ga102_disp_new()`
routes to `r535_disp_new()`, whose `r535_sor_hdmi_ctrl` performs only the
`NV0073_CTRL_CMD_SPECIFIC_SET_HDMI_ENABLE` RM call and never touches the GCP
slot, while AVI/VSI on the very same table are still written by direct MMIO
(`gv100_sor_hdmi_infoframe_*`). Run 2 therefore emitted **no GCP at all**
on GA106 — the sink faced a 36-bpp-packed stream with zero deep-colour
declaration, and “incompatible signal” is its exact expected answer.

**Patch v2 shape** (no new hardware question beyond the sufficiency test):

1. one helper computing the SUBPACK dword from (selected pixel depth, colour
   format, hActive, hBackPorch), reproducing NVKMS's rule bit for bit
   (`0x00002610` on this mode);
2. call it from both ctrl sites: replace the fixed constant in
   `gv100_sor_hdmi_ctrl` (direct path), and write the slot by MMIO in
   `r535_sor_hdmi_ctrl` after the RM enable (GSP path — MMIO writes to this
   aperture are exactly what that path already does for AVI/VSI);
3. plumb the depth/timings into both call sites — the current func signature
   carries only `(enable, max_ac_packet, rekey)`, so the depth comes from the
   atomic head state the experimental patch already extends.

Out of scope for v2, mirroring NVIDIA's visible code: 10 bpc (NVKMS fills CD
only for 36 bpp — no 30-bpp GCP branch is public), which also shelves the
10-bpc discriminator run: it would fail for the same missing-GCP reason.

**What run 3 would then test:** whether the SOR `PIXEL_DEPTH_BPP_36_444`
selection (already in the experimental patch) additionally derives the TMDS
character rate of 222.75 MHz on its own, with GCP as the pure declaration —
[inferred], because NVIDIA's open halves contain no deep-colour TMDS clock
scaling anywhere near this machinery (only FRL link-rate code, unrelated to
the TMDS character clock). Acceptance: OSD reports 12-bit at 1080p60.

**Patch v2 built (2026-09-22):** the shape above is implemented exactly as
specified, compiled clean against the same 7.0.10 tree as v1
(`make -j8 M=drivers/gpu/drm/nouveau modules`). Both the v1→v2 delta and the
combined patch were round-trip verified against a pristine base reconstructed
by reverse-applying v1.

```text
patch:        docs/upstream/nouveau-hdmi-deep-colour-experimental-v2.patch
              (pristine 7.0.10 base; includes v1, do not stack them)
patch SHA-256: ef91566df88d689430a6f9cd26ec85a58591a3245e17bca1bec2f7d4066354f6
artifact:     /K3D/temp/k317/nouveau-hdmi-deep-colour-gcp-experimental.ko
vermagic:     7.0.10+deb14-amd64 SMP preempt mod_unload
module SHA-256: 1d2f3dc41fdeb9a49b8cdc8329ed1964ae27c6b7235425b40d1dcdf3667da81f
state:        built, never loaded; hardware result pending run 3
```

Run 3 must pass
`--setenv=NOUVEAU_TEST_KO=/K3D/temp/k317/nouveau-hdmi-deep-colour-gcp-experimental.ko`
on the systemd-run line: the harness default still points at the v1 module,
and environment variables do not cross systemd-run by default.

**Run 3 measured (2026-09-22 09:09:53–09:11:49 UTC-3):** the v2 GCP module
(`nouveau-hdmi-deep-colour-gcp-experimental.ko`, sha256 `1d2f3dc4…a81f`)
completed the full driver-side path again — EDID gate hash matched, `max
bpc=12` accepted, the 1080p60 36-bpp modeset committed, zero nouveau errors
in the kernel log across load, hold, and restore. The sink answered with the
same “incompatible signal” OSD for the entire hold. No reboot this run: the
hardened harness restored the NVIDIA stack, desktop, services, and all six
stopped Docker containers by itself — the run-2 harness defect is fixed and
measured fixed. Narrative:
[`tools/stereo-modeset/run21-nouveau-deep12-gcp-incompatible-2026-09-22.log`](../../tools/stereo-modeset/run21-nouveau-deep12-gcp-incompatible-2026-09-22.log).

**Post-run-3 correction and narrowing (source-only, same evening).**
Cross-checking NVIDIA's evo3 code (`nvkms-evo3.c`) against what was actually
emitted corrects a phrasing this document has used since the plan stage:

- On the C37D/C57D cores that GA106's display runs, the `SOR_SET_CONTROL`
  method has **no** PIXEL_DEPTH field (clc37d.h: OWNER, PROTOCOL,
  DE_SYNC_POLARITY, PIXEL_REPLICATE only), matching NVKMS's
  `EvoSORSetControlC3()`. Nouveau's `sorc37d_ctrl()` pushes its control
  dword without ever merging the NV837D depth bits — that merge exists only
  in `sor507d.c`, which this hardware does not use. Runs 2/3 therefore
  already matched NVIDIA exactly: link depth reaches the hardware through
  the head `OUTPUT_RESOURCE` PIXEL_DEPTH field (`nvEvoGetPixelDepthC3()`),
  which v1 had already programmed correctly (SOR code 8 → head code 7 =
  36_444). Earlier wording here about “selecting 36-bpp SOR/head values”
  should read “head output-resource depth”; the SOR dword was always
  NVIDIA-conformant.
- NVKMS's `SET_HDMI_SINK_CAPS` RM call forwards SCDC/scrambling/FRL caps
  only — no deep-colour bits — so it cannot be a hidden gate for the rate.
- hdmipkt's control write for GCP is a plain `INFO_CTRL.ENABLE` bit,
  identical to Nouveau's bit-0 mask writes; CHKSUM/OTHER fields do not
  apply to GCP.
- NVKMS contains no other TMDS rate-related deep-colour programming
  anywhere open; the character clock must be derived inside closed
  RM/GSP from the head/OR state [inferred from absence].

The failure split now has exactly two branches, both consistent with the
same sink message: **(a)** the CPU-side GCP MMIO write did not stick under
GSP firmware ownership of the SF aperture — run 3 would then be
wire-identical to run 2 and taught nothing new — or **(b)** the GCP landed
but the TMDS character rate stayed at 148.5 MHz, in which case a
deep-colour-declared stream at 8-bpc timing is precisely what this sink
calls “incompatible”. The OSD reports one message for both classes; a
register readback separates them.

**Patch v3 built (2026-09-22) — instrumentation only,** no new hardware
behaviour: `gv100_sor_hdmi_gcp()` prints the written subpack plus readbacks
of the GCP subpack and control registers and the sibling AVI control and
subpack at the same aperture (proving both that the write landed and that
the aperture is live during that modeset); `nv50_sor_atomic_enable()`
prints the selected non-8-bpc TMDS depth and mode clock. Run-4 evidence
splits the branches: GCP subpack reading back `0x00002610` with control
enabled means branch (b) — the GCP is on the wire and the chase moves to
GSP RM clock derivation; anything else is branch (a) and the aperture
needs a different route.

```text
patch:        docs/upstream/nouveau-hdmi-deep-colour-experimental-v3.patch
              (pristine 7.0.10 base; cumulative, includes v1+v2)
patch SHA-256: 48494cfe581da4ee216f993e8a652502688e837e328b90d99b89b9f4988ec541
artifact:     /K3D/temp/k317/nouveau-hdmi-deep-colour-gcp-dbg-experimental.ko
vermagic:     7.0.10+deb14-amd64 SMP preempt mod_unload
module SHA-256: 68768c48ecf7e901330655a9aa2f7d5a1616f3a8b49a2c549073b7444748ded4
state:        built, never loaded; hardware result pending run 4
```

Run 4, on the owner's explicit go only:

```bash
sudo systemd-run --setenv=NOUVEAU_TEST_KO=/K3D/temp/k317/nouveau-hdmi-deep-colour-gcp-dbg-experimental.ko \
  --unit=nouveau-deep-colour-test --collect \
  sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nouveau-test.sh deep12
```

**Run 4 measured (2026-09-22 09:27:59–09:29:55 UTC-3):** the instrumented
v3 module (sha256 `68768c48…ded4`) repeated the full driver-side pass —
EDID gate matched, `max bpc=12`, 1080p60 36-bpp modeset committed, zero
kernel errors, harness restored everything unattended — and the sink again
answered “incompatible signal” for the whole hold. But this time the kernel
log spoke back. The instrumentation printed, in order:

```text
nouveau: disp: gcp: head 0 subpack w=0x00000010 r=0x00000010 ctrl=0x00000001 avi_ctrl=0x00000200 avi_sp0=0x0828121d
drm: deep-colour probe: TMDS bpc=12 sor-depth=0x8 clock=148500 kHz
nouveau: disp: gcp: head 0 subpack w=0x00002610 r=0x00002610 ctrl=0x00000001 avi_ctrl=0x00000200 avi_sp0=0x0828121d
```

What this resolves:

1. The GCP write **lands and holds under GSP**: after the deep-colour
   modeset the subpack read back `0x00002610` (SB0 Clear_AVMUTE, SB1
   CD=6|PP=2) with the slot enable bit set. Branch (a) — a dropped or
   shadowed MMIO write — is dead for the payload we wrote.
2. NVIDIA's proprietary stack itself sends GCP by the same MMIO slot write
   under GSP (NVKMS `SendHdmiGcp()`, called from the HDMI audio enable
   flow at nvkms-hdmi.c:1381; GSP is mandatory on that stack), so a
   register write at this aperture is the production wire route, not a
   dead register. The GCP declaration was therefore on the wire [inferred
   from landed-register plus production-path identity].
3. The sibling readback exposed GSP ownership of the aperture: the AVI
   subpack payload persisted (`avi_sp0=0x0828121d`, written by nouveau
   first) but the AVI enable bit read back clear (`avi_ctrl=0x00000200`,
   only the CHKSUM_HW reset default) — RM's `SET_HDMI_ENABLE` handler
   sanitizes the slot control words from its own state. Our GCP write
   survives precisely because v2/v3 placed it **after** the RM call; that
   ordering is load-bearing, not stylistic.
4. By elimination the refusal is branch (b): the stream declared 36-bpp
   deep colour while the TMDS character rate never rose to 222.75 MHz —
   the sink measured an 8-bpc-rate link against a 36-bpp declaration and
   called it “incompatible”, which is exactly correct of it [inferred; no
   wire analyzer].

For the clock side, the open NVIDIA halves contribute one more narrowing:
NVKMS's IMP validation block (nvkms-modeset.c:1391-1476) feeds
`pixelDepth` and the timings into the closed IMP/downgrade layer, and no
open code anywhere programs a TMDS character-rate clock for deep colour;
the C37D/C57D core channel exposes no SOR clock method. The derivation is
entirely RM/GSP-internal. Two RM calls in the neighbourhood were checked
and ruled different-but-unhelpful: `SET_HDMI_SINK_CAPS` (no deep-colour
bits) and `CTRL_HDMI` “prior to every modeset” (not used by NVKMS's HDMI
code at all — its only RM calls on this path are `SET_HDMI_ENABLE`, the
sink-caps mirror, and the audio/ELD ones, all of which nouveau matches or
which do not gate video transport).

Next levers, handed to the Codex partner for a second pair of eyes (full
briefing in
[`nouveau-deep-colour-handoff-to-codex-2026-09-22.md`](nouveau-deep-colour-handoff-to-codex-2026-09-22.md)):
find what input GSP RM needs to derive the 222.75 MHz character clock —
candidates include the proprietary-oracle register diff (the local nvidia
module exposes `hdmi_deepcolor:bool`, so a Linux-side known-good 12-bpc
wire can be produced and its aperture/SOR state dumped for comparison),
and auditing how GSP RM learns link depth — most plausibly from the very
head OUTPUT_RESOURCE pixel depth nouveau already sends, in which case the
clock derivation gate is a still-missing RM-visible input.

Narrative log:
[`tools/stereo-modeset/run22-nouveau-deep12-gcpdbg-incompatible-2026-09-22.log`](../../tools/stereo-modeset/run22-nouveau-deep12-gcpdbg-incompatible-2026-09-22.log).

## Staged harness modes

The harness modes are deliberately staged:

```text
deep12  = ordinary 1920x1080p60 SDR + requested 12-bpc link
sbs12   = proven nouveau SBS-half 3D path + requested 12-bpc link
tab12   = proven nouveau top-and-bottom 3D path + requested 12-bpc link
fp12    = proven nouveau frame-packing 3D path + requested 12-bpc link
```

Run `deep12` first. Only a stable 12-bit result advances to the combined modes,
which test coexistence of the 3D VSIF and deep-colour General Control Packet.
At the same 148.5 MHz base transport rate, the relevant 1080p60 SBS/TaB and
1080p24/720p60 frame-packing streams all require 222.75 MHz at 12 bpc and fit
under the same 225 MHz sink ceiling.

## Cross-driver combined controls

The comparison must preserve each driver's 3D correction instead of testing
deep colour in isolation:

| driver | 3D layer used | deep-colour layer | expected measurement |
|---|---|---|---|
| amdgpu | Adrian Betschart's owner-verified v3 HDMI 1.4 3D series | existing amdgpu 12-bpc path | 3D engaged and OSD 12-bit |
| nouveau | stock, already-proven 3D/VSIF/frame-packing path | this experimental patch | question under test |
| proprietary NVIDIA | project's v2 HDMI-VSDB 3D synthesis patch | closed NVKMS policy | 3D modes exposed; current control OSD 10-bit |

The proprietary open glue cannot independently repair its 10-vs-12 choice;
that policy remains inside NVKMS. It is still a valuable behavioural control.

## Acceptance matrix

| observation | meaning | next action |
|---|---|---|
| stable picture, OSD 12-bit | SOR/head selection and GCP generation work on GA106 | split, clean, test older/newer display classes, propose upstream |
| stable picture, OSD 10-bit or 8-bit | scanout survived but the requested wire depth was not achieved | trace GCP/deep-colour state and achieved link selection |
| sink loses picture | depth/packing/link state is inconsistent | automatic rollback; inspect kernel log and class mapping |
| property or modeset request rejected | property/EDID/bandwidth validation defect | fix state selection before touching packet hardware |
| module does not bind | build/vermagic/firmware problem, no display conclusion | restore stock stack and repair the harness/build only |

## Evidence that must be saved

- exact patch and source commit/tree identity;
- module SHA-256 and vermagic;
- pre/during/post `modetest -c` or `drm_info` output;
- EDID bytes, decode, and SHA-256;
- exact atomic request and return code;
- kernel log spanning load, modeset, timeout, unload, and restore;
- Daniel's timestamped OSD observation, including colour format and bit depth;
- restoration proof for NVIDIA, SDDM, services, and Docker.

## Provenance

Daniel Campos Ramos directed the experiment, owns the hardware, supplied the
cross-driver observations, and is the human acceptance observer. Kimi K3,
working through Claude Code CLI with the Ollama provider, performed the first
nouveau/HDR source survey. GPT-5.6 Sol, working through Codex CLI, corrected
the DP-only clamp interpretation, traced the HDMI bpc/SOR/head path, and
designed this bounded hardware experiment. Claims are attributed to source or
measurement; the untested GCP behaviour remains explicitly a hypothesis.
