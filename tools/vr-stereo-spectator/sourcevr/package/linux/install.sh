#!/bin/bash
# Stereo 3D for Half-Life 2 (VR Stereo Spectator): installs the display
# module and the 3D menu into a Half-Life 2 folder (the native Linux game).
# Usage: ./install.sh [path to the "Half-Life 2" folder]
# Without a path it looks in every Steam library (native and Flatpak Steam).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
G=${1:-}
if [ -z "$G" ]; then
	for root in "$HOME/.steam/steam" "$HOME/.local/share/Steam" "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam"; do
		[ -d "$root/steamapps" ] || continue
		while IFS= read -r lib; do
			if [ -x "$lib/steamapps/common/Half-Life 2/hl2_linux" ]; then G="$lib/steamapps/common/Half-Life 2"; break 2; fi
		done < <(echo "$root"; sed -n 's/^[[:space:]]*"path"[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p' "$root/steamapps/libraryfolders.vdf" 2>/dev/null)
	done
fi
if [ -z "$G" ] || [ ! -x "$G/hl2_linux" ]; then
	echo "Half-Life 2 (native Linux version) not found. Run: ./install.sh \"/path/to/steamapps/common/Half-Life 2\""
	exit 1
fi
echo "Half-Life 2: $G"
bin="$G/bin"
# Today's native Half-Life 2 runs a 32-bit engine; this package carries the
# 32-bit module and says so instead of installing the wrong one.
class=$(od -An -tu1 -j4 -N1 "$bin/engine.so" 2>/dev/null | tr -d ' ')
if [ "$class" != 1 ]; then
	echo "  bin/engine.so is not the 32-bit engine this module is built for (ELF class '${class:-none}'); nothing installed."
	exit 1
fi
# The first install keeps whatever module Valve shipped; a later install
# (the marker is there) never mistakes ours for Valve's.
mark="$bin/svrtv-installed.txt"
if [ ! -f "$mark" ] && [ -f "$bin/sourcevr.so" ] && [ ! -f "$bin/sourcevr.so.valve" ]; then
	cp -p "$bin/sourcevr.so" "$bin/sourcevr.so.valve"
	echo "  bin: Valve's sourcevr.so kept as sourcevr.so.valve"
fi
cp "$HERE/sourcevr.so" "$HERE/svrtv-anaglyph.fx" "$bin/"
echo "sourcevr.so here is Stereo 3D for Half-Life 2 (32-bit); uninstall.sh puts Valve's back." > "$mark"
[ -f "$bin/svrtv.ini" ] || echo "SVRTV_LOG=svrtv.log" > "$bin/svrtv.ini"
echo "  bin: module installed (log: $bin/svrtv.log)"
mkdir -p "$G/hl2/custom/svrtv-3d-menu/gamepadui"
cp "$HERE/menu/gamepadui/options.res" "$G/hl2/custom/svrtv-3d-menu/gamepadui/options.res"
echo "  3D menu installed: Options > Video > Stereo 3D"
echo
echo "Steam > Half-Life 2 > Properties > Launch options:"
echo "  -vulkan -gamepadui -stereo3d                              (achievements on; muzzle flash beside the gun)"
echo "  -vulkan -gamepadui -stereo3d +sv_cheats 1 +viewmodel_fov 90   (muzzle flash on the gun; no achievements)"
echo "See README.txt. Steam's 'Verify integrity of game files' puts Valve's module back: run install.sh again after it."
