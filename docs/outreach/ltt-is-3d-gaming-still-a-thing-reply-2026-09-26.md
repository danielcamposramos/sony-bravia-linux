<!-- POSTED 2026-09-26 by Daniel on the LTT thread "Is 3D gaming still a thing?":
     findComment-16938907
     https://linustechtips.com/topic/1616265-is-3d-gaming-still-a-thing/?do=findComment&comment=16938907
     Every participant answered on their own point (Kilrah and danalog only
     agreed with Hinjima, so they share his line); then the five public
     links. The text below is the draft as proposed; Daniel posts in his own
     words, so the posted text may differ. -->

@james8449834 yes, it still is, and on a 3D projector or TV it is easier than it was: side by side needs no special sync, and unlike 3D Vision it does not need a constant frame rate, because both eyes travel in every frame. The "wiggle that forces side by side" you asked about exists, several times over, all free: Half-Life 2 renders real stereo through Valve's own VR path straight to a 3D TV or projector (my work, native Linux, links below); Depth3D builds the second eye inside ReShade for the games ReShade can hook; wiz3D, the open continuation of iZ3D's driver, covers DirectX 7 to 11 and OpenGL; and Dolphin does it for GameCube and Wii. Your projector's 3D input takes side by side or top and bottom over HDMI, so any of them should work on it.
@Hinjima @Kilrah @danalog VR took the headset half, but the TV half never left, and the two can meet: I have asked Valve for a stereo spectator mode, where the room watches the headset player's game in 3D on the TV (SteamVR-for-Linux #961).
@RockstarArthur Luke Ross's mods are the headset route, and they are demanding. The TV route is lighter: in my runs Half-Life 2 in 3D side by side does about 380 fps on an RTX 3060 at 1080p, against 585 in 2D.
@LogicalDrm niche, agreed, but PC 3D was real: Nvidia 3D Vision, AMD HD3D, iZ3D and TriDef drivers covered hundreds of games from 2008 until Nvidia dropped 3D Vision in 2019. The driver era has its own section in awesome-stereoscopy, including Tom's Hardware's 18-game test from 2011. I played Max Payne in anaglyph on iZ3D's driver back then, and iZ3D lives on, open source, as wiz3D.
@Pusbucket the Odyssey 3D is in the list's glasses-free displays. Since it takes any side-by-side source, the output here should work on it too (untested; I do not have one).
@Johan Smolinski your worry about the SDK is the right one: this technology lives or dies on open tools. Side by side is the one format nobody can pull back, which is why everything here outputs the standard frame-compatible formats, and your stereo vacation photos are exactly the kind of content awesome-stereoscopy is for.
@Mark Kaine you nailed why: back then almost everything supported 3D because a game is already 3D, and one more camera is all it takes. Source proves it: its VR path renders any Half-Life 2 level in stereo, no special content, and I play it that way on a 3D TV.

What I built, all public:
Consumer Rights Wiki (the Sony case): https://consumerrights.wiki/w/Sony_BRAVIA_pre-Android_Linux_TVs_(2011-2012)
The project (3D movies over the network, Half-Life 2 in 3D, the tools): https://github.com/danielcamposramos/sony-bravia-linux
awesome-stereoscopy (history, formats, displays, players): https://github.com/danielcamposramos/awesome-stereoscopy
awesome-vr: https://github.com/danielcamposramos/awesome-vr
awesome-ar: https://github.com/danielcamposramos/awesome-ar
