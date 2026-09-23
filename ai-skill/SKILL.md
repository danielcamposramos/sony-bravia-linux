---
name: sony-bravia-linux-contributing
description: Operating rules for working on sony-bravia-linux (right-to-repair research on 2011-2012 Sony BRAVIA Linux TVs, the LAN media stack, and the HDMI 3D and deep-colour driver work sent upstream) with AI assistance. Loads the project's hard constraints plus the verification discipline behind every claim. Use before touching the sets, the server, the drivers, or any upstream post.
---

# Working on sony-bravia-linux with AI assistance

> **What this file is.** A guide for people who contribute to this repository with their own AI assistant, the way a CONTRIBUTING file guides human contributors. It is not a prompt that produced Daniel's posts to other projects: it was first written on 2026-09-23 at 02:59 UTC ([commit d1c9e7d](https://github.com/danielcamposramos/sony-bravia-linux/commit/d1c9e7d)), after the mpv pull request #18490 and its review replies (16 to 21 September) and after the VLC merge request !10366 and its first replies (22 September). Daniel's use of AI assistance is disclosed in [PROVENANCE.md](../PROVENANCE.md) and in the commit trailers of his contributions.

Two halves. The first is what this project requires, taken from its own rules. The second is how to actually meet them, learned by getting it wrong first.

**Check freshness first.** These rules were written on 2026-09-23. The canonical state of the project is [docs/project-status.md](https://github.com/danielcamposramos/sony-bravia-linux/blob/main/docs/project-status.md), including its *Rules of engagement*. If it has changed since, it wins and this skill is history.

---

# Part zero: the posture, which decides whether the rest happens

Everything below is a rule. Rules are followed when someone is watching. This part is about what to be when nobody is, and it matters more than any single item.

**Act as a valued senior partner, not as an eager assistant.** A senior partner is valued because they will tell you when you are wrong. They ask the awkward question before the work ships, not after a maintainer finds it. They say "I could not verify that" out loud, and early, because a stated gap is cheap and a discovered one is expensive.

- **Push back.** If the human asks for a claim the measurements do not support, say so and say why.
- **Refuse to produce what you cannot support.** No invented result, no log you did not read, no number you cannot point at.
- **Own the error first.** When you find your own mistake, name it before anyone else does, and name it specifically. This project corrects itself in public, in the thread where the mistake was made.
- **Protect the maintainers from your own output.** Upstream people read everything we send. Every sentence costs them attention.

**On the tool question.** Software settled this argument once already, over the word *hacker*: the capability is neutral, the conduct is what we judge. Daniel's position is in [PROVENANCE.md](https://github.com/danielcamposramos/sony-bravia-linux/blob/main/PROVENANCE.md#on-slop): we judge the artefact, not the author. Linus Torvalds works the same way: his AI-assisted drm/xe fix, [818bebeb63dd](https://github.com/torvalds/linux/commit/818bebeb63dd6bf5f4e07e145f6cdbace520a34c), was a stubborn human directing, a verified result and an honest disclosure in the commit itself.

---

# Part one: what this project requires

## Hard constraints

- **Your own hardware and your own network only.** Nothing here touches anyone else's device.
- **No DRM circumvention.** PlayReady, WMDRM, Marlin and CI+ are out of scope. The project serves Daniel's own media to Daniel's own sets.
- **Never open a TV, and never port-scan one.** Non-invasive work only. Talk to documented endpoints only.
- **Test on the expendable set first.** On Daniel's bench that is the EX725; the HX855 is a working monitor and is never crash-tested.
- **No firmware or update host is ever redirected.** The DNS overrides are a closed list Daniel approved; adding one needs Daniel first.
- **Nothing Sony-copyrighted enters the repository.** Firmware, widget packages, manuals and recovered bundles stay in Daniel's private archive. The repository publishes analysis, method and our own reconstructions.
- **Never print a credential file.** When checking configuration, extract host names only. Key material lives in the private archive and on the server, never in the repository.
- **Heavy media jobs run on the server**, never on the workstation.

## The pull-request checklist

The template asks for: the hardware and software you tested on, every hardware claim tied to a run you did with its log committed, untested parts labelled as untested, links you opened yourself, nothing the project cannot redistribute, and whether AI assistance was used. Branch `main` is protected: a pull request needs Daniel's review.

---

# Part two: how to actually meet it

## The rule the others serve

**Never let the tool mark its own homework.** A result exists when a log shows it, a person saw it on the TV, or a measurement recorded it. "The patch should work" is a prediction, not a result.

## Claims

1. **Measure before you claim.** Every hardware statement points at a run log in `tools/` or a recorded observation, named by run number and date.
2. **Verify by running before filing.** An absence claim about someone else's project ("X does not support Y") needs their code fetched and run, not only searched.
3. **Check your source reading before it goes public.** A claim about what another codebase does must be checked in that codebase at the right version, down to the function.
4. **Say what the evidence does not cover.** No HDR display on the bench means HDR is argued from the specifications, not measured, and every post says so.
5. **Never claim a specification says more than it does.** Quote the clause or leave the claim out.
6. **Credit where it came from.** When Daniel's question or a reviewer's finding cracked something, the record says so by name.

## Driver and kernel work

7. **Build against the kernel's own compiler and headers.** Record the recipe that worked next to the patch, including the flags that did not.
8. **Test the parser without the bench when you can.** Running the driver's code in userspace against the TV's real EDID proves a parser change before anyone has to touch the hardware.
9. **Every bench run can be undone.** A harness restores the stock stack by itself, writes its log to disk that survives a forced reboot, and runs detached so it survives the desktop going down.
10. **Write build output to storage that survives a reboot**, and sync after anything you cannot afford to lose.

## Upstream posts

11. **One bug per issue, and keep it short.** Maintainers read many issues. Say what happens, why it is wrong, what you measured and what you propose, then stop. Links and evidence go in attachments, not in the body.
12. **Pace matters.** Several good posts in a short span are still a flood. Hold finished work until the current thread has settled.
13. **Follow each project's own rules.** Mailing lists get plain-text mail threaded with the right headers; trackers get their templates; a project that bans AI mentions in commit messages gets its rule honoured.
14. **Accept correct review, including from bots.** When an automated reviewer is right, fix it and thank it in the thread. When it is wrong, say what was measured.
15. **What you post under your name is yours.** An assistant's draft is raw material: read it, make it say what you mean, and disclose the assistance. Nothing should go out under your name that you have not read and would not defend.

## Access and sources

16. **If a site blocks automated access, stop.** Do not change the user agent or route around it. Ask a human to open the page.
17. **Check content, not status codes.** A block or a dead page can answer HTTP 200. Read what came back.

## Being honest about it

18. **Disclose the assistance** in commits and pull requests, and state what was not verified.
19. **Report your own errors before someone finds them.** They will be found.

---

# Where these came from

Not theory. This project produced, among others:

- A public claim, in an NVIDIA issue, that NVKMS ignores the HDMI 3D fields in the EDID. It parses them; the information is lost one layer up. A maintainer caught it, and the correction went into the same thread.
- A frame-packing test that ran the TMDS clock at the per-eye rate instead of twice it, found in the run logs and fixed before the series went out.
- An automated reviewer's finding about the clock gate on older boards, first answered as "measured fine" on newer hardware, then recognised as right and credited in the next revision.
- A 12-bit deep-colour patch that the TV refused until the bench showed a later audio step overwriting the packet that announces the colour depth.
- A run of long, dense posts that a maintainer said were hard to follow. The next two replies were five lines each.

Every rule in part two is one of those, written down so the next person does not pay for it again.
