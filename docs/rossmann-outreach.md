# Reaching the Rossmann ecosystem — concrete plan (verified 2026-09-13)

The targets, verified live:

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

## 4. Serviio forum (parallel track, different audience)

forum.serviio.org — paste `tools/serviio/serviio-forum-post.md`
(Serviio's author reads it; no GitHub presence exists).

## Order of operations

1. consumerrights.wiki entry (no gatekeeper, fastest, feeds search engines)
2. repair.wiki account + technique page
3. Serviio forum post
4. Hand-written email to youtube@rossmanngroup.com linking all three
5. Archive handover to RPG/FULU if they take it up