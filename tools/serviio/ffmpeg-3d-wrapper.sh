#!/bin/bash
# ffmpeg-3d wrapper — makes Serviio transcodes 3D-native on era BRAVIA TVs.
#
# The TVs (KDL-EX725/HX855 era) auto-engage 3D when the H.264 stream carries a
# frame_packing_arrangement SEI (payload type 45). Serviio's profile XML cannot
# add x264 encoder params, and Serviio-box ffmpeg 6.1.6 does not auto-inject
# from Matroska stereo side data (ffmpeg >= 9 does). This wrapper sits in front
# of /usr/bin/ffmpeg (install as /usr/local/bin/ffmpeg) and, whenever Serviio
# re-encodes with libx264, appends `-x264-params frame-packing=3|4` if any
# input is 3D-flagged — by filename tokens ([3D], sbs/hsbs, tb/tab/htb) or a
# Matroska stereo_mode tag. Everything else passes through untouched.
#
# Decisions are logged to /opt/serviio/log/ffmpeg-3d.log.
# Repo: sony-bravia-linux, tools/serviio/ — live-proven 2026-09-13.

REAL=/usr/bin/ffmpeg
FFPROBE=/usr/bin/ffprobe
LOG=/opt/serviio/log/ffmpeg-3d.log

declare -a args=("$@")
n=$#

# 1) Is this a libx264 encode? (Serviio uses "-c:v libx264"; cover other forms)
x264_idx=-1
for ((i = 0; i < n; i++)); do
  case "${args[$i]}" in
    libx264)
      j=$((i - 1))
      if [ "$j" -ge 0 ]; then
        case "${args[$j]}" in
          -c:v | -vcodec | -codec:v | -c:v:0 | -codec:v:0) x264_idx=$i ;;
        esac
        fi ;;
    -c:v=libx264 | -vcodec=libx264 | -codec:v=libx264 | -c:v:0=libx264) x264_idx=$i ;;
  esac
done
[ "$x264_idx" -lt 0 ] && exec "$REAL" "$@"

# 2) Any 3D-flagged input?
fp=""
why=""
declare -a inputs=()
for ((i = 0; i < n; i++)); do
  if [ "${args[$i]}" = "-i" ]; then
    j=$((i + 1))
    [ "$j" -lt "$n" ] && inputs+=("${args[$j]}")
  fi
done
for f in "${inputs[@]}"; do
  b=$(basename "$f" 2>/dev/null)
  if echo "$b" | grep -qiE 'sbs|hsbs|side.?by.?side|lado.a.lado'; then
    fp=3 why="name:sbs($b)"; break
  fi
  if echo "$b" | grep -qiE '\b(tb|tab|htb)\b|top.?bottom|cima.e.baixo|up.and.down'; then
    fp=4 why="name:tb($b)"; break
  fi
  if echo "$b" | grep -q '\[3D\]'; then
    fp=3 why="name:[3D]($b)"; break
  fi
  tag=$("$FFPROBE" -v error -select_streams v:0 \
    -show_entries stream_tags=stereo_mode -of default=nw=1:nk=1 "$f" 2>/dev/null)
  case "$tag" in
    left_right | right_left) fp=3 why="tag:$tag($b)"; break ;;
    top_bottom | bottom_top) fp=4 why="tag:$tag($b)"; break ;;
  esac
done
[ -z "$fp" ] && exec "$REAL" "$@"

# 3) Insert the param right after the libx264 token (stays in the output
#    option group, well before the output URL — valid for single-output cmds)
declare -a out=()
for ((i = 0; i < n; i++)); do
  out+=("${args[$i]}")
  [ "$i" = "$x264_idx" ] && out+=(-x264-params "frame-packing=$fp")
done
echo "$(date '+%F %T') frame-packing=$fp  why=$why" >>"$LOG" 2>/dev/null
exec "$REAL" "${out[@]}"