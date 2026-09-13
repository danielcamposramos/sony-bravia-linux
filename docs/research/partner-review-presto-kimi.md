# Partner review: Presto CVE-2011-2628 study — Kimi K3

- **Reviewer:** Kimi K3 (`kimi-k3:cloud` via ollama), 2026-09-13
- **Subject:** `docs/research/presto-cve-2011-2628.md` + raw output `docs/research/liverecon/presto_study.json`
- **Charter:** 5-question adversarial review (version lineage, ISDB-Tb signalling compatibility, Linux 2.6.35 MIPS memory claims, delivery-lane ranking/omissions, experiment-ladder readouts), verdicts + severity-ranked findings + next-6-actions.
- **Provenance note:** a Claude Opus senior review was commissioned first but was refused twice by the provider's real-time cyber safeguards (owner-hardware right-to-repair study, no third-party devices, public 15-year-old CVE — flagged anyway; request IDs req_011Cf1rq6yagqL6JWpNk9Cvq, req_011Cf1s3seGHbzeKoavo12Q6). Kimi K3 was substituted as senior partner per project owner's decision. A GPT Astra (gpt-6-astra, reasoning high, codex CLI) chained consult was then also flagged by the provider's cyber classifier at its first file read (2026-09-13) and abandoned. A four-model open-weight panel (qwen3.5:397b, kimi-k2.7-code, deepseek-v4-pro, nemotron-3-ultra, via ollama) reviewed on top of this document; see `partner-review-presto-panel.md`.
- Review body below is verbatim (reconstructed from the ollama tmux transcript; terminal-redraw duplication removed).

---

# VERDICTS

## Q1 — Version-lineage reasoning: **CONFIRMED** (with one factual repair required)

The inference is sound; the raw research contains an internal contradiction that must be resolved.

- The core-band argument holds: author-tested RCE covers cores 2.2.x→2.8.131; the frameset-unload path is core layout teardown, not platform glue; 2.7.61 sits inside by one build under the RCE-verified 2.7.62. The only fix ever shipped is desktop 11.11 (May 2011) — after the 2011 TV SDK (Kjevik-era core, Dec 2010) would have frozen. For this build to be *safe*, Opera would have had to backport an unreleased security fix into a frozen embedded branch with zero advisory record, while publicly declining to patch even the maintained Mobile line. Burden of proof is on invulnerability, not on vulnerability.
- **Divergence risk, honestly stated:** the plausible divergence is not a backported fix but (a) SDK-specific unload/teardown ordering changes and (b) timing — the bug is unload-triggered, and MIPS paint/refresh scheduling on a 1 GHz-class TV SoC differs from desktop; the same bug may fire with different windowing. That is a reliability/observability issue, not a presence issue.
- **Repair needed:** the "fires on Opera Mobile *of the same 2.7 core*" leg is mislabeled per your own adversarial pass (Mobile 10.x = Presto 2.4/2.5; Mobile 11.x per that verdict = 2.8.149), while Lane 1 cites Wikipedia for Mobile 11.0 = 2.7.62. These cannot both stand. Pull primary UA evidence for exactly which Mobile builds the researcher ran. Restating as "fires on cores bracketing 2.7 from below (2.4/2.5) and above (2.8.149)" supports the conclusion without the false middle leg and changes nothing.
- **Fastest falsifier:** not the RF chain — serve the unmodified trigger as `application/xhtml+xml` via the cheapest HTTP lane (finding 2), with the meta-refresh/unload intact, repeated 3–5× with varied unload timing. Unload-correlated crash = presence established. But the negative is only meaningful after the oracle is itself calibrated (finding 3): a silent run
with an uncalibrated oracle proves nothing.

## Q2 — Signalling compatibility: **REFUTED** as a working lane on this firmware

