#!/bin/sh
# stereo-modeset test harness — run from a real VT (Ctrl+Alt+F2) as root, NOT
# from inside the desktop session:
#
#   sudo sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-3d-test.sh
#
# What it does:
#   1. stops sddm (the desktop goes away — save your work first)
#   2. swaps the running amdgpu for the K3D-patched build from /tmp/k317
#   3. runs the stereo-probe so the new stereo mode list is on record
#   4. runs stereo-modeset on the TV (HDMI-A-1): watch for the set switching
#      into 3D by itself, then press q to quit
#   5. restarts sddm; the patched driver stays loaded for the session
#
# Recovery if anything wedges: reboot — the patch never touches /lib/modules.

set -e
K3DPATCH=/tmp/k317/linux-source-7.0/drivers/gpu/drm/amd/amdgpu/amdgpu.ko
TOOLS=/K3D/GitHub/sony-bravia-linux/tools

test -f "$K3DPATCH" || { echo "patched module missing: $K3DPATCH"; exit 1; }
test "$(id -u)" = 0 || { echo "run as root"; exit 1; }

WANT="$(uname -r) SMP preempt mod_unload"
HAVE="$(modinfo -F vermagic "$K3DPATCH")"
test "$HAVE" = "$WANT" || { echo "vermagic mismatch: have '$HAVE' want '$WANT'"; exit 1; }

systemctl stop sddm
sleep 1
modprobe -r amdgpu || { echo "amdgpu unload failed"; systemctl start sddm; exit 1; }
insmod "$K3DPATCH"
sleep 2

echo "=== probe with patched driver (stereo modes should appear) ==="
"$TOOLS/stereo-kms-probe/stereo-probe" /dev/dri/card0 HDMI-A-1

echo "=== firing the stereo modeset — watch the TV ==="
"$TOOLS/stereo-modeset/stereo-modeset" /dev/dri/card0 HDMI-A-1

systemctl start sddm
echo "done. desktop is back; patched amdgpu remains loaded until reboot."
