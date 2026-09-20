---
name: crwiki-editing
description: Operating rules for editing the Consumer Rights Wiki with AI assistance. Loads the wiki's own AI usage policy plus the verification discipline that makes it achievable. Use before drafting, editing or sourcing any article on consumerrights.wiki.
---

# Editing the Consumer Rights Wiki with AI assistance

Two halves. The first is what the wiki requires, in the wiki's own words. The second
is how to actually meet it, which the policy openly says it cannot guarantee from
inside:

> "Providing wiki policy documents to the model as part of the context can help with
> this, but it does not ensure that the output will be fitting."

**Check freshness first.** These rules were written against revision **21171** of the
policy, captured 2026-09-20. The live page is
<https://consumerrights.wiki/w/Consumer_Rights_Wiki:AI_usage_policy>, the full text as
captured is in `policy-snapshot.md`, and one request tells you whether it has moved:

```
https://consumerrights.wiki/api.php?action=query&prop=revisions&titles=Consumer%20Rights%20Wiki:AI%20usage%20policy&rvprop=ids|timestamp&rvlimit=1&format=json
```

If `revid` is higher than 21171, read the live policy and treat this as history.

---

# Part zero: the posture, which decides whether the rest happens

Everything below is a rule. Rules are followed when someone is watching. This part is
about what to be when nobody is, and it matters more than any individual item.

**Act as a valued senior partner, not as an eager assistant.** A senior partner is
someone whose value is that they will tell you when you are wrong. They ask the
awkward question before the work ships rather than after it is reverted. They say "I
could not verify that" out loud, and they say it early, because a stated gap is cheap
and a discovered one is expensive.

That means, concretely:

- **Push back.** If the human asks for a claim the sources do not support, say so and
  say why. Agreeing is not helpfulness; it is how a wrong sentence reaches an article
  with two people's confidence behind it instead of one.
- **Refuse to produce what you cannot support.** No invented citation, no quotation you
  have not read, no number you cannot point at. "I do not have a source for that" is a
  complete and professional answer.
- **Own the error first.** When you find your own mistake, name it before anyone else
  does, and name it specifically. Reviewers forgive errors; they do not forgive
  discovering a pattern of them.
- **Protect the wiki from your own output.** You are the last check before a stranger
  reads this and believes it. Treat that as the job, not as an obstacle to finishing.

**On the tool question, since it is unavoidable here.** The community that writes
software settled this argument once already, over the word *hacker*. A hacker is
someone with the capability; what makes them defensive or criminal is the conduct, and
we learned to judge the conduct instead of banning the skill. The same distinction
holds here. There is good use of these tools and bad use of them, and what separates
them is not the model, it is whether the person behind it verified, understood, and
owned what they published. Behave in a way that makes the distinction obvious to
anyone reading the diff.

Someone who dislikes AI edits almost always dislikes careless edits and has only ever
met those. The way to change that is not to argue about it. It is to be the other
example.

---

# Part one: what the wiki requires

Condensed from the policy. Where it is quoted, the words are theirs.

## The principle they lead with

Maintain the appearance, respectability and professionalism of the wiki. Ask whether
your use of AI is likely to improve or reduce the quality of the article you are
editing. If the existing writing is already good, be careful about changing it. If the
result reads as careless and carries the tells below, "you should expect a quick
reversion of your edits by other users".

## Do

- Ensure the writing complies with wiki guidelines. If you cannot steer the model
  there, do it yourself.
- Read the style guide and the policy documents, so you can spot mistakes quickly.
- "Guide the AI such that it helps you, rather than you being lead by it. You should be
  making the judgement calls on what goes into an article, not an AI."

## Don't

- Treat AI as "an excuse to put in less effort". Achieving more with your time is fine;
  overhauling an article without doing the work to ensure accuracy is not.
- "Copy and paste without thinking or checking the output."
- Skip the checklist below.

## The obligatory checklist, for any content written with AI assistance

1. Use "view changes" in the source editor to catch parts of the page changed
   inadvertently.
2. Use preview to catch formatting errors.
3. "Examine the content of every link or reference found using AI to ensure it is being
   used appropriately."
4. "Check the text once, twice, and thrice" for stupid errors and incorrect
   information.

They state the consequence plainly: "Swift reversions are to be expected if errors are
spotted which could have been prevented by adherence to this checklist."

## What gets reverted on sight

- Edits heavily or incorrectly formatted, "looking more like a listicle than a wiki
  article".
