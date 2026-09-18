import socket,re,urllib.request,html
from urllib.parse import urljoin
msg=b'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: urn:schemas-upnp-org:device:MediaServer:1\r\n\r\n'
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.settimeout(4); s.sendto(msg,("239.255.255.250",1900)); locs=set()
try:
    while True:
        d,_=s.recvfrom(65535); m=re.search(rb"(?im)^location:\s*(\S+)",d)
        if m: locs.add(m.group(1).decode())
except socket.timeout: pass
kodi=None
for l in sorted(locs):
    try: desc=urllib.request.urlopen(l,timeout=5).read().decode('utf-8','replace')
    except Exception: continue
    fn=re.search(r"<friendlyName>([^<]*)",desc); fn=fn.group(1) if fn else "?"
    print(f"  on LAN: {fn:32} {l}")
    if "Kodi" in fn and "192.168.0.4" in l: kodi=(l,desc)
if not kodi: raise SystemExit("Kodi NOT visible on 192.168.0.4")
loc,desc=kodi; ctl=urljoin(loc,re.search(r"ContentDirectory:1</serviceType>.*?<controlURL>([^<]+)",desc,re.S).group(1))
def browse(oid):
    b=('<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">'
       f'<ObjectID>{html.escape(oid)}</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>0</StartingIndex><RequestedCount>200</RequestedCount><SortCriteria></SortCriteria></u:Browse></s:Body></s:Envelope>')
    r=urllib.request.Request(ctl,data=b.encode(),headers={"Content-Type":'text/xml; charset="utf-8"',"SOAPACTION":'"urn:schemas-upnp-org:service:ContentDirectory:1#Browse"'})
    x=urllib.request.urlopen(r,timeout=20).read().decode('utf-8','replace'); m=re.search(r"<Result>(.*?)</Result>",x,re.S)
    return html.unescape(m.group(1)) if m else ""
CON=re.compile(r'<container\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</container>',re.S); TIT=re.compile(r'<dc:title>([^<]*)</dc:title>')
ITEM=re.compile(r'<item\b[^>]*>(.*?)</item>',re.S); RES=re.compile(r'<res\b([^>]*)>([^<]+)</res>')
seen=set(); out={}
def walk(oid,path,d=0):
    if d>5 or oid in seen: return
    seen.add(oid); x=browse(oid)
    for m in ITEM.finditer(x):
        t=TIT.search(m.group(1)); t=t.group(1) if t else "?"
        if t[:2] in ("A-","B-","C-","D-") and t not in out:
            r=RES.search(m.group(1)); pi=re.search(r'protocolInfo="([^"]+)"',r.group(1)).group(1) if r else "?"
            out[t]=(path,pi)
    for m in CON.finditer(x):
        t=TIT.search(m.group(2)); walk(m.group(1),path+" > "+(t.group(1) if t else "?"),d+1)
walk("0","Kodi")
for t in sorted(out):
    p,pi=out[t]; pn=re.search(r'DLNA.ORG_PN=([A-Z0-9_]+)',pi)
    print(f"  {t:22} {pi.split(':')[2]:18} PN={pn.group(1) if pn else '(none)'}\n      TV path: {p}")
