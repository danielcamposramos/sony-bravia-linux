# Emulator stereo: targets, true states, and what we could actually add

**Recorded 2026-09-20.** A survey of which emulators output stereoscopic 3D, done for
the awesome-stereoscopy list, turned up a small set of upstream threads. This file
records their real states, because a first pass got three of four wrong, and separates
what is worth acting on from what is not.

## The distinction that runs through all of it

Two unrelated problems get the same name.

**Where the console really had stereo**, the emulator is preserving data that already
exists: the Virtual Boy drove two displays, the Famicom 3D System and SegaScope
alternated frames to shuttered glasses, the 3DS had a depth slider. Nothing is
rendered twice; the two views are in the content.

**Where the console never had stereo**, the emulator renders the existing 3D scene
from a second camera. This is the driver era aimed at a console, and it is only
possible because there is a scene to ask again.

Worth stating plainly because a common objection confuses them: producing stereo from
a 3D game does **not** require two scenes or duplicated geometry. It requires one
scene and two camera positions. Vulkan multiview draws both eyes in a single pass and
is an optimisation, not a precondition; rendering twice sequentially has always
worked. The reference implementation is public and MIT licensed, since iZ3D's source
was released ([bo3b/iZ3D](https://github.com/bo3b/iZ3D), modernised as
[effcol/wiz3D](https://github.com/effcol/wiz3D)).

That argument applies to PCSX2 and Dolphin-class emulators. It does **not** apply to
2D consoles, where there is no scene and no camera, and where the only route is the
one 3dSen takes: a person authoring volume per game by hand.

## True states, checked by API 2026-09-20

| Thread | State | What it actually says |
|---|---|---|
| [MAME #3492](https://github.com/mamedev/mame/issues/3492) | **open** since 2018-04-27 | A half-SBS layout for SegaScope on 3D televisions, tested by its author on one Sony set. A reply argues it belongs in external artwork rather than mainline, and objects that the SMS driver models the glasses as three physical screens when they are electronic shutters. The author concedes the layout rides an existing kludge. |
| [RPCS3 #13059](https://github.com/RPCS3/rpcs3/issues/13059) | closed **completed** 2023-04-07 | Side-by-side was implemented. Anaglyph came first in 2020. Nothing outstanding. |
| [Nestopia #155](https://github.com/0ldsk00l/nestopia/issues/155) | closed 2016-01-09 | Famicom 3D System. Revived in 2019 and the maintainer's reply is the useful part: doing it properly "would require a Vulkan renderer with multi-viewport capability". That was answering a VR-headset suggestion, not the accessory itself. He also rebuked the necro explicitly. |
| [PCSX2 #1461](https://github.com/pcsx2/pcsx2/issues/1461) | closed 2022-05-29 | Ran six years. Its substance is the stereo driver's own constraints of the era, including Direct3D 11 titles being unable to work in windowed mode. |

## What is worth doing

**Only MAME #3492 is live, and the contribution is a test rather than an opinion.** Its
author verified on a single Sony HDTV. We hold two characterised sets from the
2011-2012 generation with measured EDID declaring SBS-half, top-and-bottom and frame
packing. Running that layout on both and reporting what happens is data nobody in the
thread has. Until it is run there is nothing to say that would not be noise on a
seven-year-old issue.

**Do not comment on the three closed threads.** The Nestopia thread contains a
maintainer telling someone off by name for reviving a closed issue and adding nothing.
Doing that ourselves, on that issue, would be both rude and a demonstration of exactly
what people fear about assisted contributors.

**The iZ3D prior art goes where someone is building.** wiz3D is active and the owner
already intends to contribute there. A correction posted onto dead threads helps
nobody; the same knowledge offered to a live project is worth something.

## The observation that ties back to this project

Every emulator above emits correctly packed stereo and none of them tells the display
what it is sending. Owner-confirmed on a TVE T10 running the Virtual Boy core with
side-by-side output: both BRAVIA sets showed it in real stereo, and only after 3D was
enabled by hand on the television. The content was stereo, the packing was right, the
set advertises the format in its own EDID, and the user still pressed a button.

That is the frame-packing problem one layer down, with the HDMI 3D InfoFrame in place
of the H.264 SEI. Recorded with its uncertainties in
`sparky-armbian/05_board_tve_t10/evidence/virtualboy-stereo-on-bravia-20260920-t10/`.

## The plan, agreed 2026-09-20 and NOT yet executed

Owner's direction: rather than reviving dead threads, open a new focused issue per
project, built on that project's own code, referencing the old thread so its
subscribers are notified without anyone being necroed. Brief, objective, spec-based.
Disclose the assistance as always, and offer a patch rather than a request.

**Use the cross-reference, not a comment.** Mentioning `#1461` in a new issue creates a
backlink in the closed thread automatically. The people who subscribed get notified,
the dead thread gains no comment, and the etiquette objection never arises. This is the
mechanism that makes the whole plan safe.

### The argument, in the order it should be made

1. **Stereo from a 3D game is one scene and two cameras.** Not two scenes, not
   duplicated geometry. Two view matrices offset along the camera's right vector, plus
   a convergence setting that decides where zero parallax sits. Separation without
   convergence gives depth that is either painful or invisible depending on scene
   scale, which is why both are exposed wherever this is done properly.
2. **It is driver independent, and a sibling project proves it.** Dolphin implements
   stereoscopy inside the emulator and outputs side by side or top and bottom to any
   display that accepts a packed pair. Only its quad-buffered "HDMI 3D" mode needs
   driver cooperation, and that mode is optional. This matters most for PCSX2, whose
   thread ran six years on Direct3D 11 and 3D Vision constraints when the answer was
   to stop involving the driver.
3. **The reference implementation is public.** iZ3D's source is MIT
   ([bo3b/iZ3D](https://github.com/bo3b/iZ3D)) and is being modernised as
   [effcol/wiz3D](https://github.com/effcol/wiz3D). Nobody has to take the geometry on
   trust.
4. **Scope honestly.** This applies to emulators with a real 3D scene. It does not
   apply to 2D consoles, where there is no camera and the only route is per-game
   authoring by hand, as 3dSen does.

### Before anything is sent

- **MAME #3492 needs the test first.** We hold two characterised sets; its author had
  one. Run the layout, report what happens, and only then discuss whether it belongs in
  the tree. No opinion before the measurement, exactly as with mkvtoolnix.
- **Check capacity before offering a patch.** Offering and then not delivering costs
  more than never offering. PCSX2's renderer is substantial C++, and the honest
  question is whether this can be built and tested here, not whether it is desirable.
- **Check whether the old third-party patch survives** and what it did, so the offer
  builds on existing work rather than ignoring it.
- **Read each project's contribution policy first**, as with every other target in this
  campaign.

Status: planned, nothing sent, on the owner's explicit instruction.

## The PlayStation 3 is the existence proof, and it changes the argument

**Owner-confirmed, tested with a friend's console on a game with native 3D output.**
The set engaged 3D by itself. No button, no menu.

Firmware **3.30** gave every PS3 two of the 3D video modes defined by HDMI 1.4:
1920x1080p at 24 Hz and 1280x720p at 60 Hz, frame packed. The console declares the
format and the television obeys. That matches what these sets advertise in their own
EDID, measured separately in this project: `3D present`, SBS-half, top-and-bottom and
frame-packing VICs.

So the conclusion is not that this generation of television is awkward. **A console
from 2010 signalled 3D to these exact sets correctly, and nothing on a PC in 2026
does.** The display end has been ready the entire time. What is missing is on the
source side, and that is a software gap rather than a hardware one.

This is the strongest single argument the campaign has for the HDMI half of the
problem, and it should be stated with the firmware version and the two video modes
attached, because it is checkable by anyone who still owns a PS3.

## Two classes of 3D content, which must not be conflated

The owner's distinction, and it decides what any given project is even being asked for:

**Native 3D.** The game itself renders both eyes. It knows it is stereoscopic, the
separation and convergence are the developer's choices, and the console's job is only
to package and announce the result. PS3 titles with 3D support work this way, and
there is no official Sony list of them; the community maintains one at
[ConsoleMods](https://consolemods.org/wiki/PS3:Games_with_Stereoscopic_3D_Support).

**Everything else**, which needs a second viewpoint produced for it. This is the
driver era's trick, one scene rendered from two cameras, and it is what Dolphin does
for consoles that never had stereo at all.

**Why it matters for RPCS3 specifically.** Emulating a natively-3D PS3 title is the
first class, not the second: the game produces both views, so the emulator is
preserving stereo rather than inventing it. Its anaglyph support in 2020 and
side-by-side in 2023 are output plumbing for content that already exists. Asking
RPCS3 to add stereo to non-3D PS3 games would be the second class and a completely
different request, and should never be phrased as though it were the same one.
