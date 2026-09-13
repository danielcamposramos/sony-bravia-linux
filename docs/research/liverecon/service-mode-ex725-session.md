# Service-mode / CERS-registration session — KDL-46EX725 (2026-09-13)

Live, read-only session on the EX725 (192.168.0.22), attended by the
owner. Everything below was read from the TV's own screens or its own
APIs; nothing was written to the set. Exit was clean (POWER off), and
no service value was changed.

## 1. CERS registration — DONE (the deferred dialog, now accepted)

The one-time registration gate (FINDINGS.md §"CERS HTTP API") was
deliberately accepted on the EX725 (the safe set; never the HX855
monitor). Working procedure, matching the Media Remote app capture
(`chr15m/media-remote` SNIFF.md):

```
GET /cers/api/register?name=<client>&registrationType=initial&deviceId=MediaRemote%3A<unique-id>
X-CERS-DEVICE-ID:   MediaRemote:<unique-id>
X-CERS-DEVICE-INFO: <anything>
```
→ HTTP 200, empty body; a confirmation dialog pops **on the TV screen**;
the owner accepts it with the physical remote. Afterwards the same
`X-CERS-DEVICE-ID` header unlocks the gated CERS actions.

Post-registration, `GET /cers/api/getRemoteCommandList` (previously
403) returns the TV's **authoritative IRCC code table** (85 commands,
6037 bytes) — saved verbatim as
`cers_remoteCommandList_KDL-46EX725.xml` in this directory and merged
into `tools/bravia_ircc.py`.

### Generation-difference findings from the TV's own table

- Color buttons and the media family: **manufacturer=2, device 0x97**
  (151) — the "0x9c" live note was wrong for this set; 0x9c is the
  Android-generation variant (pro-bravia.sony.net table).
