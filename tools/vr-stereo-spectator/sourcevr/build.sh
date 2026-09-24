#!/bin/sh
# Build sourcevr.so for 32-bit (today's native Half-Life 2) and 64-bit Source
# games, against Valve's Source SDK 2013 headers, with no C++ runtime and only
# long-standing libc/libm symbols so it loads in any Steam runtime.
# Usage: build.sh [sdk-src-dir]   (default /K3D/temp/sdk2013/src; a sparse
# checkout of ValveSoftware/source-sdk-2013 with src/public, src/common,
# src/tier1 and src/mathlib is enough). Output: out/32/sourcevr.so, out/64/sourcevr.so
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
SDK=${1:-/K3D/temp/sdk2013/src}
docker run --rm -v "$HERE":/w -v "$SDK":/sdk:ro debian:testing sh -c '
set -eu
apt-get update -qq >/dev/null
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends g++ g++-multilib binutils >/dev/null
cd /w
for bits in 32 64; do
	mkdir -p out/$bits
	extra=""
	[ $bits = 64 ] && extra="-DPLATFORM_64BITS"
	g++ -m$bits -O2 -fPIC -shared -std=gnu++17 -fno-exceptions -fno-rtti \
		-fvisibility=hidden -fno-stack-protector -U_FORTIFY_SOURCE \
		-DPOSIX -D_POSIX -DLINUX -D_LINUX -DGNUC -DCOMPILER_GCC -DNO_MALLOC_OVERRIDE \
		-DVPROF_LEVEL=1 -DNDEBUG $extra \
		-I/sdk/public -I/sdk/public/tier0 -I/sdk/public/tier1 -I/sdk/common \
		-Wno-register -Wno-deprecated \
		sourcevr_tv.cpp -o out/$bits/sourcevr.so \
		-nodefaultlibs -Wl,--no-undefined -Wl,--as-needed -lm -lc -lgcc
	echo "== $bits-bit"
	readelf -h out/$bits/sourcevr.so | grep -E "Class|Machine" | tr -s " "
	echo "exports:"; nm -D --defined-only out/$bits/sourcevr.so | awk "{print \$3}" | grep -v "^_" | tr "\n" " "; echo
	echo "needs:"; objdump -p out/$bits/sourcevr.so | grep NEEDED
	echo "max symbol versions:"; objdump -T out/$bits/sourcevr.so | grep -o "GLIBC_[0-9.]*" | sort -uV | tail -3 | tr "\n" " "; echo
done
'
sha256sum "$HERE"/out/*/sourcevr.so
