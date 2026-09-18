# What these sets actually accept, audio — measured, not from a spec sheet

Three different ways in, three different capability lists. Mixing them up
is why "the TV supports X" arguments go nowhere. Everything below is
measured on the owner's own KDL-46EX725 (2011) and KDL-46HX855 (2012).

## 1. HDMI input — from the set's own EDID

Read from the HX855 while it was connected to the workstation, through
the kernel's ELD (the audio half of EDID that a sink hands its source:
`/proc/asound/card*/eld#*`). This is the set declaring its own
capabilities, not a manual:

| | Format | Channels | Sample rates | Depth / rate cap |
|---|---|---|---|---|
| sad0 | **LPCM** | 2 | 32 / 44.1 / **48 kHz** | **16, 20, 24-bit** |
| sad1 | **AC-3** | 6 | 32 / 44.1 / 48 kHz | max **640 kbps** |

`speakers [0x1] FL/FR`, `sad_count 2`. That is the whole list: **no
E-AC3, no DTS, no AAC, no TrueHD over HDMI.**

**48 kHz is the ceiling, and 24-bit is real but LPCM-only.** Verified in
use: the live stream to the set reads `format: S32_LE, channels: 2,
rate: 48000` — a 32-bit container carrying up to the 24 significant bits
the ELD allows.

**Confirmed a second way, from the driver.** With the card taken
offline for a moment so the hardware could be asked directly
(`aplay -D hw:2,7 --dump-hw-params`):

```
FORMAT: S16_LE S32_LE      SUBFORMAT: STD MSBITS_MAX
SAMPLE_BITS: [16 32]       RATE: [32000 48000]       CHANNELS: [2 6]
```

`RATE: [32000 48000]` is the link agreeing with the ELD: **48 kHz is the
ceiling**, measured twice by independent means. There is no packed
24-bit format (`S24_3LE`); 24 significant bits travel inside `S32_LE`
frames with `MSBITS_MAX`, which is how HDA always carries them.

## 2. DLNA renderer — from the sets' own GetProtocolInfo

What the TV tells the network it accepts as a *music* file
(`docs/research/liverecon/*_GetProtocolInfo.xml`):

| Set | Audio MIME types advertised |
|---|---|
| KDL-46EX725 | `audio/L16` (LPCM), `audio/mpeg` (MP3), `audio/x-ms-wma` |
| KDL-46HX855 | the same, **plus** `audio/mp4` and `audio/x-m4a` (AAC) |

**Neither advertises FLAC**, and neither takes AC-3 as an audio-only
item. Note the asymmetry: **AAC over DLNA is HX855-only**; the 2011 set
does not list it.

`audio/L16` matters for the lossless question: **L16 is 16-bit by
definition** (RFC 2586). So the DLNA path tops out at 16-bit, 44.1 or
48 kHz, stereo. There is no 24-bit road over the network.

## 3. Audio inside a video container, on the DLNA path

Different from both lists above, and better than either (owner-verified
2026-09-18 on the EX725, re-confirmed on the HX855 — `tools/kodi-dlna-test/`).
One-minute lossless cuts of real titles, each track copied bit-exact
into MP4, served by a pass-through server:

| Track | Result on the set |
|---|---|
| AC-3 5.1 and 2.0 | plays, on-screen **"Dolby Digital"** |
| E-AC3 5.1 and **7.1** | plays, on-screen **"Dolby Digital Plus"** |
| AAC 5.1 | plays (no Dolby indicator, correctly) |
| DTS 5.1 | **silent** — video fine, no audio, on both sets |
| TrueHD 7.1 | cannot be muxed into MP4 at all; as MKV the set does not list it |

**So the set decodes Dolby Digital Plus internally, 7.1 included, even
though its HDMI input does not accept E-AC3 at all.** Decoding a file
and accepting a bitstream are different capabilities, and this set has
the first without the second.

## 4. The browser media element (our media app)

The app's player is the browser's own `<video>`/`<audio>`, which
**bypasses the DLNA sink list entirely**: AAC in MP4 plays on the EX725
through the app even though the EX725 advertises no AAC to the network.

## The owner's own library, and what reaches the set

This is not hypothetical here. A random sample of 250 of the 2,473
lossless files in the music library:

| Files | Format |
|---|---|
| 201 | 16-bit / 44.1 kHz |
| **35** | **24-bit / 96 kHz** |
| 9 | 24-bit / 44.1 kHz |
| **2** | **24-bit / 192 kHz** |
| 3 | 16-bit / 22 kHz |

So roughly **one file in five is hi-res**, and none of it can reach
these televisions intact.

**Serviio cannot deliver 24-bit to them, verified.** The `sony2011x`
renderer profile defines no `<Audio>` rules of its own, so it inherits
stock `sony2011`, whose audio target is **`lpcm`** — and Serviio's LPCM
output is `audio/L16`, the same 16-bit type the sets advertise. A
24-bit/96 kHz FLAC is therefore downconverted **twice** on its way to
the TV, in bit depth and in sample rate, silently. That is not a Serviio
defect: it is the only thing the renderer accepts.

## What this means for lossless and for FLAC

The question that prompted this page: *can FLAC be encoded to AC-3 or
E-AC3 at 24-bit / 48 kHz?*

**No, and the reason is the format, not the television.** AC-3 and E-AC3
are lossy perceptual codecs: they carry frequency coefficients, not PCM
samples, so **they have no bit-depth parameter at all**. "24-bit AC-3"
cannot exist. Both also stop at **48 kHz**, so 96 kHz is out of reach in
those codecs no matter what any display supports. Converting FLAC to
either is lossless → lossy, downhill by definition.

The lossless paths that do exist:

| Source | Lossless route | Limit |
|---|---|---|
| 16-bit/44.1 or 48 kHz FLAC | DLNA as `audio/L16`, or HDMI LPCM | exact, no conversion loss |
| **24-bit/48 kHz FLAC** | **HDMI LPCM only** (from a PC) | the network path cannot carry 24-bit |
| 24-bit/96 kHz FLAC | resample to 48 kHz first, keeping 24 bits, over HDMI | the set declares 48 kHz maximum |
| 24-bit/192 kHz FLAC | the same; 192 kHz is four times the ceiling | — |
| multichannel FLAC | AC-3 5.1 at 640 kbps | lossy, but the only multichannel route the HDMI input takes |

For a 3D film library the same logic already applies to the soundtrack:
**keep the original Dolby track and let the set decode it**, rather than
converting it. That is what [the ecosystem
notes](3d-signalling-ecosystem.md) record, and it is why a lossless
remux beats any transcode: the set does more with the original bits than
a server's "compatible" re-encode leaves it.

## The practical recipe for hi-res on these sets

The television is a 48 kHz device with 24-bit LPCM on HDMI and 16-bit
LPCM on the network. Nothing changes that. What follows from it:

- **From this PC over HDMI** (the HX855 is the workstation's monitor):
  resample 96 or 192 kHz to 48 kHz and keep 24 bits. A good resampler
  matters more than anything else in the chain here:
  `ffmpeg -i in.flac -af aresample=resampler=soxr:precision=28 -ar 48000 -sample_fmt s32 …`
  No dither is needed while staying at 24 bits.
- **Over DLNA**, accept 16-bit/48 kHz and dither properly on the way
  down rather than letting a truncation happen by accident:
  `-af aresample=resampler=soxr:precision=28:dither_method=triangular_hp -ar 48000 -sample_fmt s16`.
- **Do not convert FLAC to AC-3 or E-AC3 for quality reasons.** It is
  lossless to lossy, it cannot carry bit depth, and it cannot exceed
  48 kHz either. The one case where Dolby is the right target is
  multichannel over HDMI, where AC-3 5.1 at 640 kbps is the only
  multichannel format the input accepts at all.
- Keep expectations calibrated to the transducers: the panel's own
  speakers are the weakest link by a wide margin, and the audible
  question is what an **ARC-connected receiver** gets, not what the set
  renders internally.

## Still open

- Whether the era browser's media element will play **WAV/LPCM**, which
  would give the media app a lossless music lane (16-bit) without the
  DLNA renderer. Untested.
- Whether the sets' **ARC** output passes a decoded or bitstream Dolby
  signal to a receiver. No AVR on the verified setup.
- The 96 kHz claim: if a Sony document says these panels handle 96 kHz,
  it does not apply to this HDMI port. **The set's own ELD says 48 kHz**,
  and that is the number a source negotiates against.
