#!/bin/sh
# nouveau stereo VERIFICATION harness (front 2). Source says nouveau already
# wires stereo: stereo_allowed=true (nouveau_connector.c) + VSIF on commit
# (dispnv50/disp.c). This script only gathers the hardware proof on the
# RTX 3060 -> second HDMI input of the KDL-46HX855. Expected pass signal:
# the TV switches to 3D by itself on the SBS-half modeset.
#
#   sudo systemd-run --unit=nouveau-3d-test --collect \
#        sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nouveau-test.sh
#
# Timeline mirrors the proven AMD run: desktop drops (~2 min), nvidia driver
# stack swapped for nouveau, probe + modeset on card1, stack swapped back,
# desktop restored. Recovery identical: machine stays alive even if
# pictureless; Ctrl+Alt+Del reboots; SysRq is armed.
#
# Daniel: when the screens go dark, switch the TV to the NVIDIA-driven input.

TOOLS=/K3D/GitHub/sony-bravia-linux/tools
LOG=/var/log/nouveau-3d-test.log          # service context denied /home/daniel writes (see below)
HOMELOG=/home/daniel/nouveau-3d-test.log  # mirrored here at every exit
TEST_SECONDS=90
KUSER=daniel

# first, before any redirect: if this was pastebroken into two visual lines,
# the path-only half lands here running UNPRIVILEGED. Fail loud, not silently.
if [ "$(id -u)" != 0 ]; then
	echo "run-nouveau-test: must run as root -- one line:" >&2
	echo "sudo systemd-run --unit=nouveau-3d-test --collect sh $0" >&2
	exit 1
fi

exec >>"$LOG" 2>&1
# root got EACCES redirecting straight into $HOMELOG from the systemd-run
# service context on 2026-09-20 (file: root 644 on ext4, no immutable attr).
# Log in root-land, mirror home on every exit path.
trap 'cp -f "$LOG" "$HOMELOG" 2>/dev/null; chown "$KUSER":"$KUSER" "$HOMELOG" 2>/dev/null; true' 0
echo "=== nouveau-3d-test $(date -Is) ==="
findmnt /home/daniel /var/log 2>/dev/null

echo 1 > /proc/sys/kernel/sysrq 2>/dev/null || true
test "$(id -u)" = 0 || { echo "run as root"; exit 1; }

NOUVEAU_KO="$(modinfo -n nouveau 2>/dev/null)"
test -n "$NOUVEAU_KO" || { echo "nouveau not found for $(uname -r)"; exit 1; }
echo "nouveau module: $NOUVEAU_KO"

systemctl stop sddm
loginctl terminate-user "$KUSER" 2>/dev/null || true

# NVML daemons survive the desktop drop and pin the nvidia modules
# (run 1: nvidia_uvm "in use" with the desktop already gone). Pause them
# for the test window; restarted below before the desktop returns.
for svc in nvidia-persistenced coolercontrold netdata; do
	systemctl stop "$svc" 2>/dev/null && echo "stopped $svc" || true
done

i=0
while [ $i -lt 20 ]; do
	fuser /dev/dri/card0 /dev/dri/card1 /dev/nvidia* >/dev/null 2>&1 || break
	sleep 1; i=$((i + 1))
done
echo "cards free after ${i}s"

# fbcon spans the nvidia framebuffer too when nvidia-drm.modeset=1
echo 0 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
echo 0 > /sys/class/vtconsole/vtcon0/bind 2>/dev/null || true

# reverse dependency order, with retry: stragglers (netdata's poll cycle)
# reopen nodes for a moment after being stopped
try=0
for m in nvidia_fs nvidia_drm nvidia_uvm nvidia_modeset nvidia; do
	while true; do
		if modprobe -r "$m" 2>&1; then
			echo "removed $m"
			break
		fi
		try=$((try + 1))
		if [ $try -gt 4 ]; then
			echo "FAILED to remove $m after retries:"; lsmod | grep -E "^nvidia"
			echo "--- stray holders:"; fuser -v /dev/nvidia* 2>&1 | head -15
			echo "restoring desktop"
			echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
			for svc in netdata coolercontrold nvidia-persistenced; do systemctl start "$svc" 2>/dev/null || true; done
			systemctl start sddm
			exit 1
		fi
		echo "remove $m busy (attempt $try), retrying"; lsmod | grep -E "^nvidia_"
		sleep 2
	done
done

echo "--- loading nouveau (GSP init on GA106 can take ~10s) ---"
if ! modprobe nouveau 2>&1; then
	echo "modprobe nouveau FAILED -- restoring nvidia stack and desktop"
	modprobe nvidia_drm 2>&1 || true
	sleep 2
	echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
	systemctl start sddm
	exit 1
fi
i=0
while [ $i -lt 30 ]; do
	[ -e /dev/dri/card1 ] && break
	sleep 1; i=$((i + 1))
done
echo "card1 reappeared after ${i}s under: $(cat /sys/class/drm/card1/device/uevent 2>/dev/null | grep DRIVER)"

echo "--- connectors on card1:"
ls /sys/class/drm/ | grep "^card1-" || echo "none"

# find the first connected HDMI connector that shows stereo modes
CONN=""
for c in $(ls /sys/class/drm/ 2>/dev/null | grep "^card1-HDMI" | sed 's/card1-//'); do
	echo "--- probing card1 $c:"
	"$TOOLS/stereo-kms-probe/stereo-probe" /dev/dri/card1 "$c" 2>&1 || continue
	if "$TOOLS/stereo-kms-probe/stereo-probe" /dev/dri/card1 "$c" 2>/dev/null | grep -q "stereo mode:"; then
		CONN="$c"
		break
	fi
done
echo "chosen connector: ${CONN:-none}"

if [ -n "$CONN" ]; then
	echo "--- firing the stereo modeset for ${TEST_SECONDS}s on card1 $CONN"
	echo "    (Daniel: TV input for the NVIDIA card should auto-switch to 3D)"
	timeout "$TEST_SECONDS" stdbuf -oL "$TOOLS/stereo-modeset/stereo-modeset" /dev/dri/card1 "$CONN" </dev/null || true
else
	echo "no stereo-capable connector found on nouveau -- see probe output above"
fi

echo "--- restoring nvidia stack"
modprobe -r nouveau 2>&1 || true
modprobe nvidia_drm 2>&1 || true
sleep 2
echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
for svc in netdata coolercontrold nvidia-persistenced; do
	systemctl start "$svc" 2>/dev/null && echo "restarted $svc" || true
done

systemctl start sddm
echo "=== done $(date -Is) ==="
exit 0
