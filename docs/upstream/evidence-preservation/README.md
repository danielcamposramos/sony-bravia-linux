# Deep Color evidence preservation inventory

Snapshot audited: 2026-09-28. Source location:
`/K3D/temp/dual-upstream-preserve-2026-09-22/`.

This directory commits an inventory and digests, **not the artifact bytes**.
`/K3D/temp` is an expendable local staging area: it is neither immutable nor
publicly available. The artifacts should later be copied, without changing the
bytes, to a public immutable archive and the archive URL added here. Until then,
the committed SHA-256 values can detect change or loss but cannot recover the
files.

## Origin and series map

The 2026-09-22 dual-upstream handoff records that Kimi K3 mirrored the working
trees from boot-volatile `/tmp` into the source location above. It identifies
drm-misc-next `73ef663c75688168e31dbe9c585b939be410a945` as the nouveau
prerequisite and NVIDIA 615.71.09
`61dcc93722ecb418bb5f2e00923f05b4b8051dd1` as the proprietary-open base.

| Artifact group | Contents and provenance | Verification on 2026-09-28 |
|---|---|---|
| `nouveau-deep-color-branch.bundle` (6,205 B) | Initial three-commit nouveau branch; head `a7315e24` | `git bundle verify` passed with prerequisite `73ef663c`; patch IDs match `nouveau-deep-color-series-v2/` |
| `nouveau-deep-color-series-v2/` (24,631 B total) | Cover plus initial three-patch series from the same branch | All three mails parsed and replayed cleanly on `73ef663c` |
| `nouveau-deep-color-series-v2-benched/` (28,239 B total) | Cover plus post-run25/run26 three-patch revision; commits `ec385c04`, `5f86153c`, `a01857bb` | All three mails parsed and replayed cleanly on `73ef663c` |
| `nouveau-deepcolor-v2-plus-colorformat.bundle` (23,335 B) | Sent deep-colour v2 head `c3dddeb0` and colour-format head `b8299fc5` | `git bundle verify` passed; stable patch IDs match both `series-final/` series |
| `series-final/nouveau-deep-color-series-v2-final/` (29,287 B total) | Sent v2 cover and three patches | Three patch IDs match bundle commits `477df2bd`, `1f9376eb`, `c3dddeb0` |
| `series-final/nouveau-hdmi-color-format-series/` (58,364 B total) | Sent cover and six-patch follow-on | Six patch IDs match bundle commits `129dbaee` through `b8299fc5` |
| `nouveau-deepcolor-v3-plus-colorformat-v2.bundle` (23,414 B) | Held correction revisions; heads `0d1a9489` and `27e91e45` | `git bundle verify` passed with prerequisite `73ef663c`; commit history and stable patch IDs inspected |
| `nvidia-fix-hdmi-deep-color-default.bundle` (1,076 B) | NVIDIA one-line default-cap branch, head `bbfc6708` | `git bundle verify` passed with prerequisite `61dcc937`; patch ID matches the preserved diff |
| `nvidia-default-cap.uncommitted.diff` (690 B) | Pre-commit copy of the NVIDIA 10-to-12 default change | Parsed by `git patch-id`; matches `bbfc6708` |
| `nvidia-open-base.txt` (46 B) | Base/tag and branch note | Content inspected: `61dcc93`, `615.71.09`, branch name |
| `nouveau-drm-misc.status.txt` (0 B) | Empty status capture | Digest is the SHA-256 of an empty file; it carries no status evidence |

Exact per-file sizes and SHA-256 values follow. `SHA256SUMS` uses paths
relative to the source location and is directly usable there with
`sha256sum -c`.

