#!/usr/bin/env python3
"""Regression battery for the config surface (config.ini / BRAVIA_CONFIG)
and the multimedia key mapping (KEYMAP, %KEYMAP% injection, /keys page).
    BRAVIA_SKIP_INDEX=1 python3 tests/test-config-keys.py
"""
import os
import sys
import tempfile

os.environ['BRAVIA_SKIP_INDEX'] = '1'

APPDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APPDIR)

fails = []


def check(name, cond, detail=''):
    print('%-58s %s%s' % (name, 'OK' if cond else 'FAIL',
                          (' — ' + detail) if detail and not cond else ''))
    if not cond:
        fails.append(name)


# ---------- 1. no config file -> built-in defaults ----------
cfgfile = tempfile.NamedTemporaryFile('w', suffix='.ini', delete=False)
cfgfile.write('')
cfgfile.close()
os.environ['BRAVIA_CONFIG'] = cfgfile.name
import importlib
import server  # noqa: E402
importlib.reload(server)

check('no config: serviio host default', server.SERVIIO == '192.168.0.60',
      repr(server.SERVIIO))
check('no config: serviio port default', server.SERVIIO_PORT == 8895)
check('no config: CONTROL_URL built from host/port',
      server.CONTROL_URL == 'http://192.168.0.60:8895/serviceControl')
check('no config: keymap defaults (Android family)',
      server.KEYMAP['playpause'] == [85] and server.KEYMAP['prev'] == [88]
      and server.KEYMAP['ff'] == [90], repr(server.KEYMAP))
check('keymap covers all eight actions',
      set(server.KEYMAP) == {'playpause', 'play', 'pause', 'stop',
                             'prev', 'next', 'rew', 'ff'})
check('CONFIG_PATH from BRAVIA_CONFIG env', server.CONFIG_PATH == cfgfile.name)

# ---------- 2. populated config file ----------
cfgfile2 = tempfile.NamedTemporaryFile('w', suffix='.ini', delete=False)
cfgfile2.write(
    '[app]\nbind_host = 127.0.0.1\nport = 9001\n'
    '[serviio]\nhost = media.lan\nport = 8896\n'
    '[keys]\nplaypause = 415\nprev = 412, 417\nff = 419\nstop = 0\n')
cfgfile2.close()
os.environ['BRAVIA_CONFIG'] = cfgfile2.name
importlib.reload(server)

check('config: [serviio] host', server.SERVIIO == 'media.lan', repr(server.SERVIIO))
check('config: [serviio] port', server.SERVIIO_PORT == 8896)
check('config: CONTROL_URL follows config',
      server.CONTROL_URL == 'http://media.lan:8896/serviceControl')
check('config: [app] bind_host', server.BIND_HOST == '127.0.0.1')
check('config: keymap single override', server.KEYMAP['playpause'] == [415])
check('config: keymap comma list -> sorted list',
      server.KEYMAP['prev'] == [412, 417], repr(server.KEYMAP['prev']))
check('config: 0 disables an action', server.KEYMAP['stop'] == [],
      repr(server.KEYMAP['stop']))
check('config: untouched keys keep defaults', server.KEYMAP['next'] == [87])

# ---------- 3. %KEYMAP% resolution in every player page ----------
server._UI.lang = 'pt'
FOLDER = 'A_F^FOL*R1'
TRACKS = ['%s$MI%d' % (FOLDER, 100 + i) for i in range(3)]


def fake_browse(obj_id, flag='BrowseDirectChildren', start=0, count=18):
    objs = [{'id': FOLDER, 'title': 'folder', 'container': True,
             'child_count': 3}]
    for i, tid in enumerate(TRACKS):
        objs.append({'id': tid, 'title': 'Track %02d' % (i + 1),
                     'cls': 'object.item.audioItem.musicTrack',
                     'res': [{'mime': 'audio/mpeg',
                              'url': 'http://x/r%d' % i,
                              'pn': 'p', 'ci': '0'}]})
    return objs, len(objs)


server.upnp_browse = fake_browse

obj = {'id': TRACKS[1], 'title': 'Track 02',
       'res': [{'mime': 'audio/mpeg', 'url': 'http://x/r1',
                'pn': 'p', 'ci': '0'}],
       'cls': 'object.item.audioItem.musicTrack'}
page = server.render_music(obj, obj['res'][0])
check('music page: km() helper injected', 'function km(' in page)
check('music page: KM carries config codes', 'km(\'playpause\',415)' in page
      or ('415' in page and 'var KM=' in page), page[:200])
check('music page: %KEYMAP% resolved', '%KEYMAP%' not in page)
check('music page: no unresolved placeholders remain',
      '%PREV%' not in page and '%NEXT%' not in page)

vobj = {'id': '%s$MI900' % FOLDER, 'title': 'a video',
        'cls': 'object.item.videoItem.movie',
        'res': [{'mime': 'video/mp4', 'url': 'http://x/v',
                 'pn': 'p', 'ci': '0'}]}
vpage = server.render_player(vobj, vobj['res'][0])
check('video page: km() helper injected', 'function km(' in vpage)
check('video page: prev/next URLs present',
      'prevUrl=' in vpage and 'nextUrl=' in vpage)
check('video page: %KEYMAP% resolved', '%KEYMAP%' not in vpage)

lp = server.render_local_player('x.mp4', 'video/mp4', '/stream/x')
check('local player: km() helper injected', 'function km(' in lp)
check('local player: %KEYMAP% resolved', '%KEYMAP%' not in lp)

# ---------- 4. /keys probe page renders ----------
keys_page = server.render_keys()
check('/keys page renders with beacon URL', '/keylog/' in keys_page)
check('/keys page mentions KEYPROBE', 'KEYPROBE' in keys_page)

# ---------- 5. folder_neighbors generalization ----------
p, n = server.video_neighbors({'id': '%s$MI900' % FOLDER,
                               'cls': 'object.item.videoItem.movie',
                               'res': [], 'title': 'v'})
check('video_neighbors: no video siblings -> none', p is None and n is None)

vids = ['%s$MI%d' % (FOLDER, 200 + i) for i in range(2)]


def mixed_browse(obj_id, flag='BrowseDirectChildren', start=0, count=18):
    objs = []
    for tid in TRACKS:
        objs.append({'id': tid, 'title': 't',
                     'cls': 'object.item.audioItem.musicTrack',
                     'res': [{'mime': 'audio/mpeg', 'url': 'http://x',
                              'pn': 'p', 'ci': '0'}]})
    for tid in vids:
        objs.append({'id': tid, 'title': 'v',
                     'cls': 'object.item.videoItem.movie', 'res': []})
    return objs, len(objs)


server.upnp_browse = mixed_browse
p, n = server.video_neighbors({'id': vids[0],
                               'cls': 'object.item.videoItem.movie',
                               'res': [], 'title': 'v'})
check('video_neighbors: only videoItem counted',
      p == vids[1] and n == vids[1], 'p=%r n=%r' % (p, n))
p, n = server.music_neighbors({'id': TRACKS[1],
                               'cls': 'object.item.audioItem.musicTrack',
                               'res': [], 'title': 't'})
check('music_neighbors: only audioItem counted',
      p == TRACKS[0] and n == TRACKS[2], 'p=%r n=%r' % (p, n))

# cleanup env so later imports aren't skewed
os.environ.pop('BRAVIA_CONFIG', None)
importlib.reload(server)

print()
print("RESULT:", "ALL PASS" if not fails else ("%d FAIL: %s" % (len(fails), fails)))
sys.exit(1 if fails else 0)