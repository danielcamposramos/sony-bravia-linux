# Partner panel review: Presto CVE-2011-2628 study — round 2 (on top of Kimi K3)

- **Panel:** qwen3.5:397b-cloud, kimi-k2.7-code:cloud, deepseek-v4-pro:cloud, nemotron-3-ultra:cloud — all via ollama API, 2026-09-13, run in parallel on an identical 98 KB prompt: the five-question charter + the study + the raw research JSON + the full Kimi K3 review (docs/research/partner-review-presto-kimi.md), with the mandate to AGREE/DISAGREE/EXTEND on K3's findings and add what both prior reviews missed.
- **Why this panel exists:** Claude Opus (2x) and GPT Astra via codex (1x) were each refused by their providers' cyber classifiers on this owner-hardware right-to-repair study; the open-weight fleet reviewed it without incident.
- Verdict bodies below are verbatim.

---

## Panel synthesis

Consensus of the round-2 panel (detailed votes in each section):

**Confirmed by all reviewers:**
- K3 CRITICAL 1 stands — **confirmed by all four reviewers** — the HbbTV broadcast lane is dead *as a Presto delivery path on this firmware*: ISDB-Tb carries ARIB STD-B10/ABNT Ginga descriptors, not ETSI TS 102 796 DVB AIT; no live evidence any HbbTV stack is wired to PKG4.027BRA's tuner path. **Gear-argument correction (DeepSeek + kimi-k2.7-code, independent; nemotron repeats K3's original framing — 2-2, resolved technically):** osmo-fl2k is a generic FL2K-based SDR transmitter and with gr-isdbt *can* synthesize ISDB-Tb — the blocker is the firmware's SI parser, not the RF hardware or tuner. Reclassify the lane "dormant/unverified", not "impossible at RF". Operational conclusion identical either way: no purchase for this lane.
- K3 CRITICAL 2 stands — **confirmed by all four** (nemotron: "the study's ranking is a planning error"; it cites the manual page, 42730121M.pdf p.21) — but is **gated functionally** (Qwen + kimi-k2.7-code): manual presence of "Navegador da Internet" does not prove free URL entry — 2011 BRA firmware may expose bookmarks/widget portals only, and sendText only types into a focused text field. The zero-hardware sendText test settles it in minutes and must run before the lane is relied on.
- Oracle calibration is mandatory before any CVE run: HOST_WDT counts system hangs, not clean process deaths (respawn may be silent); a guaranteed-crash positive control + JS phase beacons + quiescent-window counter reads are required (Qwen adds ARP ping loss as a real-time signal).
- CVE-2012-6468 (long HTTP response) and 2012-3561 (URL-string allocation) are the hedge triggers: server-side, fire from any fetchable resource via DNS-redirected portal/widget sub-resources, need no URL-entry UI; 6468 in particular may be *more reliable* than 2628 on MIPS (no unload-timing dependence).
- The non-browser root-daemon audit (SetAVTransportURI parser, SUBSCRIBE CALLBACK, libmicrohttpd 0.4.6, s2mtv, UDP 7776) is elevated to a co-primary lane: unauthenticated, always-on, zero delivery risk, directly serves the maintenance goal.
- Safety gates adopted: no payload writes to /dev/mtd*/NVRAM; WAN quarantine during test windows (kimi-k2.7-code adds HDMI-CEC isolation); recovery rehearsal before the first induced crash; spray cap under measured headroom.
- Memory claims: mmap base 0x2aaa8000 deterministic (kernel-verified), but "no ASLR on MIPS" is overbroad (stack/brk randomization arch-independent) and — the panel's strongest technical upgrade — **Presto's own heap arenas are the dominant unknown**: JS String spray objects may be split/relocated/UTF-16-stored in Opera's allocator, so no landing address may be derived from glibc-threshold theory; the stage-0 canary must beacon /proc/self/maps (kimi-k2.7-code: one canary resolves NX, ASLR, privilege, and allocator at once via /proc/self/status, /proc/cpuinfo, /proc/self/maps, /proc/meminfo).
- Mobile-lineage leg mislabel confirmed: restate as "cores bracketing 2.7" and pull primary UA strings before publication.

**Standout per-model contributions:** DeepSeek — branch delay slots (every sled word harmless incl. delay slots), don't assume a valid $sp; Qwen — ARP ping loss as real-time oracle signal, D-cache writeback ordering for JS-stored strings; kimi-k2.7-code — beacon via socket+connect+write (avoid six-arg sendto), direct syscall 4147 (don't trust an unverified libc wrapper), sink-hole DRM license endpoints on any DNS-faked portal so license acquisition is never triggered even accidentally, 9784/7776 need structured magic-request probing rather than declaring them dead; nemotron-3-ultra — the deepest engineering pass of the round: cacheflush *race* (I-cache may speculatively reload after flush — execute a sync barrier and jump to a trampoline *outside* the flushed region), Presto HeapAllocator reserves a 64-128 MB startup arena and StringImpl UTF-16 storage may rope-fragment large strings (spray blocks may be non-contiguous in VM), UPnP GENA SUBSCRIBE/CALLBACK as an unanalyzed SSRF/parser surface, libmicrohttpd 0.4.6 concrete probe (Content-Length/Transfer-Encoding ambiguity, path traversal on /s2mtv/), DirectFB 1.4 surface allocation overflows as a Presto-adjacent path, the **watchdog identity question** (hardware PMIC vs kernel softlockup — decides whether a browser crash can ever move HOST_WDT; read /proc/sys/kernel/watchdog post-root), CVE-2011-2629..2633 from the same 11.11 fix batch as candidate siblings of 2628, same-origin/CORS constraint on any DNS-rebinned payload (sub-resources to LAN IPs blocked unless CORS is served), the undocumented recovery procedure (exact FACTORY INIT sequence, USB recovery mode, JTAG as last resort) must be written *before* the first induced crash, and the Ginga Lua version check (`strings` post-root; if Lua 5.1, the CPqD sandbox escape is a known reliable root path that decides the RF purchase on its own).

