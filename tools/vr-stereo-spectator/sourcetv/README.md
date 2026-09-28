# SourceTV demo analysis

`entity_trace.rs` reads a Source SourceTV demo (network protocol 24: Team Fortress 2, Half-Life 2: Deathmatch, the Source SDK 2013 multiplayer games) and reports, per entity, how often it was sent as entering (created), preserved (updated), leaving or deleted, plus any update for an entity the client never created (the condition behind the engine's `Host_Error: CL_PreserveExistingEntity: missing client entity`). With an entity index it lists that entity's every event.

It is a binary for the TF2 community's demo parser, [demostf/parser](https://github.com/demostf/parser) (used here at `e1425a7`); the parser is not part of this repository. Built and run in a throwaway container:

```sh
git clone https://github.com/demostf/parser.git && cd parser
cp /path/to/entity_trace.rs src/bin/
docker run --rm -v "$PWD":/work -w /work -e CARGO_HOME=/work/.cargo rust:latest cargo build --release --bin entity_trace
./target/release/entity_trace demo.dem        # per-entity counts
./target/release/entity_trace demo.dem 77     # every event of entity 77
```

What it showed (2026-09-28, [../sourcevr/SPECTATOR.md](../sourcevr/SPECTATOR.md)): with `tv_transmitall 0` every entity except the recording's player is written as entering in every frame (60 times the data, and playback dies at a reused entity index); with `tv_transmitall 1` each entity enters once and is then updated.
