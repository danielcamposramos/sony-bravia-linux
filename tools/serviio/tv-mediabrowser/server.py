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

import hashlib
import html
import json
import os
import re
import signal
import subprocess
import sys
import threading
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
var hud=document.getElementById('hud');
function hideshow(v2){if(hud){hud.style.visibility=v2?'visible':'hidden';}}
var s=document.createElement('source');
s.type=%MIME%;
s.src=%URL%;
s.addEventListener('error',function(){st.innerHTML='ERROR: source error';hideshow(true);});
v.appendChild(s);
v.style.display='block';
v.setAttribute('width','100%');
v.setAttribute('height','100%');
v.addEventListener('loadstart',function(){st.innerHTML='loadstart';});
v.addEventListener('canplay',function(){st.innerHTML='canplay';});
v.addEventListener('durationchange',function(e){st.innerHTML='duration '+Math.round(e.target.duration)+'s';});
v.addEventListener('timeupdate',function(e){st.innerHTML=Math.round(e.target.currentTime)+'/'+Math.round(e.target.duration)+'s';hideshow(false);});
v.addEventListener('playing',function(){hideshow(false);});
// era Presto may not fire timeupdate reliably — a plain timer is the
// belt-and-braces hide; error/ended above bring the HUD back when it
// becomes the diagnostic surface
setTimeout(function(){hideshow(false);},4000);
v.addEventListener('error',function(e){st.innerHTML='ERROR: code '+(e.target.error?e.target.error.code:'?');hideshow(true);});
v.addEventListener('ended',function(){st.innerHTML='ENDED';hideshow(true);});
v.load();v.play();
st.innerHTML='load()+play()';
document.onkeydown=function(e){
  e=e||window.event;var k=e.keyCode;
  if(k==13){if(v.paused){v.play();st.innerHTML='play';hideshow(false);}else{v.pause();st.innerHTML='pause';hideshow(true);}}
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


def _page(title, body, extra_js=NAV_JS, extra_head=''):
    return ('<!DOCTYPE html>\n<html><head><meta charset="utf-8">'
            '<title>%s</title>%s<style>%s</style></head>'
            '<body>%s<script>%s</script></body></html>'
            % (esc(title), extra_head, CSS, body, extra_js))


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
                r = pick_video_res(o['res'])
                # era player only decodes progressive MP4 — anything else
                # goes to the app-side transcode lane (audio-track page)
                kind = ('vid' if r and r['mime'] == 'video/mp4' else 'tr')
                if not r:
                    kind = 'tr'  # probe/convert even with no playable res
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
                if kind == 'tr':
                    # no playable res at all — still offer the transcode
                    # lane: it locates the source by DIDL title/duration
                    rows.append('<li><a href="/tr/%s">%s</a></li>'
                                % (qid, esc(o['title'])))
                else:
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
            '<p class="hud" id="hud"><span id="ttl">%s</span> &mdash; '
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


# ------------------------------------------------- format-probe lane (/t/)

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test')
TEST_FILES = {'faststart': 'test-faststart.mp4',   # control: proven-playable layout
              'fmp4': 'test-fmp4.mp4',             # probe: fragmented MP4
              'ac3': 'test-ac3.mp4',               # probe: Dolby AC-3 5.1 (re-encoded)
              'eac3': 'test-eac3.mp4'}             # probe: E-AC3 5.1 lossless remux


def render_local_player(name, mime, url):
    body = ('<div id="player_page">'
            '<video id="player_object" width="0px" height="0px" preload="none"></video>'
            '<p class="hud" id="hud"><span id="ttl">%s</span> &mdash; '
            '<span id="fmt">%s</span> &mdash; '
            '<span id="status">starting... OK=pause, right=+30s, left=back</span></p>'
            '</div>'
            % (esc(name), esc(mime)))
    js = PLAYER_JS.replace('%MIME%', repr(mime)).replace('%URL%', repr(url))
    return _page(name, body, extra_js=js)


def render_error(where, err):
    body = ('<h2 id="hdr">K3D BRAVIA MediaBrowser</h2>'
            '<h2>Error</h2><p id="status">%s</p>'
            '<p id="foot"><a href="/">home</a></p>'
            % esc('%s: %s' % (where, err)))
    return _page('Error', body)


def render_tracks(o, fmt):
    """Audio-track selection page for a transcoded item."""
    tracks = audio_tracks(fmt)
    v = next((s for s in fmt.get('streams', [])
              if s.get('codec_type') == 'video'), None)
    vlabel = '%s %dx%d' % (v.get('codec_name') if v else '?',
                           int(v.get('width') or 0), int(v.get('height') or 0))
    rows = []
    for t in tracks:
        label = 'Audio %d: %s' % (t['n'], t['codec'] or '?')
        if t['lang']:
            label += ' (%s)' % t['lang']
        if t['ch']:
            label += ' %dch' % t['ch']
        if t['title']:
            label += ' - %s' % t['title']
        rows.append('<li><a href="/tr/%s/%d">%s</a></li>'
                    % (urllib.parse.quote(o['id'], safe=''), t['n'],
                       esc(label)))
    if not rows:
        rows = ['<li><a href="/tr/%s/na">Play (no audio track)</a></li>'
                % urllib.parse.quote(o['id'], safe='')]
    foot = 'OK starts conversion (first time only; later views play instantly). left = back'
    if any(t['codec'] in ('ac3', 'eac3') for t in tracks):
        foot = ('Dolby tracks play bit-exact (no conversion). ' + foot)
    body = ('<h2 id="hdr">K3D BRAVIA MediaBrowser</h2>'
            '<h2>%s <span style="color:#888">%s</span></h2>'
            '<h2>Choose the audio track</h2><ul>%s</ul>'
            '<p id="foot">%s</p>'
            % (esc(o['title']), esc(vlabel), ''.join(rows), foot))
    return _page(o['title'], body)


def render_progress(title, pct, note):
    head = '<meta http-equiv="refresh" content="5">'
    body = ('<h2 id="hdr">K3D BRAVIA MediaBrowser</h2>'
            '<h2>%s</h2><h2 id="status">Converting... %d%%</h2>'
            '<p id="foot">%s - this page refreshes every 5s and plays automatically when ready. left = back</p>'
            % (esc(title), int(pct), esc(note)))
    return _page('Converting', body, extra_js=IMG_JS, extra_head=head)


# ---------------------------------------------------------------- http server

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


def _oid_for_item(obj_id):
    """Item pages re-fetch the object's own metadata (BrowseMetadata)."""
    objects, _ = upnp_browse(obj_id, flag='BrowseMetadata', count=1)
    return objects[0] if objects else None


# ------------------------------------------------------- transcode lane
#
# The era browser player accepts only progressive faststart MP4 (see
# README): MKV/AVI/... are refused client-side, Serviio's live transcode
# targets are all TS-family (refused too), and fragmented MP4 is fetched
# but not decoded. So the app transcodes on demand, app-side:
#
#   DIDL item (title + res@duration) -> source file in the mounted
#   library -> ffprobe audio tracks -> track-selection page ->
#   ffmpeg (video copy when era-compatible, else era-safe x264; chosen
#   audio -> AAC; +faststart) -> cache/<key>.mp4 -> native player.
#
# Item->file mapping: Serviio DIDL titles come from online metadata and
# can differ completely from the filename, so the primary key is the
# DIDL duration matched against a ffprobe duration index of the library
# (built once in the background, persisted, refreshed by mtime). Exact
# and normalized title matches are fast path + tiebreaker.

MEDIA_ROOTS = [r for r in os.environ.get(
    'MEDIA_ROOTS', '/mnt/Backup/Vídeos').split(':') if os.path.isdir(r)]
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)
# sweep stale transcode remnants at startup: a part file with no live job
# belongs to a dead run (killed server, orphaned ffmpeg). Unlink it so a
# fresh request restarts cleanly instead of double-writing against it.
# (A SIGKILL'd ffmpeg could in theory still hold the unlinked inode; its
# output goes nowhere and its rename never happens — safe.)
for _fn in os.listdir(CACHE_DIR):
    if _fn.endswith(('.part.mp4', '.prog')):
        try:
            os.remove(os.path.join(CACHE_DIR, _fn))
        except OSError:
            pass
