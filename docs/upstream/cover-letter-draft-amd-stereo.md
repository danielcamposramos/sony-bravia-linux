# DRAFT — amd-gfx cover letter — RAW MATERIAL for Daniel to rewrite in his own words

Not for sending as-is. Daniel reviews, rewrites, and posts himself. Style constraints
for his version: plain text, one paragraph per line, no bold, no hard-wrapped lines.

Subject: [PATCH] drm/amdgpu: allow stereo 3D modes over HDMI and emit the vendor infoframe

---

Hi,

amdgpu's display connector code is currently the only place among the major DRM drivers that flat-out refuses HDMI stereo 3D: amdgpu_dm_connector_init_helper sets stereo_allowed = false, while i915 (intel_hdmi.c), vc4 (vc4_hdmi.c) and nouveau (nouveau_connector.c) all allow it. The result is that a 3D-capable HDMI sink's EDID-declared stereo modes (frame packing, side-by-side half, top-and-bottom) are pruned at probe time with MODE_NO_STEREO and never reach userspace, no matter which client caps the application sets.

This patch is the minimal wiring to close that gap on DC hardware:

1. Set stereo_allowed = true in amdgpu_dm_connector_init_helper, so drm core stops pruning the EDID's 3D-flagged mode alternates at validation time.

2. In fill_stream_properties_from_drm_display_mode, when the mode carries DRM_MODE_FLAG_3D_*, pack the vendor-specific infoframe that drm_hdmi_vendor_infoframe_from_display_mode already computed (for HDMI VIC) and attach its bytes to stream->hfvsif_infopacket, so the existing DC packet machinery emits the VSIF that tells the sink which 3D format is on the link.

timing_3d_format deliberately stays VIEW_3D_FORMAT_NONE: that field drives DC's stereo plane-address flipping, which is for kernel-composed stereo, whereas the user of these modes (compositors, players, games) composes the SBS/TaB buffer itself, same as on i915.

Tested on real hardware: a Sony KDL-46HX855 (2012, EDID advertises SBS-half and top-and-bottom over a 7-VIC mask plus frame packing on five VICs) on the HDMI port of an AMD APU running Debian's 7.0 kernel. Before the patch: 22 modes, zero stereo, with DRM_CLIENT_CAP_STEREO_3D set. After: 51 modes, 29 stereo-flagged, and modesetting the SBS-half 1920x1080@60 mode makes the TV switch itself into 3D mode without any manual input selection, with a software-rendered disparity pattern visibly presenting depth through the TV's own 3D glasses. Windows 11 on the same port and cable offers and enables the same 3D modes, so the gap was purely the Linux driver stack.

The patch does not attempt frame-packing timing generation or DC-side stereo composition; it only stops refusing what the EDID, the DRM core helpers, and DC's packet hardware already know how to do. Happy to split it, expand it toward FP timings, or rebase wherever the display team prefers — guidance on the intended shape of a fuller DC stereo implementation is very welcome.

This contribution was prepared with AI assistance (Claude Code, pair-programmed and hardware-tested by me end to end); the kernel module was built, loaded, and verified on the named display, and the patch itself is two small, reviewable deltas.

Signed-off-by: Daniel <his address>

---

Links to include: this repo's tools/stereo-modeset/README.md (verdict + numbers),
tools/stereo-modeset/run7-pass-2026-09-20.log (the passing run),
tools/stereo-kms-probe/README.md (the mechanism evidence), and the patch file
docs/upstream/amdgpu-dc-hdmi-stereo.patch (format-patch form still to be generated
once Daniel picks the target tree: amd-gfx / amd/drm next branch).