| Relative file | Bytes | SHA-256 |
|---|---:|---|
| `nouveau-deep-color-branch.bundle` | 6,205 | `d395516611e67630358e359a518466027a9627002c094aa9404fc43e246f96c1` |
| `nouveau-deep-color-series-v2-benched/v2-0000-cover-letter.patch` | 6,790 | `c65f46aa3a5c8c83d5e8a6b6b67f6551b589289052f05465fda3938e1c3569d8` |
| `nouveau-deep-color-series-v2-benched/v2-0001-drm-nouveau-select-HDMI-deep-color-link-depth.patch` | 8,317 | `1f1cdc86b3b056a0a3701e62716827ec48875f716ecdcfce14a53f480ec2b531` |
| `nouveau-deep-color-series-v2-benched/v2-0002-drm-nouveau-pass-HDMI-GCP-deep-color-state-throug.patch` | 8,642 | `d45cffcd9941727b360a86e6666c5642cc6cee33c198944076aafefd04ac3722` |
| `nouveau-deep-color-series-v2-benched/v2-0003-drm-nouveau-program-HDMI-deep-color-GCP-fields.patch` | 4,490 | `7d338be1c3d267269885495223e84903ce5b062b36652cb775cb2df8308d2a64` |
| `nouveau-deep-color-series-v2/0000-cover-letter.patch` | 4,038 | `d159bfd377d83d9262cdb664dad09b3a8ea10d764f3e815d36bd49539646442d` |
| `nouveau-deep-color-series-v2/0001-drm-nouveau-select-HDMI-deep-color-link-depth.patch` | 8,266 | `b5dc320040943b7b416cb1170bcfa6a03892358ffde65a9d26c20028e0be096b` |
| `nouveau-deep-color-series-v2/0002-drm-nouveau-pass-HDMI-GCP-deep-color-state-through-N.patch` | 7,864 | `7f328cb9026038b1b248af797844cfa7dca6185785724a8a38e8f760351f063f` |
| `nouveau-deep-color-series-v2/0003-drm-nouveau-program-HDMI-deep-color-GCP-fields.patch` | 4,463 | `72f4887075e17227e4388ab0a65eb7a3bde91db79aa3348841aa69971c174d1f` |
| `nouveau-deepcolor-v2-plus-colorformat.bundle` | 23,335 | `cf27db08bec09b6772d8fcecdee942f16f13fd4f10eacbaa365c051e4847127d` |
| `nouveau-deepcolor-v3-plus-colorformat-v2.bundle` | 23,414 | `acc83d7ba7e61b4b266657f23f0ec6a85b74bab7dc6ab2b395ced7c41b243126` |
| `nouveau-drm-misc.status.txt` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `nvidia-default-cap.uncommitted.diff` | 690 | `08cc80ac5925b00b3da92934db3446ba3682c78f30bb455fdaf2ca1b4536b5dd` |
| `nvidia-fix-hdmi-deep-color-default.bundle` | 1,076 | `9cf072f625d13edb7813b38fadd072a255fcd54ab8d998f3740510ac22439cdb` |
| `nvidia-open-base.txt` | 46 | `e1386bf4abd187526aa87768a736eeb5dec20c33d5b334fc50971b7e71853e77` |
| `series-final/nouveau-deep-color-series-v2-final/v2-0000-cover-letter.patch` | 7,341 | `5d84c4574b065f4313e4a1247591c35e35e5b48f66838b5368067a32451c142c` |
| `series-final/nouveau-deep-color-series-v2-final/v2-0001-drm-nouveau-select-HDMI-deep-color-link-depth.patch` | 8,799 | `58a8ae8977c26aa5e42d6b31c309a9524cca76b3a2fc7f0a0b56637918d9479b` |
| `series-final/nouveau-deep-color-series-v2-final/v2-0002-drm-nouveau-pass-HDMI-GCP-deep-color-state-throug.patch` | 8,657 | `5d7dcde636e82894aef3752846047a6af5c5355dbd63b123c246066d3b4db74a` |
| `series-final/nouveau-deep-color-series-v2-final/v2-0003-drm-nouveau-program-HDMI-deep-color-GCP-fields.patch` | 4,490 | `8efdc0720ee2ad6c273e47153a3db23ec18a9b6cf7397d4034edd5235fe4b355` |
| `series-final/nouveau-hdmi-color-format-series/0000-cover-letter.patch` | 5,576 | `ece3f6fd1de87ac71d7f7221fa4406f078d0e84569d9dd331c1406afed6bbfbe` |
| `series-final/nouveau-hdmi-color-format-series/0001-drm-nouveau-add-NVC57D-output-CSC-and-clamp-range-me.patch` | 5,363 | `c6bfc651b17c3d958c9b069719cfe5b9e1c6cee64dc36be1423874acfbd640f1` |
| `series-final/nouveau-hdmi-color-format-series/0002-drm-nouveau-program-head-output-conversion-for-limit.patch` | 6,970 | `0cdefb3f5c854963402530d21faf59504196fc11bcd7be81aba592295416b9a0` |
| `series-final/nouveau-hdmi-color-format-series/0003-drm-nouveau-add-the-Broadcast-RGB-property-for-HDMI.patch` | 6,339 | `17916c77e5c37568013bd36d9f162bb2d74a214b724a514a4a76fabee60519d5` |
| `series-final/nouveau-hdmi-color-format-series/0004-drm-nouveau-add-HDMI-YCbCr-4-4-4-and-4-2-2-output.patch` | 16,107 | `bd0a936dada62d04e3b66a250d81bdd62048013a1455bba555332e9a9f4225bf` |
| `series-final/nouveau-hdmi-color-format-series/0005-drm-nouveau-add-HDMI-YCbCr-4-2-0-output-on-GA102-and.patch` | 15,046 | `006d9f7f16dc18a8f0b6507f78eae5340942b58fa4392276b021d6193e85c577` |
| `series-final/nouveau-hdmi-color-format-series/0006-drm-nouveau-expose-HDMI-output-properties-on-DVI-con.patch` | 2,963 | `4c22d12781ef5afce46dc181b41c5f3f480c73b994037d6fc779c57371bdc4a8` |

## Re-verification

From the preserve root:

```sh
sha256sum -c /path/to/repo/docs/upstream/evidence-preservation/SHA256SUMS
```

`git bundle verify` must run in a repository containing the stated
prerequisite. On this workstation the nouveau bundles verified from
`/K3D/temp/ndc-v2` and the NVIDIA bundle from
`/K3D/temp/nvidia-open-wt`. Verification against an unrelated repository
correctly reports a missing prerequisite; that is not bundle corruption.

Before any release or upstream post, also run the adjacent
[adversarial review gate](REVIEW-GATE.md).