VIDEO_EXT = ('.mkv', '.avi', '.mpg', '.mpeg', '.ts', '.m2ts', '.mts',
             '.flv', '.wmv', '.mov', '.mp4', '.m4v', '.vob')

_lib_lock = threading.Lock()
_lib_by_stem = {}       # lower(filename stem) -> [paths]
_lib_durations = {}     # path -> duration seconds
_lib_ready = False      # stems usable (phase 1 done)
_lib_dur_done = False   # duration pass complete (phase 2 done)
_lib_note = ''


def _norm_title(s):
    return re.sub(r'[^a-z0-9]+', '', s.lower())


def _probe_duration(path):
    try:
        out = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'json', path], capture_output=True, timeout=120)
        return float(json.loads(out.stdout)['format']['duration'])
    except Exception:
        return None


def _probe_streams(path):
    out = subprocess.run(
        ['ffprobe', '-v', 'error', '-print_format', 'json',
         '-show_streams', '-show_format', path],
        capture_output=True, timeout=120)
    return json.loads(out.stdout)


def _build_library_index():
    """Two phases so the lane is usable fast:

    1. os.walk + stem map (minutes over CIFS) — then _lib_ready flips, and
       resolve_source's stem/normalized-title tiers work. Most DIDL titles
       match here without any probing.
    2. Duration probes (the fallback tier for metadata-mangled titles) run
       in the background and land in _lib_durations incrementally.
    """
    global _lib_ready, _lib_note
    files = []
    for root in MEDIA_ROOTS:
        for dirpath, dirnames, filenames in os.walk(root):
            for fn in filenames:
                if os.path.splitext(fn)[1].lower() in VIDEO_EXT:
                    files.append(os.path.join(dirpath, fn))
    by_stem = {}
    for p in files:
        by_stem.setdefault(os.path.splitext(os.path.basename(p))[0].lower(),
                           []).append(p)
    with _lib_lock:
        _lib_by_stem.clear()
        _lib_by_stem.update(by_stem)
        _lib_ready = True
        _lib_note = '%d files, %d probed' % (len(files), 0)
    sys.stderr.write('library stems ready: %d files\n' % len(files))

    # phase 2: durations — persisted cache (path -> {mtime, dur}) keeps
    # restarts fast; saved periodically so a restart doesn't lose hours
    dcache_path = os.path.join(CACHE_DIR, 'probe-index.json')
    dcache = {}
    try:
        dcache = json.load(open(dcache_path))
    except Exception:
        pass

    def probe(p):
        try:
            st = os.stat(p)
            mtime = int(st.st_mtime)
            cached = dcache.get(p)
            if cached and cached.get('mtime') == mtime and cached.get('dur'):
                return p, cached['dur'], False
            d = _probe_duration(p)
            if d:
                dcache[p] = {'mtime': mtime, 'dur': d}
            return p, d, True
        except Exception:
            return p, None, False

    probed = 0
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=12) as ex:
        for p, d, fresh in ex.map(probe, files):
            if d:
                with _lib_lock:
                    _lib_durations[p] = d
            if fresh:
                probed += 1
                if probed % 500 == 0:
                    try:
                        json.dump(dcache, open(dcache_path, 'w'))
                    except Exception:
                        pass
                    with _lib_lock:
                        _lib_note = ('%d files, %d probed'
                                     % (len(files), len(_lib_durations)))
                    sys.stderr.write('library probe pass: %s\n' % _lib_note)
    try:
        json.dump(dcache, open(dcache_path, 'w'))
    except Exception:
        pass
    with _lib_lock:
        _lib_note = '%d files, %d probed' % (len(files), len(_lib_durations))
    global _lib_dur_done
    _lib_dur_done = True
    sys.stderr.write('library durations ready: %s\n' % _lib_note)


