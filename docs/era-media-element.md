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

### Never clip an ancestor

Wrapping the element in a sized `<div>` with `overflow:hidden` **silenced
the audio** while the identical wrapper without `overflow:hidden` played,
and so did a layout with no wrapper at all. Measured on the panel
2026-09-18 across four variants:

| layout | audio |
|---|---|
| plain element, any size | plays |
| scaled element, no wrapper | plays |
| scaled element, sized wrapper, **`overflow:hidden`** | **silent** |
| scaled element, sized wrapper, no overflow property | plays |
| scaled element, sibling spacer instead of a wrapper | plays |

A parent is fine. **A clipped ancestor is not** — it evidently takes the
engine down a path where the decoder never starts. This belongs with the
standing rules about never using `<audio>` and never `display:none`:
this engine cares about the element's context, not only its appearance.

### Events: almost none of them fire

The probe left "loading" on screen throughout playback, which means
`loadstart`, `canplay` and `playing` never fired. `timeupdate` does fire
and is the only event worth building on — which is why the music page's
play/pause glyph is set optimistically and re-synced from `timeupdate`
rather than waiting for `play`/`pause`.

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

## Sizing

Percentages work and are preferable: a `<table width="100%">` is the
most reliable layout primitive this browser has, and an element at
`width:33%` scaled x3 fills the viewport without anyone hard-coding
1920. Height still needs pixels, since percentage heights need a
declared parent height all the way up.

## The native bar already shows time

The set's own transport draws elapsed time and a progress indicator. The
app does not need to render its own clock or progress bar when the native
controls are visible — with the one caveat that this bar fades out, so
anything that must be readable at all times still belongs to the page.

## Album art

Audio in a `<video>` element leaves the frame empty, so the **`poster`
attribute is the natural home for Serviio's cover art**, and it renders.
At full width the art is more visible laterally than vertically, and the
page still fits with no horizontal scrollbar.

## Related

- [era-key-vocabulary.md](era-key-vocabulary.md) — what the remote can send
- `tools/serviio/tv-mediabrowser/server.py` — `/probe/caps`, `/probe/art`
