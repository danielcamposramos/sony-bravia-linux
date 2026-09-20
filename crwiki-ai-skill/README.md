# crwiki-ai-skill

Operating rules for editing the [Consumer Rights Wiki](https://consumerrights.wiki)
with AI assistance, offered to that wiki rather than imposed on it.

## What is here

| File | What it is |
|---|---|
| `SKILL.md` | The rules. Two halves: what the wiki requires, then how to actually meet it. |
| `policy-snapshot.md` | The wiki's AI usage policy as captured, stamped with its revision id so you can tell whether it has moved. |
| `crwiki-ai-skill.zip` | All of the above, for anyone who would rather have a file than a link. |

## Why it exists

The wiki's own policy names a gap and says plainly that it cannot close it:

> "Providing wiki policy documents to the model as part of the context can help with
> this, but it does not ensure that the output will be fitting."

A policy states what is wanted. These are the operating rules that produce it. Every
rule in part two of `SKILL.md` is something we got wrong on that wiki first, and the
document says which.

## Using it

It is plain Markdown on purpose, so it is not tied to any one assistant:

- **Claude Code or Claude.ai** — `SKILL.md` carries the usual frontmatter, so drop the
  folder into your skills directory and it loads as `crwiki-editing`.
- **ChatGPT or similar** — paste `SKILL.md` into a custom instruction or project.
- **Anything else, including a local model** — paste it at the top of the conversation.
- **No assistant at all** — it works as a human checklist, which is what it started as.

Keep `policy-snapshot.md` alongside it. An assistant that cannot reach the wiki should
still know the rules it is bound by rather than inventing them.

## Check it is still current

These rules were written against revision **21171** of the policy, captured
2026-09-20. One request tells you whether that is still the live revision:

```
https://consumerrights.wiki/api.php?action=query&prop=revisions&titles=Consumer%20Rights%20Wiki:AI%20usage%20policy&rvprop=ids|timestamp&rvlimit=1&format=json
```

If the `revid` comes back higher, read
[the live policy](https://consumerrights.wiki/w/Consumer_Rights_Wiki:AI_usage_policy)
and treat the snapshot as history. The whole argument of `SKILL.md` is that assuming
is how this goes wrong.

## Status

Offered, not adopted. It lives here because we arrived at that wiki recently and
creating pages in someone else's project namespace is not ours to do. If the editors
there want it, they are welcome to move it on-wiki and maintain it as their own.

Corrections are welcome, particularly from anyone who has reverted a careless edit and
knows exactly which rule was missing.

## Licence

CC0. Take it, change it, put your name on it. It is only useful if it spreads.