threading.Thread(target=_build_library_index, daemon=True).start()


def _didl_duration_seconds(res_list):
    for r in res_list or []:
        d = r.get('duration') or ''
        m = re.match(r'^(\d+):(\d+):(\d+)', d)
        if m:
            return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
    return None


def resolve_source(title, didl_dur):
    """Map a DIDL item to its file in the mounted library."""
    with _lib_lock:
        paths = list(_lib_by_stem.get(title.lower(), []))
    if len(paths) == 1:
        return paths[0], None
    nt = _norm_title(title)
    if nt:
        with _lib_lock:
            cands = [p for stem, ps in _lib_by_stem.items()
                     if nt in _norm_title(stem)
                     or _norm_title(stem) in nt for p in ps]
        cands = sorted(set(cands))
        if len(cands) == 1:
            p0 = cands[0]
            # cross-check against the DIDL duration when we have one and
            # know this file's: containment on short titles ("13" ⊂
            # "The 13th Warrior") is otherwise a false-positive class
            with _lib_lock:
                d0 = _lib_durations.get(p0)
            if not didl_dur or not d0 or abs(d0 - didl_dur) < 3:
                return p0, None
        if cands:
            paths = cands
    if didl_dur:
        def d(p):
            with _lib_lock:
                return _lib_durations.get(p)

        def rank(p):
            # collision tiebreak: shared title tokens first (online-metadata
            # titles translate the filename, but keep words like "adam"),
            # then closer duration. DIDL durations are second-resolution,
            # so a sub-second delta is a strong signal on its own.
            def toks(s):
                return set(w for w in re.split(r'[^a-z0-9]+', s.lower())
                           if len(w) > 1 and not w.isdigit())
            shared = len(toks(os.path.splitext(os.path.basename(p))[0]) & toks(title))
            return (-shared, abs(d(p) - didl_dur))

        m = [p for p in paths if d(p) and abs(d(p) - didl_dur) < 3]
        if len(m) == 1:
            return m[0], None
        if not m and not paths:
            with _lib_lock:
                m = [p for p, dur in _lib_durations.items()
                     if abs(dur - didl_dur) < 3]
        if len(m) > 1:
            ranked = sorted(m, key=rank)
            if rank(ranked[0]) != rank(ranked[1]):
                return ranked[0], None
    if not _lib_ready:
        return None, 'library index still building — try again in a few minutes'
    if not _lib_dur_done:
        return None, ('still locating this title (duration index probing, '
                      'try again in a few minutes)')
    return None, 'no matching file in the mounted library'


