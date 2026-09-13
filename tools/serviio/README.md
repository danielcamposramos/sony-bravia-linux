# Serviio enhanced profile — Sony BRAVIA KDL-46EX725 / KDL-46HX855

Right-to-repair DLNA media serving for our own 2011/2012 Bravia TVs on LAN
192.168.0.x. Serviio runs on **192.168.0.60** (user `pvpgn`, target install path
`/opt/serviio`); the TVs are:

| TV | IP (live, Serviio status API) | chassis | stock profile auto-matched today |
|---|---|---|---|
| KDL-46EX725 (2011) | 192.168.0.22 | AZ2 | `sony2011` |
| KDL-46HX855 (2012) | 192.168.0.21 | AZ3 | `sony2012` |

**Files:**

- `user-profiles-3d.xml` — the deployable profile (Serviio loads it under the fixed name `config/user-profiles.xml`) (`sony2011x`, extends stock
  `sony2011`). Validates against both published XSDs
  `…/xsd/profiles/v/1.10/Profiles.xsd` and `…/xsd/profiles/v/2.4/Profiles.xsd`.

## Evidence base (nothing here is from docs alone)

1. **Live sink matrices** — `UPnP ConnectionManager:GetProtocolInfo` captured
   from both TVs (`hx855_GetProtocolInfo.xml`, `ex725_GetProtocolInfo.xml`).
   PN sets are identical; the trailing wildcard list is not (EX725 lacks
   `video/avi:*`, `video/x-msvideo:*`, `audio/mp4:*`, `audio/x-m4a:*`,
   `application/*mpegURL:*`). Key facts:
   - AVC/H.264 **only** in MPEG-TS: `AVC_TS_HD_24/50/60_AC3` (+`_T`, `_ISO`,
     `SONY.COM_PN` twins) and `AVC_TS_HD_EU`(`_T`/`_ISO`). No `AVC_TS_MP_*` PNs.
   - Audio inside TS: **AC-3 (≤640 kb/s) or MPEG-1 L2 only.** No E-AC-3, no
     TrueHD, no DTS, no AAC (the sole AAC-in-TS PN is `AVC_TS_JP_AAC_T`,
     JP market — treat as unsupported).
   - Native: MPEG-2 TS/PS (`MPEG_TS_HD/SD_*`, L2 variants), `MPEG1`, WMV
     (`WMVMED_BASE/FULL`, `WMVHIGH_FULL`, `WMVSPLL/SPML_BASE`), VC-1 in ASF
     (`VC1_ASF_AP_L1/L2_WMA`), JPEG, LPCM/MP3/WMA.
   - **No matroska line at all** (no PN, no wildcard) on either TV.
   - `video/mpeg:*`, `video/vnd.dlna.mpeg-tts:*`, `video/mp4:*`,
     `video/x-ms-wmv:*`, `video/x-ms-asf:*`, `video/x-mp2t-mphl-188:*`
     wildcards exist on both — the "half-play trap": container parses even
     when the tracks don't.
2. **Shipped stock** — `serviio-1.10.1/config/profiles.xml` and
   `serviio-2.5/config/profiles.xml` (tarballs staged in the workspace):
   the full `sony2011 → sony2012 → generic` chain the profile extends.
3. **Schema** — the current `/xsd/profiles/v/` XSD family (v/1.8, v/1.9,
   v/1.10, v/2.4). Note the non-`/v/` URLs are stale copies; several
   draft-phase "schema facts" (no h264 target, no h265/eac3 enums) came from
   those and are false on the `/v/` set.
4. **Wiki** — profile syntax (article 16) and transcoding configuration
   (article 24): inheritance semantics, `GenericTranscoding`, `maxWidth`/
   `maxHeight`, `MediaFormatProfile` direction (element = internal PN,
   `name` = PN sent to the device).
