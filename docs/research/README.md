# research

The working notes behind the finished docs: how the platform was measured, what the live sets and the recovered code actually said, and where each conclusion came from. Read this to follow the method, not just the result.

The finished, reader-facing pages live one level up in `docs/`. This folder is the evidence and the reasoning that produced them.

## The method, in the order it runs

1. **Measure on the live hardware first.** Both TVs are on the LAN, DHCP-pinned by MAC; the HX855 is also this workstation's monitor. Nothing about the platform is asserted from a spec sheet when it can be read off the panel or the wire instead. `liverecon/` holds the raw artifacts, one file per capture.
2. **Mark every claim's confidence.** The pages use `[C]` confirmed (read directly, or reproduced), `[proven]` with a dated hardware run, `[qualified]` for a reasoned inference, and say plainly when something is a plan rather than a result.
3. **Verify by running before filing anything upstream.** A code reading is a hypothesis; the claim only goes out after the file has been fetched and the behaviour reproduced. (The rule was learned the hard way and is kept as a rule.)
4. **Get it reviewed.** Several notes were put to independent partner models with the same charter and the raw data, and their reviews are kept beside the study so the reasoning can be checked, not just the verdict.
5. **Stay non-invasive and lawful.** This is a right-to-repair study of the owner's own hardware. Where a vulnerability is looked at, it is to answer "is this set exposed?", not to attack anything; the sets are studied as they shipped.

## What is here

### Live recon — the primary evidence

- [liverecon/](liverecon/) — the measurements: the port map and UPnP/DLNA survey ([FINDINGS.md](liverecon/FINDINGS.md)), the CERS/IRCC and MediaRenderer service descriptions (the `cers_*` and `dmr_*` XML), the sets' EDID (`hx855-edid*`), wire captures (`*.pcap`) of cold boot, power-up, the browser lane and the internet-content lane, and the analyses that read them ([browser-lane-test.md](liverecon/browser-lane-test.md), [biv-video-lane.md](liverecon/biv-video-lane.md), [ota-internetcontent-session.md](liverecon/ota-internetcontent-session.md), [rd1-browserhome.md](liverecon/rd1-browserhome.md), the AppliCast widget lane, the deep-colour NVIDIA-vs-amdgpu OSD comparison, the origin sweep).

### The recovered platform

- [kernel2635-survey.md](kernel2635-survey.md) — what Sony's own GPL kernel drop (recovered from the Wayback capture) contains.
- [appliwidget-programming.md](appliwidget-programming.md) — the AppliCast widget platform, reconstructed from the scavenged widget corpus.
- [oss-manifests/](oss-manifests/) — the OSS package lists Sony published for these sets, and the group they belong to.

### The browser lane and its exposure

- [presto-cve-2011-2628.md](presto-cve-2011-2628.md) — a study of whether the set's 2010-era Opera Presto browser is exposed to a known 2011 issue: an assessment of the risk an owner inherits from software that was frozen and abandoned, not an attack. Its partner reviews sit alongside it ([Kimi K3](partner-review-presto-kimi.md), [the four-model panel](partner-review-presto-panel.md)); mainstream classifiers refused the study on this owner-hardware work, and the open-weight fleet reviewed it without incident.

### Direction and synthesis

- [noninvasive-avenues.md](noninvasive-avenues.md) — the synthesis of the six-lane research workflow: the ways forward that touch nothing invasive.
- [webfindings.md](webfindings.md) — the web-research digest, with sources and the agents' own confidence notes.
- [opus-consult-raw.md](opus-consult-raw.md) — a senior-partner review of the roadmap, kept raw.

### The deep-colour and HDMI work (feeds the upstream driver patches)

- [deep-color-dual-upstream-handoff-2026-09-22.md](deep-color-dual-upstream-handoff-2026-09-22.md), the nouveau colour-format and deep-colour design and plan notes, and [nouveau-hdr-gap-2026-09-22.md](nouveau-hdr-gap-2026-09-22.md) — the measured facts kept separate from the source conclusions, the restart points for the paired nouveau and NVIDIA submissions in [../upstream/](../upstream/).