**Panel-unanimous next-6 (all four reviewers, minor ordering differences):** (1) WAN-quarantined step-0 capture + IRCC menu probe; (2) reach the cheapest HTTP lane (browser sendText if URL entry exists, else DNS-redirected portal) and run a positive-control crash page with phase beacons; (3) CVE-2011-2628 falsifier run, `application/xhtml+xml`, ≥3 unload mechanisms, ≥3 trials each, quiescent windows; (4) parallel root-daemon audit (SetAVTransportURI, SUBSCRIBE CALLBACK, libmicrohttpd/s2mtv, UDP 7776) — starts now, zero hardware; (5) if positive: measured MIPS spray ladder with /proc/self/maps beacon, landing address from measurement only, no flash writes; (6) RF gear only for a deliberately chosen Ginga/ISDB-Tb lane, never for HbbTV.

---

## 1. qwen3.5:397b-cloud — verbatim

- **Overall Position:** Kimi K3 is technically correct on the RF/Standards mismatch (Critical 1) and Oracle calibration (High 3), but over-optimistic on the IRCC "Navegador" URL entry capability (Critical 2) and under-specifies the MIPS cache coherence requirements. The ranking inversion is valid *only if* free URL entry exists, which is unproven for BRA firmware. The study's MIPS retargeting is sound but needs stricter shellcode validation. I align with Kimi on shifting focus away from HbbTV/RF until gates pass, but insist on parallel non-browser audits (UPnP) as higher-value maintenance paths.

- **Item A Findings (Response to Kimi K3)**
    1.  **Critical 1 (Standards Mismatch): AGREE.** ISDB-Tb (ABNT NBR 15606) does not natively carry DVB-AIT (ETSI TS 102 796). osmo-fl2k emits DVB-T (COFDM), which an ISDB-Tb tuner (BST-OFDM) cannot demodulate. The Rank-1 hardware plan is physically incompatible with the tuner.
    2.  **Critical 2 (Ranking Inversion): EXTEND.** IRCC is Lane 1 *only if* the "Navegador" app accepts arbitrary URLs. 2011 BRA firmware often strips the URL bar, leaving only widget portals. Manual presence ≠ functional URL entry. Verify `sendText` navigation capability specifically before ranking above RF.
    3.  **High 3 (Oracle Calibration): AGREE.** `HOST_WDT` trips on system hang, not process crash. Browser respawn may not increment counter. JS beacons (XHR/IMG) + ARP ping loss are required to distinguish process death from system hang. Positive control (forced JS crash) is mandatory baseline.
    4.  **Q3 (Memory/Cache): EXTEND.** `cacheflush` syscall 4147 is necessary but not sufficient if the shellcode is written via JS string manipulation. JS engines may store strings in non-coherent memory regions. Ensure shellcode is written via `write()` syscall or `mmap` + `memcpy` to guarantee D-cache coherence before I-cache flush.
    5.  **Medium 10 (Root Daemons): AGREE.** UPnP `SetAVTransportURI` parser is a higher-value target than the browser for maintenance goals. It runs in root context, no sandbox, unauthenticated. Prioritize this audit parallel to browser work.

- **Item B Additions (Missed Items)**
    1.  **CVE-2012-6468 (HTTP Heap Overflow):** Fits DNS-redirected portal lanes without URL entry. Server sends long HTTP response → heap overflow in Presto. Better hedge than 2628 if URL bar is missing.
    2.  **MIPS Endianness/Alignment:** mipsel is little-endian (matches PoC), but MIPS requires word-aligned access for many ops. Ensure spray landing addresses are 4-byte aligned. `0x0c0c0c0c` is `jal` (opcode 3), not NOP. Use `0x00000000` (NOP) or `0x34214141` (ORI).
    3.  **UPnP Stack Smashing:** `SetAVTransportURI` takes a long string URI. Unauthenticated. Root context. No browser sandbox. Fuzz with long strings + monitor for reboot.
    4.  **Ginga Separation:** Ginga runs NCL/Lua, not Presto. If Presto fails, Ginga is a separate root path (CPqD precedent), not a Presto fallback. Do not conflate engines.
    5.  **Watchdog Timing:** `HOST_WDT` is historical cumulative. Need delta measurement within quiescent windows. ARP ping loss is a better real-time crash signal.
    6.  **Safety Gate:** WAN quarantine is mandatory during tests. OTA update mid-experiment could patch the bug or change memory layout, invalidating results.

- **Item C Next-6-Actions**
    1.  **Step 0 Capture (WAN Quarantine):** Boot EX725. IRCC keypresses (Widgets/Video/AppliCast/Navegador). tcpdump for UA + HTTP hosts. Verify HbbTV token presence/absence.
    2.  **URL Entry Test:** IRCC into "Navegador". `sendText` `http://lan-ip/test.html`. Verify render. If fails, IRCC lane is dead for CVE-2011-2628.
    3.  **Positive Control:** Serve forced JS crash (infinite recursion). Observe `HOST_WDT` delta, LED state, ARP ping loss. Calibrate oracle sensitivity.
    4.  **CVE-2012-6468 Prep:** If URL entry fails, prepare long HTTP response for DNS-redirected portal resource. Test via captured portal hosts.
    5.  **UPnP Audit:** Fuzz `SetAVTransportURI` with long strings. Monitor for crash/reboot. Higher value than browser for maintenance goals.
    6.  **MIPS Shellcode:** Write MIPSel NOP sled + UDP beacon. Test `cacheflush` syscall locally on similar MIPS Linux box. Verify D-cache writeback before I-cache flush.
---

## 2. kimi-k2.7-code:cloud — verbatim

**Overall position.** I largely back the senior review: the HbbTV broadcast lane is over-ranked, the oracle must be calibrated before any CVE run, and zero-cost IRCC/browser probing should come first. Where I differ is precision: the senior reviewer overstates the RF impossibility — osmo-fl2k + gr-isdbt *can* produce ISDB-Tb; the real problem is that the BRA firmware almost certainly has no DVB-SI/HbbTV parser. I also think both the study and the senior review underweight Presto’s internal heap model and treat glibc mmap geometry as more predictive than it is. I support the safety-gate expansion, the non-browser audit, and the 2012 server-side CVE hedges.

---

## A. Findings vs the senior reviewer

