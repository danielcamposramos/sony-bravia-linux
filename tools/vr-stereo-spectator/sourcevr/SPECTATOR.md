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

## The SourceTV demo bug: director-only SourceTV writes broken demos

Every playback of the SourceTV demos recorded in r04 and r07 stopped at the same point with `Host_Error: CL_PreserveExistingEntity: missing client entity 77`, in 2D and 3D alike and with no VR module loaded at all (r07). Traced with a demo parser ([../sourcetv/](../sourcetv/)), then isolated in r08/r09 (2026-09-28, the same listen server, plain 2D, no module):

| recording | `tv_delay` | `tv_transmitall` | size | entities other than the player |
|---|---|---|---|---|
| r07 | 0 | 0 (default) | 104 MB for 283 s | written as entering in every frame |
| r08 A | 0 | 0 (default) | 64 MB for 172 s | written as entering in every frame |
| r08 C | 5 | 0 (default) | 30 MB for 82 s | written as entering in every frame |
| r08 B | 0 | 1 | 0.5 MB for 76 s | enter once, then updated |
| r08 D | 5 | 1 | 0.5 MB for 87 s | enter once, then updated |

With the default `tv_transmitall 0` (SourceTV culls to the director's view), every entity except the recording's own player (a door, a weapon, each prop: 2,865 times in 2,865 frames of A) is written as entering the client's view in every frame, as if the frame each packet is patched from held only the player: 60 times the data, and playback dies when an entity index is reused by another class (77: a `CBaseAnimating`, later a `CBaseGrenade`). With `tv_transmitall 1` the demo is normal, and r09 played D end to end in the engine, first person included (Daniel). The delay makes no difference. The game's server code (`CServerGameEnts::CheckTransmit`) hands SourceTV every entity; the culling and the demo writing are the engine's (closed), so this is a report to Valve with the workaround, `tv_transmitall 1`. The `Could not find table` lines at the start of every playback appear in the good demos too: harmless (the demo carries all its string tables, `modelprecache` with 313 entries). Not tried: a dedicated server's recording (Source SDK Base 2013 Dedicated Server is not installed here).

Seen on the way: the first `+command` on this launcher's command line gets its argument with a leading space (`+playdemo x` looked for ` x.dem`, `+exec x` for ` x`); harmless when that first argument is a number. The SDK's Linux launcher only moves `-game` to the end, so this is the engine's command-line parsing.

## Not tried yet

- Mapper-placed spectator cameras (`info_observer_point`): the installed map has none (Half-Life 2: Deathmatch's own maps are not installed).
- Valve's own Half-Life 2: Deathmatch from Steam, whose client does not ask for the display interface (the module keeps its own crosshair there, in every view).
- Spectating from a real headset (the display mirroring a headset player's eyes): SteamVR-for-Linux#961, next.
