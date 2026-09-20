#!/bin/sh
# stereo-modeset test harness — detached form. From the desktop terminal:
#
#   sudo systemd-run --unit=stereo-3d-test --collect \
#        sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-3d-test.sh
#
# The service survives the desktop going down. Timeline:
#   +0s   sddm stops and the user session is terminated (screens dark)
#   +2s   fbcon unbound, running amdgpu swapped for the K3D-patched build
#   +4s   probe runs on HDMI-A-1 (stereo modes now listed — into the log)
#   +6s   stereo-modeset picks the 1080p60 SBS-half mode on the TV
#         PASS SIGNAL: the Sony switches into 3D by itself, three colored
#         boxes at different depths, drifting slowly
#   +96s  sddm restarts; autologin returns the desktop. Patched driver
#         stays loaded until the next reboot.
#
# Log: /home/daniel/stereo-3d-test.log
# Recovery if anything wedges: the machine is ALIVE even when pictureless
# (no GPU driver = no console) -- Ctrl+Alt+Del still reboots, the full
# restore path below is automatic, and SysRq keys are armed for the run.

K3DPATCH=/K3D/temp/k317/linux-source-7.0/drivers/gpu/drm/amd/amdgpu/amdgpu.ko
TOOLS=/K3D/GitHub/sony-bravia-linux/tools
LOG=/home/daniel/stereo-3d-test.log
TEST_SECONDS=90
KUSER=daniel

exec >>"$LOG" 2>&1
echo "=== stereo-3d-test $(date -Is) ==="

# arm SysRq for the whole run: if we ever leave the console dead,
# Alt+SysRq+... still reaches the kernel
echo 1 > /proc/sys/kernel/sysrq 2>/dev/null || true

test -f "$K3DPATCH" || { echo "patched module missing: $K3DPATCH"; exit 1; }
test "$(id -u)" = 0 || { echo "run as root"; exit 1; }
WANT="$(uname -r) SMP preempt mod_unload"
HAVE="$(modinfo -F vermagic "$K3DPATCH" | sed 's/[[:space:]]*$//')"
test "$HAVE" = "$WANT" || { echo "vermagic mismatch: have '$HAVE' want '$WANT'"; exit 1; }

systemctl stop sddm
loginctl terminate-user "$KUSER" 2>/dev/null || true

# wait for DRM fds to drain
i=0
while [ $i -lt 15 ]; do
	fuser /dev/dri/card0 >/dev/null 2>&1 || break
	sleep 1; i=$((i + 1))
done
echo "card0 free after ${i}s"

# fbcon holds the module too: unbind it while the swap happens
echo 0 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
if ! modprobe -r amdgpu; then
	echo "amdgpu unload FAILED -- restoring desktop"
	echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
	systemctl start sddm
	exit 1
fi
# insmod resolves no dependencies, and "modprobe -r" took the whole unused
# dep chain down with it (run 4 died exactly here: "Unknown symbol in module").
# Preload the chain by name from the stock module description; symbol needs
# are identical, the patch adds no new module dependencies.
DEPS="$(modinfo -F depends amdgpu 2>/dev/null | tr ',' ' ')"
echo "preloading deps: $DEPS"
[ -n "$DEPS" ] && modprobe $DEPS

if ! insmod "$K3DPATCH"; then
	echo "insmod of patched module FAILED -- restoring stock amdgpu and desktop"
	modprobe amdgpu 2>&1 || true
	echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
	systemctl start sddm
	exit 1
fi
echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
sleep 2

echo "--- probe with patched driver (stereo modes should appear) ---"
"$TOOLS/stereo-kms-probe/stereo-probe" /dev/dri/card0 HDMI-A-1 || true

echo "--- firing the stereo modeset for ${TEST_SECONDS}s -- watch the TV ---"
timeout "$TEST_SECONDS" "$TOOLS/stereo-modeset/stereo-modeset" /dev/dri/card0 HDMI-A-1 </dev/null || true

# if the patched driver took the device down with it, swapping back to stock
# BEFORE sddm restarts is the difference between "desktop returns" and
# "alive but pictureless" (run 4's black screen)
if [ ! -e /dev/dri/card0 ]; then
	echo "no DRM device after test -- falling back to stock amdgpu"
	modprobe -r amdgpu 2>/dev/null || true
	modprobe amdgpu 2>&1 || true
	sleep 2
fi

systemctl start sddm
echo "=== done $(date -Is); patched amdgpu remains loaded until reboot ==="
exit 0