_jobs = {}   # cache key -> {proc, progress, out, part, duration, encoder}
_jobs_lock = threading.Lock()   # start_job/job_state check-then-act + rename


def _cache_key(obj_id, track):
    return hashlib.sha1(('%s#a%d' % (obj_id, track)).encode()).hexdigest()[:16]


_nvenc_ok = {'tested': False, 'ok': False}


def _nvenc_available():
    """RTX 3060 on the app host (d2server has a 970 for later). NVENC
    H.264 emits no weighted prediction, so output is EX7xx-safe."""
    if not _nvenc_ok['tested']:
        try:
            r = subprocess.run(
                ['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                 'testsrc2=size=320x240:duration=0.2:rate=10',
                 '-c:v', 'h264_nvenc', '-f', 'null', '-'],
                capture_output=True, timeout=30)
            _nvenc_ok['ok'] = r.returncode == 0
        except Exception:
            _nvenc_ok['ok'] = False
        _nvenc_ok['tested'] = True
    return _nvenc_ok['ok']


def encode_args(copy_ok, need_scale=False):
    if copy_ok:
        return ['-c:v', 'copy'], 'copy'
    # >1920-wide sources are scaled down on re-encode: the EX7xx 2011
    # decoder tops out at 1080p, and L4.1 written on a 4K frame would be
    # refused. need_scale is only set when width>1920, so no upscale risk.
    vf = ['-vf', 'scale=1920:-2'] if need_scale else []
    if _nvenc_available():
        return (['-c:v', 'h264_nvenc', '-pix_fmt', 'yuv420p',
                 '-profile:v', 'high', '-level', '4.1',
                 '-rc', 'vbr', '-cq', '23', '-b:v', '0'] + vf, 'nvenc')
    return (['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
             '-pix_fmt', 'yuv420p',
             '-x264-params', 'weightp=0:weightb=0',
             '-profile:v', 'high', '-level', '4.0'] + vf, 'x264')


