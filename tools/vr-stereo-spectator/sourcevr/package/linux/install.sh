#!/bin/bash
# Stereo 3D for Half-Life 2 and Source games (VR Stereo Spectator): installs
# the display module next to each engine of a game folder (the 32-bit one
# in bin, the 64-bit one in bin/linux64), and Half-Life 2's 3D menu.
# Usage: ./install.sh [path to the game folder]
# Without a path it looks for Half-Life 2 in every Steam library (native and
# Flatpak Steam); give the path for any other Source game (e.g. Half-Life 2:
# Deathmatch, Source SDK Base 2013 Multiplayer).
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
if [ -z "$G" ] || [ ! -d "$G/bin" ]; then
	echo "Half-Life 2 not found. Run: ./install.sh \"/path/to/steamapps/common/<game folder>\""
	exit 1
fi
echo "Game folder: $G"
# Every engine gets the module of its own architecture (ELF class 1 = 32-bit,
# 2 = 64-bit); a folder with neither gets nothing, and says so.
done=0
for sub in bin bin/linux64; do
	bin="$G/$sub"
	[ -f "$bin/engine.so" ] || continue
	case $(od -An -tu1 -j4 -N1 "$bin/engine.so" | tr -d ' ') in
		1) arch=32; mod="$HERE/sourcevr.so" ;;
		2) arch=64; mod="$HERE/linux64/sourcevr.so" ;;
		*) echo "  $sub: unknown engine architecture, skipped"; continue ;;
	esac
	# The first install keeps whatever module Valve shipped; a later install
	# (the marker is there) never mistakes ours for Valve's.
	mark="$bin/svrtv-installed.txt"
	if [ ! -f "$mark" ] && [ -f "$bin/sourcevr.so" ] && [ ! -f "$bin/sourcevr.so.valve" ]; then
		cp -p "$bin/sourcevr.so" "$bin/sourcevr.so.valve"
		echo "  $sub: Valve's sourcevr.so kept as sourcevr.so.valve"
	fi
	cp "$mod" "$bin/sourcevr.so"
	cp "$HERE/svrtv-anaglyph.fx" "$bin/"
	echo "sourcevr.so here is Stereo 3D for Source games ($arch-bit); uninstall.sh puts Valve's back." > "$mark"
	[ -f "$bin/svrtv.ini" ] || echo "SVRTV_LOG=svrtv.log" > "$bin/svrtv.ini"
	echo "  $sub: $arch-bit module installed (log: $bin/svrtv.log)"
	done=$((done + 1))
done
[ $done -gt 0 ] || { echo "No engine.so in bin or bin/linux64: is this a Source game folder?"; exit 1; }
# The 3D menu is Half-Life 2's own options file with the 3D section added.
if [ "$(tr -dc '0-9' < "$G/steam_appid.txt" 2>/dev/null)" = 220 ]; then
	mkdir -p "$G/hl2/custom/svrtv-3d-menu/gamepadui"
	cp "$HERE/menu/gamepadui/options.res" "$G/hl2/custom/svrtv-3d-menu/gamepadui/options.res"
	echo "  3D menu installed: Options > Video > Stereo 3D"
	echo
	echo "Steam > Half-Life 2 > Properties > Launch options:"
	echo "  -vulkan -gamepadui -stereo3d                              (achievements on; muzzle flash beside the gun)"
	echo "  -vulkan -gamepadui -stereo3d +sv_cheats 1 +viewmodel_fov 90   (muzzle flash on the gun; no achievements)"
else
	echo
	echo "Launch options for this game (in our tests the 64-bit engine loaded the module only with -vr):"
	echo "  -vulkan -vr -stereo3d"
	echo "(The 3D menu is Half-Life 2's; here 3D comes from -stereo3d, or vr_display_3d 1 and vr_display_apply in the console.)"
fi
echo "See README.txt. Steam's 'Verify integrity of game files' puts Valve's module back: run install.sh again after it."