**A1. CRITICAL — HbbTV/ISDB-Tb lane dead / gear mismatch.**  
**AGREE** on the operational conclusion; **DISAGREE** on the physical-layer reasoning.  
The osmo-fl2k + gr-isdbt chain *can* synthesize ISDB-Tb inside the tuner band; the tuner is not the blocker. The blocker is firmware: PKG4.027BRA parses ARIB STD-B10/ABNT Ginga descriptors, not ETSI TS 102 796 DVB AIT, and Brazil had no 2011 HbbTV mandate. No live UA/menu from this set shows HbbTV. Reclassify lane 1 as dormant/unverified, not “impossible at RF,” and buy no hardware for it.

**A2. CRITICAL — Ranking inversion to IRCC + `sendText` + “Navegador da Internet.”**  
**AGREE** on procedural priority; **DISAGREE** that this is already “the answer.”  
The family manual names an Internet Browser, but warns categories depend on region/country, and the BRA firmware may omit free URL entry. `sendText` only types into a focused text field; if the UI is bookmarks-only, the lane is dead. Test it first because it is free, but keep DNS-redirect and broadcast-Ginga fallbacks ready.

**A3. HIGH — Oracle uncalibrated.**  
**AGREE and EXTEND.**  
`HOST_WDT` counts system hangs, not clean browser process deaths; Opera may be respawned by a supervisor without tripping the watchdog. Add a guaranteed-crash JS positive control (runaway recursion/OOM), JS phase beacons (`Image`/XHR pings to a LAN collector at load, post-spray, pre-unload, and post-unload), and read the counter trio (`HOST_WDT`, boot count, 8-blink LED) only in quiescent windows. The last received beacon localizes the crash phase.

**A4. HIGH — Safety gates missing.**  
**AGREE and EXTEND.**  
Add WAN and HDMI-CEC isolation during test windows to block OTA/menu state changes; cap spray size from `/proc/meminfo MemFree`; rehearse physical recovery and firmware reflash before the first induced crash; forbid payload writes to `/dev/mtd*`, NVRAM, or persistent config; avoid CERS commands that alter pairing or settings.

**A5. HIGH — Mobile-line lineage mislabel.**  
**AGREE.**  
Restate as: the bug fires on cores bracketing 2.7 (Opera Mobile 10.x on ~2.4/2.5 and 11.x on ~2.8.x) and in desktop 11.00/11.01 (2.7.62). The TV’s 2.7.61 SDK build sits one patch below the RCE-verified desktop 2.7.62, and the frameset-unload path is core layout code, so the inference still holds.

**A6. MEDIUM — MIME/timing controls.**  
**AGREE.**  
Serve the original PoC exactly as `application/xhtml+xml` with the XHTML namespace and the meta-refresh/iframe unload path. A `text/html` fallback may silently route through a different parser. Test multiple unload vectors: meta refresh, JS `location` change, and parent iframe removal.

**A7. MEDIUM — “No ASLR on MIPS” overbroad.**  
**AGREE with correction.**  
The mmap base is deterministic at `0x2aaa8000`; any stack/brk randomization under `randomize_va_space` is irrelevant for the mmap-region spray. Library load order within that region can shift offsets by firmware build, but not by run.

**A8. MEDIUM — Allocation geometry / Opera heap.**  
**AGREE and EXTEND.**  
The glibc mmap analysis is a weak proxy. Presto 2.7 uses its own memory arenas for DOM/JS strings; the `%u` spray blocks may be split, relocated, or stored as UTF-16 units. Do not derive a landing address from `0x2aaa8000 + n`. The spray ladder must measure actual allocation addresses via a canary that reads `/proc/self/maps` and beacons them back.

**A9. MEDIUM — Stockpile server-side CVEs as hedges.**  
**AGREE.**  
CVE-2012-6468 (long HTTP response) and CVE-2012-3561 (URL allocation) are especially valuable because they fire from any fetchable resource and need no URL-entry UI. CVE-2012-6470 (GIF), 2012-6465/2013-1638 (SVG), and 2013-1637 (DOM events) fit sub-resources or inline content. They may be more reliable than 2628 if the Devices SDK build diverges.

**A10. MEDIUM — Root-daemon audit and Ginga lane.**  
**AGREE and EXTEND.**  
UPnP `SetAVTransportURI`, `SUBSCRIBE` callback handling, libmicrohttpd 0.4.6, `s2mtv` endpoints, and UDP 7776 are unauthenticated, always-on, and directly serve the maintenance goal. Ginga/ISDB-Tb is the correct broadcast lane for this market; buy RF gear only if that lane is deliberately chosen.

**A11. LOW — AIT descriptor tag.**  
**AGREE.**  
`transport_protocol_descriptor` tag is 0x02; protocol_id 0x0003 selects HTTP. Fix before any OpenCaster payload work.

**A12. LOW — Repo hygiene.**  
**AGREE.**  
`[C:live]` tags on the EUA UA are mislabeled; AppliCast should be marked “hypothesis”; step 0 must include a keyed AppliCast press during capture.

---

## B. What both the study and the senior reviewer missed

**B1. Presto’s internal heap is the dominant unknown.**  
The `%u` spray creates JS `String` objects, and Presto 2.7 manages them through its own allocator, not necessarily as contiguous glibc mmap regions. The ladder must correlate spray size with actual process VMAs and crash addresses; glibc `DEFAULT_MMAP_THRESHOLD` is not predictive enough.

**B2. MIPS shellcode details.**  
Avoid `sendto` (six o32 arguments). Use `socket` + `connect` + `write` for the LAN beacon. Use direct syscall 4147 (`cacheflush`, `a0=start`, `a1=len`, `a2=BCACHE=3`) before executing sprayed code; do not rely on a libc wrapper whose address is unverified. Check `/proc/cpuinfo` for MIPS32r2 before considering `synci`. Build a word-aligned NOP sled; 0x0c0c0c0c is a `jal`, not a sled.

**B3. Stage-0 payload should resolve all assumptions at once.**  
Beacon back uid/euid from `/proc/self/status`, `/proc/cpuinfo` flags, the first few VMAs from `/proc/self/maps`, and `/proc/meminfo` headroom. One canary answers NX, ASLR, privilege, and allocator questions empirically.

