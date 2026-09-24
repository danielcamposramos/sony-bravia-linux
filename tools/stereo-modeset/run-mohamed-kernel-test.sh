#!/bin/sh
# Bench run of Mohamed Ahmed's nouveau branch (mohamexiety/nouveau,
# nouveau-imp-upstr-v120, Linux 7.3-rc1) with and without our two-line
# GCP CD=5 fix, on the RTX 3060 (GA106) -> KDL-46HX855 (input 3) or
# KDL-46EX725 (10 m cable).
#
# Runs ONLY while booted into the test kernel (uname -r ends in -mohamed-imp).
# Automatic: mohamed-bench.service (next to this script) starts it with
# --reboot-after about 45 s after the desktop is up, and it reboots back to the
# normal kernel when done. By hand:
#   sudo systemd-run --unit=mohamed-bench --collect sh /K3D/GitHub/sony-bravia-linux/tools/stereo-modeset/run-mohamed-kernel-test.sh
#
# The installed kernel's nouveau.ko carries the fix. nouveau is blacklisted at
# boot, so the desktop comes up on the AMD card and the NVIDIA card is free
# until this script loads nouveau. Steps (STEP_SECONDS each, the frame names
# itself): 12 bpc, 3D at 12 bpc (frame packing, side-by-side, top-and-bottom),
# 10 bpc, 8 bpc with the fix; then the module WITHOUT the fix and 10 bpc again.
# --ycbcr (2026-09-24): the ycbcr-poc branch (our withdrawn colour-format
# series ported onto this branch); the run27+run28 output-format matrix,
# no module swap.
# Daniel: when the screens go dark, switch the TV to the NVIDIA input and read
# the OSD (bit depth, 3D state, or "incompatible signal") for every step.

TOOLS=/K3D/GitHub/sony-bravia-linux/tools
B=${BENCH_DIR:-/K3D/temp/mohamed-bench}
NOFIX=$B/nouveau-without-cd5.ko
STEP_SECONDS=30
LOG=/var/log/mohamed-bench.log
HOMELOG=/home/daniel/mohamed-bench.log
# Known sinks on the NVIDIA port: KDL-46HX855 (input 3) and KDL-46EX725 (10 m cable).
EXPECTED_EDIDS="4f6cc1c8b7ce1700f93ef13c76c490ea985752edadd05c64179ae169e69d5dc9 836180905c56c2bc93dead00ef2f07452a6e301a53b50b25dde44735956b0b95"

if [ "$(id -u)" != 0 ]; then
	echo "must run as root: sudo systemd-run --unit=mohamed-bench --collect sh $0" >&2
	exit 1
fi
case "$(uname -r)" in
	*-mohamed-imp) ;;
	*) echo "not booted into the -mohamed-imp test kernel ($(uname -r)); refusing" >&2; exit 1 ;;
esac

exec >"$LOG" 2>&1
REBOOT_AFTER=0
AB10=0
YCBCR=0
for a in "$@"; do
	case "$a" in
		--reboot-after) REBOOT_AFTER=1 ;;
		--ab10) AB10=1; STEP_SECONDS=45 ;; # only 10 bpc with, then without, the fix
		--ycbcr) YCBCR=1 ;;
	esac
done
finish() {
	modprobe -r nouveau 2>&1 || true
	echo 1 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true
	echo "=== done $(date -Is) ==="
	cp "$LOG" "$HOMELOG" 2>/dev/null; chown daniel: "$HOMELOG" 2>/dev/null
	sync
	if [ "$REBOOT_AFTER" = 1 ]; then
		# GRUB's default is the normal kernel; this returns there.
		systemctl reboot
	else
		systemctl start sddm
	fi
}
trap finish EXIT

echo "=== mohamed-bench $(date -Is) kernel=$(uname -r) ==="
# The r8168 DKMS alias routes the NIC to a driver absent from this kernel.
modprobe r8169 2>/dev/null && echo "network: r8169 loaded" || true
echo "installed nouveau (with CD=5): $(modinfo -n nouveau) sha256 $(sha256sum "$(modinfo -n nouveau)" | cut -c1-64)"
if [ -f "$NOFIX" ]; then
	echo "A/B nouveau (without CD=5):    $NOFIX sha256 $(sha256sum "$NOFIX" | cut -c1-64)"
	echo "vermagic A/B module: $(modinfo -F vermagic "$NOFIX")"
fi

