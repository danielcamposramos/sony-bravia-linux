# DRAFT — second reply on the Betschart v3 thread (v3 as posted, all three layouts PASS) — RAW MATERIAL for Daniel

Not for sending as-is. Daniel reviews, rewrites in his own words, and posts himself.
Style rules for his version (already applied below): plain text, no bold, one paragraph per
line, no hard-wrapped lines inside a sentence, em dashes only in list items and attributions.

Envelope for an in-thread reply:
- To: amd-gfx@lists.freedesktop.org
- Cc: dri-devel@lists.freedesktop.org, adrian.betschart@cinemaone.ch
  (Harry Wentland and Leo Li ride along: Adrian re-added the maintainers in the message this replies to)
- In-Reply-To: 20260921080126.98936-1-adrian.betschart@cinemaone.ch (his 2026-09-21 reply asking for the v3 run)
- Subject: Re: [PATCH v3 0/3] drm/amd/display: HDMI 1.4 3D output (frame packing, top-and-bottom, side-by-side)

---

Hi Adrian, Harry, Leo, others,

Done, and it is a pass across the board: v3 as posted built into a 7.3-rc4 kernel and run today on the Renoir APU (DCN 2.1, Display Core 3.2.369) driving the Sony KDL-46HX855, all three layouts in one desktop-down window of about five minutes, so this Tested-by now covers the series exactly as it sits on the list.

Top-and-bottom first, as you suggested: the TV switched itself into 3D on 1920x1080@60 TaB and the disparity picture read in depth through its glasses, so the sink is happy with the 3D_Ext_Data byte patch 2 sends for that layout. Side-by-side half at 1920x1080@60 followed with the same self-switch and picture. Frame packing closed the window at 1920x1080@24: the tool presented one 1920x2205 packed buffer, the expanded timing from patch 3 scanned it, and the full two-eye picture showed where my earlier 7.0 experiment without the expansion had signal and black picture.

The probe numbers on 7.3-rc4 + v3 are identical to what our 7.0 port produced here: 22 modes and 0 stereo without the client cap, 51 modes and 29 stereo with it, no regressions on the aspect-ratio pass. The run record is in the repo at tools/stereo-modeset/run11-betschart-v3-7.3rc4-all-pass-2026-09-21.log (https://github.com/danielcamposramos/sony-bravia-linux), probe output and per-layout modeset lines included.

One more thing I would like to put on the table while the series is in review. Since our first exchange I have kept the equivalent two changes prepared as a backport for the 7.0-era tree, where the connector code still lives in amdgpu_dm.c: same stereo_allowed plus VSIF wiring, same CRTC_STEREO_DOUBLE expansion for frame packing, forward-verified to apply cleanly against the pristine v7.0 source, sitting as format-patch mboxes in docs/upstream of the same repository. They are an offer, not a request, and there is no competing series coming: if this v3 lands and a stable backport or an older-generation follow-up ever becomes wanted, they are ready to go as-is, and I am equally happy to reshape them or to let them retire unused once v3 ships downstream on its own.

Happy to run anything further on this APU and television if the review wants it.

Tested-by: Daniel Ramos <capitain_jack@yahoo.com>

Disclosure per Documentation/process/coding-assistants.html (https://docs.kernel.org/process/coding-assistants.html): prepared with AI assistance, directed and hardware-verified by me end to end; the assisting models were LLM Kimi K3 (Codex CLI), LLM GPT 5.6 Sol (Codex CLI) and LLM Claude Opus 5 (Claude Code CLI).

---

Notes for Daniel (not for the list):
- The backport paragraph is deliberately phrased as offer-only. No subject-line series, no
  patch files attached: the mboxes stay staged on disk, and the mail only points at them.
- If you'd rather attach the two mboxes in a later, separate mail when someone bites, the
  paragraph still works unchanged.
- The run happened 12:14-12:19 UTC-3 on 2026-09-21; machine is already back on stock 7.0.10.
