# Posted to consumerrights.wiki via the API (tools/crwiki.py), account "Capitain jack",
# on 2026-09-19, right after the account was granted the "confirmed" group (Keith, Discord).
# Every save was verified byte-identical against the submitted text by the client.

| Page | Revision | Source file |
| --- | --- | --- |
| User:Capitain jack (created) | 67807 | user-page-draft.txt |
| Sony (Televisions list, one-line de-orphan) | 67808 | live article + one line |
| Capability gating (created) | 67809 | theme-capability-gating.txt |
| Format abandonment (created) | 67810 | theme-format-abandonment.txt |
| Region locking (created) | 67811 | theme-region-locking.txt |
| Region lock → Region locking | 67812 | redirect |
| Regional withholding → Region locking | 67813 | redirect |
| Geoblocking → Region locking | 67814 | redirect |
| Geo-blocking → Region locking | 67815 | redirect |
| Regional restrictions → Region locking | 67816 | redirect |
| Region code → Region locking | 67817 | redirect |
| Software gating → Capability gating | 67818 | redirect |
| Orphaned format → Format abandonment | 67819 | redirect |
| Format obsolescence → Format abandonment | 67820 | redirect |

No CAPTCHA was requested for any of these edits (confirmed group).

Baseline rule for future edits: pull the live article first (`crwiki.py get`),
edit that, never paste local copies over reviewer edits.

## Second round, 2026-09-20 (same account, confirmed group, no CAPTCHA)

Baseline rule followed: every page was pulled live first and the edit built on that
text, never on the local draft. Each save was verified byte-identical by the client.

| Page | Revision | What changed |
| --- | --- | --- |
| Capability gating | 68017 | answered the reviewer's `{{Citation needed}}` |
| Format abandonment | 68019 | joined 1 citation template broken across lines |
| Region locking | 68020 | joined 2 citation templates broken across lines |
| Sony BRAVIA pre-Android Linux TVs (2011-2012) | 68021 | added Sony's published model rosters |

**The citation-needed answer.** A reviewer split our TechCrunch ref and left the
quote "a key to unlock performance that your PC already has" unsourced. The phrase
is verbatim in that same TechCrunch article, confirmed by fetching the raw page and
searching it rather than trusting a summary (a summariser had "confirmed" it while
quoting different words with the key phrase in brackets). Fixed by naming the ref
and reusing it, so both halves cite the article that actually carries them.

**The broken templates were ours.** Three `{{Cite web}}` templates had literal
newlines inside them, which the reviewer had already had to hand-fix on Capability
gating. Repaired with zero length change (newline to space).

**House style learned from the reviewer's edits to Capability gating**, for future
drafts: years in section headings are italicised (`(''2010'')`); citations carry
`url-status`, `archive-url` and `archive-date`; **Wikipedia is not acceptable as a
source** (ours was replaced with Engadget plus a ghostarchive capture).

**The model rosters.** Sony's withdrawal notices each name every set they apply to.
Three of the notices we cite carry a genuine published list: Twitter S1Q0540 (300
models), Track ID S1Q0522 (141), Skype S1Q0505 (53), 312 distinct models in all,
reproduced in Sony's own size groupings. Where a notice was captured on more than
one country's site the list is identical (S1Q0540 on both the Brazilian and Canadian
sites), so each entry carries "Countries affected" with flag emoji rather than a
per-country breakdown; no notice was found to differ by country.

**Trap worth remembering.** These pages carry up to 1918 `KDL-` strings from three
unrelated sources: the published affected-models list, a `taggedModels` metadata
array (which product pages the article is attached to), and a site-wide `catalog`
JSON plus a model-lookup widget. Only the first is Sony saying a set is affected.
`00269731` looked like 367 affected models and is actually a "type your model
number" search box. Scrape the published list, never the page.

### Wikipedia citations replaced, and the policy talk page opened (2026-09-20)

| Page | Revision | What changed |
| --- | --- | --- |
| Consumer Rights Wiki talk:AI usage policy | created | opened the discussion Keith pointed to |
| Format abandonment | 68024 | HD DVD and pan-and-scan citations replaced |
| Region locking | 68025 | DVD region and Mother/EarthBound citations replaced |

Zero Wikipedia citations now remain in any of the three theme articles.

**Sources used.** HD DVD now cites Toshiba's own announcement of 19 February 2008
(verified here: the page title carries the date and the quoted sentence is
verbatim). DVD regions now cite How-To Geek (both quoted phrases verified here).
Mother/EarthBound now cites the Lost Levels feature, which interviews Phil Sandhop,
the localization director himself, plus its timeline supplement for the 1991
Nintendo Power preview; both pages verified here, and the citation carries no date
because the pages print none. Pan and scan cites StudioBinder.

**Where quoting was avoided on purpose.** StudioBinder returns HTTP 403 to us, so
its wording could not be checked from here. The owner confirmed the site loads for
him, so the source is used, but the sentence paraphrases rather than quotes: an
unverified quotation is the one thing that must not reach an article. Two sentences
also had to be reworded rather than merely re-cited, because they had been quoting
Wikipedia's own words, which cannot survive a change of source.

**Still owed.** archive.org was returning 503 "Temporarily Offline" throughout, so
none of these four citations carries an `archive-url` yet. The house style wants
one; add them once the archive is back.

