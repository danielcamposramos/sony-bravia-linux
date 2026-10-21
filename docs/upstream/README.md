# upstream

**IANA registration, 20 October 2026:** [Matroska Track Plane Types](https://www.iana.org/assignments/matroska#matroska-track-plane-types) now assigns **3, 4 and 5** to the depth maps of the left-eye, right-eye and background planes, respectively, with Daniel Ramos as change controller and the [stereo-layer v1.9.0 specification](https://github.com/Sparky-OS/stereo-layer/blob/v1.9.0/docs/depth-marks.md) as reference.
This gives separate picture and depth tracks shared identifiers through `TrackCombinePlanes`, so readers can preserve their relationship before rendering stereo views.
The separate request for six packed-frame `StereoMode` values (proposed 15–20) remains under designated-expert review; those values are not assigned.

Everything this project has taken to someone else's project: the diagnosis and a working fix, never just a feature request.
Two campaigns run here, and one running record ties them together.

- [issue-tracker.md](issue-tracker.md) — one row per upstream item, every one: where it is, its identifier, its status, whose move it is, and how we watch it. This is the index; read it first. The rule on every row is the same: Daniel posts everything himself, watching is gentle and never past an anti-bot control, and closed issues are left closed.

## The two campaigns

**The media-stack campaign: 3D signalling.**
These sets auto-engage 3D from one signal, the H.264 frame-packing SEI, and ignore the Matroska tag every rip carries, so good hardware plays 3D flat.
The fix was taken to every tool in the chain: encode, remux, play, serve.
Drafts, per-target status and the merges (HandBrake, MKVToolNix, mpv, Universal Media Server) are in [media-stack/](media-stack/README.md).

**The driver campaign: HDMI 1.4 3D and deep colour from a Linux PC.**
The same sets are HDMI 1.4 3D sinks; the question was which layer on a modern Linux PC drops the stereo modes, and then fixing it.
This is the loose files at this level: the amdgpu stereo and frame-packing patches (`0001-*`, `0002-*`, `amdgpu-dc-hdmi-*`), the nouveau deep-colour series (`nouveau-hdmi-deep-colour-*`, with the maintainer replies kept as `.eml`), the NVIDIA drafts and patches (`nvidia-*`), and the design and handoff notes (`community-hdmi-3d-patches.md`, `cover-letter-draft-amd-stereo.md`, `deep-color-opus-handoff-2026-09-22.md`, `nvidia-*-notes.md`).
The measurements behind them are in [../research/](../research/README.md); the run logs are in [../../tools/stereo-modeset/](../../tools/stereo-modeset/README.md).

## Subfolders

- [media-stack/](media-stack/README.md) — the 3D-signalling campaign in full: one draft per target, the merges and the review threads (including how mpv's and MKVToolNix's AI questions were answered on the merits).
- [valve/](valve/README.md) — the Half-Life 2 stereo work taken to Valve: the VR-mode behaviours on a 3D display, the SteamVR stereo-spectator ask, and the gamescope frame-race fix. One draft per issue, each with where it was posted.
- [aritger-attachments/](aritger-attachments/README.md) — the self-contained, hash-verified reproducer bundle prepared for the NVIDIA maintainer on issue #1382: the EDID, the probe source, and a guarded runner, no proprietary or private material.

Every draft here is raw material.
Daniel reviews, rewords in his own voice, and posts; nothing AI-drafted goes out without his approval, and AI assistance is disclosed once where the format asks.
