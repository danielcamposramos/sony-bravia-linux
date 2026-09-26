# docs

The written record of the project: what these Sony KDL-era BRAVIAs are, what they do and refuse to do (measured, not assumed), the right-to-repair case that follows, and the upstream work it fed.

**Start with [project-status.md](project-status.md)** — the one page a cold-start reader, human or AI, reads first. It maps every lane, what is live, and what is next, and it carries the full document map. This file is the shorter signpost to the folder.

## Read first

- [project-status.md](project-status.md) — canonical status and partner guide, kept current.
- [build-your-own-bravia-portal.md](build-your-own-bravia-portal.md) — the public method guide: give these sets a working portal and media browser on your own LAN, with two DNS overrides and your own hardware.
- [platform-map.md](platform-map.md) · [feasibility-roadmap.md](feasibility-roadmap.md) · [generation-model-map.md](generation-model-map.md) — the platform in depth, the staged plan (content → widgets → root → kernel), and which TVs the work applies to.

## The platform, measured

- [era-media-element.md](era-media-element.md) · [era-key-vocabulary.md](era-key-vocabulary.md) — what the era `<video>` element and the remote/key model actually do, read off the live panel.
- [audio-capabilities.md](audio-capabilities.md) · [kdl-hx855-sink-behavior.md](kdl-hx855-sink-behavior.md) — what the sets accept, by path, and the HX855's behaviour as an HDMI sink, each entry with its evidence.
- [trackid-bgmsearch-recovered.md](trackid-bgmsearch-recovered.md) · [withheld-by-catalog.md](withheld-by-catalog.md) · [worldclock-schema-reconstruction.md](worldclock-schema-reconstruction.md) · [hdmi-cec-audio-system.md](hdmi-cec-audio-system.md) — recovered and reconstructed features, and the one solution rebuilt from scratch.

## The 3D-signalling set

- [3d-signalling-explainer.md](3d-signalling-explainer.md) — the short, tool-agnostic explainer linked in every upstream post.
- [3d-signalling-ecosystem.md](3d-signalling-ecosystem.md) — the cross-brand, cross-software map of why file-based 3D playback fails everywhere and why one standard signal fixes it.
- [3d-blocked-in-browser.md](3d-blocked-in-browser.md) · [legacy-3d-formats.md](legacy-3d-formats.md) · [3d-photos-on-bravia.md](3d-photos-on-bravia.md) — the browser 3D block, the act-three charter (enable all 3D content ever made), and 3D photos measured on the set.
- [dual-surface-hdmi-3d.md](dual-surface-hdmi-3d.md) · [stereo-intent-interface.md](stereo-intent-interface.md) — the driver-side architecture notes behind the HDMI 3D patches.
- [3d-origin-story.md](3d-origin-story.md) — where this began: the 2011 iZ3D licence gift and the line to the campaign.

## The consumer-rights set

- [licence-basis.md](licence-basis.md) · [oss-source-recovery.md](oss-source-recovery.md) — the GPL ground the project stands on: the sets run Linux, Sony shipped the source, and what is left of its listing today.
- [legal-eula-analysis.md](legal-eula-analysis.md) · [regional-documentation-asymmetry.md](regional-documentation-asymmetry.md) · [right-to-repair.md](right-to-repair.md) — Sony's own documents read against what they let Sony do, the same product's paperwork differing by region, and the right-to-repair context (all flagged not-legal-advice).
- [sony-end-of-service-statements.md](sony-end-of-service-statements.md) — Sony's five dated end-of-service notices, each naming both models, archived as primary sources.
- [manuals-index.md](manuals-index.md) — where Sony's own documents live (linked, not hosted), with the provenance split that decides what may be shared.

## Campaign record and reach

- [judging-by-the-cover.md](judging-by-the-cover.md) · [ai-contribution-policies.md](ai-contribution-policies.md) — the doctrine proverb, and how upstreams actually gate contributions (on owned/understood/reviewed, not on "was AI used").
- [partner-review.md](partner-review.md) · [handoff-2026-09-20.md](handoff-2026-09-20.md) — the external senior-partner review of the roadmap, and a partner handoff.
- [i18n/](i18n/) — the problem and the fix in eleven languages, for owners searching in their own words.

## Folders

- [research/](research/README.md) — the working notes and live evidence behind these pages: the method, the recon, the recovered platform, the reviews. Read it to follow the path, not just the result.
- [upstream/](upstream/README.md) — everything taken to another project (media stack and drivers): diagnosis plus a working fix, with the running issue tracker.
- [outreach/](outreach/README.md) — audience-facing posts (TabNews, LTT, Rossmann), as distinct from documentation and upstream contributions.
- [wiki/](wiki/README.md) — the public wiki pages (consumerrights.wiki, repair.wiki) as submitted, and the talk-page arguments behind them.