**B4. Widget runtime identity is still unconfirmed.**  
Capture the HTTP User-Agent from InternetWidgets/AppliCast. If the runtime is Yahoo/Konfabulator or another non-Presto engine, the entire widget/DNS lane is irrelevant for CVE-2011-2628 regardless of URL entry.

**B5. DNS-redirect portal lanes can accidentally touch DRM.**  
A fake Sony Internet Video portal may trigger WMDRM/Marlin license acquisition or OTA checks. Log all outbound DNS/HTTP and sink-hole license/key endpoints; never handle DRM keys.

**B6. Port 9784 and UDP 7776 need structured re-probing.**  
9784 may expect a magic request before responding, not simply accept-close. UDP 7776 may be a debug/discovery protocol. Fuzz both with Sony/CERS-style payloads and watch the same crash oracle.

**B7. Non-browser surfaces are higher expected value than framed.**  
`SetAVTransportURI` receives attacker-controlled URI strings unauthenticated — long URIs, exotic schemes, and query strings are a classic parser fuzz target. Additional `s2mtv` endpoints (category/content list) likely accept query parameters. libmicrohttpd 0.4.6 is a 2008-era HTTP parser with a long vulnerability history in header and URI handling.

---

## C. Next-6-actions (ordered)

1. **Step-0, WAN-quarantined capture + IRCC menu probe.**  
   Press InternetWidgets / InternetVideo / AppliCast / Navegador while `tcpdump` runs; record the set’s own UA, cleartext HTTP hosts, and whether the browser app is reachable. Zero hardware, one session.

2. **Reach the cheapest HTTP lane and run a positive-control crash page.**  
   If Navegador exists, drive it to a LAN URL via IRCC + `sendText`; otherwise test DNS-redirected portal/widget endpoints. Use a guaranteed JS crash (runaway recursion / forced OOM) with phase beacons to learn which oracle signals actually move.

3. **CVE-2011-2628 falsifier run.**  
   Serve the unmodified trigger as `application/xhtml+xml` with the correct XHTML namespace, using 3–5 unload mechanisms. Record phase beacons and the counter trio only in quiescent windows.

4. **Instrumented MIPS spray ladder.**  
   Per-size benign NOP sled, on-screen/beacon markers, `/proc/self/maps`, `/proc/meminfo`, `/proc/cpuinfo`, and `/proc/self/status` readout. Cap spray size to measured headroom; never derive a landing address from theory.

5. **Code-exec canary.**  
   Cacheflush stub + direct-syscall connected-socket beacon to a LAN listener. The received packet is the only unambiguous proof of control transfer.

6. **Parallel non-browser audit.**  
   Fuzz `SetAVTransportURI` length/scheme, `SUBSCRIBE` callback URL, libmicrohttpd endpoints, `s2mtv` command endpoints, and UDP 7776 with crafted probes. Defer any RF purchase to a deliberately chosen Ginga lane, not the HbbTV lane.
---

## 3. deepseek-v4-pro:cloud — verbatim

## Overall position

I concur with the senior reviewer’s two CRITICALs, the oracle-calibration demand, and the safety-gate additions. The study’s version-lineage inference for CVE-2011-2628 remains sound; its principal defects are the lane ranking and the absence of a calibrated crash oracle and positive control. I disagree with one technical detail in the first CRITICAL (the RF-gear claim) but not with its conclusion. I add MIPS-shellcode engineering specifics, allocation-geometry caveats, and a stronger case for parallel non-browser root-daemon audit. The built-in “Navegador da Internet” + CERS sendText lane is the correct primary path, and the HbbTV broadcast lane is effectively dead on this Brazilian ISDB-Tb firmware.

---

## Item A — Senior reviewer’s major findings

1. **CRITICAL 1 — HbbTV lane standards mismatch and gear can’t be tuned**  
   **AGREE with conclusion; EXTEND on the gear claim.**  
   The lane is dead as a Presto delivery path: ISDB-Tb does not carry DVB AIT, and PKG4.027BRA has no evidence of an HbbTV stack wired to the tuner. The senior reviewer is correct that the study’s Rank 1 is standards-mismatched and must not justify any purchase.  
   *However*, the claim “osmo-fl2k emits DVB-T” is technically imprecise. osmo-fl2k is a generic SDR transmitter; with `gr-isdbt` it can produce ISDB-Tb. The real incompatibility is not the hardware but the signalling stack — the study’s plan mixes OpenCaster (DVB) with ISDB-Tb modulation, and even if the RF were correct, the BRA firmware would not parse HbbTV AIT. So the lane is blocked, but the gear argument should be corrected in the repo.

2. **CRITICAL 2 — Ranking inversion toward built-in browser + CERS sendText**  
   **AGREE fully.**  
   The senior reviewer correctly found the in-repo manual (42730121M.pdf) naming “Navegador da Internet” for this exact 2011 family. Registration is done, IRCC is unauthenticated, and the key codes are confirmed. This lane is zero-hardware, immediate, and also serves as the Q1 falsifier. The study’s caveat “no evidence it does” was stale. Make it lane 1.

3. **HIGH — Oracle is uncalibrated; no positive control**  
   **AGREE, with a specific addition.**  
   HOST_WDT counts watchdog trips, which may not increment on a clean segfault. The 8-blink Software Error LED is the process-crash signal, but its sensitivity is unmeasured. The proposed JS phase beacons are essential: they distinguish OOM from unload-phase corruption and give a soft oracle without service-mode visits.  
   *Add:* also record the process exit status if accessible via kernel log or syslog (not yet root, but the beacon can infer death by absence of subsequent heartbeats).

4. **HIGH — Safety gates missing**  
   **AGREE.**  
   The four additions (no flash writes, WAN quarantine, recovery rehearsal, headroom cap) are necessary preconditions, not caveats. I would also require a written rollback procedure for a wedged TV (hard power-cycle + factory reset path) before any induced crash.

5. **HIGH — Mobile-line lineage leg mislabeled**  
   **AGREE.**  
   The study and raw research conflict on which Presto core the researcher’s Opera Mobile builds used. The corrected statement “fires on cores bracketing 2.7” preserves the inference without the false middle leg. Pull primary UA strings for the exact Mobile builds before final publication.

