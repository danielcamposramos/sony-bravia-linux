# The panel detects 3D and is forbidden to switch — in the browser path

Observed on a KDL-46EX725 (AZ2-F), 2026-09-18, playing a 3D video through
the LAN portal's full-screen `<video>` element (the promoted video
player, native controls, served from Serviio).

## What happened

1. The TV **detected the video's 3D signal** — the frame-packing /
   stereoscopy metadata carried in the stream, the same signal the
   upstream campaign is about (see `docs/3d-signalling-explainer.md`) —
   and **said so on screen**, in its own words:

   > **Sinal 3D foi detectado**

2. It **did not switch to 3D display mode automatically.**
3. **The 3D menu was not enabled either** — the set's own 3D control
   would not engage 3D while the content was playing from the browser
   path, so manual switching was blocked as well.

So the panel read the signal, announced the finding to the owner, and
was then refused the switch — automatically *and* manually — specifically
for browser-sourced video.

**The contrast is the proof.** On the same television, a spec-correct
MPO from a USB stick **engages 3D by itself**, no prompt and no menu
needed (2026-09-19, both sets, `3d-photos-on-bravia.md`). The browser
path gets as far as printing *Sinal 3D foi detectado* and then stops.
The detector works, the panel works, the 3D engine works. What differs
between the two is which source path the content arrived on.

| Path | Set's own behaviour |
|---|---|
| USB, correct MPO | detects and **switches to 3D by itself** |
| HDMI / broadcast | switches, 3D menu available (documented by Sony) |
| DLNA, correct MPO | shown flat as JPEG; an honestly announced MPO is **hidden from the listing** |
| Browser video, 3D signal present | **detects and says so on screen**, then neither switches nor enables the 3D menu |

## Why this matters

This is the whole right-to-repair thesis in one observation, on the
hardware:

- **The hardware is fully capable.** This is a 3D television; its panel
  and 3D engine work. It even did the hard part — reading the in-stream
  signal correctly and identifying the content as 3D.
- **The restriction is a software gate, not a limitation.** The same set
  switches to 3D without complaint for HDMI, USB and broadcast sources.
  The only variable here is the *source path*: video rendered in the
  browser/portal sandbox is denied the 3D switch that every other source
  is granted.
- **It is denied both ways.** A missing auto-switch could be an oversight.
  Auto **and** manual both blocked is a deliberate fence around the
  browser content path.

It also confirms, from the panel side, the premise of
[mpv PR #18490](https://github.com/mpv-player/mpv/pull/18490): the
in-stream 3D signal is real, present, and read by real hardware. mpv was
ignoring a signal this television detects live.

## What Sony's own manual documents (the decisive part)

The KDL-46HX855 i-Manual (English, Sony doc `W0005741M`; the pt-BR
`W0005743M` matches) documents the 3D control as a display-mode button
with three modes: Side-by-Side, Over-Under, and **Simulated 3D**, the
latter described as displaying regular 2D pictures in simulated 3D. The
procedure is content-agnostic: display content on screen, press the 3D
button, pick a mode "to suit the displayed content".

Two documented facts settle the framing:

1. **The restriction is scoped to the stereoscopic modes only.** The
   manual says Side-by-Side / Over-Under may be unavailable *depending on
   the input signal or format* — because those need a real 3D source.
   **Simulated 3D carries no such restriction anywhere in the section.**
   Its only caveat is that the effect "may be less pronounced with some
   picture sources" — a statement about effect strength, never about
   availability. A full grep of the i-Manual finds no line making
   Simulated 3D unavailable by input or source.
2. **The auto-switch is documented and signal-driven.** The `[Auto 3D]`
   setting "automatically switches to 3D display mode when a 3D signal is
   detected", and `[3D Signal Notification]` notifies on detection —
   exactly the detection the owner observed on the browser-played file.

The one genuine precondition the manual states is **"3D effect is
available only when pictures are displayed in full screen."** The
promoted video player is full-screen (`position:fixed` 100%), so that
condition is met — which rules out full-screen as the reason 3D is
absent for browser content.

So Sony documents a display feature (Simulated 3D) that, by its own
manual, applies to any full-screen content with no input or source
restriction, and an auto-switch driven by signal detection. On the set's
own browser-served video, full-screen, with the signal detected, none of
it engages — automatically or manually. That is a documentation-versus-
behavior gap shown entirely in Sony's own words, with no claim about
intent required.

## Corroboration from the widget corpus

The AppliCast widget layer (the browser-era app surface) exposes **no
video-3D control API at all**. A full grep of the 45-file corpus finds
one 3D reference, `set3DSurr()` in
`SNY_AudioControl/common/ceccommandcontrol.js`, and that is **audio** 3D
surround sent over HDMI-CEC to a receiver — not video stereoscopy.

So the video-3D switch was never handed to the browser/widget
environment in the first place. It is engine-internal, and the browser
path is on the wrong side of the fence. This is consistent with the
observation: the browser cannot ask for 3D, and even the user's manual
request is refused while browser content is on screen.

## The open lead: the native DLNA path

The portal plays video through the **browser**. The same Serviio library
is also reachable by the TV's **native DLNA/media player**, a different
code path that is not the browser sandbox. The untested hypothesis worth
checking next:

> Does the TV allow 3D (auto or manual) when the same 3D file is played
> through its **native DLNA player** instead of the portal browser?

If yes, the practical answer for 3D content is to route it to native
DLNA playback rather than the portal's `<video>` element — the portal
stays the browse/audio/2D surface, and 3D video hands off to the native
player that is allowed to switch. If the native path is *also* blocked,
the fence is around all app/network sources, not just the browser, which
is a stronger finding still.

Either way the conclusion for the campaign is the same: **the capability
is present and switched off in software.**

## Related

- [3d-signalling-explainer.md](3d-signalling-explainer.md) — what the
  in-stream signal is
- [era-media-element.md](era-media-element.md) — the browser video path
- `docs/upstream/media-stack/` — the upstream campaign this
  corroborates
- [right-to-repair.md](right-to-repair.md)
