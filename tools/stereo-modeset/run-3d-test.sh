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
# Recovery if anything wedges: reboot — the patch never touches /lib/modules.

K3DPATCH=/tmp/k317/linux-source-7.0/drivers/gpu/drm/amd/amdgpu/amdgpu.ko
TOOLS=/K3D/GitHub/sony-bravia-linux/tools
LOG=/home/daniel/stereo-3d-test.log
TEST_SECONDS=90
KUSER=daniel

exec >>"$LOG" 2>&1
echo "=== stereo-3d-test $(date -Is) ==="

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
insmod "$K3DPATCH"
echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
sleep 2

echo "--- probe with patched driver (stereo modes should appear) ---"
"$TOOLS/stereo-kms-probe/stereo-probe" /dev/dri/card0 HDMI-A-1 || true

echo "--- firing the stereo modeset for ${TEST_SECONDS}s -- watch the TV ---"
timeout "$TEST_SECONDS" "$TOOLS/stereo-modeset/stereo-modeset" /dev/dri/card0 HDMI-A-1 </dev/null || true

systemctl start sddm
echo "=== done $(date -Is); patched amdgpu remains loaded until reboot ==="
exit 0