6. **MEDIUM — Trigger delivery needs MIME/timing controls**  
   **AGREE.**  
   `application/xhtml+xml` is mandatory; `text/html` changes the parser path and yields false negatives. Use multiple unload mechanisms (meta refresh, location change, iframe teardown) and ≥3 trials.

7. **MEDIUM — “No ASLR on MIPS” overbroad**  
   **AGREE.**  
   The mmap/lib region is deterministic (kernel-verified), but stack and brk randomization may be enabled under `randomize_va_space`. This does not affect the mmap spray, but the claim must be corrected.

8. **MEDIUM — Allocation geometry unknowable ex ante**  
   **AGREE, strongly.**  
   Opera Devices SDK may use a custom allocator, so 1 MB spray blocks may never reach glibc’s mmap path. The step-2 deliverable must be the *measured* layout, and the stage-0 payload must beacon `/proc/self/maps` to close the loop.

9. **MEDIUM — Stockpile lane-fit alternates**  
   **AGREE.**  
   CVE-2012-6468 (long HTTP response) and CVE-2012-3561 (URL-string allocation) are server-triggered and fit DNS/portal lanes without any URL-entry UI. Keep 2628 as primary but prepare these as fallback triggers.

10. **MEDIUM — Promote root-daemon audit and Ginga lane**  
    **AGREE.**  
    SetAVTransportURI parser, SUBSCRIBE CALLBACK, libmicrohttpd 0.4.6, s2mtv, and UDP 7776 are always-on surfaces with zero delivery risk. For the maintenance goal, any one of these may beat the browser chain. Ginga/ISDB-Tb is the correct broadcast lane if RF gear is ever purchased.

11. **LOW — AIT descriptor labeling error**  
    **AGREE.**  
    `transport_protocol_descriptor` has descriptor_tag 0x02; protocol_id 0x0003 is inside. Fix before any OpenCaster work.

12. **LOW — Repo hygiene**  
    **AGREE.**  
    `[C:live]` tags are mislabeled; AppliCast should read “hypothesis”; step 0 must include a keyed AppliCast press during capture.

---

## Item B — Additions (things both study and senior reviewer missed or underweighted)

1. **MIPS shellcode specifics beyond cacheflush**  
   The study correctly identifies syscall 4147, but additional constraints matter:  
   - The cacheflush stub must be position-independent and must set `a0`–`a2` correctly (start, len, BCACHE=3).  
   - Branch delay slots: every jump executes the following instruction; the sled must be word-aligned and every word individually harmless, including the delay slot after the final jump into payload.  
   - Null bytes in the decoded shellcode are acceptable because `unescape("%u...")` produces binary memory; however, the *string* itself must not contain raw NULs before decoding. The study’s suggestion of `0x00000000` as NOP is fine, but verify Opera’s unescape implementation preserves all bytes.  
   - The payload should not assume a valid stack pointer; set `$sp` to a known sprayed region before calling any function or syscall wrapper.

2. **Allocation geometry: fragmentation risk**  
   Even if large allocations reach mmap, the corrupted pointer may land in a fragmented heap if Opera’s sub-allocator interleaves smaller blocks. The spray ladder must include multiple small-to-medium sprays and a final large contiguous region; the stage-0 `/proc/self/maps` beacon will reveal the actual layout.

3. **Alternative era bugs: CVE-2012-6468 as a better first trigger**  
   CVE-2012-6468 (heap overflow via long HTTP response) can be triggered by any server-controlled response — a single oversized header or body. It requires no precise heap grooming and may be more reliable on a MIPS build than 2628’s unload-timing dependency. Consider running it as a parallel falsifier or fallback if 2628 fails to crash.

4. **Non-browser surfaces: SUBSCRIBE CALLBACK and libmicrohttpd**  
   - UPnP event subscription (`SUBSCRIBE` with a callback URL) may allow header injection or SSRF; even if not exploitable for code execution, it may leak internal state or cause a crash.  
   - libmicrohttpd 0.4.6 is old and has known parsing bugs; fuzzing its HTTP handling via the TV’s exposed services (s2mtv, 9784 if it ever reads) is cheap.  
   - UDP 7776 is bound but silent; black-box probes with malformed payloads may elicit a response or crash, providing a root-daemon crash oracle independent of the browser.

5. **Ginga lane as direct root path**  
   The CPqD SBSeg 2010 findings show NCL/Lua runs as root on Brazilian ISDB-Tb middleware. If the owner ever buys RF gear, targeting Ginga with a known NCL/Lua injection may yield root faster than a Presto exploit. This should be a parallel lane, not a footnote, especially since the same ISDB-Tb modulator can serve both Ginga and (theoretically) HbbTV if it ever existed.

6. **HbbTV token check via passive capture**  
   The senior reviewer’s step 0 already captures the live UA; if the token `HbbTV/1.1.1` appears, an HbbTV-flavored page over plain HTTP (via browser lane) exercises the same Presto core even without AIT. That is a cheap way to test HbbTV-specific code paths if the engine includes them.

---

## Item C — My ordered next-6 actions

1. **Step 0 with WAN quarantine**  
   Boot the EX725, press IRCC keys (InternetWidgets, InternetVideo, AppliCast, Ddata) while capturing all outbound traffic. Record live UA (HbbTV token yes/no), portal hosts, and whether AppliCast emits anything. No new hardware.

2. **Confirm “Navegador da Internet” via IRCC**  
   Navigate Home → Aplicativos using IRCC; visually confirm the browser app exists. Use `sendText` to enter a LAN URL serving a simple test page. If it loads, delivery is solved today.

3. **Calibrate the crash oracle with a positive control**  
   Serve a page that forces a guaranteed browser crash (runaway recursion or forced OOM). Record HOST_WDT, boot count, and LED state before/after. Also run a JS phase-beacon page to verify beacon collection and distinguish hang from death.

4. **Falsifier run for CVE-2011-2628 via browser lane**  
   Serve the unmodified trigger as `application/xhtml+xml` with three unload-timing variants. Use phase beacons; record counter deltas per run. A positive crash localizes to unload phase; a silent run with calibrated oracle is meaningful.

5. **If positive: benign MIPS sled ladder**  
   Spray with pure NOP sled in increasing sizes (capped under measured headroom), with on-screen markers and `/proc/self/maps` beacon at each step. Determine actual allocation geometry and memory budget. No payload, no flash writes.

