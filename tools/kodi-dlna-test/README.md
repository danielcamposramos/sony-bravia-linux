# Kodi as a DLNA server, in a throwaway container

A reproducible harness for one question: **does a 3D TV auto-engage 3D
when Kodi's UPnP/DLNA server hands it a file whose only 3D signal is the
H.264 frame-packing SEI?** Kodi runs from Debian main, inside Docker, so
nothing is installed on the host and the media server stays untouched.

## Run it

```bash
docker build -t kodi-sei-test .
docker run -d --init --name kodi-dlna-test --network host \
  -v /path/to/test/files:/work/share:ro -v "$PWD/cfg:/cfg" kodi-sei-test \
  sh -c 'mkdir -p /root/.kodi/userdata && cp /cfg/*.xml /root/.kodi/userdata/ \
         && exec xvfb-run -n 173 -s "-screen 0 1280x720x24" kodi --debug'
python3 lanprobe.py          # what the TV will see: server, paths, protocolInfo
docker rm -f kodi-dlna-test  # when done
```

On the TV: the media-server list → **Kodi (hostname)** → Video Library →
Files → work.

Two details that each cost a failed start, kept here so they cost nobody
else one:

- **`--init` is required.** Without it `xvfb-run` becomes the container's
  PID 1, the readiness signal from Xvfb is lost to PID 1's signal rules,
  and Kodi is never launched. Nothing errors; it just waits.
- **`--network host`** puts Kodi on the LAN so SSDP discovery reaches the
  TV. That also puts Xvfb's abstract X socket in the host's namespace, so
  pick a display number the host is not using (`-n 173`).

And one for the test design: **name files neutrally.** Kodi's player
detects 3D from filename tokens, so a file called `sbs_*.mp4` confounds a
test of the stream signal.

## Result on the KDL-46EX725 (2026-09-18, owner-verified)

Four files, lossless (no re-encode), identical where it matters:

| File | Signal | Kodi advertises | On the set |
|---|---|---|---|
| `A-bonsai-com-sei.mp4` | SEI, no container tag | `video/mp4`, `MPEG4_P2_SP_AAC` | **3D engaged automatically** |
| `B-bonsai-sem-sei.mp4` | A minus its SEI (791 bytes) | same | plays flat |
| `C-3d-maestro.mp4` | SEI, MKV remuxed to MP4 | same | **3D engaged automatically** |
| `D-3d-maestro.mkv` | SEI + Matroska tag | `video/x-matroska` | **not listed** |

The SEI alone flips the set into 3D, through a second, independent DLNA
server. Kodi serves the bytes untouched, so the SEI arrives; its wrong
DLNA profile for H.264 MP4 (xbmc/xbmc#29337) does not matter to this set,
which accepts any `video/mp4`. Matroska is filtered out by the set before
playback, because `video/x-matroska` is not in its advertised list.

## Audio, same day: the same issue, on audio

Seven one-minute cuts from real titles, one per audio format in the
owner's library, remuxed to MP4 with the **original track copied
bit-exact** and the SEI added (`tools/bravia_sei3d.py`):

| File (60 s, lossless cut, original track, SEI added) | Audio | On the set |
|---|---|---|
| E1 *Gravity* | AC-3 5.1 | **3D engaged**, OSD **"Dolby Digital"** |
| E2 *A Lenda do Rei Macaco* | AC-3 2.0 | **3D engaged**, **"Dolby Digital"** |
| E3 *Brahmastra* | E-AC3 5.1 | **3D engaged**, **"Dolby Digital Plus"** |
| E4 *Avatar: The Way of Water* | E-AC3 7.1 | **3D engaged**, **"Dolby Digital Plus"** |
| E5 *Predador* | AAC 5.1 | **3D engaged**, no Dolby indicator (AAC) |
| E6 *Gravity* | DTS 5.1 | 3D engaged, **no audio** |
| E7 *Gravity* | TrueHD 7.1 | cannot be put in MP4 (FFmpeg's TrueHD-in-MP4 is experimental and failed); as MKV, **not listed** |

**The set decodes Dolby Digital Plus natively from MP4 on its own DLNA
player**, 7.1 included. Every SEI-carrying MP4 engaged 3D whatever
audio travelled with it. Kodi labels all of these `..._AAC`, Dolby and
DTS included; the set ignores the label (xbmc/xbmc#29337 updated).
