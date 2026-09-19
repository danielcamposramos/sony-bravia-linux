#!/usr/bin/env python3
"""
mpo_dlna_probe.py — a throwaway DLNA MediaServer that offers the *same* MPO
bytes four different ways, so one pass through the set's photo browser says
which part of the announcement the network photo path actually dispatches on.

Why: a spec-correct MPO engages 3D from USB on both sets, and stays flat over
DLNA. Serviio, Universal Media Server and Gerbera all deliver it identically —
bytes untouched, announced `image/jpeg`, with the URL rewritten to end `.jpg` —
so none of them can separate the candidate causes. This server can:

    1  jpeg-jpg   image/jpeg   + URL ...MPOOK01.jpg   (control: what the three
                                                       real servers send)
    2  jpeg-mpo   image/jpeg   + URL ...MPOOK01.mpo   (does the URL extension
                                                       pick the decoder?)
    3  mpo-mpo    image/mpo    + URL ...MPOOK01.mpo   (is the set lenient about
                                                       a MIME it never declared?)
    4  mpo-pn     image/mpo    + DLNA.ORG_PN=MPO_LRG  (the profile name Vizio
                                                       and JRiver advertise)

Both sets' GetProtocolInfo declare `image/jpeg` only (JPEG_LRG/MED/SM plus a
catch-all `image/jpeg:*`) and no MPO of any kind, so 3 and 4 are expected to be
filtered out of the listing entirely. If they are, that filtering is itself the
measurement: the set hides what it did not declare.

Usage:
    mpo_dlna_probe.py FILE.mpo [--port 8899] [--ip 192.168.0.60]
"""
import argparse, http.server, os, socket, socketserver, struct, sys, threading, time, uuid
from xml.sax.saxutils import escape

SSDP_ADDR, SSDP_PORT = "239.255.255.250", 1900
UDN = "uuid:" + str(uuid.uuid5(uuid.NAMESPACE_DNS, "mpo-dlna-probe.sony-bravia-linux"))

# (id, title, mime, dlna_pn, url extension)
VARIANTS = [
    ("1", "1 jpeg-jpg CONTROL", "image/jpeg", "JPEG_LRG", "jpg"),
    ("2", "2 jpeg-mpo EXT",     "image/jpeg", "JPEG_LRG", "mpo"),
    ("3", "3 mpo-mpo MIME",     "image/mpo",  None,       "mpo"),
    ("4", "4 mpo-pn PROFILE",   "image/mpo",  "MPO_LRG",  "mpo"),
]

DESC = """<?xml version="1.0" encoding="utf-8"?>
<root xmlns="urn:schemas-upnp-org:device-1-0"><specVersion><major>1</major><minor>0</minor></specVersion>
<device><deviceType>urn:schemas-upnp-org:device:MediaServer:1</deviceType>
<friendlyName>MPO-PROBE</friendlyName><manufacturer>sony-bravia-linux</manufacturer>
<modelName>mpo_dlna_probe</modelName><modelNumber>1</modelNumber><UDN>{udn}</UDN>
<dlna:X_DLNADOC xmlns:dlna="urn:schemas-dlna-org:device-1-0">DMS-1.50</dlna:X_DLNADOC>
<serviceList><service>
<serviceType>urn:schemas-upnp-org:service:ContentDirectory:1</serviceType>
<serviceId>urn:upnp-org:serviceId:ContentDirectory</serviceId>
<SCPDURL>/cds.xml</SCPDURL><controlURL>/ctl/cds</controlURL><eventSubURL>/evt/cds</eventSubURL>
</service><service>
<serviceType>urn:schemas-upnp-org:service:ConnectionManager:1</serviceType>
<serviceId>urn:upnp-org:serviceId:ConnectionManager</serviceId>
<SCPDURL>/cms.xml</SCPDURL><controlURL>/ctl/cms</controlURL><eventSubURL>/evt/cms</eventSubURL>
</service></serviceList></device></root>"""

