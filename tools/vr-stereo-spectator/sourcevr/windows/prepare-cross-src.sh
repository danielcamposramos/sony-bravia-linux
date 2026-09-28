#!/bin/sh
# Copies the SDK tree the Windows cross-build needs, and applies two
# clang-cl shims to Valve's headers, in the COPY only (Valve's MSVC build
# needs neither; the fork and the pull request are unchanged):
#  - ssemath.h: __m128's m128_f32/m128_u32 members exist only in MSVC's
#    headers; under clang use the POSIX path (the same element read).
#  - platform.h: RESTRICT (__restrict) on member functions, which clang
#    rejects as a declaration/definition mismatch; empty under clang.
# Usage: prepare-cross-src.sh <sdk-src> <copy>
set -e
SRC=$1 DST=$2
mkdir -p "$DST"
rsync -a --delete --include='/common/***' --include='/public/***' --include='/tier1/***' \
  --include='/sourcevr_display/***' --include='/lib/' --include='/lib/public/' --include='/lib/public/x64/***' \
  --exclude='*' "$SRC"/ "$DST"/
python3 - "$DST" <<'PY'
import sys
d=sys.argv[1]
p=d+'/public/mathlib/ssemath.h'; t=open(p).read()
n=t.count('#ifndef POSIX\n\treturn a.m128_')
assert n==4, n
t=t.replace('#ifndef POSIX\n\treturn a.m128_','#if !defined(POSIX) && !defined(__clang__)\n\treturn a.m128_')
open(p,'w').write(t)
p=d+'/public/tier0/platform.h'; t=open(p).read()
old='	#define RESTRICT __restrict\n	#define RESTRICT_FUNC __declspec(restrict)'
assert t.count(old)==1
t=t.replace(old,'	#ifdef __clang__\n	#define RESTRICT\n	#else\n	#define RESTRICT __restrict\n	#endif\n	#define RESTRICT_FUNC __declspec(restrict)')
open(p,'w').write(t)
PY
echo "cross source ready: $DST"
