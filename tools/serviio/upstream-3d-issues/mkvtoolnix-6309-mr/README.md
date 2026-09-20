# mkvtoolnix #6309 — the AVC merge request, for the owner's review

Everything needed to check the merge request before it is sent: the
maintainer's requirements and how each is met, the four texts to be
posted (commit message, NEWS.md entry, MR description, issue comment),
the test evidence, and the campaign it belongs to.

**Provenance.** The code, the tests and the four drafts below were
produced with an LLM (Claude) working as Daniel Campos Ramos's
assistant, on a design agreed with the maintainer in the issue. Daniel
reviews and edits the texts into his own voice before anything is
posted, and he is the one who sends them. English is his second
language; this is the reason the prose is drafted rather than written
from scratch. The maintainer has said he would likely want "no LLMs for
documentation", so the MR says so openly and offers to rewrite.

Branch: `avc-frame-packing-sei-stereo-mode` in `/K3D/GitHub/mkvtoolnix`
(uncommitted until Daniel approves the commit message).
Backup of the diff: `../mkvtoolnix-6309-avc-frame-packing.patch`.

---

## 1. What the maintainer asked for, and how the patch meets it

| Requirement (source) | Met by |
|---|---|
| Precedence: "command-line option wins, if not specified container-level signalling wins, if not present elementary-stream-level signalling wins, if not present default is used" (#6309, comment 23287867) | The result is applied with the existing `option_source_e::bitstream` (10), below `container` (20) and `command_line` (30); `option_with_source_c::set()` already ignores lower sources. The Matroska reader also skips probing entirely when the track has a StereoMode element. Verified: CLI 3 over container 11 over bitstream 1 gives 3; container 11 over bitstream 1 gives 11. |
| MP4 and Matroska use the framed packetizer, not the ES parser (#6309) | Detection is done in the readers, not the packetizers. |
| Must be known during identification, because the GUI runs `mkvmerge --identify` and only readers run then (#6309, comment 23288164 reply) | All four readers report `stereo_mode` in the identification output. |
| No buffering of the whole input when there is no SEI (#6309) | No packetizer-level scan at all. MP4 reads at most the first 10,000 bytes (the same bound the existing `derive_track_params_from_avc_bitstream` uses); Matroska reads the first frame only; AVC ES and MPEG TS reuse the parser pass they already make. |
| MP4: use the existing bitstream hook `derive_track_params_from_avc_bitstream` / `verify_avc_video_parameters` (#6309) | The existing Annex B path now also keeps the stereo mode; a new `derive_stereo_mode_from_avc_bitstream()` covers the normal case, where the avcC is present and the old hook never runs. |
| Matroska: "something very similar to what the MP4 reader does" (#6309) | `derive_stereo_mode_from_avc_bitstream(kax_track_t *)`, called from `verify_video_track()` using the existing `read_first_frames()`, as the DTS and TrueHD verifiers do. |
| Separate MRs for AVC and HEVC (#6309) | This MR is AVC only. The SEI helper and parser state live in `common/xyzvc` so the HEVC MR reuses them. |
| Build requirements: C++20 compiler (GCC ≥ 10), Boost ≥ 1.74 with filesystem, Ogg, Vorbis, zlib, rake, Qt ≥ 6.2 (README §2.1, configure) | Built on Debian trixie: GCC 14.2, Boost 1.83, Qt 6, `--disable-gui`. |
| NEWS.md format: "* component: … Implements #NNNN." under `# Version ?` (NEWS.md) | Draft below. |
| Commit subject style: short, lowercase component prefix (git log) | Draft below. |
| LLM stance: "you-the-human must understand all changes, their effect & be able to explain the reasoning behind why they're correct" and likely "no LLMs for documentation" (#6278) | Code walkthrough given to Daniel; the documentation texts disclose LLM drafting and offer a rewrite. |
| Keep it short: "I will outright close & ignore overly verbose & meandering issue requests" (#6278) | The MR description is kept to the change, the tests and the references; the campaign context is one short list. |

## 2. What changed (14 files, +254 −9)

| File | Change |
|---|---|
| `src/common/xyzvc/util.{h,cpp}` | `parse_frame_packing_arrangement()`: reads `frame_packing_arrangement_id` ue(v), `…_cancel_flag` u(1), `…_type` u(7), `quincunx_sampling_flag` u(1), `content_interpretation_type` u(6) and maps them to `stereo_mode_c`. Shared by AVC and HEVC because these leading fields are identical in both. |
| `src/common/xyzvc/es_parser.{h,cpp}` | `m_stereo_mode` state and `get_stereo_mode()`. |
| `src/common/avc/es_parser.cpp` | `handle_sei_nalu()` parses payload type 45, and no longer returns after a recovery point (type 6): it steps over each payload by its size and keeps walking, so a frame packing message after a recovery point in the same NAL unit is seen. |
| `src/input/r_qtmp4.{h,cpp}` | Probe of the first frames even when the avcC is present (parser fed the avcC first, then the length-prefixed samples); keep the Annex B path's result; report in identification; pass to the packetizer as bitstream-level. |
| `src/input/r_matroska.{h,cpp}` | First-frame probe only when the track has no StereoMode element; identification reports the effective value (container first); packetizer gets container then bitstream. |
| `src/input/r_avc.{h,cpp}` | Keep the probe parser's result; identification; packetizer. |
| `src/input/r_mpeg_ts.{h,cpp}` | Keep the parser's result in `new_stream_v_avc()`; identification; packetizer. |
| `tests/unit/common/xyzvc_frame_packing_arrangement.cpp` | Six new unit tests (below). |

Mapping (RFC 9559 §5.1.4.1.28.3, table 5): type 0 → 5 / 4, type 1 → 9 / 8,
type 2 → 7 / 6, type 3 → 1 / 11, type 4 → 3 / 2 (left-first / right-first,
the right-first value chosen when `content_interpretation_type` is 2).
Type 5 (temporal interleaving) has no StereoMode equivalent and is ignored,
as is a message with the cancel flag set. `content_interpretation_type` 0
(unspecified) is treated as left-first, as FFmpeg does.

## 3. Evidence

**Unit tests.** `common` 256/256 (250 existing + 6 new), `merge` 22/22,
`propedit` 24/24. New tests: every arrangement type left-first and
right-first; unspecified interpretation; non-zero arrangement IDs (3 and
254, exercising the Exp-Golomb decode); types 5, 6 and 7 give nothing;
cancel gives nothing.

**Source checks** (`rake tests:source`): no findings in any patched or new
file other than the tree-wide "no include guard line found" rule, which
every header in the project trips because it uses `#pragma once`.

**Behaviour,** before → after, on synthetic samples (the ones uploaded to
the maintainer's server for #6309, plus right-eye-first variants made by
setting `content_interpretation_type` to 2 inside the SEI and checked
against FFmpeg's independent reading, `right_left`):

| Input | Reader | Stock mkvmerge | Patched: identify | Patched: after mux |
|---|---|---|---|---|
| side by side | MP4 | absent | 1 | 1 |
| top and bottom | MP4 | absent | 3 | — |
| side by side, SEI only | Matroska | absent | 1 | 1 |
| side by side | AVC ES | — | 1 | 1 |
| side by side, right first | AVC ES | — | 11 | 11 |
| side by side | MPEG TS | — | 1 | 1 |
| side by side, right first | MPEG TS | — | 11 | 11 |
| plain 2D | MP4, AVC ES, MPEG TS, Matroska | absent | absent | absent |

Precedence: container 11 over bitstream 1 → 11 (identify and remux);
command line 3 over container 11 over bitstream 1 → 3; command line 11
over bitstream 1 on MP4 → 11.

## 4. The texts to post (drafts — Daniel edits into his own words)

### 4.1 Commit message

```
mkvmerge: AVC: set stereo mode from frame packing arrangement SEI

Parse the frame packing arrangement SEI message (payloadType 45) in the AVC ES parser and use it to set the stereo mode at bitstream level, i.e. only if neither the command line nor the container specifies one but the source contains one.

The detection happens in the readers so that the stereo mode is known during file identification: the MP4 reader probes the first frames even when the avcC is present, the Matroska reader looks at the first frame of tracks without a StereoMode element, and the AVC ES and MPEG TS readers keep the result of the parser pass they already make.

The SEI loop no longer stops at a recovery point, so a frame packing message following one in the same NAL unit is found, too.

The mapping follows RFC 9559, table 5; content_interpretation_type 2 selects the right-eye-first values. The helper lives in common/xyzvc so that HEVC support can reuse it.

Implements the AVC part of #6309.

Written with LLM assistance for the prose and the code to overcome personal difficulties and language barrier (English is not my native language - LLM drafted, I've read and edited where was due), reviewed and tested by me; see the merge request.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

### 4.2 NEWS.md entry

A new section above `## Bug fixes` under `# Version ?`:

```
## New features and enhancements

* mkvmerge: AVC/H.264: the stereo mode is now set from the frame packing
  arrangement SEI message in the video stream if neither the command line
  nor the container specifies one. This works for MP4, Matroska, AVC
  elementary stream and MPEG transport stream input and is already known
  during file identification. Implements the AVC part of #6309.
```

### 4.3 Merge request — **OPENED 2026-09-19 as [!6311](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6311)**
(body verified byte-identical against `mr-avc-body.md` after creation; title
verified byte-identical against `mr-avc-title.txt`)

**Title:** `mkvmerge: set stereo mode from the AVC frame packing arrangement SEI`

```
This implements the AVC part of #6309, following the design discussed there. HEVC will follow as a separate MR.

What it does:

- The AVC ES parser now parses the frame packing arrangement SEI
  (payloadType 45). It also keeps walking the SEI loop after a recovery
  point instead of returning, so a frame packing message after one in
  the same NAL unit is found.
- Detection is done in the readers, so the stereo mode is known during
  identification: MP4 probes the first frames even when the avcC is
  present (at most the first 10,000 bytes, as the existing avcC
  derivation does), Matroska looks at the first frame only when the
  track has no StereoMode element, and the AVC ES and MPEG TS readers
  keep the result of the parser pass they already make.
- The result is applied with option_source_e::bitstream, so the command
  line and the container keep precedence without new logic.
- Mapping per RFC 9559, table 5; content_interpretation_type 2 selects
  the right-eye-first values. Type 5 and cancel messages are ignored.
- The parser helper lives in common/xyzvc for the HEVC MR to reuse.

Testing:

- Six new unit tests in tests/unit/common/xyzvc_frame_packing_arrangement.cpp
  (all arrangement types in both view orders, unspecified interpretation,
  non-zero arrangement IDs, types without an equivalent, cancel). The
  common, merge and propedit suites pass (256, 22, 24).
- The samples from #6309 plus right-eye-first variants, cross-checked
  against FFmpeg's reading: identification and muxing give 1, 3 and 11
  as expected for MP4, Matroska, AVC ES and MPEG TS input. Plain 2D gives
  nothing. Command line over container over bitstream verified.
- Built on Debian trixie (GCC 14, Boost 1.83) without the GUI.

References:

- Rec. ITU-T H.264 | ISO/IEC 14496-10, Annex D, frame packing
  arrangement SEI message (payloadType 45)
- RFC 9559, section 5.1.4.1.28.3 (StereoMode), table 5
- FFmpeg, libavcodec/h2645_sei.c, decode_frame_packing_arrangement()

Disclamer about how this was written: English is my second language (my first is Brazilian Portuguese), so I drafted the code, this description, the commit message and the NEWS entry with an LLM, then reviewed, tested and edited them. I know you said you would likely want no LLMs for documentation. I would rather tell you than hide it, and I am happy to rewrite the texts myself, or you can replace the NEWS line with your own. I understand every change and can explain any of it. I am a registered electrical engineer in Brazil, and I stand behind the work.

This is part of a wider effort to keep stereo 3D signalling intact from encoder to display, since that SEI is the signal 3D televisions act on:

- HandBrake #8100, merged: the x264 encoder writes the SEI
- Universal Media Server #6330, merged: transcodes signal it for Sony
  3D televisions
- mpv #18490, in review: the player reads it
- reports to FFmpeg (#24530, #24531), x265 (#970), AndroidX Media3
  (#3419), Gerbera (#3937) and Kodi (#29337), and a comment on
  Jellyfin #18060

The full record, with the measurements on the televisions:
https://github.com/danielcamposramos/sony-bravia-linux
```

### 4.4 Comment on issue #6309, once the MR is open

```
The AVC part is now in !6311, implemented along the lines we discussed here. HEVC will follow as its own MR.

Thanks for pointing me to the identification path, it made the change smaller and cleaner than what I had first planned.
```

**On closing the issue.** Your habit is to close the issue citing the MR.
Here the HEVC part is still outstanding, and the maintainer asked for it
as a separate MR, so closing now would mark the request as done while half
of it remains. Recommended: post 4.4 without closing, and close with a
short line citing both MRs once the HEVC one is in. This is a judgement
call for Daniel.

## 5. The wider campaign (for the record)

| Where | What | State |
|---|---|---|
| [HandBrake #8100](https://github.com/HandBrake/HandBrake/pull/8100) | x264 encoder writes the frame packing SEI | **merged** 2026-09-16 |
| [Universal Media Server #6330](https://github.com/UniversalMediaServer/UniversalMediaServer/pull/6330) | SEI injection on transcode; Sony renderer fixes | **merged** 2026-09-19 |
| [mpv #18490](https://github.com/mpv-player/mpv/pull/18490) / [#18489](https://github.com/mpv-player/mpv/issues/18489) | player reads stream-signalled stereo | in review |
| [mkvtoolnix #6309](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309) | mkvmerge sets StereoMode from the SEI | patch accepted in principle; this MR |
| [AndroidX Media3 #3419](https://github.com/androidx/media/issues/3419) | parse the SEI in ExoPlayer | open |
| [Gerbera #3937](https://github.com/gerbera/gerbera/issues/3937) | optional SEI injection | open |
| [Kodi #29337](https://github.com/xbmc/xbmc/issues/29337) | UPnP profile mislabel (Kodi already reads the SEI) | open |
| [x265 #970](https://github.com/Multicorewareinc/x265/issues/970) | write the SEI in HEVC | open |
| [FFmpeg #24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530), [#24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531) | encoder-side signalling | open |
| [Jellyfin #18060](https://github.com/jellyfin/jellyfin/pull/18060) | comment on a Jellyfin developer's PR | commented |
| [wiz3D #32](https://github.com/effcol/wiz3D/issues/32) | hardware testing of stereo output modes | offered |
| [PhereoRoll3D #2](https://github.com/JackDesBwa/PhereoRoll3D/issues/2) | stereo photography, MPO finding | posted |
| [StaxRip #1873](https://github.com/staxrip/staxrip/issues/1873) | answer on re-encoding frame-packed 3D | commented |

## 6. Before sending — checklist for Daniel

- [ ] Read section 2 until every change makes sense to you; ask about any
      that does not.
- [ ] Edit 4.1–4.4 into your own voice.
- [ ] Fork `mbunkus/mkvtoolnix` on Codeberg.
- [ ] Decide on 4.4: comment only, or close.
- [ ] Tell me to commit with your final message and push, or push yourself.

---

# The HEVC twin merge request (same review rules)

Branch: `hevc-frame-packing-sei-stereo-mode` in `/K3D/GitHub/mkvtoolnix`,
**committed 2026-09-19 as `48cec25cf`** with Daniel's chosen trailer line
(Claude Opus 5 and Kimi-K3 over ollama inside Claude Code).
Built on top of the AVC commit (`1d430d281`); the AVC MR carries the shared
helper, this one only wires HEVC into it.

## 7. What changed (12 files, +119 −3, plus one new test file)

| File | Change |
|---|---|
| `src/common/hevc/util.{h,cpp}` | `parse_sei()` takes an optional `stereo_mode` out-parameter. When it sees payload type 45 (frame packing arrangement) it reads the payload into a bit reader for the shared `xyzvc` helper, then rewinds the byte reader so the existing user-data handling still walks the same NAL unit. |
| `src/common/hevc/es_parser.cpp` | The one live `parse_sei()` call now passes the base-class state, `&m_stereo_mode`. |
| `src/input/r_hevc.{h,cpp}` | Raw ES reader: keep the probe parser's result, report it in identification, pass to the packetizer as bitstream-level. |
| `src/input/r_mpeg_ts.cpp` | `new_stream_v_hevc()` keeps the parser's result; the two HEVC packetizer creations apply it. Identification was already generic from the AVC commit. |
| `src/input/r_qtmp4.{h,cpp}` | `derive_stereo_mode_from_hevc_bitstream()`: feeds the hvcC through the parser (configuration record, then at most the first 10,000 bytes as length-prefixed samples) when the stream is not Annex B, exactly the AVC twin. Both HEVC packetizer creations apply the result. |
| `src/input/r_matroska.{h,cpp}` | `derive_stereo_mode_from_hevc_bitstream(kax_track_t *)`: first-frame probe only when the track has no StereoMode element, mirroring the AVC twin; called from `verify_video_track()` for `V_MPEGH/ISO/HEVC`. |
| `NEWS.md` | Twin line under `## New features and enhancements`, ending "Implements the HEVC part of #6309." |
| `tests/unit/common/hevc_sei_frame_packing.cpp` | Seven new unit tests (below). |

**One quirk worth knowing when reviewing.** `hevcc_c::unpack()` fills
`m_size_nalu_minus_one`, not `m_nalu_size_length`: the length-prefixed
parser must be called with `m_size_nalu_minus_one + 1` as the NAL length
size. Using the other member passes 0 and the parser loop never advances.
Both HEVC derivation sites use the correct member. (Found the hard way: an
infinite loop in `mkvmerge -J` on the first MP4 run, fixed and covered by
the matrix below.)

## 8. Evidence

**Unit tests.** `common` 263/263 (256 with the AVC part + 7 new),
`merge` 22/22, `propedit` 24/24. New tests: detection after other payloads
in the same NAL unit; top-and-bottom right-first via
`content_interpretation_type` 2; cancel gives nothing; type 5 (temporal)
has no equivalent; no frame packing payload gives nothing; the first
message wins; a suffix SEI NAL unit is not treated as a prefix one.

**Source checks** (`rake tests:source`): no findings in any patched or new
file other than the tree-wide "no include guard line found" rule (495 hits
across untouched headers as well; the tree uses `#pragma once`).

**Sample provenance** (stated plainly, because it differs from the AVC
side). x265 has no frame-packing option at all: checked on 3.5 (Debian
testing) and 4.1 (Debian trixie), both answer "Unknown option". So the
HEVC companions are plain x265 elementary streams with a spec-exact SEI
injected before the first IRAP by a small script
(`hevc_inject_frame_packing.py`, kept with the samples). The injected
payload bytes were verified by hand against Rec. ITU-T H.265, annex D.2.7
(e.g. side by side, frame0 = left view: `81 81 2C 02 80`), and FFmpeg's
independent reading was not usable as an oracle for HEVC, which is exactly
why the bytes were checked directly. Generation commands are in the
samples' README.txt.

**Behaviour** (patched build, 19/19 identification + 19/19 remux):

| Input | ES (.h265) | MP4 | MPEG TS | Matroska (no element) |
|---|---|---|---|---|
| side by side, left first | 1 | 1 | 1 | 1 |
| side by side, right first | 11 | 11 | 11 | 11 |
| top and bottom, left first | 3 | 3 | 3 | 3 |
| top and bottom, right first | 2 | 2 | 2 | 2 |
| plain 2D | — | absent | absent | absent |

"Matroska (no element)" means fixtures written by stock mkvmerge v101,
which carry the SEI but no StereoMode element: the case the maintainer
asked to be derived. Remux sets the element to the same value in all
sixteen cases; 2D stays absent.

**Precedence** (same `option_with_source_c` rule as AVC, no new logic):

- Container over bitstream: mkvpropedit stereo-mode 11 on a remuxed
  side-by-side file (element 1, SEI still in the stream) → identify 11.
- Command line over bitstream: `--stereo-mode 0:side_by_side_right_first`
  → element 11 although the SEI says 1.
- Command line `mono`: no element is written, identical to stock v101,
  because libmatroska omits an element whose value equals the Matroska
  default (0 = mono). The bitstream-derived value does not leak through.

## 9. The texts to post (HEVC drafts — Daniel edits)

### 9.1 Commit message

```
mkvmerge: HEVC: set stereo mode from frame packing arrangement SEI

Parse the frame packing arrangement SEI message (payloadType 45) in the HEVC SEI reader and use it to set the stereo mode at bitstream level, i.e. only if neither the command line nor the container specifies one but the source contains one.

The detection happens in the readers so that the stereo mode is known during file identification: the MP4 reader probes the first frames even when the hvcC is present, the Matroska reader looks at the first frame of tracks without a StereoMode element, and the HEVC ES and MPEG TS readers keep the result of the parser pass they already make.

The mapping reuses the shared AVC/HEVC helper introduced with the AVC part and follows RFC 9559, table 5; content_interpretation_type 2 selects the right-eye-first values.

Implements the HEVC part of #6309.

Written with LLM assistance for the prose and the code to overcome personal difficulties and language barrier (English is not my native language - LLM drafted, I've read and edited where was due), reviewed and tested by me; see the merge request.

Co-Authored-By: Claude Opus 5 and Kimi-K3 over ollama inside Claude Code <noreply@anthropic.com>
```

(this is the committed message; the trailer was Daniel's choice.)

### 9.2 NEWS.md entry

Already in the tree, the twin line shown in the diff of section 7
(identical wording to the AVC line, with HEVC/H.265 in place of AVC/H.264).

### 9.3 Merge request — **OPENED 2026-09-19 as [!6312](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6312)**
(body verified byte-identical against `mr-hevc-body.md`; style-reviewed before opening: all hard wraps joined, no em dashes, `!NNNN` filled with !6311)

**Title:** `mkvmerge: set stereo mode from the HEVC frame packing arrangement SEI`

```
This implements the HEVC part of #6309, following the same design as the AVC MR (!NNNN): detection in the readers so the stereo mode is known during identification, and the result applied at bitstream level so the container and the command line keep precedence.

What it does:

- The HEVC SEI walk now also reads the frame packing arrangement message
  (payloadType 45) using the shared AVC/HEVC helper, then rewinds so the
  existing user-data handling is unchanged.
- MP4 probes the first frames even when the hvcC is present (at most the
  first 10,000 bytes, as the existing avcC derivation does), Matroska
  looks at the first frame only when the track has no StereoMode element,
  and the HEVC ES and MPEG TS readers keep the result of the parser pass
  they already make.
- One implementation note: with a configuration record the parser must be
  fed with m_size_nalu_minus_one + 1 as the NAL length size, because
  hevcc_c::unpack() does not fill m_nalu_size_length. Both new call sites
  do this.

Testing:

- Seven new unit tests in tests/unit/common/hevc_sei_frame_packing.cpp
  (prefix SEI parsing, right-eye-first selection, cancel, the arrangement
  type without a StereoMode equivalent, suffix SEI rejection). The common,
  merge and propedit suites pass (263, 22, 24).
- HEVC companions for all four containers (ES, MP4, MPEG TS, Matroska
  without an element): identification and muxing give 1, 2, 3 and 11
  exactly per RFC 9559 table 5, and plain 2D gives nothing.
- Command line over container over bitstream verified; "mono" writes no
  element, identical to the released version, because that is the Matroska
  default value.
- Built on Debian trixie (GCC 14, Boost 1.83) without the GUI.

Sample provenance: x265 does not offer frame packing (checked 3.5 and
4.1), so the samples carry a spec-exact SEI injected by a script, and the
payload bytes were verified by hand against Rec. ITU-T H.265, annex D.2.7.
I can upload the set (with the script and README) to your FTP area like
the AVC ones if you want to try them.

References:

- Rec. ITU-T H.265 | ISO/IEC 23008-2, annex D, frame packing arrangement
  SEI message (payloadType 45)
- RFC 9559, section 5.1.4.1.28.3 (StereoMode), table 5

Same disclaimer as the AVC MR: LLM-assisted drafting, reviewed, tested and understood by me; happy to rewrite the documentation texts if you prefer.
```

### 9.4 Closing comment on issue #6309 — **POSTED 2026-09-19 as [comment 23294641](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309#issuecomment-23294641), issue CLOSED** (body verified byte-identical server-side)

```
The HEVC part is now in !6312, the twin of the AVC one. With both parts in, the issue looks complete to me, so I am closing it: AVC in !6311, HEVC in !6312, both following the design we discussed here.

Thanks again for the guidance, in particular for pointing me at the identification path.
```

## 9.5 Stereo-family triage comment on !6311 — **POSTED 2026-09-20 as [comment 23296426](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6311#issuecomment-23296426)**

Full sweep of all 35 open issues in mbunkus/mkvtoolnix (enumerated via API, then body-verified) for the stereo 3D family. Result posted to mbunkus on the MR he is reviewing:

```
Triage note so you do not have to hunt for overlap yourself: I went through every open issue in this tracker in the stereo 3D family.

Closed by !6311 + !6312:

- #6309, my own report, already closed. No other open issue is affected.

Open but not closed by these MRs:

- #2709, raw H.264 streams with MVC sub-views (mvcC). Different mechanism: MVC carries a second coded view in the bitstream, while the frame-packing SEI is pure metadata about how one view is spatially arranged. These MRs do not touch MVC handling, so #2709 stays open and unaffected. Both read the same ES parser streams but look for orthogonal data, so a future MVC implementation should not conflict with this code.

Closed history in the same family, none of them about the frame-packing SEI path: #1106 (SSIF/MVC feature request), #1458 (left/right eye swap), #2444 (eye flipping in 3D MVC), #625 (StereoMode=0 vs EBML v2/v3 headers).
```

Characterization evidence for the four closed ones: #1458 = user expected L/R swap to change pixels, not just the metadata flag (closed as designed); #2444 = same theme via propedit on 3D MVC files (closed); #1106 = SSIF/MVC Blu-ray feature request, sibling of #2709 (closed); #625 = StereoMode=0 elided vs EBML header version (closed).

## 9.6 HEVC samples-uploaded comment on !6312 — **POSTED 2026-09-20 as [comment 23296627](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6312#issuecomment-23296627)** (body verified byte-identical server-side)

The !6312 body offered "I can upload the set … to your FTP area like the AVC ones if you want"; Daniel uploaded the HEVC set to `/6309/` on the maintainer's SFTP server, and this comment closes the loop. Text reviewed by Daniel ("post as is") before posting:

```
The HEVC companion set from the body is uploaded, same place as the AVC ones: /6309/ on your server.
It is the plain x265 base streams, the injected left/right variants for side by side (type 3) and top and bottom (type 4), each wrapped to MP4 and TS, the remuxes made with mkvmerge v101 (SEI present, no StereoMode element — the direct before/after fixture), the README and the injector script.
The README covers the provenance from the body, including the x265 frame-packing gap and the byte check against H.265 D.2.7.
```

## 9.7 Review round 1 on !6311 — **ANSWERED 2026-09-20 as [comment 23323531](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6311#issuecomment-23323531)** (body verified byte-identical server-side, 6092 bytes)

mbunkus reviewed on 2026-09-20 in two rounds (`REQUEST_CHANGES` 1892761 at
13:56 with 5 inline comments, 1893043 at 14:50 with 2) and reopened #6309
with "The MRs haven't been merged yet, so let's keep it open until then"
([comment 23316670](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309#issuecomment-23316670)).
**He raised nothing about AI assistance** — every comment was technical,
despite the commits carrying the `Co-Authored-By: Claude Opus 5` trailer and
the LLM-assistance disclosure paragraph. He opened with "Most of it is
exactly the way I'd want it".

| # | Request | Resolution |
|---|---|---|
| [23316856](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6311#issuecomment-23316856) | static 2D array over the `case` cascade | `s_stereo_modes[type][right_first]`, bounds-checked, in his `static std::array<…> const s_…` idiom |
| [23317144](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6311#issuecomment-23317144) | `verify_avc_video_track` for family consistency | renamed, returns `bool`, dispatched from the same `if`/`else` chain as Theora |
| [23317252](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6311#issuecomment-23317252) | alignment + helper before the `info.add` cascade | `?` both at col 74, `:` under `=` at col 21, values at col 76; helper hoisted above the cascade |
| [23317336](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6311#issuecomment-23317336) | shared video handling, not codec-specific | new `qtmp4_demuxer_c::set_packetizer_stereo_mode()` beside `set_packetizer_display_dimensions()`/`_color_properties()` |
| [23317711](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6311#issuecomment-23317711) | fold into `derive_track_params_from_avc_bitstream` | merged, one read + one parse; `derive_stereo_mode_from_avc_bitstream` deleted |
| [23319547](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6311#issuecomment-23319547) | align the `=` (style-only commit) | separate `cosmetics: alignment` commit `1735de63f`, all four `=` at col 16 |
| [23319652](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6311#issuecomment-23319652) | generic in `create_packetizer` | moved to the tail before `show_packetizer_info`; covers every codec |

**The one request that could not be taken literally**, and why it was
measured rather than argued. mbunkus expected `verify_avc_video_parameters`
to need no changes. Built exactly that way (byte-identical to `origin/main`)
it breaks MP4 entirely: `derive_track_params_from_avc_bitstream()` has a
single call site, in the branch reached only when the avcC is *missing*, so
an ordinary MP4 never reaches the merged function. Measured: all four MP4
identification cases report no stereo mode and the remux writes **no**
`StereoMode` element. A first run appeared to show "remux ok" — that was a
false positive, because re-identifying the *Matroska* output triggers the
Matroska probe, a different path. Dropping the early `return true` is the
whole change; 22/22 with it.

**Third commit, `46a12c6fb` — a pre-existing bug found while testing.**
`mkvmerge --stereo-mode 0:0` never recorded the choice: StereoMode's default
is 0, mkvmerge renders track headers without defaults, so the element was
dropped and the track read back as unset. `mkvpropedit --set stereo-mode=0`
*does* write it, so the two tools disagreed about whether mono is
expressible. **Confirmed pre-existing against stock Debian v101.0** (same
behaviour, no patch involved) — this MR only makes the consequence visible,
since the SEI now fills the void and an explicit mono comes back as side by
side. Also means a propedit-set mono does not survive one remux. Fixed with
libebml's `ForceNoDefault()` via a `kax_video_stereo_mode_c` subclass,
following the existing `kax_block_add_id_c` precedent, so no other default
element is affected. After it: mono round-trips through three remuxes, plain
2D files gain no element, SEI-derived and command-line values unchanged.
Kept as its own commit so it can be dropped or split into a separate MR.

**Precedence flip investigated and rejected on evidence, not deference.**
Whether the SEI should outrank the container was tested; `mkvpropedit`-set
mono is a deliberate user statement that a flip would silently override, and
the case that matters (a rip with the SEI and no StereoMode element) already
works under mbunkus's ordering. RFC 9559 §5.1.4.1.28.3 defines StereoMode
with default 0 and is **silent** on container-versus-bitstream precedence
(verified by fetching the RFC), so no spec supports a "SEI wins" claim —
never assert one. See [[sei-discovery-came-from-daniel]].

**Verification:** 23/23 behavioural (identification + remux across MP4,
Matroska, AVC ES, MPEG TS; left-first and right-first; 2D reporting nothing;
command line > container > bitstream; plus the mono round-trip that used to
fail) and 256 unit tests, on a clean AVC-only tree. `rake tests:source` has
no findings attributable to the change: its 495 hits are a tree-wide
`#pragma once` false positive that also flags untouched upstream files.

Posted body, verbatim:

```
All seven points are in, force-pushed as two commits.

The static two dimensional array replaces the case cascade in `parse_frame_packing_arrangement`, indexed by `frame_packing_arrangement_type` and then by whether frame 0 is the right view. The types without a StereoMode equivalent are simply not listed and a bounds check catches them. Much more slim and simple, thank you for the tip.

`verify_avc_video_track` now exists in the Matroska reader and is dispatched from the same `if`/`else` chain as the other codec types, next to `verify_theora_video_track`. It returns `bool` like the rest of the family, always true for now, since a missing SEI is not a track error.

The identification helper is set before the whole `info.add`/`info.set` cascade, so the cascade is intact again. The `?` are aligned, the `:` sit under the `=`, and the last value lines up with the other two. It really makes things easier to spot on code.

The MP4 packetizer hookup moved out of `create_video_packetizer_avc` into `qtmp4_demuxer_c::set_packetizer_stereo_mode`, called right after `set_packetizer_display_dimensions` and `set_packetizer_color_properties` in `create_packetizer`, in the same shape as the other shared video track properties. Neat design!

`derive_track_params_from_avc_bitstream` absorbed the stereo mode detection, so the bitstream is read and parsed once and `derive_stereo_mode_from_avc_bitstream` is gone. No twice the work anymore.

About `verify_avc_video_parameters` needing no changes, I built it your way first and measured it, so you do not have to spend time on it yourself. It does not hold, and the reason is narrow. That function is the only caller of `derive_track_params_from_avc_bitstream`, and it calls it in the second branch, which is reached only when the avcC is missing. With the early `return true` still in place, an ordinary MP4 that has an avcC never reaches the merged function, so nothing ever parses the bitstream. On that build all four MP4 identification cases report no stereo mode and the remux writes no `StereoMode` element at all, while the AVC elementary stream, MPEG TS and Matroska cases stay correct because they do not pass through this function.

Dropping that early branch is the entire change. The function is now the `derive_track_params_from_avc_bitstream` call plus the existing warning, which keeps the avcC decision inside the function that actually owns it. With that, the suite is 22 of 22 again.

The MPEG TS hookup is at the end of `create_packetizer`, just before `show_packetizer_info`, so it covers every codec.

The `=` alignment is a separate `cosmetics: alignment` commit, as you suggested.

On the HEVC side you are right that this makes the corresponding TS change unnecessary there, and the same turns out to be true of both MP4 hookups. I will rebase !6312 onto this once the shape here is settled rather than now, so I am not chasing a moving target.

While testing I went after the corner where the container and the bitstream disagree, and it turned into a fix rather than a question, so there is now a third commit.

`mkvmerge --stereo-mode 0:0` never actually recorded the choice. StereoMode's default value is 0, mkvmerge renders its track headers without defaults, so the element was dropped and the track read back as if nothing had been said about the stereo mode. mkvpropedit does not behave that way, because it only ever holds the elements that were really in the file, so `mkvpropedit --edit track:v1 --set stereo-mode=0` does write it. The two tools disagreed about whether mono can be expressed at all.

This merge request does not introduce that. I checked against the stock v101.0 packaged by Debian and it behaves identically, with no patch involved. What the SEI detection changes is the consequence. Before, a discarded mono left the track merely unset, and now the bitstream fills the gap, so an explicit mono comes back as side by side on the next read. The same thing happens to a mono set with mkvpropedit: it does not survive a single remux, because mkvmerge cannot write it back.

The fix takes the default away from that one element, the same way `kax_block_add_id_c` already does for the block addition ID, so nothing else in the headers changes. After it: `--stereo-mode 0:0` writes mono and still reads back as mono after three remux rounds, an ordinary 2D file gains no StereoMode element at all, and the SEI derived and command line values are unaffected.

It is a separate commit on purpose. If you would rather have it as its own merge request, or not at all, drop that one commit and the rest still stands.

I did also look at whether the bitstream should simply outrank the container for this property, since on the televisions this came from the SEI is the only stereo signal the sets act on. I am not proposing it. A mono set with mkvpropedit is a deliberate statement by the user and flipping the order would quietly override it, and the case that actually matters, a rip carrying the SEI with no StereoMode element, already works under your ordering. The real problem in that corner was the one above, that mkvmerge could not record the choice in the first place.

One last thing worth putting on the record about why this SEI is worth reading at all. For side by side and top and bottom the frame geometry corroborates it: split the frame the way the arrangement says, compare the per eye aspect against the container, and you get full against half. For checkerboard and the two interleaved modes it does not corroborate anything, because both eyes occupy the same pixels and the frame is indistinguishable from 2D by any measurement you can make on it. For those three arrangements the SEI is not the best signal, it is the only one that exists.

Verified on the patched build, 23 of 23: identification and remux across MP4, Matroska, AVC elementary stream and MPEG TS, left first and right first, 2D files reporting nothing, command line over container over bitstream, and the mono round trip that used to fail. The 256 unit tests pass, including the six for the mapping helper.
```

## 10. HEVC checklist for Daniel

- [x] Commit trailer chosen by Daniel; committed as `48cec25cf`.
- [x] Fork `capitain_jack/mkvtoolnix` created; both branches pushed via
      SSH key `SparkyLinux2026` (2026-09-19). PR creation URLs:
      AVC `https://codeberg.org/mbunkus/mkvtoolnix/compare/main...capitain_jack:avc-frame-packing-sei-stereo-mode`,
      HEVC `.../compare/main...capitain_jack:hevc-frame-packing-sei-stereo-mode`.
- [ ] Read section 7 until every change makes sense to you (the
      hevcc_c quirk is the one non-obvious part).
- [ ] Edit 9.3–9.4 into your own voice (9.1 and 9.2 are committed).
- [x] Both MRs open: AVC !6311, HEVC !6312 (2026-09-19).
- [x] Closing comment posted and issue #6309 closed by API on Daniel's
      explicit instruction (2026-09-19).
- [x] Maintainer edits enabled on both MRs by Daniel (the API create call
      missed `allow_maintainer_edit`; verified True on both 2026-09-19).
