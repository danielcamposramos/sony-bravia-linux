# NVIDIA PR draft — nvidia-modeset: raise default max_output_color_depth to 12

**State: PR OPEN 2026-09-22 evening — https://github.com/NVIDIA/open-gpu-kernel-modules/pull/1386**
Runbook executed on the owner's explicit go ("then go, fork and PR"):
fork `danielcamposramos/open-gpu-kernel-modules` created (no fork existed),
`fix-hdmi-deep-color-default` pushed over HTTPS via the gh credential
helper (no GitHub SSH key on this box), PR opened with the body below
exactly as reviewed. "Refs #1384" in the body already back-references the
issue timeline; no separate comment was posted on the issue.
Working tree: `/K3D/temp/nvidia-open-wt`, fix-hdmi-deep-color-default @ bbfc670 on official base 61dcc937 (615.71.09).

## PR metadata

- Target: `NVIDIA/open-gpu-kernel-modules`, base branch `main`
- Head: `danielcamposramos:fix-hdmi-deep-color-default` (after fork+push)
- Title (RETITLED 2026-09-22 by owner request "cite the specs now", via REST PATCH;
  second pass same evening per owner: the "max_output_color_depth to 12" half was
  dropped because it singled out one depth right next to the three VSDB
  capabilities, and parentheses removed):
  `nvidia-modeset: raise default output color depth for HDMI 1.4 Deep Color, EDID VSDB DC_30/DC_36/DC_48`
- Deliberately **not** using "Fixes #1384" — that issue tracks three
  symptoms (mode prune, 3D exposure, deep-colour cap); closing keywords
  would be wrong. The commit and body use "Refs".

## PR body (paste as is)

**What this changes.** The `max_output_color_depth` module parameter's default goes from 10 to 12 on the Linux side.

**Why it is safe.** NVKMS already parses the sink's HDMI Deep Color capability (VSDB `DC_30`/`DC_36`/`DC_48`) and already constructs and programs 10 and 12 bpc output for RGB and for YCbCr 4:4:4, 4:2:2 and 4:2:0. Nothing new is programmed anywhere; the existing path is simply allowed to reach the depth the sink declares. The parameter still permits capping at 10, so anyone on a marginal link keeps the override.

**Measured on the current production build.** With stock 615.71.09 reloaded using only `nvidia_modeset.max_output_color_depth=12` (this change, applied at load time), a GA106 (GALAX RTX 3060) drives a Sony KDL-46HX855 (HDMI 1.4, EDID `DC_30`/`DC_36`, 225 MHz TMDS ceiling) at 1080p60 RGB requiring 222.75 MHz, and the set's own OSD reports **12-bit**: passed with full colors (pun intended). Windows on this same card and set already trains 12-bit, and amdgpu on this same sink selects 12 bpc; Linux 615.71.09 at the current default selects 10 bpc on the identical cable. Harness, module-state readback, and the sink observation are preserved: https://github.com/danielcamposramos/sony-bravia-linux/blob/main/tools/stereo-modeset/run24-nvidia-deepcolor-param12-pass-2026-09-22.log

**Refs #1384** — this addresses the measured deep-colour symptom there (the 10-vs-12 narrowing). It does not touch the mode-prune or 3D-exposure symptoms the same issue tracks.

**Open-source counterpart.** The same end state for nouveau is in review on the kernel lists as a three-patch HDMI Deep Color series (link-depth selection, GCP state through NVIF, GCP programming around the late HDMI-audio rewrite), hardware-verified at 12 bpc on this same bench: https://lore.kernel.org/dri-devel/20260922192132.114546-1-Capitain_Jack@yahoo.com/

**Scope.** SDR deep colour only; no HDR claim is made (there is no HDR sink on this bench). Because the parameter gates NVKMS's existing deep-colour selection wholesale, the lifted default applies to its existing YCbCr 4:4:4/4:2:2/4:2:0 modes as well as RGB.

AI partners were leveraged in the production of this work.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Approval-gated runbook (after Daniel's per-act go at each gate)

1. Create the fork: `gh repo fork NVIDIA/open-gpu-kernel-modules --clone=false`
2. In `/K3D/temp/nvidia-open-wt`: `git remote add fork git@github.com:danielcamposramos/open-gpu-kernel-modules.git`
3. `git push -u fork fix-hdmi-deep-color-default`
4. `gh pr create -R NVIDIA/open-gpu-kernel-modules --base main --head danielcamposramos:fix-hdmi-deep-color-default --title "nvidia-modeset: raise default max_output_color_depth to 12" --body-file <this PR body>`
5. After the PR URL exists: cross-link pass per
   `docs/research/deep-color-dual-upstream-handoff-2026-09-22.md`
   (comment on #1384 pointing at the PR; nouveau series is email-only so
   its cross-link back happens in the record files), then index updates:
   `issue-tracker.md`, `project-status.md`, awesome-linux-hdr.

## Verified while assembling (2026-09-22)

- NVIDIA accepts PRs; cosmetic-only changes are rejected (ours is
  functional); style follows surrounding code (one-liner, matches).
  No CLA surfaced in the contributing guide excerpt reviewed.
- lore.kernel.org is behind Anubis anti-bot for datacenter fetches; the
  series URL is the canonical archive form and resolves in browsers —
  same citation form already public for the amd-gfx thread.
