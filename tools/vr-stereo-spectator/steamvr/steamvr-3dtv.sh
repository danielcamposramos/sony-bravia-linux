#!/bin/sh
# SteamVR inside gamescope on a 3D display, for the stereodisplay driver.
# gamescope is Valve's own wrapper for its games on all its hardware; here it
# gives SteamVR's desktop-window headset a screen of its own, full screen on
# the 3D display, with our effects available. Installed as
# ~/.local/bin/steamvr-3dtv; SteamVR's launch options (set once):
#     sh /home/daniel/.local/bin/steamvr-3dtv %command%
# Settings, changed without touching Steam: ~/.config/steamvr-3dtv.env
#     GS_BIN   the gamescope to run (default: the patched gamescope-3dtv)
#     GS_ARGS  its arguments (default: the HL2 bench's: RTX 3060, 1920x1080,
#              full screen on display 0, the HX855)
#     GS_OFF=1 no gamescope: SteamVR's window straight on the desktop's X11
#     GS_PASS=1 nothing changed: SteamVR as Steam launches it
# Everything it runs, and gamescope's errors, go to
# ~/.local/state/steamvr-3dtv.log.
LOG=${STEAMVR_3DTV_LOG:-$HOME/.local/state/steamvr-3dtv.log}
mkdir -p "$(dirname "$LOG")"
ENV_FILE=${STEAMVR_3DTV_ENV:-$HOME/.config/steamvr-3dtv.env}
[ -f "$ENV_FILE" ] && . "$ENV_FILE"
GS_BIN=${GS_BIN:-$HOME/.local/bin/gamescope-3dtv}
# SteamVR's setup check runs getcap, which Debian keeps in /usr/sbin, outside
# a desktop user's PATH: without it every start shows "SteamVR setup is
# incomplete" although vrcompositor-launcher already has cap_sys_nice
# (vrsetup.sh: "getcap is required to complete the SteamVR setup").
case ":$PATH:" in *:/usr/sbin:*) ;; *) PATH="$PATH:/usr/sbin:/sbin"; export PATH ;; esac
GS_ARGS=${GS_ARGS:---backend sdl -g --prefer-vk-device 10de:2504 -f -W 1920 -H 1080 -w 1920 -h 1080 --display-index 0}
# A Steam started from an environment without the session's runtime folder
# (seen 2026-09-28: XDG_RUNTIME_DIR=/tmp/runtime-root) hands that to
# everything it launches; the session's Wayland and PipeWire sockets are in
# /run/user/<uid>. Repaired here, and logged, when the given one lacks them.
if [ ! -S "${XDG_RUNTIME_DIR:-/nonexistent}/${WAYLAND_DISPLAY:-wayland-0}" ] && [ -S "/run/user/$(id -u)/${WAYLAND_DISPLAY:-wayland-0}" ]; then
	echo "XDG_RUNTIME_DIR was ${XDG_RUNTIME_DIR:-unset}: set to /run/user/$(id -u)" >>"$LOG"
	export XDG_RUNTIME_DIR="/run/user/$(id -u)"
fi
# gamescope's own window goes through X11: its Wayland path hands NVIDIA
# buffers to KWin on the AMD iGPU, which cannot import them (game-wrap.sh).
export SDL_VIDEODRIVER=x11
{
	echo "== $(date '+%F %T') steamvr-3dtv"
	env | grep -E '^(DISPLAY|WAYLAND_DISPLAY|XDG_RUNTIME_DIR|XDG_SESSION_TYPE|SDL_VIDEODRIVER|LD_LIBRARY_PATH|LD_PRELOAD)='
} >>"$LOG"
# GS_PASS=1: SteamVR exactly as Steam launches it (a driver that presents
# the picture itself, such as VRto3D, needs the session untouched).
if [ -n "${GS_PASS:-}" ]; then
	echo "exec $*" >>"$LOG"
	exec "$@" 2>>"$LOG"
fi
# SteamVR's compositor picks Wayland whenever WAYLAND_DISPLAY is set, and
# the desktop's Wayland socket is not reachable from its container.
if [ -n "${GS_OFF:-}" ]; then
	echo "exec env -u WAYLAND_DISPLAY $*" >>"$LOG"
	exec env -u WAYLAND_DISPLAY "$@" 2>>"$LOG"
fi
echo "exec $GS_BIN $GS_ARGS -- env -u WAYLAND_DISPLAY $*" >>"$LOG"
# shellcheck disable=SC2086 # GS_ARGS is a word list
exec "$GS_BIN" $GS_ARGS -- env -u WAYLAND_DISPLAY "$@" 2>>"$LOG"
