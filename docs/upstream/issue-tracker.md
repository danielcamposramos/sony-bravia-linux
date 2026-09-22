# Upstream issue tracker — every filed/planned touch of the campaign

One row per upstream item. "Whose move" is always explicit. Rules in force for every
row: no agent ever posts to any forge (Daniel posts everything himself); polling is
gentle and content-checked, never past anti-bot controls; email-first where the forge
mails us; never necro closed issues. Sorted by activity, not importance.

| # | item | where | identifier | status (2026-09-21) | whose move | how we watch |
|---|---|---|---|---|---|---|
| 1 | NVIDIA HDMI 1.4 3D: `stereo_allowed` glue delta | github.com/NVIDIA/open-gpu-kernel-modules (issues) | **#1382** (github.com/NVIDIA/open-gpu-kernel-modules/issues/1382) + PR-offer comment 5764542206 | **LIVE EXCHANGE.** Original post + PR offer 2026-09-21 (comment 5764542206); aritger asked for a test case 2026-09-22 01:19 UTC; measured v1 A/B posted (comment 5770907110 — stock 17/0, stereo_allowed-patched 17/0, necessary-but-not-sufficient); color-depth/TaB PS (comment 5771032927); **v2 VSDB-synthesis patch + measured numbers posted 2026-09-22T05:03Z ([comment 5771464134](https://github.com/NVIDIA/open-gpu-kernel-modules/issues/1382#issuecomment-5771464134), 3 attachments: v2 patch, design doc, run19 log — 39/22 stereo under STEREO_3D cap, gap to nouveau = missing 1080i family in NVKMS base list)**; open question to maintainers: does NVKMS's EDID parse model VSDB 3D at all | **aritger** | one gentle `gh api repos/NVIDIA/open-gpu-kernel-modules/issues/1382` check on request; no crawling |
| 2 | Betschart v3 HDMI 1.4 3D series (amd-gfx) | amd-gfx list, lore.kernel.org/amd-gfx | Tested-by mail <20260921034104.1021664-1-capitain_jack@yahoo.com>; v3 PASS + backport offer <20260921153400.53321-1-capitain_jack@yahoo.com> | BOTH SENT, public in lore in-thread; Tested-by covers v3 as posted (runs on 7.3-rc4+v3, all three layouts) | maintainers / Adrian | lore thread check on request; amd-gfx also reaches Daniel's subscribed inbox |
| 12 | NVIDIA unified EDID-surface issue (3D absent + 10v12 deep colour + 17/51 prune; HDR adjacency; cites #1348, #1369, #1184, HDR trio, #1101) | github.com/NVIDIA/open-gpu-kernel-modules (issues) | **#1384** (github.com/NVIDIA/open-gpu-kernel-modules/issues/1384); draft at `nvidia-edid-surface-issue-draft.md`; cross-link from #1382 = comment 5771657559 | **FILED 2026-09-22** by gh as danielcamposramos on explicit per-act approval; machine line: RTX 3060 (GA106), GALAX, 12 Gb VRAM; asks NVKMS-vs-glue ownership + EDID capability model | **NVIDIA maintainers** | GitHub email notifications only (author is Daniel) |
| 3 | amdgpu 7.0 backport pair (0001/0002 mboxes) | this repo `docs/upstream/` + community hub | offered in mail #2, offer-only | staged; offered, not sent; forward-verified vs pristine v7.0; also now the community installable path (`community-hdmi-3d-patches.md`) | upstream asks, or it retires | tied to row 2's thread |
| 4 | MKVToolNix: auto StereoMode from SEI | codeberg.org/mbunkus/mkvtoolnix | issue #6309; Daniel's two fix branches pushed from capitain_jack | **!6311 (AVC) MERGED 2026-09-21** to main; !6312 (HEVC) reworked+rebased onto the merge 2026-09-22, maintainer's two asks (HEVC samples, rework) answered same night — comments 23418046/23418100; our 3d-wrapper prints the `mkvmerge --stereo-mode` fix-up meanwhile | **mbunkus (final review of !6312)** | Codeberg email notifications only (no site polling) |
| 5 | mpv stereo-metadata issue | github.com/mpv-player/mpv | #18489 | review round 2 **fully answered 2026-09-21/22**: v2 force-pushed (`049bb33bba`+`fc2ac9e8cb`), kasper93's seven line comments answered (4067137433–4067138147), summary comment [5768736315](https://github.com/mpv-player/mpv/pull/18490#issuecomment-5768736315), and the norm-cited answer to his clips comment posted on #17632 ([comment 5768747371](https://github.com/mpv-player/mpv/issues/17632#issuecomment-5768747371)); re-request review is Daniel's one browser click (REST refuses it for non-collaborators); resolve buttons stay with kasper93 | theirs (kasper93 re-review) | GitHub email notifications |
| 6 | VLC/vlc-devel: account-unblock mail (the only gate before the x264 MR) | lists.videolan.org vlc-devel | **SENT 2026-09-21** by the owner in his own words; draft on disk: `tools/serviio/upstream-3d-issues/vlc-account-unblock-mail.md`; list-archive ID still to record once it lands there | account gate: code.videolan.org held the 2026-09-19 capitain_jack registration for administrator approval, no approval mail ever arrived; mail asks an admin to approve the account or state the route | **VideoLAN admins** | Daniel's inbox (primary) + vlc-devel archive check on request |
| 7 | MAME SegaScope stereo layout | github.com/mamedev/mame | #3492 (open since 2018) | watching only; unmerged community layout; no comment planned unless the campaign has new working evidence | theirs | GitHub email notifications |
| 8 | Kodi 3D/SBS handling | github.com/xbmc/xbmc | #29337 (lesson, not an open touch) | CLOSED upstream; our verify-by-running rule came from here — do not reopen | nobody | none |
| 9 | Jellyfin stereoscopy comment | github.com/jellyfin | #18060 comment draft (`docs/jellyfin-18060-comment-draft.md`) | draft staged | Daniel when he chooses | GitHub email notifications |
| 10 | awesome main-index claim (awesome-stereoscopy → sindresorhus/awesome, + awesome-vr, awesome-ar back-claims) | github.com/sindresorhus/awesome (PR) | not yet filed | planned; list is public, entry-quality gates per `PROVENANCE.md` | Daniel (PR in his name) | PR thread on request |
| 11 | Rossmann/FULU right-to-repair outreach | direct mail | `docs/rossmann-outreach.md` | outreach lane, owner-paced | Daniel | Daniel's inbox |

## Standing notes

- 2026-09-21 negative sweep, for the record (so no future session re-runs it blind):
  NVIDIA/open-gpu-kernel-modules issues AND PRs, all states, queried via `gh search`
  with stereoscopic / stereo / 3D Vision / 3DTV / frame packing / VSIF /
  stereo_allowed / glasses / 3D — zero entries cover HDMI 1.4 3D or stereo mode
  exposure. Ours is the first report there; the patch carries no Closes line because
  there is no number to close. The one 3D-adjacent noise field is power-management
  (D3cold) and rendering performance, unrelated.
- 2026-09-22 color/HDR sweep, for the record (all states, `gh search` over
  NVIDIA/open-gpu-kernel-modules): our exact 10-vs-12-bit training symptom
  (DC_36bit declared, exposed ceilings identical, link trains 10-bit where
  amdgpu trains 12, Windows unaffected — same card, same sink) is
  UNREPORTED there; the filed unified-surface issue would be the first.
  Same-shape siblings found, each an independent axis of the
  NVKMS-narrows-the-EDID-surface family and each citeable without touching
  its thread: **#1348** (same driver 615.71.09; HF-VSDB `DSC_MaxSlices`
  misparse forces YCbCr 4:2:2-limited on HDMI 2.1; zero maintainer replies
  since 2026-09-10 — the load-bearing adjacency), **#1369** (mode pruned
  after sink power-cycle, identical EDID, Windows unaffected — siblings our
  17/51 prune), **#1184** (EDID Max_FRL_Rate ignored → capped 4K60),
  HDR trio #1285/#779/#933 (colorspace EINVAL / HDR never activates;
  HDR10's stock transport is 10-bit YCC422 carried at 12-bit container
  depth, so depth narrowing plausibly feeds this family — [qualified], not
  proven), **#1101** (HDR DRM props missing on force-enabled connectors,
  fixed in 610.43.02 — precedent that glue-side surfacing works). Full
  query list + reasoning in the sweep section of
  `../research/liverecon/nv-vs-amd-deepcolor-osd-2026-09-22.md`. Nothing was
  filed or commented from this sweep; the unified NVKMS EDID-surface issue
  (3 measured symptoms + #1348 citation) is Daniel's call.
- Rows 1–3 are the live hardware-driver campaign; everything else is parked until its
  owning human moves.
- "Watch on request" means Daniel asks for a status pull; nothing on this page gets
  polled on a timer. The one historical exception (a video webboard) tripped the
  site's anti-bot and was dropped — that is why.
- When Daniel posts an item, the identifier cell gets the real number/ID in the same
  commit that marks it SENT, so future sessions never guess from history.
