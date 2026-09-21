# DRAFT — reply to Adrian Betschart's v3 series on amd-gfx — RAW MATERIAL for Daniel

Not for sending as-is. Daniel reviews, rewrites in his own words, and posts himself.
Style rules for his version (already applied below): plain text, no bold, one paragraph per
line, no hard-wrapped lines inside a sentence, em dashes only in list items and attributions.

Envelope for an in-thread reply:
- To: amd-gfx@lists.freedesktop.org
- Cc: dri-devel@lists.freedesktop.org
- In-Reply-To: 20260907125015.69811-1-adrian.betschart@cinemaone.ch (his v3 cover letter, 2026-09-07)
- Subject: Re: [PATCH v3 0/3] drm/amd/display: HDMI 1.4 3D output (frame packing, top-and-bottom, side-by-side)

---

Hi Adrian,

independent confirmation of this approach on older DCN hardware and a consumer-TV sink, plus a boundary record that matches your patch 3's diagnosis.

Hardware here is a Renoir APU (0000:0b:00.0, DCN 2.1, Display Core 3.2.369, Debian 7.0 kernel) driving a Sony KDL-46HX855 from 2012, whose HDMI 1.4b-class EDID advertises side-by-side half and top-and-bottom over a 7-VIC mask and frame packing on five VICs. The coverage is complementary to yours: yours runs DCN 3.2.1 into a JVC projector behind an HDFury, mine runs DCN 2.1 straight into a living-room television.

With the equivalent wiring here (stereo_allowed allowed on HDMI connectors, the vendor infoframe attached to the stream's hfvsif packet when the mode carries DRM_MODE_FLAG_3D_*, timing_3d_format deliberately left at NONE), side-by-side half 1920x1080@60 makes the set switch itself into 3D with no remote input, and a software-rendered disparity pattern reads in depth through the TV's own glasses. The mode probe goes from 22 modes with zero stereo to 51 modes with 29 stereo-flagged.

Frame packing shows the boundary your patch 3 fixes, observed independently: without the CRTC_STEREO_DOUBLE expansion the sink entered 3D on a valid FP VSIF while DC scanned the un-doubled 1080-line 74.25 MHz timing against the 2205-line plane, which is signal pass and picture black. With the stream mode expanded (1920/2750 horizontal active and total, 2205/2250 vertical, 148.5 MHz for 1080p24 FP) the same television both switched itself into 3D and displayed the full two-eye picture through the AMD link.

A cross-vendor control on the same sink: stock nouveau on a GA106 drives this television into 3D in the same 1920x1080@24 frame-packing mode, so the EDID and the sink behavior are proven independently of the AMD path.

On your DCC note: our test buffers are dumb buffers without DCC, so I cannot speak to that wedge; every flip with a plain buffer completed, which is at least consistent with the failure being DCC-specific.

Logs, the DRM test tool, and the two reference deltas (built for the 7.0 tree, kept as a DCN 2.1 port in case an older-generation follow-up is wanted) are public at https://github.com/danielcamposramos/sony-bravia-linux: run records and verdicts are in tools/stereo-modeset/ and the patches are in docs/upstream/.

Happy to run anything specific on this APU and television combination if it helps the review.

Tested-by: Daniel Ramos <danielcamposramos.68@gmail.com>

Disclosure per Documentation/process/coding-assistants.html: prepared with AI assistance, directed and hardware-verified by me end to end; the assisting models were LLM Kimi K3 (Codex CLI), LLM GPT 5.6 Sol (Codex CLI) and LLM Claude Opus 5 (Claude Code CLI).

---

Note for Daniel: our two format-patches in docs/upstream/ stay staged, unsent. They become a
follow-up only if maintainers ask for a DCN 2.1 series or if the v3 stalls; otherwise the
Tested-by reply above is the contribution.
