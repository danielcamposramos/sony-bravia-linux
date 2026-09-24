#!/bin/bash
# Arms session B: installs the nouveau loader service and the autostart
# entry, sets the one-shot marker, and points the next boot (one time) at
# the test kernel. GRUB's default stays on the normal kernel, so the reboot
# at the end of the session returns there. Needs sudo; run it, then reboot.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
TEST="Advanced options for SparkyLinux GNU/Linux>SparkyLinux GNU/Linux, with Linux 7.3.0-rc1-mohamed-imp"
grep -q "7.3.0-rc1-mohamed-imp" /boot/grub/grub.cfg || { echo "test kernel not in GRUB" >&2; exit 1; }
grep -q '^GRUB_DEFAULT="Advanced options.*7\.0\.10' /etc/default/grub || { echo "GRUB_DEFAULT is not pinned to 7.0.10; refusing" >&2; exit 1; }
# The TV bench service (runs 30-34) targets the same test kernel; it would
# stop the desktop and reboot mid-session, so it must be off for session B.
if systemctl is-enabled --quiet mohamed-bench.service 2>/dev/null; then
	sudo systemctl disable mohamed-bench.service
	echo "disabled mohamed-bench.service (re-enable it for TV bench runs)"
fi
sudo install -m 644 "$HERE/hl2-bench-nouveau.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hl2-bench-nouveau.service
mkdir -p ~/.config/autostart /K3D/temp/hl2-bench
install -m 644 "$HERE/hl2-bench-session-b.desktop" ~/.config/autostart/
touch /K3D/temp/hl2-bench/session-b.armed
sudo grub-reboot "$TEST"
sudo grub-editenv list
echo "armed: reboot when ready; session B runs by itself and reboots back"
