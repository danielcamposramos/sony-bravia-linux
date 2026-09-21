#!/bin/sh
# run-nvidia-test.sh — proprietary nvidia-drm 3D test harness — detached form.
# The 615-series blob is the TEST SUBJECT here, so unlike the amdgpu harness
# nothing is swapped or removed: sddm stops, the session is terminated, and
# nvidia_drm stays loaded the whole time. The client drives plain 2D
# 1920x1080@60 on card1/HDMI-A-2 and injects the HDMI 1.4 3D VSIF through the
# NV_HDMI_VSIF_METADATA connector blob (userspace -> open glue -> NVKMS).
# Frame packing is out of scope on this leg: its link timing is doubled and
# the injection only announces the packing.
#
# From the desktop terminal:
#
#   sudo systemd-run --unit=nvidia-3d-test --collect \
#        sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nvidia-test.sh [sbs|tab|all]
#
# TV choreography (the NVIDIA cable feeds a SECOND HDMI input of the
# KDL-46HX855, which only asserts HPD while that input is selected):
#   fire the command -> screens settle to consoles; switch the TV to the
#   NVIDIA input with the IR -> the harness polls the connector and proceeds
#   the moment it goes live (45s budget, switch moment lands in the log) ->
#   watch the 90s-per-layout windows -> when the desktop returns, switch the
#   TV back to the AMD input. This terminal on the DP monitor stays alive
#   throughout (that output is on card0, untouched).
#
# Log: /home/daniel/stereo-3d-test.log  Recovery: nothing was unloaded, so a
# stuck run still has consoles; Ctrl+Alt+Del reboots, SysRq is armed.

TOOLS=/K3D/GitHub/sony-bravia-linux/tools
LOG=/home/daniel/stereo-3d-test.log
CARD=/dev/dri/card1
CONN=HDMI-A-2
SYSCONN=/sys/class/drm/card1-HDMI-A-2
TEST_SECONDS=90
KUSER=daniel
MODE="${1:-sbs}"

case "$MODE" in
	sbs|tab|all) ;;
	*) echo "usage: $0 [sbs|tab|all]" >&2; exit 2 ;;
esac

exec >>"$LOG" 2>&1
echo "=== nvidia-3d-test $(date -Is) layout=$MODE ==="
echo "module under test: proprietary nvidia-drm $(modinfo -F version nvidia_drm 2>/dev/null) on $(uname -r) (no swap, no removal; VSIF injection client)"

test "$(id -u)" = 0 || { echo "run as root"; exit 1; }

# arm SysRq for the whole run
echo 1 > /proc/sys/kernel/sysrq 2>/dev/null || true

systemctl stop sddm
loginctl terminate-user "$KUSER" 2>/dev/null || true

# terminate-user is async; the session holds card fds (and the NVIDIA
# control devices) while it dies. Drain before touching the card.
i=0
while [ $i -lt 25 ]; do
	fuser /dev/dri/card0 /dev/dri/card1 /dev/nvidia* >/dev/null 2>&1 || break
	sleep 1; i=$((i + 1))
done
echo "fds free after ${i}s"

# The Sony keeps inactive HDMI inputs' hotplug dark. Wait for Daniel to
# IR-switch the TV to the NVIDIA input: the connector flips to connected.
i=0
while [ $i -lt 45 ]; do
	[ "$(cat $SYSCONN/status 2>/dev/null)" = connected ] && break
	sleep 1; i=$((i + 1))
done
if [ "$(cat $SYSCONN/status 2>/dev/null)" = connected ]; then
	echo "HPD live: $CONN connected after ${i}s (TV on the NVIDIA input)"
else
	echo "HPD never came up (45s) -- restoring desktop without testing"
	systemctl start sddm
	exit 1
fi

echo "--- baseline probe on the blob (stereo modes are pruned: expect zeros) ---"
"$TOOLS/stereo-kms-probe/stereo-probe" "$CARD" "$CONN" || true

LAYOUTS="$MODE"
[ "$MODE" = all ] && LAYOUTS="tab sbs"
FIRST=1
for L in $LAYOUTS; do
	if [ $FIRST = 0 ]; then
		sleep 5
		echo "--- switching to $L (TV may blink back to 2D) ---"
	fi
	FIRST=0
	echo "--- firing the $L 2D modeset + injected 3D VSIF for ${TEST_SECONDS}s -- watch the TV ---"
	timeout "$TEST_SECONDS" "$TOOLS/stereo-modeset/stereo-modeset" "$CARD" "$CONN" "$L" isolate vsif </dev/null || true
done

systemctl start sddm
echo "=== done $(date -Is); desktop returning -- switch the TV back to the AMD input ==="
exit 0
