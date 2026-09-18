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
| 24-bit/96 kHz FLAC | resample to 48 kHz first | the set declares 48 kHz maximum |
| multichannel FLAC | AC-3 5.1 at 640 kbps | lossy, but the only multichannel route the HDMI input takes |

For a 3D film library the same logic already applies to the soundtrack:
**keep the original Dolby track and let the set decode it**, rather than
converting it. That is what [the ecosystem
notes](3d-signalling-ecosystem.md) record, and it is why a lossless
remux beats any transcode: the set does more with the original bits than
a server's "compatible" re-encode leaves it.

## Still open

- Whether the era browser's media element will play **WAV/LPCM**, which
  would give the media app a lossless music lane (16-bit) without the
  DLNA renderer. Untested.
- Whether the sets' **ARC** output passes a decoded or bitstream Dolby
  signal to a receiver. No AVR on the verified setup.
- The 96 kHz claim: if a Sony document says these panels handle 96 kHz,
  it does not apply to this HDMI port. **The set's own ELD says 48 kHz**,
  and that is the number a source negotiates against.
