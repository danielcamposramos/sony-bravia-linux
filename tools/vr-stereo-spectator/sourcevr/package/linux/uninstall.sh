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
for sub in bin bin/linux64; do
	[ -d "$G/$sub" ] || continue
	p=$(cd "$G/$sub" && ls svrtv-crosshair-off svrtv-blur-restore svrtv-restore-* 2>/dev/null | sed "s|^|$G/$sub/|" || true)
	[ -n "$p" ] && pending="$pending$p"$'\n'
done
if [ -n "$pending" ]; then
	echo "The game last quit with 3D on, so your own settings are still waiting to be restored:"
	printf '%s' "$pending" | sed 's|^|  |'
	echo "Start the game, set Stereo 3D to off (Options > Video, or vr_display_3d 0 and vr_display_apply), quit, then run uninstall.sh again."
	exit 1
fi
for sub in bin bin/linux64; do
	bin="$G/$sub"
	[ -d "$bin" ] || continue
	if [ -f "$bin/sourcevr.so.valve" ]; then mv -f "$bin/sourcevr.so.valve" "$bin/sourcevr.so"; echo "  $sub: Valve's sourcevr.so back"
	elif [ -f "$bin/svrtv-installed.txt" ]; then rm -f "$bin/sourcevr.so"; echo "  $sub: our sourcevr.so removed (Valve had none here)"; fi
	[ -f "$bin/svrtv-installed.txt" ] && rm -f "$bin/svrtv-anaglyph.fx"
	rm -f "$bin/svrtv.ini" "$bin/svrtv-launch-3d" "$bin/svrtv-installed.txt"
done
[ -d "$G/hl2/custom/svrtv-3d-menu" ] && rm -rf "$G/hl2/custom/svrtv-3d-menu" && echo "  3D menu removed"
echo "Done. The logs (svrtv.log next to each module), if any, are left for you to keep or delete."
