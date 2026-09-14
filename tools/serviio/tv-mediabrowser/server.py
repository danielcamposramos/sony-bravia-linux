#!/usr/bin/env python3
"""Era-lean Serviio MediaBrowser proxy for 2011-era Sony BRAVIA browsers.

Browses the Serviio library on the LAN media server (192.168.0.60, Serviio
2.5) and plays items on the EX725's built-in browser — modeled on Serviio's
own MediaBrowser web app: same library, same category containers (A/I/V),
same 18-items-per-page structure, re-rendered server-side so a 2011 Presto
browser can use it.

Data source: Serviio's UPnP ContentDirectory (plain HTTP, port 8895, FREE
edition, no license gate). Serviio's own MediaBrowser backend (/cds REST on
port 23424) was reverse-engineered first but refuses login with errorCode
554 "MediaBrowser is only available in the Pro edition" — the UPnP lane
serves the same library with no auth and hands out resource URLs that
stream Range/206 to any plain HTTP client (verified with curl).

Design constraints of the era browser (Presto 11 / InettvBrowser 2.2):
  - no frameworks, no client-side JSON, no cross-origin XHR (no CORS)
    => every page is fully server-rendered here; the browser only does
       plain GETs plus a small arrow-key script
  - era memory ceiling ("page too big to display" on heavy pages)
    => pages stay a few KB
  - playback is NOT same-origin restricted: the <video> source points
    straight at Serviio's resource URLs (Range/206 handled by Serviio),
    exactly like DCH's page-on-one-host / video-on-CDN split
  - the Sony-path player recipe is the one proven live on the EX725
    (docs/research/liverecon/lan-media-mvp.md): <video> hidden, then a
    <source> child with type+src, then show + load() + play()

Non-MP4 formats are handed to the player with their real MIME type and a
format label on screen — the era player's response doubles as a
format-support probe for the transcode-lane design (next phase).

Run:  python3 server.py [port]        (default 8090)
"""

import html
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

SERVIIO = os.environ.get('SERVIIO', '192.168.0.60')
CONTROL_URL = 'http://%s:8895/serviceControl' % SERVIIO
RES_BASE = 'http://%s:8895' % SERVIIO
# Serviio binds res URLs to the browsing client's IP: when the TV fetched
# them directly, Serviio answered 500 "No media description available for
# required version" (verified live). So the app proxies media through
# itself: browse client == fetch client, and the TV streams Range/206
# from this server instead.
OWN_BASE = os.environ.get('OWN_BASE', 'http://192.168.0.4:%d')
PAGE_SIZE = 18
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8090

NS = {'didl': 'urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/',
      'dc': 'http://purl.org/dc/elements/1.1/',
      'upnp': 'urn:schemas-upnp-org:metadata-1-0/upnp/'}

# ---------------------------------------------------------------- upnp

def upnp_browse(object_id, flag='BrowseDirectChildren', start=0, count=PAGE_SIZE):
    """SOAP Browse against Serviio's ContentDirectory; returns
    (objects, total_matches) where objects are dicts:
      containers: {container:True, id, title, child_count}
      items:      {id, title, res: [{url, mime, pn, ci, size, duration}]}
    """
    soap = ('<?xml version="1.0" encoding="utf-8"?>'
            '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
            's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
            '<s:Body><u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">'
            '<ObjectID>%s</ObjectID><BrowseFlag>%s</BrowseFlag><Filter>*</Filter>'
            '<StartingIndex>%d</StartingIndex><RequestedCount>%d</RequestedCount>'
            '<SortCriteria></SortCriteria>'
            '</u:Browse></s:Body></s:Envelope>'
            % (html.escape(object_id), flag, start, count))
    req = urllib.request.Request(
        CONTROL_URL, data=soap.encode(),
        headers={'Content-Type': 'text/xml; charset="utf-8"',
                 'SOAPACTION': '"urn:schemas-upnp-org:service:ContentDirectory:1#Browse"'})
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read().decode()
    m = re.search(r'<Result>(.*?)</Result>', body, re.S)
    total = int(re.search(r'<TotalMatches>(\d+)', body).group(1))
    if not m or not m.group(1):
        return [], total
    didl = html.unescape(m.group(1))
    objects = []
    for el in ET.fromstring(didl):
        tag = el.tag.split('}')[1]
        obj = {'id': el.get('id'),
               'title': el.findtext('dc:title', default='', namespaces=NS) or '',
               'cls': el.findtext('upnp:class', default='', namespaces=NS) or '',
               'container': tag == 'container'}
        if obj['container']:
            obj['child_count'] = int(el.get('childCount') or 0)
        else:
            obj['res'] = []
            for res in el.findall('didl:res', NS):
                pi = res.get('protocolInfo', '')
                # http-get:*:MIME:DLNA.ORG_PN=PN;DLNA.ORG_OP=..;DLNA.ORG_CI=..
                mime = pi.split(':')[2] if pi.count(':') >= 2 else ''
                pn = (re.search(r'DLNA\.ORG_PN=([^;]+)', pi) or [None, ''])[1]
                ci = (re.search(r'DLNA\.ORG_CI=(\d)', pi) or [None, '0'])[1]
                obj['res'].append({'url': res.text or '',
                                   'mime': mime,
                                   'pn': pn,
                                   'ci': ci,
                                   'size': res.get('size'),
                                   'duration': res.get('duration')})
        objects.append(obj)
    return objects, total


