# Paste-ready post for forum.serviio.org
# (Suggested board: "User created renderer profiles" / playback problems —
# moderators feel free to move. The links at the bottom carry all files.)

**Subject:** 3D auto-detection restored on 2011–2012 BRAVIA over DLNA —
frame-packing SEI; one profile + two small tools (stock Serviio 2.5)

**Body:**

Hi all — sharing a finding and a working fix, in case it helps other era 3D
TV owners (and in case the devs want to fold any of it upstream).

**The short version:** 2011–2012 Sony BRAVIA 3D sets (tested on a
KDL-46EX725/2011 and a KDL-46HX855/2012) auto-engage 3D when the H.264
elementary stream carries a `frame_packing_arrangement` SEI (payload type
45). They ignore the Matroska `StereoMode` container tag — the only 3D flag
web rips ever carry — so every DLNA-served 3D MKV plays flat. Two breaks:
remuxes copy the ES bit-exact and drop the container tag (no SEI appears),
and the profile XML has no way to pass x264 `--frame-packing` on re-encodes.

**The fix, on stock Serviio 2.5:**

1. One renderer profile, "Sony Bravia EX7xx/HX8xx (3D Enhanced)"
   (extends stock `sony2011`, covers both lines) — MPEG-TS + AC-3 output,
   h264 re-encode targets instead of mpeg2video (which cannot carry
   frame-packing at all), no DAR squeezes.
2. An ffmpeg wrapper on the Serviio host that appends
   `-x264-params frame-packing=3|4` whenever Serviio re-encodes a
   3D-flagged input with libx264 → **on-the-fly 3D** for every re-encode
   path (proven on MPEG4 AVI, VC-1 WMV, MPEG4 MOV).
3. A lossless tool (`bravia_sei3d.py`) for the remux paths, where nothing
   can be injected in flight: inserts the 16-byte SEI before every IDR, no
   re-encode, ~0.002% size growth, idempotent, verified in-place.

**What works on the fly vs. what needs one-time pre-processing:**

- On the fly (re-encode paths, wrapper handles SEI): non-h264 codecs
  (AVI/MOV mpeg4, VC-1, msmpeg4, MJPEG, DV…), HEVC, 10-bit, >L4.1, >1920
  wide, subtitle burn-in, online feeds.
- One-time pre-processing (bit-exact remux / video-copy paths): h264 ≤L4.1
  8-bit with AC-3, and h264 with any other audio (video is copied, only
  audio transcodes). Fix once with the SEI injector, plays 3D forever.

**Possibly relevant upstream:** ffmpeg ≥ 9 auto-injects frame-packing SEI
from Matroska stereo side data on x264 encode — bundling it would make the
wrapper unnecessary. Per-profile x264 params would make the transcode-path
fix pure-profile. A remux-side SEI injection (bitstream filter on video-copy
paths) would be the general fix for every renderer that auto-detects this
way — and the signalling is standard H.264 stereoscopic syntax, not
Sony-proprietary, so other manufacturers' era 3D DLNA sets plausibly behave
the same (untested — we only have the two TVs; community test results
welcome in the GitHub discussion below).

**Disclaimer:** this investigation and tooling were produced with the
assistance of an AI coding agent (Claude Code CLI, GLM 5.3 model), under the
direction and live on-hardware verification of the TV owner. All conclusions
were confirmed empirically on the actual sets.

Everything (profile, wrapper, injector, evidence base, test log):

- Repo: https://github.com/danielcamposramos/sony-bravia-linux
- Write-up + community testing ask:
  https://github.com/danielcamposramos/sony-bravia-linux/discussions/1
- Files: `tools/serviio/user-profiles-3d.xml`,
  `tools/serviio/ffmpeg-3d-wrapper.sh`, `tools/bravia_sei3d.py`

Happy to answer questions or help people reproduce on their own sets.