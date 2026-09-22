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
6. atomically request `max bpc = 12` with 1920x1080p60 and show a deterministic
   gradient for 90 seconds;
7. Daniel reads and records the television OSD while the second AMD control
   head and remote shell remain available;
8. timeout or any exit unloads nouveau, removes the guard, restores NVIDIA,
   the desktop, services, and the prior Docker containers;
9. capture the post-restore state.

Do not run this unattended. The existing harness has already demonstrated
recovery from failed module loads and a pictureless output, but the human OSD
observation is part of the measurement.

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
| atomic request rejected | property/EDID/bandwidth validation defect | fix state selection before touching packet hardware |
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
