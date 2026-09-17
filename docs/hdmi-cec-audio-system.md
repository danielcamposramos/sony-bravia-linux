# The HDMI-CEC audio-system lane

**Recorded 2026-09-17. Not a current target** — written down because the
material was recovered while fixing something else, and because it will
be expensive to re-derive if it is ever wanted.

## What was recovered

The `SNY_AudioControlApp` / `SNY_AudioControl` bundles are not simple
volume widgets. They are a **complete remote for a Sony audio system,
driven over raw HDMI-CEC vendor commands**, and they carry two things
worth keeping:

1. **26 distinct Sony vendor CEC opcodes** (`0xF000`–`0xF21F`) with
   their request/response handling, in `common/ceccommandcontrol.js` —
   `giveAudioSetting`, `giveSpeakerConfigration`, `giveSpeakerLevelSetting`,
   `giveSoundEffectSetting`, `giveToneSetting`, `giveSndCustomSetting`,
   `giveModelInfo`, `giveStatus`, `setAudioModeOn`, plus the status-output
   request/end pair.
2. **`model/model.json`** — 102 entries, 81 distinct products, mapping a
   CEC vendor ID to a Sony product name. The full list is in the
   [README](../README.md#sony-audio-systems-hdmi-cec).

Both files are **outside the signed set** (`digest.txt` lists neither)
and both are referenced only by concatenation
(`FILE_MODELLIST = '../model/model.json'`,
`FILE_DICPATH = '../language/Dic_UTF8_'`), so they were invisible to the
reference-following scavenger until asked for by name — the same failure
class documented in
[worldclock-schema-reconstruction.md](worldclock-schema-reconstruction.md).
The 32-file `language/` dictionary tree was recovered at the same time;
without it the widget was running with no localization at all.

This matters beyond the widget: it is a **documented control protocol
for 81 Sony audio products, extracted from the vendor's own
implementation**. Most of the older ones — the `RHT-G` sound bases, the
early `HT-CT` bars — have no network port at all, so CEC is the only
control channel they will ever have. A protocol table does not expire
when a server is switched off.

## Why the widget reports "unavailable"

Not a broken restore. The bundle is complete and verifies (13/13 signed
files, every digest matching). `dock/dock.js` has exactly three
outcomes:

```js
function DefineViewMode() {
    if (IsFirstAnimNeeded())  return 'VIEWMODE_FIRSTANIM';
    if (!IsEnableHDMI())      return 'VIEWMODE_ERRORBYHDMI';      // hdmiCec.isControlEnabled()
    if (!IsConnected())       return 'VIEWMODE_ERRORBYUNCONNECTED';
    ...
```

So the message distinguishes **CEC control disabled in the TV's own
settings** (BRAVIA Sync off) from **no audio system answering on the
bus**. On a test LAN with no Sony audio hardware, the second is correct
behaviour — the widget is being honest.

## The gap nobody had looked at

The widget probes `HdmiCec.LOGICAL_ADDR_AUDIO_SYSTEM` (`0x05`).

Both Android TV boxes on this LAN claim **`device_type 4`, Playback
Device** — the T10 at logical `0x08`, the RK322x at `0x04`. A grep of
both board trees in the sibling `sparky-armbian` project found **no
document anywhere considering device type 5**. That is the untried
direction, and the pieces for trying it already exist:

- `ro.hdmi.device_type` is a **comma-separated list**, currently `4` in
  the T10's `vendor/build.prop`; `4,5` would claim both roles.
- The T10 runs Android 10, which ships `HdmiCecLocalDeviceAudioSystem`,
  and its ROM already carries the audio-system properties
  (`property_system_audio_mode_muting_enable`,
  `property_sytem_audio_device_arc_port`).
- T10 CEC transport **works bidirectionally** — its message history
  shows a successful `[S] <Report Physical Address> 8F:84:40:00:04`.
  (The RK322x has CEC enabled via a verified DTB patch but its transmit
  fails below the key-mapping layer; that is diagnosed, not fixed, in
  `rk322x-cec-t10-offline-audit-20260728`.)

### Where the chain would break, stated in advance

1. Box claims `0x05` → the Sony sees an audio system — plausible.
2. `isConnected()` returns true → the widget stops reporting
   unavailable — likely.
3. The widget then sends `_r_giveModelInfo`, a **Sony vendor frame**.
   Android's generic audio-system device has no handler for `0xF0xx`
   and will not answer.
4. No model match against the 102-entry table → some *other* failure
   state.

The realistic result is therefore **not** a working home-theatre remote.
It is the widget failing differently — which is still useful, because
the frame it sends while failing names the first opcode an emulator
would have to answer, and we hold the table.

## The zero-risk experiment, if this is ever picked up

No property edit, no reboot, no risk to the working BRAVIA Sync
handshake:

1. Open the Home Theatre widget on the **EX725** (never the HX855 first
   — rule 5).
2. On the T10: `dumpsys hdmi_control` and read the **CEC message
   history**, which Android maintains itself. No sniffer needs building.
3. If the TV polls the bus for an audio system, that poll is in the log.

That answers "does the TV even look?" for nothing. Only if it does is
`device_type=4,5` worth considering — and that is a real system change
to a working box, so it is a decision, not a step.

## Cross-references

- Recovered CEC opcode handling and model table: owner's private
  archive (rule 9b — the archive is not distributed from here).
- Box-side CEC state, DTB patch and transport diagnosis:
  `sparky-armbian/01_board_r329q/hdmi-cec-work/`,
  `.../prototypes/rk322x-cec-t10-offline-audit-20260728/`,
  `sparky-armbian/05_board_tve_t10/`.
- The invisible-file classes that hid `model.json` and the language
  tree: [worldclock-schema-reconstruction.md](worldclock-schema-reconstruction.md).
