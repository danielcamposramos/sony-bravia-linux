#!/usr/bin/env python3
"""Navigation polish: row glyphs, cursor restore, and the goBack contract.

The bug this battery exists for: NAV_JS called goBack() while only the two
player templates defined it, so LEFT and BACKSPACE threw a ReferenceError
that killed the whole inline script — arrow keys dead, no error on screen.
An unresolved %SEL0% has the same shape: a JS syntax error that looks like
"the remote stopped working" rather than like a crash.
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['BRAVIA_SKIP_INDEX'] = '1'
import server as S

ok = fail = 0
def chk(name, cond):
    global ok, fail
    if cond: ok += 1; print('%-58s OK' % name)
    else: fail += 1; print('%-58s FAIL' % name)

# ---- every template that binds back must also define it ----
for tname in ('NAV_JS', 'PLAYER_JS', 'MUSIC_JS'):
    tpl = getattr(S, tname)
    js = S._resolve_js(tpl)
    chk('%s: goBack() is defined where it is called' % tname,
        ('goBack()' not in js) or ('function goBack(' in js))
    chk('%s: no unresolved %%placeholder%% left' % tname,
        not re.search(r'%(SEL0|GOBACK|BACK)%', js))

# ---- _page is the backstop: a raw template must still come out clean ----
for tname in ('NAV_JS', 'PLAYER_JS', 'MUSIC_JS'):
    page = S._page('t', '<p>x</p>', extra_js=getattr(S, tname))
    chk('_page(%s) emits no placeholder' % tname,
        not re.search(r'%(SEL0|GOBACK|BACK)%', page))
chk('_page default (no extra_js) emits no placeholder',
    not re.search(r'%(SEL0|GOBACK|BACK)%', S._page('t', '<p>x</p>')))

# ---- backUrl wiring ----
js = S._resolve_js(S.NAV_JS)
chk('no back target -> falls back to history.go(-1)',
    'var backUrl="";' in js and 'history.go(-1)' in js)
js = S._resolve_js(S.MUSIC_JS, back='/b/1%244?start=18&sel=3')
chk('back target -> assigns window.location',
    '/b/1%244?start=18&sel=3' in js and 'window.location=backUrl' in js)

# ---- back_url() parses what render_list emits ----
chk('back_url: full origin round-trips',
    S.back_url('s=7&p=1%244~18') == '/b/1%244?start=18&sel=7')
chk('back_url: no origin -> empty (history fallback)', S.back_url('') == '')
chk('back_url: garbage start -> 0', S.back_url('s=2&p=x~zz') == '/b/x?start=0&sel=2')
chk('back_url: non-numeric sel -> 0', S.back_url('s=../x&p=x~0') == '/b/x?start=0&sel=0')

# ---- a stale or hand-typed query must not 500 the listing ----
from urllib.parse import parse_qs
chk('_qs_int: garbage -> default', S._qs_int(parse_qs('sel=abc'), 'sel') == 0)
chk('_qs_int: absent -> default', S._qs_int(parse_qs(''), 'start') == 0)
chk('_qs_int: real value survives', S._qs_int(parse_qs('start=18'), 'start') == 18)

# ---- row glyphs: every kind render_list can emit has one ----
for kind in ('dir', 'aud', 'vid', 'tr', 'img', 'na'):
    chk('GLYPH has %-4s' % kind, kind in S.GLYPH)
chk('glyphs stay in Unicode 1.1 (era fonts carry them)',
    all(ord(g) <= 0x25FF or g == '♪' for g in S.GLYPH.values()))
row = S._row('aud', '/aud/x?s=2&p=0~0', 'Track')
chk('_row: glyph precedes the label', row.index('♪') < row.index('Track'))
chk('_row: carries its origin', 's=2&p=0~0' in row)
chk('_row: no href -> unclickable row', '<a' not in S._row('na', '', 'Unplayable'))
chk('_row: label is escaped', '&amp;' in S._row('dir', '/b/x', 'Rock & Roll'))

print('\nRESULT: %s' % ('ALL PASS' if not fail else '%d FAILED' % fail))
sys.exit(1 if fail else 0)
