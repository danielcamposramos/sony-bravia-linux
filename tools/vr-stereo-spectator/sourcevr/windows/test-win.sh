#!/bin/sh
# Loads the Windows sourcevr.dll builds under Wine, outside the game, and
# runs test_geometry.cpp on each format: the DLL loads (its imports resolve
# against stub_tier0.cpp), starts (module folder, svrtv.ini, log) and does
# the stereo math as a Windows DLL. Images: svrtv-wincross (clang-cl,
# lld-link) and svrtv-winetest (the same plus Wine), with Microsoft's CRT
# and Windows SDK from xwin at /K3D/temp/win-build/msvc.
# Usage: test-win.sh <sdk-src> <dir with sourcevr-x64.dll / sourcevr-x86.dll>
set -e
SRC=$1 DLLS=$2 HERE=$(cd "$(dirname "$0")/.." && pwd)
for ARCH in x64 x86; do
[ -f "$DLLS/sourcevr-$ARCH.dll" ] || { echo "$ARCH: no sourcevr-$ARCH.dll"; continue; }
docker run --rm --user "$(id -u):$(id -g)" -e ARCH=$ARCH -e HOME=/tmp -e WINEPREFIX=/tmp/b/wineprefix -e WINEDEBUG=-all \
  -v "$SRC":/src:ro -v "$HERE":/t:ro -v "${MSVC:-/K3D/temp/win-build/msvc}":/msvc:ro -v "$DLLS":/dll:ro \
  svrtv-winetest sh -ec '
  if [ $ARCH = x64 ]; then T=x86_64-pc-windows-msvc M=X64 L=x86_64 A="-DPLATFORM_64BITS -DWIN64 -D_WIN64 -DCOMPILER_MSVC64" W=wine
  else T=i686-pc-windows-msvc M=X86 L=x86 A="-DCOMPILER_MSVC32 /arch:SSE2" W=wine; fi
  D="-DVPC -DSOURCESDK -DWIN32 -D_WIN32 -DNDEBUG -D_WINDOWS -D_CRT_SECURE_NO_DEPRECATE -D_CRT_NONSTDC_NO_DEPRECATE -DCOMPILER_MSVC -D_DLL_EXT=.dll"
  I="/I/src/common /I/src/public /I/src/public/tier0 /I/src/public/tier1 /imsvc/msvc/crt/include /imsvc/msvc/sdk/include/ucrt /imsvc/msvc/sdk/include/um /imsvc/msvc/sdk/include/shared"
  F="--target=$T -fms-compatibility-version=19.40 /nologo /c /O1 /MT /EHsc /std:c++17 -Wno-everything"
  LP="/LIBPATH:/msvc/crt/lib/$L /LIBPATH:/msvc/sdk/lib/um/$L /LIBPATH:/msvc/sdk/lib/ucrt/$L libcmt.lib libucrt.lib libvcruntime.lib kernel32.lib"
  B=/tmp/b; mkdir -p $B
  clang --driver-mode=cl $F $A $D $I -DTIER0_DLL_EXPORT /t/windows/stub_tier0.cpp /Fo$B/stub.obj
  lld-link /nologo /DLL /MACHINE:$M /OUT:$B/tier0.dll $B/stub.obj $LP
  clang --driver-mode=cl $F $A $D $I /t/test_geometry.cpp /Fo$B/tg.obj
  lld-link /nologo /MACHINE:$M /OUT:$B/test_geometry.exe $B/tg.obj $LP
  cp /dll/sourcevr-$ARCH.dll $B/sourcevr.dll
  cd $B
  $W wineboot -i >/dev/null 2>&1 || true
  for LAY in tabfull sbsfull tab sbs; do
    printf "%s %s: " $ARCH $LAY
    SVRTV_LAYOUT=$LAY SVRTV_LOG=svrtv.log $W test_geometry.exe sourcevr.dll 2>&1 | tr -d "\r" | grep -E "GEOMETRY|LoadLibrary|rc=" | tr "\n" " "; echo
  done
  printf "%s log: " $ARCH; tr -d "\r" < svrtv.log | grep -m3 -E "config|CreateInterface|first call" | tr "\n" " "; echo
'
done
