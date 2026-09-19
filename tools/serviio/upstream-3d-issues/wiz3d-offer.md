# wiz3D — offer of hardware testing on real 3D displays

Target: https://github.com/effcol/wiz3D (LGPL-2.1, active 2026, built on the
MIT-licensed iZ3D source at https://github.com/bo3b/iZ3D)

No AI policy in the repository (the only "AI" string is `immersity.ai`).
Their CONTRIBUTING asks for exactly this: "Game testing" and "Output modes —
test the various stereo output plugins (SBS, anaglyph, interlaced, shutter)",
and says to open an issue before starting anything large.

Owner fills in the GPU models before posting.

---

**Title:** Offer: systematic testing of the output modes on real 3D displays (shutter TV, parallax barrier, glasses-free tablet, anaglyph)

Hello, and thank you for doing this.

I am one of the people iZ3D mattered to.
In February 2011 I could not afford their monitor, so I wrote to Vadim Asadov with a market-entry idea for Brazil, and he answered honestly and then gave me a full iZ3D All Outputs licence.
That is how I played my first game in stereo.
Seeing his source code kept alive here, under a licence nobody can withdraw, is the best possible outcome for it.

**The offer is hardware.**
Your contributing list asks for testing of the output plugins, and output modes are hard to test because almost nobody still owns working displays of each kind.
I do, and they are all in one room:

- **Two active-shutter 3D televisions**, Sony KDL-46HX855 and KDL-46EX725, both working, both driven from the PC over HDMI. One of them is this machine's main display.
- **Anaglyph**, on anything, including material authored for CRT phosphors.
- **Both vendors on one machine**: a Ryzen 5 5600G with its integrated Radeon, and a GeForce RTX 3060, 93 GB of RAM. The iGPU is not worth a performance number, but it is a genuine AMD path for correctness testing, and the 3060 covers the Nvidia side.

So I can cover side-by-side, top-and-bottom, shutter and anaglyph on displays that natively expect them, rather than checking that the output "looks right" in a window.
I do not have a working parallax-barrier or lenticular panel to offer, so I cannot speak for the interlaced modes.

**What I would do with it.**
I document measurements rather than impressions.
My other project is about why correctly authored 3D files play flat on televisions that support 3D: the `frame_packing_arrangement` SEI that displays act on and almost nothing wrote.
That work went upstream and was merged by HandBrake (PR #8100) and Universal Media Server (PR #6330), and it means I already know, in detail, how these particular sets decide to engage 3D and how they refuse.
The same discipline applies here: one variable at a time, the exact build, the exact settings, photographs of the screen where the result is visual, and a plain statement when something does not work.

**Two questions, so I test what is actually useful:**

1. Which output plugins and which build do you want covered first? The status notes say half the HD3D games display correctly in half-TAB and half-SBS and the rest do not, so that list seems the obvious place to start, but you know where the gaps hurt most.
2. You ask for game results as edits to the README tables and a PR. Do you want output-mode results in the same tables, or somewhere separate, since they are a property of the display rather than the game?
3. Does the HD3D path still initialise on a current Radeon with current drivers, or does that side need a card of the HD 5000/6000 era that the API was built for? My AMD side is a 5600G's integrated Radeon, so if HD3D needs period hardware I would rather know before reporting a failure that is really just the wrong card.

One thing you may not have data on, and I can answer: the 3D televisions of this generation accept stereo over HDMI in two different ways, an automatic path and a manual one, and which of them a given output mode lands on is not obvious from the PC side. If that is useful to you, I will write it up properly.

I also maintain a public list of stereoscopic material, and wiz3D is in it, together with the iZ3D source release and Vadim's name, because that lineage deserves to be recorded: https://github.com/danielcamposramos/awesome-stereoscopy
