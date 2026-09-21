# DRAFT — GitHub issue for NVIDIA/open-gpu-kernel-modules — RAW MATERIAL for Daniel

Not for posting as-is. Daniel reviews, rewrites in his own words, and posts it himself at
https://github.com/NVIDIA/open-gpu-kernel-modules/issues. Style for his version: no bold,
one paragraph per line, no hard-wrapped lines. The patch referenced below is
`nvidia-615.71.09-hdmi-3d-contribution.patch` in this directory (applies clean against the
615.71.09 kernel-open tree, verified by dry-run).

Suggested title:
nvidia-drm: HDMI 1.4 3D modes are always pruned (stereo_allowed never set) — one-line glue fix, verified end-to-end

---

Environment: 615.71.09 kernel-open modules from Debian testing, kernel 7.0.10, GA106 desktop card, HDMI to a Sony KDL-46HX855 (2012, HDMI 1.4 3D; its EDID declares side-by-side half, top-and-bottom and frame packing).

What I expected: per HDMI 1.4 / CTA-861, SBS-half and top-and-bottom 3D modes are ordinary VIC link timings plus a 3D structure flag, announced with the HDMI Vendor Specific InfoFrame. In the DRM core, stereo modes from the EDID are kept only when the driver sets connector->stereo_allowed (drm_probe_helper.c, "mode_flags |= DRM_MODE_FLAG_3D_MASK"), and even then they are exposed only to clients that opt in with DRM_CLIENT_CAP_STEREO_3D (drm_connector.c, drm_mode_expose_to_userspace). So a compliant driver opts in once, and 2D-only userspace is unaffected.

What happens: nvidia-drm never sets it. The only occurrence of stereo_allowed in kernel-open is the client-cap getter in nvidia-drm-drv.c. Mode listing on my TV's connector returns 17 modes, 0 stereo, with or without the cap; the same sink under nouveau on the same GPU family returns 51 modes, 29 stereo, because nouveau sets the opt-in ("HDMI 3D support" in nouveau_connector.c).

The announcement pipe already ships in the driver: the NV_HDMI_VSIF_METADATA connector blob property (documented in nv_drm_common_ioctl.h as the 3-byte HDMI OUI plus infoframe body, up to 27 bytes) is created in nvidia-drm-drv.c and its payload is memcpy'd into modeSetConfig.hdmiVsifMetadata for NVKMS at every modeset (nvidia-drm-connector.c). So the only missing piece for HDMI 1.4 3D is mode exposure.

Proof it works with zero driver changes: a small libdrm client sets a plain 2D timing and injects the 3D VSIF through that blob property. On the Sony: side-by-side half 1080p60 enters 3D with correct picture (twice, run logs 13 and 14), top-and-bottom 1080p24 enters 3D with correct picture and working 2D fallback (run log 17). All logs and the client are at https://github.com/danielcamposramos/sony-bravia-linux/tree/main/tools/stereo-modeset.

Full matrix, honestly reported: injected SBS passes at 60 Hz; injected TaB passes at 24 Hz but TaB, specifically, is rejected by this sink at both 60 Hz timings (the same bytes pass at 1080p60 from a kernel-emitted VSIF on an AMD link, so the payload is exonerated and the difference presumably lives in infoframe emission specifics I cannot measure without an HDMI analyzer). This is exactly why userspace injection is a proof, not a substitute: native stereo modeset handling owned by the driver is the supportable configuration.

Prior reports: before filing I searched this tracker, open and closed, issues and PRs (stereoscopic, stereo, 3D Vision, 3DTV, frame packing, VSIF, stereo_allowed; 2026-09-21), and as far as the record goes this is the first report on HDMI 1.4 3D mode exposure. So the attached patch closes no visible number; it closes a hole nobody had filed.

A bit of history, because we keep it curated: NVIDIA's own 3D Vision and 3DTV Play drove exactly this HDMI 1.4 signaling into 3D televisions back in the driver era — frame packing to the set, the set's own glasses on the couch. That era, including NVIDIA's chapters, is documented entry by entry in a public list we maintain: https://github.com/danielcamposramos/awesome-stereoscopy#pc-gaming-and-the-driver-era. 3D Vision was discontinued in 2019, before the kernel driver was open-sourced in 2022, which is presumably why nvidia-drm never grew the stereo opt-in that nouveau has always carried. This issue asks for that missing line on today's pipeline, not for a 3D Vision revival.

The ask: set connector->stereo_allowed for HDMI connectors (attached patch against 615.71.09, or any equivalent NVIDIA prefers). Frame packing is out of scope for this delta: its doubled scanout timing needs NVKMS support, the same expansion AMD DC needed (CRTC_STEREO_DOUBLE in Adrian Betschart's amd-gfx v3 series, which this TV also verified).

Disclosure per Documentation/process/coding-assistants.html: prepared with AI assistance, directed and hardware-verified by me end to end (Ollama Kimi K3 and Claude Opus 5 / Claude Code CLI).

---

Notes for Daniel (not for the issue):
- "This TV also verified" Betschart v3 line: fine to keep, it cross-references your amd-gfx
  mails; drop it if you'd rather not tie the two threads publicly.
- If NVIDIA asks for the client source, it is stereo-modeset.c in the same repo (CC0).
- The community variant of the patch (install instructions for users) sits next to the
  contribution variant in this directory and is what the awesome list links.
