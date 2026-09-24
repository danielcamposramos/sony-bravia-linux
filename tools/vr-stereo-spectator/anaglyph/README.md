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

```sh
mkdir -p ~/.local/share/gamescope/reshade/Shaders
cp svrtv-anaglyph.fx ~/.local/share/gamescope/reshade/Shaders/
# Steam launch options of the game (Half-Life 2 with the module: SVRTV_LAYOUT=sbs in bin/svrtv.ini):
gamescope --backend sdl --prefer-vk-device 10de:2504 -f -W 1920 -H 1080 -w 1920 -h 1080 \
    --reshade-effect svrtv-anaglyph.fx --reshade-technique-idx 1 -- env -u WAYLAND_DISPLAY %command% -vulkan
```

The bench suite does this for `vr=anaglyph-crt` and `vr=anaglyph-modern`
steps (`tools/hl2-bench/`).

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
- **`--backend sdl`**: in Steam's launch environment the automatic choice
  fell to headless, which shows nothing.
- **`env -u WAYLAND_DISPLAY`** for the game: inside gamescope it must use
  gamescope's X11 display, not the desktop's Wayland.
- **Keyboard:** under gamescope the keys did not reach the game (the mouse
  did): KWin did not give gamescope's window keyboard focus. The suite's
  KWin rule now forces focus with focus-stealing prevention off (untested
  yet).
- `Couldn't find texture with name: V__BackBufferTex` in gamescope's log is
  harmless: gamescope binds the frame to the `COLOR` texture at draw time.

## Result

Daniel, on the HX855 (no glasses to hand, a long-time anaglyph viewer): "both
perfect results", CRT and modern screens. In fast mouse pans the colours
flicker out of step; slow pans are clean. The same on the EX725 (NVIDIA port,
no copy between GPUs) and on a cheap LED panel through a DisplayPort adapter,
so neither one TV's processing nor the GPU copy. The likely cause is the
panels: sample-and-hold LCD/LED with colour-dependent response times, a
documented motion artifact that anaglyph makes visible. Pending: the same
fast pans in side by side with shutter glasses, to clear the render.
