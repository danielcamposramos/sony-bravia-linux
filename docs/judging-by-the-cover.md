# Judging by the cover — the campaign proverb, in both languages

Recorded 2026-09-16, after the mpv PR #18490 episode. This is the
campaign's doctrine proverb and where it came from — it lives here in
the repo docs, deliberately **not** in any upstream post (a proverb is
the wrong register for a tracker reply; the replies carry the facts).

## The proverb

- **PT-BR:** "Não julgue um livro pela capa."
- **EN:** "Don't judge a book by its cover." — the original of the
  pair: American English, mid-20th century; earliest recorded form is
  "you can't judge a book by its binding" (1946, _American Speech_).
  The Portuguese saying is its calque.

## The siblings — same blade, other edge

- **PT-BR:** "O hábito não faz o monge." — the gown does not make
  the monk; provenance is not substance.
- **EN/Latin:** "The cowl does not make the monk" — _habitus non
  facit monachum_ (medieval, pan-European: French _l'habit ne fait
  pas le moine_, Italian _l'abito non fa il monaco_).
- **EN:** "All that glitters is not gold." (Shakespeare, _The
  Merchant of Venice_; Latin: _non omne quod lucet aurum est_.)
- **EN:** "Still waters run deep." — silence and plain style are not
  absence of depth (fits the owner's ESL writing being misread).
- **EN:** "By their fruits ye shall know them." (Matthew 7:20) — the
  canonical judge-by-outputs rule.
- **Latin:** _Fronti nulla fides._ — "no trusting appearances."

## Slop, side by side — and where AI slop comes from

The mpv thread put both kinds on the same record, so the ledger can
be shown rather than argued. Two axes, independent: **authorship**
(human / AI-assisted) and **information** (substance / slop).

| | Substance | Slop |
|---|---|---|
| **Human** | HandBrake's review of PR #8100 — judged by code alone, merged in 81 minutes. r0lZ's reply — engaged every claim, corrected none, added real nuance (view-order in the SEI). | The "mucho texto" meme: 529×95 pixels, one image, zero technical content, nothing to check. "Thanks for the slop." |
| **AI-assisted** | PR #18490 — reproduction commands, a 9-file before/after test table, keyframe/side-data counts measured on real files, every claim specific enough to be wrong. | What the guideline rightly fears: unverified padded volume at machine speed — and the reason reviewer attention is scarce enough that cover-judging exists at all. |

**The origin, stated plainly: AI slop is human slop repeated.** The
models were trained on human text — human padding, human hedging,
human fake confidence, human verbosity in issue reports. Wherever an
AI produces slop, a human wrote that slop first; the machine
repeats it, faster. Slop's defining property (low information
density, unverifiable claims, volume without checkable content)
predates AI by centuries — which is exactly why every proverb above
judges the *content* axis and none of them judges the *authorship*
axis. "O hábito não faz o monge" was warning about covers before
there was anything to wear but habits.

The guideline's honest root — scarce reviewer attention — is the one
thing the table validates: the AI-assisted/slop quadrant produces at
machine speed, so covers get judged because books multiply. But the
table also shows the heuristic misfiring in real time: on the day the
cover said "AI," the sloppiest entry in the thread was human-made
and the most checkable entry was AI-assisted. The cure is cheaper
books — short posts, repro commands, measured results — not blinder
judging.

## Why this proverb, for this campaign

The mpv exchange judged a contribution by its cover — the AI
disclosure, the prose length, the non-native English — while the
content carried a reproduction matrix, a measured side-data table,
and claims specific enough to be refuted. The cover was unfamiliar;
the book was fine.

The tech-native proverb makes the irony complete: Linus Torvalds'
**"Talk is cheap. Show me the code."** In that thread the code *was*
shown — and the talk is what got judged.

The doctrine, stated plainly:

1. **Slop is a property of the work, not of the author.** Unverifiable
   claims, padding, low information density — humans produce it, AI
   repeats it (AI learned padding from humans). Authorship is a
   cover; information density is the content.
2. **Judge the artifact, not the provenance.** Reproduction steps,
   measured results, refutable claims, responsiveness in review. A
   contribution that can be checked should be checked, whatever wrote
   its prose.
3. **The cover-heuristic has one honest root:** reviewer attention is
   scarce, and grading every book is expensive. The heuristic is a
   triage shortcut — it misfires when the book at the door is already
   annotated, tested and measured. The cure for expensive review is
   shorter books, not blinder judging.
4. **The blade cuts our way too:** AI assistance does not launder
   anything. A contribution we sign must carry the same standard —
   measured on real machines, every claim checkable — because the
   proverb that defends us against bad judging also obligates us to
   write books that are genuinely worth opening.

## Related in-repo records

- The episode itself: `tools/serviio/upstream-3d-issues/README.md`,
  section "mpv PR #18490 — review round 1".
- The owner's standing question that the maintainers never answered:
  what is "AI-slop," if the sloppiest contribution in the thread (a
  one-image comment with zero technical content) was human-made?
- The counter-example, same day: HandBrake merged the patch —
  judging by the code alone — in an 81-minute window.