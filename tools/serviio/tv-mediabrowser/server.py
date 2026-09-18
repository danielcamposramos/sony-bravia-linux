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

import configparser
import hashlib
import html
import http.client
import json
import os
import queue
import re
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------- config
# Install-time surface: everything host/path specific lives in a config
# file (INI) next to this file — config.ini by default, override the
# location with BRAVIA_CONFIG=/path. Precedence per option: environment >
# config file > built-in default, so a deployed box is configured by file
# while tests stay env-driven. See config.ini.example in this directory.

CONFIG_PATH = os.environ.get(
    'BRAVIA_CONFIG',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini'))
_cfg = configparser.ConfigParser()
if os.path.isfile(CONFIG_PATH):
    _cfg.read(CONFIG_PATH, encoding='utf-8')


def _cfg_get(section, option, default):
    if _cfg.has_option(section, option):
        return _cfg.get(section, option).strip()
    return default


def _cfg_int(section, option, default):
    try:
        return int(_cfg_get(section, option, default))
    except (TypeError, ValueError):
        return default


# Remote multimedia-key codes: which keyCode the era browser reports for
# each of the remote's media buttons. The shipped values are an educated
# guess (the Android-TV keyCode family) — the ground truth for a given
# set is two minutes at the /keys probe page: every press shows its code
# on screen AND is logged server-side. Paste the observed numbers into
# config.ini [keys] and restart. 0 = unmapped/disabled.
KEY_ACTIONS = ('playpause', 'play', 'pause', 'stop', 'prev', 'next',
                'rew', 'ff')
KEY_DEFAULTS = {'playpause': '85', 'play': '126', 'pause': '127',
                'stop': '86', 'prev': '88', 'next': '87',
                'rew': '89', 'ff': '90'}
KEYMAP = {}
for _act in KEY_ACTIONS:
    _codes = [int(c.strip()) for c in
              _cfg_get('keys', _act, KEY_DEFAULTS[_act]).split(',')
              if c.strip().isdigit()]
    KEYMAP[_act] = [c for c in _codes if c > 0]

SERVIIO = os.environ.get(
    'SERVIIO', _cfg_get('serviio', 'host', '192.168.0.60'))
SERVIIO_PORT = _cfg_int('serviio', 'port', 8895)
CONTROL_URL = 'http://%s:%d/serviceControl' % (SERVIIO, SERVIIO_PORT)
RES_BASE = 'http://%s:%d' % (SERVIIO, SERVIIO_PORT)
# Serviio binds res URLs to the browsing client's IP: when the TV fetched
# them directly, Serviio answered 500 "No media description available for
# required version" (verified live). So the app proxies media through
# itself: browse client == fetch client, and the TV streams Range/206
# from this server instead. The proxy URL is RELATIVE (see
# proxied_res_url) so it survives host moves.
PAGE_SIZE = 18
# The TV's own start page (the rd1.sony.net host we serve on the LAN).
# Configurable because the spoof target is a deployment detail.
PORTAL_URL = _cfg_get('app', 'portal_url', 'https://rd1.sony.net/tv1/')
# CLI arg still wins (the systemd unit passes its port), then the config
# file, then the built-in default
PORT = (int(sys.argv[1]) if len(sys.argv) > 1 else
        _cfg_int('app', 'port', 8090))
BIND_HOST = _cfg_get('app', 'bind_host', '0.0.0.0')

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
/* Every size below is tuned for the TV browser's MEDIUM font setting.
   Large or Small will overflow the viewport or drop under couch-reading
   distance; there is no media query on this engine to compensate. */
ul{list-style:none;margin:10px;padding:0;}
/* audio player: small grey library path, and the legend of the
   actions the native control bar has no concept of */
.loc{font-size:26px;color:#777;margin:0 10px 6px;word-wrap:break-word;}
.legend{margin:8px 10px;}
.legend li{background:#111;border-left:8px solid #333;padding:8px 14px;font-size:34px;margin:0 0 8px 0;}
#repl{color:#3cf;}
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
#music img{display:block;margin:8px auto;width:512px;max-width:95%;border:4px solid #333;}
/* transport bar: inline-block is CSS 2.1 and safe on Presto (no flex,
   no grid). #bar holds the transport buttons (cursor group 0, moved
   with left/right); the plain <ul> under it is group 1 (up/down).
   Buttons with no target (no previous/next track in this folder) are
   dimmed and skipped by the cursor instead of silently doing nothing. */
#bar{margin:10px 10px 0 10px;}
#bar li{display:inline-block;margin:0 10px 10px 0;padding:6px 20px;text-align:center;}
#bar li.dim{color:#666;border-left-color:#444;}
#bar li.dim a{color:#666;}
/* progress: two nested divs, inner width set as a percent on timeupdate */
#pb{margin:10px;height:16px;background:#222;border-left:8px solid #3cf;}
#pbf{height:16px;width:0;background:#3cf;}
#time{margin:0 10px;font-size:44px;color:#ccc;}
/* name of the currently selected transport button (the bar itself shows
   glyphs only — six labelled buttons would not fit the era viewport) */
#blbl{margin:0 10px 10px 10px;font-size:44px;color:#3cf;}
"""

# goBack() in one place instead of three: every template that binds LEFT or
# BACKSPACE must also DEFINE it, and an undefined goBack() is a silent
# ReferenceError that kills the whole inline script on these sets.
GOBACK_JS = """
var backUrl=%BACK%;
function goBack(){if(backUrl){window.location=backUrl;}else if(history.go){history.go(-1);}else{history.back();}}
"""

NAV_JS = """
%GOBACK%
var items=document.getElementsByTagName('li');
// start on the row the server pre-selected (the one you came back from)
var sel=%SEL0%;
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
  // Back is the remote's GREEN button, which Opera itself handles as
  // history-back and never delivers to the page (measured 2026-09-18).
  // LEFT is deliberately NOT bound to back: keyCode 37 is also the
  // remote's REW button, so binding it meant REW quit the page.
  // keyCode 8 is kept as a harmless extra on sets that send it.
  else if(k==8){goBack();}
  else{return true;}
  return false;
};
"""

PLAYER_JS = """
var v=document.getElementById('player_object');
var st=document.getElementById('status');
var hud=document.getElementById('hud');
// next/previous video in folder (page navigation, same as the music
// player) and remote multimedia-key codes from config.ini [keys]
var prevUrl=%PREV%;
var nextUrl=%NEXT%;
var KM=%KEYMAP%;
%GOBACK%
function km(a,k){var c=KM[a]||[];for(var i=0;i<c.length;i++){if(c[i]==k){return true;}}return false;}
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
  if(km('playpause',k)){if(v.paused){v.play();st.innerHTML=%hud_play%;hideshow(false);}else{v.pause();st.innerHTML=%hud_pause%;hideshow(true);}}
  else if(km('play',k)){if(v.paused){v.play();st.innerHTML=%hud_play%;hideshow(false);}}
  else if(km('pause',k)){if(!v.paused){v.pause();st.innerHTML=%hud_pause%;hideshow(true);}}
  else if(km('stop',k)){goBack();}
  else if(km('prev',k)){if(prevUrl){window.location=prevUrl;}}
  else if(km('next',k)){if(nextUrl){window.location=nextUrl;}}
  else if(km('rew',k)){try{v.currentTime-=30;}catch(x){}}
  else if(km('ff',k)){try{v.currentTime+=30;}catch(x){}}
  else if(k==13){if(v.paused){v.play();st.innerHTML=%hud_play%;hideshow(false);}else{v.pause();st.innerHTML=%hud_pause%;hideshow(true);}}
  // 37/39 are d-pad left/right AND the remote's REW/FF buttons — the set
  // sends the same code for both — so they seek, symmetrically. Back is
  // the GREEN button (handled by Opera) or the on-screen control.
  else if(k==39){try{v.currentTime+=30;}catch(x){}}
  else if(k==37){try{v.currentTime-=30;}catch(x){}}
  else if(k==8){goBack();}
  else{return true;}
  return false;
};
"""

MUSIC_JS = """
var v=document.getElementById('pv');
var st=document.getElementById('status');
var repl=document.getElementById('repl');
var prevUrl=%PREV%;
var nextUrl=%NEXT%;
%GOBACK%
// Repeat persists in a dated cookie: each track is a full page load (the
// era player cannot swap a <source> in place), so an in-page flag would
// reset on every next-track navigation. Cookies survive that, and a power
// cycle (measured on the EX725, 2026-09-18).
function ckget(n){var m=(';'+document.cookie).split('; '+n+'=');return m.length<2?'':m.pop().split(';').shift();}
function ckset(n,val){var d=new Date();d.setTime(d.getTime()+31536000000);document.cookie=n+'='+val+'; Expires='+d.toGMTString()+'; Path=/';}
var rep=(ckget('bravia_rep')=='1');
function rstate(){if(repl){repl.innerHTML=rep?%music_rep_on%:%music_rep_off%;}}
function toggleRep(){rep=!rep;ckset('bravia_rep',rep?'1':'0');rstate();}
// attach the source the era-proven way: a bare src= attribute loaded
// nothing on these sets, a <source> child with an explicit type plays
var s=document.createElement('source');
s.type=%MIME%;s.src=%URL%;
s.addEventListener('error',function(){if(st){st.innerHTML=%hud_err_src%;}});
v.appendChild(s);
v.addEventListener('error',function(e){if(st){st.innerHTML=%hud_err_code%+(e.target.error?e.target.error.code:'?');}});
// on end: repeat this track (reload restarts the /atr/ ffmpeg pipe from
// zero, more reliable than a currentTime seek against the live pipe), or
// auto-advance to the next track when there is one
v.addEventListener('ended',function(){if(rep){try{v.load();}catch(x){try{v.currentTime=0;}catch(x2){}}v.play();}else if(nextUrl){window.location=nextUrl;}});
try{v.load();v.play();v.focus();}catch(x){}
rstate();
// Keys (EX725, 2026-09-18): native controls own OK (play/pause) and the
// seek bar; we own what the native bar has no concept of. Back has three
// routes -- RETURN(8), the GREEN button (Opera handles it, never reaches
// here), and DOWN.
document.onkeydown=function(e){
  e=e||window.event;var k=e.keyCode;
  if(k==13){return true;}
  if(k==37){if(prevUrl){window.location=prevUrl;}return false;}
  if(k==39){if(nextUrl){window.location=nextUrl;}return false;}
  if(k==38){toggleRep();return false;}
  if(k==40||k==8){goBack();return false;}
  return true;
};
"""

IMG_JS = """
document.onkeydown=function(e){
  e=e||window.event;var k=e.keyCode;
  if(k==8){history.go?history.go(-1):history.back();}
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
        'nav_foot': 'Arrows navigate, OK opens, GREEN = back',
        'portal': 'Portal BRAVIA (start page)',
        'audio_player': 'Audio player',
        'video_player': 'Video player',
        'manual': 'How to use it',
        'no_items': '(no items)',
        'empty': '(empty)',
        'prev': '&lt; previous',
        'next': 'next &gt;',
        'of': 'of',
        'browse': 'Browse',
        'starting': 'starting... OK=pause, right=+30s, left=-30s, GREEN=back',
        'back_foot': 'GREEN = back',
        'error': 'Error',
        'home': 'home',
        'audio': 'Audio',
        'no_audio': 'Play (no audio track)',
        'choose_track': 'Choose the audio track',
        'conv_foot': ('OK starts conversion (first time only; '
                      'later views play instantly). GREEN = back'),
        'dolby_note': 'Dolby tracks play bit-exact (no conversion). ',
        'converting': 'Converting... %d%%',
        'converting_t': 'Converting',
        'refresh_foot': ('this page refreshes every 5s and plays '
                         'automatically when ready. GREEN = back'),
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
        'btn_prev': 'Previous track',
        'btn_next': 'Next track',
        'btn_rep': 'Repeat this track',
        'music_rep_on': 'repeat on',
        'music_rep_off': 'repeat off',
        'music_foot': 'left/right = choose, OK = act, down = Back',
        'music_start': 'playing',
        'music_live': 'live MP3 conversion',
        'music_unknown': 'unknown format',
    },
    'pt': {
        'nav_foot': 'Setas navegam, OK abre, VERDE = voltar',
        'portal': 'Portal BRAVIA (p\u00e1gina inicial)',
        'audio_player': 'Reprodutor de \u00e1udio',
        'video_player': 'Reprodutor de v\u00eddeo',
        'manual': 'Como usar',
        'no_items': '(sem itens)',
        'empty': '(vazio)',
        'prev': '&lt; anterior',
        'next': 'próximo &gt;',
        'of': 'de',
        'browse': 'Navegar',
        'starting': 'iniciando... OK=pausa, direita=+30s, esquerda=-30s, VERDE=voltar',
        'back_foot': 'VERDE = voltar',
        'error': 'Erro',
        'home': 'início',
        'audio': 'Áudio',
        'no_audio': 'Reproduzir (sem faixa de áudio)',
        'choose_track': 'Escolha a faixa de áudio',
        'conv_foot': ('OK inicia a conversão (só na primeira vez; '
                      'depois toca na hora). VERDE = voltar'),
        'dolby_note': 'Faixas Dolby tocam bit-exatas (sem conversão). ',
        'converting': 'Convertendo... %d%%',
        'converting_t': 'Convertendo',
        'refresh_foot': ('esta página atualiza a cada 5s e toca '
                         'automaticamente quando ficar pronta. VERDE = voltar'),
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
        'btn_prev': 'Faixa anterior',
        'btn_next': 'Próxima faixa',
        'btn_rep': 'Repetir esta faixa',
        'music_rep_on': 'repetir ligado',
        'music_rep_off': 'repetir desligado',
        'music_foot': 'esquerda/direita = escolher, OK = acionar, baixo = Voltar',
        'music_start': 'tocando',
        'music_live': 'conversão MP3 ao vivo',
        'music_unknown': 'formato desconhecido',
    },
    'es': {
        'nav_foot': 'Flechas navegan, OK abre, VERDE = volver',
        'portal': 'Portal BRAVIA (p\u00e1gina de inicio)',
        'audio_player': 'Reproductor de audio',
        'video_player': 'Reproductor de v\u00eddeo',
        'manual': 'C\u00f3mo usar',
        'no_items': '(sin elementos)',
        'empty': '(vacío)',
        'prev': '&lt; anterior',
        'next': 'siguiente &gt;',
        'of': 'de',
        'browse': 'Explorar',
        'starting': 'iniciando... OK=pausa, derecha=+30s, izquierda=-30s, VERDE=volver',
        'back_foot': 'VERDE = volver',
        'error': 'Error',
        'home': 'inicio',
        'audio': 'Audio',
        'no_audio': 'Reproducir (sin pista de audio)',
        'choose_track': 'Elija la pista de audio',
        'conv_foot': ('OK inicia la conversión (solo la primera vez; '
                      'luego reproduce al instante). VERDE = volver'),
        'dolby_note': 'Las pistas Dolby se reproducen bit-exactas (sin conversión). ',
        'converting': 'Convirtiendo... %d%%',
        'converting_t': 'Convirtiendo',
        'refresh_foot': ('esta página se actualiza cada 5s y reproduce '
                         'automáticamente al estar lista. VERDE = volver'),
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
        'btn_prev': 'Pista anterior',
        'btn_next': 'Pista siguiente',
        'btn_rep': 'Repetir esta pista',
        'music_rep_on': 'repetir activado',
        'music_rep_off': 'repetir desactivado',
        'music_foot': 'izquierda/derecha = elegir, OK = accionar, abajo = Volver',
        'music_start': 'reproduciendo',
        'music_live': 'conversión MP3 en vivo',
        'music_unknown': 'formato desconocido',
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
# MUSIC_JS extras (repeat toggle + prev/next-in-folder URLs); harmless
# no-ops for the video templates that lack the placeholders
MUSIC_KEYS = ('music_rep_on', 'music_rep_off')


def _resolve_js(js, back='', sel=0):
    """Fill the placeholders every template shares.

    %GOBACK% expands first because the snippet it inserts itself contains
    %BACK%. _page() calls this again as a backstop: an unresolved %SEL0%
    is not a cosmetic slip, it is a JS syntax error that silently disables
    the arrow keys on whatever page it lands in."""
    js = js.replace('%GOBACK%', GOBACK_JS)
    js = js.replace('%BACK%', json.dumps(back or ''))
    js = js.replace('%SEL0%', str(sel))
    return js


def player_js(mime, url, tpl=PLAYER_JS, prev=None, nxt=None, dur=None,
              back=None):
    js = (tpl.replace('%MIME%', repr(mime)).replace('%URL%', repr(url)))
    js = js.replace('%KEYMAP%', json.dumps(KEYMAP))
    js = js.replace('%PREV%', json.dumps(prev or ''))
    js = js.replace('%NEXT%', json.dumps(nxt or ''))
    # known length from the DIDL metadata — the live /atr/ pipe gives the
    # element no duration at all, so the progress bar needs this fallback
    js = js.replace('%DUR%', json.dumps(dur or 0))
    js = _resolve_js(js, back=back)
    for k in HUD_KEYS + MUSIC_KEYS:
        js = js.replace('%%%s%%' % k, json.dumps(T(k)))
    return js


def _latin1(s):
    """HTTP status lines encode latin-1-strict; T() strings and paths
    (Música, em dashes) crash send_error otherwise."""
    return str(s).encode('latin-1', 'replace').decode('latin-1')


def _page(title, body, extra_js=NAV_JS, extra_head=''):
    extra_js = _resolve_js(extra_js)
    return ('<!DOCTYPE html>\n<html><head><meta charset="utf-8">'
            '<title>%s</title>%s<style>%s</style></head>'
            '<body>%s<script>%s</script></body></html>'
            % (esc(title), extra_head, CSS, body, extra_js))


BRAND = 'Serviio BRAVIA 3D edition'
_HOST_LABEL = [None]


def serviio_label():
    """How the Serviio host is named on screen: its resolved hostname
    when the LAN answers a PTR lookup, the configured address otherwise.
    Resolved once and cached — a reverse lookup on every page render
    would put a DNS round-trip in front of the TV's browsing."""
    if _HOST_LABEL[0] is None:
        label = SERVIIO
        try:
            name = socket.gethostbyaddr(SERVIIO)[0]
            if name:
                label = name.split('.')[0]
        except Exception:
            pass  # no PTR record, no resolver, wrong network — show the IP
        _HOST_LABEL[0] = label
    return _HOST_LABEL[0]


def _hdr(sub=''):
    """Brand header, one definition instead of five copies."""
    return ('<h2 id="hdr">%s</h2>%s'
            % (BRAND, ('<h2>%s</h2>' % sub) if sub else ''))


def _foot(text):
    return '<p id="foot">%s</p>' % text


def render_root():
    objects, total = upnp_browse('0')
    rows = ''.join(
        '<li><a href="/b/%s">%s (%s)</a></li>'
        % (urllib.parse.quote(o['id'], safe=''), esc(o['title']),
           o.get('child_count', '?'))
        for o in objects)
    # a way back to the start page, because the remote has no Home key
    # that reaches a page and typing a URL on an IR remote is punishing
    rows += _row('dir', '/manual', T('manual'))
    if PORTAL_URL:
        rows += _row('dir', esc(PORTAL_URL), T('portal'))
    body = (_hdr('Serviio @ %s' % esc(serviio_label()))
            + '<ul>%s</ul>' % rows
            + _foot(T('nav_foot')))
    return _page('BRAVIA MediaBrowser', body)


# Row glyphs. Unicode 1.1 geometric shapes plus U+266A, old enough for era
# fonts to carry; anything newer risks tofu boxes on these sets. The point is
# scannability at couch distance — you should know what a row IS before you
# read its name.
GLYPH = {'dir': '\u25b8', 'aud': '\u266a', 'vid': '\u25b6',
         'tr': '\u25b6', 'img': '\u25a3', 'na': '\u00b7'}


def _row(kind, href, label, extra=''):
    """One list row: glyph, then the name. href='' renders an unclickable
    row (Serviio listed it but nothing can play it)."""
    inner = '%s %s%s' % (GLYPH.get(kind, GLYPH['na']), esc(label), extra)
    if not href:
        return '<li>%s</li>' % inner
    return '<li><a href="%s">%s</a></li>' % (href, inner)


def render_list(obj_id, objects, total, start, title='', sel=0):
    rows = ['<li>%s</li>' % T('no_items')] if not objects else []
    # the listing's own address, handed to each item so its player can come
    # back to this page AND this row instead of the top of the list
    pq = '%s~%d' % (urllib.parse.quote(obj_id, safe=''), start)
    for o in objects:
        qid = urllib.parse.quote(o['id'], safe='')
        if o['container']:
            rows.append(_row('dir', '/b/%s' % qid, o['title'],
                             ' (%s)' % o['child_count']))
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
                    rows.append(_row('tr', '/tr/%s?s=%d&p=%s'
                                     % (qid, len(rows), pq), o['title']))
                elif kind == 'aud':
                    # Serviio lists some audio items with NO res at all
                    # (live 2026-09-15: mpc/wv items are musicTracks with
                    # empty res — Serviio can't serve them). The /atr/
                    # lane can still resolve the source by DIDL
                    # title/duration, so keep them clickable.
                    rows.append(_row('aud', '/aud/%s?s=%d&p=%s'
                                     % (qid, len(rows), pq), o['title']))
                else:
                    rows.append(_row('na', '', o['title']))
                continue
            rows.append(_row(kind, '/%s/%s?s=%d&p=%s'
                             % (kind, qid, len(rows), pq), o['title']))
    nav = ''
    if rows:
        # restore the cursor to the row the viewer left from (?sel=), not the
        # top of the list; NAV_JS picks the same index up so the two agree
        i = sel if 0 <= sel < len(rows) else 0
        rows[i] = rows[i].replace('<li>', '<li class="sel">', 1)
    if start > 0:
        nav += ('<li><a href="/b/%s?start=%d">%s</a></li>'
                % (urllib.parse.quote(obj_id, safe=''),
                   max(0, start - PAGE_SIZE), T('prev')))
    if start + len(objects) < total:
        nav += ('<li><a href="/b/%s?start=%d">%s</a></li>'
                % (urllib.parse.quote(obj_id, safe=''),
                   start + PAGE_SIZE, T('next')))
    t_title = esc(title or T('browse'))
    body = (_hdr('%s <span style="color:#888">%d-%d %s %d</span>'
                 % (t_title, start + 1, start + len(objects), T('of'),
                    total))
            + '<ul>%s%s</ul>' % (''.join(rows), nav)
            + _foot(T('nav_foot')))
    js = _resolve_js(NAV_JS, sel=sel if 0 <= sel < len(rows) else 0)
    return _page(title or T('browse'), body, extra_js=js)


def proxied_res_url(res_url):
    """Wrap a Serviio res URL in our /stream/ proxy (same-client delivery).

    RELATIVE on purpose: this same server serves the page, so the URL
    resolves to whichever host the browser reached us on. The old
    absolute OWN_BASE=192.168.0.4 survived the d2server move and left
    every native MP3/MP4 stream URL pointing at the dead workstation —
    live 2026-09-15, MP3 items 404'd via connection-refused."""
    return '/stream/%s' % urllib.parse.quote(res_url, safe='')


def render_player(o, res, back=''):
    """Video player: full-viewport picture with the set's OWN transport.

    Presto has no JS fullscreen API, so full screen is a position:fixed
    100%x100% <video>. Adding `controls` gives the picture AND the native
    bar together (owner-confirmed on the EX725, 2026-09-18) so the old
    hand-built HUD is gone. No overlay: the picture is the whole point.
    The bar is small and cannot be enlarged -- the -o-transform scale that
    grows it for audio destroys video, whose picture rides a hardware
    plane CSS transforms do not follow. Keys: OK -> native play/pause,
    left/right -> previous/next sibling, down/RETURN/GREEN -> back."""
    title = o['title']
    prev_id, next_id = video_neighbors(o)
    prev_url = _tr_url(prev_id) if prev_id else ''
    next_url = _tr_url(next_id) if next_id else ''
    css = ('html,body{margin:0;padding:0;background:#000;overflow:hidden;}'
           '#fv{position:fixed;left:0;top:0;width:100%;height:100%;'
           'border:0;background:#000;}')
    js = ("var v=document.getElementById('fv');"
          "var s=document.createElement('source');"
          "s.type=%s;s.src=%s;v.appendChild(s);"
          % (json.dumps(res['mime']),
             json.dumps(proxied_res_url(res['url']))) +
          "try{v.load();v.play();v.focus();}catch(x){}"
          "var pu=%s,nu=%s;" % (json.dumps(prev_url), json.dumps(next_url)) +
          "document.onkeydown=function(e){var k=(e||window.event).keyCode;"
          "if(k==13){return true;}"
          "if(k==37){if(pu){window.location=pu;}return false;}"
          "if(k==39){if(nu){window.location=nu;}return false;}"
          "if(k==40||k==8){if(history.go){history.go(-1);}else{history.back();}"
          "return false;}"
          "return true;};")
    body = ('<video id="fv" controls preload="none"></video>'
            '<style>%s</style>' % css)
    # a bare page: no _page() chrome, the video owns the whole screen
    return ('<!DOCTYPE html>\n<html><head><meta charset="utf-8">'
            '<title>%s</title></head><body>%s<script>%s</script>'
            '</body></html>' % (esc(title), body, js))


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


# res mime -> library extension(s): the first rank tiebreak for dual-format
# stems (one album often exists as both FLAC and MP3). Full Serviio audio
# roster (owner-directed 2026-09-15): every format Serviio serves goes down
# the same live /atr/ MP3 pipe, so each mime needs an extension mapping.
# Values are str or tuple — endswith() takes either.
MIME_EXT = {'audio/mpeg': '.mp3', 'audio/mp3': '.mp3',
            'audio/x-flac': '.flac', 'audio/flac': '.flac',
            'audio/x-wav': '.wav', 'audio/wav': '.wav',
            'audio/mp4': '.m4a', 'audio/aac': '.aac', 'audio/aacp': '.aac',
            'audio/ogg': ('.ogg', '.oga'), 'audio/x-ogg': '.ogg',
            'audio/x-ms-wma': '.wma', 'audio/wma': '.wma',
            'audio/x-musepack': '.mpc', 'audio/x-mpc': '.mpc',
            'audio/x-wavpack': '.wv',
            'audio/x-aiff': ('.aiff', '.aif'), 'audio/aiff': '.aiff',
            'audio/x-ape': '.ape', 'audio/opus': '.opus',
            'audio/x-matroska': ('.mka', '.mks')}
# reverse: extension -> canonical mime. No-res items (mpc/wv: Serviio
# lists them with no res at all) have no DIDL mime to label the music
# page with, but the DIDL title carries the extension — derive the
# format label from it instead of showing "unknown" (owner report live
# 2026-09-15: mpc played fine, page read "formato desconhecido").
_EXT_MIME = {}
for _m, _e in MIME_EXT.items():
    for _x in (_e if isinstance(_e, tuple) else (_e,)):
        _EXT_MIME.setdefault(_x, _m)

# same for the /tr/ video lane: Serviio's video mimes -> container
# extensions, so dual-format movie stems resolve to the file the res
# mime actually describes (owner-directed 2026-09-15 — every Serviio-
# compatible video format goes through the conversion lane)
VID_MIME_EXT = {'video/mp4': ('.mp4', '.m4v'),
                'video/x-matroska': ('.mkv', '.mk3d', '.webm'),
                'video/avi': '.avi', 'video/x-msvideo': '.avi',
                'video/mpeg': ('.mpg', '.mpeg', '.vob'),
                'video/mp2t': ('.ts', '.m2ts', '.mts'),
                'video/x-ms-wmv': '.wmv', 'video/quicktime': '.mov',
                'video/x-flv': '.flv', 'video/3gpp': ('.3gp', '.3g2'),
                'video/webm': '.webm',
                'video/vnd.rn-realvideo': '.rmvb',
                # Serviio reports x-ms-asf for many .wmv files (live
                # 2026-09-15: DreamScene's Beach/Caverays/Elixir/...);
                # now that .webm is indexed, dual-format stems like
                # Aurora/Elixir NEED this hint or a duration tie can
                # hand the wmv item its webm twin's bytes.
                'video/x-ms-asf': '.wmv'}


def music_art_available(o):
    """Art ladder for the music page: Serviio's cover res first, then
    embedded extraction (Serviio 404s covers it never generated — the
    'Cover image ... cannot be found' warn). True = show <img>."""
    if pick_image_res(o['res']):
        return True
    src, _ = resolve_source(o['title'], _didl_duration_seconds(o['res']),
                             want='audio')
    return bool(src) and extract_embedded_art(src, _art_path(o['id']))


def folder_neighbors(o, cls_needle):
    """Prev/next item ids of the same kind in the same DIDL folder,
    folder order, wrapping at the ends. Serviio item ids are
    '<parent>$MI<number>': strip the tail to browse the folder.
    (None, None) when the folder can't be resolved — no $MI tail,
    browse failure, or the item isn't in it — so the page renders
    without the prev/next affordances."""
    m = re.match(r'^(.*)\$MI\d+$', o['id'])
    if not m:
        return None, None
    try:
        objs, _ = upnp_browse(m.group(1), count=1000)
    except Exception:
        return None, None
    ids = [x['id'] for x in objs
           if not x.get('container') and cls_needle in x.get('cls', '')]
    if o['id'] not in ids or len(ids) < 2:
        return None, None
    i = ids.index(o['id'])
    return ids[i - 1], ids[(i + 1) % len(ids)]


def music_neighbors(o):
    return folder_neighbors(o, 'audioItem')


def video_neighbors(o):
    return folder_neighbors(o, 'videoItem')


def _qs_int(q, name, default=0):
    """A query value the TV echoes back is not necessarily a number:
    stale bookmarks and hand-typed URLs reach here too, and int() raising
    inside the handler turns a listing into an error page."""
    try:
        return int((q.get(name) or [str(default)])[0])
    except (TypeError, ValueError):
        return default


def back_url(query):
    """The listing URL a player was opened from, cursor included.

    List rows carry ?s=<row index>&p=<quoted parent>~<page start>, so a
    player can return to the exact row instead of the top of the list.
    history.go(-1) would re-fetch the listing (pages are no-store) and land
    the cursor back on row 0, which is the small daily annoyance this fixes.
    Returns '' when the item was reached by a path that carries no origin."""
    q = parse_qs(query or '')
    p_ = (q.get('p') or [''])[0]
    if '~' not in p_:
        return ''
    parent, _, start = p_.partition('~')
    try:
        start = int(start)
    except ValueError:
        start = 0
    sel = (q.get('s') or ['0'])[0]
    sel = sel if sel.isdigit() else '0'
    # parse_qs already decoded the parent ('1%244' -> '1$4'); it has to go
    # back out quoted or Serviio object ids round-trip wrong in the path
    return '/b/%s?start=%d&sel=%s' % (
        urllib.parse.quote(parent, safe=''), start, sel)


def _tr_url(obj_id):
    return '/tr/%s' % urllib.parse.quote(obj_id, safe='')


def render_music(o, res, back=''):
    """Audio player: cover art as poster, the set's own native transport
    (scaled so it reads from a sofa), and a small legend for the track-nav
    and repeat actions the native bar has no concept of.

    Native controls do play/pause/seek/volume; our keys do previous/next
    track (left/right), repeat toggle (up, persisted in a cookie), and
    back (down / RETURN / GREEN). See docs/era-media-element.md and
    docs/era-key-vocabulary.md.

    res may be None (mpc/wv musicTracks Serviio lists with no res); the
    /atr/ pipe resolves the source by title/duration, so the page renders
    either way. Only MP3/AAC play natively, so the rest goes down the live
    transcode.
    """
    qid = urllib.parse.quote(o['id'], safe='')
    live = res is None or res['mime'] != 'audio/mpeg'
    url = ('/atr/%s' % qid) if live else proxied_res_url(res['url'])
    fmt = res['mime'] if res else _EXT_MIME.get(
        os.path.splitext(o['title'])[1].lower(), T('music_unknown'))
    label = fmt + ((', ' + T('music_live')) if live else '')
    art = ('/art/%s' % qid) if music_art_available(o) else ''
    where = where_line(o['title'], _didl_duration_seconds(o['res']), 'audio')
    prev_id, next_id = music_neighbors(o)
    xf = ('-o-transform:scale(3);-o-transform-origin:top left;'
          'transform:scale(3);transform-origin:top left;')
    poster = (' poster="%s"' % esc(art)) if art else ''
    player = _scaled_video(poster, '33%', '240px', xf, 3, 'table')
    legend = ('<ul class="legend">'
              '<li>\u25c0 / \u25b6 &nbsp; %s / %s</li>'
              '<li>\u25b2 &nbsp; %s &nbsp; <span id="repl"></span></li>'
              '<li>\u25bc &nbsp; %s</li>'
              '</ul>'
              % (esc(T('btn_prev')), esc(T('btn_next')),
                 esc(T('btn_rep')), esc(T('btn_back'))))
    # one tiny line under the title: where in the library (when the index
    # resolved it) and the format/live label. The label also carries the
    # "ao vivo" marker that tells the viewer why a transcoded track shows
    # no time on the native bar.
    meta = ((esc(where) + ' \u00b7 ') if where else '') + esc(label)
    body = ('<div id="music">'
            '<h2 id="hdr">%s - %s</h2>'
            '<p id="fmt">%s</p>'
            '<p class="loc">%s</p>'
            '%s%s'
            '<p id="status"></p>'
            '<ul><li><a href="%s">%s</a></li></ul>'
            '</div>'
            % (BRAND, T('audio_player'), esc(o['title']), meta,
               player, legend, esc(PORTAL_URL), T('portal')))
    js = player_js('audio/mpeg' if live else res['mime'], url, tpl=MUSIC_JS,
                   prev=('/aud/%s' % urllib.parse.quote(prev_id, safe=''))
                   if prev_id else None,
                   nxt=('/aud/%s' % urllib.parse.quote(next_id, safe=''))
                   if next_id else None,
                   back=back)
    return _page(o['title'], body, extra_js=js)


def render_local_player(name, mime, url, prev=None, nxt=None, back=''):
    body = ('<div id="player_page">'
            '<video id="player_object" width="0px" height="0px" preload="none"></video>'
            '<p class="hud" id="hud"><span id="ttl">%s</span> &mdash; '
            '<span id="fmt">%s</span> &mdash; '
            '<span id="status">%s</span></p>'
            '</div>'
            % (esc(name), esc(mime), T('starting')))
    js = player_js(mime, url, prev=prev, nxt=nxt, back=back)
    return _page(name, body, extra_js=js)


KEYS_JS = """
var st=document.getElementById('status');
var seen=[];
document.onkeydown=function(e){
  e=e||window.event;var k=e.keyCode;
  // show the code on screen AND beacon it server-side (a plain Image
  // fetch is the era-Presto-safe channel; the server logs KEYPROBE)
  seen[seen.length]=k;
  st.innerHTML=seen.join(', ');
  var i=new Image();
  i.src='/keylog/'+k+'?n='+seen.length;
  return false;
};
"""


# ---------------------------------------------------- /probe (era facts)

# Candidate glyphs, each with an ASCII name the owner can read back to us
# off the screen. U+21BA is in here as the known-bad control: it is the
# repeat button that rendered as a box on the EX725 (2026-09-17), which is
# how we learned the "Unicode 1.1 is safe" rule had an exception the code
# comment claimed it did not.
PROBE_GLYPHS = [
    ('U+25B6 play',        '\u25b6', '1.1'),
    ('U+25C0 left',        '\u25c0', '1.1'),
    ('U+25AE bar (pause)', '\u25ae', '1.1'),
    ('U+25A0 square',      '\u25a0', '1.1'),
    ('U+266A note',        '\u266a', '1.1'),
    ('U+221E infinity',    '\u221e', '1.1'),
    ('U+2195 updown',      '\u2195', '1.1'),
    ('U+2194 leftright',   '\u2194', '1.1'),
    ('U+21B5 return',      '\u21b5', '1.1'),
    ('U+00AB guillemet',   '\u00ab', 'Latin-1'),
    ('U+00BB guillemet',   '\u00bb', 'Latin-1'),
    ('U+21BA loop BAD?',   '\u21ba', '3.2'),
    ('U+21BB loop',        '\u21bb', '3.2'),
    ('U+23EE prev',        '\u23ee', '4.0'),
]


def probe_track():
    """An audio URL for the controls probe: first item of Random Music.

    Returns (url, mime, title) or (None, None, None). The probe must not
    be the reason a page 500s, so every failure here is silent."""
    try:
        objects, _ = upnp_browse('A_R', count=4)
        for o in objects:
            if o['container']:
                continue
            r = pick_audio_res(o['res'])
            live = r is None or r['mime'] != 'audio/mpeg'
            qid = urllib.parse.quote(o['id'], safe='')
            url = ('/atr/%s' % qid) if live else proxied_res_url(r['url'])
            return url, ('audio/mpeg' if live else r['mime']), o['title']
    except Exception:
        pass
    return None, None, None


# ---------------------------------------------------------------- /manual
#
# Everything here is measured on a KDL-46EX725 (AZ2-F), 2026-09-18, not
# copied from a spec. See docs/era-key-vocabulary.md and
# docs/era-media-element.md for how each line was established.
MANUAL = {
    'en': [
        ('Browser settings', [
            'Font size must be Medium. Every size on these pages was chosen against that setting, and Large or Small will push text off the screen or shrink it below couch-reading distance.',
            "The browser is the TV's own. Closing it or changing input ends the session, which is why anything worth remembering is stored in a dated cookie rather than for the session.",
        ]),
        ('Navigating', [
            'Up / Down move the cursor. OK opens.',
            'GREEN goes back. Opera handles that key itself, so it always '
            'works, even where the page has no Back row.',
            'YELLOW goes forward again.',
            'Left / Right walk the buttons on a player.',
        ]),
        ('The remote', [
            'PLAY, PAUSE, STOP, PREV and NEXT send nothing at all on this '
            'generation. They are not mapped wrong, the browser never sees '
            'them. Use the on-screen controls instead.',
            'REW and FF send the same codes as Left and Right, so the app '
            'cannot tell them apart.',
            'RED jumps to the bottom of the page, BLUE to the top. All four '
            'colour keys belong to the browser, not to the app.',
        ]),
        ('In the player', [
            'The TV draws its own transport bar: play, pause, seek and '
            'volume. It fades out, press OK to bring it back.',
            'Elapsed time appears for files that play directly (MP3, AAC, '
            'MP4). Lossless files are converted as they play and have no '
            'known length, so that bar shows no time for them.',
        ]),
        ('Formats', [
            'Plays directly: MP3, AAC, MP4 audio and video.',
            'Converted live: FLAC, OGG, WAV and anything else. Nothing is '
            'written to disk.',
            'The set cannot play WebM or Matroska at all.',
        ]),
    ],
    'pt': [
        ('Ajustes do navegador', [
            'O tamanho da fonte precisa estar em Médio. Todos os tamanhos destas páginas foram escolhidos para esse ajuste, e Grande ou Pequeno jogam o texto para fora da tela ou deixam ilegível de longe.',
            'O navegador é o da própria TV. Fechá-lo ou trocar de entrada encerra a sessão, por isso o que vale a pena lembrar fica em cookie com data, não em cookie de sessão.',
        ]),
        ('Navegar', [
            'Cima / Baixo movem o cursor. OK abre.',
            'VERDE volta. Essa tecla é tratada pelo próprio Opera, então '
            'funciona sempre, mesmo onde a página não tem linha Voltar.',
            'AMARELO avança de novo.',
            'Esquerda / Direita andam pelos botões do reprodutor.',
        ]),
        ('O controle remoto', [
            'PLAY, PAUSE, STOP, ANTERIOR e PRÓXIMA não enviam nada nesta '
            'geração. Não estão mapeadas errado, o navegador simplesmente '
            'não as recebe. Use os controles na tela.',
            'REW e FF enviam os mesmos códigos que Esquerda e Direita, '
            'então o aplicativo não consegue distinguir.',
            'VERMELHO vai para o fim da página, AZUL para o topo. As quatro '
            'teclas coloridas são do navegador, não do aplicativo.',
        ]),
        ('No reprodutor', [
            'A TV desenha a própria barra: reproduzir, pausar, avançar e '
            'volume. Ela some sozinha, aperte OK para trazer de volta.',
            'O tempo aparece nos arquivos que tocam direto (MP3, AAC, '
            'MP4). Os arquivos sem perdas são convertidos enquanto tocam e '
            'não têm duração conhecida, então a barra não mostra tempo '
            'para eles.',
        ]),
        ('Formatos', [
            'Tocam direto: MP3, AAC, áudio e vídeo MP4.',
            'Convertidos ao vivo: FLAC, OGG, WAV e o resto. Nada é gravado '
            'em disco.',
            'O aparelho não toca WebM nem Matroska de jeito nenhum.',
        ]),
    ],
    'es': [
        ('Ajustes del navegador', [
            'El tamaño de fuente debe estar en Medio. Todos los tamaños de estas páginas se eligieron para ese ajuste, y Grande o Pequeño sacan el texto de la pantalla o lo vuelven ilegible de lejos.',
            'El navegador es el del propio televisor. Cerrarlo o cambiar de entrada termina la sesión, por eso lo que vale la pena recordar se guarda en una cookie con fecha.',
        ]),
        ('Navegar', [
            'Arriba / Abajo mueven el cursor. OK abre.',
            'VERDE vuelve. Esa tecla la maneja el propio Opera, así que '
            'siempre funciona, incluso donde la página no tiene fila Volver.',
            'AMARILLO avanza de nuevo.',
            'Izquierda / Derecha recorren los botones del reproductor.',
        ]),
        ('El mando', [
            'PLAY, PAUSE, STOP, ANTERIOR y SIGUIENTE no envían nada en esta '
            'generación. No están mal asignadas, el navegador nunca las '
            'recibe. Use los controles en pantalla.',
            'REW y FF envían los mismos códigos que Izquierda y Derecha, '
            'así que la aplicación no puede distinguirlos.',
            'ROJO salta al final de la página, AZUL al inicio. Las cuatro '
            'teclas de color son del navegador, no de la aplicación.',
        ]),
        ('En el reproductor', [
            'El televisor dibuja su propia barra: reproducir, pausar, '
            'avanzar y volumen. Se oculta sola, pulse OK para recuperarla.',
            'El tiempo aparece en los archivos que se reproducen directo '
            '(MP3, AAC, MP4). Los archivos sin pérdida se convierten '
            'mientras suenan y no tienen duración conocida, así que esa '
            'barra no muestra tiempo para ellos.',
        ]),
        ('Formatos', [
            'Se reproducen directo: MP3, AAC, audio y vídeo MP4.',
            'Convertidos en vivo: FLAC, OGG, WAV y el resto. Nada se '
            'escribe en disco.',
            'El equipo no reproduce WebM ni Matroska en absoluto.',
        ]),
    ],
}


def render_manual():
    """/manual — how to drive this thing, from the sofa.

    Every statement here was measured on the panel rather than taken from
    a specification, because on this generation the specification and the
    hardware disagree often enough that only the hardware counts."""
    lang = getattr(_UI, 'lang', None)
    sections = MANUAL.get(lang if lang in MANUAL else 'en', MANUAL['en'])
    out = []
    for heading, items in sections:
        out.append('<h2>%s</h2><ul>%s</ul>'
                   % (esc(heading),
                      ''.join('<li>%s</li>' % esc(i) for i in items)))
    body = ('<h2 id="hdr">%s - %s</h2>' % (BRAND, T('manual'))
            + ''.join(out)
            + '<ul><li><a href="/">%s</a></li>'
              '<li><a href="%s">%s</a></li></ul>'
            % (T('browse'), esc(PORTAL_URL), T('portal')))
    return _page(T('manual'), body)


def render_probe():
    """/probe — index of the era probes that need eyes on the panel."""
    rows = ''.join('<li><a href="%s">%s</a></li>' % (h, t) for h, t in [
        ('/probe/glyphs', 'A \u2014 glyph coverage (which are boxes?)'),
        ('/probe/ctl?v=1', 'B \u2014 native controls, 1px element (today\u0027s shape)'),
        ('/probe/ctl?v=2', 'C \u2014 native controls, 640x360 element'),
        ('/probe/ctl?v=3', 'D \u2014 native controls, 640x360, no key handler'),
        ('/probe/ctl?v=4', 'E \u2014 native controls, full width, no key handler'),
        ('/keys', 'F \u2014 remote keycode probe (done 2026-09-18)'),
        ('/probe/caps', 'G \u2014 what this player supports'),
        ('/probe/art?v=1', 'H \u2014 album art 960x540'),
        ('/probe/art?v=2', 'I \u2014 art + transform scale x2'),
        ('/probe/art?v=3', 'J \u2014 art + zoom 2'),
        ('/probe/art?v=4', 'K \u2014 art full width'),
        ('/probe/art?v=5', 'L \u2014 art + scale x2, wrapped'),
        ('/probe/art?v=6', 'M \u2014 art + scale x3, wrapped'),
        ('/probe/art?v=7', 'O \u2014 candidate: x3, no chrome'),
        ('/probe/art?v=8', 'P \u2014 x3, wrapper no clip (audio?)'),
        ('/probe/art?v=9', 'Q \u2014 x3, no wrapper, spacer (audio?)'),
        ('/probe/art?v=10', 'R \u2014 candidato: 33%% x3, tabela'),
        ('/probe/art?v=11', 'S \u2014 candidato: v\u00eddeo, mesmo layout'),
        ('/probe/art?v=12', 'T \u2014 v\u00eddeo SEM escala (volta a imagem?)'),
        ('/probe/art?v=13', 'U \u2014 v\u00eddeo tela cheia + controles nativos'),
        ('/probe/cookie', 'N \u2014 cookies: do they persist?'),
    ])
    body = (_hdr('Era probes')
            + '<ul>%s</ul>' % rows
            + _foot('Report what you see; nothing here changes the player.'))
    return _page('Probes', body)


def probe_art_url():
    """Album art for a track that has some, for the poster probes."""
    try:
        objects, _ = upnp_browse('A_R', count=8)
        for o in objects:
            if not o['container'] and music_art_available(o):
                return '/art/%s' % urllib.parse.quote(o['id'], safe='')
    except Exception:
        pass
    return ''


def read_cookies(header):
    """Parse a Cookie: header into a dict. Era browsers send the plain
    name=value; form, so nothing fancier is needed."""
    out = {}
    for part in (header or '').split(';'):
        name, _, value = part.strip().partition('=')
        if name:
            out[name] = urllib.parse.unquote(value)
    return out


def bake(name, value, days=365, path='/'):
    """A Set-Cookie value with an explicit expiry.

    Session cookies would die with the browser, and on a TV the browser
    closes whenever the set changes input. Anything worth remembering
    needs a real Expires."""
    when = time.strftime('%a, %d %b %Y %H:%M:%S GMT',
                         time.gmtime(time.time() + days * 86400))
    return '%s=%s; Expires=%s; Path=%s' % (
        name, urllib.parse.quote(str(value), safe=''), when, path)


def render_probe_cookie(cookie_header):
    """/probe/cookie — do cookies survive a navigation, and a power cycle?

    Three separate questions, because they fail independently: does the
    browser return a Set-Cookie on the next request, can script read and
    write document.cookie, and does an Expires-dated cookie outlive the
    browser being closed (which on a TV happens on every input change)."""
    jar = read_cookies(cookie_header)
    visits = 0
    try:
        visits = int(jar.get('bravia_visits', '0'))
    except ValueError:
        visits = 0
    visits += 1
    rows = ''.join('<li>%s = <b>%s</b></li>' % (esc(k), esc(v))
                   for k, v in sorted(jar.items())) or '<li>(none sent)</li>'
    body = (_hdr('N \u2014 cookies')
            + '<p id="fmt">server saw <b>%d</b> cookie(s) on this request; '
              'visit counter is now <b>%d</b></p>' % (len(jar), visits)
            + '<p id="fmt">cookies the browser sent us:</p>'
            + '<ul style="font-size:32px;">%s</ul>' % rows
            + '<p id="fmt">document.cookie says:</p>'
            + '<p id="js" style="color:#3cf;font-size:32px;'
              'word-wrap:break-word;">(reading)</p>'
            + '<ul><li><a href="/probe/cookie">reload \u2014 the counter '
              'should go up by one</a></li>'
            + '<li><a href="/probe">back to probes</a></li></ul>'
            + _foot('If the counter survives turning the TV off and on, '
                    'cookies are durable storage here.'))
    js = ("var j=document.getElementById('js');"
          "try{document.cookie='bravia_js=written; Path=/';"
          "j.innerHTML=document.cookie||'(empty)';}"
          "catch(e){j.innerHTML='document.cookie THREW: '+e;}")
    return (_page('Cookies', body, extra_js=js),
            [bake('bravia_visits', visits)])


def where_line(title, didl_dur, want):
    """A small "where in the library is this" line.

    The DIDL title alone does not say which album, which disc, or which
    of two copies is playing. The duration index already maps a title to
    its file, so the relative path answers all three and costs nothing we
    are not computing anyway for the transcode lanes. Falls back to empty
    when the library is unindexed or the file cannot be resolved."""
    try:
        path, _err = resolve_source(title, didl_dur, want=want)
    except Exception:
        return ''
    if not path:
        return ''
    for root in MEDIA_ROOTS:
        if path.startswith(root):
            return path[len(root):].lstrip('/') or path
    return path


def probe_video():
    """A directly playable video for the probe: video/mp4 only.

    The era player refuses Serviio's live transcode targets, so anything
    that is not already progressive MP4 is no use as a probe subject."""
    for container in ('V_T', 'V_M'):
        try:
            objects, _ = upnp_browse(container, count=18)
        except Exception:
            continue
        for o in objects:
            if o['container']:
                continue
            r = pick_video_res(o['res'])
            if r and r.get('mime') == 'video/mp4':
                return proxied_res_url(r['url']), r['mime'], o['title']
    return None, None, None


def render_probe_caps():
    """/probe/caps -- what does this set's media element actually support?

    Every answer is read off the live object on the panel rather than
    inferred from the browser version, and written into the page so it can
    be read from the couch and reported back."""
    url, mime, _title = probe_track()
    if not url:
        return render_error('probe', 'no audio item found to test with')
    js = (
        "var v=document.getElementById('pv');"
        "var out=document.getElementById('out');"
        "var fired=document.getElementById('fired');"
        "var seen='';"
        "var s=document.createElement('source');"
        "s.type=%s;s.src=%s;v.appendChild(s);"
        % (json.dumps(mime), json.dumps(url)) +
        "function row(k,val){out.innerHTML+='<li>'+k+' = <b>'+val+'</b></li>';}"
        "function has(o,k){try{return (typeof o[k]!='undefined')?'yes':'no';}"
        "catch(e){return 'throws';}}"
        "var props=['controls','volume','muted','playbackRate','duration',"
        "'currentTime','paused','readyState','networkState','preload',"
        "'poster','seekable','buffered','loop','autoplay','videoWidth'];"
        "for(var i=0;i<props.length;i++){row(props[i],has(v,props[i]));}"
        "row('controls value',v.controls);"
        "row('volume value',v.volume);"
        "var mimes=['audio/mpeg','audio/mp4','audio/aac','audio/flac',"
        "'audio/ogg','audio/wav','video/mp4','video/webm','video/x-matroska'];"
        "for(var j=0;j<mimes.length;j++){var r='n/a';"
        "try{r=v.canPlayType(mimes[j])||'(empty)';}catch(e){r='throws';}"
        "row('canPlayType '+mimes[j],r);}"
        "var stl=v.style;"
        "var css=['transform','OTransform','WebkitTransform','zoom'];"
        "for(var c=0;c<css.length;c++){row('style.'+css[c],has(stl,css[c]));}"
        "var fs=['requestFullscreen','webkitRequestFullScreen',"
        "'oRequestFullscreen'];"
        "for(var f=0;f<fs.length;f++){row(fs[f],has(v,fs[f]));}"
        "var evs=['loadstart','durationchange','loadedmetadata','loadeddata',"
        "'progress','canplay','canplaythrough','play','playing','pause',"
        "'timeupdate','ended','volumechange','ratechange','seeking','seeked',"
        "'error','stalled','suspend','waiting'];"
        "function mk(n){return function(){if(seen.indexOf('['+n+']')<0){"
        "seen+='['+n+']';fired.innerHTML=seen;}};}"
        "for(var e=0;e<evs.length;e++){"
        "try{v.addEventListener(evs[e],mk(evs[e]),false);}catch(x){}}"
        "try{v.play();}catch(x){}"
    )
    body = (_hdr('G - player capabilities')
            + '<p id="fmt">%s</p>' % esc(mime)
            + '<video id="pv" controls preload="none" width="480" '
              'height="270" style="width:480px;height:270px;'
              'background:#111;"></video>'
            + '<p id="fmt">events that fired:</p>'
            + '<p id="fired" style="color:#3cf;font-size:30px;'
              'word-wrap:break-word;">(none yet)</p>'
            + '<ul id="out" style="font-size:30px;"></ul>'
            + _foot('<a href="/probe">back to probes</a>'))
    return _page('Capabilities', body, extra_js=js)


def _scaled_video(poster, w, h, extra, factor, mode='clip'):
    """A <video> that may be CSS-scaled, plus room for the scaled pixels.

    A transform takes no part in layout: the element keeps its pre-scale
    footprint, so whatever follows renders underneath it (EX725,
    2026-09-18). Reserving the final size is therefore necessary — but
    HOW it is reserved is not free. Wrapping the element in a sized,
    clipped <div> killed audio on the panel (variants 5 and 6 both went
    silent while the unwrapped scaled element played), which is the same
    class of quirk as the standing rules about <audio> and display:none:
    this engine cares where the media element sits.

      clip   — sized wrapper with overflow:hidden  (SILENT on the EX725)
      wrap   — sized wrapper, no overflow property  (plays)
      spacer — no wrapper; a sibling <div> reserves the height, leaving
               the <video> a direct child           (plays)

    Measured 2026-09-18: 'wrap' and 'spacer' both play, 'clip' does not.
    So a parent element is fine and **overflow:hidden is what silences
    the audio** — a clipped ancestor evidently takes this engine down a
    path where the decoder never starts. Never clip an ancestor of the
    media element.
    """
    vid = ('<video id="pv" controls preload="none"%s width="%s" '
           'height="%s" style="width:%s;height:%s;background:#111;%s">'
           '</video>' % (poster, w, h, w, h, extra))
    if factor <= 1:
        return vid
    try:
        ph = int(h.replace('px', ''))
        pw = int(w.replace('px', '')) if w.endswith('px') else 0
    except ValueError:
        return vid
    fw, fh = pw * factor, ph * factor
    if mode == 'table':
        # A table with width="100%" is the most reliable layout primitive
        # this browser has, and percentages mean the player follows the
        # screen instead of assuming 1920 wide. The cell reserves the
        # scaled height; nothing is clipped.
        return ('<table width="100%%" border="0" cellpadding="0" '
                'cellspacing="0"><tr><td height="%d" valign="top">%s'
                '</td></tr></table>' % (ph * factor, vid))
    if mode == 'spacer':
        # the element keeps its own footprint (pw x ph); the spacer adds
        # only the DIFFERENCE, so the total reserved height is fh
        return ('%s<div style="width:%s;height:%dpx;"></div>'
                % (vid, ('%dpx' % fw) if pw else '100%%', fh - ph))
    overflow = 'overflow:hidden;' if mode == 'clip' else ''
    return ('<div style="width:%dpx;height:%dpx;%s">%s</div>'
            % (fw, fh, overflow, vid))


def render_probe_fullvideo():
    """/probe/art?v=13 — full-viewport video WITH native controls.

    The working video player fills the viewport with a position:fixed
    100%x100% element (Presto has no JS fullscreen API) but draws a custom
    HUD. This asks the obvious follow-up now that native controls are
    known to work for audio: does a full-screen video element also get the
    set's own transport bar? If yes, the video player can drop its custom
    HUD for the native one, same as the audio surface."""
    url, mime, title = probe_video()
    if not url:
        return render_error('probe', 'no direct-play MP4 found to test with')
    css = ('html,body{margin:0;padding:0;background:#000;overflow:hidden;}'
           '#fv{position:fixed;left:0;top:0;width:100%;height:100%;'
           'border:0;background:#000;}')
    js = ("var v=document.getElementById('fv');"
          "var s=document.createElement('source');"
          "s.type=%s;s.src=%s;v.appendChild(s);"
          % (json.dumps(mime), json.dumps(url)) +
          "try{v.play();}catch(x){}"
          "document.onkeydown=function(e){var k=(e||window.event).keyCode;"
          # green is history-back; keep 8 as an extra exit
          "if(k==8){window.location='/probe';return false;}return true;};")
    # no overlay text: the owner confirmed the picture should be clean
    # (2026-09-18). The native bar is the only chrome; GREEN exits.
    body = '<video id="fv" controls preload="none"></video>'
    return ('<!DOCTYPE html>\n<html><head><meta charset="utf-8">'
            '<title>Full video</title><style>%s</style></head>'
            '<body>%s<script>%s</script></body></html>'
            % (css, body, js))


def render_probe_art(variant):
    """/probe/art -- album art behind native controls, and can we enlarge them?

    Audio in a <video> element leaves the frame empty, so the poster is the
    natural place for Serviio's cover art. Variants 2 and 3 try to scale the
    element up, because the native bar renders at a fixed height and is
    unreadable at couch distance otherwise."""
    if variant in (11, 12):
        url, mime, title = probe_video()
        art = ''
        if not url:
            return render_error('probe', 'no direct-play MP4 found to test '
                                         'with (Serviio lists none)')
    else:
        url, mime, title = probe_track()
        art = probe_art_url()
        if not url:
            return render_error('probe', 'no audio item found to test with')
    # Measured on the EX725, 2026-09-18:
    #   * the native control bar has a FIXED pixel height. Growing the
    #     element widens the bar but never makes it taller (1 and 4).
    #   * zoom: has no effect — the element stayed 480x270 (3), even
    #     though style.zoom exists on the object.
    #   * -o-transform:scale() DOES scale the element and its native
    #     controls (2), but a transform takes no part in layout, so the
    #     text below rendered underneath it. Reserving the final size
    #     with a sized container is the fix, which is what 5 and 6 do.
    styles = {
        1: ('960px', '540px', '', 1),
        2: ('480px', '270px',
            '-o-transform:scale(2);-o-transform-origin:top left;'
            'transform:scale(2);transform-origin:top left;', 1),
        3: ('480px', '270px', 'zoom:2;', 1),
        4: ('100%', '600px', '', 1),
        5: ('480px', '270px',
            '-o-transform:scale(2);-o-transform-origin:top left;'
            'transform:scale(2);transform-origin:top left;', 2),
        6: ('440px', '248px',
            '-o-transform:scale(3);-o-transform-origin:top left;'
            'transform:scale(3);transform-origin:top left;', 3),
        # 7 is the production candidate: scale x3 like 6, but with the
        # explanatory chrome removed. On the panel 6 scrolled vertically
        # and the cause was the text above the player, not the player.
        7: ('420px', '236px',
            '-o-transform:scale(3);-o-transform-origin:top left;'
            'transform:scale(3);transform-origin:top left;', 3),
        8: ('440px', '248px',
            '-o-transform:scale(3);-o-transform-origin:top left;'
            'transform:scale(3);transform-origin:top left;', 3),
        9: ('440px', '248px',
            '-o-transform:scale(3);-o-transform-origin:top left;'
            'transform:scale(3);transform-origin:top left;', 3),
        # 10 sizes by percentage so it follows the screen instead of
        # assuming 1920 wide: 33% scaled x3 fills ~99% of the viewport.
        10: ('33%', '240px',
             '-o-transform:scale(3);-o-transform-origin:top left;'
             'transform:scale(3);transform-origin:top left;', 3),
        # 11 is the same surface for video. No poster: the frames are the
        # picture, so the art slot is the video itself.
        11: ('33%', '240px',
             '-o-transform:scale(3);-o-transform-origin:top left;'
             'transform:scale(3);transform-origin:top left;', 3),
        # 12 is variant 11 with NO transform. On the panel 11 played the
        # audio of an MP4 but showed no picture, and the transform is the
        # obvious suspect: video on these sets goes to a hardware plane
        # that CSS may not follow. If 12 shows the picture, scaling is
        # simply unavailable for video and that surface must be sized
        # rather than scaled.
        12: ('99%', '600px', '', 1),
    }
    w, h, extra, factor = styles.get(variant, styles[1])
    # 5/6/7 clip, 8 wraps without clipping, 9 uses a sibling spacer
    mode = {8: 'wrap', 9: 'spacer', 10: 'table', 11: 'table',
            12: 'table'}.get(variant, 'clip')
    poster = (' poster="%s"' % esc(art)) if art else ''
    what = {1: '960x540, poster only',
            2: '480x270 scaled x2 via transform',
            3: '480x270 with zoom:2',
            4: 'full width, 600px tall',
            5: '480x270 scaled x2, wrapped at 960x540',
            6: '440x248 scaled x3, wrapped at 1320x744',
            7: 'production candidate: x3, no chrome',
            8: 'x3, wrapper WITHOUT overflow:hidden',
            9: 'x3, NO wrapper - sibling spacer',
            10: 'candidate: 33%% width x3, table, no clip',
            11: 'candidate: same, video',
            12: 'video, NO transform (does the picture come back?)'
            }.get(variant, '')
    js = ("var v=document.getElementById('pv');"
          "var st=document.getElementById('status');"
          "var s=document.createElement('source');"
          "s.type=%s;s.src=%s;v.appendChild(s);"
          % (json.dumps(mime), json.dumps(url)) +
          "function say(t){st.innerHTML=t;}"
          "var hits='';"
          "function mark(n){if(hits.indexOf(n)<0){hits+=n+' ';}}"
          # 'loading' stayed on screen while audio played (EX725,
          # 2026-09-18), so loadstart/canplay/playing do NOT fire here.
          # timeupdate is the one event this platform is proven to send,
          # so the clock is driven from it and the others are only noted.
          "v.addEventListener('timeupdate',function(){mark('timeupdate');"
          "say('t='+Math.round(v.currentTime||0)+'s  paused='+v.paused"
          "+'  ['+hits+']');});"
          "v.addEventListener('loadstart',function(){mark('loadstart');});"
          "v.addEventListener('canplay',function(){mark('canplay');});"
          "v.addEventListener('playing',function(){mark('playing');});"
          "v.addEventListener('play',function(){mark('play');});"
          "v.addEventListener('pause',function(){mark('pause');});"
          "v.addEventListener('durationchange',function(){"
          "mark('durationchange');});"
          "v.addEventListener('stalled',function(){say('STALLED');});"
          "v.addEventListener('error',function(e){say('ERROR code '"
          "+((e.target&&e.target.error)?e.target.error.code:'?'));});"
          "s.addEventListener('error',function(){say('SOURCE rejected');});"
          "try{v.play();}catch(x){say('play() threw: '+x);}")
    if variant in (10, 11, 12):
        # The owner's layout, 2026-09-18: brand line with the surface
        # named, the file that is playing, the player, and a shortcut
        # home. No status text — the native bar shows its own time, and a
        # 'loading' line that never clears (loadstart/canplay/playing do
        # not fire here) is worse than no line at all.
        video = variant in (11, 12)
        surface = T('video_player') if video else T('audio_player')
        where = where_line(title, 0, 'video' if video else 'audio')
        body = ('<h2 id="hdr">%s - %s</h2>' % (BRAND, surface)
                + '<p id="fmt">%s</p>' % esc(title or '')
                + ('<p style="font-size:26px;color:#777;margin:0 10px 6px;'
                   'word-wrap:break-word;">%s</p>' % esc(where)
                   if where else '')
                + _scaled_video(poster, w, h, extra, factor, mode)
                + '<ul><li><a href="%s">%s</a></li></ul>'
                % (esc(PORTAL_URL), T('portal')))
    elif variant == 7:
        # nothing above the player: the scroll bar on variant 6 came from
        # the chrome, so the candidate layout simply has none
        body = (_scaled_video(poster, w, h, extra, factor, mode)
                + '<p id="status" style="font-size:34px;">loading</p>')
    else:
        body = (_hdr('Art %d - %s' % (variant, what))
                + '<p id="fmt">%s%s</p>' % (esc(title or ''),
                                            '' if art else ' (no art found)')
                + _scaled_video(poster, w, h, extra, factor, mode)
                + '<p id="status">loading</p>'
                + '<p id="fmt">Watch for: art visible while playing, and '
                  'whether the control bar got bigger.</p>'
                + _foot('<a href="/probe">back to probes</a>'))
    return _page('Art probe %d' % variant, body, extra_js=js)


def render_probe_glyphs():
    """Which codepoints does this panel's font actually carry?

    Each row prints the glyph big, then its ASCII name, so a box can be
    reported precisely instead of as "the third one"."""
    rows = ''.join(
        '<li>%s &nbsp; <span style="font-size:28px;color:#888">%s (%s)</span></li>'
        % (g, esc(name), era) for name, g, era in PROBE_GLYPHS)
    body = (_hdr('A \u2014 glyph coverage')
            + '<p id="fmt">Every row should show a symbol before its name. '
              'Tell me which rows show an empty box instead.</p>'
            + '<ul>%s</ul>' % rows
            + _foot('<a href="/probe">back to probes</a>'))
    return _page('Glyphs', body)


def render_probe_ctl(variant):
    """Does this browser draw native transport chrome for AUDIO?

    The video page gets the set\u0027s own fading play/pause and progress bar,
    so the chrome exists on this platform. The open question is whether an
    audio source in a *visibly sized* element gets it too, and whether the
    remote can reach it. Variants 3 and 4 install no onkeydown handler at
    all, because ours returns false and that may be what stops the browser
    doing its own focus handling."""
    url, mime, title = probe_track()
    if not url:
        return render_error('probe', 'no audio item found to test with')
    sizes = {1: ('1px', '1px'), 2: ('640px', '360px'),
             3: ('640px', '360px'), 4: ('100%', '480px')}
    w, h = sizes.get(variant, sizes[2])
    keys = variant in (1, 2)
    vid = ('<video id="pv" controls preload="none" '
           'width="%s" height="%s" style="width:%s;height:%s;'
           'background:#111;"></video>' % (w, h, w, h))
    note = ('Arrow keys are handled by the page (like the real player).'
            if keys else
            'No key handler on this page: the browser keeps the arrows, so '
            'the remote may be able to focus the native controls.')
    # the bare src= attribute loaded nothing on the EX725 (2026-09-18);
    # the era-proven attach is a <source> child carrying an explicit type,
    # exactly as MUSIC_JS does it
    js = ("var v=document.getElementById('pv');"
          "var st=document.getElementById('status');"
          "var s=document.createElement('source');"
          "s.type=%s;s.src=%s;v.appendChild(s);"
          % (json.dumps(mime), json.dumps(url))
          + "function say(t){if(st){st.innerHTML=t;}}"
          "v.addEventListener('loadedmetadata',function(){say('metadata ok');});"
          "v.addEventListener('playing',function(){say('playing');});"
          "v.addEventListener('play',function(){say('play event FIRED');});"
          "v.addEventListener('pause',function(){say('pause event FIRED');});"
          "v.addEventListener('error',function(){say('error');});"
          "try{v.play();}catch(x){}")
    if keys:
        js += ("document.onkeydown=function(e){var k=(e||window.event).keyCode;"
               "if(k==13){if(v.paused){v.play();}else{v.pause();}return false;}"
               "if(k==8){window.location='/probe';return false;}"
               "return true;};")
    body = (_hdr('Variant %d \u2014 native controls' % variant)
            + '<p id="fmt">%s &nbsp; %s x %s</p>' % (esc(mime), w, h)
            + vid
            + '<p id="status">loading</p>'
            + '<p id="fmt">%s</p>' % note
            + '<p id="fmt">Watch for: (1) does a transport bar appear over '
              'the element, (2) can the remote move onto it, (3) do the '
              'play/pause EVENTS fire above.</p>'
            + _foot('<a href="/probe">back to probes</a>'))
    return _page('Controls probe %d' % variant, body, extra_js=js)


def render_keys():
    """/keys — remote multimedia-key probe. Every keydown shows its
    keyCode on the TV and is logged server-side as
    'KEYPROBE <client> code=<n>' (server.log). Press the remote's play,
    pause, stop, previous, next, rewind and fast-forward buttons, read
    the codes off the screen or the log, paste them into config.ini
    [keys], restart the app — the player pages honor them."""
    body = ('<div id="music">'
            '<h2 id="hdr">Remote key probe</h2>'
            '<p id="fmt">press every media button on the remote</p>'
            '<p id="status">(press keys)</p>'
            '<p id="foot">codes on screen + KEYPROBE lines in server.log; '
            'GREEN = back</p>'
            '</div>')
    return _page('key probe', body, extra_js=KEYS_JS)


def render_error(where, err):
    body = (_hdr(T('error'))
            + '<p id="status">%s</p>' % esc('%s: %s' % (where, err))
            + _foot('<a href="/">%s</a>' % T('home')))
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
    body = (_hdr('%s <span style="color:#888">%s</span>'
                 % (esc(o['title']), esc(vlabel)))
            + '<h2>%s</h2><ul>%s</ul>' % (T('choose_track'), ''.join(rows))
            + _foot(foot))
    return _page(o['title'], body)


def render_progress(title, pct, note):
    head = '<meta http-equiv="refresh" content="5">'
    body = (_hdr(esc(title))
            + '<h2 id="status">%s</h2>' % (T('converting') % int(pct))
            + _foot('%s - %s' % (esc(note), T('refresh_foot'))))
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

def _pick_local(*cands):
    """First existing dir — lets the same file run on d2server (media is
    LOCAL there: /mnt/arquivos2) and on the workstation (CIFS mirror at
    /mnt/Backup). Daniel's rule: heavy media work belongs on d2server,
    so that is the app's real home; the CIFS paths are the fallback."""
    for c in cands:
        if os.path.isdir(c):
            return c
    return cands[-1]

MEDIA_ROOTS = [r for r in os.environ.get('MEDIA_ROOTS', '').split(':')
               if os.path.isdir(r)]
if not MEDIA_ROOTS:
    _roots_cfg = _cfg_get('library', 'roots', '')
    MEDIA_ROOTS = [r for r in _roots_cfg.split(':') if os.path.isdir(r)]
if not MEDIA_ROOTS:
    # Música first: the probe pass walks roots in order and the duration
    # cache replays already-probed files instantly, so audio (the small,
    # newly indexed root) finishes while video replays from cache.
    MEDIA_ROOTS = [_pick_local('/mnt/arquivos2/Música', '/mnt/Backup/Música'),
                   _pick_local('/mnt/arquivos2/Vídeos', '/mnt/Backup/Vídeos')]
CACHE_DIR = _cfg_get('library', 'cache_dir', '') or \
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
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
             '.flv', '.wmv', '.mov', '.mp4', '.m4v', '.vob',
             '.3gp', '.3g2', '.rmvb', '.webm', '.mk3d', '.m2t')
# live 2026-09-15 (workflow audit): .rmvb (92 files) and .webm (51) were
# missing — Serviio lists both, so every /tr/ click on an rmvb fell to the
# duration-index fallback and silently offered to transcode an UNRELATED
# video (Cavaleiros ep 01 -> an mpeg4 512x384 of the same length), and
# .webm items either 404'd or resolved to their .wmv twin. .mk3d/.m2t
# are latent table alignment (VID_MIME_EXT already promises them).
# era Presto decodes MP3 but not FLAC/OGG/WAV/... — those route to the
# live /atr/ MP3 pipe, so the index must know them too. Full Serviio
# roster (owner-directed 2026-09-15): mpc/wv/aiff are in the library
# and stream through the same pipe, so they must be indexed.
AUDIO_EXT = ('.mp3', '.flac', '.m4a', '.aac', '.wav', '.ogg', '.oga',
             '.wma', '.opus', '.ape', '.mka', '.mks', '.mpc', '.wv',
             '.aif', '.aiff')   # .mks: MIME_EXT promises it (x-matroska)

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
    # Serviio sometimes titles an item with its extension included
    # ("02 Querem Meu Sangue.wma" — live 2026-09-15): strip it so the
    # stem map hits directly instead of dropping to the substring tier
    tl = title.lower()
    if os.path.splitext(tl)[1] in (AUDIO_EXT + VIDEO_EXT):
        tl = os.path.splitext(tl)[0]
    with _lib_lock:
        paths = [p for p in _lib_by_stem.get(tl, [])
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
    if len(paths) > 1 and not didl_dur:
        # No DIDL duration to rank with. Some sources have none at all:
        # raw mpegvideo streams report duration=N/A to ffprobe and
        # Serviio's DIDL res carries no duration either (live
        # 2026-09-15: "Autmn Yard.mpg", a duration-less MPEG-1 1280x720
        # DreamScene clip — its .webm twin shares the stem, so the
        # duration tier was the only thing that could separate them and
        # every click 404'd). Rank with the duration term dropped:
        # prefer_ext first (the res mime still says which twin is
        # playing), then shared title tokens. A tie means same-stem
        # copies or versions of the same-titled recording — pick the
        # first rather than 404ing the track (same rationale as the
        # duplicate-copy tie below).
        def toks(s):
            return set(w for w in re.split(r'[^a-z0-9]+', s.lower())
                       if len(w) > 1 and not w.isdigit())

        def rank_nd(p):
            ext_ok = bool(prefer_ext and p.lower().endswith(prefer_ext))
            shared = len(toks(os.path.splitext(os.path.basename(p))[0])
                         & toks(title))
            return (-ext_ok, -shared)
        ranked = sorted(paths, key=rank_nd)
        return ranked[0], None
    if didl_dur:
        def d(p):
            with _lib_lock:
                return _lib_durations.get(p)

        def toks(s):
            return set(w for w in re.split(r'[^a-z0-9]+', s.lower())
                       if len(w) > 1 and not w.isdigit())

        def rank(p):
            # collision tiebreak: requested format first (dual-format
            # stems: FLAC and MP3 of one song differ by ~1-2s, inside
            # the ±3s duration window, so duration alone ties), then
            # shared title tokens (online-metadata titles translate the
            # filename, but keep words like "adam"), then closer
            # duration. DIDL durations are second-resolution, so a
            # sub-second delta is a strong signal on its own.
            ext_ok = bool(prefer_ext and p.lower().endswith(prefer_ext))
            shared = len(toks(os.path.splitext(os.path.basename(p))[0]) & toks(title))
            return (-ext_ok, -shared, abs(d(p) - didl_dur))

        m = [p for p in paths if d(p) and abs(d(p) - didl_dur) < 3]
        if not m and not paths:
            # duration-index fallback (no title hit at all): inline kind
            # check — kind_ok() would re-acquire _lib_lock and deadlock.
            # A duration-only match whose name shares NO title token is a
            # different recording that happens to be the same length —
            # live 2026-09-15 the (then unindexed) rmvb probe matched an
            # unrelated mpeg4 within ±3s and offered to transcode IT
            # under the episode's title. Require token overlap so the
            # fallback never crosses titles; a miss is a clean error.
            tt = toks(title)
            with _lib_lock:
                m = [p for p, dur in _lib_durations.items()
                     if abs(dur - didl_dur) < 3
                     and (want is None or _lib_kind.get(p) == want)
                     and toks(os.path.splitext(os.path.basename(p))[0]) & tt]
        if len(m) == 1:
            return m[0], None
        if len(m) > 1:
            ranked = sorted(m, key=rank)
            if rank(ranked[0]) != rank(ranked[1]):
                return ranked[0], None
            # a complete rank tie — same format (prefer_ext), same title
            # tokens, same duration — is two copies of one recording
            # (live: "02 Querem Meu Sangue.wma" sits in both MPB/ and
            # Reggae/, 201.266s each). Any copy plays the right bytes:
            # pick the first instead of 404ing the track.
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
                _q = parse_qs(u.query)
                start = _qs_int(_q, 'start')
                sel = _qs_int(_q, 'sel')
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
                    body = render_list(obj_id, objects, total, start, title,
                                       sel=sel)
            elif u.path.startswith('/keylog/'):
                # probe beacon from the /keys page: log and answer a
                # tiny transparent gif (Image() src fetches)
                code = u.path[len('/keylog/'):].split('?')[0]
                sys.stderr.write('%s - KEYPROBE code=%s\n'
                                 % (self.address_string(), code))
                self.send_response(200)
                self.send_header('Content-Type', 'image/gif')
                gif = (b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
                       b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00'
                       b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
                self.send_header('Content-Length', str(len(gif)))
                self.end_headers()
                self._sent = True  # no HTML fallback if the socket dies
                self.wfile.write(gif)
                return
            elif u.path == '/manual':
                self._send_html(render_manual().encode())
                return
            elif u.path == '/probe':
                self._send_html(render_probe().encode())
                return
            elif u.path == '/probe/glyphs':
                self._send_html(render_probe_glyphs().encode())
                return
            elif u.path == '/probe/cookie':
                html, cookies = render_probe_cookie(
                    self.headers.get('Cookie'))
                self._send_html(html.encode(), cookies=cookies)
                return
            elif u.path == '/probe/caps':
                self._send_html(render_probe_caps().encode())
                return
            elif u.path == '/probe/art':
                _v = _qs_int(parse_qs(u.query), 'v', 1)
                if _v == 13:
                    self._send_html(render_probe_fullvideo().encode())
                else:
                    self._send_html(render_probe_art(_v).encode())
                return
            elif u.path == '/probe/ctl':
                self._send_html(render_probe_ctl(
                    _qs_int(parse_qs(u.query), 'v', 2)).encode())
                return
            elif u.path == '/keys':
                self._send_html(render_keys().encode())
                return
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
                back = back_url(u.query)
                o = _oid_for_item(obj_id)
                if not o:
                    body = render_error('item', T('no_meta') % obj_id)
                elif kind == 'img':
                    r = pick_image_res(o['res'])
                    body = render_image(o, r) if r else render_error('item', T('no_image_res'))
                elif kind == 'aud':
                    # r may be None (mpc/wv: Serviio lists them with no
                    # res) — render_music handles that via the /atr/ lane
                    r = pick_audio_res(o['res'])
                    body = render_music(o, r, back=back)
                else:
                    r = pick_video_res(o['res'])
                    body = (render_player(o, r, back=back) if r
                            else render_error('item', T('no_video_res')))
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
            # 320 kbps CBR + 48 kHz (owner-directed quality, 2026-09-15):
            # max MP3 fidelity for the era player, and 48k is the era-safe
            # rate the video lane already uses for AAC
            proc = subprocess.Popen(
                ['ffmpeg', '-nostdin', '-v', 'error', '-i', src,
                 '-map', '0:a:0', '-c:a', 'libmp3lame', '-b:a', '320k',
                 '-ar', '48000', '-f', 'mp3', '-'],
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
            # the request thread kills ffmpeg + closes stdout on client
            # abort (track skip / voltar); the pump's in-flight read then
            # raises on the closed pipe — that is the normal shutdown
            # path, not an error (live 2026-09-15: it crash-logged as
            # "Exception in thread Thread-N (pump)" on every skip)
            try:
                while True:
                    b = proc.stdout.read(64 * 1024)
                    q.put(b)
                    if not b:
                        return
            except (ValueError, OSError):
                pass   # stdout closed under us: stream over, exit clean

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
                self._send_html(render_player(
                    o, r, back=back_url(u.query)).encode())  # direct-play
                return
            dur = _didl_duration_seconds(o['res'])
            src, err = resolve_source(
                o['title'], dur, want='video',
                prefer_ext=VID_MIME_EXT.get(r['mime']) if r else None)
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
                prev_id, next_id = video_neighbors(o)
                self._send_html(render_local_player(
                    o['title'], 'video/mp4', '/tcf/%s' % key,
                    prev=_tr_url(prev_id) if prev_id else None,
                    nxt=_tr_url(next_id) if next_id else None,
                    back=back_url(u.query)).encode())
            else:
                self._send_html(render_progress(
                    o['title'], pct, _lib_note).encode())
        except Exception as e:
            self._send_html(render_error('transcode', e).encode())

    def _send_html(self, payload, cookies=None):
        if self._sent:
            return
        self._sent = True
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            # pages are no-store, so any state that must outlive a page
            # load has to ride in a cookie: every track change here is a
            # full navigation (the era player cannot swap a <source>)
            for c in (cookies or []):
                self.send_header('Set-Cookie', c)
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
    print('  config: %s (%s)' % (CONFIG_PATH,
                                 'loaded' if os.path.isfile(CONFIG_PATH)
                                 else 'not present — built-in defaults'))
    print('  media roots: %s' % ':'.join(MEDIA_ROOTS))
    print('  keymap: %s' % json.dumps(KEYMAP))
    ThreadingHTTPServer((BIND_HOST, PORT), Handler).serve_forever()


if __name__ == '__main__':
    main()