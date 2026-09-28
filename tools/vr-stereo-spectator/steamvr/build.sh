#!/bin/sh
# Builds the stereodisplay SteamVR driver (64-bit Linux) in Valve's Steam
# Runtime SDK image, against OpenVR's headers at the commit the sample came
# from. Output: out/stereodisplay/, a driver folder SteamVR can load
# (register it with vrpathreg adddriver <that folder>).
# Usage: build.sh [openvr-checkout]   (default: a sparse clone in /K3D/temp/openvr)
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
OPENVR=${1:-/K3D/temp/openvr}
COMMIT=0924064
if [ ! -f "$OPENVR/headers/openvr_driver.h" ]; then
	mkdir -p "$OPENVR" && cd "$OPENVR"
	git init -q && git remote add origin https://github.com/ValveSoftware/openvr.git
	git config core.sparseCheckout true
	printf 'headers/\nsamples/drivers/\nLICENSE\n' > .git/info/sparse-checkout
	git fetch -q origin master && git checkout -q "$COMMIT"
fi
rm -rf "$HERE/out/stereodisplay"
mkdir -p "$HERE/out/stereodisplay/bin/linux64"
cp -r "$HERE/stereodisplay/." "$HERE/out/stereodisplay/"
docker run --rm --user "$(id -u):$(id -g)" -v "$HERE":/w -v "$OPENVR":/openvr:ro \
  registry.gitlab.steamos.cloud/steamrt/sniper/sdk:latest sh -ec '
  cd /w
  g++ -std=gnu++17 -O2 -fPIC -shared -fvisibility=hidden -Wall -DLINUX -DPOSIX -pthread \
      -I/openvr/headers src/*.cpp \
      -o out/stereodisplay/bin/linux64/driver_stereodisplay.so \
      -static-libstdc++ -static-libgcc -Wl,--no-undefined
  echo "exports:"; nm -D --defined-only out/stereodisplay/bin/linux64/driver_stereodisplay.so | awk "{print \$3}" | grep -v "^_" | tr "\n" " "; echo
  echo "needs:"; objdump -p out/stereodisplay/bin/linux64/driver_stereodisplay.so | grep NEEDED
'
sha256sum "$HERE/out/stereodisplay/bin/linux64/driver_stereodisplay.so"