- A Brazilian ISDB-Tb set's demux/SI pipeline parses ARIB/ABNT-flavored SI, not ETSI TS 102 796 DVB AIT. For the Opera HbbTV stack to ever see an AIT, it must be (a) compiled into PKG4.027BRA, (b) registered on the section-filter path in ISDB-Tb tuner mode, (c) fed semantically equivalent
sections. Zero live evidence for any of the three; the only contrary artifact is an EUA-firmware sibling UA. Prior probability: low. The HbbTV stack, if present, is dormant on this tuner.
- **Gear mismatch makes it worse:** osmo-fl2k emits DVB-T. An ISDB-Tb-only
tuner cannot tune it, full stop. The plan as written mixes an OpenCaster ISDB-Tb fork (which natively produces Ginga signalling, not HbbTV) with DVB-AIT concepts. Every dollar of the Rank-1 hardware plan is pointed at the wrong engine.
- **Lanes that remain into Presto (broadcast or otherwise):**
  1. The built-in Internet Browser — your own adversarial pass found Sony's BRA manual (42730121M.pdf) names "Navegador da Internet" in Aplicativos for this exact family; drive it with IRCC + sendText. Zero hardware.
  2. Any cleartext HTTP endpoint the set still polls (portal/widget/SIV/update-ish hosts) → LAN DNS redirect → serve our page. Requires the step-0 capture; if a walled-garden portal page is reached, its *sub-resources* (images, SVG, long responses) are also attacker-controlled — which is where the server-triggered CVEs (finding 9)
come in.
  3. HbbTV *content* over broadband needs no AIT if a browser lane exists — the AIT is only a bootstrap; the engine is the same. If the HbbTV token shows in our own live UA, an HbbTV-flavored page over plain HTTP exercises
the identical Presto core.
  4. Broadcast reaches Ginga (NCL/Lua), not Presto — separate engine, but root-via-NCL/Lua precedent (CPqD SBSeg 2010) directly serves the maintenance goal.
- Cheap disambiguation of "compiled-in vs absent": passive capture for the
`HbbTV/1.1.1` token in *our* set's traffic + menu inspection now; post-root, `strings` on the browser binary for HbbTV/TS 102 796 artifacts.
The gate is correctly placed in the study; the lane's rank is wrong.

## Q3 — Memory-management claims: **PARTIALLY CONFIRMED**

(a) **Confirmed, one scope correction.** TASK_SIZE 0x7fff8000, TASK_UNMAPPED_BASE = TASK_SIZE/3 = **0x2aaa8000**, legacy bottom-up `arch_pick_mmap_layout` (mm/util.c, no `HAVE_ARCH_PICK_MMAP_LAYOUT` for MIPS in v2.6.35 Kconfig) — libraries and mmap'd allocations land deterministically upward from 0x2aaa8000. But "no address-space randomization on MIPS" is overbroad: stack randomization (`randomize_stack_top`) and brk randomization (`arch_randomize_brk` under `randomize_va_space`) are arch-independent and may be on in Sony's build. Irrelevant to an mmap-region spray; fix the sentence anyway.
(b) **Confirmed.** v2.6.35 `pgtable-bits.h` puts `_PAGE_NO_EXEC` behind `kernel_uses_smartmips_rixi` (BUG() otherwise; R3000 branch has no exec bit at all; `CPU_HAS_SMARTMIPS` depends on `SYS_SUPPORTS_SMARTMIPS`). No RIXI → every readable page executable → no ROP needed. Residual config question (SmartMIPS off, BSP patches) is empirical.
(c) **Confirmed.** `__NR_cacheflush` = 4000+147 = **4147** (o32), BCACHE=3
(`cachectl.h`); I/D non-coherence makes the flush stub mandatory before executing freshly-written spray. `cacheflush()` libc wrapper at a deterministic base is a valid alternate. Only add `synci` if the core is verified MIPS32r2 — it is not.
(d) **Unverifiable from sources; the study must treat it as empirical.** The kernel guarantees placement only *if* the allocation reaches mmap. glibc 2.7 logic (128 KiB static threshold, dynamic threshold capped at 512
KiB on 32-bit, never-freed spray blocks stay mmapped) is accurately described — but if the Devices SDK build routes JS string storage through Opera's own sub-allocator or a pre-grabbed arena, 1 MB spray blocks never reach malloc's mmap path, and the study's geometry collapses to "somewhere
inside Opera's arena." Determinism survives; the *shape* doesn't. Change: step 2's deliverable is the *measured* layout, and the stage-0 payload should read and beacon `/proc/self/maps` — that turns stage 3 into ground truth for stage 2's assumptions.

## Q4 — Lane ranking and omissions: **PARTIALLY CONFIRMED**