5. **Library workload** — ffprobe of the 3D folder (40 files): 38× h264
   High/Main ≤L4.1, 1× h264 High@L5.1, 1× mpeg4-ASP; audio 22× aac-only,
   16/40 with an AC-3 track, 1× eac3×4, 1× truehd+dts+dts+ac3×4; external
   `.srt`/`.forced.srt` subs; 3D SBS files are ordinary 1920×1080 h264 frames.

## Symptoms → root cause → fix

| User symptom | Root cause (evidence) | Fix |
|---|---|---|
| 1. MKVs not listed at all | Sink has zero matroska support; native resource can never sink-match; on old/community-era stock the listing also lacked a valid transcoded-PN path | Native MKV resource PN-neutralised (`name=""` remap); **every** MKV guaranteed a transcoded MPEG-TS resource whose advertised PN is sink-listed via the inherited `AVC_TS_MP_* → AVC_TS_HD_*` renames (B2/B3/B4 below cover all MKV contents) |
| 2. "HDR" files: audio, no video | Video over TV spec (10-bit h264 / HEVC / h264 >L4.1) copied or listed via wildcards while audio passes | B1 catches 10-bit/422/444 at any level, HEVC, all h264 profiles >L4.1, >1920-wide → full re-encode to h264+AC-3 |
| 3. Atmos files: video, no audio | E-AC-3/TrueHD passthrough (stock 1.10.1/2.5 even *remuxes* h264+eac3 into TS); sink decodes neither | B3: any non-AC-3 audio → AC-3 384k; the stock eac3-remux lines are shadowed |
| 4. Multi-audio + subs choice | Serviio matches/trancode's the *primary* audio track; no profile attribute selects tracks; TV has no track-selection UI | Best-effort: AC-3 policy guarantees sound from any primary track (TrueHD→AC-3 still excellent). Track *choice* is inexpressible — see the upstream gap below |

## What changed vs stock, and why (each override mapped to evidence)

1. **`extendsProfileId="sony2011"`** — inherits the whole working chain:
   `SonyDLNAMessageBuilder`, `WMPContentDirectoryDefinitionFilter`, WMP
   `DeviceDescription`, the `AVC_TS_MP_* → AVC_TS_HD_24/50/60/EU(_AC3)(_T/_ISO)`
   `MediaFormatProfile` renames (shipped 1.10.1 lines 1059–1078 / 2.5 lines
   1147–1166 — direction verified: element = internal PN, `name` = sent PN;
   every name produced is in both sink captures), Audio→LPCM and Image→YUV444
   blocks. Goal: change only what's broken, keep the browse tree intact.
2. **Own `Detection`** (union regex of stock 2011+2012 patterns) — `Detection`
   is not in the wiki's inherited-elements list, so every stock child in the
   chain redefines it; we do too. Console assignment by IP makes it
   deterministic anyway.
3. **`MATROSKA` → empty-PN remap** — belt-and-braces neutralisation of the
   native MKV resource (same trick stock uses for AVI). Honest framing: the
   sink has no matroska *mime* either, so under a MIME-strict TV filter this
   rule is a no-op — Goal-1's real lever is the guaranteed transcoded resource
   with a sink-listed PN. Kept because it is harmless and protects a
   PN-lenient filter from preferring an unplayable native resource.
4. **No `DAR` attribute anywhere** — stock sony2012's transcode targets carry
   `DAR="16:9"`, which vertically squeezes 1920×8xx cinemascope rips (forum
   t=25233; confirmed present in shipped 1.10.1/2.5 blocks S1/S4/S5,
   OnlineTranscoding block 2 and **GenericTranscoding**, which is the burn
   path). Our blocks are a superset of every inherited DAR-carrying match, so
   stock DAR never fires. The only escape is AV1 on Serviio ≥2.5 (see risks).
5. **B1 re-encodes to `targetVCodec="h264"`, not mpeg2video** — `h264` has
   been a legal `targetVCodec` in every `/v/` XSD since v/1.8 and is used by
   shipped 2.5 profiles for local mpegts transcodes; the TV accepts h264-in-TS
   (that's its only AVC path). This meets design goal 2(c) directly (the
   draft's "mpeg2video is the schema ceiling" was an artifact of the stale
   non-`/v/` XSDs). `maxWidth="1920" maxHeight="1080"` downscales 4K (these
   attributes exist since v/1.8 and force scaling when exceeded).
