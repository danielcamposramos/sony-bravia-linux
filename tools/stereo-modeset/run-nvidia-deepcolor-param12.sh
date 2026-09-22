#!/bin/sh
# run-nvidia-deepcolor-param12.sh — reload the proprietary stack with
# max_output_color_depth=12 and bring the desktop back.
#
# v4: the v3 fires (both) removed drm/uvm but 'nvidia' core stayed pinned
# by nvidia_fs (missing from the removal list) and by nvidia_uvm which
# RESURRECTED mid-removal: systemd-udevd's kmod builtin reloads on device
# events, and nvidia-modprobe (setuid) loads on node opens, unless a
# /run/modprobe.d guard no-ops them ("install X /bin/true"). That guard
# plus nvidia_fs-first order plus vtconsole unbind is exactly how
# run-nouveau-test.sh swapped this stack cleanly three times today; v4
# mirrors it, then drops the guard only for the parameterized reload.
# Steps land in $LOG (on /K3D, survives a forced reboot). Twice burned:
# the verdict is gated on the post-reload param readback.
#
# Fire from a desktop terminal:
#   sudo systemd-run --unit=nvidia-deepcolor12 --collect \
#        sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nvidia-deepcolor-param12.sh
#
# After it returns: TV to the NVIDIA input, confirm 1920x1080@60, read
# the signal-info OSD: 12-bit = the default cap is the only gate (PASS);
# 10-bit with param live at 12 = another NVKMS policy gate exists (still
# evidence; keep the log).

LOG=/K3D/temp/run24-nv-param12-steps.log
GUARD=/run/modprobe.d/zz-deepcolor-param12-off.conf
KUSER=daniel
step() { echo "$(date -Is) $*" >> "$LOG"; }
echo "=== run24 nvidia max_output_color_depth=12 attempt v4 $(date -Is) ===" >> "$LOG"

test "$(id -u)" = 0 || { step "not root, abort"; exit 1; }
echo 1 > /proc/sys/kernel/sysrq 2>/dev/null || true

restore() {
	rm -f "$GUARD"
	echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
	modprobe nvidia_drm 2>/dev/null || true   # pulls nvidia + nvidia_modeset back
	systemctl start sddm
	for svc in netdata coolercontrold nvidia-persistenced; do
		systemctl start "$svc" 2>/dev/null || true
	done
	systemctl start docker docker.socket containerd 2>/dev/null || true
	step "desktop + daemons restored"
}

mkdir -p /run/modprobe.d
printf 'blacklist nvidia\nblacklist nvidia_modeset\nblacklist nvidia_drm\nblacklist nvidia_uvm\nblacklist nvidia_fs\ninstall nvidia /bin/true\ninstall nvidia_modeset /bin/true\ninstall nvidia_drm /bin/true\ninstall nvidia_uvm /bin/true\ninstall nvidia_fs /bin/true\n' > "$GUARD"
step "autoload guard installed: $GUARD"

systemctl stop sddm
loginctl terminate-user "$KUSER" 2>/dev/null || true
step "sddm stopped, user session terminated"

systemctl stop docker docker.socket containerd 2>/dev/null
step "docker/containerd stopped"

for svc in nvidia-persistenced coolercontrold netdata; do
	systemctl stop "$svc" 2>/dev/null && step "stopped $svc" || true
done

i=0
while [ $i -lt 20 ]; do
	fuser /dev/dri/card0 /dev/dri/card1 /dev/nvidia* >/dev/null 2>&1 || break
	sleep 1; i=$((i + 1))
done
step "cards free after ${i}s"
if [ $i -ge 20 ]; then
	step "GPU still busy; abort (no test happened)"
	fuser -v /dev/nvidia* /dev/dri/card* >> "$LOG" 2>&1 || true
	restore; exit 3
fi

echo 0 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null && step "vtcon1 unbound" || step "vtcon1 unbind skipped/failed"
echo 0 > /sys/class/vtconsole/vtcon0/bind 2>/dev/null && step "vtcon0 unbound" || step "vtcon0 unbind skipped/failed"

# proven order: fs first, core last
for m in nvidia_fs nvidia_drm nvidia_uvm nvidia_modeset nvidia; do
	grep -q "^$m " /proc/modules || { step "$m not loaded, skip"; continue; }
	try=0
	while :; do
		modprobe -r "$m" 2>>"$LOG" && { step "removed $m"; break; }
		try=$((try + 1))
		if [ $try -gt 4 ]; then
			step "FAILED to remove $m after retries; no test happened"
			lsmod | grep -E "^(nvidia|nouveau)" >> "$LOG" 2>&1 || true
			fuser -v /dev/nvidia* /dev/dri/card* >> "$LOG" 2>&1 | head -12 >> "$LOG" || true
			restore; exit 4
		fi
		sleep 2
	done
done

if lsmod | grep -q "^nvidia"; then
	step "nvidia family still present after teardown; abort (no test happened)"
	lsmod | grep -E "^nvidia" >> "$LOG" 2>&1 || true
	restore; exit 5
fi
step "nvidia family fully unloaded (guard holding)"

# guard blocks our own modprobe too; drop it for the parameter load
rm -f "$GUARD"
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
