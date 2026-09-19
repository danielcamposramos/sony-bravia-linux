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

Parse the frame packing arrangement SEI message (payloadType 45) in
the AVC ES parser and use it to set the stereo mode at bitstream
level, i.e. only if neither the command line nor the container
specifies one.

The detection happens in the readers so that the stereo mode is known
during file identification: the MP4 reader probes the first frames
even when the avcC is present, the Matroska reader looks at the first
frame of tracks without a StereoMode element, and the AVC ES and MPEG
TS readers keep the result of the parser pass they already make.

The SEI loop no longer stops at a recovery point, so a frame packing
message following one in the same NAL unit is found, too.

The mapping follows RFC 9559, table 5; content_interpretation_type 2
selects the right-eye-first values. The helper lives in common/xyzvc
so that HEVC support can reuse it.

Implements the AVC part of #6309.

Written with LLM assistance for the prose and the code, reviewed and
tested by me; see the merge request.

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

### 4.3 Merge request

**Title:** `mkvmerge: set stereo mode from the AVC frame packing arrangement SEI`

```
This implements the AVC part of #6309, following the design discussed
there. HEVC will follow as a separate MR.

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

About how this was written: English is my second language (my first is
Brazilian Portuguese), so I drafted the code, this description, the
commit message and the NEWS entry with an LLM, then reviewed, tested
and edited them. I know you said you would likely want no LLMs for
documentation. I would rather tell you than hide it, and I am happy to
rewrite the texts myself, or you can replace the NEWS line with your
own. I understand every change and can explain any of it. I am a
registered electrical engineer in Brazil, and I stand behind the work.

This is part of a wider effort to keep stereo 3D signalling intact
from encoder to display, since that SEI is the signal 3D televisions
act on:

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
The AVC part is now in !NNNN, implemented along the lines we discussed
here. HEVC will follow as its own MR.

Thanks for pointing me to the identification path, it made the change
smaller and cleaner than what I had first planned.
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