6. **B1 adds `c_baseline` >L4.1** (a distinct enum value the draft missed) and
   `widthGreaterThan="1920"`, `h265` explicitly (all in the v/1.10+ enums).
7. **B2 pure remux** (h264+AC-3 → TS, attributes-free) — the 3D SBS fast
   path: bit-exact, no filters, no DAR, no size caps; SPS aspect signaling
   passes through.
8. **B3 video-copy + audio→AC-3 always** — fixes the AAC-in-TS trap (sink's
   only AAC-in-TS PN is JP-market), E-AC-3/TrueHD/DTS/DTS-HD, and `mp4`
   h264 (per the sink matrix AVC exists only in TS, so native mp4 is a
   half-play risk; it transcodes instead). The mpegts/mpeg lines are
   **vCodec-scoped** so MPEG4-ASP or VC-1 video inside TS is never blindly
   copied (falls to B4) — this closes the shadow defect where an
   audio-conditional line swallowed B4's `vc1` match. `eac3`/`dts-hd` are
   legal enum values since v/1.8, so TS-sourced E-AC-3 is matched directly.
9. **B4 catch-all adds `avi`+`mpeg4` and `mp4`+`mpeg4`** — the EX725 sink has
   **no `video/avi:*` wildcard** (unlike the HX855), so a native AVI resource
   never lists on the 2011 TV; transcoding guarantees listing on both.
   Deliberately *not* caught: WMV/ASF (sink-listed `WMVMED_*` etc. on both
   TVs), MPEG-PS/VOB (`MPEG_PS_PAL/NTSC`), MPEG1 — native is correct there.
10. **B5** keeps stock's DVR-MS monotone-timestamp fix, minus its DAR.
11. **`OnlineTranscoding` override** — mirrors shipped (remux+AC-3 for online
    h264; re-encode for the rest) minus the DAR, and guards against
    community-era parents that kept AAC in the remux (unsink-listed).
12. **`GenericTranscoding` (burn path) = h264+AC-3, attributes-only, no DAR** —
    replaces stock's `mpeg2video@17M + DAR="16:9"` burn path: no squeeze during
    subtitle burn-in, and better subbed quality. (Attributes only:
    GenericTranscoding's `Video` takes no `Matches` children — it matches all
    content by default; schema-verified.)
13. **`Subtitles` = HardSubs only** (`TextBased` + `BitmapBased`,
    `RequiredFor container="*"`) — no SoftSubs (this generation has no
    external-subtitle delivery). Burn engages only when a subtitle is present
    and enabled, so sub-free files keep the native/remux paths and avoid the
    known burn penalties (slow clip start, restarts, broken seeking).
14. **`MultipleAudioTrackAware=false` explicit** (same as parent sony2011) —
    the TVs can't select tracks; also keeps the inherited sony2012
    `AudioTrackRemux` block inert.

## Effective first-match table (local files)

Blocks are evaluated top to bottom; the first matching `Video` block wins.
Child blocks precede all inherited sony2012 blocks (inherited
`forceInheritance` blocks sit at the end of the list, lowest priority).