def audio_tracks(fmt):
    return [{'n': n, 'codec': s.get('codec_name'),
             'lang': (s.get('tags') or {}).get('language'),
             'ch': s.get('channels'),
             'title': (s.get('tags') or {}).get('title')}
            for n, s in enumerate(
                [s for s in fmt.get('streams', [])
                 if s.get('codec_type') == 'audio'])]


def video_decision(fmt):
    """Era-safe delivery: copy H.264 8-bit <=L4.1 <=1920, re-encode the rest.
    (The EX7xx 2011 decoder refuses weighted_pred_flag=1 — weightp is
    disabled on the encode path; copy of a weightp stream is a known
    limitation, see the SEI wiki page.)"""
    v = next((s for s in fmt.get('streams', [])
              if s.get('codec_type') == 'video'), None)
    if v is None:
        return False
    ok = (v.get('codec_name') == 'h264'
          and v.get('pix_fmt') in ('yuv420p',)
          and int(v.get('level') or 99) <= 41
          and int(v.get('width') or 0) <= 1920)
    return ok


def start_job(src, obj_id, track, copy_ok, duration, force_x264=False,
               need_scale=False, channels=None, acodec=None):
    key = _cache_key(obj_id, track)
    outp = os.path.join(CACHE_DIR, key + '.mp4')
    if os.path.exists(outp) and os.path.getsize(outp) > 0:
        return key, outp
    # build the encode plan BEFORE taking _jobs_lock: the one-time NVENC
    # availability probe runs ffmpeg (~1 s) and must not serialize requests
    vargs, encoder = encode_args(copy_ok, need_scale)
    if force_x264 and encoder == 'nvenc':
        # NVENC failed on this source — force the x264 branch explicitly
        # (the global _nvenc_ok stays untouched: the failure may be
        # source-specific, other sources keep the fast path)
        vargs = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                 '-pix_fmt', 'yuv420p',
                 '-x264-params', 'weightp=0:weightb=0',
                 '-profile:v', 'high', '-level', '4.0']
        if need_scale:
            vargs += ['-vf', 'scale=1920:-2']
        encoder = 'x264'
    if track < 0:
        audio = ['-an']
    elif acodec in ('ac3', 'eac3'):
        # era player decodes Dolby tracks in MP4 — live-verified on the
        # EX725 2026-09-14 (/t/eac3 probe: h264 + copied E-AC3 5.1 played).
        # Copy bit-exact: Dolby Digital (Plus) 5.1 over HDMI, no quality
        # loss, and with copy_ok video the whole job is a pure remux.
        audio = ['-map', '0:a:%d' % track, '-c:a', 'copy']
    else:
        # keep the source channel layout (5.1 stays 5.1 — the sets decode
        # multichannel AAC and pass it over HDMI); 48 kHz is the era-safe
        # rate; bitrate scales with the layout
        abr = 640 if (channels or 2) > 2 else 256
        audio = ['-map', '0:a:%d' % track, '-c:a', 'aac',
                '-b:a', '%dk' % abr, '-ar', '48000']
    part = os.path.join(CACHE_DIR, key + '.part.mp4')
    prog = os.path.join(CACHE_DIR, key + '.prog')
    cmd = (['ffmpeg', '-y', '-v', 'error', '-i', src,
            '-map', '0:v:0'] + audio + vargs +
           ['-sn', '-movflags', '+faststart', '-progress', prog,
            '-nostdin', part])
    with _jobs_lock:
        # check-then-act under the lock: a second request for the same
        # item (IR repeat, meta-refresh racing OK) must see the live job
        # here instead of double-spawning ffmpeg onto the same .part file
        if os.path.exists(outp) and os.path.getsize(outp) > 0:
            return key, outp
        j = _jobs.get(key)
        if j and j['proc'].poll() is None:
            return key, outp
        logf = open(os.path.join(CACHE_DIR, key + '.log'), 'w')
        proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, process_group=0)
        logf.close()  # child holds its own copy; don't leak the parent fd
        _jobs[key] = {'proc': proc, 'progress': prog, 'out': outp,
                      'part': part, 'duration': duration,
                      'encoder': encoder, 'force_x264': force_x264}
    return key, outp


