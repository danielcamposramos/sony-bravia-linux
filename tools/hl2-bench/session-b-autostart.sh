#!/bin/bash
# Runs at desktop login (autostart entry). Only on the test kernel and only
# when armed: runs session B once, then reboots back to the normal kernel
# (GRUB's default). Armed by arm-session-b.sh.
MARK=/K3D/temp/hl2-bench/session-b.armed
LOG=/K3D/temp/hl2-bench/session-b-autostart.log
case "$(uname -r)" in *-mohamed-imp) ;; *) exit 0 ;; esac
[ -f "$MARK" ] || exit 0
rm -f "$MARK"
exec >>"$LOG" 2>&1
echo "=== session B autostart $(date -Is) kernel $(uname -r)"
lsmod | grep -E '^nouveau' || echo "nouveau is NOT loaded"
sleep 60   # let the desktop and Steam settle after login
"$(dirname "$0")/hl2-suite.sh" "$(dirname "$0")/session-b-open.conf" --force --reboot-after
