# Draft comment for mamedev/mame#3492 — for Daniel's review before posting

Status: APPROVED by Daniel 2026-09-20, awaiting posting. Issue is open, created 2018-04-27 by darkfalz79, last activity 2021-02-05, labels `driver` + `artwork`, 3 comments.

---

Apologies for adding to a thread this old. I would not have, except that it is still open and still carries both the driver and the artwork labels, which reads as parked rather than settled, and what follows bears directly on what happens to this layout if the driver is ever reworked. If it should simply be closed, say so and I will not press it.

Confirming darkfalz79's layout still works, unmodified, on current MAME and on a different stack from his.

Tested on MAME 0.289 on Linux with the OpenGL renderer, driver `sms1`, on a Sony KDL-46HX855, a 2012 active-shutter set on Sony's AZ3F chassis (SEGM 3A-G). The recipe is exactly the one in the first post and nothing needed changing: SegaScope (3-D Glasses) set to On in Machine Configuration, SegaScope - Binocular Hack set to Both Lens, the layout's H-SBS view selected, and the television switched to Side by Side by hand. Maze Hunter 3-D gives clean, comfortable separation. Seven years and a lot of driver churn later, the behaviour the layout depends on is intact.

For anyone else trying this on the same hardware generation, these sets are built by chassis rather than by model number, so the siblings matter more than the badge. The AZ2-F chassis (SEGM.3A-2) covers KDL-32EX725, KDL-40EX725, KDL-46EX725 and KDL-55EX725 under one service manual, with a separate schematic for KDL-60EX725. The set tested here is the AZ3F one; we have only the KDL-46HX855 manual in hand and have not documented which other sizes that chassis covers.

On hap's objection, which we think is right and worth engaging rather than working around.

Modelling the glasses as electronic shutters instead of three physical screens is clearly more faithful, and tceptor2.lay is a good illustration of the pattern. But that pattern does not survive being pointed at a 3D television, and it is worth saying why before the SMS driver is reworked. In tceptor2.lay the same screen is drawn twice and each copy is covered by a shutter element driven from `tceptor2_shutter_w`, so exactly one of the two halves is black at any instant. That is correct for free-viewing and for real shutter glasses, where persistence of vision does the work. A 3D television in Side by Side mode does not work that way: it samples whole frames and expects both halves to carry an image in the same frame. Fed alternating halves, it gets a half-black frame every time.

What makes the current SMS path work for a television is specifically the binocular hack. In `screen_update_left` and `screen_update_right`, a lens that would otherwise blank instead does `copybitmap` from `m_prevleft_bitmap` or `m_prevright_bitmap`, so each lens holds its own eye's most recent frame. Both halves therefore carry content simultaneously, which is a genuine stereo pair rather than an alternation. The layout is only arranging what that frame-hold already produces.

So the request is narrow: if and when the driver moves to a shutter-accurate model, please keep an equivalent per-lens frame-hold available, even as an option. Without it there is no way to get a Master System 3-D title onto a 3D display at all, and with it both the accurate model and the television path can coexist.

One thing that is not MAME's problem, noted here so nobody files it as one. The television cannot switch itself into Side by Side, and never will from this path, because the HDMI 3D signalling lives in a Vendor Specific InfoFrame that an application cannot emit under X11 or Wayland. The set advertises the capability plainly in its EDID (3D present, Side-by-side half horizontal, Top-and-bottom, plus frame packing on several VICs) and the Linux kernel has carried `DRM_MODE_FLAG_3D_SIDE_BY_SIDE_HALF` and `DRM_CLIENT_CAP_STEREO_3D` for over a decade, but nothing in the desktop stack asks for them. That gap belongs to SDL and the compositors, and we are pursuing it separately.

Two offers, take either or neither.

We have working 2011 and 2012 active-shutter BRAVIAs here and are happy to test any rework of this driver on real 3D hardware, which seems to be the scarce resource in this area. And if the layout is still considered external artwork material rather than something to ship, we can prepare and submit it to Mr Do's collection as suggested in 2018, with darkfalz79 credited as the author, if he has not already done so.

Context for why we are in this corner of the tracker at all: we maintain a list of stereoscopic tooling and history at https://github.com/danielcamposramos/awesome-stereoscopy, and a right-to-repair project for these specific sets at https://github.com/danielcamposramos/sony-bravia-linux, where the test kit and full measurements for the above live under `tools/mame-segascope-test/`.

Disclosure: this comment was researched and drafted with AI assistance, Claude Opus 5 in the Claude Code harness, then reviewed and posted by me. The measurements are from my own hardware and I can answer for every claim in it.
