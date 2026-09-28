#!/bin/sh
# Windows sourcevr.dll (x64 = the main build; x86 = stock Half-Life 2 today,
# whose Windows hl2.exe is 32-bit), cross-built with clang-cl + lld-link in a
# throwaway container, with the defines and /MT CRT of Valve's
# source_dll_win32_*.vpc. Microsoft's CRT and Windows SDK come from xwin
# (Daniel accepted Microsoft's license, 2026-09-28). tier1 is compiled from
# the SDK as in build32-hl2.sh; memoverride.cpp as in every SDK dll (on
# Windows each dll has its own static CRT heap; tier0's allocator is the
# shared one). tier0/vstdlib: the SDK's x64 import libs; for x86, import libs
# generated from the symbols the module needs.
# Usage: build-win.sh <sdk-src> <outdir> [x64|x86]...
set -e
SRC=$1 OUT=$2; shift 2
[ $# -gt 0 ] || set -- x64 x86
mkdir -p "$OUT"
for ARCH in "$@"; do
docker run --rm --user "$(id -u):$(id -g)" -e ARCH=$ARCH \
  -v "$SRC":/src:ro -v "${MSVC:-/K3D/temp/win-build/msvc}":/msvc:ro -v "$OUT":/out \
  svrtv-wincross sh -ec '
  cd /src
  if [ $ARCH = x64 ]; then T=x86_64-pc-windows-msvc M=X64 L=x86_64 A="-DPLATFORM_64BITS -DWIN64 -D_WIN64 -DCOMPILER_MSVC64"
  else T=i686-pc-windows-msvc M=X86 L=x86 A="-DCOMPILER_MSVC32 /arch:SSE2"; fi
  D="-DVPC -DSOURCESDK -DSOURCE_HAS_FREETYPE -DWIN32 -D_WIN32 -DNDEBUG -D_WINDOWS -D_USRDLL -D_CRT_SECURE_NO_DEPRECATE -D_CRT_NONSTDC_NO_DEPRECATE -D_ALLOW_RUNTIME_LIBRARY_MISMATCH -D_ALLOW_ITERATOR_DEBUG_LEVEL_MISMATCH -D_ALLOW_MSC_VER_MISMATCH -DCOMPILER_MSVC -D_DLL_EXT=.dll -DDLLNAME=sourcevr"
  I="/Icommon /Ipublic /Ipublic/tier0 /Ipublic/tier1 /Ipublic/sourcevr /imsvc/msvc/crt/include /imsvc/msvc/sdk/include/ucrt /imsvc/msvc/sdk/include/um /imsvc/msvc/sdk/include/shared"
  F="--target=$T -fms-compatibility-version=19.40 /nologo /c /O2 /MT /EHsc /Zc:threadSafeInit- /Zc:inline /Gw /Zc:__cplusplus /std:c++17 -Wno-everything"
  O=/tmp/o; mkdir -p $O
  for f in sourcevr_display/sourcevr_display.cpp public/tier0/memoverride.cpp \
           tier1/convar.cpp tier1/tier1.cpp tier1/strtools.cpp tier1/characterset.cpp \
           tier1/utlbuffer.cpp tier1/generichash.cpp tier1/strtools_unicode.cpp tier1/utlstring.cpp tier1/qsort_s.cpp; do
    [ -f "$f" ] || { echo "skip $f"; continue; }
    clang --driver-mode=cl $F $A $D $I "$f" /Fo$O/$(basename "$f" .cpp).obj
  done
  if [ $ARCH = x64 ]; then LIBS="lib/public/x64/tier0.lib lib/public/x64/vstdlib.lib"
  else
    # x86 import libs: every symbol the objects import (__imp_) that the
    # x64 tier0/vstdlib libs of the SDK export (same source): C names without
    # the x86 leading underscore, data as DATA, C++ names as they are.
    llvm-nm --undefined-only $O/*.obj | awk "{print \$NF}" | grep "^__imp_" | sed "s/^__imp_//" | sort -u > $O/imports.txt
    for lib in tier0 vstdlib; do
      llvm-nm lib/public/x64/$lib.lib 2>/dev/null | awk "NF>=2 {print \$NF}" | sed "s/^__imp_//" | sort -u > $O/$lib.x64
      { echo "LIBRARY $lib.dll"; echo EXPORTS
        while read -r s; do
          case "$s" in
          \?*) k=${s%%@@*}; grep -q "^$(printf %s "$k" | sed "s/[?]/[?]/g")@@" $O/$lib.x64 && echo "  $s" ;;
          *) c=${s#_}; grep -qxF "$c" $O/$lib.x64 && case "$c" in g_*) echo "  $c DATA" ;; *) echo "  $c" ;; esac ;;
          esac
        done < $O/imports.txt; } > $O/$lib.def
      llvm-dlltool -m i386 -d $O/$lib.def -l $O/$lib.lib -D $lib.dll
      cp $O/$lib.def /out/$lib-x86.def
    done
    LIBS="$O/tier0.lib $O/vstdlib.lib"
  fi
  lld-link /nologo /DLL /MACHINE:$M /OUT:/out/sourcevr-$ARCH.dll $O/*.obj $LIBS \
    /LIBPATH:/msvc/crt/lib/$L /LIBPATH:/msvc/sdk/lib/um/$L /LIBPATH:/msvc/sdk/lib/ucrt/$L \
    libcmt.lib libucrt.lib libvcruntime.lib kernel32.lib user32.lib /OPT:REF /OPT:ICF
  llvm-readobj --coff-imports /out/sourcevr-$ARCH.dll | grep -E "Name:|Symbol:" | tr -s " " | tr "\n" " "; echo
  llvm-readobj --coff-exports /out/sourcevr-$ARCH.dll | grep "Name:" | tr -s " "
'
done
sha256sum "$OUT"/sourcevr-*.dll