| # | Input | Block | Output | Advertised PN (via inherited renames) | Tier |
|---|---|---|---|---|---|
| 1 | h264 >L4.1 / 10-bit / 422 / 444 / HEVC / >1920 wide | B1 | h264+AC-3 TS (re-encode, ≤1080p) | `AVC_TS_HD_24/50/60_AC3_ISO`, `AVC_TS_HD_EU_ISO` | re-encode (best possible for over-spec) |
| 2 | h264 ≤L4.1 + AC-3 (mkv/avi/flv/mp4/wtv) | B2 | **untouched remux to TS** | same | bit-exact — 3D SBS / cinemascope fast path |
| 3 | h264 ≤L4.1 + any other audio; TS/PS with aac/eac3/dts(-hd)/truehd/flac/mp3/lpcm audio | B3 | video copy + AC-3 384k | same | video bit-exact, audio re-encoded (forced: sink takes AC-3/L2 in TS only) |
| 4 | mpeg4-ASP (avi/mp4/mkv), vc1-in-TS, msmpeg4, DV, MJPEG, theora/vp8/vp9, odd containers | B4 | h264+AC-3 TS (re-encode) | same | re-encode |
| 5 | asf+mpeg2video (DVR-MS) | B5 | mpeg2→TS forced transcode, AC-3 | `MPEG_TS_*` family | fix path |
| 6 | TS h264+AC-3 / TS-PS mpeg2+AC-3/L2 / WMV-ASF / VC1-ASF / MPEG1 / VOB+AC-3 | — (falls through, native) | native | sink-listed PNs or wildcards | native (best) |
| 7 | AV1 (Serviio ≥2.5, only if header note applied) | B1 | h264+AC-3 | same | re-encode |

Library walkthrough (40-file 3D folder): 26× High@4.0+aac → B3; 10× High@4.1
(ac3 subset → B2, others → B3); 2× Main@4.0 → B2/B3; 1× High@5.1 → B1; 1×
mpeg4-ASP → B4 (AVI branch: previously invisible on the EX725); the truehd /
eac3 / dts multi-track files → B3 (video bit-exact, primary audio → AC-3);
3D SBS (h264 ≤L4.1 + ac3) → B2 untouched. Subtitled playback of any file →
GenericTranscoding burn (h264+AC-3, no DAR).

## Known gap → upstream-contribution candidate

**Audio-track selection.** Serviio matches a file on its *primary* audio
track; no attribute on `Video`/`Matches` can prefer or pin a track by codec,
language or index. The TrueHD-Atmos + DTS-HD MA + DTS + 4×AC-3 MKV therefore
lands on B3 with its TrueHD primary transcoded to AC-3 (fine quality, but the
four native AC-3 tracks would have allowed a pure B2 remux, and the user
cannot *choose* a track on this TV generation at all). The schema's existing
`AudioTrackRemux` mechanism only helps `MultipleAudioTrackAware` renderers,
which these TVs are not. Candidate contribution: an
`aCodecPriority="ac3,dca,aac"` attribute (or exposing alternate audio
resources for renderer-side selection). Workaround for the one offending
file: one-time `ffmpeg -map` remux putting an AC-3 track first → B2 fires.

## Deploy steps

1. **Confirm the Serviio version on 192.168.0.60 first** (Console > About, or
   `ls /opt/serviio/lib/serviio-core*.jar`). This profile targets **1.10.1 /
   2.x shipped stock**. On anything older (or a community-profiles pack
   install), upgrade first — `serviio-2.5-linux.tar.gz` is staged in the
   workspace — then continue. Also run
   `grep AVC_TS_MP_HD_AC3_ISO /opt/serviio/config/profiles.xml` to confirm the
   parent chain's renames are present.
2. Copy this file: `tools/serviio/user-profiles-3d.xml` →
   `/opt/serviio/config/user-profiles.xml` (owner `pvpgn`, mode 644).
