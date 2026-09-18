# What the era `<video>` element can actually do

Measured on a KDL-46EX725 (AZ2-F) with `/probe/caps` and `/probe/art`,
2026-09-18. Everything here was read off the live object on the panel,
not inferred from the browser version.

## Codec support — the transcode pipe stays

`canPlayType()` returns an empty string for a format the set cannot play.

| plays natively | returns empty |
|---|---|
| `audio/mpeg` · `audio/mp4` · `audio/aac` · `video/mp4` | `audio/flac` · `audio/ogg` · `audio/wav` · `video/webm` · `video/x-matroska` |

**This closes an open Phase 2 question.** The idea was that a dedicated
Serviio profile might serve lossless audio directly and let the app-side
`/atr/` ffmpeg pipe retire. It cannot: FLAC, OGG and WAV are not
playable here in any container Serviio could offer, so the live MP3
transcode is not a workaround to be removed, it is the only way this
generation hears a lossless library. Matroska and WebM are equally out,
which matches the video lane already only trusting progressive MP4.

## Property surface

Every property probed exists **except `preload`**, which reports as
unsupported — so `preload="none"` in our markup is decorative, and the
element decides its own buffering. `volume` exists and reads `1`.
`playbackRate`, `seekable`, `buffered`, `loop`, `poster`, `readyState`
and `networkState` are all present.

## Native controls

The `controls` attribute works, and with the source attached as a
`<source>` child carrying an explicit `type`, **audio plays under the
set's own transport bar and OK operates it**.

Three measured limits:

1. **The bar's height is fixed in pixels.** Growing the element widens
   the bar but never makes it taller. At full width it is a thin strip
   across the screen — legible only up close.
2. **`zoom` does nothing.** `style.zoom` exists on the object, but
   setting `zoom:2` left the element at its declared size. A property
   existing is not the same as it working; only the panel can tell you
   which.
3. **`-o-transform: scale()` works, and scales the native controls with
   the element.** This is the lever for making the transport readable at
   couch distance.

### The transform caveat

A transform takes no part in layout. The element keeps its pre-scale
footprint, so the page content after it renders *underneath* the scaled
pixels. The fix is to reserve the final size with a plainly sized
container:

```html
<div style="width:960px;height:540px;overflow:hidden;">
  <video controls width="480" height="270"
         style="width:480px;height:270px;
                -o-transform:scale(2);-o-transform-origin:top left;">
  </video>
</div>
```

No flexbox, no `calc()`, just declared dimensions — which is all this
browser can be trusted with.

## Album art

Audio in a `<video>` element leaves the frame empty, so the **`poster`
attribute is the natural home for Serviio's cover art**, and it renders.
At full width the art is more visible laterally than vertically, and the
page still fits with no horizontal scrollbar.

## Related

- [era-key-vocabulary.md](era-key-vocabulary.md) — what the remote can send
- `tools/serviio/tv-mediabrowser/server.py` — `/probe/caps`, `/probe/art`