- **Ruled-out list: correct, one line.** sendContentUrl absent (live ActionList diff), 9784 accept-close (live verdict), DLNA push media-only, BML vestigial on BRA. Agreed, done.
- **Ranking: wrong.** A lane that requires (i) unproven HbbTV presence, (ii) tuner-incompatible gear, (iii) a purchase, outranks a zero-hardware lane with registration already done and a manual-verified browser app. Invert: lane 2 becomes primary; lane 1 becomes "blocked pending gate, do not spend."
- **Omissions:**
  1. **Server-triggered CVEs fit the walled-garden lanes** nobody needs URL entry for: **CVE-2012-6468** (long HTTP response heap overflow — pure server-side, fires on *any* fetch we control, including DNS-redirected portal/widget manifests) and **CVE-2012-3561** (URL-string allocation — deliverable via 302 `Location`). 2012-6470 (GIF) fires from any `<img>` sub-resource. Stockpile these as hedges against 2628's unproven Devices-SDK applicability.
  2. **Non-browser root surfaces deserve a parallel audit lane, not a footnote:** SetAVTransportURI parser (unauthenticated, live-proven), SUBSCRIBE CALLBACK handling, libmicrohttpd 0.4.6 HTTP parsing, the s2mtv endpoints (already shown to leak), and UDP 7776 (bound, undocumented — black-box probes cost nothing). Every one of these is an always-on root-era daemon with zero delivery risk and no HbbTV dependency; for the stated goal — *a maintenance path* — any one beats the browser chain on expected value.
  3. **Unasked question that gates lanes 2–4:** what engine hosts "Internet Widgets" on this set? If the 2011 Sony widget layer is Yahoo/Konfabulator-derived, DNS-faked widgets never touch Presto regardless of capture results. Settle in the step-0 session.
  4. **Ginga broadcast is misfiled as a caveat.** On ISDB-Tb it is the *only* standards-native broadcast attack surface, it has a public root precedent, and it reuses the same RF gear correctly purchased for gr-isdbt. If the owner ever buys RF gear, it is for Ginga — promote this from footnote to its own lane under the maintenance-goal framing.

## Q5 — Experiment ladder and readouts: **PARTIALLY CONFIRMED**

Structure is right; the readouts are uncalibrated and one safety gate is missing.

- **Oracle specificity: unknown and unproven.** `HOST_WDT` counts *watchdog trips* — system hangs. A clean segfault of a supervised process likely gets respawned *without* tripping the watchdog, i.e., a true positive can produce a false negative. Conversely, the 8-blink "Software Error" state is the process-crash-correlated signal, and its exact sensitivity on this firmware is likewise unmeasured. Baseline 21 over 11,498 boots means the counter is *historical*, not per-event — deltas are
only valid inside quiescent test windows.
- **False positives:** OOM kill of the browser by the spray (raw research already flags), unrelated middleware crash, tuning/CEC-induced hang inside
the window. **False negatives:** silent kill+respawn; MIME mis-serve (`text/html` instead of `application/xhtml+xml` silently changes the parser path — this is the classic way this PoC produces "bug absent" results on vulnerable builds); unload-timing window missed on MIPS scheduling.
- **Cheaper/softer oracle, missing from the ladder:** JS **phase beacons**
from the test page itself — `img`/`XHR` hits to a LAN collector at page-load, after each spray size, and immediately before triggering unload. The last received beacon localizes the crash to spray-phase (OOM) vs unload-phase (the bug), distinguishes hang from death (hang → sustained
page alive then WDT), and needs no service-mode visit. Combined readout: counter trio (HOST_WDT, boot count, LED state) before/after each run — reboot vs respawn vs hang separate cleanly.
- **The missing gate (two):**
  1. **Positive control.** Before the CVE page means anything, run a *guaranteed* browser crash (runaway recursion / forced OOM from JS) and verify which observables actually move on this firmware. If HOST_WDT and the LED both stay silent on a certain crash, a silent CVE run is uninterpretable.
  2. **Damage-bounding.** No payload may ever write flash/NVRAM/mtd (beacon = network + screen only); WAN uplink quarantined during test windows (an OTA or portal refresh mid-experiment would invalidate the baseline); power-cycle/self-check/factory-reset recovery path rehearsed *before* the first induced crash; spray sizes capped under measured headroom to avoid wedging the full middleware; coax work stays attenuated into the antenna port only (already policy — keep it).

---

# FINDINGS (ordered)

