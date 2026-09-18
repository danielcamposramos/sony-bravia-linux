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
