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
