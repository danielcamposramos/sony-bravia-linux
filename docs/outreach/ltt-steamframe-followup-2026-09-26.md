<!-- POSTED 2026-09-26 by Daniel, as a follow-up to his own comment
     16936512 on the Steam Frame review thread:
     https://linustechtips.com/topic/1642726-the-steam-frame-changes-everything-full-review/
     Comment: findComment-16938900
     https://linustechtips.com/topic/1642726-the-steam-frame-changes-everything-full-review/?do=findComment&comment=16938900
     Same day, Daniel sent Luke a short forum DM pointing at this comment
     (the DM's text stays private).
     Mentions Luke (forum handle Slick, picked from the forum's autocomplete).
     Timing: posted once, now, while the thread was still alive (quiet since
     2026-09-21); the source-sdk-2013 pull request goes to Valve's own
     trackers (#8297, #961), not to a second LTT post.
     The text below is the draft as proposed; Daniel posts in his own words,
     so the posted text may differ. -->

Pinging @Slick, since this one is VR and 3D together.

Follow-up to my comment above, because two things moved.

The movie side is now closed end to end: mpv merged reading the 3D signal from the stream on 2026-09-23. HandBrake writes it, MKVToolNix tags from it, mpv plays from it, Universal Media Server serves it. Four merges, all stock free software.

The game side is the new part, and it answers the same "so little 3D content" point from ~21:10. Valve already built a stereo renderer into its own engine: Source games from the 2013 SteamVR era still carry the VR render path. With a replacement VR module, Half-Life 2 renders both eyes with real stereo geometry into a frame a 3D TV unpacks, top and bottom or side by side, with a 3D section added to the game's options menu. It runs natively on Linux (RTX 3060 here), and I have been playing it on a 2012 Sony 3D TV. Through gamescope the same game also goes to red/cyan anaglyph, for any screen.

The Steam Frame connection is an idea, not a shipped thing: a stereo spectator mode. Someone plays in the headset, and the game's window on the PC, today a flat mirror, shows the two eyes in stereo on a 3D TV, so the room watches in 3D too. I asked Valve for it here: https://github.com/ValveSoftware/SteamVR-for-Linux/issues/961

The Half-Life 2 report to Valve: https://github.com/ValveSoftware/Source-1-Games/issues/8297
A gamescope fix that came out of it (a frame race in the nested output, which showed up as swimming depth): https://github.com/ValveSoftware/gamescope/pull/2438
The module and how it works: https://github.com/danielcamposramos/sony-bravia-linux/tree/main/tools/vr-stereo-spectator
