# Valve: stereo spectator drafts (2026-09-24)

Raw material for Daniel, who reviews and approves each one before it is posted. **Posted 2026-09-24: 01 as [Source-1-Games#8297](https://github.com/ValveSoftware/Source-1-Games/issues/8297); 02 as a [comment on #3782](https://github.com/ValveSoftware/Source-1-Games/issues/3782#issuecomment-5822863780); 03 as a [comment on #1013](https://github.com/ValveSoftware/Source-1-Games/issues/1013#issuecomment-5822869918); 04 as a [comment on source-sdk-2013#268](https://github.com/ValveSoftware/source-sdk-2013/issues/268#issuecomment-5822876523); 05 as [SteamVR-for-Linux#961](https://github.com/ValveSoftware/SteamVR-for-Linux/issues/961). All five posted.**
Order: 01 first (the main Half-Life 2 issue); 02-04 are short comments on older issues that link to it; 05 is the SteamVR issue, which links to 01.

| draft | where | what |
|---|---|---|
| [01](01-source-1-games-hl2-vr-on-3d-display.md) | ValveSoftware/Source-1-Games **#8297** (posted) | the six VR-mode behaviours found making HL2 drive a 3D TV, plus the OpenGL crash; pings @kisak-valve, cc @misyltoad |
| [02](02-source-1-games-3782-comment.md) | Source-1-Games #3782 (posted) | "Is sourcevr supported on linux?" (2022): yes, with a replacement module |
| [03](03-source-1-games-1013-comment.md) | Source-1-Games #1013 (posted) | the 2013 request for side-by-side 3D: it exists now |
| [04](04-source-sdk-2013-268-comment.md) | source-sdk-2013 #268 (posted) | the 2014 HUD checkerboard: the cause (no precache) and the fix |
| [05](05-steamvr-for-linux-stereo-spectator.md) | ValveSoftware/SteamVR-for-Linux **#961** (posted) | stereo spectator (side-by-side VR View mirror) and player (an OpenVR driver for a 3D display, openvr #706); pings @kisak-valve, cc @charleslvalve, @aaronleiby |
| [06](06-source-1-games-8297-update-gamescope.md) | [#8297, comment](https://github.com/ValveSoftware/Source-1-Games/issues/8297#issuecomment-5842650764) (posted 2026-09-26) | the gamescope frame race, found and fixed (two acts); posted after 07 |
| [07](07-gamescope-nested-present-mode-pr.md) | [ValveSoftware/gamescope#2438](https://github.com/ValveSoftware/gamescope/pull/2438) (posted 2026-09-26) | `GAMESCOPE_NESTED_PRESENT_MODE`: the nested output off FIFO; cites misyltoad |

Rules applied: pings only in the two new issues; each comment carries only its own new content; disclosure once, at the end of each new issue, if Daniel wants it; every claim traced to a log, a measurement, a source file or a quoted source.
