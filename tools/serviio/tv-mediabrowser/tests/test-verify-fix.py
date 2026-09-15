#!/usr/bin/env python3
"""Regression battery for the workflow-audit fixes (rmvb/webm index, mime
table alignment, duration-fallback token guard). Run from the
tv-mediabrowser dir:  BRAVIA_SKIP_INDEX=1 python3 tests/verify-fix.py
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


# --- 1. extension tables now cover the audit gaps
for ext in ('.rmvb', '.webm', '.mk3d', '.m2t'):
    check('VIDEO_EXT has %s' % ext, ext in server.VIDEO_EXT)
check('AUDIO_EXT has .mks', '.mks' in server.AUDIO_EXT)
check('VID_MIME_EXT rmvb', server.VID_MIME_EXT.get('video/vnd.rn-realvideo') == '.rmvb',
      repr(server.VID_MIME_EXT.get('video/vnd.rn-realvideo')))
check('VID_MIME_EXT asf->wmv', server.VID_MIME_EXT.get('video/x-ms-asf') == '.wmv',
      repr(server.VID_MIME_EXT.get('video/x-ms-asf')))

# --- 2. duration-index fallback never crosses titles
# fake a ready index with one unrelated video of the exact same length
server._lib_ready = True
server._lib_dur_done = True
server._lib_durations.clear()
server._lib_kind.clear()
server._lib_by_stem.clear()
server._lib_durations['/media/Videos/Some Unrelated Thing.avi'] = 1432.0
server._lib_kind['/media/Videos/Some Unrelated Thing.avi'] = 'video'
src, err = server.resolve_source('01.As.Lendas.de.uma.nova.era].rmvb',
                                 1432.0, want='video')
check('fallback: unrelated same-length video -> no_match',
      src is None and err == server.T('no_match'),
      'src=%r err=%r' % (src, err))

# now the real file exists at that duration -> resolves
server._lib_durations['/media/Videos/Cav/01.As.Lendas.de.uma.nova.era].rmvb'] = 1432.0
server._lib_kind['/media/Videos/Cav/01.As.Lendas.de.uma.nova.era].rmvb'] = 'video'
src, err = server.resolve_source('01.As.Lendas.de.uma.nova.era].rmvb',
                                 1432.0, want='video')
check('fallback: token-sharing file resolves',
      src == '/media/Videos/Cav/01.As.Lendas.de.uma.nova.era].rmvb',
      'src=%r err=%r' % (src, err))

# --- 3. dual-format stem with mime hint: asf wmv must not get its webm twin
# (regression for the tiebreak that becomes live now that .webm is indexed)
server._lib_durations.clear(); server._lib_kind.clear(); server._lib_by_stem.clear()
for p, dur in (('/m/Aurora.wmv', 30.0), ('/m/Aurora.webm', 31.0)):
    server._lib_durations[p] = dur
    server._lib_kind[p] = 'video'
    server._lib_by_stem.setdefault('aurora', []).append(p)
# both inside the +-3s window; prefer_ext from x-ms-asf must pick the wmv
src, err = server.resolve_source('Aurora', 30.5, want='video',
                                 prefer_ext=server.VID_MIME_EXT.get('video/x-ms-asf'))
check('dual-format: asf hint picks Aurora.wmv', src == '/m/Aurora.wmv',
      'src=%r err=%r' % (src, err))
# webm mime hint must pick the webm twin
src, err = server.resolve_source('Aurora', 30.5, want='video',
                                 prefer_ext=server.VID_MIME_EXT.get('video/x-matroska'))
check('dual-format: matroska hint includes .webm prefer',
      src == '/m/Aurora.webm', 'src=%r err=%r' % (src, err))

# --- 4. duplicate-copy tie still picks first (WMA case regression)
server._lib_durations.clear(); server._lib_kind.clear(); server._lib_by_stem.clear()
for p, dur in (('/m/MPB/02 Querem Meu Sangue.wma', 201.266),
               ('/m/Reggae/02 Querem Meu Sangue.wma', 201.266)):
    server._lib_durations[p] = dur
    server._lib_kind[p] = 'audio'
    server._lib_by_stem.setdefault('02 querem meu sangue', []).append(p)
src, err = server.resolve_source('02 Querem Meu Sangue.wma', 201.0,
                                 want='audio', prefer_ext='.wma')
check('duplicate copies tie -> first (not 404)', src is not None and 'Querem' in src,
      'src=%r err=%r' % (src, err))

print()

# --- 5. no-DIDL-duration resolve: rank by ext hint + tokens (mpg case)
server._lib_ready = True
server._lib_dur_done = True
server._lib_durations.clear(); server._lib_kind.clear(); server._lib_by_stem.clear()
for p2 in ('/m/DreamScene/Autmn Yard.mpg',
           '/m/DreamScene/Mp4/Autmn Yard.webm',
           '/m/DreamScene/Mp4/~Autmn Yard.webm'):
    server._lib_kind[p2] = 'video'
    server._lib_by_stem.setdefault('autmn yard', []).append(p2)
src, err = server.resolve_source('Autmn Yard.mpg', None, want='video',
                                 prefer_ext=('.mpg', '.mpeg', '.vob'))
check('mpg no-duration -> .mpg picked via mime hint',
      src == '/m/DreamScene/Autmn Yard.mpg', 'src=%r err=%r' % (src, err))
src, err = server.resolve_source('Autmn Yard', None, want='video',
                                 prefer_ext=('.mkv', '.mk3d', '.webm'))
check('webm no-duration -> webm twin via mime hint',
      src == '/m/DreamScene/Mp4/Autmn Yard.webm', 'src=%r err=%r' % (src, err))
# artist-tree shape: stripped title, no res (prefer_ext None) -> picks first
server._lib_kind.clear(); server._lib_by_stem.clear(); server._lib_durations.clear()
server._lib_kind['/m/Dream Theater/Lie single/01 - Lie (Edit).mpc'] = 'audio'
server._lib_kind['/m/Dream Theater/compilation/Lie (Edit).mpc'] = 'audio'
server._lib_by_stem['01 - lie (edit)'] = ['/m/Dream Theater/Lie single/01 - Lie (Edit).mpc']
server._lib_by_stem['lie (edit)'] = ['/m/Dream Theater/compilation/Lie (Edit).mpc']
src, err = server.resolve_source('Lie (Edit)', None, want='audio')
check('artist-tree no-res title resolves (not 404)',
      src is not None and 'Lie' in src, 'src=%r err=%r' % (src, err))

print('RESULT:', 'ALL PASS' if not fails else ('%d FAIL: %s' % (len(fails), fails)))
sys.exit(1 if fails else 0)