- Volume: `VolumeUp 0x12`, `VolumeDown 0x13`, `Mute 0x14` — the
  standard table, byte-for-byte. (An earlier "0x12 does volume minus"
  report was a misread; live re-test at a known volume level confirmed
  0x12 = up, 0x13 = down, matching the TV's own list.)
- `Display` is 0x3a — correct in the driver — but on this set it
  shows no info banner on a steady HDMI input (behaviour, not code).
- Previously unverified driver codes now confirmed by the TV itself:
  gguide 0x0e, epg (2,164,0x5b), jump 0x3b, teletext 0x3f,
  wide (2,164,0x3d), top-menu/popup-menu (2,26,0x60/0x61),
  num11/num12 0x0a/0x0b, exit 0x63.
- Codes added to the driver from this list: closed-caption, pap,
  program-description, rewind/forward/replay/advance/eject/rec,
  ten-key, analog, digital, bs/cs/bscs, ddata, mode3d, my-epg,
  write-chapter, delete-video, easy-startup, internet-widgets,
  internet-video, scene-select, imanual, applicast, actvila, track-id,
  one-touch-{view,rec,time-rec,rec-stop}.

## 2. Service-mode entry: LAN IRCC CANNOT arm it (live-tested negative)

Two attempts, both with every code verified against the TV's own
table:

1. Spaced manual sends (several seconds apart): booted normally.
2. `seq service-mode-entry` at remote-like pacing (5 s standby settle,
   0.6 s cadence): **booted normally again** — channel 5 tuned, volume
   applied, no service screen.

The owner then keyed the identical sequence
(standby → DISPLAY → Ch5 → Vol+ → POWER) on the **physical remote** and
the set armed **instantly**. Conclusion: the standby-key arming state
machine does not honour network-injected IRCC keys (at minimum the
DISPLAY arm step). Consequences:

- Service-mode entry (and therefore NVM writes via service mode) is
  **not reachable over the LAN** with this generation's IRCC — good
  for safety, and it means remote service-mode sessions need the
  physical remote (or post-root injection at the standby input layer).
- All IRCC *navigation* keys used during the failed arming executed
  literally (channel 5, volume), which re-confirms keys are buffered
  and applied in standby.

## 3. Service-mode screens (physical remote; read-only)

Three categories, cycled with JUMP/OPTIONS: Digital → Chassis → VPC.

### Digital Service (firmware / identity — our unit's actual values)

| Field | Value |
|---|---|
| `001 OP` / `000 VERS ---` | item header lines (see SM p.90+) |
| DM (main digital) | `DM4.027BRA` (previous: `(DM3.505BRA)`) — matches final firmware PKG4.027BRA |
| RF | `0000` |
| WF (WiFi) | `WF2310W00AA` (ext: `--------`) |
| DF | `DF2.290W00AA` (ext: `--------`), FD 0.69 |
| YM | `YM1.030W00AA` |
| M | `M4.001C` |
| PK (PEM / panel micro) | `PK4.190W00AA  <PEM>` |
| **MID** (motherboard ID) | `3D65E205` |
| **PID** (panel ID) | `0E050000` |
| **PNL** (panel model) | `LTY460HJJ0501` |

(The `MID:1C117081 / PID:04020000 / PNL:LTY320AB01` values quoted from
the SM are its *example* figures, not ours.) Note the EX725's chassis
codename in service mode is **WYVERN — the same as the AZ3F HX855's**,
so "WYVERN" spans both chassis generations of this platform.

### Chassis Service
- `000 WYVERN` (chassis codename)
- `000 S2_NOISE_TH 32` — a tuner noise-threshold adjustment value.

### VPC Service
- `DATA_COPY` — write-op: restores white-balance/gamma data to the B
  board after USB-DL / board replacement (SM p.92). **Not touched.**
- `BU_TRANS 0` — backup-transfer companion write-op. **Not touched.**

## 4. SELF CHECK screen (self-diagnostic; DISPLAY → Ch5 → Vol− → POWER)

| Diagnostic | Count | Meaning |
|---|---|---|
| RGB_SEN / RESERVED ×2 | 00 | unused |
| 002 MAIN_POWE | 00 | main power OVP — clean |
| 003 DC_ALERT / AUD_PROT | 00 | DC alert / audio protection — clean |
| 004 VLED / BALANCER | 00 / **01** | one historic panel-balancer error |
| 005 HFR_ERR / TCON_ERR / P_ID_ERR | 00 | panel/ID chain — clean |
| 006 BACKLITE | 00 | backlight — clean |
| 007 TEMP_ERR / FAN_ERR | 00 | thermal — clean |
| 010 EMITTER / 011 IA | 00 | unused on this set |
| 101 VPC_WDT / 102 MEPS_WDT | 00 | panel / power watchdogs — never fired |
| **103 HOST_WDT** | **21** | **main-CPU watchdog fired 21 times over the set's life** |
| 104 STBY_WDT | 00 | standby watchdog — clean |
| Counters `25758-11498-26682` | | panel hours **25758**, **boot count 11498**, total hours **26682** |

Error-history timestamp rows were all dashes (no pending entries shown
to us). No NEXT PAGE item. Exited via POWER off. The clear procedures
(Ch8→Ch0 error history, Ch7→Ch0 panel time) were deliberately **not**
used — the record stays intact as our baseline.

## 5. What this means for the project

- **Crash oracle is live and baseline-captured.** `HOST_WDT=21` on a
  heavily-used 15-year-old set proves watchdog resets accumulate
  *recoverably* across normal life. The Track B-alt crash-probe rig
  (Presto CVE fuzzing etc., EX725 only) can use
  `HOST_WDT`/8-blink-state deltas as its success/crash signal, knowing
  a handful of extra trips is statistically nothing against 21.
- **Boot count 11498** is also a cheap before/after tripwire for any
  experiment that resets the set.
- **The LAN attack surface cannot reach service NVM** — arming needs IR.
  That bounds the worst-case remote damage to normal keypresses and
  player/watchdog state.
- **Full command table now authoritative for this exact chassis** —
  IRCC driver merged to 90 named codes; no more code guessing anywhere
  in the tooling.
- Platform identity for OUR unit recorded (MID/PID/PNL/PEM/DM firmware
  history) — the panel is an LG Display `LTY460HJJ0501`, giving us the
  panel-side reference for any future T-CON/PEM work.