def pick_video_res(res_list):
    """Era preference: MP4 first (proven), then TS/PS (era-DLNA native),
    then anything else as a probe."""
    def score(r):
        mime = r['mime']
        if mime == 'video/mp4':
            return 0
        if mime in ('video/mpeg', 'video/mp2t'):
            return 1
        return 2
    vids = [r for r in res_list if r['mime'].startswith('video/')]
    return sorted(vids, key=score)[0] if vids else None


def pick_image_res(res_list):
    imgs = [r for r in res_list if r['mime'].startswith('image/')]
    return imgs[0] if imgs else None


def pick_audio_res(res_list):
    auds = [r for r in res_list if r['mime'].startswith('audio/')]
    return auds[0] if auds else None


# ---------------------------------------------------------------- pages

CSS = """
body{background:#000;color:#fff;font-family:sans-serif;margin:0;}
a{color:#fff;text-decoration:none;}
h2{margin:10px;font-size:30px;font-weight:normal;}
#hdr{color:#ccc;font-size:34px;}
ul{list-style:none;margin:10px;padding:0;}
li{padding:10px 14px;font-size:28px;}
li.sel{background:#fff;color:#000;}
li.sel a{color:#000;}
#foot{color:#888;font-size:22px;margin:10px;}
#status{margin:10px;font-size:28px;}
#fmt{color:#ccc;font-size:22px;margin:0 10px;}
video{background:#000;}
img{max-width:100%;}
/* player pages: full-viewport video like the karajan/DCH app — era Presto
   has no JS fullscreen API, so the video is a fixed 100%x100% element and
   the HUD is a fixed bottom strip; neither is in the document flow, so no
   scrollbar and no embedded letterboxing */
#player_page video{position:fixed;left:0;top:0;width:100%;height:100%;border:0;z-index:1;}
.hud{position:fixed;left:0;bottom:0;width:100%;margin:0;padding:6px 14px;background:#000;color:#fff;font-size:22px;z-index:2;}
.hud #fmt{color:#ccc;margin:0;}
"""

NAV_JS = """
var items=document.getElementsByTagName('li');
var sel=0;
function show(){for(var i=0;i<items.length;i++){items[i].className=(i==sel)?'sel':'';}}
function move(d){if(!items.length){return;}sel=(sel+d+items.length)%items.length;show();}
function openSel(){if(!items.length||!items[sel]){return;}var a=items[sel].getElementsByTagName('a');if(a.length){window.location=a[0].href;}}
show();
document.onkeydown=function(e){
  e=e||window.event;var k=e.keyCode;
  if(k==38){move(-1);}
  else if(k==40){move(1);}
  else if(k==13||k==39){openSel();}
  else if(k==37||k==8){history.back();}
  else{return true;}
  return false;
};
"""

PLAYER_JS = """
var v=document.getElementById('player_object');
var st=document.getElementById('status');
var s=document.createElement('source');
s.type=%MIME%;
s.src=%URL%;
s.addEventListener('error',function(){st.innerHTML='ERROR: source error';});
v.appendChild(s);
v.style.display='block';
v.setAttribute('width','100%');
v.setAttribute('height','100%');
v.addEventListener('loadstart',function(){st.innerHTML='loadstart';});
v.addEventListener('canplay',function(){st.innerHTML='canplay';});
v.addEventListener('durationchange',function(e){st.innerHTML='duration '+Math.round(e.target.duration)+'s';});
v.addEventListener('timeupdate',function(e){st.innerHTML=Math.round(e.target.currentTime)+'/'+Math.round(e.target.duration)+'s';});
v.addEventListener('error',function(e){st.innerHTML='ERROR: code '+(e.target.error?e.target.error.code:'?');});
v.addEventListener('ended',function(){st.innerHTML='ENDED';});
v.load();v.play();
st.innerHTML='load()+play()';
document.onkeydown=function(e){
  e=e||window.event;var k=e.keyCode;
  if(k==13){if(v.paused){v.play();st.innerHTML='play';}else{v.pause();st.innerHTML='pause';}}
  else if(k==39){try{v.currentTime+=30;}catch(x){}}
  else if(k==37||k==8){history.back();}
  else{return true;}
  return false;
};
"""

