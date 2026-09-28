#!/bin/bash
# Stereo 3D for Source games: puts Valve's sourcevr.so back in every engine
# folder and removes Half-Life 2's 3D menu.
# Usage: ./uninstall.sh [path to the game folder] (default: Half-Life 2)
set -e
G=${1:-}
if [ -z "$G" ]; then
	for root in "$HOME/.steam/steam" "$HOME/.local/share/Steam" "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam"; do
		[ -d "$root/steamapps" ] || continue
		while IFS= read -r lib; do
			if [ -x "$lib/steamapps/common/Half-Life 2/hl2_linux" ]; then G="$lib/steamapps/common/Half-Life 2"; break 2; fi
		done < <(echo "$root"; sed -n 's/^[[:space:]]*"path"[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p' "$root/steamapps/libraryfolders.vdf" 2>/dev/null)
	done
fi
[ -n "$G" ] && [ -d "$G/bin" ] || { echo "Game folder not found. Run: ./uninstall.sh \"/path/to/<game folder>\""; exit 1; }
# While these markers exist the module still holds your own crosshair,
# motion blur, anisotropic filtering or video mode, to put back at the next
# start (the game quit with 3D on). Valve's module would not put them back.
pending=""
had_mark=0
for sub in bin bin/linux64; do
	[ -d "$G/$sub" ] || continue
	[ ! -f "$G/$sub/svrtv-installed.txt" ] || had_mark=1
	p=$(cd "$G/$sub" && ls svrtv-crosshair-off svrtv-blur-restore svrtv-restore-* 2>/dev/null | sed "s|^|$G/$sub/|" || true)
	[ -n "$p" ] && pending="$pending$p"$'\n'
done
if [ -n "$pending" ]; then
	echo "The game last quit with 3D on, so your own settings are still waiting to be restored:"
	printf '%s' "$pending" | sed 's|^|  |'
	echo "Start the game, set Stereo 3D to off (Options > Video, or vr_display_3d 0 and vr_display_apply), quit, then run uninstall.sh again."
	exit 1
fi
menu="$G/hl2/custom/svrtv-3d-menu/gamepadui/options.res"
menu_state="$G/.svrtv-menu-install-state"
if [ -d "$menu_state" ]; then
	case $(cat "$menu_state/presence" 2>/dev/null || true) in
		present) [ -f "$menu_state/original" ] || { echo "Incomplete 3D-menu state at $menu_state" >&2; exit 1; } ;;
		absent) ;;
		*) echo "Incomplete 3D-menu state at $menu_state" >&2; exit 1 ;;
	esac
	expected=$(cat "$menu_state/installed-sha256" 2>/dev/null || true)
	current=$([ -f "$menu" ] && sha256sum "$menu" | cut -d' ' -f1 || echo absent)
	[ -n "$expected" ] && [ "$current" = "$expected" ] || {
		echo "$menu changed after installation; refusing to destroy that edit" >&2; exit 1;
	}
fi
# Validate every ownership record before changing either engine, so damage
# in the second record cannot leave a half-uninstalled game.
for sub in bin bin/linux64; do
	bin="$G/$sub"; mark="$bin/svrtv-installed.txt"; state="$bin/.svrtv-install-state"
	[ -f "$mark" ] || continue
	[ -d "$state" ] || { echo "  $sub: legacy install has no ownership state; refusing destructive uninstall" >&2; exit 1; }
	for owned in svrtv.ini svrtv-anaglyph.fx; do
		presence=$(cat "$state/$owned.presence" 2>/dev/null || true)
		case "$presence" in
			present) [ -f "$state/$owned.original" ] || { echo "  $sub: missing original $owned; refusing uninstall" >&2; exit 1; } ;;
			absent) ;;
			*) echo "  $sub: incomplete ownership state for $owned; refusing uninstall" >&2; exit 1 ;;
		esac
	done
	for owned in sourcevr.so svrtv-anaglyph.fx; do
		expected=$(cat "$state/$owned.installed-sha256" 2>/dev/null || true)
		current=$([ -f "$bin/$owned" ] && sha256sum "$bin/$owned" | cut -d' ' -f1 || echo absent)
		[ -n "$expected" ] && [ "$current" = "$expected" ] || {
			echo "  $bin/$owned changed after installation; refusing to destroy that edit" >&2; exit 1;
		}
	done
done
for sub in bin bin/linux64; do
	bin="$G/$sub"
	[ -d "$bin" ] || continue
	mark="$bin/svrtv-installed.txt"
	state="$bin/.svrtv-install-state"
	if [ -f "$mark" ] && [ -f "$bin/sourcevr.so.valve" ]; then mv -f "$bin/sourcevr.so.valve" "$bin/sourcevr.so"; echo "  $sub: Valve's sourcevr.so back"
	elif [ -f "$mark" ]; then rm -f "$bin/sourcevr.so"; echo "  $sub: our sourcevr.so removed (Valve had none here)"; fi
	if [ -f "$mark" ] && [ -d "$state" ]; then
		for owned in svrtv.ini svrtv-anaglyph.fx; do
			presence=$(cat "$state/$owned.presence" 2>/dev/null || true)
			case "$presence" in
			present)
				# For svrtv.ini the installer never changed an existing file.
				# Restore only when it disappeared; a user's later edits win.
				if [ "$owned" = svrtv.ini ] && [ -e "$bin/$owned" ]; then :
				else cp -p "$state/$owned.original" "$bin/$owned"
				fi
				;;
			absent)
				if [ "$owned" = svrtv.ini ] && [ -e "$bin/$owned" ]; then
					current=$(sha256sum "$bin/$owned" | cut -d' ' -f1)
					installed=$(cat "$state/svrtv.ini.installed-sha256" 2>/dev/null || true)
					if [ -n "$installed" ] && [ "$current" != "$installed" ]; then
						echo "  $sub: keeping user-modified svrtv.ini"
						continue
					fi
				fi
				rm -f "$bin/$owned"
				;;
			esac
		done
		rm -rf "$state"
	fi
	if [ -f "$mark" ]; then rm -f "$bin/svrtv-launch-3d" "$mark"; fi
done
if [ -d "$menu_state" ]; then
	case $(cat "$menu_state/presence" 2>/dev/null || true) in
		present) mkdir -p "$(dirname "$menu")"; cp -p "$menu_state/original" "$menu" ;;
		absent) rm -f "$menu" ;;
		*) echo "Incomplete 3D-menu ownership state; refusing to touch $menu" >&2; exit 1 ;;
	esac
	rm -rf "$menu_state"
	rmdir "$(dirname "$menu")" "$(dirname "$(dirname "$menu")")" 2>/dev/null || true
	echo "  3D menu removed"
elif [ "$had_mark" = 1 ] && [ -d "$G/hl2/custom/svrtv-3d-menu" ]; then
	echo "  3D menu has no ownership state; leaving it untouched" >&2
fi
echo "Done. The logs (svrtv.log next to each module), if any, are left for you to keep or delete."