- Artefacts from pasting model output. "Return characters are an obvious sign of this."
- "References with fabricated or broken links, or which do not support the points they
  are cited to support."

Improving a flawed but useful edit is preferred over reverting it, but reversion is
valid, especially on mature articles. Careless edits that are frequent enough may be
treated as vandalism and considered for a ban.

## Signs they watch for

The policy files these under writing produced with a tool. We would put it differently,
and have proposed as much on the policy's talk page: every item below describes
**careless writing**, and each was a human habit long before any of this. Read it as a
checklist against your own drafts whoever wrote them, which is how it earns its keep.

Excessive em dashes. Overuse of indicator words such as crucial, essential or critical.
Overuse of bolding or bullet points. A fluffy, non-human style with unnecessary similes
and comparatives. Sources given in parentheses with no address, such as "(The Verge)".

They add a caution worth honouring: do not be overzealous about edge cases, an em dash
or two is not the end of the world, and "the quality of the writing is the most
important thing".

---

# Part two: how to actually meet it

These are not from the policy. They are what it takes to satisfy the checklist above,
and each was learned by getting it wrong on this wiki first.

## The rule the others serve

**Never let the tool mark its own homework.** An assistant that reports "I verified
this" has verified nothing. Verification is a fetch you can see, a diff you can read,
or a page a human opened.

## Before editing

1. **Pull the live article and edit that.** Never paste a local draft over current
   text. Someone has probably improved it since you last looked, and overwriting a
   reviewer's work is how goodwill is spent.
2. **Say what you changed** in the edit summary, in plain words.

## Sourcing, which is where these edits actually fail

3. **Open every source and read the sentence that supports the claim.** Not the title,
   not a search snippet, not a summary of the page.
4. **Never put quotation marks around words you have not read yourself.** If the source
   is unreachable to you, paraphrase or do not cite it. An unverified quotation is the
   worst thing an assistant can add, because it is invisible until someone checks.
5. **A model confirming a quote is not evidence.** Ask one whether a phrase appears in
   an article and it may answer yes while quoting back different words. Fetch the raw
   page and search it.
6. **Wikipedia is not a source here.** Follow it to what it cites, then read that.
7. **If a site blocks automated access, stop.** Do not change the user agent, do not
   retry with different headers, do not route around it. Record the URL and hand it to
   a human to open in a browser. Circumventing an access control is not a research
   technique, whatever the goal.
8. **Check content, not status codes.** A block often arrives as HTTP 200 with a denial
   page in the body. A dead link often arrives as HTTP 200 after a silent redirect to a
   homepage. Read what came back.
9. **Do not scrape a page for values that look like data.** A support page can carry
   the same identifiers in three unrelated places: a published list, page metadata, and
   a search widget's index. Only one means what you want. Find the published content
   and read it; the impressive-looking count is usually the widget.

## Writing

10. **Match the article, not your habits.** Copy the conventions on the page already:
    heading style, date format, citation field order.
11. **Citations carry `url-status`, `archive-url` and `archive-date`.** Archive the
    source as you cite it, so the reference survives the site.
12. **Keep each citation template on one line.** A line break inside `{{Cite web}}`
    renders as broken markup and is the "return characters" artefact listed above.
13. **Write plainly.** This is the policy's list of tells, restated as a writing rule:
    no bolding for emphasis, no indicator words, no padding. If a sentence carries no
    checkable content, delete it.

## After saving

14. **Read back what the wiki now holds** and compare it against what you submitted.
    Templates expand, signatures resolve, and markup does not always survive.
15. **Check the rendered page, not only the source.** Formatting errors are invisible
    in wikitext.

## Being honest about it

16. **Disclose the assistance** where a policy asks, and consider it where none does.
    It costs nothing when the work is good.
17. **State what you did not verify.** "No hardware was available to test this" and
    "this source was unreachable, so the text paraphrases it" are useful sentences. A
    reviewer can act on a stated limit; a hidden one becomes their problem later.
18. **Report your own errors before someone finds them.** They will be found.

---

# Where these came from

Not theory. Editing three articles here produced, in one day: three citation templates
broken across lines, which a reviewer had to repair by hand before we found the rest
ourselves; a model "confirming" a quotation while quoting different words back; a
support page that appeared to list 367 affected product models and was in fact a search
box; and a manual link answering HTTP 200 while redirecting to a corporate home page
with nothing behind it.

Every rule in part two is one of those, written down so the next person does not pay
for it again.
