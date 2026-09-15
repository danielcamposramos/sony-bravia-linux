#!/bin/sh
# One-shot bring-up of the rd1 era-TLS probe on this workstation (192.168.0.4).
# Zero DNS change: the probe URL is https://192.168.0.4/tv1/ typed into the
# TV browser's URL field. Server serves the IP-matched cert, era TLS profile.
set -e
cd "$(dirname "$0")"

sh ./make-cert.sh rd1.sony.net   # for the hostname phase (DNS override, later)
sh ./make-cert.sh 192.168.0.4    # for the first, zero-DNS-change probe

pkill -f "rd1-portal/serve.py" 2>/dev/null || true
# :443 needs root — probe on a high port instead (the browser's URL field
# takes explicit ports). Production :443 goes to d2server's Apache later.
nohup python3 serve.py 8443 ip.crt ip.key >/tmp/acig-/rd1-serve.log 2>&1 &
sleep 2

echo "--- server log:"
cat /tmp/acig-/rd1-serve.log
echo "--- positive control (era TLS 1.0 handshake from this LAN host):"
echo | openssl s_client -connect 192.168.0.4:8443 -tls1 \
       -cipher "AES128-SHA:@SECLEVEL=0" 2>&1 \
  | grep -E "subject=|Protocol|Cipher is|Verify return" | head -5
echo "--- page fetch over the era profile:"
echo | openssl s_client -quiet -connect 192.168.0.4:8443 -tls1 \
       -cipher "AES128-SHA:@SECLEVEL=0" 2>/dev/null \
  <<< "GET /tv1/ HTTP/1.0" | head -6
echo ""
echo "[rd1] probe URL for the TV:  https://192.168.0.4:8443/tv1/"