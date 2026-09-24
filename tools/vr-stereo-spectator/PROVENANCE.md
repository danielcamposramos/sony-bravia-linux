# VR Stereo Spectator: provenance

## What it is built on

- **Valve's Source SDK 2013**, `ValveSoftware/source-sdk-2013` at commit
  `b8cfb12c0e08` (2026-09-05): the `ISourceVirtualReality` interface
  (`src/public/sourcevr/isourcevirtualreality.h`, `SourceVirtualReality001`)
  and the headers it pulls in. The module is our own code that implements
  that interface; no SDK source file is copied into it. It follows the SDK's
  license, the Source 1 SDK License (see `sourcevr/LICENSE`).
- **How the engine uses the interface** was read from the same SDK's client
  code (`src/game/client/view.cpp`, `client_virtualreality.cpp`) and
  mathlib (`src/mathlib/vmatrix.cpp`, the projection convention), not
  guessed. The file names and line-level facts are in `sourcevr/README.md`.
- **The target game** is Half-Life 2's native Linux build, as installed and
  inspected on 2026-09-24 (Steam build 19307283): 32-bit binaries, a shipped
  `bin/sourcevr.so` exporting `SourceVirtualReality001` with no headset SDK
  code, and a client that still carries the VR render path.

## Who made it, and how

Directed by Daniel Campos Ramos, who set the goal (native Linux stereo for
Half-Life 2 on 3D televisions, with wiz3D as the reference to measure
against), chose the route (the 2013 SteamVR-era engine path), the name, and
the license. Written with an AI partner, Claude (Anthropic, Claude Opus 5.5
through the Claude CLI), under that direction, as with the rest of this
repository ([../../PROVENANCE.md](../../PROVENANCE.md)).

## What has been verified, and what has not

- **Verified (2026-09-24):**
  - both builds (32-bit and 64-bit) compile against the SDK headers;
  - the only export is `CreateInterface`;
  - the only dependencies are `libc` and `libm`, at GLIBC 2.1.3 and 2.2.5;
  - `sourcevr/test_geometry.cpp` loads each build and checks the stereo
    numerically: zero parallax at the convergence distance, behind-screen
    and in-front parallax on the correct sides, and the viewports for both
    layouts and the eye swap. The test caught one bug before any game run:
    a swap option that swapped both cameras and halves and so cancelled out.
- **Not yet verified:** anything inside the game. The open questions are
  listed in `sourcevr/README.md`, and the first in-game run will be recorded
  here with its date and result.