IMG_JS = """
document.onkeydown=function(e){
  e=e||window.event;var k=e.keyCode;
  if(k==37||k==8){history.back();}
  else{return true;}
  return false;
};
"""


def esc(s):
    return html.escape(str(s), quote=True)


def _page(title, body, extra_js=NAV_JS):
    return ('<!DOCTYPE html>\n<html><head><meta charset="utf-8">'
            '<title>%s</title><style>%s</style></head>'
            '<body>%s<script>%s</script></body></html>'
            % (esc(title), CSS, body, extra_js))


def render_root():
    objects, total = upnp_browse('0')
    rows = ''.join(
        '<li><a href="/b/%s">%s (%s)</a></li>'
        % (urllib.parse.quote(o['id'], safe=''), esc(o['title']),
           o.get('child_count', '?'))
        for o in objects)
    body = ('<h2 id="hdr">K3D BRAVIA MediaBrowser</h2>'
            '<h2>Serviio @ %s</h2><ul>%s</ul>'
            '<p id="foot">Arrows navigate, OK opens, left = back</p>'
            % (esc(SERVIIO), rows))
    return _page('BRAVIA MediaBrowser', body)


def render_list(obj_id, objects, total, start, title=''):
    rows = ['<li>(no items)</li>'] if not objects else []
    for o in objects:
        qid = urllib.parse.quote(o['id'], safe='')
        if o['container']:
            rows.append('<li><a href="/b/%s">%s (%s)</a></li>'
                        % (qid, esc(o['title']), o['child_count']))
        else:
            # route by upnp:class, not res order: audio tracks carry a
            # JPEG_TN cover-art res that would otherwise win the pick
            cls = o.get('cls', '')
            if 'videoItem' in cls:
                r, kind = pick_video_res(o['res']), 'vid'
            elif 'audioItem' in cls:
                r, kind = pick_audio_res(o['res']), 'aud'
            elif 'imageItem' in cls:
                r, kind = pick_image_res(o['res']), 'img'
            else:
                r = (pick_video_res(o['res']) or pick_audio_res(o['res'])
                     or pick_image_res(o['res']))
                kind = ('img' if r and r['mime'].startswith('image/')
                        else 'aud' if r and r['mime'].startswith('audio/')
                        else 'vid')
            if not r:
                rows.append('<li>%s</li>' % esc(o['title']))
                continue
            rows.append('<li><a href="/%s/%s">%s</a></li>'
                        % (kind, qid, esc(o['title'])))
    nav = ''
    if rows:
        rows[0] = rows[0].replace('<li>', '<li class="sel">', 1)
    if start > 0:
        nav += ('<li><a href="/b/%s?start=%d">&lt; previous</a></li>'
                % (urllib.parse.quote(obj_id, safe=''), max(0, start - PAGE_SIZE)))
    if start + len(objects) < total:
        nav += ('<li><a href="/b/%s?start=%d">next &gt;</a></li>'
                % (urllib.parse.quote(obj_id, safe=''), start + PAGE_SIZE))
    body = ('<h2 id="hdr">K3D BRAVIA MediaBrowser</h2>'
            '<h2>%s <span style="color:#888">%d-%d of %d</span></h2>'
            '<ul>%s%s</ul>'
            '<p id="foot">Arrows navigate, OK opens, left = back</p>'
            % (esc(title or 'Browse'), start + 1, start + len(objects), total,
               ''.join(rows), nav))
    return _page(title or 'Browse', body)


def proxied_res_url(res_url):
    """Wrap a Serviio res URL in our /stream/ proxy (same-client delivery)."""
    return '%s/stream/%s' % (OWN_BASE % PORT,
                             urllib.parse.quote(res_url, safe=''))


def render_player(o, res):
    label = '%s / %s%s' % (res['mime'], res['pn'],
                           ' (converted)' if res['ci'] == '1' else '')
    title = o['title']
    body = ('<div id="player_page">'
            '<video id="player_object" width="0px" height="0px" preload="none"></video>'
            '<p class="hud"><span id="ttl">%s</span> &mdash; '
            '<span id="fmt">%s</span> &mdash; '
            '<span id="status">starting... OK=pause, right=+30s, left=back</span></p>'
            '</div>'
            % (esc(title), esc(label)))
    js = (PLAYER_JS.replace('%MIME%', repr(res['mime']))
                   .replace('%URL%', repr(proxied_res_url(res['url']))))
    return _page(title, body, extra_js=js)


