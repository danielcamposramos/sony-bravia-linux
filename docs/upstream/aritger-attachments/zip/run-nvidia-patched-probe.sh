#!/bin/sh
# run-nvidia-patched-probe.sh — A/B probe: stock nvidia-drm vs the
# stereo_allowed community patch, same boot, one detached run.
#
# Purpose: answer NVIDIA/open-gpu-kernel-modules#1382 (aritger) with a
# MEASURED before/after, not a source-reading prediction: does setting
# connector->stereo_allowed change the mode list on 615.71.09 (MODE_NO_STEREO
# gate in __drm_helper_update_and_validate -> drm_mode_validate_flag), given
# that NvKmsKapiDisplayMode has no stereo member and
# nvkms_display_mode_to_drm_mode() maps no DRM_MODE_FLAG_3D_* bits?
#
# Sequence: wait for HPD (IR-switch the TV to the NVIDIA HDMI input, up to
# 120 s) -> probe STOCK module -> drop sddm + user session -> rmmod nvidia_drm,
# insmod the patched build from /usr/src -> probe PATCHED module -> restore
# stock module -> sddm back. The AMD desktop session is dead for the whole
# middle section; this terminal's Claude session goes with it. Run detached:
#
#   sudo systemd-run --unit=nvidia-patched-probe --collect \
#        sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nvidia-patched-probe.sh
#
# Recovery if the patch probe fails: the script re-modprobes the stock
# nvidia_drm and restarts sddm; worst case Ctrl+Alt+Del, SysRq armed.

TOOLS=/K3D/GitHub/sony-bravia-linux/tools
LOG=/home/daniel/nvidia-patched-probe.log
PROBE=$TOOLS/stereo-kms-probe/stereo-probe
CARD=/dev/dri/card1
CONN=HDMI-A-2
SYSCONN=/sys/class/drm/card1-HDMI-A-2
PATCHED_KO=/usr/src/nvidia-615.71.09/kernel-open/nvidia-drm.ko
KUSER=daniel

exec >>"$LOG" 2>&1

restore() {
	echo "== restore: stock module + desktop =="
	rmmod nvidia_drm 2>/dev/null
	modprobe nvidia_drm && echo "stock nvidia_drm restored"
	systemctl start sddm
	echo "=== done $(date -Is) ==="
	sync
}

echo "=== nvidia-patched-probe $(date -Is) ==="
echo "kernel $(uname -r); nvidia-drm $(modinfo -F version nvidia_drm 2>/dev/null)"
echo "STOCK srcversion: $(cat /sys/module/nvidia_drm/srcversion 2>/dev/null)"
echo "PATCHED ko: $PATCHED_KO md5=$(md5sum "$PATCHED_KO" 2>/dev/null | cut -d' ' -f1)"

test "$(id -u)" = 0 || { echo "run as root"; exit 1; }
test -f "$PATCHED_KO" || { echo "patched module missing: $PATCHED_KO (build first)"; exit 1; }
test -x "$PROBE" || { echo "probe missing: $PROBE"; exit 1; }

echo 1 > /proc/sys/kernel/sysrq 2>/dev/null || true

# Phase 1: HPD dance with the desktop still up. Daniel IR-switches the TV to
# the NVIDIA input; the probe below is read-only and coexists with the session.
i=0
while [ $i -lt 120 ]; do
	[ "$(cat $SYSCONN/status 2>/dev/null)" = connected ] && break
	sleep 1; i=$((i + 1))
done
[ "$(cat $SYSCONN/status 2>/dev/null)" = connected ] || { echo "no HPD in 120s - abort"; exit 1; }
echo "HPD live after ${i}s ($(cat $SYSCONN/status))"

echo "=== PROBE 1/2: STOCK nvidia-drm (srcversion above) ==="
"$PROBE" "$CARD" "$CONN"

# Phase 2: display down, module swap.
echo "== dropping display stack =="
systemctl stop sddm
loginctl terminate-user "$KUSER" 2>/dev/null || true
i=0
while [ $i -lt 30 ]; do
	fuser /dev/dri/card1 /dev/nvidia* >/dev/null 2>&1 || break
	sleep 1; i=$((i + 1))
done
echo "fds free after ${i}s"

if rmmod nvidia_drm; then
	echo "stock nvidia_drm unloaded"
else
	echo "rmmod nvidia_drm failed - cannot swap module"
	restore
	exit 1
fi

if insmod "$PATCHED_KO"; then
	echo "patched nvidia-drm.ko loaded"
else
	echo "insmod of patched module failed"
	modprobe nvidia_drm
	systemctl start sddm
	exit 1
fi
echo "PATCHED srcversion: $(cat /sys/module/nvidia_drm/srcversion 2>/dev/null)"

sleep 2	# let NVKMS re-probe the connector before reading modes

echo "=== PROBE 2/2: PATCHED nvidia-drm (stereo_allowed=true) ==="
"$PROBE" "$CARD" "$CONN"

# Phase 3: always restore.
restore
