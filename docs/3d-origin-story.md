# The 3D origin story — from a gifted iZ3D license to the SEI campaign

The SEI signalling work in this repo ([3d-signalling-explainer.md](3d-signalling-explainer.md))
and the upstream campaign behind it didn't come out of nowhere. This
page records where the author's 3D work actually started — mostly so
that the person who made it possible gets cited by name. He is owed
one.

## The iZ3D era (2011)

In February 2011 the author — then a teenager who couldn't afford the
hardware — was corresponding directly with **Vadim Asadov**, CEO of
iZ3D, the San Diego company behind the 22" passive-polarized 3D
monitor and the DirectX interceptor driver that forced stereoscopic 3D
into games that never shipped with it.

The thread was a market-entry pitch from the author: don't fight for
the USA/EU top market first, enter through Brazil instead — nationwide
TV advertising there was cheap and trivial to buy (three stations,
Globo/SBT/Record, ~99% coverage), and he offered to negotiate
government cooperation on both sides. The pitch closed with the part
that has aged the best (quoted from the author's original email,
2011-02-01):

> I dream on Brasilian and Russian minds developing something that
> surely can overkill the big ones since I was a little kid, like
> multiple stereo rendering or capturing to achieve an real hologram.

Vadim answered the business case honestly (quoted from his reply,
2011-02-01 — shared as the author's own correspondence, with respect):

> This is not an issue of USA / EU and / or Brasil / Russia -
> especially not an issue with Russian government.
> You can not find better place to make monitor than Asia - this is a
> fact.
>
> Also fact is that Samsung spent about 10-20 mio USD in Russia for
> ads and marketing - we don't have this money

And then he did the thing this page exists to record: **iZ3D gifted
the author a full "iZ3D All Outputs" license** — activation email from
iz3d.com, 2011-02-02 (from Vadim following the thread), license record
verbatim from the author's archive:

```
Customer ID:       DR034593
Full name:         Daniel Campos Ramos
Registration name: Daniel Ramos

Order ref. no:      368345
Licenses purchased: 1
Licenses granted:   1
Licenses activated: 1

Program title:      iZ3D All Outputs
```

That license is how Max Payne played in anaglyph stereo on an ordinary
monitor, years before the author ever touched a 3D TV. It was a gift
from a company founder to a kid who had offered them his country for
the price of an email — and it is the earliest instance of the same
pattern the upstream campaign ran on twenty years later: **diagnose,
offer the fix, get taken seriously.**

## What happened to iZ3D

iZ3D folded around 2012, with the rest of the consumer-3D wave. The
driver is abandonware now; the monitors are collector's items. Vadim
Asadov's honest answer was right — a small company could not outspend
Samsung in anyone's market, and the "big ones" won the round. But the
kid's hologram line turned out to be the long bet: stereoscopic 3D
died twice (gaming, then TV), and the people who kept depth alive were
the ones doing it for love, on secondhand hardware, with gift
licenses.

## The arc, stated plainly

- **2011:** anaglyph Max Payne through the gifted iZ3D driver — 3D
  development, contributed-to rather than bought.
- **2026:** two dead 2011/2012 Sony 3D TVs, on the owner's own LAN,
  made to auto-engage 3D again by reverse-engineering the signalling
  ([the explainer](3d-signalling-explainer.md)).
- **2026:** the diagnosis goes upstream — HandBrake merges [PR
  #8100](https://github.com/HandBrake/HandBrake/pull/8100) (x264
  frame-packing SEI on encode), the ffmpeg reports ([#24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530),
  [#24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531)) follow,
  and the whole ecosystem's oldest unanswered question — *why do my
  3D rips play flat?* — finally has a published, hardware-proven
  answer.
- **Next:** [Knowledge3D](https://github.com/danielcamposramos/Knowledge3D)
  — knowledge as a place you walk through instead of a window you
  look through. The 2011 email already described it: "multiple stereo
  rendering or capturing to achieve an real hologram." Same dream,
  better tools.

Vadim Asadov: if this page ever reaches you — the license worked. It
took twenty years and a different display, but the kid you gifted
"All Outputs" to spent 2026 teaching HandBrake how to write 3D
signalling the way your driver once forced it into Max Payne. Consider
this the citation you were owed.

---

*Correspondence quoted with the author's permission from his own
archive. The author's email address in the headers is deliberately
omitted; everything else is verbatim.*