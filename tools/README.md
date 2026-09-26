# tools

Everything this project runs, tests or measures with. Each folder has its own README with the details. The single files carry their notes in their header.

Project status and the partner guide: [docs/project-status.md](../docs/project-status.md).

## The TV media stack (runs on d2server)

- [serviio/](serviio/README.md) — Serviio renderer profiles for the KDL-46EX725 and KDL-46HX855, the 3D-aware transcode wrapper (`ffmpeg-3d-wrapper.sh`), and [tv-mediabrowser](serviio/tv-mediabrowser/README.md), the media app both sets use on Daniel's LAN.
- [systemd/](systemd/README.md) — the units that run the TV services as real system services, started together by `bravia-stack.target`.
- [rd1-portal/](rd1-portal/) — an era-TLS HTTPS server: with a DNS override, the EX725 browser's hardcoded homepage (`rd1.sony.net`) opens our portal.
- [bravia_ircc.py](bravia_ircc.py) — remote control over the network (IRCC), no pairing or registration needed.

## 3D files: video and photos

- [bravia_sei3d.py](bravia_sei3d.py) — restores 3D auto-detection to side-by-side and top-and-bottom movies by putting back the H.264 frame-packing SEI. No re-encode: the picture stays byte-identical.
- [bravia_3dcatalog.py](bravia_3dcatalog.py) — builds a 3D index of the library, so the portal can offer "all 3D photos" and "all 3D videos" wherever the files live.
- [bravia_mpo.py](bravia_mpo.py) — writes and inspects MPO stereo photos (CIPA DC-007), the format Sony's own 3D cameras wrote.
- [bravia_anaglyph.py](bravia_anaglyph.py) — anaglyph to side by side and back, for legacy red/cyan content.
- [mpo_dlna_probe.py](mpo_dlna_probe.py) — a throwaway DLNA server that offers the same MPO four ways, to find what the sets' network photo path decides on.
- [fieldseq-3d/](fieldseq-3d/verify-fieldseq-to-sbs.sh) — checks the field-sequential to side-by-side conversion with ffmpeg on synthetic clips.
- [ffmpeg-s3dprobe/](ffmpeg-s3dprobe/s3dprobe.c) — prints the stereo 3D side data of each decoded frame, to show which layout wins when the container and the SEI disagree.
- [kodi-dlna-test/](kodi-dlna-test/README.md) — Kodi's DLNA server in a throwaway container, for the SEI-only 3D test ([xbmc/xbmc#29337](https://github.com/xbmc/xbmc/issues/29337)).

## HDMI 3D and deep colour from a Linux PC

- [stereo-kms-probe/](stereo-kms-probe/README.md) — the starting point: the evidence that amdgpu dropped every stereo mode at probe time, before userspace could ask for one.
- [stereo-modeset/](stereo-modeset/README.md) — the HDMI bench: the stereo modeset tool, the run scripts, the sets' EDIDs, and one log per run (3D, Deep Color and colour formats, on amdgpu, nouveau and the proprietary NVIDIA driver).
- [nvtiming-parse-test/](nvtiming-parse-test/nvtiming-parse.c) — runs NVIDIA's EDID timing library in userspace, so a parser change can be checked against the HX855's EDID without loading a kernel module.

## Games in 3D

These work on any 3D display, not only on these two sets.

- [vr-stereo-spectator/](vr-stereo-spectator/) — Half-Life 2 in 3D through the Source engine's own VR path:
  - [sourcevr/](vr-stereo-spectator/sourcevr/README.md), the VR module that presents the 3D display to the engine as its headset;
  - [gamescope/](vr-stereo-spectator/gamescope/), gamescope-3dtv, the build with the frame-race fix sent as [ValveSoftware/gamescope#2438](https://github.com/ValveSoftware/gamescope/pull/2438);
  - [anaglyph/](vr-stereo-spectator/anaglyph/README.md), the red/cyan effect gamescope applies for any colour screen;
  - [FORMULA.md](vr-stereo-spectator/FORMULA.md), what it takes to bring any VR engine to a 3D display.
- [hl2-bench/](hl2-bench/README.md) — the unattended Half-Life 2 test suite: the steps files, one per session, and the Steam launch wrapper.
- [mame-segascope-test/](mame-segascope-test/README.md) — testing MAME's SegaScope half side-by-side layout on the two sets, for [mamedev/mame#3492](https://github.com/mamedev/mame/issues/3492).

## Research helpers

- [fetch-rendered.sh](fetch-rendered.sh) — reads JavaScript-rendered pages through a local browserless container. It stops at anti-bot controls, by design.
- [crwiki.py](crwiki.py) — a small Consumer Rights Wiki client for reviewed edits: every write prints a diff of what the wiki holds afterwards.
