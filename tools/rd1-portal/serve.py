#!/usr/bin/env python3
"""rd1.sony.net browser-homepage lane — era-TLS HTTPS server.

The EX725's built-in browser opens on the hardcoded homepage
https://rd1.sony.net:443/tv1/ (docs/research/liverecon/browser-lane-test.md).
This server, plus a Unbound host override rd1.sony.net -> this host, makes
the default browser page OUR portal — same pattern as the applicast widget
lane (docs/research/appliwidget-programming.md §6).

Two era facts drive the TLS profile:
- The browser's TLS is 2010-grade (Presto 2.7.61): live-verified by the
  "outdated keys" refusal on https://www.sony.com.br (modern servers no
  longer offer its cipher suites). We terminate TLS ourselves, so we keep
  TLS 1.0 + AES128-SHA-class suites alive for it.
- Whether the era client accepts a self-signed cert is THE open question
  (certs.opera.com root-list injection is signature-gated — see the
  certificate-lane section of applicast-widgetlane.md). This server is the
  probe: serve, log the handshake, let the owner read what the browser does.

Run:  python3 serve.py [port] [cert] [key]   # default 443 rd1.crt/rd1.key
      — also mirrors plain HTTP on :80 when port is 443
Cert: ./make-cert.sh [rd1.sony.net|192.168.0.4] first.

Logs every request with UA (the UA string itself confirms the lane before
the page even renders) and logs TLS handshake failures with the reason.
"""
import http.server
import os
import socket
import ssl
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
WWWROOT = os.path.join(HERE, "wwwroot")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 443
CRT = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(HERE, "rd1.crt")
KEY = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else os.path.join(HERE, "rd1.key")

# Era cipher profile for Presto 2.7.61 (2010-era OpenSSL/Opera crypto):
# TLS_RSA_WITH_AES_128_CBC_SHA and siblings. SECLEVEL=0 is required on
# OpenSSL 3 to permit the TLS 1.0 handshake at all.
ERA_CIPHERS = "AES128-SHA:AES256-SHA:DES-CBC3-SHA:@SECLEVEL=0"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=WWWROOT, **kw)

    def log_message(self, fmt, *args):
        ua = self.headers.get("User-Agent", "-") if self.headers else "-"
        sys.stdout.write("[rd1] %s :: %s :: UA %s\n"
                         % (self.address_string(), fmt % args, ua))
        sys.stdout.flush()

    def end_headers(self):
        # era caches: keep revalidation cheap and observable
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


def start_tls():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    try:
        ctx.minimum_version = ssl.TLSVersion.TLSv1
    except Exception:
        pass  # older python: TLS1.0 is already the floor
    ctx.set_ciphers(ERA_CIPHERS)
    ctx.load_cert_chain(CRT, KEY)
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    # wrap_socket eats the handshake exception silently otherwise
    print("[rd1] HTTPS (TLS1.0-era profile) on :%d, root %s" % (PORT, WWWROOT))
    httpd.serve_forever()


def start_plain():
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", 80), Handler)
    print("[rd1] plain-HTTP probe mirror on :80 (http://rd1.sony.net/tv1/)")
    httpd.serve_forever()


if __name__ == "__main__":
    if not (os.path.exists(CRT) and os.path.exists(KEY)):
        sys.exit("[rd1] no cert: run ./make-cert.sh first")
    os.chdir(WWWROOT)
    if PORT != 443:
        start_tls()          # non-root custom port: TLS only
    else:
        threading.Thread(target=start_plain, daemon=True).start()
        start_tls()