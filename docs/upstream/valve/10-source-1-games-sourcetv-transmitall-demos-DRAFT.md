# DRAFT (not posted): SourceTV with tv_transmitall 0 writes demos that re-create every entity each frame

Target: ValveSoftware/Source-1-Games (a new issue). Raw material for Daniel to post in his own words; not posted.

---

**SourceTV demos recorded with `tv_transmitall 0` (the default) write every non-player entity as entering the view in every frame, and playback dies with `CL_PreserveExistingEntity: missing client entity`**

Recorded on a listen server with SourceTV (Half-Life 2: Deathmatch built from the current source-sdk-2013 on Source SDK Base 2013 Multiplayer, Linux, 64-bit, `dm_lockdown`, `tv_enable 1`, `tv_autorecord 1`), then played back with `playdemo`.

Playback of the default recording stops at the same point every time, with:

```
Host_Error: CL_PreserveExistingEntity: missing client entity 77.
```

Same result with no VR module loaded and nothing but the stock game.

Parsed with a demo parser (per entity: entering, updated, leaving, deleted), four recordings of the same session:

| `tv_delay` | `tv_transmitall` | size | entities other than the recording's player |
|---|---|---|---|
| 0 | 0 (default) | 64 MB for 172 s | written as entering the view in every frame |
| 5 | 0 (default) | 30 MB for 82 s | written as entering the view in every frame |
| 0 | 1 | 0.5 MB for 76 s | enter once, then updated |
| 5 | 1 | 0.5 MB for 87 s | enter once, then updated |

With `tv_transmitall 0` a door, a weapon and every physics prop are each sent as entering in all 2,865 frames of a 172 s recording; only the recording's own player is delta-updated normally. That is 60 times the data, and playback fails when an entity index is reused by another class (here 77: a `CBaseAnimating`, later a `CBaseGrenade`). With `tv_transmitall 1` the demo is normal and plays end to end, first-person spectating included. The delay makes no difference.

The game side (`CServerGameEnts::CheckTransmit`) hands SourceTV every entity, as intended; the culling to the director's view and the demo writing are in the engine, so this looks like the engine's delta reference for culled SourceTV frames. Not tried: a dedicated server.

Workaround: `tv_transmitall 1`.

The parser binary (`entity_trace.rs`, for demostf/parser) and the full notes: https://github.com/danielcamposramos/sony-bravia-linux/tree/main/tools/vr-stereo-spectator/sourcetv

---

Notes for Daniel (not for posting):
- Found while testing the stereo spectator (SourceTV demos in 3D); the bug is in 2D too, which is why it gets its own issue, not the 3D pull request.
- AI disclosure: once, in the form the repository uses, if you mention it.
