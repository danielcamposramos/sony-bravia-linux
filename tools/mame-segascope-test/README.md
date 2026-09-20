# Testing the SegaScope half-SBS layout on the 2011/2012 BRAVIA sets

**Purpose: produce data for [MAME #3492](https://github.com/mamedev/mame/issues/3492),
which has been open since April 2018.** Its author wrote this layout and verified it on
a single Sony HDTV. We hold two characterised sets from a generation whose EDID we have
measured. Testing it on those is something nobody in that thread can do, and it is the
only thing worth saying there.

Nothing goes to MAME before this is run. An opinion on a seven-year-old issue is noise;
a result on two more displays is not.

## What is here

`sms1.lay` — the author's layout, reproduced verbatim so that what we test is what he
proposed. It is his work and the file says so.

## What we have

- MAME 0.289, packaged, on the workstation
- All seven SegaScope 3-D titles, in `roms/mastersystem`: Blade Eagle 3D, Maze Hunter
  3-D, Missile Defense 3-D, Out Run 3-D, Poseidon Wars 3-D, Space Harrier 3D, Zaxxon 3D,
  several with Brazilian releases
- KDL-46EX725 (AZ2-F, 2011) and KDL-46HX855 (AZ3F, 2012), both measured, both declaring
  `3D present` with SBS-half, top-and-bottom and frame-packing VICs in their EDID
- `subroc3d` in the MAME set, Sega's 1982 arcade stereo cabinet, as a second and quite
  different case if the first one works

## The procedure

1. Put `sms1.lay` where MAME will find it as artwork for the `sms1` driver.
2. Start a 3-D title on the `sms1` driver.
3. In machine configuration, set **SegaScope (3-D Glasses)** to *On* and **SegaScope -
   Binocular Hack** to *Both Lens*. Without both, there is nothing for the layout to
   arrange.
4. Select the **SegaScope 3-D Glasses (3DTV H-SBS)** view.
5. Output to the television and switch it to side-by-side by hand.

## What to record, and it is the whole point

- Whether the view renders correctly on each set, with a photograph
- **Whether the television engages 3D on its own, which it will not.** This is the
  finding that connects to the rest of this project: the pixels are correctly packed
  and nothing tells the set what they are, so a human presses a button. Over HDMI the
  missing piece is the 3D InfoFrame, exactly as the frame-packing SEI is the missing
  piece in a file.
- Whether the result differs between the 2011 and 2012 sets
- Which titles were tried and whether any behaves differently
- The MAME version, so the report is reproducible

## Then, and only then

MAME's policy on this is the most permissive of the three projects surveyed and is
explicitly non-punitive: assistance "will not be used to reject a pull request or a
change out-of-hand, however it must be mentioned so that additional scrutiny can be
given", and it asks for the model and version used. Disclose that, and name the harness
too, which is more than is asked for.

The comment should report the measurement and nothing else. The open question in that
thread is whether a 3D-television view belongs in the tree or in external artwork, and
that is theirs to decide, not ours to argue.
