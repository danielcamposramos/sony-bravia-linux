# Signal Ledger — Deep Color pilot

Generated from the canonical TOML entries. Do not edit this view.
Ledger digest: `c3a19265cbd6b7a1ecd29b462d822ddf325306864e3ca176649ebbc3ff9a9838`.

| Claim | Status | Basis | Domain | Assertion |
|---|---|---|---|---|
| `SBL-DC-0001` | supported | `normative-citation` | `standard` | For HDMI Deep Color, the General Control Packet carries the color-depth and pixel-packing-phase fields used to declare the transmitted pixel encoding depth. |
| `SBL-DC-0002` | supported | `instrument-measurement` | `driver` | On the GA106 run-23 test window, nouveau requested 12 bpc and the logged active HDMI-audio-path GCP state after enable was subpack=0x01002610; a later enable=0 line records teardown. |
| `SBL-DC-0003` | supported | `human-observation` | `visible-sink` | Daniel observed the HX855 OSD report 12-bit and a stable green-to-purple gradient over black and white squares, with no incompatible-signal OSD — passed with full colors (pun intended). |
| `SBL-DC-0004` | supported | `instrument-measurement` | `driver` | During the run-24 verification session, NVIDIA 615.71.09 reported max_output_color_depth=12 and hdmi_deepcolor=Y after reload. |
| `SBL-DC-0005` | supported | `human-observation` | `visible-sink` | Daniel observed the HX855 OSD report 12-bit during the stable NVIDIA run-24 session after the output-depth cap was set to 12. |
| `SBL-DC-0006` | supported | `analysis` | `driver` | Under the HDMI 1.4b GCP field mapping, the active software-visible run-23 payload 0x002610 encodes the 12-bpc color-depth and packing-phase state; this does not prove packet emission on the cable by itself. |
| `SBL-DC-0007` | undetermined: untested | `scope-record` | `scope` | This project has not tested physical 16-bpc output. |
| `SBL-DC-0008` | undetermined: untested | `scope-record` | `scope` | This project has not physically verified native HDR output. |

## Claim records

### SBL-DC-0001 — HDMI Deep Color is declared through GCP color-depth fields

- Authority: **supported** (`SUPPORTED`)
- Basis / domain: `normative-citation` / `standard`
- Scope: HDMI Deep Color signalling; this claim does not reproduce licensed specification text.
- Entry hash: `f9623140c60d9eb72a4f8640e50dd8e557d298f15e4600e6f943e5a024dc0c10`
- Normative citation: High-Definition Multimedia Interface Specification 1.4b, section 6.5.3

For HDMI Deep Color, the General Control Packet carries the color-depth and pixel-packing-phase fields used to declare the transmitted pixel encoding depth.

### SBL-DC-0002 — nouveau run 23 retained 12-bpc GCP state after the audio path

- Authority: **supported** (`SUPPORTED`)
- Basis / domain: `instrument-measurement` / `driver`
- Scope: GALAX RTX 3060 GA106, nouveau experimental v4, Sony KDL-46HX855, 1920x1080p60 SDR RGB.
- Entry hash: `0f8092d0715a203dfc19aa3d138f6ce21c2b7f104e208c1144e342704cb44c3a`
- Artifact: [run-23 kernel and harness record](../../../tools/stereo-modeset/run23-nouveau-deep12-gcp-audio-preserve-pass-2026-09-22.log) — `412fb1cc1f9fada127506e5693aecea107104f2d46d233331f8732c2bb400d7e`

On the GA106 run-23 test window, nouveau requested 12 bpc and the logged active HDMI-audio-path GCP state after enable was subpack=0x01002610; a later enable=0 line records teardown.

### SBL-DC-0003 — The HX855 visibly accepted nouveau 12-bpc output

- Authority: **supported** (`SUPPORTED`)
- Basis / domain: `human-observation` / `visible-sink`
- Scope: The visible result on Daniel's Sony KDL-46HX855 during nouveau run 23; it is not a native-HDR claim.
- Entry hash: `d9097d9b440bddb718e55266f49dac207cf71092942ea8095110182d6b7ecaa5`
- Observer: Daniel Campos
- Context links: `SBL-DC-0002`
- Artifact: [contemporaneous owner-observation record](../../../tools/stereo-modeset/run23-nouveau-deep12-gcp-audio-preserve-pass-2026-09-22.log) — `412fb1cc1f9fada127506e5693aecea107104f2d46d233331f8732c2bb400d7e`

