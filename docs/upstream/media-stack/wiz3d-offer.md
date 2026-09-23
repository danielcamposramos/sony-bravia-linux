# wiz3D — offer of hardware testing on real 3D displays

Target: https://github.com/effcol/wiz3D (LGPL-2.1, active 2026, built on the
MIT-licensed iZ3D source at https://github.com/bo3b/iZ3D)

No AI policy in the repository (the only "AI" string is `immersity.ai`).
Their CONTRIBUTING asks for exactly this: "Game testing" and "Output modes —
test the various stereo output plugins (SBS, anaglyph, interlaced, shutter)",
and says to open an issue before starting anything large.


---

**Title:** Offer: systematic testing of the output modes on real Sony 3D TVs (active shutter)

Hello, and thank you for doing this.

I am one of the people iZ3D mattered to.
In February 2011 I could not afford their monitor, so I wrote to Vadim Asadov with a market-entry idea for Brazil, and he answered honestly and then gave me a full iZ3D All Outputs licence.
That is how I played my first game in stereo.
Seeing his source code kept alive here, under a licence nobody can withdraw, is the best possible outcome for it.

**The offer is hardware.**
Your contributing list asks for testing of the output plugins, and output modes are hard to test because almost nobody still owns working displays of each kind.
I do, and they are all in one room:

- **Two active-shutter 3D televisions**, Sony KDL-46HX855 and KDL-46EX725, both working, both driven from the PC over HDMI. One of them is this machine's main display.
- **The configuration wiz3D exists for**: a GeForce RTX 3060 on Windows 11, driving a 3D television. Modern hardware where 3D Vision is dead and no legacy driver can be installed, which is exactly the case your proxy approach is meant to rescue. Also a Ryzen 5 5600G with its integrated Radeon on the same machine, and 93 GB of RAM. The iGPU is not worth a performance number, but it is a genuine AMD path for correctness testing.
- **Period-correct Nvidia hardware, still owned**: a GTX 970, which is on Nvidia's own 3D Vision compatibility list, and a GTX 550. Both are old enough for a driver branch from when 3D Vision was still supported. These are not needed to test wiz3D, which is the point of wiz3D. They are useful as a **ruler**: a genuine 3D Vision rig to hold your output against when judging whether convergence, separation and the shader fixes behave the way the original did. The 970 currently serves as the GPU in a Linux home server, but the two cards can trade places, so that reference costs a card swap rather than a purchase. If it would genuinely help, I will build it, though not overnight.

**About my time, so nothing here reads as a promise I cannot keep.**
I cannot commit large blocks of it, and I have another project running.
What I can offer reliably is the scarce part: working displays of the kinds this needs, both GPU vendors, the old Nvidia cards, and careful reporting of whatever I do test.
Point me at what is most useful and I will work through it steadily rather than quickly.

So I can cover side-by-side, top-and-bottom and the shutter path on displays that natively expect them, rather than checking that the output "looks right" in a window.
Two honest gaps: I have no working parallax-barrier or lenticular panel, so I cannot speak for the interlaced modes, and I no longer own anaglyph glasses, which matters least since anaglyph is the one mode anybody can check on any screen.

**What I would do with it.**
I document measurements rather than impressions.
My other project is about why correctly authored 3D files play flat on televisions that support 3D: the `frame_packing_arrangement` SEI that displays act on and almost nothing wrote.
That work went upstream and was merged by HandBrake (PR #8100) and Universal Media Server (PR #6330), and it means I already know, in detail, how these particular sets decide to engage 3D and how they refuse.
The same discipline applies here: one variable at a time, the exact build, the exact settings, photographs of the screen where the result is visual, and a plain statement when something does not work.

**Two questions, so I test what is actually useful:**

1. Which output plugins and which build do you want covered first? The status notes say half the HD3D games display correctly in half-TAB and half-SBS and the rest do not, so that list seems the obvious place to start, but you know where the gaps hurt most.
2. You ask for game results as edits to the README tables and a PR. Do you want output-mode results in the same tables, or somewhere separate, since they are a property of the display rather than the game?
3. On the AMD side I have a 5600G's integrated Radeon, which looks close to the 5600U iGPU reported working in #6, so I assume the path is fine. Is there anything specific you want checked there, or is the Radeon side better served by game coverage than by another hardware report?
4. For the 3D Vision work, would a side-by-side comparison against genuine 3D Vision be useful? Your notes say the Automatic Mode games still need convergence and separation wired through to iZ3D and that the shader fixes are not triggering yet, and that is easier to judge against the original behaviour than against a description of it. One question about the reference only, not about wiz3D: the last driver supporting 3D Vision is 425.31, listed by Nvidia for Windows 10, 8.1 and 7, and my Windows installation is 11. If anyone has seen 425.31 run on Windows 11 I will use that, otherwise I will put Windows 10 on the reference machine. My wiz3D testing itself stays on the modern setup, since that is the situation your users are actually in.

One thing you may not have data on, and I can answer: the 3D televisions of this generation accept stereo over HDMI in two different ways, an automatic path and a manual one, and which of them a given output mode lands on is not obvious from the PC side. If that is useful to you, I will write it up properly.

**One measurement you may find useful, since it is the gap wiz3D sits in.**
Both operating systems can already see that this television does 3D, and neither offers any way to use it on the desktop.
Reading the EDID over the live HDMI link on Linux, the set's HDMI vendor block declares `3D present`, a 3D-capable VIC mask, side-by-side (half) and top-and-bottom, and frame packing on specific VICs including 1080i at 50 and 60 Hz and 1080p24.
Windows detects the same capability from the same cable.
Neither one exposes a switch, a mode or a checkbox that turns it on for anything, so the capability is advertised by the display, parsed by the operating system and then dropped on the floor.
There is no desktop path to stereo left on either platform, which is exactly why a wrapper like this is the only route back in.

**Two suggestions, both about reach rather than code.**

*Proton.* I see #6 already has people running wiz3D under Proton, one of them on a Steam Deck, and that you fixed the HD3D path for Proton systems in 0.2.0. I would treat that as a headline feature rather than a compatibility footnote. Valve has spent years making Proton the way Windows games run on Linux, and it is the one route where stereo can reach a broad audience without asking anyone to keep an old Windows install alive. On my side that also means the same games can be tested through Proton and native Windows on the same machine, with the same GPU and the same television, which isolates the wrapper from the platform.

*Steam Frame.* Valve's standalone SteamOS headset shipped on 14 September 2026, runs Proton and streams from a PC over its own wireless adapter. That makes a headset a plain output target for a wrapper that already produces side-by-side, and I notice VR output came up in #19 as roadmap. A stereo wrapper whose output can land on a 3D television, a 3D projector or a Steam Frame, through Proton on Linux or natively on Windows, covers essentially every way anyone can still watch stereo.

I also maintain a public list of stereoscopic material, and wiz3D is in it, together with the iZ3D source release and Vadim's name, because that lineage deserves to be recorded: https://github.com/danielcamposramos/awesome-stereoscopy
