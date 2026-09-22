#!/bin/sh
# run-nvidia-deepcolor-param12.sh — reload the proprietary stack with
# max_output_color_depth=12 and bring the desktop back. Built after the
# 15:51 first attempt raced the dying Wayland session (modprobe: FATAL:
# Module nvidia_drm is in use; param never applied; journal boot -1).
# Every step lands in $LOG (on /K3D = survives a forced reboot).
#
# Fire from a desktop terminal:
#   sudo systemd-run --unit=nvidia-deepcolor12 --collect \
#        sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nvidia-deepcolor-param12.sh
#
# After it returns: switch the TV to the NVIDIA input, confirm
# 1920x1080@60, read the signal-info OSD: 12-bit = PASS, 10-bit = the
# default-cap thesis is wrong (still evidence; keep the log).

exec >/dev/null 2>&1   # everything we print goes to $LOG explicitly
LOG=/K3D/temp/run24-nv-param12-steps.log
step() { echo "$(date -Is) $*" >> "$LOG"; }
echo "=== run24 nvidia max_output_color_depth=12 attempt $(date -Is) ===" >> "$LOG"

test "$(id -u)" = 0 || { step "not root, abort"; exit 1; }
echo 1 > /proc/sys/kernel/sysrq 2>/dev/null || true

systemctl stop sddm
step "sddm stopped"

# pause docker so nothing holds nvidia-uvm
systemctl stop docker containerd 2>/dev/null
step "docker/containerd stopped"

# wait until no process holds the NVIDIA nodes (max 60 s)
i=0
while fuser -s /dev/dri/card1 /dev/dri/card1-* /dev/nvidia* 2>/dev/null; do
	i=$((i+1)); [ "$i" -ge 30 ] && { step "GPU still busy after 60s, abort reload; starting sddm back"; systemctl start sddm; systemctl start docker 2>/dev/null; exit 3; }
	sleep 2
done
step "GPU nodes free after ~$((i*2))s"

# remove with retries; verify with lsmod
ok=no
for j in $(seq 1 10); do
	modprobe -r nvidia_drm nvidia_uvm nvidia_modeset nvidia 2>>"$LOG" && { ok=yes; break; }
	sleep 2
done
step "unload ok=$ok"
lsmod | grep nvidia >> "$LOG" 2>&1 || step "no nvidia modules loaded"

# load fresh WITH the parameter
modprobe nvidia_modeset max_output_color_depth=12 hdmi_deepcolor=1 2>>"$LOG"
sleep 1
V=$(cat /sys/module/nvidia_modeset/parameters/max_output_color_depth 2>/dev/null)
H=$(cat /sys/module/nvidia_modeset/parameters/hdmi_deepcolor 2>/dev/null)
step "AFTER RELOAD: max_output_color_depth=$V hdmi_deepcolor=$H"

systemctl start sddm
step "sddm started"
systemctl start docker 2>/dev/null && step "docker restarted"

[ "$V" = "12" ] && step "VERDICT-READY: param live at 12 - read the TV OSD now" || step "VERDICT-FAIL: param reads $V - reload did not take"
exit 0
