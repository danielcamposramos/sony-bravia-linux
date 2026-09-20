#!/bin/sh
# nouveau stereo VERIFICATION harness (front 2). Source says nouveau already
# wires stereo: stereo_allowed=true (nouveau_connector.c) + VSIF on commit
# (dispnv50/disp.c). This script only gathers the hardware proof on the
# RTX 3060 -> second HDMI input of the KDL-46HX855. Expected pass signal:
# the TV switches to 3D by itself on the SBS-half modeset.
#
#   sudo systemd-run --unit=nouveau-3d-test --collect \
#        sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-nouveau-test.sh
#   (ONE line -- a line-broken paste runs 'sh' with no script, then runs this
#    file unprivileged, which the root check below rejects loudly.)
#
# docker: any container touching the GPU pins nvidia_uvm and blocks the swap.
# Per Daniel's directive the harness shuts the WHOLE docker stack down for the
# window ("as if we shutted down") and restores it on every exit path. If
# nvidia_uvm refs turn out LEAKED (refcount > 0 with no live holders -- only
# a reboot clears those), it additionally masks the docker units for exactly
# one boot and asks you to reboot and rerun; that post-reboot run unmasks,
# restarts docker and restarts every recorded container automatically.
#
# autoload guard: nvidia.ko answers to char-major-195-* AND the 10de PCI
# modalias, so any stray open of /dev/nvidia* (or a uevent) after the stack is
# removed drags the whole proprietary driver back in and wins the race for the
# card (2026-09-20 run: full stack reloaded 0.7s after removal, nouveau probed
# nothing, card1 never appeared). install-rules in /run/modprobe.d no-op every
# nvidia-family modprobe for the window; /run is tmpfs, so even a hard reset
# wipes the guard.
#
# Timeline mirrors the proven AMD run: desktop drops (~2 min), nvidia driver
# stack swapped for nouveau, probe + modeset on card1, stack swapped back,
# desktop and docker restored. Recovery identical: machine stays alive even
# if pictureless; Ctrl+Alt+Del reboots; SysRq is armed.
#
# Daniel: when the screens go dark, switch the TV to the NVIDIA-driven input.

TOOLS=/K3D/GitHub/sony-bravia-linux/tools
LOG=/var/log/nouveau-3d-test.log          # service context denied /home/daniel writes once; keep root-land
HOMELOG=/home/daniel/nouveau-3d-test.log  # mirrored here at every exit
TEST_SECONDS=90
KUSER=daniel
DSTATE=/K3D/temp/nouveau-docker.state     # survives the intentional reboot
DCONS=/K3D/temp/nouveau-docker.containers # containers we stopped, to restart
GUARD=/run/modprobe.d/zz-nouveau-stereo-test.conf  # tmpfs: gone on any reset

# first, before any redirect: a line-broken paste runs this file unprivileged.
if [ "$(id -u)" != 0 ]; then
	echo "run-nouveau-test: must run as root -- one line:" >&2
	echo "sudo systemd-run --unit=nouveau-3d-test --collect sh $0" >&2
	exit 1
fi

exec >>"$LOG" 2>&1

resume_docker() {
	[ -f "$DSTATE" ] || return 0
	case "$(cat "$DSTATE" 2>/dev/null)" in
	masked-awaiting-reboot)
		return 0 ;;  # run A just armed this: stay masked across the reboot
	paused|armed)
		echo "--- restoring docker stack"
		systemctl unmask docker docker.socket containerd 2>&1 || true
		rm -f "$DSTATE"
		systemctl start containerd docker.socket docker 2>&1 || true
		if [ -s "$DCONS" ]; then
			while read c; do docker start "$c" 2>&1; done < "$DCONS"
			rm -f "$DCONS"
		fi ;;
	esac
}

trap 'rm -f "$GUARD"; resume_docker; cp -f "$LOG" "$HOMELOG" 2>/dev/null; chown "$KUSER":"$KUSER" "$HOMELOG" 2>/dev/null; true' 0

