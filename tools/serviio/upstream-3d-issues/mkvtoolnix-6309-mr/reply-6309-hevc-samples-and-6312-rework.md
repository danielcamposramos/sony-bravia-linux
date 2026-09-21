<!-- BOTH POSTED 2026-09-22T00:19-20Z (owner-approved, posted by agent under his account after review):
     Context:
     - Issue #6309: mbunkus asked "do you have synthetic samples for HEVC, too? The AVC ones
       work well, basically the same two files would be nice."
     - !6312 comment 23409274: "As I've now merged the AVC changes, can you please rework this
       MR now?"
     - Public record (§9.6): the HEVC set was already uploaded to /6309/ on his server on
       2026-09-20, announced in !6312 comment 23296627. His server is upload-only (no listing
       our side), so the answer names the upload and offers re-upload if anything is missing.
     - The rework: branch rebased on merged main (1735de63f118), dropping the third commit
       (write-stereo-mode-even-when-mono) he rejected on !6311.
     Posts as Daniel, on #6309 for the samples and on !6312 for the rework. -->

=== comment for #6309 (samples question) — POSTED as [comment 23418046](https://codeberg.org/mbunkus/mkvtoolnix/issues/6309#issuecomment-23418046) ===

Yes, the HEVC set is already on your server, in the same /6309/ folder, uploaded together with the announcement on !6312.

It mirrors the AVC set: the plain x265 base streams, the injected left/right variants for side by side (type 3) and top and bottom (type 4), each wrapped to MP4 and TS, the mkvmerge v101 remuxes (SEI present, no StereoMode element — the direct before/after fixture), the README and the injector script.

x265 has no frame-packing switch (checked 3.5 and 4.1), so the SEI was injected by the script; the payload bytes were verified by hand against H.265 annex D.2.7, as the README there explains.

If anything in that listing is missing on your side just say the word and I upload it again.

=== comment for !6312 (after rework push, head now 731de6cb2) — POSTED as [comment 23418100](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6312#issuecomment-23418100) ===

Reworked and rebased onto current main (1735de63f118): the third commit is dropped, the branch is now only the HEVC change plus the cosmetics one, nothing else moved.

For completeness, what we found around the not-explicitly-set case while testing this:

- The reader probes the bitstream only when the track has no StereoMode element at all, in both the merged AVC code and this rebased HEVC one (`stereo_mode_c::unspecified` is the default the reader assigns when the element is absent). A rip carrying only the SEI — the case that matters to the TVs I work with — is detected; and explicit container values, including an explicit mono, always win.
- With the third commit dropped, `mkvmerge --stereo-mode 0:0` again does not survive a remux, exactly as in stock v101/v102 (element absent and element at default being the same statement, as you explained on !6311), and a propedit-set mono is likewise gone after one remux. Pre-existing behavior, unchanged by either MR — and under your explanation it is not expressible in Matroska anyway, so there is nothing left to fix there on my side.
- One note that may help your planned reader adjustment ("if the source StereoMode is semantically 0, still use the bitstream"): the HEVC probe sits in the same verify chain right next to the AVC one and feeds the same `v_bitstream_stereo_mode`, so your change covers both codecs automatically.

Build and the unit suites (common, merge, propedit, including the seven HEVC SEI tests) pass after the rebase.