SCPD_CDS = """<?xml version="1.0" encoding="utf-8"?>
<scpd xmlns="urn:schemas-upnp-org:service-1-0"><specVersion><major>1</major><minor>0</minor></specVersion>
<actionList><action><name>Browse</name><argumentList>
<argument><name>ObjectID</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_ObjectID</relatedStateVariable></argument>
<argument><name>BrowseFlag</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_BrowseFlag</relatedStateVariable></argument>
<argument><name>Filter</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_Filter</relatedStateVariable></argument>
<argument><name>StartingIndex</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_Index</relatedStateVariable></argument>
<argument><name>RequestedCount</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable></argument>
<argument><name>SortCriteria</name><direction>in</direction><relatedStateVariable>A_ARG_TYPE_SortCriteria</relatedStateVariable></argument>
<argument><name>Result</name><direction>out</direction><relatedStateVariable>A_ARG_TYPE_Result</relatedStateVariable></argument>
<argument><name>NumberReturned</name><direction>out</direction><relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable></argument>
<argument><name>TotalMatches</name><direction>out</direction><relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable></argument>
<argument><name>UpdateID</name><direction>out</direction><relatedStateVariable>A_ARG_TYPE_UpdateID</relatedStateVariable></argument>
</argumentList></action></actionList>
<serviceStateTable>
<stateVariable sendEvents="no"><name>A_ARG_TYPE_ObjectID</name><dataType>string</dataType></stateVariable>
<stateVariable sendEvents="no"><name>A_ARG_TYPE_Result</name><dataType>string</dataType></stateVariable>
<stateVariable sendEvents="no"><name>A_ARG_TYPE_BrowseFlag</name><dataType>string</dataType></stateVariable>
<stateVariable sendEvents="no"><name>A_ARG_TYPE_Filter</name><dataType>string</dataType></stateVariable>
<stateVariable sendEvents="no"><name>A_ARG_TYPE_SortCriteria</name><dataType>string</dataType></stateVariable>
<stateVariable sendEvents="no"><name>A_ARG_TYPE_Index</name><dataType>ui4</dataType></stateVariable>
<stateVariable sendEvents="no"><name>A_ARG_TYPE_Count</name><dataType>ui4</dataType></stateVariable>
<stateVariable sendEvents="no"><name>A_ARG_TYPE_UpdateID</name><dataType>ui4</dataType></stateVariable>
<stateVariable sendEvents="yes"><name>SystemUpdateID</name><dataType>ui4</dataType></stateVariable>
<stateVariable sendEvents="yes"><name>ContainerUpdateIDs</name><dataType>string</dataType></stateVariable>
</serviceStateTable></scpd>"""

SCPD_CMS = """<?xml version="1.0" encoding="utf-8"?>
<scpd xmlns="urn:schemas-upnp-org:service-1-0"><specVersion><major>1</major><minor>0</minor></specVersion>
<actionList><action><name>GetProtocolInfo</name><argumentList>
<argument><name>Source</name><direction>out</direction><relatedStateVariable>SourceProtocolInfo</relatedStateVariable></argument>
<argument><name>Sink</name><direction>out</direction><relatedStateVariable>SinkProtocolInfo</relatedStateVariable></argument>
</argumentList></action></actionList>
<serviceStateTable>
<stateVariable sendEvents="yes"><name>SourceProtocolInfo</name><dataType>string</dataType></stateVariable>
<stateVariable sendEvents="yes"><name>SinkProtocolInfo</name><dataType>string</dataType></stateVariable>
<stateVariable sendEvents="yes"><name>CurrentConnectionIDs</name><dataType>string</dataType></stateVariable>
</serviceStateTable></scpd>"""