pause_docker() {
	if systemctl is-active docker >/dev/null 2>&1; then
		docker ps -q > "$DCONS" 2>/dev/null
		if [ -s "$DCONS" ]; then
			echo "--- pausing $(wc -l < "$DCONS") docker containers for the test window:"
			docker ps --format '    {{.Names}} ({{.ID}})'
			docker stop $(cat "$DCONS") 2>&1
		else
			echo "--- docker up but no running containers"
		fi
		systemctl stop docker docker.socket containerd 2>&1 || true
		echo paused > "$DSTATE"
		echo "--- docker stack down"
	else
		echo "--- docker not active, nothing to pause"
	fi
}

echo "=== nouveau-3d-test $(date -Is) ==="

echo 1 > /proc/sys/kernel/sysrq 2>/dev/null || true

NOUVEAU_KO="$(modinfo -n nouveau 2>/dev/null)"
test -n "$NOUVEAU_KO" || { echo "nouveau not found for $(uname -r)"; exit 1; }
echo "nouveau module: $NOUVEAU_KO"

# --- docker down for the whole window, THEN the UVM gate, both BEFORE the
# desktop is touched. Live holders die with their containers (poll 15s);
# leaked refs cannot drop at all and take the one-boot mask + reboot path.
UREF="$(awk '$1=="nvidia_uvm"{print $3}' /proc/modules 2>/dev/null)"
[ -n "$UREF" ] && [ "$UREF" != "0" ] && echo "nvidia_uvm refcount=$UREF before docker pause"
pause_docker
i=0
while [ $i -lt 15 ]; do
	UREF="$(awk '$1=="nvidia_uvm"{print $3}' /proc/modules 2>/dev/null)"
	[ -z "$UREF" ] || [ "$UREF" = "0" ] && break
	sleep 1; i=$((i + 1))
done
if [ -n "$UREF" ] && [ "$UREF" != "0" ]; then
	echo "nvidia_uvm STILL pinned ($UREF) after docker shutdown with no live holders:"
	echo "leaked references -- only a reboot clears them. Masking docker for"
	echo "exactly one boot so no CUDA client can re-leak during the test boot:"
	systemctl mask docker docker.socket containerd 2>&1
	echo "masked-awaiting-reboot" > "$DSTATE"
	echo ""
	echo ">>> desktop untouched. REBOOT NOW, then rerun the same command."
	echo ">>> That run restores docker (units + recorded containers) at the end,"
	echo ">>> pass or fail. To abandon instead: sudo systemctl unmask docker"
	echo ">>> docker.socket containerd; sudo systemctl start containerd docker"
	exit 2
fi
# gate passed: if we are the post-reboot run, consume run A's marker so the
# exit trap restores docker
if [ -f "$DSTATE" ] && [ "$(cat "$DSTATE" 2>/dev/null)" = "masked-awaiting-reboot" ]; then
	echo "post-reboot run, gate passed: docker restore armed for exit"
	echo armed > "$DSTATE"
fi
echo "nvidia_uvm refcount: ${UREF:-not loaded} -- gate passed"

# hold the coming removal window against reloaders, BEFORE the desktop drops.
# Two autoload paths exist and each honors a different rule type, so both are
# needed (run 2 vs run 3 vs post-run churn, all verified live):
#   - modprobe binary (request_module on /dev/nvidia* open, nvidia-modprobe
#     from the udev RUN): honors install rules -> /bin/true no-ops
#   - systemd-udevd kmod builtin (pci modalias uevents): honors ONLY blacklist
# guard removal is what re-enables 'modprobe nvidia*' at restore time.
mkdir -p /run/modprobe.d
printf 'blacklist nvidia\nblacklist nvidia_modeset\nblacklist nvidia_drm\nblacklist nvidia_uvm\nblacklist nvidia_fs\ninstall nvidia /bin/true\ninstall nvidia_modeset /bin/true\ninstall nvidia_drm /bin/true\ninstall nvidia_uvm /bin/true\ninstall nvidia_fs /bin/true\n' > "$GUARD"
echo "autoload guard installed: $GUARD"

systemctl stop sddm
loginctl terminate-user "$KUSER" 2>/dev/null || true

