# Spectating in 3D: SourceTV and the observer cameras

Daniel's design (2026-09-28): the spectator is the 2D game with a second camera. Nothing about a view changes except its second eye, so it works beside what exists: the cameras people already put in levels serve the stereo view too, with no new adaptation, in the same engine and configured the same way as play mode.

That is how Source's VR path is built: the client works out the view first (the player, the observer's in-eye, chase and free cameras, a mapper's `info_observer_point`, SourceTV's director, a scripted `point_viewcontrol`), and the VR path then renders that view as two eyes. What was missing was the game's own rules on top: the module drew a crosshair in every view, where the game shows one in first person and in-eye only.

## The change (fork `stereo3d-full-res-wip`, `151b114`)

- `hud_crosshair.cpp`: on a stereoscopic display the client places its crosshair as in 2D, at the centre where view and aim meet, not through a headset's HUD projection.
- The module hands the crosshair back to any client that asks for its display interface (`SourceVirtualRealityDisplay001`): it restores the player's crosshair setting and stops drawing its own. Clients that never ask (today's Half-Life 2) keep the module's crosshair, unchanged.

There is no standalone spectator program: Source's standalone spectator is SourceTV, which is the same game and the same module. SourceTV sends the game's state, not video, so every viewer's game renders the picture: one broadcast serves 2D and 3D viewers, each in the format they choose, and a future multi-view display (the glasses-free prototypes of 2026) would need more cameras in the viewer's game, not a different broadcast.

## Runs (2026-09-28, native to the KDL-46HX855, RTX 3060)

Bed: Half-Life 2: Deathmatch built from the fork (client, server and `sourcevr.so` `bde1e978`, 64-bit) on Source SDK Base 2013 Multiplayer, `dm_lockdown`, a listen server with SourceTV (`tv_enable 1`, `tv_autorecord 1`, `tv_delay 0`), launched with `-vulkan -vr -stereo3d` (the 64-bit engine loaded the module only with `-vr`).

| run | what | result |
|---|---|---|
| r04 | play in 3D (full top and bottom), `spectate`, observer modes, SourceTV recording, demo playback | Crosshair centred in both eyes (the client's own; the module log: "crosshair: the client's own (display-aware client)"). The spectator's free camera in 3D. Choosing a player with nobody else in the game left the camera stuck (nothing to watch). The SourceTV demo (183 s) showed black and the choose-player screen. |
| r05 | the same demo, module loaded but 3D off (2D) | Plays after a while in black; stops with `Host_Error: CL_PreserveExistingEntity: missing client entity 77`. |
| r06 | the same demo with 3D turned on (from the console, then replayed) | The SourceTV demo plays in 3D (Daniel: "it works"); it stops at the same point as in 2D. |
| r07 | a new SourceTV recording in plain 2D, no `-vr` (the module not loaded), played back in 2D | The same: `Could not find table "modelprecache"` (and every other string table) at the start, then the same Host_Error. Not the stereo. |

## The SourceTV demo bug (for its own pull request, Daniel's call)

Every playback of a SourceTV demo recorded on this listen server starts with `Could not find table` for all of the demo's string tables (`downloadables`, `modelprecache`, `genericprecache`, `soundprecache`, `decalprecache`, `instancebaseline`, `lightstyles`, `userinfo`, ...) and stops at the same point with `Host_Error: CL_PreserveExistingEntity: missing client entity 77`, in 2D and 3D alike, and with no VR module loaded at all (r07). The demo header is complete (demo protocol 3, network protocol 24, 183.1 s, 12,205 ticks, sign-on 222,345 bytes). Daniel's lead: precache, the tables the demo should carry; an entity whose model is not in them can fail to be created, and a later update for it gives exactly this error. The error class is long known in Source demos (e.g. [Source-1-Games#3112](https://github.com/ValveSoftware/Source-1-Games/issues/3112)). Not yet tried: a dedicated server's recording (the usual SourceTV setup; Source SDK Base 2013 Dedicated Server is not installed here).

## Not tried yet

- Mapper-placed spectator cameras (`info_observer_point`): the installed map has none (Half-Life 2: Deathmatch's own maps are not installed).
- Valve's own Half-Life 2: Deathmatch from Steam, whose client does not ask for the display interface (the module keeps its own crosshair there, in every view).
- Spectating from a real headset (the display mirroring a headset player's eyes): SteamVR-for-Linux#961, next.
