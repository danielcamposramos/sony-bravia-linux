#!/bin/sh
# run-nvidia-deepcolor-param12.sh — reload the proprietary stack with
# max_output_color_depth=12 and bring the desktop back.
#
# v3: grafts in the nouveau harness's proven teardown (runs 2-5 swapped
# this stack cleanly three times today) after two no-test attempts:
# attempt 1 (v1 runbook) raced dying kwin (modprobe FATAL: nvidia_drm in
# use); attempt 2 (v2) waited 60 s but nvidia-persistenced/coolercontrold/
# netdata hold the NVML nodes regardless of the desktop. v3 terminates
# the user session via loginctl and stops the NVML daemons FIRST, like
# run-nouveau-test.sh does, then reloads with the parameter and gates the
# verdict on the post-reload readback. Steps land in $LOG (on /K3D, so
# they survive even a forced reboot).
#
# Fire from a desktop terminal:
#   sudo systemd-run --unit=nvidia-deepcolor12 --collect \
#        sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nvidia-deepcolor-param12.sh
#
# After it returns (~30-60 s): switch the TV to the NVIDIA input, confirm
# 1920x1080@60, read the signal-info OSD: 12-bit = PASS (the default cap
# is the only gate), 10-bit with param live at 12 = another NVKMS policy
# gate exists (still evidence; keep the log).

LOG=/K3D/temp/run24-nv-param12-steps.log
KUSER=daniel
step() { echo "$(date -Is) $*" >> "$LOG"; }
echo "=== run24 nvidia max_output_color_depth=12 attempt v3 $(date -Is) ===" >> "$LOG"

test "$(id -u)" = 0 || { step "not root, abort"; exit 1; }
echo 1 > /proc/sys/kernel/sysrq 2>/dev/null || true

restore() {
	systemctl start sddm
	for svc in netdata coolercontrold nvidia-persistenced; do
		systemctl start "$svc" 2>/dev/null || true
	done
	systemctl start docker docker.socket containerd 2>/dev/null || true
	step "desktop + daemons restored"
}

systemctl stop sddm
loginctl terminate-user "$KUSER" 2>/dev/null || true
step "sddm stopped, user session terminated"

systemctl stop docker docker.socket containerd 2>/dev/null
step "docker/containerd stopped"

# NVML daemons survive the desktop drop and pin the nvidia modules:
for svc in nvidia-persistenced coolercontrold netdata; do
	systemctl stop "$svc" 2>/dev/null && step "stopped $svc" || true
done

# wait until nothing holds the NVIDIA nodes (~20 s budget, proven value)
i=0
while [ $i -lt 20 ]; do
	fuser /dev/dri/card0 /dev/dri/card1 /dev/nvidia* >/dev/null 2>&1 || break
	sleep 1; i=$((i + 1))
done
step "cards free after ${i}s"
if [ $i -ge 20 ]; then
	step "GPU still busy; abort reload (no test happened)"
	fuser -v /dev/nvidia* /dev/dri/card* >> "$LOG" 2>&1 || true
	restore; exit 3
fi

# per-module removal with retries (proven order)
ok=yes
for m in nvidia_drm nvidia_uvm nvidia_modeset nvidia; do
	grep -q "^$m " /proc/modules || { step "$m already out"; continue; }
	try=0
	while :; do
		modprobe -r "$m" 2>>"$LOG" && { step "removed $m"; break; }
		try=$((try + 1))
		if [ $try -gt 4 ]; then
			step "FAILED to remove $m after retries; no test happened"
			lsmod | grep -E "^(nvidia|nouveau)" >> "$LOG" 2>&1 || true
			modprobe nvidia_drm 2>/dev/null || true
			restore; exit 4
		fi
		sleep 2
	done
done

# clean reload WITH the parameter
modprobe nvidia_modeset max_output_color_depth=12 hdmi_deepcolor=1 2>>"$LOG"
sleep 1
V=$(cat /sys/module/nvidia_modeset/parameters/max_output_color_depth 2>/dev/null)
H=$(cat /sys/module/nvidia_modeset/parameters/hdmi_deepcolor 2>/dev/null)
step "AFTER RELOAD: max_output_color_depth=$V hdmi_deepcolor=$H"

restore
if [ "$V" = "12" ] && [ "$H" = "Y" ]; then
	step "VERDICT-READY: param live at 12 - read the TV OSD now"
else
	step "VERDICT-FAIL: reload did not take (v=$V h=$H); no test happened"
fi
exit 0
