# Reaching the Rossmann ecosystem — concrete plan (verified 2026-09-13)

The targets, verified live:

## 0. Rossmann in his own words — the timing could not be better (2026-09-18)

Reviewed a set of his recent videos directly (transcripts held privately,
rule 9b; public videos cited by title and timestamp). The alignment is
not general, it is exact and current:

- **His live campaign is Sony.** He opens one episode with "welcome to
  today's episode of how we are getting Sony back" (*Sony admits you own
  your games*, ~0:00). The series is about Sony revoking purchased
  content and Sony's court argument that "it is unreasonable for
  customers to believe that they own the games that they bought and paid
  for." Our BRAVIA entry lands on his target during his push, not into a
  cold void.
- **consumerrights.wiki is his channel, literally.** In his own words the
  wiki "made about six different news sites over this," he links wiki
  articles in his videos, and it is "designed to be a collaborative
  effort of everybody who watches this channel ... Many of you have
  created a table that goes into every single time Sony has mentioned on
  their website that you own" your content (*Sony admits you own your
  games*, ~0:20-1:30). He closes another episode with "Please do keep
  contributing to the Consumer Rights Wiki. It is how he holds companies
  like Sony accountable." So the path to Rossmann is not an email, it is
  a strong wiki entry, which we now have.
- **The thesis our evidence refutes is the quote he ends on.** He signs
  off most videos with a corporate lawyer's public-hearing line: "It is
  in fact the manufacturers who have the relevant rights, not consumers"
  (the speaker later sued Rossmann over its use and lost). That sentence
  is exactly what the BRAVIA record answers: Sony documented the features,
  shipped them, then withdrew them while the buyer still owns the
  hardware; the GPL source obligation the manufacturer itself points to
  was withdrawn. The manufacturer's "rights" did not keep the product
  working; the owner's ownership is what is stranded.

**Strategic implication.** The 2026-09-13 plan below still holds, but the
priority order shifts: the single highest-leverage move is that the
consumerrights.wiki BRAVIA entry (posted 2026-09-18, now sourced entirely
to Sony's own documents, dated end-of-service notices naming both models,
and independent press) is **strong and discoverable during his active
Sony campaign**. He and his community source from that wiki. Making noise
directly at him is lower-value than making the wiki entry unmissable and
letting his existing sourcing pipeline find it. A brief, factual note in
the wiki community channels he watches (not a pitch) is the natural
nudge.

## 1. consumerrights.wiki — FULU Foundation (Rossmann-founded)

Open-edit MediaWiki, **~1,461 articles, no account required to edit**
(registering keeps edits under one identity). Documents bricked devices,
revoked features, DRM-locked consumables, abandoned products.

**REGISTER AN ACCOUNT before creating the entry** — not just to keep edits
under one identity: it credits the work to its author, and if FULU's
Repair Bounty Program picks up any of this platform's bypass work, a
registered account is how they trace and pay out (bounty mechanics aren't
documented on the front page; ask in their Zulip once registered).

- The Sony BRAVIA KDL story is a textbook entry: EOL'd smart-TV platform,
  online services shut down, firmware downloads removed (Jan 2022), even
  the GPL source downloads deleted from Sony's own site — hardware fully
  capable (12-bit X-Reality, active 3D) left to die.
- Entry paths: `/w/Consumer_Rights_Wiki:Create_page` (guided creator),
  first-article guide at `/w/Consumer_Rights_Wiki:Write_your_first_article!`,
  suggestion list `/w/Article_suggestions`.
- Community: Zulip (`zulip.consumerrights.wiki`) + Discord — good place to
  ask which category fits before creating the page.

## 2. repair.wiki — Repair Preservation Group (501(c)(3))

- Free account signup at repair.wiki; read `RepairWiki:Guidelines` first;
  check for an existing Sony TV page to avoid duplicates.
- Home for the *technique* content: the DLNA 3D auto-detection fix
  (frame-packing SEI), service-mode findings, board/chassis notes
  (AZ2-F / AZ3). Anything a future owner-repairer would need.

## 3. youtube@rossmanngroup.com — the man himself

His channel lists this as the contact, with the note
**"Louis reads this (if not written by AI)"** — so the email must be
hand-written by the owner, short, in first person. Talking points (not
prose — write it yourself):