**Talk page.** The AI usage policy discussion page did not exist, so the owner's
contribution opens it. It discloses that these edits were AI-assisted, supports a
disclosure requirement while arguing it acts mainly on people who were already
careful, and uses two of our own mistakes as the evidence: the citation templates we
broke across lines, and a model "confirming" a quotation while quoting different
words. It cites HandBrake (merged in 81 minutes on the code), MKVToolNix (seven
technical requests, nothing about AI) and mpv (parked, LLM-in-commit-messages rule
landing the day after disclosure).

### AI usage policy discussion (2026-09-20)

| Page | What |
| --- | --- |
| Consumer Rights Wiki talk:AI usage policy | opened the discussion; then a `PS:` reply, posted by the owner himself in the site editor |

The first post discloses that our recent edits were AI-assisted, supports a
disclosure requirement while arguing it acts mainly on people who were already
careful, and uses two of our own mistakes as evidence. The `PS:` reply carries the
other half: that slop predates the tools.

Its four specimens all came out of the citation cleanup rather than out of an
argument, which is why it reads as a sourcing report: Russian Wikipedia dating
Stereo-70 to 1963 in one article and 1965/1966 in another, dvdforum.org dead in DNS
and dvdcca.org on a broken certificate (the two bodies behind DVD region coding,
both unreachable), a manual link answering HTTP 200 while redirecting to a corporate
home page, and Sony's 1918 model-number strings across three meanings.

Historical anchor: Hacktoberfest, October 2020. DigitalOcean's own recap gives
34,595 pull requests accepted by no maintainer, 9,598 labelled spam or invalid,
172,599 aimed at repositories that had not opted in, and 17,260 at excluded
repositories. Re-verified against that recap on 2026-09-20 rather than relying on
the 17/09 check, since the post argues for verification.

The ask is deliberately small and is a naming change, not a policy change: the
"common signs of AI writing" section describes careless writing rather than an
author, and read that way it catches strictly more while no longer needing its
edge-case caveat.

**The owner posted the PS himself**, shortening the heading to `PS:`, indenting it
as a reply, splitting the Hacktoberfest paragraph across lines and bolding the four
statistics plus the two closing claims. `docs/wiki/talk-ai-usage-policy-ps.txt` now
holds his posted text verbatim, not the draft.

**TabNews is closed as a venue for this** (owner's decision, 2026-09-20): reception
there was hostile, and the essay of 17/09 already stands as a dated public record.
A follow-up draft exists at `docs/tabnews-post-criterio-aplicado.md` and is not to
be published.

### Matching the Sony article's conventions (2026-09-20)

| Page | Revision | What |
| --- | --- | --- |
| Sony | 68030 | added the 2011-2012 BRAVIA generation to the controversies table |
| Sony BRAVIA pre-Android Linux TVs (2011-2012) | 68031 | model rosters relisted one model per line |

The BRAVIA article was linked from the Sony article's Products section but had no row
in its controversies table, where comparable pages such as "Sony BRAVIA firmware
update breaks recent televisions" already appear. The new row follows the table's own
conventions: a plain year range in the "2020-ongoing" style used by an existing row,
`TBD` in Aftermath as five of the six rows use, and a linked related article. Its
background cell states the three withdrawals with the model counts from Sony's own
notices (53, 141 and 300), the DLNA versus USB difference for 3D, and the GPL source
removal.

The model rosters were then relisted one model per line, which is how the Sony
article lists the 71 audio and AV models affected by the November 2026 network
service termination. Same content, 494 entries, and it now reads the same way on both
pages.

**Not done, and deliberately.** Our televisions were not added to that November 2026
"Affected models" list. It is Sony's own roster for that termination, it covers audio
and micro component systems, AV receivers, Blu-ray players and home theatre systems,
media players, soundbars and wireless speakers, and it contains no televisions at all.
Adding ours would be a factual error. The BRAVIA withdrawals are a separate and older
sequence, which is why they get their own row instead.

### The audio systems, and our own affected-models list on the Sony article (2026-09-20)

| Page | Revision | What |
| --- | --- | --- |
| Sony BRAVIA pre-Android Linux TVs (2011-2012) | 68032 | the 81 Sony audio products added |
| Sony | 68033 | the withdrawal added as its own incident, with its own affected-models list |

**The audio argument, as the owner framed it.** The point is not whether the Home
Theatre Control application still drives a sound system. It does, and it does so
offline, because it speaks Sony vendor HDMI-CEC rather than talking to a server. The
point is that a television cannot obtain it again. The catalog that offered it was
withdrawn, so a set that loses its applications, after a factory reset for example,
permanently loses a control surface Sony shipped, and the 81 audio products that
application drives lose it with them. Basic BRAVIA Sync on the infrared remote is
firmware and is unaffected.

**Provenance and its limit.** The 81 products are Sony's own compatibility table,
read out of the application's model file and indexed in `docs/manuals-index.md`,
across sound bars (29), Blu-ray home theatre systems (9), receivers and amplifiers
(42) and one wireless headphone. Two entries are combined products, which is why a
naive count returns 78 against Sony's 81. Both articles state plainly that no audio
system was available to test against, so this records what Sony's own application
says it drives, not a tested result. The unverified support URLs from the manuals
index were deliberately not carried over; only the model names were.

**Why a separate incident on the Sony article rather than an addition to the
existing list.** That article's "Affected models" list belongs to Sony's November
2026 network service termination, which names audio and AV products and no
televisions at all. The BRAVIA withdrawal is a different and older sequence, so it
now has its own incident section with its own list, alongside the controversies-table
row added earlier. The television rosters stay in the main article and are linked by
section, since duplicating 312 models onto the parent page would serve nobody.
