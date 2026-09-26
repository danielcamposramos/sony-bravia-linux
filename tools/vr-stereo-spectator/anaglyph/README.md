# Anaglyph for any colour screen

`svrtv-anaglyph.fx` turns a side-by-side stereo frame into red/cyan anaglyph,
for any colour screen and a pair of red/cyan glasses (red on the left eye).
It is a ReShade effect run by gamescope, outside the game and 64-bit, so it
works for any game that outputs side by side, 32-bit or 64-bit, native or
Proton. The stereo module keeps producing side by side; this is one extra
step at the very end of the chain.

| mode | `--reshade-technique-idx` | matrix |
|---|---|---|
| CRT | 0 | computed for a CRT's phosphors (Sanders and McAllister; the one StereoPhoto Maker uses) |
| modern screens | 1 | computed for an LCD panel (Zhang and McAllister) |

Both are least-squares channel mixes for red/cyan glasses No. 7003 from
REEL3D (Eric Dubois's method, 2001), coefficients as collected at
http://chrisjones.id.au/Dubois/Dubois.html and checked against its raw page
(2026-09-24); the CRT one matches `tools/bravia_anaglyph.py`. The mix is done
in linear light (the sampler decodes sRGB, the pass encodes it again).

## Running it

Two things decide whether turns stay solid (2026-09-25, see "The gamescope frame race"
below): the game must render freely inside gamescope, and gamescope's own
output must not queue behind vsync. The second needs the 3D TV build of
gamescope in `../gamescope/` (a one-line patch, built 64-bit from Debian's
source; the system gamescope is untouched).

```sh
mkdir -p ~/.local/share/gamescope/reshade/Shaders
cp svrtv-anaglyph.fx ~/.local/share/gamescope/reshade/Shaders/
# DXVK 2.0 (bundled with Half-Life 2) reads its settings from a file:
printf 'd3d9.presentInterval = 0\n' > "$HOME/.local/share/svrtv-dxvk.conf"
# Steam launch options of the game (Half-Life 2 with the module: SVRTV_LAYOUT=sbs in bin/svrtv.ini):
DXVK_CONFIG_FILE="$HOME/.local/share/svrtv-dxvk.conf" SDL_VIDEODRIVER=x11 gamescope-3dtv --backend sdl -g --prefer-vk-device 10de:2504 -f -W 1920 -H 1080 -w 1920 -h 1080 --reshade-effect svrtv-anaglyph.fx --reshade-technique-idx 1 -- env -u WAYLAND_DISPLAY %command% -vulkan +mat_forceaniso 16
```

`--reshade-technique-idx 0` is the CRT matrix, `1` modern screens.
`+mat_forceaniso 16` (anisotropic filtering 16x) keeps slanted surfaces sharp
in both eyes. The bench suite does all of this for `vr=anaglyph-crt` and
`vr=anaglyph-modern` steps (`tools/hl2-bench/`, `GAMESCOPE_BIN`,
`PLAY_PRESENT_INTERVAL=0`, `HL2BENCH_ARGS`).

## What it took (gamescope 3.16.24, 2026-09-24)

- **An effect with no uniforms never runs.** gamescope always allocates a
  uniform buffer of the effect's uniform size; with none that is a zero-size
  allocation, which the NVIDIA driver refuses (`vkAllocateMemory failed`) and
  RADV crashed on. The effect declares one unused uniform. (A gamescope bug;
  a minimal inverting effect showed it too.)
- **gamescope must composite on the GPU the game renders on**
  (`--prefer-vk-device`, here the RTX 3060): on the other one the import of
  the game's frames failed (`importing the supplied dmabufs failed`) and
  gamescope aborted.
- **`--backend sdl`**, with gamescope's SDL on X11: in Steam's launch
  environment the automatic choice fell to headless, which shows nothing;
  the `wayland` backend hands NVIDIA buffers to KWin on the AMD iGPU, which
  cannot import them (the same dmabuf error, then an abort).
- **`env -u WAYLAND_DISPLAY`** for the game: inside gamescope it must use
  gamescope's X11 display, not the desktop's Wayland.
- **Keyboard:** under gamescope the keys did not reach the game (the mouse
  did), even with a KWin rule forcing focus. `-g` (gamescope's "grab the
  keyboard") fixed it (Daniel, 2026-09-24).
- `Couldn't find texture with name: V__BackBufferTex` in gamescope's log is
  harmless: gamescope binds the frame to the `COLOR` texture at draw time.

## Result

Daniel, on the HX855 (no glasses to hand, a long-time anaglyph viewer): "both
perfect results", CRT and modern screens.

## The gamescope frame race, found and fixed (2026-09-25)

It showed first in anaglyph: static geometry swam in depth during fast mouse
turns; slow pans, walking and moving objects were clean, and native side by
side never showed it. It was never an anaglyph fault. It was a frame race in
gamescope: side by side **through gamescope** on the 3D TV swam the same way
(runs p08, p09), and anaglyph only made it easy to see.
A per-frame log of the engine's view angles (`SVRTV_ANGLELOG=1`) measured it:

| run | path | frame time p5 / p95 | frames over 1.5x median |
|---|---|---|---|
| p13 | native side by side | 15.6 / 17.7 ms | 0.2% |
| p14 | gamescope, game on vsync | **4.0 / 33.7 ms** | 16% |
| p16a | gamescope, game free-running | 2.6 / 15.8 ms | 28% |
| p16c | gamescope-3dtv (output IMMEDIATE), free-running | 2.6 / 5.7 ms | 8% |
| p18 | same, anaglyph (modern screens) | 2.5 / 4.5 ms | 2% |
| p19 | same, anaglyph (CRT) | 2.5 / 5.6 ms | 8% |

Two queues in a row: the game's vsync, then gamescope's nested output, which
gamescope 3.16 hard-codes to FIFO (`src/rendervulkan.cpp`). Frames reached
the screen in 4 ms / 33 ms pairs; the view froze, then jumped, and during a
turn that reads as depth. Letting the game run free removed the swim (p15,
p16; Daniel: "not to the point of artifacting, now it's more akin to mouse
lag"); the output on IMMEDIATE removed the lag (p16c: "just like the original
sbs", no tearing, since KWin still composites the window). NVIDIA offers no
MAILBOX for that window (p16b fell back to FIFO). Daniel, anaglyph p18:
"PERFECTION!"; p19 (CRT): "also a perfect run".

Ruled out on the way: the colour matrices, the Pulfrich effect, the ReShade
pass itself (an identity pass swam too), `--force-grab-cursor`, `m_filter`,
the GPU copy, the eyes' timing inside the frame.
