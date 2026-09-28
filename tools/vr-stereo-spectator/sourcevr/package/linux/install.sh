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
app_id=""
[ ! -f "$G/steam_appid.txt" ] || app_id=$(tr -dc '0-9' <"$G/steam_appid.txt")
# Validate both engines and all existing ownership records before changing
# either one, so an interrupted record cannot cause a half-update.
for sub in bin bin/linux64; do
	bin="$G/$sub"; [ -f "$bin/engine.so" ] || continue
	case $(od -An -tu1 -j4 -N1 "$bin/engine.so" | tr -d ' ') in
		1) candidate="$HERE/sourcevr.so" ;;
		2) candidate="$HERE/linux64/sourcevr.so" ;;
		*) continue ;;
	esac
	[ -f "$candidate" ] || { echo "Missing packaged module: $candidate" >&2; exit 1; }
	mark="$bin/svrtv-installed.txt"; state="$bin/.svrtv-install-state"
	[ -f "$mark" ] || {
		[ ! -e "$state" ] || { echo "Incomplete prior install state at $state" >&2; exit 1; }
		[ ! -e "$bin/sourcevr.so.valve" ] || { echo "Unowned sourcevr.so.valve in $bin; refusing to guess its provenance" >&2; exit 1; }
		continue
	}
	[ -d "$state" ] || { echo "Legacy install in $bin has no ownership state; refusing a destructive update" >&2; exit 1; }
	[ ! -d "$state" ] || for owned in svrtv.ini svrtv-anaglyph.fx; do
		presence=$(cat "$state/$owned.presence" 2>/dev/null || true)
		case "$presence" in
			present) [ -f "$state/$owned.original" ] || { echo "Missing original $owned in $state" >&2; exit 1; } ;;
			absent) ;;
			*) echo "Incomplete ownership state for $owned in $state" >&2; exit 1 ;;
		esac
	done
	if [ -d "$state" ]; then
		for owned in sourcevr.so svrtv-anaglyph.fx; do
			expected=$(cat "$state/$owned.installed-sha256" 2>/dev/null || true)
			current=$([ -f "$bin/$owned" ] && sha256sum "$bin/$owned" | cut -d' ' -f1 || echo absent)
			[ -n "$expected" ] && [ "$current" = "$expected" ] || {
				echo "$bin/$owned changed after installation; refusing to overwrite it" >&2; exit 1;
			}
		done
	fi
done
if [ "$app_id" = 220 ] && [ -d "$G/.svrtv-menu-install-state" ]; then
	menu_state="$G/.svrtv-menu-install-state"
	menu="$G/hl2/custom/svrtv-3d-menu/gamepadui/options.res"
	case $(cat "$menu_state/presence" 2>/dev/null || true) in
		present) [ -f "$menu_state/original" ] || { echo "Incomplete 3D-menu state at $menu_state" >&2; exit 1; } ;;
		absent) ;;
		*) echo "Incomplete 3D-menu state at $menu_state" >&2; exit 1 ;;
	esac
	expected=$(cat "$menu_state/installed-sha256" 2>/dev/null || true)
	current=$([ -f "$menu" ] && sha256sum "$menu" | cut -d' ' -f1 || echo absent)
	[ -n "$expected" ] && [ "$current" = "$expected" ] || {
		echo "$menu changed after installation; refusing to overwrite it" >&2; exit 1;
	}
fi
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
	state="$bin/.svrtv-install-state"
	if [ ! -f "$mark" ]; then
		# Keep an ownership record for every non-Valve file we may create or
		# replace.  Never recapture on an update: these are the bytes from
		# immediately before the first install.
		if [ -e "$state" ]; then
			echo "  $sub: incomplete prior install state at $state; refusing to overwrite it" >&2
			exit 1
		fi
		mkdir "$state"
		for owned in svrtv.ini svrtv-anaglyph.fx; do
			if [ -e "$bin/$owned" ]; then
				echo present >"$state/$owned.presence"
				cp -p "$bin/$owned" "$state/$owned.original"
			else
				echo absent >"$state/$owned.presence"
			fi
		done
	fi
	if [ ! -f "$mark" ] && [ -f "$bin/sourcevr.so" ] && [ ! -f "$bin/sourcevr.so.valve" ]; then
		cp -p "$bin/sourcevr.so" "$bin/sourcevr.so.valve"
		echo "  $sub: Valve's sourcevr.so kept as sourcevr.so.valve"
	fi
	cp "$mod" "$bin/sourcevr.so"
	cp "$HERE/svrtv-anaglyph.fx" "$bin/"
	sha256sum "$bin/sourcevr.so" | cut -d' ' -f1 >"$state/sourcevr.so.installed-sha256"
	sha256sum "$bin/svrtv-anaglyph.fx" | cut -d' ' -f1 >"$state/svrtv-anaglyph.fx.installed-sha256"
	echo "sourcevr.so here is Stereo 3D for Source games ($arch-bit); uninstall.sh puts Valve's back." > "$mark"
	if [ ! -f "$bin/svrtv.ini" ]; then
		echo "SVRTV_LOG=svrtv.log" > "$bin/svrtv.ini"
		[ ! -d "$state" ] || sha256sum "$bin/svrtv.ini" | cut -d' ' -f1 >"$state/svrtv.ini.installed-sha256"
	fi
	echo "  $sub: $arch-bit module installed (log: $bin/svrtv.log)"
	done=$((done + 1))
done
[ $done -gt 0 ] || { echo "No engine.so in bin or bin/linux64: is this a Source game folder?"; exit 1; }
# The 3D menu is Half-Life 2's own options file with the 3D section added.
if [ "$app_id" = 220 ]; then
	menu="$G/hl2/custom/svrtv-3d-menu/gamepadui/options.res"
	menu_state="$G/.svrtv-menu-install-state"
	if [ -d "$menu_state" ]; then
		case $(cat "$menu_state/presence" 2>/dev/null || true) in
			present) [ -f "$menu_state/original" ] || { echo "Incomplete 3D-menu state at $menu_state" >&2; exit 1; } ;;
			absent) ;;
			*) echo "Incomplete 3D-menu state at $menu_state" >&2; exit 1 ;;
		esac
	else
		mkdir "$menu_state"
		if [ -e "$menu" ]; then
			echo present >"$menu_state/presence"
			cp -p "$menu" "$menu_state/original"
		else
			echo absent >"$menu_state/presence"
		fi
	fi
	mkdir -p "$(dirname "$menu")"
	cp "$HERE/menu/gamepadui/options.res" "$menu"
	sha256sum "$menu" | cut -d' ' -f1 >"$menu_state/installed-sha256"
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
