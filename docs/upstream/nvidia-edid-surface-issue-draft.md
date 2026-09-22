<!--
RAW MATERIAL for Daniel's edit pass — not for posting as-is.
Everything below the ===== line is the draft body in Daniel's voice
(one sentence per line, no hard wraps, no mid-sentence em dashes).
Fill the single bracketed [GPU model] before posting.
Target: new issue at https://github.com/NVIDIA/open-gpu-kernel-modules/issues
Nothing is posted until Daniel posts it himself in the browser.
Suggested title:

615.71.09 narrows what the EDID declares across independent axes: HDMI 1.4 3D absent, deep colour trained at 10-bit, mode list pruned (siblings #1348, #1369, #1184)

================================================================================
-->

I run an NVIDIA card on Linux against a 2012 Sony 3DTV (KDL-46HX855, HDMI 1.4a), and I keep measuring the same shape of problem: **the sink declares a capability in its EDID, and the NVIDIA stack delivers less than what was declared**.

This is not one bug but one behaviour showing up on independent axes. I can measure three of them on my own bench, and this tracker already holds more, reported by other people, on other GPUs, on other monitors.

**Measured on my bench (driver 615.71.09, kernel 7.0.10, same machine, same TV).**

**1. Mode list narrowing.** The same EDID gives nouveau 51 modes and gives nvidia-drm 17. Detail in #1382.

**2. HDMI 1.4 3D modes never surface.** The TV declares its stereo layouts in the HDMI VSDB (structure-all bitmask, 3D mask, per-VIC detail entries, byte-verified by me against my set's own EDID dump). NVKMS parses none of it, so no DRM_MODE_FLAG_3D mode can ever exist, and the stereo_allowed gate has nothing to admit. With my community patch that mirrors the DRM core's do_hdmi_vsdb_modes() in the open glue, the same sink goes from 17 modes / 0 stereo to **39 modes / 22 stereo** (7 frame-packing, 8 top-and-bottom, 7 side-by-side-half). Patch, design document and measured A/B are posted on #1382: https://github.com/NVIDIA/open-gpu-kernel-modules/issues/1382#issuecomment-5771464134

**3. Deep colour trained down.** The EDID declares DC_36bit. The driver reports max bpc 16 upward to DRM, and debugfs shows output_bpc Maximum: 12. The TV still receives **10-bit**. The AMD card in the same machine drives the same model of TV at **12-bit**, with both links live at the same time, and I read both depths on the TV's own OSD. Windows on this same NVIDIA card drives 12-bit as well. So the narrowing is Linux driver policy, not the card, not the cable, not the sink.

**Same shape, reported by others on their own hardware.**

- **#1348** (same driver, 615.71.09): an HF-VSDB field (DSC_MaxSlices) mis-parsed, 7 declared slices read as 12, forcing YCbCr 4:2:2 limited where the link should carry the full format. Filed 2026-09-10, no maintainer reply yet.
- **#1369**: a mode pruned after the sink power-cycles, with an identical EDID, where Windows is unaffected.
- **#1184**: the EDID's Max_FRL_Rate ignored, capping the link at 4K60.
- **#779, #933, #1285**: HDR never activates, HDR properties missing, or the Colorspace atomic commit rejected with EINVAL.
- **#1101**: HDR DRM properties absent on force-enabled connectors, reported fixed in 610.43.02, which at least shows the open glue can expose the full property surface when the closed side provides the data.

**Why HDR belongs on this ticket.**

The stack of standards that carries HDR over HDMI shares the same machinery as my three symptoms.

ITU-R BT.2100 defines HDR television image parameters at 10- and 12-bit precision (current edition BT.2100-3, February 2025: https://www.itu.int/rec/R-REC-BT.2100-3-202502-I/en).

HDMI 2.0a (HDMI Forum, April 2015) added HDR transport to the link layer by referencing CEA-861.3: https://hdmiforum.org/hdmi-forum-inc-release-2-0a-specification/

CTA-861.3-A defines HDR signalling in the EDID (HDR Static Metadata Data Block) and on the wire (Dynamic Range and Mastering InfoFrame): https://shop.cta.tech/products/cta-861-3

The classic HDR10 wire format is 10-bit PQ samples carried in a **12-bit YCbCr 4:2:2 container**. So a driver that clips wire depth to 10 bits, and that mis-parses EDID capability blocks, sits directly under both my deep-colour finding and the HDR activation failures above.

One honest scope note: I do not own an HDR display, so the HDR connection is argued from the specifications and from the sibling reports on this tracker, not measured on my bench. The deep-colour finding itself is measured, on the TV's own OSD, with two other stacks as controls.

**What I would like from NVIDIA.**

1. Which of these axes should live in NVKMS versus the open glue, and would glue-side contributions be accepted for the parts the community can reach? The patch on #1382 proves the glue lane is real and measurable.
2. What capability model does NVKMS's EDID parser actually use? A short statement would let the community write fixes against the real policy instead of reverse-engineering it one symptom at a time.

Full measurement records (EDID dumps, OSD-confirmed A/B, run logs, patch, design documents): https://github.com/danielcamposramos/sony-bravia-linux — see docs/research/liverecon/nv-vs-amd-deepcolor-osd-2026-09-22.md and docs/upstream/nvidia-615.71.09-hdmi-3d-vsdb-synthesis-design-2026-09-22.md.

My machine: NVIDIA **[GPU model]**, driver 615.71.09, kernel 7.0.10+deb14.

Prepared with AI assistance; every number above was measured or byte-verified on my hardware, and every citation re-read, before posting.
