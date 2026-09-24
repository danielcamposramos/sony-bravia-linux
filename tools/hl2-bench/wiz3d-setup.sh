#!/bin/bash
# Install or remove wiz3D (the D3D9 stereo proxy, iZ3D's successor) in
# Half-Life 2's Windows build, for the bench suite's wiz3D reference steps.
# Follows wiz3D's own instructions: copy the contents of dx9/x86 next to
# hl2.exe; the output method is set to SideBySideOutput for 3D televisions.
# Files that would be overwritten are kept in .wiz3d-backup/ and restored on
# removal. Needs HL2 switched to Proton in Steam (the Windows build).
#
# Usage: wiz3d-setup.sh install|remove|status
set -eu
GAME=${HL2_GAME:-/mnt/games/SteamLibrary/steamapps/common/Half-Life 2}
PKG=${WIZ3D_DIR:-/K3D/temp/wiz3d/v0.3.1/wiz3D.v0.3.1}/dx9/x86
BACKUP="$GAME/.wiz3d-backup"
LIST="$BACKUP/installed.txt"

case "${1:-}" in
install)
	[ -f "$GAME/hl2.exe" ] || { echo "no hl2.exe in $GAME: switch Half-Life 2 to Proton in Steam first" >&2; exit 1; }
	[ -d "$PKG" ] || { echo "wiz3D package not found: $PKG" >&2; exit 1; }
	[ -f "$LIST" ] && { echo "wiz3D already installed"; exit 0; }
	mkdir -p "$BACKUP"
	(cd "$PKG" && find . -type f | sed 's|^\./||') >"$LIST.tmp"
	while read -r f; do
		[ -e "$GAME/$f" ] && { mkdir -p "$BACKUP/$(dirname "$f")"; cp -p "$GAME/$f" "$BACKUP/$f"; }
		mkdir -p "$GAME/$(dirname "$f")"
		cp -p "$PKG/$f" "$GAME/$f"
	done <"$LIST.tmp"
	mv "$LIST.tmp" "$LIST"
	sed -i 's|<OutputMethodDll Value="[^"]*"/>|<OutputMethodDll Value="SideBySideOutput"/>|' "$GAME/wiz3D_Config.xml"
	grep -o '<OutputMethodDll Value="[^"]*"/>' "$GAME/wiz3D_Config.xml"
	echo "wiz3D installed: $(wc -l <"$LIST") files"
	;;
remove)
	[ -f "$LIST" ] || { echo "wiz3D not installed"; exit 0; }
	while read -r f; do
		rm -f "$GAME/$f"
		[ -e "$BACKUP/$f" ] && cp -p "$BACKUP/$f" "$GAME/$f"
	done <"$LIST"
	rmdir "$GAME/OutputMethods" 2>/dev/null || true
	rm -rf "$BACKUP"
	echo "wiz3D removed"
	;;
status)
	[ -f "$LIST" ] && echo "installed ($(wc -l <"$LIST") files)" || echo "not installed"
	;;
*) echo "usage: $0 install|remove|status" >&2; exit 2 ;;
esac
