#!/bin/sh
# stereo-modeset test harness — detached form. From the desktop terminal:
#
#   sudo systemd-run --unit=stereo-3d-test --collect \
#        sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-3d-test.sh [sbs|tab|fp|all]
#
# Kernel-under-test form (booted kernel's own amdgpu carries the patches,
# e.g. the Betschart v3 series built into a 7.3-rc4 kernel): no module swap,
# everything else identical:
#
#   sudo systemd-run --unit=stereo-3d-test --collect --setenv=K3D_STOCK_MODULE=1 \
#        sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-3d-test.sh [sbs|tab|fp|all]
#
# The service survives the desktop going down. Timeline:
#   +0s   sddm stops and the user session is terminated (screens dark)
#   +2s   nvidia_drm removed, fbcon unbound, running amdgpu swapped for the
#         K3D-patched build (the FP selector uses the experimental expanded-
#         timing module); CUDA modules and containers remain live
#   +4s   probe runs on HDMI-A-1 (stereo modes now listed — into the log)
#   +6s   stereo-modeset picks the requested 1080p stereo mode on HDMI-A-1
#         PASS SIGNAL: the Sony switches into 3D by itself; SBS/TaB should
#         show three colored boxes at different depths, drifting slowly
#   +96s  sddm restarts; autologin returns the desktop. Patched driver
#         stays loaded until the next reboot.
#
# Log: /home/daniel/stereo-3d-test.log
# Recovery if anything wedges: the machine is ALIVE even when pictureless
# (no GPU driver = no console) -- Ctrl+Alt+Del still reboots, the full
# restore path below is automatic, and SysRq keys are armed for the run.

K3DPATCH_SBS=/K3D/temp/k317/amdgpu-stereo-sbs.ko
K3DPATCH_FP=/K3D/temp/k317/amdgpu-fp-experimental.ko
TOOLS=/K3D/GitHub/sony-bravia-linux/tools
LOG=/home/daniel/stereo-3d-test.log
TEST_SECONDS=90
KUSER=daniel
MODE="${1:-sbs}"
NVIDIA_GUARD=/run/modprobe.d/zz-amd-stereo-isolate-nvidia-drm.conf
NVIDIA_DRM_REMOVED=0

case "$MODE" in
	sbs|tab|fp|all) ;;
	*) echo "usage: $0 [sbs|tab|fp|all]" >&2; exit 2 ;;
esac

# all = one desktop-down window, three layouts, TaB first (Betschart asked
# for TaB coverage of v3 2/3 specifically), 90s each with a short gap so the
# TV re-syncs between layouts. Needs the FP-capable module in swap mode.
if [ "$MODE" = fp ] || [ "$MODE" = all ]; then
	K3DPATCH=$K3DPATCH_FP
else
	K3DPATCH=$K3DPATCH_SBS
fi

if [ "$K3D_STOCK_MODULE" = 1 ]; then
	# kernel-under-test boot: the running kernel's own amdgpu already
	# carries the patches under review; skip the swap entirely
	K3DPATCH="stock amdgpu of $(uname -r) (patches built in)"
fi

exec >>"$LOG" 2>&1
echo "=== stereo-3d-test $(date -Is) layout=$MODE ==="
echo "module under test: $K3DPATCH"

restore_nvidia_display() {
	rm -f "$NVIDIA_GUARD"
	if [ "$NVIDIA_DRM_REMOVED" = 1 ]; then
		if modprobe nvidia_drm; then
			echo "restored nvidia_drm"
			NVIDIA_DRM_REMOVED=0
		else
			echo "WARNING: nvidia_drm restore failed; reboot restores the stock display stack"
		fi
	fi
}
trap restore_nvidia_display EXIT

# arm SysRq for the whole run: if we ever leave the console dead,
# Alt+SysRq+... still reaches the kernel
echo 1 > /proc/sys/kernel/sysrq 2>/dev/null || true

test "$(id -u)" = 0 || { echo "run as root"; exit 1; }
if [ "$K3D_STOCK_MODULE" != 1 ]; then
	test -f "$K3DPATCH" || { echo "patched module missing: $K3DPATCH"; exit 1; }
	WANT="$(uname -r) SMP preempt mod_unload"
	HAVE="$(modinfo -F vermagic "$K3DPATCH" | sed 's/[[:space:]]*$//')"
	test "$HAVE" = "$WANT" || { echo "vermagic mismatch: have '$HAVE' want '$WANT'"; exit 1; }
fi

systemctl stop sddm
loginctl terminate-user "$KUSER" 2>/dev/null || true

# terminate-user is async: kwin keeps BOTH cards' fds open while it dies.
# Drain card0 AND card1 before touching nvidia_drm. Run 9 raced this --
# 4x1s of modprobe retries lost to kwin shutdown and the run aborted
# untested, back at the desktop in seconds.
i=0
while [ $i -lt 25 ]; do
	fuser /dev/dri/card0 /dev/dri/card1 >/dev/null 2>&1 || break
	sleep 1; i=$((i + 1))
