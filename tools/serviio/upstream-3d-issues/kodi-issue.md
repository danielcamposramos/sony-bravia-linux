<!-- POSTED 2026-09-18 as https://github.com/xbmc/xbmc/issues/29337, then
     EDITED the same day on the owner's instruction.

     v1 (filed from this session, owner's instruction "no AI policy, post
     brief and objective") claimed Kodi never reads the H.264 frame-packing
     SEI. WRONG: DVDVideoCodecFFmpeg.cpp:1043 reads "stereo_mode" from the
     decoded frame's metadata, which FFmpeg's H.264 decoder fills from the
     SEI — verified in Docker on Kodi 21.2. The claim rested on gh code
     search alone (see memory: verify-by-running-before-filing).

     v2 (below, the live text): the edit note says plainly that v1 was
     wrong — GitHub had already emailed v1 to watchers, so the note had to
     be a correction, not "detail added". The report now covers what the
     DLNA side actually measured: every MP4 advertised as MPEG4_P2_SP_AAC
     from a static Platinum table. For the BRAVIAs, which cannot run Kodi
     and are only ever DLNA renderers, the DLNA side is the only side that
     matters. Watch: email trigger only, never poll. -->

**Edit (2026-09-18):** the first version of this report was wrong and has been replaced. It said Kodi never reads the H.264 frame-packing SEI. It does: `CDVDVideoCodecFFmpeg` takes `stereo_mode` from the decoded frame's metadata ([DVDVideoCodecFFmpeg.cpp#L1043](https://github.com/xbmc/xbmc/blob/6c678081054b69a1299c85ff6fd1fba9d58ba60a/xbmc/cores/VideoPlayer/DVDCodecs/Video/DVDVideoCodecFFmpeg.cpp#L1043)), which FFmpeg's H.264 decoder fills from the SEI. Verified on Kodi 21.2 (Debian trixie): an SEI-only MP4 logs `autodetected stereo mode for movie mode left_right`, and the UPnP server passes the SEI through byte-exact. Apologies for the noise. Checking the UPnP side turned up the problem below.

## Bug report
### Describe the bug
Kodi's UPnP server advertises every MP4 as `DLNA.ORG_PN=MPEG4_P2_SP_AAC` (MPEG-4 Part 2 Simple Profile with AAC), whatever the file contains.
The profile comes from a fixed MIME table, [PltProtocolInfo.cpp#L95](https://github.com/xbmc/xbmc/blob/6c678081054b69a1299c85ff6fd1fba9d58ba60a/lib/libUPnP/Platinum/Source/Core/PltProtocolInfo.cpp#L95), which has no `AVC_MP4_*` entries, so H.264 MP4 files are labelled as MPEG-4 Part 2.
`DLNA.ORG_PN` is what renderers from any maker use to decide what they are being sent.

## Expected Behavior
The advertised profile matches the stream (an `AVC_MP4_*` profile for H.264), or `DLNA.ORG_PN` is left out when it is not known, as Kodi already does for `video/x-matroska`.

## Actual Behavior
`res@protocolInfo` for an H.264 + AAC MP4, from Kodi 21.2's ContentDirectory:
`http-get:*:video/mp4:DLNA.ORG_PN=MPEG4_P2_SP_AAC;DLNA.ORG_OP=01;DLNA.ORG_CI=0;DLNA.ORG_FLAGS=01500000000000000000000000000000`
An H.264 MP4 with no audio track gets the same profile.

## Possible Fix
Build the profile from the stream details Kodi already has (video codec, profile, resolution, audio codec), or omit `DLNA.ORG_PN` for `video/mp4` rather than asserting Part 2.
Renderers that accept any `video/mp4` are unaffected (Sony BRAVIA 2011–2012 sets, for example, advertise `http-get:*:video/mp4:*`); renderers that match on `DLNA.ORG_PN` receive the wrong profile.

### To Reproduce
1. `ffmpeg -f lavfi -i testsrc2=size=1280x720:rate=25 -f lavfi -i sine=frequency=440 -t 6 -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest clip.mp4`
2. Add its folder as a video source with sharing allowed, and enable Settings → Services → UPnP/DLNA → Share my libraries.
3. Browse the server from any UPnP client (Videos → Files → the source) and read the item's `res@protocolInfo`.

### Debuglog
Kodi 21.2 run with `--debug` while a client browsed the server (excerpt; the full log is available on request):
```
info <general>: Starting Kodi from Debian (21.2 Debian package version: 2:21.2+dfsg-4). Platform: Linux x86 64-bit
info <general>: starting upnp server
info <CUPnPServer[Kodi]>: Received Browse DirectChildren request for encoded object '0' (plain value: '0'), with sort criteria
debug <CUPnPServer[Kodi]>: Translated id to 'virtualpath://upnproot/'
```
The profile string itself is not logged; it is visible in the Browse response quoted above.

### Your Environment
 - [ ] Android
 - [ ] iOS
 - [ ] tvOS
 - [x] Linux
 - [ ] macOS
 - [ ] Windows
 - [ ] Windows UWP

 - Operating system version/name: Debian 13 (trixie)
 - Kodi version: 21.2 (Debian package 2:21.2+dfsg-4); the table is unchanged on master at 6c678081054b
