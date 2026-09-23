# POSTED 2026-09-18 — https://codeberg.org/mbunkus/mkvtoolnix/issues/6309
**Filed as:** capitain_jack (account created for this — the Codeberg signup
page is easy to mistake for the donate page; they look near-identical).
**Text:** the body below, verbatim except paragraphing — the owner lightly
restructured it while typing it as himself, per the doctrine. No AI
disclaimer, no provenance block, filed as his own words. Comments at
filing: 0, no labels yet.
**Notifications:** Codeberg emails the author on every reply, so this
joins the DLNA threads on the email-trigger watch — never poll Codeberg
("we don't want to be flagged" applies there too; check notifications if a
quiet period needs a manual glance, no scheduled fetches).

**Tracker:** https://codeberg.org/mbunkus/mkvtoolnix/issues
**Account:** https://join.codeberg.org/ — email + username signup
(Codeberg is a non-profit Forgejo instance; no GitHub login.)
**Codeberg ToU note (verified live 2026-09-18):** Codeberg's Terms of Use
§ 2 (1) 7 bans *hosting projects that mostly consist of AI-generated code*
(names Claude/Codex), for copyright/safety reasons. That is a project-
hosting rule — it does NOT forbid filing a human-authored issue. So: do
NOT mirror this repo to Codeberg (it stays on GitHub); the issue below was
filed as the owner's own human-authored text. This reinforces the
no-disclaimer rule: file it as yourself, owning every claim.
**Doctrine (kept for the record — it governed how this was filed):**
mbunkus has stated publicly (tracker meta-issue #6278) that he will
"outright close & ignore overly verbose & meandering issue requests", and
that AI assistance is acceptable only when the submitter demonstrably
understands every claim. So: keep it short, name the source files you
checked, own every sentence. **No AI disclaimer, no provenance block —
file it as yourself.** This is the opposite of the DLNA-server issues; do
not paste our disclosure block here.
**Own these before filing:** the two source-file references below, and
the SEI→Matroska mapping. Verified against a mkvtoolnix dev checkout
(configure.ac v102.0) on 2026-09-15; re-glance if you want to stand
behind them.

---

**Title:** mkvmerge: derive the stereo mode from the H.264/HEVC frame-packing SEI when --stereo-mode is not given

mkvmerge sets a track's stereo mode from only two sources today: the `--stereo-mode` option, and an existing `KaxVideoStereoMode` in a Matroska input (`src/input/r_matroska.cpp`). The AVC parser in `src/common/avc/es_parser.cpp` walks SEI NALs but only interprets payload type 6 (recovery point); `frame_packing_arrangement` (payload 45) is skipped.

**Request:** when `--stereo-mode` is not given, read the `frame_packing_arrangement` SEI from AVC (and the equivalent HEVC SEI) and set the stereo mode from it — `frame_packing_arrangement_type` 3 → side-by-side, 4 → top-and-bottom, with `content_interpretation_type` (which view is first) selecting the left-first vs right-first Matroska variant. If a source carries both a container tag and a SEI and they disagree, keep the tag and print a warning.

**Why:** the frame-packing SEI is the standardized in-stream stereo signal (H.264 Annex D; it is what hardware 3D displays read to auto-engage, and what DVB frame-compatible 3DTV mandates), while the Matroska tag is what most software reads. A raw H.264/HEVC elementary stream or MP4 that carries only the SEI currently muxes with no stereo mode at all. mkvmerge already derives other track properties from the bitstream, so this is the same idea for stereo. These inputs are also getting more common now that HandBrake writes this SEI when encoding flagged 3D sources (merged 2026).

mkvmerge stream-copies the video, so this is detection only, no re-encode. I know the AVC parser skips the payload today, so it is a real feature, not a one-liner; happy to test against SEI-reading hardware if useful. Background, live-tested on two 3D TVs: https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/3d-signalling-explainer.md
