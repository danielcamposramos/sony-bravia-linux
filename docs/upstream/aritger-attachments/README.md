# NVIDIA issue #1382 test attachments

Public, self-contained reproducer material prepared for `aritger` in
[NVIDIA/open-gpu-kernel-modules#1382](https://github.com/NVIDIA/open-gpu-kernel-modules/issues/1382).
Captured on 2026-09-22 from the project measurement workstation and the Sony
KDL-46HX855 EDID. No proprietary NVIDIA binaries, credentials, or private Sony
material are included.

| file | purpose | SHA-256 |
|---|---|---|
| `nvidia-1382-test-materials.zip` | upload-ready bundle containing the EDID, probe source, and guarded runner | `14b9e07e5e9fdaf95e383950eda98bfba596cdeb079fb1a1704cc68a7795f018` |
| `hx855-edid-decode.txt` | human-readable decode of the exact 256-byte sink EDID | `04f8b66f3da4420c544861e5ae0ff10386832f4add43090c365fa08352b870a9` |
| `run18-nvidia-stereo-allowed-patch-no-delta-2026-09-22.log` | stock-versus-six-line-patch result: 17 modes and zero stereo modes in both cases | `8d4d67112782aeaad1f84f4653b0d5908242c4e7b40ca2dbb4adb2f8b776567c` |

The `zip/` directory is the extracted, reviewable form of the upload bundle:

| file | SHA-256 |
|---|---|
| `zip/hx855-edid.bin` | `fbe6a3b455e69eab37f36bd0e7b0084a4d105c2adba101e37f0d5309c0a8eadc` |
| `zip/run-nvidia-patched-probe.sh` | `70c89901f8f5223d2c818fc8cf2ea3ca0f5a89733e1a7579bd245d5f46fbf5d8` |
| `zip/stereo-probe.c` | `0c593744ce0adf761cd7070f993b64c546dcae49c2d599294ddeece1b20112b3` |

`unzip -t nvidia-1382-test-materials.zip` passes. The bundle members and the
files under `zip/` are byte-identical.
