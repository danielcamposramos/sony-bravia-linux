#!/bin/sh
# Assembles the end-user packages from built modules:
#   svrtv-hl2-3d-windows.zip   x86 + x64 sourcevr.dll, install.bat/ps1, README
#   svrtv-hl2-3d-linux.tar.gz  32-bit sourcevr.so + anaglyph effect, install.sh, README
# Both carry the 3D menu (the game's options.res with the section added) and
# SHA256SUMS.txt naming the source commit.
# Usage: make-packages.sh <out> <sourcevr-x86.dll> <sourcevr-x64.dll> <sourcevr.so>
#                         <svrtv-anaglyph.fx> <options.res> <source commit>
set -e
OUT=$1 X86=$2 X64=$3 SO=$4 FX=$5 RES=$6 COMMIT=$7
HERE=$(cd "$(dirname "$0")" && pwd)
SRCURL="https://github.com/danielcamposramos/source-sdk-2013 branch stereo3d-full-res-wip, commit $COMMIT (src/sourcevr_display)"
rm -rf "$OUT/svrtv-hl2-3d-windows" "$OUT/svrtv-hl2-3d-linux"
W="$OUT/svrtv-hl2-3d-windows" L="$OUT/svrtv-hl2-3d-linux"
mkdir -p "$W/x86" "$W/x64" "$W/menu/gamepadui" "$L/menu/gamepadui"
cp "$X86" "$W/x86/sourcevr.dll"; cp "$X64" "$W/x64/sourcevr.dll"; cp "$RES" "$W/menu/gamepadui/options.res"
cp "$HERE"/windows/* "$W/"
for f in "$W"/*.txt "$W"/*.bat "$W"/*.ps1; do sed -i 's/\r$//; s/$/\r/' "$f"; done   # Windows line ends (batch files need them)
cp "$SO" "$FX" "$L/"; cp "$RES" "$L/menu/gamepadui/options.res"; cp "$HERE"/linux/* "$L/"; chmod +x "$L"/*.sh
for P in "$W" "$L"; do
	( cd "$P" && { echo "Built $(date +%F) from $SRCURL."; echo; find . -type f ! -name SHA256SUMS.txt | sort | xargs sha256sum; } > SHA256SUMS.txt )
done
sed -i 's/$/\r/' "$W/SHA256SUMS.txt"
( cd "$OUT" && rm -f svrtv-hl2-3d-windows.zip svrtv-hl2-3d-linux.tar.gz && zip -qr svrtv-hl2-3d-windows.zip svrtv-hl2-3d-windows && tar czf svrtv-hl2-3d-linux.tar.gz svrtv-hl2-3d-linux )
ls -la "$OUT"/svrtv-hl2-3d-windows.zip "$OUT"/svrtv-hl2-3d-linux.tar.gz
