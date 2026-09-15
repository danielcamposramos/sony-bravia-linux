#!/bin/sh
# Self-signed certs for the rd1.sony.net homepage lane.
#
#   ./make-cert.sh                    -> rd1.crt/rd1.key   (CN=rd1.sony.net)
#   ./make-cert.sh 192.168.0.4        -> ip.crt/ip.key     (CN=192.168.0.4,
#                                        SAN IP — the zero-DNS-change first
#                                        probe: browser -> https://<ip>/tv1/)
#
# Era-compat choices (this cert is for one name on our own LAN, whose DNS
# we override — not a public-trust claim):
#   RSA 2048, SHA-1 signature first (2011-era Presto predates universal
#   SHA-256-in-certs support; SHA-1 was what the real rd1 cert era used),
#   730-day validity, CN + SAN both set.
set -e
cd "$(dirname "$0")"

NAME="${1:-rd1.sony.net}"
case "$NAME" in
  [0-9]*.[0-9]*.[0-9]*.[0-9]*|*:*)  # dotted quad or v6 — an address
    CRT=ip.crt; KEY=ip.key
    SUBJ="/CN=$NAME"
    SAN="IP:$NAME,DNS:$NAME" ;;
  *)
    CRT=rd1.crt; KEY=rd1.key
    SUBJ="/CN=$NAME"
    SAN="DNS:$NAME" ;;
esac

if openssl req -x509 -newkey rsa:2048 -sha1 -days 730 -nodes \
     -keyout "$KEY" -out "$CRT" \
     -subj "$SUBJ" \
     -addext "subjectAltName=$SAN" \
     -addext "basicConstraints=critical,CA:FALSE" \
     -addext "keyUsage=digitalSignature,keyEncipherment" \
     -addext "extendedKeyUsage=serverAuth" 2>/dev/null; then
  echo "[rd1] wrote $CRT/$KEY (SHA-1 signed, $SUBJ)"
else
  echo "[rd1] SHA-1 signing refused by this OpenSSL; falling back to SHA-256"
  openssl req -x509 -newkey rsa:2048 -sha256 -days 730 -nodes \
    -keyout "$KEY" -out "$CRT" \
    -subj "$SUBJ" \
    -addext "subjectAltName=$SAN" \
    -addext "basicConstraints=critical,CA:FALSE" \
    -addext "keyUsage=digitalSignature,keyEncipherment" \
    -addext "extendedKeyUsage=serverAuth"
  echo "[rd1] wrote $CRT/$KEY (SHA-256 signed, $SUBJ)"
fi

openssl x509 -in "$CRT" -noout -subject -dates -ext subjectAltName