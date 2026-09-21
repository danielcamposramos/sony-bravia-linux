# AI-contribution policies by upstream target

Compiled 2026-09-20 from documented sources (every page read; freedesktop GitLab
content verified via mirror because its Anubis bot-wall was NOT bypassed).
Purpose: before any patch or MR leaves this project, check its row here.
Our own doctrine (name model+harness on every AI-assisted post, never claim
"not AI-generated", Daniel signs and posts in his own words) is the baseline;
each row adds that target's specific requirements on top.

## Kernel and GPU drivers

| target | policy location | verdict | key quote |
|---|---|---|---|
| Linux kernel (all lists incl. amd-gfx, dri-devel) | https://docs.kernel.org/next/process/coding-assistants.html and https://docs.kernel.org/next/process/generated-content.html (merged Dec 2025, torvalds/linux 78d979d, per Maintainers Summit consensus) | Explicitly allowed with disclosure; human certifies the DCO | "AI agents MUST NOT add Signed-off-by tags. Only humans can legally certify the Developer Certificate of Origin (DCO)." |
| DRM trees specifically | https://dri.freedesktop.org/docs/drm/process/generated-content.html (mirrors the kernel doc) | Allowed with disclosure; maintainer discretion preserved | "Expect additional scrutiny in proportion to how much of it was generated." At least two human contributors must understand a patchset; AI review does not remove the need for review. |
| Linus Torvalds' public position | lkml.org/lkml/2025/11/10/1647; phoronix.com/news/Torvalds-Linux-Kernel-AI-Slop (Jan 2026); the "Linking Patchwork with Sashiko" thread via Ars Technica (Jul 2026) | Approves disclosed, human-owned use; rejects label-based slop enforcement | "It's just another tool, guys." / "Linux is not one of those anti-AI projects, and if somebody has issues with that, they can do the open-source thing and fork it." / decisions "primarily based on technical merit. Not fear of new tools." |
| NVIDIA open-gpu-kernel-modules | https://github.com/NVIDIA/open-gpu-kernel-modules/blob/main/CONTRIBUTING.md | Silent on AI; functional changes only; NVIDIA CLA applies | No AI clause (commit history confirms none was ever added); "we have decided not to accept non-functional changes." NVIDIA-family precedent (NeMo Guardrails AI_POLICY.md): "Disclose AI assistance in the pull request description", "the human submitter remains responsible", "Do not add AI tools as commit co-authors." |
| Valve gamescope | (no CONTRIBUTING in repo) | Silent; plain PR with a disclosure note in the body is safe practice | no policy found |
| Monado (freedesktop GitLab) | gitlab.freedesktop.org/monado/monado CONTRIBUTING.md (Anubis-walled; verified via mirror) | Allowed implicitly; human DCO is mandatory and is their only AI-relevant clause | "Note that only a human can legally certify the DCO." Submissions without a valid sign-off are rejected. |

## Media players and emulators