# NVML daemons survive the desktop drop and pin the nvidia modules
for svc in nvidia-persistenced coolercontrold netdata; do
	systemctl stop "$svc" 2>/dev/null && echo "stopped $svc" || true
done

i=0
while [ $i -lt 20 ]; do
	fuser /dev/dri/card0 /dev/dri/card1 /dev/nvidia* >/dev/null 2>&1 || break
	sleep 1; i=$((i + 1))
done
echo "cards free after ${i}s"

echo 0 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null && echo "vtcon1 unbound" || echo "vtcon1 unbind FAILED"
echo 0 > /sys/class/vtconsole/vtcon0/bind 2>/dev/null && echo "vtcon0 unbound" || echo "vtcon0 unbind FAILED"

try=0
for m in nouveau nvidia_fs nvidia_drm nvidia_uvm nvidia_modeset nvidia; do
	grep -q "^$m " /proc/modules || { echo "$m: not loaded, skip"; continue; }
	while true; do
		if modprobe -r "$m" 2>&1; then
			echo "removed $m"
			break
		fi
		try=$((try + 1))
		if [ $try -gt 4 ]; then
			echo "FAILED to remove $m after retries:"; lsmod | grep -E "^(nvidia|nouveau)"
			echo "--- stray holders:"; fuser -v /dev/nvidia* /dev/dri/card* 2>&1 | head -15
			echo "restoring desktop"
			rm -f "$GUARD"
			modprobe nvidia_drm 2>/dev/null || true   # some family members already came out
			echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
			for svc in netdata coolercontrold nvidia-persistenced; do systemctl start "$svc" 2>/dev/null || true; done
			systemctl start sddm
			exit 1
		fi
		echo "remove $m busy (attempt $try), retrying"; lsmod | grep -E "^(nvidia_|nouveau)"
		fuser -v /dev/dri/card1 2>&1 | head -6
		sleep 2
	done
done

echo "--- nvidia-family modules present (guard should keep this empty):"
lsmod | grep -E "^nvidia" || echo "none -- guard holding"

echo "--- loading nouveau (GSP init on GA106 can take ~10s) ---"
if ! modprobe nouveau 2>&1; then
	echo "modprobe nouveau FAILED -- restoring nvidia stack and desktop"
	rm -f "$GUARD"
	modprobe nvidia_drm 2>&1 || true
	sleep 2
	echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
	for svc in netdata coolercontrold nvidia-persistenced; do systemctl start "$svc" 2>/dev/null || true; done
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

CONN=""
for c in $(ls /sys/class/drm/ 2>/dev/null | grep "^card1-HDMI" | sed 's/card1-//'); do
	echo "--- probing card1 $c:"
	"$TOOLS/stereo-kms-probe/stereo-probe" /dev/dri/card1 "$c" 2>&1 || continue
	if "$TOOLS/stereo-kms-probe/stereo-probe" /dev/dri/card1 "$c" 2>/dev/null | grep -q "side-by-side half"; then
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
# nouveau must leave while the guard still blocks autoloaders; fbcon or a slow
# connector client may pin it briefly, so retry with holder dumps, and if it
# still will not go, keep the desktop on it -- a plain reboot restores the
# stock stack (nouveau is blacklisted at boot)
try=0
while grep -q "^nouveau " /proc/modules; do
	modprobe -r nouveau 2>&1 && break
	try=$((try + 1))
	if [ $try -gt 3 ]; then
		echo "nouveau stays pinned after retries; starting the desktop on it as-is."
		echo "--- holders now:"; fuser -v /dev/dri/card1 2>&1 | head -12
		lsmod | grep -E "^(nouveau|nvidia)"
		break
	fi
	sleep 1
done
rm -f "$GUARD"                        # from here 'modprobe nvidia*' works again
modprobe nvidia_drm 2>&1 || true
sleep 2
echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
for svc in netdata coolercontrold nvidia-persistenced; do
	systemctl start "$svc" 2>/dev/null && echo "restarted $svc" || true
done

systemctl start sddm
echo "=== done $(date -Is) ==="
exit 0