1. **CRITICAL — Rank-1 lane is standards-mismatched and the gear can't even be tuned.** DVB AIT/TS 102 796 is not carried by ISDB-Tb; osmo-fl2k emits DVB-T, which this tuner cannot receive. *Change:* strike lane 1 as a
purchase justification; reclassify HbbTV as "gated hypothesis"; any RF gear purchased later targets ISDB-Tb/Ginga via gr-isdbt.
2. **CRITICAL — Ranking inversion.** IRCC + sendText into "Navegador da Internet" (manual-named for this family, registration done, zero hardware)
is simultaneously the delivery answer *and* the Q1 falsifier. *Change:* make it lane 1; the first purchase decision waits on its outcome.
3. **HIGH — Oracle is uncalibrated; no positive control.** Add a guaranteed-crash control page, the counter trio per run, and JS phase beacons before interpreting any CVE run. *Change:* insert as new step 1; renumber.
4. **HIGH — Safety gates missing.** Add: no-flash-writes payload constraint, WAN quarantine during windows, pre-crash recovery rehearsal, run-window quiescence discipline, spray headroom cap. *Change:* make these
explicit ladder preconditions, not caveats.
5. **HIGH — Mobile-line lineage leg is factually mislabeled and internally
contradictory** (Lane 1: Mobile 11.0 = 2.7.62 per Wikipedia; adversarial pass: Mobile 10.x = 2.4/2.5, 11.x = 2.8.149). *Change:* pull primary UA strings for the tested Mobile builds; restate as "cores bracketing 2.7," or cite a tested 2.7.x Mobile build if one is found.
6. **MEDIUM — Trigger delivery needs MIME/timing controls.** Serve `application/xhtml+xml`; implement unload via multiple mechanisms (meta refresh, location change, iframe teardown); ≥3 trials. Document that a single silent run is a non-result.
7. **MEDIUM — "No ASLR on MIPS" is overbroad.** Mmap/lib region: deterministic (kernel-verified). Stack/brk: possibly randomized under `randomize_va_space`; process rlimits and `vm.overcommit_*` on Sony's init
scripts unknown. *Change:* fix the claim; add these to the step-2 unknowns
list.
8. **MEDIUM — Allocation geometry (Opera allocator) unknowable ex ante.** *Change:* treat step 2's deliverable as measured layout; stage-0 payload beacons `/proc/self/maps` to close the loop.
9. **MEDIUM — Stockpile lane-fit alternates.** CVE-2012-6468 and 2012-3561
fire from server responses and fit DNS/portal lanes without any URL-entry UI; 2012-6470 fits `<img>`; 6465/1638 (SVG) and 1637 (DOM) fit any page. 2628 stays primary (only bug with demonstrated cross-core firing).
10. **MEDIUM — Promote the root-daemon audit and the Ginga lane.** SetAVTransportURI parser, SUBSCRIBE CALLBACK, libmicrohttpd 0.4.6, s2mtv, UDP 7776 probes: parallel lane, zero delivery risk, directly serves the maintenance goal. Ginga/ISDB-Tb becomes the designated broadcast lane.
11. **LOW — AIT descriptor labeling error** (if HbbTV is ever used): `transport_protocol_descriptor` has descriptor_tag **0x02**; **0x0003** is
the protocol_id value inside it. Fix before any OpenCaster payload work.
12. **LOW — Repo hygiene.** `[C:live]` tags on UA strings are mislabeled (no live capture exists); AppliCast rank should read "hypothesis"; step 0 should include a keyed AppliCast press during capture.

# WHAT I WOULD DO NEXT, IN ORDER

1. **Step 0, once, with WAN quarantine:** boot + IRCC keypresses (InternetWidgets / InternetVideo / AppliCast / Ddata) under capture. One session answers: our set's live UA (HbbTV token yes/no), which portal hosts are still cleartext HTTP, whether AppliCast emits anything, and which engine the widgets run in.
2. **IRCC Home → Aplicativos: confirm "Navegador da Internet"; sendText a LAN URL.** If it loads, delivery is solved today with zero purchases.
3. **Build the positive-control crash page + phased JS beacons; run it; record which of HOST_WDT / boot count / 8-blink actually move.** Only now is any CVE run interpretable.
4. **Falsifier run:** unmodified trigger, `application/xhtml+xml`, 3–5 unload-timing variants, counter deltas per run, quiescent windows, WAN down.
5. **If positive:** benign MIPS sled ladder with per-size on-screen/beacon
markers, capped under measured headroom, no flash writes; landing address from measurement, not from 0x2aaa8000+n arithmetic.
6. **In parallel, no hardware:** audit the root daemons (SetAVTransportURI
parser, libmicrohttpd 0.4.6, s2mtv, UDP 7776 probes). Buy RF gear only if the Ginga lane is chosen deliberately — never for the HbbTV lane as currently specified.