3. **Fully restart the Serviio server process** (the Linux service/process —
   not just the console's UPnP restart buttons).
4. Console > Status > Devices: assign **"Sony Bravia EX7xx/HX8xx (3D Enhanced)"**
   to 192.168.0.22 (EX725) **and** 192.168.0.21 (HX855); Save. (Today they sit
   on `sony2011`/`sony2012`.)
5. Console > Settings > Subtitles: enable burn-in, set the `.srt` character
   encoding (UTF-8 or cp1252), and choose forced-subtitle behaviour for
   `.forced.srt`. These are console-level only — a wrong setting either never
   burns the forced subs or burns subs on everything.
6. Optional on Serviio ≥2.5: add `<Matches container="*" vCodec="av1"/>` to
   the B1 block (omitted here for 1.10.x schema compatibility).

## Test plan (from the TVs, after deploy)

| # | Sample | Path exercised | Expected |
|---|---|---|---|
| 1 | Any MKV from the library | Goal 1 — listing | **Appears in the browse tree on both TVs** (the original complaint) |
| 2 | 3D SBS MKV, h264 ≤L4.1 + AC-3 | B2 remux | Plays immediately (no transcode delay), seek works, 3D layout intact, aspect correct |
| 3 | 1920×8xx cinemascope MKV + AC-3 | B2 + no-DAR | No vertical squeeze (compare stock) |
| 4 | MKV h264 + AAC (the 22 aac-only files) | B3 | Video plays, audio present (AC-3 384k) |
| 5 | Atmos/TrueHD MKV | B3 | Video **and** audio (the "no audio" symptom gone) |
| 6 | "HDR" 10-bit / HEVC / High@5.1 MKV | B1 | Video **and** audio (the "no video" symptom gone); picture re-encoded h264 |
| 7 | mpeg4-ASP AVI | B4 | Listed **on the EX725** (invisible under stock there), plays |
| 8 | Native TS h264+AC-3 file / VOB+AC-3 / WMV / music MP3 / FLAC / JPEG | native + inherited audio/image | Plays natively; FLAC→LPCM; no regressions vs stock |
| 9 | 3D SBS file **with external .srt, subs enabled** | GenericTranscoding burn | Subs visible, aspect still correct (no squeeze during burn); note slower start — inherent to this TV generation |
| 10 | Same file, subs off | B2 | Fast start, seek works (burn penalties avoided) |
| 11 | `.forced.srt` file | burn + console setting | Forced subs only, correct charset |
| 12 | Online feed (optional) | OnlineTranscoding | Plays without cinema-scope squeeze |

## Remaining risks / open items before deploy

- **Installed version unconfirmed** — the whole design assumes shipped
  1.10.1/2.5 stock parents (step 1 of deploy). The profile XML itself is
  schema-valid for both, but the shadowing analysis (no DAR ever fires,
  eac3-remux shadowed) was done against those bodies.
- **AV1 on Serviio ≥2.5** falls through to the inherited stock block
  (mpeg2video + DAR). No AV1 in the library; add the one-liner from the XML
  header if desired.
- **MKV listing mechanism** — the transcoded resource's PN/mime are verified
  sink-listed; if items *still* don't list on-device, the remaining suspects
  are the Serviio version (upgrade) or the WMP definition filter — that's
  what test #1 is for.
- **h264 >L4.1 gate vs 3D rips at High@4.2** (common BD-3D level): such a file
  re-encodes via B1 (watchable, SBS structure survives). Probe the SBS files
  with ffprobe; if any is 4.2, optionally test raising B1's `high` threshold
  to 4.2 on the HX855 only — the AVC decoder may take it; the profile is
  shared by both TVs, so keep 4.1 until proven.
- **Subtitled 3D SBS / any subbed file** drops to the re-encode tier (schema
  has no "copy video + overlay subs" target); quality cost is inherent.
- **Undeterminable h264 levels** can slip past `levelGreaterThan` into B2/B3
  (same behavior as stock; H264LevelCheck left at stock default).
- **4K downscale** (B1 `maxWidth/maxHeight`) is schema-supported but untested
  on-device; library is ≤1080p today.

## Ground-truth artifacts (workspace)

`/tmp/acig-/hx855_GetProtocolInfo.xml`, `ex725_GetProtocolInfo.xml` (sink
captures) · `serviio-1.10.1/config/profiles.xml`, `serviio-2.5/config/profiles.xml`
(parent chain) · `xsd_v1.8/1.9/1.10.xsd`, `xsd_2.4.xsd` (current schema set) ·
`wiki_profiles.html`, `wiki_transcoding.html` (syntax + inheritance docs) ·
`serviio-community-profiles.xml` (old-era comparison only — **not** the
deploy target).