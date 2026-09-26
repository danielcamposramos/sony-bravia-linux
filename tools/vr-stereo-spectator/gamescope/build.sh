#!/bin/sh
# Builds Debian's gamescope 3.16.24+ds-2 (64-bit) with nested-present-mode.patch,
# in a throwaway debian:testing container. Output: out/*.deb (not installed).
set -e
cd "$(dirname "$0")"
mkdir -p out
docker run --rm -v "$PWD:/w" debian:testing sh -ec '
  sed -i -e "s/^Types: deb$/Types: deb deb-src/" -e "s/^Components: main$/Components: main contrib/" /etc/apt/sources.list.d/debian.sources
  export DEBIAN_FRONTEND=noninteractive; apt-get update -qq
  apt-get install -y -qq dpkg-dev devscripts quilt >/dev/null
  mkdir -p /b && cd /b
  apt-get source -qq gamescope=3.16.24+ds-2
  cd gamescope-3.16.24*
  apt-get build-dep -y -qq . >/dev/null
  cp /w/nested-present-mode.patch debian/patches/
  echo nested-present-mode.patch >> debian/patches/series
  QUILT_PATCHES=debian/patches quilt push -a >/dev/null
  grep -c ePresentMode src/rendervulkan.cpp
  DEB_BUILD_OPTIONS="nocheck parallel=12" dpkg-buildpackage -b -uc -us >/w/out/build.log 2>&1
  cp ../*.deb /w/out/
  chown -R '"$(id -u):$(id -g)"' /w/out
'
ls -la out/*.deb