def job_state(key):
    outp = os.path.join(CACHE_DIR, key + '.mp4')
    if os.path.exists(outp) and os.path.getsize(outp) > 0:
        return 'done', 100
    with _jobs_lock:
        j = _jobs.get(key)
        if j is None:
            return 'none', 0
        if j['proc'].poll() is None:
            pct = 0
            try:
                txt = open(j['progress']).read()
                us = re.findall(r'out_time_us=(\d+)', txt)
                if us and j['duration']:
                    pct = min(99, int(us[-1]) / (j['duration'] * 1e6) * 100)
            except Exception:
                pass
            return 'running', pct
        if j['proc'].returncode == 0:
            try:
                os.rename(j['part'], outp)
            except OSError:
                return 'failed', 0
            return 'done', 100
        return 'failed', 0


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
            elif u.path.startswith('/t/file/'):
                return self.do_local_file(u)
            elif u.path.startswith('/tcf/'):
                return self.do_cache_file(u)
            elif u.path.startswith('/tr/'):
                return self.do_transcode(u)
            elif u.path.startswith('/t/'):
                name = urllib.parse.unquote(u.path[3:])
                if name not in TEST_FILES:
                    self.send_error(404)
                    return
                fn = os.path.join(TEST_DIR, TEST_FILES[name])
                if not os.path.exists(fn):
                    body = render_error('test', 'clip missing: %s' % name)
                else:
                    body = render_local_player(name, 'video/mp4',
                                               '/t/file/%s' % urllib.parse.quote(name))
                self._send_html(body.encode())
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

    def _serve_file(self, fn, mime):
        """Serve a file with byte-range support (era player sends
        Range: bytes=0- even on first fetch and expects 206, like
        Serviio/DCH answer)."""
        size = os.path.getsize(fn)
        start, end = 0, size          # end is exclusive
        ranged = bool(self.headers.get('Range'))
        m = re.match(r'bytes=(\d+)-(\d*)', self.headers.get('Range') or '')
        if m:
            start = int(m.group(1))
            if m.group(2):
                end = min(int(m.group(2)) + 1, size)
        length = end - start
        if start >= size:
            self.send_response(416)
            self.send_header('Content-Range', 'bytes */%d' % size)
            self.end_headers()
            return
        try:
            self.send_response(206 if ranged else 200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(length))
            self.send_header('Accept-Ranges', 'bytes')
            if ranged:
                self.send_header('Content-Range',
                                 'bytes %d-%d/%d' % (start, end - 1, size))
            self.end_headers()
            with open(fn, 'rb') as f:
                f.seek(start)
                while True:
                    chunk = f.read(64 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass  # player aborted the fetch

    def do_local_file(self, u):
        """Serve a test clip from ./test."""
        name = urllib.parse.unquote(u.path[len('/t/file/'):])
        if name not in TEST_FILES:
            self.send_error(404)
            return
        fn = os.path.join(TEST_DIR, TEST_FILES[name])
        if not os.path.exists(fn):
            self.send_error(404)
            return
        self._serve_file(fn, 'video/mp4')

    def do_cache_file(self, u):
        """Serve a finished transcode from the cache."""
        key = urllib.parse.unquote(u.path[len('/tcf/'):])
        if not re.match(r'^[0-9a-f]{16}$', key):
            self.send_error(404)
            return
        fn = os.path.join(CACHE_DIR, key + '.mp4')
        if not os.path.exists(fn):
            self.send_error(404)
            return
        self._serve_file(fn, 'video/mp4')

    def do_transcode(self, u):
        """Audio-track selection + on-demand faststart-MP4 transcode."""
        parts = [p for p in u.path[4:].split('/') if p]
        if not parts:
            self.send_error(404)
            return
        obj_id = urllib.parse.unquote(parts[0])
        track = None
        if len(parts) > 1:
            track = -1 if parts[1] == 'na' else int(parts[1])
        try:
            o = _oid_for_item(obj_id)
            if not o:
                self._send_html(render_error(
                    'transcode', 'no metadata for %r' % obj_id).encode())
                return
            r = pick_video_res(o['res'])
            if track is None and r and r['mime'] == 'video/mp4':
                self._send_html(render_player(o, r).encode())  # direct-play
                return
            dur = _didl_duration_seconds(o['res'])
            src, err = resolve_source(o['title'], dur)
            if not src:
                self._send_html(render_error(
                    'transcode', err or 'source not found').encode())
                return
            if track is None:
                fmt = _probe_streams(src)
                self._send_html(render_tracks(o, fmt).encode())
                return
            key = _cache_key(obj_id, track)
            st, pct = job_state(key)
            force_x264 = False
            if st == 'failed':
                with _jobs_lock:
                    j = _jobs.get(key) or {}
                    # NVENC failed on this source — degrade to the software
                    # path once. _nvenc_ok stays untouched: the failure may
                    # be source-specific, other items keep the fast path.
                    if j.get('encoder') == 'nvenc' and not j.get('force_x264'):
                        force_x264 = True
                    for ext in ('.part.mp4', '.prog'):
                        try:
                            os.remove(os.path.join(CACHE_DIR, key + ext))
                        except OSError:
                            pass
                    _jobs.pop(key, None)
                if not force_x264:
                    # pop the entry so the next OK retries instead of a
                    # terminal dead state (failure may have been transient)
                    self._send_html(render_error(
                        'transcode',
                        'conversion failed — OK to try again '
                        '(cache/%s.log)' % key).encode())
                    return
                st, pct = 'none', 0
            if st == 'none':
                fmt = _probe_streams(src)
                if not dur:
                    try:
                        dur = float(fmt['format'].get('duration') or 0) or None
                    except Exception:
                        pass
                v = next((s for s in fmt.get('streams', [])
                          if s.get('codec_type') == 'video'), None)
                need_scale = bool(v) and int(v.get('width') or 0) > 1920
                ch = acodec = None
                if track >= 0:
                    atr = audio_tracks(fmt)
                    if 0 <= track < len(atr):
                        ch = atr[track]['ch']
                        acodec = atr[track]['codec']
                start_job(src, obj_id, track, video_decision(fmt), dur,
                          force_x264=force_x264,
                          need_scale=need_scale, channels=ch, acodec=acodec)
                st, pct = 'running', 0
            if st == 'done':
                self._send_html(render_local_player(
                    o['title'], 'video/mp4', '/tcf/%s' % key).encode())
            else:
                self._send_html(render_progress(
                    o['title'], pct, _lib_note).encode())
        except Exception as e:
            self._send_html(render_error('transcode', e).encode())

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


def _kill_live_jobs():
    """SIGTERM handler: on restart (kill+setsid) the running ffmpeg
    children die with us instead of orphaning onto their part files."""
    with _jobs_lock:
        for j in _jobs.values():
            try:
                if j['proc'].poll() is None:
                    os.killpg(os.getpgid(j['proc'].pid), signal.SIGTERM)
                    j['proc'].wait(timeout=10)
            except Exception:
                pass


def _on_sigterm(signum, frame):
    _kill_live_jobs()
    sys.exit(0)


def main():
    signal.signal(signal.SIGTERM, _on_sigterm)
    print('BRAVIA MediaBrowser proxy: serving on 0.0.0.0:%d' % PORT)
    print('  Serviio UPnP ContentDirectory: %s' % CONTROL_URL)
    ThreadingHTTPServer(('0.0.0.0', PORT), Handler).serve_forever()


if __name__ == '__main__':
    main()