- What: 2011/2012 Sony BRAVIA Linux TVs (pre-Android), both ends of the
  line (entry EX725 + high-end HX855), owner-owned, on my own LAN.
- What Sony did: killed the platform, pulled firmware and even the GPL
  sources; the 3D feature the panels are fully capable of silently broke
  for DLNA playback.
- What I did: reverse-engineered why (H.264 frame-packing SEI vs Matroska
  StereoMode — the DLNA player only reads the SEI), and restored fully
  automatic 3D on stock Serviio with one profile + two small tools;
  lossless, no DRM circumvention anywhere (no PlayReady/Marlin/CI+ content
  touched — this is signalling metadata for standard files).
- The punchline he'll like: commercial servers "solve" this with paid
  re-encodes; the free fix is a 16-byte SEI the TVs were built to read.
- Offer: the platform's now-unobtainable research material (firmware
  images, service manuals, Sony widget-server content — 500 files, ~700MB)
  is packed in a **password-protected archive on the owner's own
  self-hosted server in Brazil** (7z, AES, encrypted headers, not indexed,
  link + password shared only with RPG/FULU):
  `https://zionbtnet.ddns.net/downloads/sony-bravia-kdl-research-archive.7z`
  — **offered to Repair Preservation Group / FULU for preservation**;
  their call, their legal footing, the right hands. (The password lives
  only in the offline `rossmann-email-draft.md`, never in this repo.)
- Links: repo, discussion #1, the Serviio forum thread once posted.
- One line on AI assistance (honesty matters to him): research and tooling
  were done with an AI agent's help under my direction, every conclusion
  verified by me on the actual hardware. Say it in your own words.

### Why hosting it on the owner's own Brazilian server (legal context, not
### legal advice)

Brazil's statutes are NOT more permissive than the US for redistribution:
Lei 9.609/98's backup exception covers a single safeguard copy for the
legitimate owner's own use, and its interoperability exception is for the
user's own exclusive use — neither authorizes redistributing Sony's
firmware/manuals to third parties. What differs is the machinery: Brazil
has **no DMCA-style notice-and-takedown** (Marco Civil da Internet, Lei
12.965/2014, art. 19 — an application provider becomes liable only after
failing to comply with a *specific court order*; art. 19 §2 defers
copyright liability to specific legislation). A non-indexed,
password-gated share on a server physically in Brazil, disclosed only to a
repair nonprofit, has no takedown pipeline pointed at it — removal would
take a Brazilian court order against a private individual over
preservation material for discontinued hardware. That, plus removing every
Sony byte from the US-hosted GitHub repo (done — history rewritten), is
the exposure posture: our own work public in the US; Sony's material
gated, on our soil, offered to the movement.

## 4. Serviio forum (parallel track, different audience) — DONE

Posted (2026-09-13), live at:
https://forum.serviio.org/viewtopic.php?f=7&t=31269
(BBcode version swapped in via edit; Serviio's author reads the forum —
no GitHub presence exists.)

## Order of operations

1. consumerrights.wiki entry — DONE (2026-09-13), live at
   https://consumerrights.wiki/w/Sony_BRAVIA_pre-Android_Linux_TVs_(2011-2012)
   (product-line page via the guided creator; draft in
   docs/wiki/consumerrights-wiki-entry.txt)
2. repair.wiki account + technique page (draft ready in
   docs/wiki/repairwiki-technique-page.txt) — BLOCKED: site down for
   maintenance with no firm date (2026-09-13); revisit later, not a
   dependency for the email
3. Serviio forum post — DONE (see section 4)
4. Hand-written email — SENT 2026-09-13 (hand-rewritten by the owner; archive
   offer + password included; response window is weeks, not days — Louis
   reads them all but slowly). Sent to BOTH youtube@rossmanngroup.com
   (Louis's video-channel inbox) and help@rossmanngroup.com (verified legit:
   the repair-shop help line, published on boards.rossmanngroup.com —
   staff-triaged, board-repair techs, a second and arguably warmer
   audience). Awaiting reply from either.
5. Archive handover to RPG/FULU if they take it up
5. Archive handover to RPG/FULU if they take it up