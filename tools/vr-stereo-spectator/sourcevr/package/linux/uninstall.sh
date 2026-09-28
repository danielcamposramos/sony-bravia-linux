#!/bin/bash
# Stereo 3D for Half-Life 2: puts Valve's sourcevr.so back and removes the
# 3D menu. Usage: ./uninstall.sh [path to the "Half-Life 2" folder]
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
[ -n "$G" ] && [ -d "$G/bin" ] || { echo "Half-Life 2 not found. Run: ./uninstall.sh \"/path/to/Half-Life 2\""; exit 1; }
bin="$G/bin"
# While these markers exist the module still holds your own crosshair,
# motion blur, anisotropic filtering or video mode, to put back at the next
# start (the game quit with 3D on). Valve's module would not put them back.
pending=$(cd "$bin" && ls svrtv-crosshair-off svrtv-blur-restore svrtv-restore-* 2>/dev/null || true)
if [ -n "$pending" ]; then
	echo "The game last quit with 3D on, so your own settings are still waiting to be restored:"
	echo "$pending" | sed "s|^|  $bin/|"
	echo "Start Half-Life 2, set Options > Video > Stereo 3D to off, Apply, quit, then run uninstall.sh again."
	exit 1
fi
if [ -f "$bin/sourcevr.so.valve" ]; then mv -f "$bin/sourcevr.so.valve" "$bin/sourcevr.so"; echo "  bin: Valve's sourcevr.so back"
elif [ -f "$bin/svrtv-installed.txt" ]; then rm -f "$bin/sourcevr.so"; echo "  bin: our sourcevr.so removed (Valve had none here)"; fi
rm -f "$bin/svrtv.ini" "$bin/svrtv-launch-3d" "$bin/svrtv-installed.txt" "$bin/svrtv-anaglyph.fx"
rm -rf "$G/hl2/custom/svrtv-3d-menu" && echo "  3D menu removed"
echo "Done. The log ($bin/svrtv.log), if any, is left for you to keep or delete."
