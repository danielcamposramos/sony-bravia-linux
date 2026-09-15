#!/usr/bin/env python3
"""Regression battery for the mpc/wv + relative-URL fixes (2026-09-15).

Run from the tv-mediabrowser dir with BRAVIA_SKIP_INDEX=1:
    BRAVIA_SKIP_INDEX=1 python3 tests/mpcwv-fix.py
"""
import os
import sys

os.environ['BRAVIA_SKIP_INDEX'] = '1'
sys.path.insert(0, os.getcwd())
import server  # noqa: E402

fails = []


def check(name, cond, detail=''):
    print('%-58s %s%s' % (name, 'OK' if cond else 'FAIL',
                          (' — ' + detail) if detail and not cond else ''))
    if not cond:
        fails.append(name)


# 1. proxied_res_url is RELATIVE (OWN_BASE bug fix)
u = server.proxied_res_url('http://192.168.0.60:8895/resource/83001/'
                           'MEDIA_ITEM/MP3-0/ORIGINAL')
check('proxied_res_url relative', u.startswith('/stream/'), u)
check('proxied_res_url quoted', '%3A' in u and u.startswith('/stream/http%3A'), u)

# 2. T dicts have music_unknown in all three languages
for lang in ('en', 'pt', 'es'):
    server._UI.lang = lang
    v = server.T('music_unknown')
    check('music_unknown [%s]' % lang, bool(v) and '%s' not in v, repr(v))

# 3. render_music with res=None (mpc/wv item shape: res==[])
server._UI.lang = 'pt'
o_mpc = {'id': 'A_F^FOL*R1$MI25256', 'title': 'Lie (Edit)',
         'res': [], 'cls': 'object.item.audioItem.musicTrack'}
try:
    page = server.render_music(o_mpc, None)
    check('render_music(res=None) no raise', True)
    check('render_music res=None -> /atr/', '/atr/A_F%5EFOL%2AR1%24MI25256' in page)
    check('render_music res=None -> unknown label (extensionless titles)',
          server.T('music_unknown') in page and 'audio/x-' not in page)
    check('render_music res=None -> live label', server.T('music_live') in page)
except Exception as e:
    check('render_music(res=None) no raise', False, repr(e))

# 4. render_music with a native MP3 res -> /stream/, no live label
o_mp3 = {'id': 'X$MI1', 'title': 'Track 03',
         'res': [{'mime': 'audio/mpeg', 'url': 'http://192.168.0.60:8895/resource/1/MEDIA_ITEM/MP3-0/ORIGINAL', 'pn': 'http-get:*:audio/mpeg:*', 'ci': '0'}],
         'cls': 'object.item.audioItem.musicTrack'}
try:
    page = server.render_music(o_mp3, o_mp3['res'][0])
    check('render_music(mp3) -> /stream/ relative',
          "s.src='/stream/" in page, page[:200])
    check('render_music(mp3) no live label', server.T('music_live') not in page)
    check('render_music(mp3) no http://192.168 in src',
          "src='http://" not in page)
except Exception as e:
    check('render_music(mp3) no raise', False, repr(e))

# 5. render_music with a FLAC res -> /atr/ (unchanged behavior)
o_flac = {'id': 'X$MI2', 'title': 'some flac',
          'res': [{'mime': 'audio/x-flac', 'url': 'http://x/', 'pn': 'p', 'ci': '0'}],
          'cls': 'object.item.audioItem.musicTrack'}
try:
    page = server.render_music(o_flac, o_flac['res'][0])
    check('render_music(flac) -> /atr/', '/atr/X%24MI2' in page)
except Exception as e:
    check('render_music(flac) no raise', False, repr(e))


# --- appended 2026-09-15: format label for no-res items derives from title ext
try:
    page = server.render_music(o_mpc, None)
    check('no-res extensionless still unknown', server.T('music_unknown') in page)
    o_mpc2 = {'id': 'X$MI77', 'title': '01 - Lie (Edit).mpc',
              'res': [], 'cls': 'object.item.audioItem.musicTrack'}
    page = server.render_music(o_mpc2, None)
    check('mpc title-ext -> audio/x-musepack label', 'audio/x-musepack' in page,
          page[:300])
    check('mpc no longer says unknown', server.T('music_unknown') not in page)
    o_wv = {'id': 'X$MI9', 'title': 'David Garrett - Rock Symphonies (Deluxe Version) CD1.wv',
            'res': [], 'cls': 'object.item.audioItem.musicTrack'}
    page = server.render_music(o_wv, None)
    check('wv title-ext -> audio/x-wavpack label', 'audio/x-wavpack' in page)
except Exception as e:
    check('label derivation no raise', False, repr(e))
print()
print("RESULT:", "ALL PASS" if not fails else ("%d FAIL: %s" % (len(fails), fails)))
sys.exit(1 if fails else 0)
