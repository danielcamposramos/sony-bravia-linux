#!/bin/sh
# run-nvidia-cta-dualrate-probe.sh — A/B probe: stock nvidia-modeset vs the
# CTA-861 dual-rate VIC patch, same boot, one detached run.
#
# Purpose: measure, not predict, the first mode-list bug under
# NVIDIA/open-gpu-kernel-modules#1384. NVKMS's parse861bShortTiming() adds each
# short video descriptor once, at the 1000/1001 rate stored in EIA861B[]
# (59.94, 29.97, 23.976 Hz ...). CTA-861 defines those formats at both rates
# under the same VIC, and the DRM core adds the integer-rate twin
# (add_alternate_cea_modes()). On the KDL-46HX855 this leaves nvidia-drm at 17
# modes where nouveau and amdgpu list 22 distinct timings.
#
# Only nvidia_modeset (patched) and nvidia_drm (stock, reloaded on top) move.
# The nvidia core stays loaded, so CUDA containers are not touched.
#
# Sequence: wait for HPD (IR-switch the TV to the NVIDIA HDMI input, up to
# 120 s) -> probe STOCK -> drop sddm + user session -> autoload guard ->
# rmmod nvidia_drm nvidia_modeset -> insmod patched nvidia-modeset.ko ->
# modprobe stock nvidia_drm -> probe PATCHED -> restore stock pair -> sddm.
# The desktop is down for the middle section; run detached:
#
#   sudo systemd-run --unit=nvidia-cta-dualrate --collect \
#        sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nvidia-cta-dualrate-probe.sh
#
# Recovery if anything fails: restore() reloads the stock pair and restarts
# sddm; worst case Ctrl+Alt+Del, SysRq armed.
TOOLS=/K3D/GitHub/sony-bravia-linux/tools
LOG=/K3D/temp/run29-nvidia-cta-dualrate-probe.log
PROBE=$TOOLS/stereo-kms-probe/stereo-probe
CARD=/dev/dri/card1
CONN=HDMI-A-2
SYSCONN=/sys/class/drm/card1-HDMI-A-2
PATCHED_KO=/K3D/temp/nvidia-open-cta-wt/kernel-open/nvidia-modeset.ko
GUARD=/run/modprobe.d/zz-cta-dualrate-probe-off.conf
KUSER=daniel

exec >>"$LOG" 2>&1

guard_on() {
	mkdir -p /run/modprobe.d
	printf 'install nvidia_modeset /bin/true\ninstall nvidia_drm /bin/true\n' > "$GUARD"
}

restore() {
	echo "== restore: stock nvidia_modeset + nvidia_drm, desktop =="
	guard_on
	rmmod nvidia_drm 2>/dev/null
	rmmod nvidia_modeset 2>/dev/null
	rm -f "$GUARD"
	modprobe nvidia_drm && echo "stock pair restored (modeset srcversion $(cat /sys/module/nvidia_modeset/srcversion 2>/dev/null))"
	systemctl start nvidia-persistenced 2>/dev/null || true
	systemctl start sddm
	echo "=== done $(date -Is) ==="
	sync
}

echo "=== nvidia-cta-dualrate-probe $(date -Is) ==="
echo "kernel $(uname -r); nvidia-modeset $(modinfo -F version nvidia_modeset 2>/dev/null)"
echo "STOCK modeset srcversion: $(cat /sys/module/nvidia_modeset/srcversion 2>/dev/null)"
echo "PATCHED ko: $PATCHED_KO sha256=$(sha256sum "$PATCHED_KO" 2>/dev/null | cut -d' ' -f1)"
echo "PATCHED vermagic: $(modinfo -F vermagic "$PATCHED_KO" 2>/dev/null)"

test "$(id -u)" = 0 || { echo "run as root"; exit 1; }
test -f "$PATCHED_KO" || { echo "patched module missing: $PATCHED_KO (build first)"; exit 1; }
test -x "$PROBE" || { echo "probe missing: $PROBE"; exit 1; }
[ "$(modinfo -F vermagic "$PATCHED_KO")" = "$(modinfo -F vermagic nvidia_modeset)" ] ||
	{ echo "vermagic mismatch - abort before touching anything"; exit 1; }

echo 1 > /proc/sys/kernel/sysrq 2>/dev/null || true

# Phase 1: HPD with the desktop still up; the probe is read-only.
i=0
while [ $i -lt 120 ]; do
	[ "$(cat $SYSCONN/status 2>/dev/null)" = connected ] && break
	sleep 1; i=$((i + 1))
done
[ "$(cat $SYSCONN/status 2>/dev/null)" = connected ] || { echo "no HPD in 120s - abort"; exit 1; }
echo "HPD live after ${i}s ($(cat $SYSCONN/status))"

echo "=== PROBE 1/2: STOCK nvidia-modeset ==="
"$PROBE" "$CARD" "$CONN"

# Phase 2: display down, module swap.
echo "== dropping display stack =="
systemctl stop sddm
loginctl terminate-user "$KUSER" 2>/dev/null || true
# nvidia-persistenced holds /dev/nvidia-modeset; it must go for the swap
# (run 24 did the same). restore() starts it again.
systemctl stop nvidia-persistenced 2>/dev/null && echo "nvidia-persistenced stopped"
i=0
while [ $i -lt 30 ]; do
	fuser /dev/dri/card1 /dev/nvidia-modeset >/dev/null 2>&1 || break
	sleep 1; i=$((i + 1))
done
echo "fds free after ${i}s"
echo "remaining holders of /dev/nvidia-modeset: $(fuser /dev/nvidia-modeset 2>/dev/null || echo none)"

guard_on
if rmmod nvidia_drm && rmmod nvidia_modeset; then
	echo "stock nvidia_drm + nvidia_modeset unloaded"
else
	echo "rmmod failed - cannot swap ($(lsmod | grep -E '^nvidia_(drm|modeset)' | tr '\n' ';'))"
	restore
	exit 1
fi

if insmod "$PATCHED_KO"; then
	echo "patched nvidia-modeset.ko loaded, srcversion $(cat /sys/module/nvidia_modeset/srcversion 2>/dev/null)"
else
	echo "insmod of patched nvidia-modeset failed"
	restore
	exit 1
fi
rm -f "$GUARD"
if modprobe nvidia_drm; then
	echo "stock nvidia_drm loaded on top of the patched nvidia_modeset"
else
	echo "modprobe nvidia_drm failed"
	restore
	exit 1
fi

sleep 3	# let NVKMS re-read the EDID and build its mode pool

echo "=== PROBE 2/2: PATCHED nvidia-modeset (CTA dual-rate VICs) ==="
"$PROBE" "$CARD" "$CONN"

# Phase 3: always restore.
restore
