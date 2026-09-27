<!-- POSTED 2026-09-26 by Daniel on LTT's own video thread "The Demise of
     3DTV - The Hype Machine's Biggest Mistake":
     findComment-16938905
     https://linustechtips.com/topic/1431094-the-demise-of-3dtv-the-hype-machines-biggest-mistake/?do=findComment&comment=16938905
     Every participant (pages 1 and 2, 29 people) answered on their own
     point, one line each, fans and sceptics alike; then the five public
     links. The text below is the draft as proposed; Daniel posts in his own
     words, so the posted text may differ. -->

@AdamFromLTT four years later, an answer to the video's question from someone who never stopped using 3D: two Sony 3D TVs from 2011 and 2012, still in daily use. Home 3D did not die of bad hardware. It was stranded: the sets still work, and what broke was software, one missing signal inside the files, and support. Most of that is fixable now, on free software. One line for each of you, since this thread covers every angle of it.

@Quackers101 the ReShade route you linked is where the anaglyph end of my chain lives too (a ReShade effect inside gamescope), and your light-field and XR links have a home in awesome-vr and awesome-ar.
@Rellik66 that per-eye split is exactly what a 3D TV does with side by side. The next step I have asked Valve for is the other direction: a headset player's two eyes shown in stereo on the room's 3D TV (a stereo spectator mode, SteamVR-for-Linux #961).
@Uttamattamakin what you saw in Titanic was a hand-tuned conversion (IRMacGuyver explains it below). A game engine gives real stereo for free, and that is what Half-Life 2 now shows on a 3D TV, through Valve's own VR render path.
@Vishera HD3D footage is history worth keeping, and AMD's side of HDMI 3D on Linux is moving again: the amdgpu HDMI 1.4 3D patch series on the kernel lists passes frame packing, side by side and top and bottom on my Sony (I sent the test report).
@iLikeBananas @Lightwreather Despicable Me 2 it is. Like any 3D rip, it plays flat over the network on a 3D TV unless the file carries the frame-packing flag; HandBrake, MKVToolNix and mpv now handle that flag.
@GodAtum fair on the hype, but unlike a smart oven, the 3D part never needed the cloud. The smart features are what died, and the 3D kept working.
@kokosnh no loud intro in this one, promise.
@Error 52 your Panasonic story is my Sony story: the smart side went useless, the panel is still great. I documented Sony's own end-of-service notices on the Consumer Rights Wiki (link below). And not everyone's eyes take to 3D equally, which is why awesome-stereoscopy has a whole section on who can see it and who cannot.
@NimbusEntry as a VR researcher you may like the other direction: the stereo spectator idea above, and my write-up of what it takes to bring a VR engine's eyes to a 3D display. Bigscreen and the other players are in awesome-vr.
@Thaldor agreed that content is the wall, but a big part of it is not DRM, it is signalling: 3D files people already own play flat on 3D TVs because one flag inside the video is missing. The explainer is in the project below.
@05032-Mendicant-Bias the hype comparison is fair. The difference is that 3D TVs are already in living rooms, paid for, and the fixes here cost their owners nothing.
@timdine Dolphin's stereo is one of the clearest worked examples in awesome-stereoscopy's emulator section, and a 3D TV in side by side is exactly its target. Half-Life 2 is couch 3D on a TV now too.
@WaggyOnline cross-eyed viewing is the one 3D display nobody can take away from you; the list has tools that build cross-eye pairs. And thanks for answering the Super Stardust HD question.
@Kano3D you are why the photo side matters: MPO stereo photos engage 3D from USB on my Sonys, and the Lume Pad and the other glasses-free devices are in the list.
@IRMacGuyver your projectionist knowledge is exactly what gets lost. Creature from the Black Lagoon is already in the list's cinema history, and its contribution lane is open: your red-green print would be welcome there as an issue, with whatever record of it exists.
@Middcore fair enough, 3D is not for everyone, and it never has to be on: everything here is one menu switch away from 2D.
@silentdragon95 3D Vision's end stranded a lot of people with good hardware. On Linux an NVIDIA card now runs Half-Life 2 in real stereo through the engine itself, no driver hack (mine is an RTX 3060).
@abit-sean your LG 3D OLED is exactly the target: it unpacks side by side and top and bottom over HDMI like my Sonys, so Half-Life 2 in 3D should work on it today.
@Stahlmann in my experience much of 3D's headache reputation came from converted films and tiny parallax barriers; an engine rendering true geometry at a sane depth is a different experience.
@DonCarlos an E6 with an OPPO 203 is a reference setup, and I think you are right that 3D will be back. Meanwhile your E6 should take Half-Life 2 in 3D from a PC today.
@aka the gamer WaggyOnline found it: Super Stardust HD.
@Kid.Lazer flicker is why passive screens exist; the build has a row-interleaved output for them, still untested on a real passive screen.
@BlubberLord you would like what a game engine does: every frame is native stereo from two real virtual cameras, no conversion, and I play it on active-shutter Sonys.
@Northstorm a 120-year-old Perfecscope and the PlayStation display's split-screen mode in one post is the whole arc of awesome-stereoscopy's history section.
@supertouring @Marzzel @Eboy the TV in the video is LG's 2016 OLED Signature G6. Sony and LG both dropped 3D in January 2017, so the 2016 OLEDs (C6, E6, G6) were the last with it; the newer Signature models have none, which is why Google says no.

What I built, all public:
Consumer Rights Wiki (the Sony case): https://consumerrights.wiki/w/Sony_BRAVIA_pre-Android_Linux_TVs_(2011-2012)
The project (3D movies over the network, Half-Life 2 in 3D, the tools): https://github.com/danielcamposramos/sony-bravia-linux
awesome-stereoscopy (history, formats, displays, players): https://github.com/danielcamposramos/awesome-stereoscopy
awesome-vr: https://github.com/danielcamposramos/awesome-vr
awesome-ar: https://github.com/danielcamposramos/awesome-ar
The lists take contributions, and this thread alone holds enough knowledge for a few entries.
