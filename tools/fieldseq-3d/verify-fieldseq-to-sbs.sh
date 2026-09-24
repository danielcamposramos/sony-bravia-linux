#!/bin/sh
# Field-sequential (H.264 frame_packing_arrangement type 5 in its SD field
# form) to side-by-side: build synthetic 576i TFF and 480i BFF clips whose
# temporally first field carries the left view (red, box at x) and whose
# second field carries the right view (blue, box at x+20), convert with
#   separatefields,stereo3d=al:sbs2l
# and check every output frame: left half red, right half blue, both boxes
# from the same instant (disparity 20 px, same step per frame).
# Then the TV-ready form: 1920x1080 SBS-half with the frame-packing SEI.
# Verified 2026-09-24 with ffmpeg 9.0.1: about 50 tff and 60 bff frames (the
# generator varies by one), 0 failures; the SEI reads back as Stereo 3D left_right.
# Usage: verify-fieldseq-to-sbs.sh [workdir]   (default /K3D/temp/fieldseq-test)
set -eu
D=${1:-/K3D/temp/fieldseq-test}
mkdir -p "$D" && cd "$D"
for SF in tff bff; do
	if [ $SF = tff ]; then R=25; S=720x288; FF=top; else R=30000/1001; S=720x240; FF=bottom; fi
	# framepack=frameseq alternates L,R with exact timestamps; weave puts
	# the first of each pair in the temporally first field.
	ffmpeg -hide_banner -loglevel error -y \
		-f lavfi -i "color=c=red:s=$S:r=$R:d=2" -f lavfi -i "color=c=blue:s=$S:r=$R:d=2" \
		-f lavfi -i "color=c=white:s=60x80:r=$R:d=2" -filter_complex \
		"[2]split[b1][b2];[0][b1]overlay=x='100+8*n':y=100[L];[1][b2]overlay=x='120+8*n':y=100[R];[L][R]framepack=frameseq,weave=first_field=$FF,setfield=$SF[v]" \
		-map "[v]" -c:v ffv1 src-$SF.mkv
	# al = left eye in the temporally first field; use ar when it is the second.
	ffmpeg -hide_banner -loglevel error -y -i src-$SF.mkv -vf "separatefields,stereo3d=al:sbs2l" -c:v ffv1 out-$SF.mkv
done
python3 - <<'EOF'
import subprocess, numpy as np
fail = 0
for sf, h in (('tff', 288), ('bff', 240)):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'out-{sf}.mkv', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    o = np.frombuffer(raw, np.uint8).reshape(-1, h, 1440, 3)
    def bx(r):
        w = np.where(r.min(-1) > 200)[0]
        return int(w[0]) if len(w) else -1
    def dom(x):
        p = x[20:80].reshape(-1, 3).mean(0)
        return 'red' if p[0] > p[2] + 80 else 'blue' if p[2] > p[0] + 80 else '?'
    x0 = bx(o[0][140][:720])  # the generator's own start offset
    bad = [n for n, f in enumerate(o) if not (dom(f[:, :720]) == 'red' and dom(f[:, 720:]) == 'blue'
           and bx(f[140][:720]) == x0 + 8 * n and bx(f[140][720:]) == x0 + 20 + 8 * n)]
    print(sf, len(o), 'frames, failures:', len(bad))
    fail += len(bad)
raise SystemExit(1 if fail else 0)
EOF
ffmpeg -hide_banner -loglevel error -y -i src-tff.mkv \
	-vf "separatefields,stereo3d=al:sbs2l,scale=1920:1080,setsar=1" \
	-c:v libx264 -x264-params frame-packing=3 -crf 18 -pix_fmt yuv420p tv-sbs-sei.mp4
ffprobe -v error -select_streams v -read_intervals '%+#1' -show_frames -of flat tv-sbs-sei.mp4 |
	grep -E 'stereo_mode|side_data_type="Stereo 3D"'