Daniel observed the HX855 OSD report 12-bit and a stable green-to-purple gradient over black and white squares, with no incompatible-signal OSD — passed with full colors (pun intended).

### SBL-DC-0004 — NVIDIA run 24 loaded a 12-bpc output-depth cap

- Authority: **supported** (`SUPPORTED`)
- Basis / domain: `instrument-measurement` / `driver`
- Scope: GALAX RTX 3060 GA106, NVIDIA open kernel modules 615.71.09, Sony KDL-46HX855, 1920x1080p60 SDR RGB.
- Entry hash: `49ce77fa9748c2e3e582dd183348fec13f4863f9381b290b8d14b4bf23fbc077`
- Artifact: [run-24 module-state and harness record](../../../tools/stereo-modeset/run24-nvidia-deepcolor-param12-pass-2026-09-22.log) — `d3eba2ed94969fd59dad9770b364e60fd8a8519cff078850ca60c696ad19da10`

During the run-24 verification session, NVIDIA 615.71.09 reported max_output_color_depth=12 and hdmi_deepcolor=Y after reload.

### SBL-DC-0005 — The HX855 visibly accepted NVIDIA 12-bpc output

- Authority: **supported** (`SUPPORTED`)
- Basis / domain: `human-observation` / `visible-sink`
- Scope: The visible result on Daniel's Sony KDL-46HX855 during NVIDIA run 24; it is SDR RGB and not a native-HDR claim.
- Entry hash: `33f4d873f7e16a8ac0e7ccddd1e8463b6ec14ac9723722dcfe3914f4f93a47a1`
- Observer: Daniel Campos
- Context links: `SBL-DC-0004`
- Artifact: [contemporaneous owner-observation record](../../../tools/stereo-modeset/run24-nvidia-deepcolor-param12-pass-2026-09-22.log) — `d3eba2ed94969fd59dad9770b364e60fd8a8519cff078850ca60c696ad19da10`

Daniel observed the HX855 OSD report 12-bit during the stable NVIDIA run-24 session after the output-depth cap was set to 12.

### SBL-DC-0006 — The active run-23 GCP value encodes a 12-bpc declaration

- Authority: **supported** (`SUPPORTED`)
- Basis / domain: `analysis` / `driver`
- Scope: Interpretation of the nouveau run-23 software-visible GCP slot; physical sink acceptance is recorded separately in SBL-DC-0003.
- Entry hash: `7fe314935e7b9782145669b0d012d982fd9fbe5f329c931647cea134d96e7367`
- Authority premises: `SBL-DC-0001`, `SBL-DC-0002`

Under the HDMI 1.4b GCP field mapping, the active software-visible run-23 payload 0x002610 encodes the 12-bpc color-depth and packing-phase state; this does not prove packet emission on the cable by itself.

### SBL-DC-0007 — Sixteen-bpc output remains untested on this bench

- Authority: **undetermined** (`UNTESTED`)
- Basis / domain: `scope-record` / `scope`
- Scope: Local hardware coverage only; the statement must not be generalized to all NVIDIA hardware or professional displays.
- Entry hash: `1881aa2fcc59c9a4ec61e049bc87b980ab09c0ed33e1eefd1ccb887745bc16d7`
- Missing precondition: No owned display or analyzer advertises and verifies HDMI DC_48 / 16-bpc input.
- Not claimed: This entry does not claim that 16-bpc output works, fails, or is supported by every relevant GPU generation.

This project has not tested physical 16-bpc output.

### SBL-DC-0008 — Native HDR output remains untested on this bench

- Authority: **undetermined** (`UNTESTED`)
- Basis / domain: `scope-record` / `scope`
- Scope: Local hardware coverage only; the HX855 is an SDR display even though it can report and accept 12-bit Deep Color.
- Entry hash: `76770e3f4176766d23992a77c30ca40e7882835206901ceb4abfe08e93a8543d`
- Missing precondition: Daniel does not own an HDR display or HDMI analyzer that can verify HDR metadata and rendered HDR behavior.
- Not claimed: This entry does not claim that HDR output works or fails on nouveau, NVIDIA proprietary drivers, or other systems.

This project has not physically verified native HDR output.
