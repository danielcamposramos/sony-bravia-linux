# Windows builds of the display module, from Linux

The module (`src/sourcevr_display` on [the Sparky Stereo OS fork of Valve's SDK](https://github.com/Sparky-OS/source-sdk-2013/tree/stereo3d-full-res-wip/src/sourcevr_display)) builds for Windows in Valve's own route (VPC, Visual Studio 2022). These scripts build it from Linux instead, for testing before a Windows boot, and load it under Wine.

Today's Half-Life 2 on Windows is 32-bit (Steam launches `hl2.exe` and lists no 64-bit Half-Life 2; Half-Life 2: Deathmatch has `hl2mp_win64.exe`), so both architectures are built: x86 for Half-Life 2 today, x64 for the 64-bit Source engines and the future (Daniel: 64-bit is the main one).

| file | what it does |
|---|---|
| `Dockerfile.wincross` | clang 19, lld, llvm on Debian trixie (image `svrtv-wincross`) |
| `Dockerfile.winetest` | the same plus Wine 10, 64 and 32-bit (image `svrtv-winetest`) |
| `prepare-cross-src.sh` | copies the SDK tree and applies two clang shims to Valve's headers, in the copy only: `__m128`'s `m128_f32` member (MSVC's headers only) and `__restrict` on member functions |
| `build-win.sh` | `sourcevr-x64.dll` and `sourcevr-x86.dll` with clang-cl and lld-link, Valve's defines from `source_dll_win32_*.vpc`, static CRT (`/MT`), `memoverride.cpp` as in every SDK dll; x64 links the SDK's `tier0.lib`, x86 gets import libs generated from the symbols the module takes from tier0 |
| `stub_tier0.cpp` | a stand-in `tier0.dll` with the six symbols the module imports, for loading it outside the game |
| `test-win.sh` | builds the stub and `../test_geometry.cpp` for Windows and runs the geometry test under Wine, four formats, both architectures |

Microsoft's CRT and Windows SDK come from [xwin](https://github.com/Jake-Shadle/xwin) (`xwin --accept-license --arch x86,x86_64 splat --output <dir>`; accepting Microsoft's license terms is the user's decision, Daniel's here on 2026-09-28), mounted from `$MSVC` (default `/K3D/temp/win-build/msvc`).

```sh
docker build -t svrtv-wincross -f Dockerfile.wincross .
docker build -t svrtv-winetest -f Dockerfile.winetest .
./prepare-cross-src.sh /path/to/source-sdk-2013/src /path/to/src-cross
./build-win.sh /path/to/src-cross /path/to/out          # x64 and x86
./test-win.sh /path/to/src-cross /path/to/out
```

Result on 2026-09-28 (fork commit `4c79423`): both DLLs link against tier0 only (six symbols) and kernel32, no runtime to install; under Wine both load, find their own folder, write their log there and pass the geometry test in all four formats. What Wine cannot show is the game itself: the first in-game run on Windows is Daniel's test. The end-user packages are assembled by `../package/make-packages.sh`.
