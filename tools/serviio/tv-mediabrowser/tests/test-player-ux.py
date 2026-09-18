#!/usr/bin/env python3
"""Regression battery for the audio player.

Rewritten 2026-09-18 for the native-controls design (validated on the
EX725): the player is the set's own transport, scaled, with cover art as
the poster; our JS owns only what the native bar cannot do — previous /
next track (left/right), repeat (up, persisted in a cookie), and back
(down / RETURN / the GREEN button, which Opera handles itself). The old
custom glyph bar, virtual cursor, progress bar and injected duration are
gone; see docs/era-media-element.md and docs/era-key-vocabulary.md.

    BRAVIA_SKIP_INDEX=1 python3 tests/test-player-ux.py
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


# --- fake DIDL folder: 3 musicTracks + a container + a video item
FOLDER = 'A_F^FOL*R1'
TRACKS = ['%s$MI%d' % (FOLDER, 100 + i) for i in range(3)]


def fake_browse(obj_id, flag='BrowseDirectChildren', start=0, count=18):
    objs = []
    if obj_id == FOLDER:
        objs = [{'id': FOLDER, 'title': 'folder', 'container': True,
                 'child_count': 4},
                {'id': '%s$MI900' % FOLDER, 'title': 'a video',
                 'cls': 'object.item.videoItem.movie', 'res': []},
                ]
        for i, tid in enumerate(TRACKS):
            objs.append({'id': tid, 'title': 'Track %02d' % (i + 1),
                         'cls': 'object.item.audioItem.musicTrack',
                         'res': [{'mime': 'audio/mpeg',
                                  'url': 'http://x/r%d' % i,
                                  'pn': 'p', 'ci': '0'}]})
    return objs, len(objs)


server.upnp_browse = fake_browse
server._UI.lang = 'pt'


def track_obj(i):
    return {'id': TRACKS[i], 'title': 'Track %02d' % (i + 1),
            'res': [{'mime': 'audio/mpeg', 'url': 'http://x/r%d' % i,
                     'pn': 'p', 'ci': '0'}],
            'cls': 'object.item.audioItem.musicTrack'}


# --- 1. neighbors: order + wrap (unchanged, still the source of prev/next)
p, n = server.music_neighbors(track_obj(1))
check('neighbors middle: prev=MI100 next=MI102',
      p == TRACKS[0] and n == TRACKS[2], 'p=%r n=%r' % (p, n))
p, n = server.music_neighbors(track_obj(0))
check('neighbors first: prev wraps to last',
      p == TRACKS[2] and n == TRACKS[1], 'p=%r n=%r' % (p, n))
p, n = server.music_neighbors(track_obj(2))
check('neighbors last: next wraps to first',
      p == TRACKS[1] and n == TRACKS[0], 'p=%r n=%r' % (p, n))
p, n = server.music_neighbors({'id': '%s$MI900' % FOLDER, 'title': 'a video',
                               'res': [], 'cls': ''})
check('non-audio / not-in-folder -> no neighbors', p is None and n is None)
p, n = server.music_neighbors({'id': 'A_F^FOL*R1', 'title': 'x',
                               'res': [], 'cls': ''})
check('container-like id -> no neighbors', p is None and n is None)


def raising_browse(obj_id, flag='BrowseDirectChildren', start=0, count=18):
    raise OSError('soap down')


orig_browse = server.upnp_browse
server.upnp_browse = raising_browse
p, n = server.music_neighbors(track_obj(1))
check('browse failure -> no neighbors (no raise)', p is None and n is None)
server.upnp_browse = orig_browse

print()

# --- 2. the native-controls player: element, poster, chrome
page = server.render_music(track_obj(1), track_obj(1)['res'][0])
check('native <video controls> element present',
      'id="pv"' in page and 'controls' in page)
check('scaled x3 via -o-transform (enlarges the native bar)',
      '-o-transform:scale(3)' in page and 'transform:scale(3)' in page)
check('wrapped in a percentage-width table, nothing clipped',
      'width="100%"' in page and 'overflow:hidden' not in page)
check('brand header names the surface',
      server.BRAND in page and server.T('audio_player') in page)
check('legend lists prev / next / repeat',
      server.T('btn_prev') in page and server.T('btn_next') in page
      and server.T('btn_rep') in page)
check('repeat-state span present for JS to fill', 'id="repl"' in page)
check('portal shortcut present', server.PORTAL_URL in page)

# --- 3. the JS: prev/next URLs, cookie-backed repeat, key model
check('prevUrl points at MI100 (quoted id)',
      'A_F%5EFOL%2AR1%24MI100' in page)
check('nextUrl points at MI102 (quoted id)',
      'A_F%5EFOL%2AR1%24MI102' in page)
check('no unresolved %PREV%/%NEXT%/%GOBACK%/%BACK% placeholders',
      not any(t in page for t in ('%PREV%', '%NEXT%', '%GOBACK%', '%BACK%')))
check('repeat persists via the bravia_rep cookie',
      'bravia_rep' in page and 'toggleRep' in page)
check('repeat-on/off strings resolved (pt)',
      server.T('music_rep_on') in page and server.T('music_rep_off') in page
      and '%music_rep_on%' not in page)
check('ended handler: repeat-reload or auto-advance to next',
      'v.load();' in page and 'window.location=nextUrl' in page)
# key model: OK(13) let through to native; 37/39 prev/next; 38 repeat;
# 40/8 back. The handler returns true for 13 so native play/pause works.
check('OK (13) let through to native controls',
      'if(k==13){return true;}' in page)
check('left(37)=prev, right(39)=next in the handler',
      'if(k==37){if(prevUrl)' in page and 'if(k==39){if(nextUrl)' in page)
check('up(38) toggles repeat', 'if(k==38){toggleRep()' in page)
check('down(40)/RETURN(8) go back',
      'if(k==40||k==8){goBack()' in page)
check('no leftover custom-bar machinery (km/data-grp/#blbl/progress)',
      not any(t in page for t in ("function km(", 'data-grp=', 'id="blbl"',
                                  'id="pbf"', 'id="ppg"')))

print()

# --- 4. single-track folder: prev/next are empty, no crash
def single_browse(obj_id, flag='BrowseDirectChildren', start=0, count=18):
    return ([{'id': TRACKS[0], 'title': 'only', 'res': track_obj(0)['res'],
               'cls': 'object.item.audioItem.musicTrack'}], 1)


server.upnp_browse = single_browse
page1 = server.render_music(track_obj(0), track_obj(0)['res'][0])
check('single track: prevUrl/nextUrl are empty strings',
      'prevUrl=""' in page1 and 'nextUrl=""' in page1)
check('single track: repeat still available', 'toggleRep' in page1)
check('single track: legend still rendered',
      server.T('btn_rep') in page1)
server.upnp_browse = fake_browse

# --- 5. no-res item (mpc/wv shape) still gets the player + a label
o_mpc = {'id': TRACKS[1], 'title': 'Lie (Edit).mpc', 'res': [],
         'cls': 'object.item.audioItem.musicTrack'}
page2 = server.render_music(o_mpc, None)
check('no-res item: native player present',
      'id="pv"' in page2 and 'controls' in page2)
check('no-res item: /atr/ transcode lane', '/atr/' in page2)
check('no-res item: format label shown (audio/x-musepack)',
      'audio/x-musepack' in page2)

# --- 6. all languages carry the strings the player needs
for lang in ('en', 'pt', 'es'):
    server._UI.lang = lang
    for key in ('btn_prev', 'btn_next', 'btn_rep', 'audio_player',
                'portal', 'music_rep_on', 'music_rep_off'):
        v = server.T(key)
        check('%s [%s]' % (key, lang), bool(v) and '%' not in v, repr(v))
server._UI.lang = 'pt'

print()

# --- 7. byte budget: the page stays lean
page = server.render_music(track_obj(1), track_obj(1)['res'][0])
check('page stays within the era byte budget (<12 KB)',
      len(page.encode('utf-8')) < 12288,
      '%d bytes' % len(page.encode('utf-8')))

print()
print("RESULT:", "ALL PASS" if not fails else ("%d FAIL: %s" % (len(fails), fails)))
sys.exit(1 if fails else 0)
