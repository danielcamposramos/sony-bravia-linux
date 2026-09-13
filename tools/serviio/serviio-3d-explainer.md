# 3D auto-detection on era Sony BRAVIA DLNA players — findings and a working fix

**Audience:** Serviio developers and community. We (a right-to-repair project,
own hardware, own LAN) reverse-engineered why 2011–2012 3D-capable BRAVIA
sets never auto-engage 3D over DLNA, then fixed it with **stock Serviio 2.5**
plus two small add-ons and one renderer profile. This note documents the
mechanism, the fix, and what we believe Serviio could adopt so the solution
reaches 3D-capable renderer families we cannot test.

## Hardware tested (both ends of the family)

| TV | year | chassis | line |
|---|---|---|---|
| KDL-46EX725 | 2011 | AZ2-F | EX (entry) |
| KDL-46HX855 | 2012 | AZ3 | HX (high-end) |

Identical DLNA sink PN matrices on both (captured live via
`ConnectionManager:GetProtocolInfo`): AVC only in MPEG-TS, AC-3/MPEG-1 L2 the
only audio decodable inside TS, **no Matroska PN at all**. One renderer
profile serves both; the only real silicon difference found is AVC decoder
generation (see footnote).

## The discovery

These TVs auto-engage 3D (on-screen notice, e.g. "Foi detectado um sinal 3D")
when the H.264 **elementary stream** carries a `frame_packing_arrangement`
SEI (payload type 45) — the standard stereoscopic signalling of H.264
(stereoscopic high profile family). They **do not** read the Matroska
`StereoMode` container tag — which is the only 3D flag web rips carry.

So the 3D pipeline breaks at exactly two places in any DLNA server:

1. **Remux path** (MKV → TS): the ES is copied bit-exact, the container tag
   is dropped, and no SEI exists in-file → the TV plays the SBS/T&B frames
   flat.
2. **Re-encode path**: profile XML has no way to pass x264 encoder
   parameters (`--frame-packing`), so even a freshly re-encoded 3D file
   carries no SEI → flat.

Proof was single-variable: byte-identical clips with and without the 16-byte
SEI — the TV flips only with it. Live-proven 2026-09-13 on **both** sets:
re-encode path across three codec families (MPEG4-ASP AVI, VC-1/WMV,
MPEG4 MOV full-SBS 2560×720) and lossless remux path (SEI injected in-file).

## The fix (runs today on stock Serviio 2.5)

1. **`user-profiles-3d.xml`** — one extra profile, *"Sony Bravia EX7xx/HX8xx
   (3D Enhanced)"* (id `sony2011x`, extends stock `sony2011`). Deploys as
   `config/user-profiles.xml`. Output policy MPEG-TS + AC-3; h264 re-encode
   targets (not the stock `mpeg2video`, which cannot carry frame-packing at
   all) for over-spec and catch-all paths; no `DAR="16:9"` squeezes.
2. **`ffmpeg-3d-wrapper.sh`** — installed as `/usr/local/bin/ffmpeg` in
   front of the real binary on the Serviio host. Whenever Serviio re-encodes
   with libx264 and any input is 3D-flagged (Matroska `stereo_mode` tag,
   filename tokens sbs/tb/`[3D]`), it appends
   `-x264-params frame-packing=3|4` (3 = side-by-side, 4 = top-and-bottom).
   Decisions are logged. SEI is ignorable metadata, so non-3D renderers are
   unaffected.
3. **`bravia_sei3d.py`** — for the remux path, where nothing can be injected
   in flight: losslessly inserts the x264-verbatim frame_packing SEI before
   every IDR of the existing stream (no re-encode, ~0.002% size growth),
   remuxes, restores the Matroska StereoMode tag, verifies, replaces
   in place. Idempotent — files that already carry the SEI are skipped.

## What Serviio could adopt upstream

- **Bundled ffmpeg ≥ 9** auto-injects frame-packing SEI from Matroska stereo
  side data on x264 encode — that alone would obsolete our wrapper for the
  re-encode path (our host runs system ffmpeg 6.1.6).
- **Encoder parameters per profile** — profile-XML access to x264 params
  (`frame-packing`, and we'd add `weightp/weightb`, see footnote) would turn
  the transcode-path fix into a pure-profile fix, no host-level wrapper.
- **Remux-side SEI injection** — the general fix: on video-copy/remux
  delivery paths, carry the container's stereo flag into the elementary
  stream as SEI (a bitstream filter). That covers the remux path with no
  preprocessing and zero quality cost, for *any* renderer that auto-detects
  from SEI.
- **Scope beyond Sony**: frame-packing SEI is standard H.264 signalling, not
  a Sony mechanism — we simply cannot test other manufacturers' era sets
  (Samsung/LG/Panasonic/Toshiba 3D DLNA renderers). A per-profile "inject
  stereoscopic signalling" toggle (or even a debug log line when a 3D-flagged
  file is delivered without SEI) would let the community verify on their own
  hardware quickly and map which renderer families auto-detect.

## Requirements — what works on the fly vs. what needs pre-processing

With the profile + wrapper deployed on the Serviio host:

| File situation | 3D handling |
|---|---|
| Non-h264 video (MPEG4-ASP AVI/MOV, VC-1/WMV, msmpeg4, MJPEG, DV, theora…) | **On the fly** — re-encode path; wrapper injects SEI; TV flips. Proven on AVI, WMV, MOV. |
| Over-spec h264 (HEVC, 10-bit, >L4.1, >1920 wide) | **On the fly** — re-encode + wrapper SEI. |
| Subtitle burn-in, online feeds (3D source) | **On the fly** — burn/online transcode re-encodes + wrapper SEI. |
| h264 ≤L4.1 8-bit + AC-3 audio | **Needs one-time pre-processing** — pure remux is bit-exact, nothing can be injected in flight. Run `bravia_sei3d.py` once (lossless, in-place, idempotent); plays 3D forever after. |
| h264 ≤L4.1 8-bit + other audio (aac/eac3/dts/truehd/…) | **Needs one-time pre-processing** — video is stream-copied (only audio transcodes). Same one-time SEI injection. |
| HEVC 3D, 10-bit 3D | **On the fly** (re-encoded to h264), at the CPU cost of a full encode. |

A whole library can be fixed overnight:
`bravia_sei3d.py "3D Movies" --recursive --in-place` (dry-run first with
`--dry-run`).

### Footnote — 2011 vs 2012 AVC decoder generation

Before testing other era sets, know this: the **2011** EX7xx AVC decoder
cannot decode H.264 **weighted prediction** (`weighted_pred_flag=1` /
`weighted_bipred_idc=2`): black screen, audio only. The **2012** HX8xx
decodes the same stream fine. Every 2015+ WEB-DL we sampled carries weighted
prediction, so such files need a re-encode (x264 `weightp=0:weightb=0`) for
2011-generation silicon — regardless of 3D. Don't misread that black screen
as a 3D/SEI problem: position reporting still advances and audio plays.

## Files (this repo, `tools/serviio/`)

- `user-profiles-3d.xml` — the renderer profile (single profile, both lines)
- `ffmpeg-3d-wrapper.sh` — transcode-path SEI injection wrapper
- `bravia_sei3d.py` — lossless remux-path SEI injector
- `README.md` — full evidence base and test log (sink matrices, profile
  chain analysis, live proof timeline)