done
echo "DRM card fds free after ${i}s"

# Make the AMD HDMI result unambiguous. The previous FP run left the NVIDIA
# connector scanning its old desktop buffer, and its sink also entered 3D.
# Guard against autoload, remove only the DRM display leaf (CUDA remains up),
# and restore it before SDDM starts again.
if grep -q '^nvidia_drm ' /proc/modules; then
	mkdir -p /run/modprobe.d
	printf 'blacklist nvidia_drm\ninstall nvidia_drm /bin/true\n' > "$NVIDIA_GUARD"
	i=0
	while [ $i -lt 4 ] && grep -q '^nvidia_drm ' /proc/modules; do
		modprobe -r nvidia_drm 2>&1 || true
		grep -q '^nvidia_drm ' /proc/modules || break
		echo "nvidia_drm still held (attempt $((i + 1))/4):"
		fuser -v /dev/dri/card* 2>&1 || true
		sleep 1
		i=$((i + 1))
	done
	if grep -q '^nvidia_drm ' /proc/modules; then
		echo "nvidia_drm isolation FAILED -- restoring desktop without testing"
		rm -f "$NVIDIA_GUARD"
		systemctl start sddm
		exit 1
	fi
	NVIDIA_DRM_REMOVED=1
	echo "nvidia_drm removed; NVIDIA HDMI is dark, CUDA stack remains loaded"
fi

# (fd drain now runs right after terminate-user above, before nvidia_drm isolation)

if [ "$K3D_STOCK_MODULE" = 1 ]; then
	echo "kernel-under-test mode: running built-in amdgpu ($(uname -r)), no swap"
else
# fbcon holds the module too: unbind it while the swap happens
echo 0 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
if ! modprobe -r amdgpu; then
	echo "amdgpu unload FAILED -- restoring desktop"
	echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
	restore_nvidia_display
	systemctl start sddm
	exit 1
fi
echo "--- /proc/modules after modprobe -r amdgpu:"
cat /proc/modules
# insmod resolves no dependencies, and "modprobe -r" took the whole unused
# dep chain down with it (run 4 died on that). Preload the chain from the
# stock module metadata, but verify EACH module individually against
# /proc/modules -- run 6 proved a silent aggregate "success" cannot be
# trusted (symbols were still absent at insmod time despite no error).
DEPS="$(modinfo -F depends amdgpu 2>/dev/null | tr ',' ' ')"
echo "deps needed: $DEPS"
for m in $DEPS; do
	kn="$(echo "$m" | tr '-' '_')"
	if grep -q "^$kn " /proc/modules; then
		echo "dep $m: already loaded"
	else
		modprobe "$m" 2>&1
		if grep -q "^$kn " /proc/modules; then
			echo "dep $m: loaded ok"
		else
			echo "dep $m: FAILED TO LOAD"
		fi
	fi
done
echo "--- /proc/modules before insmod:"
cat /proc/modules

if ! insmod "$K3DPATCH"; then
	echo "insmod of patched module FAILED -- kernel said:"
	dmesg | grep -i "unknown symbol" | tail -25
	echo "restoring stock amdgpu and desktop"
	modprobe amdgpu 2>&1 || true
	echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
	restore_nvidia_display
	systemctl start sddm
	exit 1
fi
echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
sleep 2
fi

echo "--- probe with patched driver (stereo modes should appear) ---"
"$TOOLS/stereo-kms-probe/stereo-probe" /dev/dri/card0 HDMI-A-1 || true

LAYOUTS="$MODE"
[ "$MODE" = all ] && LAYOUTS="tab sbs fp"
FIRST=1
for L in $LAYOUTS; do
	if [ $FIRST = 0 ]; then
		sleep 5
		echo "--- switching to $L (TV may blink back to 2D) ---"
	fi
	FIRST=0
	echo "--- firing the $L stereo modeset for ${TEST_SECONDS}s -- watch the TV ---"
	timeout "$TEST_SECONDS" "$TOOLS/stereo-modeset/stereo-modeset" /dev/dri/card0 HDMI-A-1 "$L" isolate </dev/null || true
done

# if the patched driver took the device down with it, swapping back to stock
# BEFORE sddm restarts is the difference between "desktop returns" and
# "alive but pictureless" (run 4's black screen)
if [ ! -e /dev/dri/card0 ]; then
	echo "no DRM device after test -- falling back to stock amdgpu"
	modprobe -r amdgpu 2>/dev/null || true
	modprobe amdgpu 2>&1 || true
	sleep 2
fi

restore_nvidia_display
systemctl start sddm
echo "=== done $(date -Is); patched amdgpu remains loaded until reboot ==="
exit 0
