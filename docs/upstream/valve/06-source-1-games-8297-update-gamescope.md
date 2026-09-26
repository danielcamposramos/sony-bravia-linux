# Draft 06: #8297 update, three display modes and the gamescope frame race (comment)

Status: **DRAFT 2026-09-25**, for Daniel to post in his own words.
Target: https://github.com/ValveSoftware/Source-1-Games/issues/8297 (comment)
Evidence: angle logs `svrtv-angles.tsv` of runs p13-p19 under `/K3D/temp/hl2-bench/` (local); gamescope logs of p16b, p16c, p18; `tools/vr-stereo-spectator/gamescope/`.
No new pings: the issue already cc's misyltoad.

---

An update since the report: Half-Life 2's VR mode now runs in three display modes, all from the same module.

1. **Side by side, native** (game straight to the 3D TV): shutter or polarised glasses.
2. **Side by side through gamescope**: the same picture, as the base for mode 3.
3. **Red/cyan anaglyph through gamescope**, for any colour screen: a gamescope ReShade effect with two least-squares matrices (Dubois), one for CRTs and one for modern screens.

Anaglyph showed a depth swim on fast mouse turns that native side by side never had.
It was not anaglyph: side by side through gamescope did the same.
It was a **frame race in gamescope**.
A per-frame log of the view angles showed it:
- **Native:** frame time 15.6 to 17.7 ms (5th to 95th percentile).
- **Through gamescope with vsync:** 4.0 to 33.7 ms, frames arriving in pairs, the view freezing and then jumping.

There were two queues in a row.
The game's vsync was one.
The other is gamescope's own output in a window, which is hard-coded to FIFO (`src/rendervulkan.cpp`, the nested swapchain).

What cured it:
- The game renders freely inside gamescope (DXVK `d3d9.presentInterval = 0`), so gamescope always takes the newest frame.
- gamescope's nested output uses IMMEDIATE instead of FIFO. That took a small patch: `GAMESCOPE_NESTED_PRESENT_MODE=mailbox|immediate`, falling back to FIFO when the surface does not offer the mode. NVIDIA offers no MAILBOX for that window; IMMEDIATE did not tear, since the desktop compositor still composites it.

Result in anaglyph, 95th percentile frame time 4.5 ms, and in my eyes: **"PERFECTION!"**
Side by side through gamescope now feels just like native.

One module change came with it: the pointer confinement from point 6 pinned the view inside gamescope, so the module leaves it off when `GAMESCOPE_WAYLAND_DISPLAY` is set.

The gamescope patch will go to ValveSoftware/gamescope as its own pull request.
Point 5 still stands: the muzzle flash needs `viewmodel_fov 90`, and that needs `sv_cheats 1`.

---

Notes for Daniel (not for posting):
- Numbers: p13 native p5/p95 15.56/17.68 ms; p14 gamescope FIFO 4.03/33.66 ms; p16a (free, stock gamescope) p95 15.80 ms, 28% of frames over 1.5x median; p16c (free, IMMEDIATE) p95 5.67 ms, 8%; p18 anaglyph modern p95 4.52 ms, 2%. p16b asked for MAILBOX and got FIFO (gamescope log: "not offered by the surface").
- "PERFECTION!" is your line from p18; keep it or drop it, your call.
- Wait for the p19 (CRT) and p20 (blur) verdicts before posting, in case either changes the text.