def render_image(o, res):
    body = ('<h2 id="hdr">%s</h2>'
            '<p><img src="%s" alt=""></p>'
            '<p id="foot">left = back</p>'
            % (esc(o['title']), esc(res['url'])))
    return _page(o['title'], body, extra_js=IMG_JS)


def render_error(where, err):
    body = ('<h2 id="hdr">K3D BRAVIA MediaBrowser</h2>'
            '<h2>Error</h2><p id="status">%s</p>'
            '<p id="foot"><a href="/">home</a></p>'
            % esc('%s: %s' % (where, err)))
    return _page('Error', body)


# ---------------------------------------------------------------- http server

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


def _oid_for_item(obj_id):
    """Item pages re-fetch the object's own metadata (BrowseMetadata)."""
    objects, _ = upnp_browse(obj_id, flag='BrowseMetadata', count=1)
    return objects[0] if objects else None


class Handler(BaseHTTPRequestHandler):
    _sent = False  # one HTTP response per request; error paths must not double-send

    def do_GET(self):
        u = urlparse(self.path)
        if u.path.startswith('/stream/'):
            return self.do_stream(u)
        try:
            if u.path == '/':
                body = render_root()
            elif u.path.startswith('/b/'):
                obj_id = urllib.parse.unquote(u.path[3:])
                start = int((parse_qs(u.query).get('start') or ['0'])[0])
                objects, total = upnp_browse(obj_id, start=start)
                if not objects and total == 0:
                    body = render_list(obj_id, [], 0, 0, '(empty)')
                else:
                    # title is cosmetic: best-effort, never discard the listing
                    title = ''
                    try:
                        meta, _ = upnp_browse(obj_id, flag='BrowseMetadata', count=1)
                        if meta:
                            title = meta[0]['title']
                    except Exception:
                        pass
                    body = render_list(obj_id, objects, total, start, title)
            elif u.path.startswith(('/vid/', '/img/', '/aud/')):
                kind = u.path.split('/')[1]
                obj_id = urllib.parse.unquote(u.path.split('/', 2)[2])
                o = _oid_for_item(obj_id)
                if not o:
                    body = render_error('item', 'no metadata for %r' % obj_id)
                elif kind == 'img':
                    r = pick_image_res(o['res'])
                    body = render_image(o, r) if r else render_error('item', 'no image res')
                elif kind == 'aud':
                    r = pick_audio_res(o['res'])
                    body = render_player(o, r) if r else render_error('item', 'no audio res')
                else:
                    r = pick_video_res(o['res'])
                    body = render_player(o, r) if r else render_error('item', 'no video res')
            else:
                self.send_error(404)
                return
            self._send_html(body.encode())
        except urllib.error.HTTPError as e:
            self._send_html(render_error('HTTP %d' % e.code, e.read()[:300]).encode())
        except Exception as e:
            self._send_html(render_error('server', e).encode())

    def do_stream(self, u):
        """Proxy a Serviio res URL with Range passthrough.

        The upstream fetch comes from THIS host (the same client that
        browsed), so Serviio's version-bound res URLs resolve; the TV
        streams from us instead of from Serviio directly.
        """
        target = urllib.parse.unquote(u.path[len('/stream/'):])
        if not target.startswith(RES_BASE + '/'):
            self.send_error(403)
            return
        headers = {'User-Agent': 'K3D-BRAVIA-MediaBrowser/0.1'}
        rng = self.headers.get('Range')
        if rng:
            headers['Range'] = rng
        try:
            req = urllib.request.Request(target, headers=headers)
            upstream = urllib.request.urlopen(req, timeout=30)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            return
        except Exception as e:
            self.send_error(502, str(e))
            return
        try:
            self.send_response(upstream.status)
            for h in ('Content-Type', 'Content-Length', 'Content-Range',
                      'Accept-Ranges'):
                v = upstream.headers.get(h)
                if v:
                    self.send_header(h, v)
            self.end_headers()
            while True:
                chunk = upstream.read(64 * 1024)
                if not chunk:
                    break
                self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass  # player aborted the fetch (seek/stop); upstream closes with us
        finally:
            upstream.close()

    def _send_html(self, payload):
        if self._sent:
            return
        self._sent = True
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass  # TV aborted the fetch; nothing more to send

    def log_message(self, fmt, *args):
        sys.stderr.write('%s - %s\n' % (self.address_string(), fmt % args))


def main():
    print('BRAVIA MediaBrowser proxy: serving on 0.0.0.0:%d' % PORT)
    print('  Serviio UPnP ContentDirectory: %s' % CONTROL_URL)
    ThreadingHTTPServer(('0.0.0.0', PORT), Handler).serve_forever()


if __name__ == '__main__':
    main()