systemctl stop sddm
sleep 3
echo 0 > /sys/class/vtconsole/vtcon1/bind 2>/dev/null || true

find_card() {
	CARD=""; CONN=""
	for d in /sys/class/drm/card[0-9]; do
		[ "$(basename "$(readlink "$d/device/driver")")" = nouveau ] && CARD=$(basename "$d")
	done
	[ -n "$CARD" ] || return 1
	for c in $(ls /sys/class/drm/ | grep "^$CARD-HDMI" | sed "s/$CARD-//"); do
		E=/sys/class/drm/$CARD-$c/edid
		[ -r "$E" ] || continue
		H=$(sha256sum "$E" | cut -c1-64)
		case " $EXPECTED_EDIDS " in *" $H "*) CONN=$c; EDIDSHA=$H; return 0 ;; esac
	done
	return 1
}

run_steps() { # label, steps separated by |
	label=$1; shift
	i=0; until find_card || [ $i -ge 30 ]; do sleep 1; i=$((i + 1)); done
	echo "--- [$label] card=$CARD connector=${CONN:-none} after ${i}s"
	[ -n "$CONN" ] || { echo "Sony EDID not found on nouveau; skipping [$label]"; return; }
	echo "sink EDID sha256 $EDIDSHA:"
	edid-decode "/sys/class/drm/$CARD-$CONN/edid" 2>/dev/null | grep -E 'Model:|Made in|Maximum TMDS|DC_|RGB quantization' | sed 's/^ */    /' 
	modetest -M nouveau -c 2>&1 | grep -A3 -E 'max bpc' | head -8
	OLDIFS=$IFS; IFS='|'; set -- $1; IFS=$OLDIFS
	for step in "$@"; do
		echo "--- [$label] step: $step (${STEP_SECONDS}s) $(date +%T)"
		T0=$(date +%s)
		# shellcheck disable=SC2086 # $step is a deliberate word list
		timeout "$STEP_SECONDS" stdbuf -oL "$TOOLS/stereo-modeset/stereo-modeset" "/dev/dri/$CARD" "$CONN" $step isolate </dev/null || true
		# From the journal, by time: a dmesg line count breaks once a
		# warning flood rotates the ring buffer (run33).
		K=$(journalctl -k -b --since "@$T0" --no-pager -q 2>/dev/null)
		echo "    kernel warnings this step: $(printf '%s\n' "$K" | grep -c 'WARNING: CPU')"
		printf '%s\n' "$K" | grep -E 'WARNING: CPU|RIP: |nouveau.*(error|fail)' | sort -u | head -4 | sed 's/^/    kernel: /'
	done
}

modprobe nouveau
if [ "$YCBCR" = 1 ]; then
	echo "branch: ycbcr-poc (Broadcast RGB + color format)"
	run_steps "ycbcr-poc RGB" 'deep12 fmt=rgbfull|deep12 fmt=rgblimited|deep12 fmt=rgbauto|deep10 fmt=rgbfull|deep10 fmt=rgblimited|deep8 fmt=rgbfull|deep8 fmt=rgblimited'
	run_steps "ycbcr-poc YUV" 'deep12 fmt=yuv444|deep10 fmt=yuv444|deep8 fmt=yuv444|deep12 fmt=yuv422|deep10 fmt=yuv422|deep8 fmt=yuv422'
	run_steps "ycbcr-poc 3D+SD" 'sbs bpc12 fmt=yuv444|tab bpc12 fmt=rgblimited|fp bpc12 fmt=yuv422|fp bpc12 fmt=yuv444|deep12 720p fmt=yuv444|deep12 576p fmt=yuv444|deep12 480p fmt=yuv422|deep12 576p fmt=rgbauto|deep12 vga fmt=rgbfull'
	exit 0
fi
if [ "$AB10" = 1 ]; then
	run_steps "with CD=5" 'deep10 tag=CD-ON'
else
	run_steps "with CD=5" 'deep12|fp bpc12|sbs bpc12|tab bpc12|deep10|deep8'
fi

echo "--- swapping to the module without the fix"
# rmmod, not modprobe -r: the latter also unloads nouveau's helper modules,
# and insmod does not reload them (run30: "Unknown symbol in module").
rmmod nouveau 2>&1 || { sleep 2; rmmod nouveau 2>&1; }
insmod "$NOFIX"
if [ "$AB10" = 1 ]; then
	run_steps "without CD=5" 'deep10 tag=CD-OFF'
else
	run_steps "without CD=5" 'deep10|deep12'
fi
