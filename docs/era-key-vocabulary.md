# What keys the era app layer could actually see

Recovered from the scavenged AppliCast widget corpus (45 JS files,
6.9 MB, served from `/var/www/applicast` on d2server), 2026-09-18, while
looking for the numeric remote keycodes the `/keys` probe has never
captured.

## The corpus does not carry numbers

`KeyEvent` is referenced 166 times and **defined nowhere**. Every use is
symbolic:

```js
case KeyEvent.KEY_CODE_UP:
```

No `VK_*` table, no `DOM_VK_*`, no numeric `keyCode ==` comparison in any
file. The object is injected by the widget engine at runtime, so Sony's
own apps never needed to know the integers. Our numeric map still has to
come from the panel.

## But it gives the complete vocabulary

Every `KEY_CODE_*` name that appears anywhere in the corpus:

| available | |
|---|---|
| `KEY_CODE_UP` `KEY_CODE_DOWN` `KEY_CODE_LEFT` `KEY_CODE_RIGHT` | d-pad |
| `KEY_CODE_CONFIRM` `KEY_CODE_CANCEL` | OK / back |
| `KEY_CODE_RED` `KEY_CODE_GREEN` `KEY_CODE_YELLOW` `KEY_CODE_BLUE` | colour keys |

That is the whole list. **There is no PLAY, PAUSE, STOP, NEXT or PREV.**
Not in the audio widgets, not in the gallery, not anywhere.

## What follows, and what does not

**Evidence, not proof.** This is the vocabulary of the *widget engine*,
which is not the same environment as the browser (InettvBrowser 2.2) our
portal runs in. A key absent from the widget API could still reach the
browser as a keydown.

What it does mean:

1. The eight transport keycodes in `config.ini [keys]` are a guess
   inherited from Android TV, and the platform's own app layer had no
   such concept. Expecting them to fire is now the less likely bet.
2. The on-screen transport bar is not a stopgap until the media keys are
   mapped. It may be the only transport this platform can offer an app.
3. **The colour keys are the unexploited surface.** Sony's own widgets
   bind RED/GREEN/YELLOW/BLUE, so those presses demonstrably reach the
   app layer, they are physical buttons on the remote, and our player
   currently ignores all four. If they arrive as keydowns in the browser,
   they are four free, unambiguous, single-press actions — the natural
   home for play/pause, next, previous and repeat.

## Measured on the panel, 2026-09-18

The `/keys` session was finally run on the EX725. **15 KEYPROBE captures,
five distinct codes**, and the prediction above held:

| code | what sends it |
|---|---|
| 13 | OK / confirm |
| 37 | d-pad LEFT **and the remote's REW button** |
| 39 | d-pad RIGHT **and the remote's FF button** |
| 38 | d-pad UP |
| 40 | d-pad DOWN |

**PLAY, PAUSE, STOP, PREV and NEXT produce no keydown at all.** Not a
wrong code, no event. The widget corpus said the app layer had no such
concept and the panel agrees.

Two further findings, neither predicted:

- **REW and FF are not separate keys.** They deliver 37 and 39, the same
  codes as d-pad left and right, so an app cannot tell them apart.
- **The colour keys are not ours — all four belong to Opera.** The
  browser states this itself in the status line while a link loads.
  Green and yellow navigate between pages (history back / forward); red
  and blue scroll within a page (bottom / top). None reach the page, so
  none is bindable. That
  kills the "four free actions" idea from the previous section — worth
  recording precisely because it was the plausible-sounding conclusion
  the corpus pointed at, and the panel refuted it.

### What follows

The on-screen transport bar is not a stopgap until the media keys are
mapped. **It is the only transport this platform can give an app**, and
the eight guessed codes in `config.ini [keys]` are inert on this
generation.

## Font coverage, same session

The glyph probe was run at the same time, and it corrected the rule this
project had been using:

| renders | box |
|---|---|
| U+25B6 \u25b6 U+25C0 \u25c0 U+25AE \u25ae U+25A0 \u25a0 (Geometric Shapes) | U+2194 U+2195 U+21B5 U+21BA U+21BB (Arrows) |
| U+266A \u266a U+221E \u221e U+00AB \u00ab U+00BB \u00bb | U+23EE (Media Controls) |

"Unicode 1.1 is safe" was the wrong predictor: U+2194, U+2195 and U+21B5
are all Unicode 1.1 and all render as empty boxes. **The right predictor
is the block the panel's font ships**, and this font has Geometric
Shapes, Latin-1 and a few scattered symbols, but nothing from Arrows.

The repeat button used U+21BA and was the one button that rendered as a
box on first test. It is now U+221E, which the same probe confirms.

## Related

- `tools/serviio/tv-mediabrowser/README.md` — the `[keys]` config block
- [worldclock-schema-reconstruction.md](worldclock-schema-reconstruction.md)
  — the same corpus, same method