6. **In parallel, start non-browser root-daemon audit**  
   Probe SetAVTransportURI parser with long strings, fuzz libmicrohttpd via s2mtv, send malformed packets to UDP 7776. Document any crash or unexpected response. Buy RF gear only if Ginga lane is chosen deliberately — never for HbbTV.
---

## 4. nemotron-3-ultra:cloud — verbatim

## Overall Position

The senior reviewer is technically precise on the two CRITICAL findings (DVB-AIT/ISDB-Tb mismatch, ranking inversion) and the oracle/safety gaps. I agree with the substance of all 12 findings but extend several where the engineering reality is worse than stated — particularly on the MIPS retarget (Opera allocator vs. glibc mmap, cacheflush race windows, branch-delay-slot constraints) and the non-browser attack surface (UPnP GENA SUBSCRIBE, libmicrohttpd 0.4.6 request parsing, UDP 7776 as a fuzz target). The study's "right-to-repair" framing is sound, but the experiment ladder treats the TV as a generic Linux/MIPS box; it is not — it's a Sony AZ2-F platform with proprietary middleware, unknown compiler hardening, and a process supervisor that may mask crashes. The senior reviewer's next-6 is operationally correct; I reorder slightly to parallelize the root-daemon audit and add a hard stop on flash-write risk.

---

## A. Senior Reviewer Major Findings — AGREE / DISAGREE / EXTEND

1. **CRITICAL — DVB-AIT/ISDB-Tb standards mismatch (Finding 1)**  
   **AGREE.** ISDB-Tb (ARIB STD-B10) carries application signalling in the PMT via `component_descriptor` (tag 0x50) pointing to a data component carrying an AIT *equivalent* (ARIB B23 `application_info_table`), not ETSI TS 102 796 AIT sections on `stream_type 0x05`. The Opera HbbTV stack expects DVB-SI; it will never see ISDB-Tb AIT sections. `osmo-fl2k` generates DVB-T; the EX725's ISDB-Tb tuner (likely Sony CXD28xx) cannot demodulate it. The OpenCaster ISDB-Tb fork produces Ginga NCL signalling, not HbbTV. **Lane 1 is dead for HbbTV on this hardware.** Reclassify as "gated hypothesis — only testable if post-root firmware inspection reveals a dormant HbbTV AIT parser wired to the ISDB-Tb demux path (probability: near zero)."

2. **CRITICAL — Ranking inversion toward built-in browser + CERS sendText (Finding 2)**  
   **AGREE.** The Brazilian manual (42730121M.pdf, p.21) explicitly lists "Navegador da Internet" under Aplicativos for the EX725 family. CERS registration is live; `sendText`/`getText` are in the ActionList; IRCC keys for InternetWidgets/InternetVideo/AppliCast exist. Zero hardware, zero purchase, delivery path verified end-to-end *except* the final UI interaction. This **must be Lane 1**. The study's Lane 2 is the only lane that can falsify CVE-2011-2628 *today*. The senior reviewer's inversion is correct; the study's ranking is a planning error.

3. **HIGH — Oracle uncalibrated, no positive control (Finding 3)**  
   **EXTEND.** The senior reviewer correctly identifies that `HOST_WDT` counts hardware watchdog trips (full-system hang), not supervised-process crashes. The browser likely runs under a `procd`/`init` supervisor that respawns on SIGSEGV/SIGKILL — a clean exploit crash may *never* increment `HOST_WDT`. The 8-blink LED is the only per-crash signal, and its sensitivity is unmeasured. **Additional flaw:** the study's "SELF CHECK" readout requires the *physical remote* (service mode not armable via IRCC — live-tested negative). Between crashes you must physically press buttons on the TV. This makes high-frequency ladder runs impractical. **Fix:** the stage-0 payload *must* include a LAN beacon *and* an on-screen DirectFB write (via Presto's DFB layer) as primary readouts; service-mode counters are secondary, low-frequency confirmation only.

4. **HIGH — Safety gates missing (Finding 4)**  
   **AGREE.** The study lists "deliberate safety gates" as narrative; they are not encoded as pass/fail preconditions. **Add:** (a) payload manifest: `no open("/dev/mtd*", O_WRONLY)`, `no ioctl(MEMERASE/MEMWRITE)`, `no write()` to `/dev/block/*` — enforced by static analysis of shellcode bytes; (b) WAN quarantine: `iptables -A OUTPUT -o br0 -d ! 192.168.0.0/16 -j DROP` during test windows; (c) spray cap: `measured_headroom_MB - 32` (leave margin for middleware); (d) recovery rehearsal: document the exact physical-remote sequence for factory reset / service-mode "FACTORY INIT" before first induced crash.

5. **HIGH — Mobile-line lineage mislabeled (Finding 5)**  
   **AGREE.** The study claims "fires on Opera Mobile of the same 2.7 core." Adversarial pass shows Mobile 10.x = Presto 2.4/2.5, Mobile 11.x = 2.8.149 (Wikipedia says Mobile 11.0 = 2.7.62 — conflict unresolved). **Correct statement:** "fires on cores bracketing 2.7 from below (2.4/2.5) and above (2.8.149/2.7.62), demonstrating the frameset-unload path survives cross-product compilation." Pull the exact Mobile UA strings from the researcher's blog (Nokia N8/Symbian^3 debug session) to anchor this.

6. **MEDIUM — MIME/timing controls for trigger (Finding 6)**  
   **AGREE.** `application/xhtml+xml` is mandatory — `text/html` uses a different parser path in Presto. Unload must be triggered via multiple mechanisms: `<meta http-equiv="refresh">`, `location.href = ...`, `iframe.remove()`, `window.open('','_self')`. Minimum 3 trials per mechanism. Document that a single silent run = non-result.

7. **MEDIUM — "No ASLR on MIPS" overbroad (Finding 7)**  
   **AGREE.** `mmap`/library base is deterministic (no `HAVE_ARCH_PICK_MMAP_LAYOUT` for MIPS in 2.6.35). But `randomize_va_space` (sysctl) enables `randomize_stack_top()` and `arch_randomize_brk()` — arch-independent. Sony's init scripts may set `vm.mmap_rnd_bits`/`vm.mmap_rnd_compat_bits` (backported?). **Fix:** treat stack/brk as *potentially* randomized; add `cat /proc/self/maps` beacon in stage-0 to measure actual layout per run.

