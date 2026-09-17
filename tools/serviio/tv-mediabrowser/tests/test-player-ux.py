#!/usr/bin/env python3
"""Regression battery for the player-UX additions (prev/next in folder +
repeat-this-track toggle). Run from the tv-mediabrowser dir:
    BRAVIA_SKIP_INDEX=1 python3 tests/player-ux.py
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


# --- 1. neighbors: order + wrap
p, n = server.music_neighbors(track_obj(1))
check('neighbors middle: prev=MI100 next=MI102',
      p == TRACKS[0] and n == TRACKS[2], 'p=%r n=%r' % (p, n))
p, n = server.music_neighbors(track_obj(0))
check('neighbors first: prev wraps to last',
      p == TRACKS[2] and n == TRACKS[1], 'p=%r n=%r' % (p, n))
p, n = server.music_neighbors(track_obj(2))
check('neighbors last: next wraps to first',
      p == TRACKS[1] and n == TRACKS[0], 'p=%r n=%r' % (p, n))

# --- 2. video/container siblings excluded
p, n = server.music_neighbors({'id': '%s$MI900' % FOLDER, 'title': 'a video',
                               'res': [], 'cls': ''})
check('non-audio / not-in-folder -> no neighbors', p is None and n is None)

# --- 3. no $MI tail -> no neighbors
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

# --- 4. rendered page: middle track has prev/next + repeat buttons
page = server.render_music(track_obj(1), track_obj(1)['res'][0])
check('prev button present', "data-act=\"prv\"" in page)
check('next button present', "data-act=\"nxt\"" in page)
check('repeat button present', "data-act=\"rep\"" in page)
check('prev URL in JS points at MI100',
      'prevUrl=' in page and '$MI100' not in page and 'A_F%5EFOL%2AR1%24MI100' in page,
      page[page.find('prevUrl='):page.find('prevUrl=') + 60])
check('next URL in JS points at MI102',
      'A_F%5EFOL%2AR1%24MI102' in page)
check('no unresolved %PREV%/%NEXT% placeholders',
      '%PREV%' not in page and '%NEXT%' not in page)
check('repeat-on string in JS (pt)', server.T('music_rep_on') in page)
check('repeat-off string in JS (pt)', server.T('music_rep_off') in page)
check('ended handler replays when repeat on', 'v.load();' in page
      and '%music_rep_on%' not in page)

# --- 5. all languages carry the new strings
for lang in ('en', 'pt', 'es'):
    server._UI.lang = lang
    for key in ('btn_prev', 'btn_next', 'btn_rep',
                'music_rep_on', 'music_rep_off'):
        v = server.T(key)
        check('%s [%s]' % (key, lang), bool(v) and '%' not in v, repr(v))
server._UI.lang = 'pt'

# --- 6. single-track folder -> no prev/next buttons, no JS crash
single = [TRACKS[0]]


def single_browse(obj_id, flag='BrowseDirectChildren', start=0, count=18):
    return ([{'id': TRACKS[0], 'title': 'only', 'res': track_obj(0)['res'],
               'cls': 'object.item.audioItem.musicTrack'}], 1)


server.upnp_browse = single_browse
page = server.render_music(track_obj(0), track_obj(0)['res'][0])
# The transport bar keeps a stable shape: prev/next always render, but
# with no sibling track they are dimmed and the cursor skips them (the
# old behavior dropped the buttons, which shifted the rest of the bar
# under the user's thumb depending on where a track was opened from).
check('single track: prev/next rendered but dimmed',
      'data-act="prv"' in page and 'data-act="nxt"' in page
      and page.count('class="dim"') == 2)
check('single track: prevUrl/nextUrl are empty strings',
      'prevUrl=""' in page and 'nextUrl=""' in page)
check('single track: repeat still present', 'data-act="rep"' in page)
server.upnp_browse = fake_browse

print()

# --- 7. no-res item (mpc/wv shape) gets the full player too
o_mpc = {'id': TRACKS[1], 'title': 'Lie (Edit).mpc', 'res': [],
         'cls': 'object.item.audioItem.musicTrack'}
page = server.render_music(o_mpc, None)
check('no-res item: prev/next + repeat present',
      'data-act="prv"' in page and 'data-act="nxt"' in page
      and 'data-act="rep"' in page)
check('no-res item: label from title ext', 'audio/x-musepack' in page)

# --- 8. video PLAYER_JS still resolves (no leftover %PREV% etc.)
js = server.player_js('video/mp4', '/stream/x', tpl=server.PLAYER_JS)
check('PLAYER_JS unaffected by new placeholders',
      '%PREV%' not in js and '%NEXT%' not in js and '%music_rep_on%' not in js
      and '%DUR%' not in js)

print()

# --- 9. transport bar: two cursor groups, glyphs, progress, duration
page = server.render_music(track_obj(1), track_obj(1)['res'][0])
check('bar: transport buttons are cursor group 0',
      page.count('data-grp="0"') == 6)
check('bar: Back row is cursor group 1', page.count('data-grp="1"') == 1)
check('bar: every button carries a label for #blbl',
      page.count('data-lbl="') == 7)
check('bar: play glyph has an id so JS can track real state',
      'id="ppg"' in page and '▶' in page)
check('progress: bar + clock elements present',
      'id="pb"' in page and 'id="pbf"' in page and 'id="time"' in page)
check('progress: DUR always injected (0 when DIDL has no duration)',
      'var DUR=0;' in page)
# a DIDL duration must reach the page as seconds — this is what gives a
# live-transcoded FLAC a progress bar, since the /atr/ pipe leaves the
# element's own duration NaN
o_dur = dict(track_obj(1))
o_dur['res'] = [dict(track_obj(1)['res'][0], duration='0:03:05.000')]
check('progress: DIDL duration converted to seconds and injected',
      'var DUR=185;' in server.render_music(o_dur, o_dur['res'][0]))
check('cursor opens on Play/Pause, not on row 0',
      "getAttribute('data-act')=='pp'" in page)
check('no stale %DUR% placeholder in the music page', '%DUR%' not in page)
check('page stays within the era byte budget (<12 KB)',
      len(page.encode('utf-8')) < 12288,
      '%d bytes' % len(page.encode('utf-8')))

print()
print("RESULT:", "ALL PASS" if not fails else ("%d FAIL: %s" % (len(fails), fails)))
sys.exit(1 if fails else 0)