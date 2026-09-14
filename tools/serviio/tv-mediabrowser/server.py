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
import http.client
import json
import os
import queue
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
    # prefer an era-decodable MP3 res when Serviio offers several variants
    for r in auds:
        if r['mime'] == 'audio/mpeg':
            return r
    return auds[0] if auds else None


# ---------------------------------------------------------------- pages

CSS = """
body{background:#000;color:#fff;font-family:sans-serif;margin:0;}
a{color:#fff;text-decoration:none;}
h2{margin:10px;font-size:60px;font-weight:normal;}
#hdr{color:#3cf;font-size:68px;}
ul{list-style:none;margin:10px;padding:0;}
li{padding:10px 14px;font-size:56px;background:#222;border-left:8px solid #3cf;margin:0 0 12px 0;}
li.sel{background:#3cf;color:#000;}
li.sel a{color:#000;}
#foot{color:#999;font-size:44px;margin:10px;}
#status{margin:10px;font-size:56px;}
#fmt{color:#ccc;font-size:44px;margin:0 10px;}
video{background:#000;}
img{max-width:100%;}
/* player pages: full-viewport video like the karajan/DCH app — era Presto
   has no JS fullscreen API, so the video is a fixed 100%x100% element and
   the HUD is a fixed bottom strip; neither is in the document flow, so no
   scrollbar and no embedded letterboxing */
#player_page video{position:fixed;left:0;top:0;width:100%;height:100%;border:0;z-index:1;}
.hud{position:fixed;left:0;bottom:0;width:100%;margin:0;padding:6px 14px;background:#000;color:#fff;font-size:44px;z-index:2;}
.hud #fmt{color:#ccc;margin:0;}
/* #status alone would win on ID specificity (56px) inside the 44px strip */
.hud #status{font-size:44px;margin:0;}
/* music page: album art centered over the on-screen button row; the
   audio element stays 1px in-flow (display:none risks era decode skips) */
#music img{display:block;margin:8px auto;max-width:70%;border:4px solid #333;}
"""

NAV_JS = """
var items=document.getElementsByTagName('li');
var sel=0;
// big-font rows overflow the era viewport: without this the highlight
// walks off-screen and the arrows never scroll (onkeydown returns false)
function show(){for(var i=0;i<items.length;i++){items[i].className=(i==sel)?'sel':'';}if(items.length){try{items[sel].scrollIntoView(false);}catch(x){}}}
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
s.addEventListener('error',function(){st.innerHTML=%hud_err_src%;hideshow(true);});
v.appendChild(s);
v.style.display='block';
v.setAttribute('width','100%');
v.setAttribute('height','100%');
v.addEventListener('loadstart',function(){st.innerHTML=%hud_loadstart%;});
v.addEventListener('canplay',function(){st.innerHTML=%hud_canplay%;});
v.addEventListener('durationchange',function(e){st.innerHTML='duration '+Math.round(e.target.duration)+'s';});
v.addEventListener('timeupdate',function(e){st.innerHTML=Math.round(e.target.currentTime)+'/'+Math.round(e.target.duration)+'s';hideshow(false);});
v.addEventListener('playing',function(){hideshow(false);});
// era Presto may not fire timeupdate reliably — a plain timer is the
// belt-and-braces hide; error/ended above bring the HUD back when it
// becomes the diagnostic surface
setTimeout(function(){hideshow(false);},4000);
v.addEventListener('error',function(e){st.innerHTML=%hud_err_code%+(e.target.error?e.target.error.code:'?');hideshow(true);});
v.addEventListener('ended',function(){st.innerHTML=%hud_ended%;hideshow(true);});
v.load();v.play();
st.innerHTML=%hud_load%;
document.onkeydown=function(e){
  e=e||window.event;var k=e.keyCode;
  if(k==13){if(v.paused){v.play();st.innerHTML=%hud_play%;hideshow(false);}else{v.pause();st.innerHTML=%hud_pause%;hideshow(true);}}
  else if(k==39){try{v.currentTime+=30;}catch(x){}}
  else if(k==37||k==8){history.back();}
  else{return true;}
  return false;
};
"""

