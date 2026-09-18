# Sony's own end-of-service statements — primary sources

Sony Brasil published dated support articles announcing the end of
specific TV services. The owner captured all three to the Internet
Archive on 2026-09-18, so they are permanent and citable. **Each names
the KDL-46EX725 and the KDL-46HX855 explicitly** among affected models —
so this is Sony's own published statement about our exact sets, not owner
observation.

These are the primary, verifiable sources the consumerrights.wiki
{{Incomplete}} notice asked for.

## The three notices

### TrackID / Artist Information — the service this repo reverse-engineered

- **Title:** "Informações do Artista e Track ID não funcionarão"
- **Sony article ID:** S1Q2522 · last modified 11/03/2025
- **Live URL:** sony.com.br/…/kdl-46hx855/articles/S1Q0522
- **Archive:** https://web.archive.org/web/20260918042547/https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx855/articles/S1Q0522
- **What it says:** Artist Information and Track ID will no longer work;
  the same applies on Blu-ray players and Blu-ray Home Theatre systems;
  other information continues to work as before.
- **Names our models:** KDL-46EX725 ✓ and KDL-46HX855 ✓ (among ~130 sets).

This is Sony's own confirmation of the TrackID shutdown we investigated
independently on 2026-09-18 (the empty widget shells, the Gracenote/SMRP
client bundle, the button that phones nothing — see
[trackid-bgmsearch-recovered.md](trackid-bgmsearch-recovered.md)). The
button returns "esta opção não está mais disponível" because Sony
announced exactly that.

### Skype

- **Title / notice:** Skype end of service
- **Sony article ID:** S1Q2505 · last modified 11/03/2025
- **Archive:** https://web.archive.org/web/20260918042421/https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx855/articles/S1Q0505
- **What it says:** reaffirms the May 2016 notice that Skype would no
  longer be available on Blu-ray players and BRAVIA televisions after
  June 2016; the Skype service for televisions officially ended 30 June
  2017; Sony apologises for any inconvenience.
- **Names our models:** KDL-46EX725 ✓ and KDL-46HX855 ✓.

### Twitter / TV Tweet

- **Title:** "Fim da disponibilidade do Serviço Twitter"
- **Sony article ID:** S1Q2540 · last modified 11/03/2025
- **Archive:** https://web.archive.org/web/20260918042710/https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx855/articles/S1Q0540
- **What it says:** because of a Twitter login-API change, connecting to
  Twitter (TV Tweet / Twitter) is no longer possible on TVs released
  2010–2016; the Twitter icons were removed from the listed models in
  March 2018.
- **Names our models:** KDL-46EX725 ✓ and KDL-46HX855 ✓.

### Facebook

- **Title:** "Rescisão do app do Facebook em certos televisores"
- **Sony article ID:** S1Q2489
- **Archive:** https://web.archive.org/web/20260918050451/https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx855/articles/S1Q0489
- **What it says:** Facebook, Inc. decided to stop providing the Facebook
  application on certain devices including some Sony TV models; from 27
  April 2015 the app would no longer be provided.
- **Names our model:** KDL-46HX855 ✓. Corroborates the "Facebook widget
  shows as Deleted in the catalog" observation elsewhere on the wiki with
  Sony's own dated announcement.

### Video & TV SideView (second-screen companion)

- **Title / notice:** end-of-function for Video & TV SideView
- **Sony article ID:** S1Q2517
- **Archive:** https://web.archive.org/web/20260918050316/https://www.sony.com.br/electronics/support/televisions-projectors-lcd-tvs/kdl-46hx855/articles/S1Q0517
- **What it says:** the TV-programme and video functions would no longer
  be offered by Video & TV SideView after 24 May 2017.
- **Roadmap tie-in:** the phone-as-remote / second-screen capability is a
  candidate to reimplement from the rd1 portal (feasibility-roadmap A6).

### The source hub, and a broken link on Sony's own FAQ

The owner archived the model's support FAQ hub itself
(sony.com.br/electronics/support/product/kdl-46hx855/faqs, snapshot
20260918050407), which links out to these per-service notices. Noted for
the record but **not** proposed as a wiki claim: one of the FAQ's own
outbound links, article 00258962, returned HTTP 504 during archiving and
was also down in the owner's browser on 2026-09-18. A single gateway
timeout can be transient, so it is held as an observation to re-check,
not cited &mdash; if it is persistently dead it becomes a small, fair
illustration that even the vendor's live support index has decayed.

## Why this matters for the record

1. **It resolves the sourcing challenge.** Every "the service ended"
   claim on the wiki can now cite Sony's own dated announcement, archived,
   naming the exact model — not a forum post or owner observation.
2. **It is Sony confirming the pattern, one service at a time.** Twitter,
   Skype, TrackID: each a separate dated notice, each blaming an external
   cause (a partner's API, a third-party service) while the hardware kept
   working. That is precisely the right-to-repair thesis — the panels are
   fine; the pillars they depend on were switched off — stated by Sony
   itself.
3. **TrackID closes tonight's loop.** We found the dead button and the
   preserved client independently; S1Q2522 is Sony's matching
   announcement. Independent reverse engineering and the vendor's own
   notice agree.

## The distinction to keep (per [legal-eula-analysis.md](legal-eula-analysis.md))

These notices are Sony discontinuing *services*, which the EULA reserved
the right to do. They are strong as **documentation that the services
ended and which models lost them**, and as consumer-rights context — not
as proof of a contract breach. The non-disclaimable point remains the GPL
source deletion; these notices are the dated, model-named backbone of the
"what was lost" record.

## Related

- [trackid-bgmsearch-recovered.md](trackid-bgmsearch-recovered.md)
- [withheld-by-catalog.md](withheld-by-catalog.md)
- [legal-eula-analysis.md](legal-eula-analysis.md)
- [regional-documentation-asymmetry.md](regional-documentation-asymmetry.md)