8. **MEDIUM — Allocation geometry unknowable ex ante (Finding 8)**  
   **EXTEND.** The senior reviewer notes Opera's sub-allocator may intercept large blocks. **Deeper:** Presto's `OpMemory`/`HeapAllocator` carves a single large `mmap` region at startup (typically 64–128 MB on embedded) and sub-allocates DOM/JS objects from it. `%u`-encoded JS strings may be allocated from this arena *or* from glibc via `malloc` — depends on string length and Presto's `StringImpl` threshold. The 1 MB spray blocks in the PoC likely exceed Presto's internal threshold and fall back to `malloc` → `mmap`, but **this is unverified**. The spray ladder *must* measure: (a) where each spray block lands (`/proc/self/maps` beacon), (b) whether adjacent blocks are contiguous (required for sled reliability), (c) whether the allocator returns `MAP_FIXED` regions (unlikely). **Do not assume glibc malloc geometry.**

9. **MEDIUM — Stockpile lane-fit alternates (Finding 9)**  
   **AGREE.** CVE-2012-6468 (long HTTP response heap overflow) is the highest-value hedge: pure server-side, triggers on *any* fetch the attacker controls (DNS-redirected portal, widget manifest, `<img>`, `<svg>`, XHR). CVE-2012-3561 (URL-string allocation) via 302 `Location` header. CVE-2012-6470 (GIF) via `<img>`. CVE-2012-6465/2013-1638 (SVG clipPaths) and CVE-2013-1637 (DOM events) fire from any rendered page. **All six require no URL-entry UI.** They fit Lanes 2–4 (DNS redirect) and the HbbTV broadband path. Stockpile PoCs for each; test in parallel with 2628.

10. **MEDIUM — Promote root-daemon audit and Ginga lane (Finding 10)**  
    **EXTEND.** The non-browser surfaces are *always-on, unauthenticated, root-privilege* (or `root`-equivalent via `libupnp`/`libmicrohttpd` running as `root` on AZ2-F):
    - **UPnP SetAVTransportURI**: `libupnp` 1.6.x parser for `URI` argument (unvalidated length, scheme, path) — classic stack/heap overflow surface.
    - **SUBSCRIBE / CALLBACK**: GENA eventing delivers `NOTIFY` to attacker-controlled `CALLBACK` URLs (SSRF, parser bugs, internal service enumeration).
    - **libmicrohttpd 0.4.6** (s2mtv endpoint): known CVEs (CVE-2012-2741 path traversal, CVE-2013-0294 DoS), but more importantly: minimal request parsing, no limits on header/body size, runs as `root`.
    - **UDP 7776**: bound socket, undocumented protocol. Black-box fuzz with `radamsa`/`boofuzz` from LAN — zero cost, high yield.
    - **Ginga/ISDB-Tb**: the *only* standards-native broadcast lane. CPqD SBSeg 2010 demonstrated root via malicious NCL/Lua (TQTVD Astro engine). Same `gr-isdbt` modulator gear. **Promote to Lane 1b (parallel to browser lane).**

11. **LOW — AIT descriptor labeling (Finding 11)**  
    **AGREE.** `transport_protocol_descriptor.descriptor_tag = 0x02`; `protocol_id = 0x0003` for HTTP. Descriptor tag `0x03` = `dvb_j_application_descriptor` (unused). Fix in any OpenCaster payload script.

12. **LOW — Repo hygiene (Finding 12)**  
    **AGREE.** `[C:live]` tags on UA strings are false (no live capture from PKG4.027BRA). AppliCast rank = "hypothesis (untested)." Step 0 must include `IRCC AppliCast` keypress during `tcpdump`.

---

## B. Additions — Missed by Both Study and Senior Reviewer

1. **UPnP GENA SUBSCRIBE / CALLBACK handling** — The `libupnp` stack processes `SUBSCRIBE` with `CALLBACK` headers containing attacker-controlled URLs (IPv6, internal IPs, redirects, long paths). This hits the event delivery HTTP client code path (often a minimal `libcurl`/`wget`-like fetcher running as `root`). No analysis in study; no fuzz plan.

2. **libmicrohttpd 0.4.6 request parsing** — The s2mtv endpoint (`/s2mtv/SSDgetDeviceInfo/`) runs on MHD 0.4.6. This version lacks request size limits, has a stack-based header parser, and handles `Content-Length`/`Transfer-Encoding` ambiguously. A single oversized `POST`/`PUT` with malformed headers is a trivial remote DoS/RCE candidate. **Test: `curl -X POST -H "Content-Length: 2147483647" -H "Transfer-Encoding: chunked" --data-binary @/dev/zero http://tv/s2mtv/...`**

3. **UDP 7776 as a fuzz target** — Bound UDP socket, no auth, unknown parser. Send malformed packets (oversized, fragmented, crafted TLV if protocol guessed) from LAN. Cost: one `python` script. Yield: potential pre-auth RCE in a root daemon.

4. **MIPS mipsel retarget — Opera allocator vs. glibc mmap**  
   - Presto 2.7 `HeapAllocator` reserves a 64–128 MB `mmap` region at startup (`MAP_PRIVATE | MAP_ANONYMOUS`, no `MAP_FIXED`). DOM/JS allocations < 128 KB typically come from here.  
   - `%u`-encoded strings: Presto's `StringImpl` uses UTF-16 (2 bytes/char). A 1 MB JS string = 524,288 chars. Presto may rope-fragment large strings or cap at 64 KB. **Spray blocks may not be contiguous in virtual memory.**  
   - glibc 2.7 `mmap_threshold` = 512 KB (32-bit cap). Blocks > 512 KB *and freed* raise threshold; **never-freed blocks always mmap**. But if Opera's allocator satisfies the request from its arena, `malloc` never sees it.  
   - **Cacheflush race:** `cacheflush(syscall 4147, BCACHE=3)` flushes *data* cache to RAM, but I-cache lines for the *same VA range* may be speculatively loaded *after* flush if the CPU prefetches. Must execute a `sync`/`nop` barrier *and* jump to a trampoline address *outside* the flushed region, then branch into payload.  
   - **Branch delay slots:** Every `j`/`jal`/`b` executes the next instruction. Shellcode sled must be `NOP`-safe *per word* (0x00000000 = `sll $zero,$zero,0` works; 0x34214141 = `ori $at,$at,0x4141` works). Landing in the middle of a 4-byte instruction = crash. Sled must be word-aligned and every word individually harmless.

