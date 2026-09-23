#!/bin/sh
# Recipe used on 2026-09-23 for runs 30-32. To rebuild:
#   git clone --depth 60 -b nouveau-imp-upstr-v120 https://gitlab.freedesktop.org/mohamexiety/nouveau.git /K3D/temp/mohamexiety-nouveau
#   cd /K3D/temp/mohamexiety-nouveau && git am ../../GitHub/sony-bravia-linux/docs/upstream/mohamexiety-nouveau-gcp-cd5-10bpc-2026-09-23.patch
#   B=/K3D/temp/mohamed-bench; mkdir -p $B; lsmod > $B/lsmod.txt; cp /boot/config-$(uname -r) $B/base.config; cp this-file $B/build.sh
#   docker run --rm -v /K3D/temp/mohamexiety-nouveau:/src -v $B:/out debian:testing sh /out/build.sh
# Then: dpkg -i the .deb, pin GRUB_DEFAULT to the normal kernel, grub-reboot into -mohamed-imp,
# and enable mohamed-bench.service (next to this file).
# Build Mohamed Ahmed's nouveau-imp-upstr-v120 (+ our CD=5 fix, commit 83accf62b)
# as Debian kernel packages, plus a nouveau.ko WITHOUT the fix for the A/B.
# Runs inside debian:testing; the tree is /src (mounted), output /out.
set -eu
apt-get update -qq
apt-get install -y -qq --no-install-recommends build-essential bc bison flex libssl-dev libelf-dev dwarves cpio kmod rsync python3 git ca-certificates debhelper libdw-dev zstd >/dev/null
cd /src
git config --global --add safe.directory /src
git log --oneline -1
cp /out/base.config .config
scripts/config --set-str SYSTEM_TRUSTED_KEYS "" --set-str SYSTEM_REVOCATION_KEYS "" \
  --disable DEBUG_INFO --disable DEBUG_INFO_DWARF5 --disable DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT --enable DEBUG_INFO_NONE \
  --disable MODULE_SIG_ALL --module DRM_NOUVEAU
make -s olddefconfig
make -s LSMOD=/out/lsmod.txt localmodconfig </dev/null
scripts/config --module DRM_NOUVEAU --enable DRM_NOUVEAU_BACKLIGHT --module R8169 --module REALTEK_PHY
make -s olddefconfig
grep -E '^CONFIG_DRM_NOUVEAU=' .config
make -s -j12 bindeb-pkg LOCALVERSION=-mohamed-imp KDEB_PKGVERSION=1
cp ../linux-image-*mohamed-imp*_1_amd64.deb /out/ 2>/dev/null || true
cp drivers/gpu/drm/nouveau/nouveau.ko /out/nouveau-with-cd5.ko
# A/B: the same tree without our two lines
git revert --no-edit -n 83accf62b
make -s -j12 M=drivers/gpu/drm/nouveau modules
cp drivers/gpu/drm/nouveau/nouveau.ko /out/nouveau-without-cd5.ko
git revert --abort 2>/dev/null || git checkout -q -- .
git status --short | head
sha256sum /out/*.deb /out/nouveau-*.ko
modinfo -F vermagic /out/nouveau-with-cd5.ko
