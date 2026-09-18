# The panel detects 3D and is forbidden to switch — in the browser path

Observed on a KDL-46EX725 (AZ2-F), 2026-09-18, playing a 3D video through
the LAN portal's full-screen `<video>` element (the promoted video
player, native controls, served from Serviio).

## What happened

1. The TV **detected the video's 3D signal** — the frame-packing /
   stereoscopy metadata carried in the stream, the same signal the
   upstream campaign is about (see `docs/3d-signalling-explainer.md`).
2. It **did not switch to 3D display mode automatically.**
3. **Manual switching was also blocked** — the set's own 3D control would
   not engage 3D while the content was playing from the browser path.

So the panel read the signal, knew the content was 3D, and was refused
the switch — automatically *and* manually — specifically for
browser-sourced video.

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
- `tools/serviio/upstream-3d-issues/` — the upstream campaign this
  corroborates
- [right-to-repair.md](right-to-repair.md)