5. **DirectFB as shared attack surface** — EX725 uses DirectFB 1.4.x for compositing. Presto renders via DFB. DFB 1.4 had multiple integer overflows in surface allocation (CVE-2011-XXXX class). If the browser and DFB share a process (likely on AZ2-F), a DFB overflow via crafted HbbTV/portal HTML5 `<canvas>`/`<video>` is a parallel Presto-adjacent path.

6. **NVRAM/flash recovery procedure undocumented** — The study assumes "power-cycle/self-check/factory-reset recovery path rehearsed." **No such procedure is documented in the repo.** Service mode requires physical remote. Factory reset from service mode may not clear a corrupted kernel/module state. Need: (a) exact service-mode key sequence for "FACTORY INIT", (b) USB firmware recovery mode (if any), (c) JTAG header location (unpopulated?) as last resort.

7. **Watchdog identity** — `HOST_WDT` baseline 21 over 11,498 boots. Is this the *hardware* watchdog (external PMIC, trips only on full-system hang) or the *kernel softlockup detector* (`kernel.watchdog=1`, trips on CPU stall)? If hardware, a browser-process crash/respawn *will not increment it*. If kernel softlockup, it *might*. **Read `/proc/sys/kernel/watchdog` and `dmesg | grep -i watchdog` on the live set.**

8. **CVE-2011-2629..2633 (same 11.11 fix batch)** — Pop-up reload, `column-count` CSS, Silverlight destruction, CRL handling. Fixed in same release as 2628. Some may affect 2.7.61. **Check Presto 2.7.62 changelog for backport markers.**

9. **DNS rebinding / same-origin on LAN** — If the browser loads a page from `http://tv.local/...` (DNS-redirected portal), its same-origin policy applies to `tv.local`. Sub-resources (XHR, fetch, WebSocket) to `192.168.0.x` may be blocked unless CORS headers are served. **Exploit payload must be same-origin or serve CORS.**

10. **Ginga NCL/Lua engine version** — CPqD SBSeg 2010 exploited Lua 5.1 sandbox escape in TQTVD Astro. **What Lua version ships on PKG4.027BRA?** `strings` on Ginga binaries post-root. If Lua 5.1, the sandbox escape is a known, reliable root path via broadcast NCL — no browser needed.

---

## C. My Next-6-Actions (Ordered)

1. **Step 0 — Live capture + browser confirmation (WAN quarantined)**  
   Boot EX725, `tcpdump -i br0 -w step0.pcap`, IRCC press: `InternetWidgets`, `InternetVideo`, `AppliCast`, `Ddata`, `Home → Aplicativos`. Capture: (a) live UA string (HbbTV token?), (b) cleartext HTTP hosts, (c) AppliCast emission?, (d) **visually confirm "Navegador da Internet" in Aplicativos menu**. If present → `sendText "http://192.168.0.XX/test.xhtml"` via CERS. **Delivery solved in < 30 min, zero hardware.**

2. **Positive control crash + oracle calibration (parallel with #1)**  
   Serve `crash.xhtml`: JS runaway recursion (`function f(){f()}f()`) + forced OOM (`Array(1e7).join('x')`) via same delivery lane. Run 3×. Record: (a) `HOST_WDT` delta, (b) boot count delta, (c) 8-blink LED, (d) DirectFB on-screen "CRASH OK" marker, (e) LAN beacon receipt. **Only after this run is any CVE result interpretable.**

3. **CVE-2011-2628 falsifier run**  
   Unmodified EDB 17936 trigger, `application/xhtml+xml`, 3 unload mechanisms (meta-refresh, `location.href`, `iframe.remove()`), 3 trials each. Quiescent windows (60s idle), WAN down. Readouts: beacon + on-screen marker + service-mode counters post-reboot. **If negative on all 9 trials → 2628 not exploitable on this build; pivot to stockpiled CVEs.**

4. **Parallel root-daemon audit (starts now, zero hardware)**  
   - `SetAVTransportURI`: fuzz `URI` arg (long, `%`-encoded, `file://`, `http://127.0.0.1:7776/`) via `upnp-tool`/custom SOAP.  
   - `SUBSCRIBE`: `CALLBACK=<http://192.168.0.ATTACKER:PORT/longpath>`, `NT=upnp:event`, `Timeout=Second-3600`. Observe `NOTIFY` delivery.  
   - `libmicrohttpd 0.4.6` (s2mtv): oversized headers/body, `Transfer-Encoding: chunked` + `Content-Length`, path traversal in `GET /s2mtv/../../../etc/passwd`.  
   - `UDP 7776`: `radamsa` corpus from any captured packet (or empty) → 10k iterations, watch for crash/LED blink.  
   - **Document findings before any RF purchase decision.**

5. **If 2628 positive: MIPS spray ladder with measurement beacon**  
   Stage-0 payload: (a) `cacheflush` stub (syscall 4147, BCACHE=3), (b) read `/proc/self/maps` → UDP beacon, (c) on-screen "SPRAY N MB OK" via DirectFB. Sled: `0x00000000` (NOP) or `0x34214141` (null-free). Spray sizes: 4/8/16/32/64 MB (cap at `measured_headroom - 32 MB`). Landing address from *measured* maps, not arithmetic. **No flash writes, no persistence.**

6. **Ginga/ISDB-Tb lane assessment (decides RF purchase)**  
   Post-root: `strings` Ginga binaries for Lua version, NCL parser. If Lua 5.1 + known sandbox escape → **buy `gr-isdbt` modulator (HackRF/bladeRF + GNU Radio), target Ginga via broadcast NCL.** This is the standards-native, public-precedent path for ISDB-Tb. If Ginga unreachable → browser lane only; no RF gear needed.
