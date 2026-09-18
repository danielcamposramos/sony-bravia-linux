# BgmSearch / TrackID — a recovered service description

Sony's on-TV music/media recognition feature (the button labelled
"TrackID" on these sets, "BgmSearch" internally). Retired. This is what
it was, established 2026-09-18 without opening anything.

## What pressing the button does now

On the EX725 the TrackID menu item returns **"esta opção não está mais
disponível"**. A firewall-side `tcpdump` on the TV's address, run twice
(the second with ARP filtered out), captured **zero packets** — no DNS,
no HTTP, no TLS. The message is generated locally: the firmware already
knows the service is gone and never reaches the network. This is the same
tombstone pattern as the withheld widgets — availability decided by data
on the device, not by asking a server.

## What it was, from the archived client

The Internet Archive holds the client bundle
`bravia.dl.playstation.net/bravia/WidgetBundles/BgmSearch/2.0.1/
MediaExplorerCommon.img` (200, captured 2019-07-05) and the manifest
`BgmSearch-2ndDisp/info.xml` (200, 2024-04-15).

`MediaExplorerCommon.img` is uncompressed JavaScript,
`JAVA_SCRIPT_BUNDLE_VERSION_2.0.1`, 3,281 lines. It names the whole
architecture:

| piece | value |
|---|---|
| recognition backend | **Gracenote** (`urn:bookmark:gracenote:music`) |
| SMRP endpoint | `https://media.np.ac.playstation.net/sony/mmr` |
| bookmark store | `upbookmark.ww.np.community.playstation.net/np/up/` |
| identity | a per-set "Gracenote User ID for SMRP communication" |
| shared by | MusicExplorer, VideoExplorer, MediaSearch, BgmSearch |

The manifest declares profile **`SWA1.0`** (a profile not otherwise seen
in our corpus), entry point `server.xml`, view `notification`.

## Why it cannot simply be re-enabled

Three independent walls, in the order they were tested:

1. **The switch is not ours to flip.** The catalog we serve on the
   spoofed applicast controls the *widget gallery* (`status=""` vs
   `Deleted`), and that is how the five widgets were restored. TrackID is
   not a gallery widget; its button is firmware-resident, and the TV
   never reads any catalog for it (zero packets, above).
2. **The recognition half lives in the firmware, encrypted.** The feature
   fingerprints the set's own audio, which is an engine-internal path a
   browser page cannot touch (no getUserMedia in Presto 11). That code is
   inside the firmware image, and the images are whole-file encrypted
   (CBC/CTR-class, no public decryptor, no correctness oracle — see
   platform-map.md §6). It cannot be unpacked from a keyboard.
3. **The backend is off-limits anyway.** The only two hosts in the bundle
   are on `*.playstation.net`, which is on the project's do-not-touch
   list, and Gracenote's brokered endpoint is long gone.

## The routes that remain, and when

- **Now, on the portal:** a music-ID *page* can live in the unsigned
  portal lane, but it has no audio to identify — so it is only useful for
  library-side identification, not "what is playing on the TV".
- **Now, on d2server:** `fpcalc` (Chromaprint) + AcoustID against the
  38,782-file library index would fill in what Serviio lists as Unknown.
  Entirely local, no service that can retire. Not started.
- **Future, needs hardware:** the firmware-resident half is reachable
  only via the recorded UART → ABK-monitor route (platform-map.md §7),
  which means opening a chassis. Deferred by the owner until a spare unit
  exists — the two live sets are never opened. An older firmware image
  would carry the pre-tombstone recognition code, to be re-enabled and
  re-pointed at a modern backend; that whole path waits on (1) a unit to
  open and (2) the decryption or UART extraction it depends on.

## Provenance

Client bundle and manifest: Internet Archive, URLs above. Live null
result: OPNsense firewall `tcpdump` on bce0, 2026-09-18. Nothing
Sony-copyrighted is committed here (rule 9); the 123 KB bundle stays in
the private working area.
