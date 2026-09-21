# Upstream issue tracker — every filed/planned touch of the campaign

One row per upstream item. "Whose move" is always explicit. Rules in force for every
row: no agent ever posts to any forge (Daniel posts everything himself); polling is
gentle and content-checked, never past anti-bot controls; email-first where the forge
mails us; never necro closed issues. Sorted by activity, not importance.

| # | item | where | identifier | status (2026-09-21) | whose move | how we watch |
|---|---|---|---|---|---|---|
| 1 | NVIDIA HDMI 1.4 3D: `stereo_allowed` glue delta | github.com/NVIDIA/open-gpu-kernel-modules (issues) | **#1382** (github.com/NVIDIA/open-gpu-kernel-modules/issues/1382) + PR-offer comment 5764542206 | **POSTED 2026-09-21 ~14:55 UTC-3** — Daniel's explicit order, his gh account; his reviewed body verbatim, contribution patch attached by him in the first comment, PR offer posted; CLA engages only if NVIDIA invites the PR | **NVIDIA** | one gentle `gh api repos/NVIDIA/open-gpu-kernel-modules/issues/1382` check on request; no crawling |
| 2 | Betschart v3 HDMI 1.4 3D series (amd-gfx) | amd-gfx list, lore.kernel.org/amd-gfx | Tested-by mail <20260921034104.1021664-1-capitain_jack@yahoo.com>; v3 PASS + backport offer <20260921153400.53321-1-capitain_jack@yahoo.com> | BOTH SENT, public in lore in-thread; Tested-by covers v3 as posted (runs on 7.3-rc4+v3, all three layouts) | maintainers / Adrian | lore thread check on request; amd-gfx also reaches Daniel's subscribed inbox |
| 3 | amdgpu 7.0 backport pair (0001/0002 mboxes) | this repo `docs/upstream/` + community hub | offered in mail #2, offer-only | staged; offered, not sent; forward-verified vs pristine v7.0; also now the community installable path (`community-hdmi-3d-patches.md`) | upstream asks, or it retires | tied to row 2's thread |
| 4 | MKVToolNix: auto StereoMode from SEI | codeberg.org/mbunkus/mkvtoolnix | issue #6309; Daniel's two fix branches pushed from capitain_jack | **!6311 (AVC) MERGED 2026-09-21** to main; !6312 (HEVC) reworked+rebased onto the merge 2026-09-22, maintainer's two asks (HEVC samples, rework) answered same night — comments 23418046/23418100; our 3d-wrapper prints the `mkvmerge --stereo-mode` fix-up meanwhile | **mbunkus (final review of !6312)** | Codeberg email notifications only (no site polling) |
| 5 | mpv stereo-metadata issue | github.com/mpv-player/mpv | #18489 | review round 2: kasper93 CHANGES_REQUESTED answered with a v2 rework (his four asks landed exactly), **force-pushed 2026-09-21/22** (`049bb33bba`+`fc2ac9e8cb`, author Capitain_Jack@yahoo.com, LLM-disclosure kept); line replies + summary + the #17632 answer await Daniel's own words; drafts in the private research folder | theirs (kasper93 re-review) | GitHub email notifications |
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
- Rows 1–3 are the live hardware-driver campaign; everything else is parked until its
  owning human moves.
- "Watch on request" means Daniel asks for a status pull; nothing on this page gets
  polled on a timer. The one historical exception (a video webboard) tripped the
  site's anti-bot and was dropped — that is why.
- When Daniel posts an item, the identifier cell gets the real number/ID in the same
  commit that marks it SENT, so future sessions never guess from history.