def protocol_info(mime, pn):
    pn_part = f"DLNA.ORG_PN={pn};" if pn else ""
    return f"http-get:*:{mime}:{pn_part}DLNA.ORG_OP=01;DLNA.ORG_CI=0;DLNA.ORG_FLAGS=00900000000000000000000000000000"


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *a):
        print(f"[http] {self.address_string()} {fmt % a}", flush=True)

    def _send(self, body, ctype, extra=None):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/desc.xml":
            return self._send(DESC.format(udn=UDN), "text/xml; charset=utf-8")
        if path == "/cds.xml":
            return self._send(SCPD_CDS, "text/xml; charset=utf-8")
        if path == "/cms.xml":
            return self._send(SCPD_CMS, "text/xml; charset=utf-8")
        if path.startswith("/media/"):
            vid = path.split("/")[2]
            for i, title, mime, pn, ext in VARIANTS:
                if i == vid:
                    pn_part = f"DLNA.ORG_PN={pn};" if pn else ""
                    return self._send(self.server.payload, mime,
                                      {"contentFeatures.dlna.org":
                                       f"{pn_part}DLNA.ORG_OP=01;DLNA.ORG_CI=0;"
                                       "DLNA.ORG_FLAGS=00900000000000000000000000000000",
                                       "transferMode.dlna.org": "Interactive"})
        self.send_error(404)

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n).decode(errors="ignore")
        if "GetProtocolInfo" in body:
            src = ",".join(protocol_info(m, p) for _, _, m, p, _ in VARIANTS)
            return self._send(
                '<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"'
                ' s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>'
                '<u:GetProtocolInfoResponse xmlns:u="urn:schemas-upnp-org:service:ConnectionManager:1">'
                f"<Source>{escape(src)}</Source><Sink></Sink>"
                "</u:GetProtocolInfoResponse></s:Body></s:Envelope>",
                "text/xml; charset=utf-8")
        if "Browse" not in body:
            return self.send_error(401)
        oid = body.split("<ObjectID>")[1].split("</ObjectID>")[0] if "<ObjectID>" in body else "0"
        base = f"http://{self.server.ip}:{self.server.port}"
        if oid == "0" and "BrowseDirectChildren" in body:
            didl = ('<container id="1" parentID="0" restricted="1" childCount="%d">'
                    "<dc:title>MPO probe</dc:title>"
                    "<upnp:class>object.container.storageFolder</upnp:class></container>" % len(VARIANTS))
            n_ret = 1
        else:
            items = []
            for i, title, mime, pn, ext in VARIANTS:
                res = (f'<res protocolInfo="{escape(protocol_info(mime, pn))}" '
                       f'size="{len(self.server.payload)}" resolution="{self.server.res}">'
                       f"{base}/media/{i}/{self.server.name}.{ext}</res>")
                items.append(f'<item id="i{i}" parentID="1" restricted="1">'
                             f"<dc:title>{escape(title)}</dc:title>"
                             "<upnp:class>object.item.imageItem.photo</upnp:class>"
                             f"{res}</item>")
            didl, n_ret = "".join(items), len(VARIANTS)
        result = ('<DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/" '
                  'xmlns:dc="http://purl.org/dc/elements/1.1/" '
                  'xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" '
                  'xmlns:dlna="urn:schemas-dlna-org:metadata-1-0/">' + didl + "</DIDL-Lite>")
        self._send('<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"'
                   ' s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>'
                   '<u:BrowseResponse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">'
                   f"<Result>{escape(result)}</Result><NumberReturned>{n_ret}</NumberReturned>"
                   f"<TotalMatches>{n_ret}</TotalMatches><UpdateID>1</UpdateID>"
                   "</u:BrowseResponse></s:Body></s:Envelope>", "text/xml; charset=utf-8")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def ssdp_loop(ip, port, stop):
    """Answer M-SEARCH and announce on start — enough for the set to find us."""
    loc = f"http://{ip}:{port}/desc.xml"
    targets = ["upnp:rootdevice", "urn:schemas-upnp-org:device:MediaServer:1",
               "urn:schemas-upnp-org:service:ContentDirectory:1", UDN]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", SSDP_PORT))
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                 struct.pack("4s4s", socket.inet_aton(SSDP_ADDR), socket.inet_aton(ip)))
    s.settimeout(2)
    out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    out.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)
    for nt in targets:
        usn = UDN if nt == UDN else f"{UDN}::{nt}"
        out.sendto((f"NOTIFY * HTTP/1.1\r\nHOST:{SSDP_ADDR}:{SSDP_PORT}\r\nCACHE-CONTROL:max-age=1800\r\n"
                    f"LOCATION:{loc}\r\nNT:{nt}\r\nNTS:ssdp:alive\r\nUSN:{usn}\r\n"
                    "SERVER:Linux/2.6 UPnP/1.0 mpo_dlna_probe/1\r\n\r\n").encode(),
                   (SSDP_ADDR, SSDP_PORT))
    while not stop.is_set():
        try:
            data, addr = s.recvfrom(2048)
        except socket.timeout:
            continue
        msg = data.decode(errors="ignore")
        if not msg.startswith("M-SEARCH"):
            continue
        st = ""
        for line in msg.split("\r\n"):
            if line.upper().startswith("ST:"):
                st = line.split(":", 1)[1].strip()
        if st in ("ssdp:all", *targets):
            for nt in (targets if st == "ssdp:all" else [st]):
                usn = UDN if nt == UDN else f"{UDN}::{nt}"
                out.sendto((f"HTTP/1.1 200 OK\r\nCACHE-CONTROL:max-age=1800\r\nEXT:\r\n"
                            f"LOCATION:{loc}\r\nST:{nt}\r\nUSN:{usn}\r\n"
                            "SERVER:Linux/2.6 UPnP/1.0 mpo_dlna_probe/1\r\n\r\n").encode(), addr)
            print(f"[ssdp] answered {addr[0]} ST={st}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--ip", required=True, help="LAN address the set will reach us on")
    ap.add_argument("--port", type=int, default=8899)
    a = ap.parse_args()
    payload = open(a.file, "rb").read()
    srv = Server(("", a.port), Handler)
    srv.payload, srv.ip, srv.port = payload, a.ip, a.port
    srv.name = os.path.splitext(os.path.basename(a.file))[0]
    srv.res = "1920x1080"
    try:
        from PIL import Image
        srv.res = "%dx%d" % Image.open(a.file).size
    except Exception:
        pass
    stop = threading.Event()
    threading.Thread(target=ssdp_loop, args=(a.ip, a.port, stop), daemon=True).start()
    print(f"MPO-PROBE on http://{a.ip}:{a.port}/desc.xml — {len(payload)} bytes, {srv.res}", flush=True)
    for i, title, mime, pn, ext in VARIANTS:
        print(f"  {title:24s} {mime:11s} {'PN='+pn if pn else '(no PN)':14s} .{ext}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        stop.set()


if __name__ == "__main__":
    main()