MUSIC_JS = """
var v=document.getElementById('player_object');
var st=document.getElementById('status');
var items=document.getElementsByTagName('li');
var sel=0;
function show(){for(var i=0;i<items.length;i++){items[i].className=(i==sel)?'sel':'';}if(items.length){try{items[sel].scrollIntoView(false);}catch(x){}}}
function move(d){if(!items.length){return;}sel=(sel+d+items.length)%items.length;show();}
function act(a){
 if(a=='pp'){if(v.paused){v.play();}else{v.pause();}}
 else if(a=='bk'){try{v.currentTime-=30;}catch(x){}}
 else if(a=='fw'){try{v.currentTime+=30;}catch(x){}}
 else if(a=='back'){history.back();}
}
function openSel(){if(!items.length||!items[sel]){return;}var a=items[sel].getElementsByTagName('a');if(a.length){act(a[0].getAttribute('data-act'));}}
var s=document.createElement('source');
s.type=%MIME%;
s.src=%URL%;
s.addEventListener('error',function(){st.innerHTML=%hud_err_src%;});
v.appendChild(s);
v.addEventListener('timeupdate',function(e){st.innerHTML=Math.round(e.target.currentTime)+'/'+Math.round(e.target.duration)+'s';});
v.addEventListener('error',function(e){st.innerHTML=%hud_err_code%+(e.target.error?e.target.error.code:'?');});
v.addEventListener('ended',function(){st.innerHTML=%hud_ended%;});
v.load();v.play();
st.innerHTML=%hud_load%;
show();
document.onkeydown=function(e){
  e=e||window.event;var k=e.keyCode;
  if(k==38){move(-1);}
  else if(k==40){move(1);}
  else if(k==13){openSel();}
  else if(k==39){act('fw');}
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

# ---------------------------------------------------------------- i18n
# Server-side UI strings. The era browser sends Accept-Language; do_GET
# resolves it once per request into _UI (threading.local — the renderers
# are module-level functions, not methods) and every user-facing string
# goes through T(). 'en' is the base/fallback, 'pt' is the household
# language of the verified sets, 'es' the other big regional language.

_UI = threading.local()

STRINGS = {
    'en': {
        'nav_foot': 'Arrows navigate, OK opens, left = back',
        'no_items': '(no items)',
        'empty': '(empty)',
        'prev': '&lt; previous',
        'next': 'next &gt;',
        'of': 'of',
        'browse': 'Browse',
        'starting': 'starting... OK=pause, right=+30s, left=back',
        'back_foot': 'left = back',
        'error': 'Error',
        'home': 'home',
        'audio': 'Audio',
        'no_audio': 'Play (no audio track)',
        'choose_track': 'Choose the audio track',
        'conv_foot': ('OK starts conversion (first time only; '
                      'later views play instantly). left = back'),
        'dolby_note': 'Dolby tracks play bit-exact (no conversion). ',
        'converting': 'Converting... %d%%',
        'converting_t': 'Converting',
        'refresh_foot': ('this page refreshes every 5s and plays '
                         'automatically when ready. left = back'),
        'converted': ' (converted)',
        'retry': 'conversion failed — OK to try again (cache/%s.log)',
        'lib_building': ('library index still building — '
                         'try again in a few minutes'),
        'locating': ('still locating this title (duration index probing, '
                     'try again in a few minutes)'),
        'no_match': 'no matching file in the mounted library',
        # player HUD live status (PLAYER_JS overwrites #status as playback
        # progresses — these replace what were hardcoded English strings)
        'hud_load': 'loading and playing',
        'hud_loadstart': 'loading stream',
        'hud_canplay': 'ready',
        'hud_play': 'playing',
        'hud_pause': 'paused',
        'hud_ended': 'ended',
        'hud_err_src': 'ERROR: source error',
        'hud_err_code': 'ERROR: code ',
        # error-page detail lines (render_error interpolates these raw)
        'no_meta': 'no metadata for %r',
        'no_image_res': 'no image resource',
        'no_audio_res': 'no audio resource',
        'no_video_res': 'no video resource',
        'clip_missing': 'clip missing: %s',
        # music page (album art + on-screen buttons)
        'btn_pp': 'Play / Pause',
        'btn_b30': '-30 s',
        'btn_f30': '+30 s',
        'btn_back': 'Back',
        'music_foot': 'OK = select button, right = +30s, left = back',
        'music_start': 'playing... OK = pause, right = +30s',
        'music_live': 'live MP3 conversion',
    },
    'pt': {
        'nav_foot': 'Setas navegam, OK abre, esquerda = voltar',
        'no_items': '(sem itens)',
        'empty': '(vazio)',
        'prev': '&lt; anterior',
        'next': 'próximo &gt;',
        'of': 'de',
        'browse': 'Navegar',
        'starting': 'iniciando... OK=pausa, direita=+30s, esquerda=voltar',
        'back_foot': 'esquerda = voltar',
        'error': 'Erro',
        'home': 'início',
        'audio': 'Áudio',
        'no_audio': 'Reproduzir (sem faixa de áudio)',
        'choose_track': 'Escolha a faixa de áudio',
        'conv_foot': ('OK inicia a conversão (só na primeira vez; '
                      'depois toca na hora). esquerda = voltar'),
        'dolby_note': 'Faixas Dolby tocam bit-exatas (sem conversão). ',
        'converting': 'Convertendo... %d%%',
        'converting_t': 'Convertendo',
        'refresh_foot': ('esta página atualiza a cada 5s e toca '
                         'automaticamente quando ficar pronta. esquerda = voltar'),
        'converted': ' (convertido)',
        'retry': 'conversão falhou — OK para tentar de novo (cache/%s.log)',
        'lib_building': ('índice da biblioteca ainda em construção — '
                         'tente de novo em alguns minutos'),
        'locating': ('ainda localizando este título (sondagem do índice de '
                     'durações, tente de novo em alguns minutos)'),
        'no_match': 'nenhum arquivo correspondente na biblioteca montada',
        'hud_load': 'carregando e tocando',
        'hud_loadstart': 'carregando o fluxo',
        'hud_canplay': 'pronto',
        'hud_play': 'tocando',
        'hud_pause': 'pausado',
        'hud_ended': 'fim',
        'hud_err_src': 'ERRO: erro na origem',
        'hud_err_code': 'ERRO: código ',
        'no_meta': 'sem metadados para %r',
        'no_image_res': 'sem recurso de imagem',
        'no_audio_res': 'sem recurso de áudio',
        'no_video_res': 'sem recurso de vídeo',
        'clip_missing': 'clipe ausente: %s',
        'btn_pp': 'Tocar / Pausar',
        'btn_b30': '-30 s',
        'btn_f30': '+30 s',
        'btn_back': 'Voltar',
        'music_foot': 'OK = escolher botão, direita = +30s, esquerda = voltar',
        'music_start': 'tocando... OK = pausa, direita = +30s',
        'music_live': 'conversão MP3 ao vivo',
    },
    'es': {
        'nav_foot': 'Flechas navegan, OK abre, izquierda = volver',
        'no_items': '(sin elementos)',
        'empty': '(vacío)',
        'prev': '&lt; anterior',
        'next': 'siguiente &gt;',
        'of': 'de',
        'browse': 'Explorar',
        'starting': 'iniciando... OK=pausa, derecha=+30s, izquierda=volver',
        'back_foot': 'izquierda = volver',
        'error': 'Error',
        'home': 'inicio',
        'audio': 'Audio',
        'no_audio': 'Reproducir (sin pista de audio)',
        'choose_track': 'Elija la pista de audio',
        'conv_foot': ('OK inicia la conversión (solo la primera vez; '
                      'luego reproduce al instante). izquierda = volver'),
        'dolby_note': 'Las pistas Dolby se reproducen bit-exactas (sin conversión). ',
        'converting': 'Convirtiendo... %d%%',
        'converting_t': 'Convirtiendo',
        'refresh_foot': ('esta página se actualiza cada 5s y reproduce '
                         'automáticamente al estar lista. izquierda = volver'),
        'converted': ' (convertido)',
        'retry': 'conversión fallida — OK para reintentar (cache/%s.log)',
        'lib_building': ('índice de la biblioteca aún en construcción — '
                         'intente de nuevo en unos minutos'),
        'locating': ('aún localizando este título (sondeo del índice de '
                     'duraciones, intente de nuevo en unos minutos)'),
        'no_match': 'ningún archivo coincidente en la biblioteca montada',
        'hud_load': 'cargando y reproduciendo',
        'hud_loadstart': 'cargando el flujo',
        'hud_canplay': 'listo',
        'hud_play': 'reproduciendo',
        'hud_pause': 'en pausa',
        'hud_ended': 'finalizado',
        'hud_err_src': 'ERROR: error de origen',
        'hud_err_code': 'ERROR: código ',
        'no_meta': 'sin metadatos para %r',
        'no_image_res': 'sin recurso de imagen',
        'no_audio_res': 'sin recurso de audio',
        'no_video_res': 'sin recurso de video',
        'clip_missing': 'clip ausente: %s',
        'btn_pp': 'Reproducir / Pausar',
        'btn_b30': '-30 s',
        'btn_f30': '+30 s',
        'btn_back': 'Volver',
        'music_foot': 'OK = elegir botón, derecha = +30s, izquierda = volver',
        'music_start': 'reproduciendo... OK = pausa, derecha = +30s',
        'music_live': 'conversión MP3 en vivo',
    },
}


def T(key):
    lang = getattr(_UI, 'lang', None)
    if lang not in STRINGS:
        lang = 'en'
    return STRINGS[lang].get(key, STRINGS['en'][key])


def set_ui_lang(accept_language):
    """Resolve the request's Accept-Language to a UI language.

    Walks tokens in order, stripping ;q= weights (RFC-legal forms like
    'pt;q=0.9,en;q=0.8' must not defeat the lookup) and falls through to
    later tokens when the first is unsupported.
    """
    for part in (accept_language or '').split(','):
        code = part.split(';', 1)[0].strip().lower()
        code = code.split('-', 1)[0]
        if code in STRINGS:
            _UI.lang = code
            return
    _UI.lang = 'en'


def esc(s):
    return html.escape(str(s), quote=True)


# PLAYER_JS HUD placeholders resolved per-request (json.dumps gives a
# JS-safe quoted literal; T() gives the request's language)
HUD_KEYS = ('hud_err_src', 'hud_loadstart', 'hud_canplay', 'hud_err_code',
            'hud_ended', 'hud_load', 'hud_play', 'hud_pause')


def player_js(mime, url, tpl=PLAYER_JS):
    js = (tpl.replace('%MIME%', repr(mime)).replace('%URL%', repr(url)))
    for k in HUD_KEYS:
        js = js.replace('%%%s%%' % k, json.dumps(T(k)))
    return js


def _latin1(s):
    """HTTP status lines encode latin-1-strict; T() strings and paths
    (Música, em dashes) crash send_error otherwise."""
    return str(s).encode('latin-1', 'replace').decode('latin-1')


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
    body = ('<h2 id="hdr">Servioo BRAVIA 3D edition</h2>'
            '<h2>Serviio @ %s</h2><ul>%s</ul>'
            '<p id="foot">%s</p>'
            % (esc(SERVIIO), rows, T('nav_foot')))
    return _page('BRAVIA MediaBrowser', body)


def render_list(obj_id, objects, total, start, title=''):
    rows = ['<li>%s</li>' % T('no_items')] if not objects else []
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
        nav += ('<li><a href="/b/%s?start=%d">%s</a></li>'
                % (urllib.parse.quote(obj_id, safe=''),
                   max(0, start - PAGE_SIZE), T('prev')))
    if start + len(objects) < total:
        nav += ('<li><a href="/b/%s?start=%d">%s</a></li>'
                % (urllib.parse.quote(obj_id, safe=''),
                   start + PAGE_SIZE, T('next')))
    t_title = esc(title or T('browse'))
    body = ('<h2 id="hdr">Servioo BRAVIA 3D edition</h2>'
            '<h2>%s <span style="color:#888">%d-%d %s %d</span></h2>'
            '<ul>%s%s</ul>'
            '<p id="foot">%s</p>'
            % (t_title, start + 1, start + len(objects), T('of'), total,
               ''.join(rows), nav, T('nav_foot')))
    return _page(title or T('browse'), body)


def proxied_res_url(res_url):
    """Wrap a Serviio res URL in our /stream/ proxy (same-client delivery)."""
    return '%s/stream/%s' % (OWN_BASE % PORT,
                             urllib.parse.quote(res_url, safe=''))


def render_player(o, res):
    label = '%s / %s%s' % (res['mime'], res['pn'],
                           T('converted') if res['ci'] == '1' else '')
    title = o['title']
    body = ('<div id="player_page">'
            '<video id="player_object" width="0px" height="0px" preload="none"></video>'
            '<p class="hud" id="hud"><span id="ttl">%s</span> &mdash; '
            '<span id="fmt">%s</span> &mdash; '
            '<span id="status">%s</span></p>'
            '</div>'
            % (esc(title), esc(label), T('starting')))
    js = player_js(res['mime'], proxied_res_url(res['url']))
    return _page(title, body, extra_js=js)


def render_image(o, res):
    body = ('<h2 id="hdr">%s</h2>'
            '<p><img src="%s" alt=""></p>'
            '<p id="foot">%s</p>'
            % (esc(o['title']), esc(res['url']), T('back_foot')))
    return _page(o['title'], body, extra_js=IMG_JS)


# --------------------------------------------------- music lane (/aud/, /atr/)

def _art_path(obj_id):
    return os.path.join(CACHE_DIR, 'art',
                       _cache_key(obj_id, 0) + '.jpg')


def extract_embedded_art(src, dst):
    """Pull the first embedded cover (ID3 APIC / FLAC picture) into
    cache/art/ as JPEG. True when a usable picture sits at dst."""
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return True
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
    except OSError:
        return False
    tmp = '%s.%d.tmp.jpg' % (dst, threading.get_ident())
    try:
        # re-encode to mjpeg for uniform output (covers arrive as jpeg/
        # png/bmp). Review catch: the bare '.tmp' suffix gave ffmpeg no
        # muxer to infer, so this step silently never worked before.
        r = subprocess.run(['ffmpeg', '-nostdin', '-y', '-v', 'error',
                            '-i', src, '-map', '0:v:0', '-frames:v', '1',
                            '-an', '-q:v', '3', '-f', 'image2', tmp],
                           capture_output=True, timeout=20)
        if r.returncode == 0 and os.path.exists(tmp) \
                and os.path.getsize(tmp) > 0:
            os.replace(tmp, dst)
            return True
    except Exception:
        pass
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    return False


# res mime -> library extension: the first rank tiebreak for dual-format
# stems (one album often exists as both FLAC and MP3)
MIME_EXT = {'audio/mpeg': '.mp3', 'audio/mp3': '.mp3',
            'audio/x-flac': '.flac', 'audio/flac': '.flac',
            'audio/x-wav': '.wav', 'audio/wav': '.wav',
            'audio/mp4': '.m4a', 'audio/aac': '.aac', 'audio/aacp': '.aac',
            'audio/ogg': '.ogg', 'audio/x-ms-wma': '.wma'}


def music_art_available(o):
    """Art ladder for the music page: Serviio's cover res first, then
    embedded extraction (Serviio 404s covers it never generated — the
    'Cover image ... cannot be found' warn). True = show <img>."""
    if pick_image_res(o['res']):
        return True
    src, _ = resolve_source(o['title'], _didl_duration_seconds(o['res']),
                             want='audio')
    return bool(src) and extract_embedded_art(src, _art_path(o['id']))


def render_music(o, res):
    """Music page: album art + on-screen buttons, NOT full-screen.

    MP3 plays era-native (proxied); anything else (FLAC/OGG/WAV/...)
    points at the live /atr/ MP3 pipe — ffmpeg bytes straight to the
    player, nothing written to disk.
    """
    qid = urllib.parse.quote(o['id'], safe='')
    live = res['mime'] != 'audio/mpeg'
    url = ('/atr/%s' % qid) if live else proxied_res_url(res['url'])
    label = res['mime'] + ((', ' + T('music_live')) if live else '')
    art = ('<img src="/art/%s" alt="">' % qid) if music_art_available(o) \
        else ''
    btns = (('pp', 'btn_pp'), ('bk', 'btn_b30'),
            ('fw', 'btn_f30'), ('back', 'btn_back'))
    rows = ''.join('<li><a href="#" data-act="%s">%s</a></li>'
                   % (act, esc(T(key))) for act, key in btns)
    body = ('<div id="music">'
            '<h2 id="hdr">%s</h2>'
            '<p id="fmt">%s</p>'
            '%s'
            '<video id="player_object" width="1px" height="1px" '
            'preload="none" style="width:1px;height:1px;"></video>'
            '<p id="status">%s</p>'
            '<ul>%s</ul>'
            '<p id="foot">%s</p>'
            '</div>'
            % (esc(o['title']), esc(label), art, T('music_start'),
               rows, T('music_foot')))
    js = player_js('audio/mpeg' if live else res['mime'], url, tpl=MUSIC_JS)
    return _page(o['title'], body, extra_js=js)


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
            '<span id="status">%s</span></p>'
            '</div>'
            % (esc(name), esc(mime), T('starting')))
    js = player_js(mime, url)
    return _page(name, body, extra_js=js)


def render_error(where, err):
    body = ('<h2 id="hdr">Servioo BRAVIA 3D edition</h2>'
            '<h2>%s</h2><p id="status">%s</p>'
            '<p id="foot"><a href="/">%s</a></p>'
            % (T('error'), esc('%s: %s' % (where, err)), T('home')))
    return _page(T('error'), body)


def render_tracks(o, fmt):
    """Audio-track selection page for a transcoded item."""
    tracks = audio_tracks(fmt)
    v = next((s for s in fmt.get('streams', [])
              if s.get('codec_type') == 'video'), None)
    vlabel = '%s %dx%d' % (v.get('codec_name') if v else '?',
                           int(v.get('width') or 0), int(v.get('height') or 0))
    rows = []
    for t in tracks:
        label = '%s %d: %s' % (T('audio'), t['n'], t['codec'] or '?')
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
        rows = ['<li><a href="/tr/%s/na">%s</a></li>'
                % (urllib.parse.quote(o['id'], safe=''), T('no_audio'))]
    foot = T('conv_foot')
    if any(t['codec'] in ('ac3', 'eac3') for t in tracks):
        foot = T('dolby_note') + foot
    body = ('<h2 id="hdr">Servioo BRAVIA 3D edition</h2>'
            '<h2>%s <span style="color:#888">%s</span></h2>'
            '<h2>%s</h2><ul>%s</ul>'
            '<p id="foot">%s</p>'
            % (esc(o['title']), esc(vlabel), T('choose_track'),
               ''.join(rows), foot))
    return _page(o['title'], body)


def render_progress(title, pct, note):
    head = '<meta http-equiv="refresh" content="5">'
    body = ('<h2 id="hdr">Servioo BRAVIA 3D edition</h2>'
            '<h2>%s</h2><h2 id="status">%s</h2>'
            '<p id="foot">%s - %s</p>'
            % (esc(title), T('converting') % int(pct), esc(note),
               T('refresh_foot')))
    return _page(T('converting_t'), body, extra_js=IMG_JS, extra_head=head)


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
    'MEDIA_ROOTS', '/mnt/Backup/Vídeos:/mnt/Backup/Música').split(':')
               if os.path.isdir(r)]
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
# era Presto decodes MP3 but not FLAC/OGG/WAV/... — those route to the
# live /atr/ MP3 pipe, so the index must know them too
AUDIO_EXT = ('.mp3', '.flac', '.m4a', '.aac', '.wav', '.ogg', '.oga',
             '.wma', '.opus', '.ape', '.mka')

_lib_lock = threading.Lock()
_lib_by_stem = {}       # lower(filename stem) -> [paths]
_lib_durations = {}     # path -> duration seconds
_lib_kind = {}          # path -> 'video' | 'audio' — the index grew
                        # AUDIO_EXT, so resolve_source must be kind-aware:
                        # a song stem must never resolve as a movie
                        # transcode source, nor a movie as an /atr/ source
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
                ext = os.path.splitext(fn)[1].lower()
                if ext in VIDEO_EXT or ext in AUDIO_EXT:
                    files.append(os.path.join(dirpath, fn))
    by_stem = {}
    by_kind = {}
    for p in files:
        by_stem.setdefault(os.path.splitext(os.path.basename(p))[0].lower(),
                           []).append(p)
        by_kind[p] = ('video'
                      if os.path.splitext(p)[1].lower() in VIDEO_EXT
                      else 'audio')
    with _lib_lock:
        _lib_by_stem.clear()
        _lib_by_stem.update(by_stem)
        _lib_kind.clear()
        _lib_kind.update(by_kind)
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


if os.environ.get('BRAVIA_SKIP_INDEX') != '1':   # unit tests set this
    threading.Thread(target=_build_library_index, daemon=True).start()


def _didl_duration_seconds(res_list):
    for r in res_list or []:
        d = r.get('duration') or ''
        m = re.match(r'^(\d+):(\d+):(\d+)', d)
        if m:
            return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
    return None


def resolve_source(title, didl_dur, want=None, prefer_ext=None):
    """Map a DIDL item to its file in the mounted library.

    want: 'video' or 'audio' — every tier filters to that kind, so the
    index growing AUDIO_EXT can never cross-resolve a song into a movie
    transcode (or a movie into the /atr/ audio lane).
    prefer_ext: '.flac'/'.mp3'/... — first rank tiebreak for dual-format
    stems (the same album often exists as both FLAC and MP3 with
    near-identical durations; the res mime says which one is playing).
    """
    def kind_ok(p):
        if want is None:
            return True
        with _lib_lock:
            return _lib_kind.get(p) == want

    # NB: filter inside this one lock acquisition — calling kind_ok() here
    # would re-acquire _lib_lock (non-reentrant) and deadlock every
    # want=-filtered resolve.
    with _lib_lock:
        paths = [p for p in _lib_by_stem.get(title.lower(), [])
                 if want is None or _lib_kind.get(p) == want]
    if len(paths) == 1:
        return paths[0], None
    nt = _norm_title(title)
    if nt:
        with _lib_lock:
            cands = [p for stem, ps in _lib_by_stem.items()
                     if nt in _norm_title(stem)
                     or _norm_title(stem) in nt for p in ps]
        cands = sorted(set(p for p in cands if kind_ok(p)))
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
            # collision tiebreak: requested format first (dual-format
            # stems: FLAC and MP3 of one song differ by ~1-2s, inside
            # the ±3s duration window, so duration alone ties), then
            # shared title tokens (online-metadata titles translate the
            # filename, but keep words like "adam"), then closer
            # duration. DIDL durations are second-resolution, so a
            # sub-second delta is a strong signal on its own.
            def toks(s):
                return set(w for w in re.split(r'[^a-z0-9]+', s.lower())
                           if len(w) > 1 and not w.isdigit())
            ext_ok = bool(prefer_ext and p.lower().endswith(prefer_ext))
            shared = len(toks(os.path.splitext(os.path.basename(p))[0]) & toks(title))
            return (-ext_ok, -shared, abs(d(p) - didl_dur))

        m = [p for p in paths if d(p) and abs(d(p) - didl_dur) < 3]
        if not m and not paths:
            # duration-index fallback (no title hit at all): inline kind
            # check — kind_ok() would re-acquire _lib_lock and deadlock
            with _lib_lock:
                m = [p for p, dur in _lib_durations.items()
                     if abs(dur - didl_dur) < 3
                     and (want is None or _lib_kind.get(p) == want)]
        if len(m) == 1:
            return m[0], None
        if len(m) > 1:
            ranked = sorted(m, key=rank)
            if rank(ranked[0]) != rank(ranked[1]):
                return ranked[0], None
    if not _lib_ready:
        return None, T('lib_building')
    if not _lib_dur_done:
        return None, T('locating')
    return None, T('no_match')


_jobs = {}   # cache key -> {proc, progress, out, part, duration, encoder}
_jobs_lock = threading.Lock()   # start_job/job_state check-then-act + rename

# live /atr/ ffmpeg pipes: not cached, but they must die with the server
# too (a stalled one would orphan onto init after a restart)
_live_procs = set()
_live_lock = threading.Lock()


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
        set_ui_lang(self.headers.get('Accept-Language'))
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
                    body = render_list(obj_id, [], 0, 0, T('empty'))
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
            elif u.path.startswith('/atr/'):
                return self.do_audio_transcode(u)
            elif u.path.startswith('/art/'):
                return self.do_art(u)
            elif u.path.startswith('/tr/'):
                return self.do_transcode(u)
            elif u.path.startswith('/t/'):
                name = urllib.parse.unquote(u.path[3:])
                if name not in TEST_FILES:
                    self.send_error(404)
                    return
                fn = os.path.join(TEST_DIR, TEST_FILES[name])
                if not os.path.exists(fn):
                    body = render_error('test', T('clip_missing') % name)
                else:
                    body = render_local_player(name, 'video/mp4',
                                               '/t/file/%s' % urllib.parse.quote(name))
                self._send_html(body.encode())
            elif u.path.startswith(('/vid/', '/img/', '/aud/')):
                kind = u.path.split('/')[1]
                obj_id = urllib.parse.unquote(u.path.split('/', 2)[2])
                o = _oid_for_item(obj_id)
                if not o:
                    body = render_error('item', T('no_meta') % obj_id)
                elif kind == 'img':
                    r = pick_image_res(o['res'])
                    body = render_image(o, r) if r else render_error('item', T('no_image_res'))
                elif kind == 'aud':
                    r = pick_audio_res(o['res'])
                    body = render_music(o, r) if r else render_error('item', T('no_audio_res'))
                else:
                    r = pick_video_res(o['res'])
                    body = render_player(o, r) if r else render_error('item', T('no_video_res'))
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

    def do_audio_transcode(self, u):
        """Live audio lane: era Presto decodes MP3 but not FLAC/OGG/WAV;
        ffmpeg pipes libmp3lame bytes straight to the player socket —
        nothing is written to disk (no duplicate files ever).
        No Range support by nature; pause works, seek is best-effort."""
        obj_id = urllib.parse.unquote(u.path[len('/atr/'):])
        o = _oid_for_item(obj_id)
        if not o:
            self.send_error(404)
            return
        r = pick_audio_res(o['res'])
        src, err = resolve_source(
            o['title'], _didl_duration_seconds(o['res']),
            want='audio',
            prefer_ext=MIME_EXT.get(r['mime']) if r else None)
        if not src:
            # review catch: send_error puts this text on the HTTP status
            # line, which encodes latin-1-strict — T() strings carry an
            # em dash and crashed it. Log the note, send a bare status.
            sys.stderr.write('atr: no source for %r: %s\n' % (obj_id, err))
            self.send_error(404, 'no source')
            return
        try:
            proc = subprocess.Popen(
                ['ffmpeg', '-nostdin', '-v', 'error', '-i', src,
                 '-map', '0:a:0', '-c:a', 'libmp3lame', '-q:a', '2',
                 '-f', 'mp3', '-'],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL)
        except Exception as e:
            self.send_error(500, _latin1(e))
            return
        with _live_lock:
            _live_procs.add(proc)
        # review catch: a plain blocking read on proc.stdout hangs the
        # request thread forever when the CIFS source stalls (ffmpeg
        # produces no bytes and no EOF). Pump via a queue with a
        # deadline instead: silence past the timeout kills the stream.
        q = queue.Queue()

        def pump():
            while True:
                b = proc.stdout.read(64 * 1024)
                q.put(b)
                if not b:
                    return

        threading.Thread(target=pump, daemon=True).start()
        try:
            # buffer the first chunk before committing headers: a dead
            # source then answers as an error page, not a silent stall
            try:
                first = q.get(timeout=30)
            except queue.Empty:
                self.send_error(502, 'no audio data')
                return
            if not first:
                self.send_error(502, 'no audio data')
                return
            self.send_response(200)
            self._sent = True   # raw send — no HTML fallback may follow
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Accept-Ranges', 'none')
            self.end_headers()
            self.wfile.write(first)
            while True:
                try:
                    buf = q.get(timeout=30)
                except queue.Empty:
                    break   # source went silent: cut the stream here
                if not buf:
                    break
                self.wfile.write(buf)
        except (BrokenPipeError, ConnectionResetError):
            pass  # player stopped/paused the fetch; ffmpeg dies with us
        finally:
            with _live_lock:
                _live_procs.discard(proc)
            proc.kill()
            try:
                proc.stdout.close()
            except Exception:
                pass
            proc.wait()

    def do_art(self, u):
        """Cover art ladder: Serviio's JPEG res proxied (same-client),
        falling back to embedded extraction when the upstream 404s
        ('Cover image ... cannot be found') or has no res at all."""
        obj_id = urllib.parse.unquote(u.path[len('/art/'):])
        o = _oid_for_item(obj_id)
        if not o:
            self.send_error(404)
            return
        r = pick_image_res(o['res'])
        if r:
            try:
                req = urllib.request.Request(
                    r['url'], headers={'User-Agent': 'K3D-BRAVIA-MediaBrowser/0.1'})
                up = urllib.request.urlopen(req, timeout=30)
            except Exception:
                r = None  # cover promised but unresolvable — fall through
            else:
                try:
                    self.send_response(200)
                    self.send_header(
                        'Content-Type',
                        up.headers.get('Content-Type') or 'image/jpeg')
                    self.send_header('Cache-Control', 'no-cache')
                    self.end_headers()
                    self._sent = True   # headers committed — no error page after
                    while True:
                        chunk = up.read(64 * 1024)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                except (OSError, http.client.HTTPException):
                    # broken pipe/reset/timeout mid-body — same handling as
                    # _serve_file; must NOT fall through to send_error (404)
                    # which would emit a second status line on this socket.
                    pass
                finally:
                    up.close()
                return
        # No Serviio thumbnail, or it 404'd (live-observed "Cover image
        # cannot be found") — fall back to embedded cover art. Art lives on
        # the audio side: never resolve to a video file sharing the stem.
        src, _ = resolve_source(o['title'], _didl_duration_seconds(o['res']),
                                want='audio')
        if src and extract_embedded_art(src, _art_path(obj_id)):
            self._serve_file(_art_path(obj_id), 'image/jpeg')
            return
        self.send_error(404)

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
                    'transcode', T('no_meta') % obj_id).encode())
                return
            r = pick_video_res(o['res'])
            if track is None and r and r['mime'] == 'video/mp4':
                self._send_html(render_player(o, r).encode())  # direct-play
                return
            dur = _didl_duration_seconds(o['res'])
            src, err = resolve_source(o['title'], dur, want='video')
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
                        'transcode', T('retry') % key).encode())
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
    with _live_lock:
        for p in _live_procs:
            try:
                p.kill()
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