| target | policy location | verdict | key quote |
|---|---|---|---|
| MAME | https://docs.mamedev.org/contributing/index.html (commit 58fca9a) | Explicitly allowed with disclosure | "All pull requests using AI assistance... must mention it as part of the initial pull request description" and "must include the model and version used"; "you are responsible for understanding and describing your changes"; AI use alone is not grounds for out-of-hand rejection but invites additional scrutiny. |
| MKVToolNix | no project-level policy (repo/docs/issues checked) | Silent; hosting restriction applies | Codeberg ToU 2(1)7 (voted 2026) forbids hosting projects that "mostly consist of" generative-AI code (https://blog.codeberg.org/protecting-our-floss-commons-from-llms.html). Small disclosed patches are unaffected. |
| VideoLAN / VLC | https://wiki.videolan.org/SoC_2026/ | AI banned for GSoC; silent for regular contributions | "AI-generated content is not permitted in any part of your GSoC participation with VideoLAN" (code, proposals, even communications with mentors). |
| Kodi | https://github.com/xbmc/xbmc/blob/master/docs/CONTRIBUTING.md (no AI section) | Silent; informal hostility to unchecked AI output on forums | closest signal: a team member's "we can do without the AI generated responses. Especially as some of it is clearly wrong." |
| mpv | https://github.com/mpv-player/mpv/blob/master/DOCS/contribute.md (commit 7ce58f7, Jan 2026) | Allowed, human responsibility + mandatory disclosure | "you must disclose this in the PR description"; AI "must not be used to write commit messages or pull request descriptions"; "Clearly vibe-coded patches will not be considered." |
| Dolphin | https://github.com/dolphin-emu/dolphin/blob/master/Contributing.md (PR 14445, merged 2026-03-20) | Allowed with disclosure; agents not accepted; LLMs barred for console-behavior work | "We accept contributions from humans, not from AI agents." Disclose which parts are generated; "you're not allowed to use LLMs to make changes related to the behavior of the emulated console." |
| RPCS3 | https://github.com/RPCS3/rpcs3/blob/master/README.md (commit c0b3580, 2026-05-10) | Allowed, human responsibility + mandatory disclosure; autonomous agents banned; repeat violations = repo ban | All communication "must come from the human contributor"; AI PRs "must include a disclosure in the PR description" (scope, parts, human testing); omission "may be closed without review"; "Repeated violations will result in a ban from the repository." |
| RetroArch / libretro | AGENTS.md and CONTRIBUTING.md checked, both engineering-only | Silent (de facto permissive) | no policy found; merged agent-authored commits observed by third-party trackers. |
| PCSX2 | https://pcsx2.net/docs/contributing/ + pcsx2 AGENTS.md (raw file verified) | Agents forbidden from posting anything to their GitHub; no full-code-generation; permanent ban risk | "Agents must not use GitHub or any GitHub API, CLI, or web UI automation to open or update PRs, create/edit/close issues or discussions, or post comments." We stay away entirely (already project policy here). |

## What satisfies the strictest targets we actually interact with

Combined kernel + mpv/MAME/Dolphin/RPCS3 denominator (PCSX2 is stricter but we
do not interact with it at all, by project rule):

1. Daniel writes and posts every word that reaches a forge. No agent ever
   opens, edits, or comments — no API, CLI, or web automation, anywhere.
2. Disclosure in the initial PR text / cover letter: that AI was used, the
   model and version (MAME names this explicitly), which parts were generated
   (Dolphin/RPCS3), and what human testing and review happened (RPCS3).
3. Daniel owns every line: able to explain the change and its decisions
   without the assistant. No full-code-generation submissions, nothing
   "clearly vibe-coded" — hardware-evidenced small deltas are our shape.
4. Domain bans: no LLM-authored changes to emulated-console behavior
   (Dolphin; apply the same caution to any emulation core we touch); no AI
   anywhere near mentored programs like VideoLAN GSoC.
5. Silent projects (Kodi, RetroArch, MKVToolNix project-level): disclose
   anyway. It violates nobody's policy and it is our doctrine regardless.

## What the strictest target requires (the kernel)

1. Every kernel patch carries Daniel's human `Signed-off-by:` (he certifies
   the DCO) and an `Assisted-by: LLM Claude Code` style trailer. The AI never
   signs; in-tree precedent for the tag exists ("Assisted-by: LLM coccinelle
   sparse"); editors/compilers are not listed.
2. The cover letter names the tools, describes the inputs, says which portions
   are tool-generated, how it was tested, and what was NOT done (untested
   paths, missing reproducers). Our cover-letter draft already carries a
   version of this; align its wording with the merged docs.
3. The human sender must understand and be able to defend every line;
   maintainers are entitled to reject a series without detailed review
   otherwise. Build clean, pass checkpatch.pl, verify behavior on hardware —
   which is exactly what this project's [proven] runs already do.
4. The AI never submits anything itself, anywhere. Daniel posts everything.
