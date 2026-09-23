# Casting a frame-packing SEI clip to a Chromecast (2026-09-23)

Sender: our VLC 3.0.23 with the 3D fix (Debian 13 release package `3.0.23-0+deb13u1+3d1`, in a
throwaway `debian:trixie` container with host networking). Receiver: Chromecast at
`192.168.0.20` on the Sony KDL-46EX725, its input selected.
Clip: `sbs-half-1080p24-sei-60s.mp4` (1920x1080 half side-by-side, H.264 frame-packing SEI,
SHA-256 in `clip.sha256`).

Command: `cvlc /clip.mp4 --sout '#chromecast{ip=192.168.0.20}' --demux-filter=demux_chromecast`.
VLC did not transcode: the chain was
`chromecast-proxy:std{mux=avformat{mux=matroska,options={live=1},reset-ts},access=chromecast-http}`,
so the H.264 stream, SEI included, reached the Chromecast unchanged.

Result (Daniel, watching the TV): **flat** side by side, no 3D switch.

The Chromecast decodes the stream and sends 2D HDMI; it does not turn the SEI into the HDMI 3D
InfoFrame. Since the SEI already arrived in passthrough, a transcoded cast cannot do better.
Automatic 3D through a Chromecast is not possible from the sender side.
