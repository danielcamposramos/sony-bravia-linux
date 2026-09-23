# VLC-HiFi and VLC-3D-HiFi: who is asking

People who asked, in public, for what our VLC builds now do. Gathered 2026-09-23. Each entry says which build answers it.

**The builds:**
- **VLC with the 3D fix** (all platforms): VLC detects the H.264 frame-packing SEI and keeps it through transcoding. Released: [3.0.24-3d1](https://github.com/danielcamposramos/vlc/releases/tag/3.0.24-3d1).
- **VLC-HiFi** (Android, in preparation): full-precision audio path, float from decoder to AudioTrack and SoXR at its highest quality. With a ROM whose HAL is opened up (below), measured end to end on a TV box: 24/96 FLAC in, `S24_LE`/48 kHz out.
- **VLC-3D-HiFi** (Android, in preparation): both. For the ultimate 3D cinema experience with high-definition audio, on the boxes that drive 3D televisions.

## The player is half of it: the ROM caps the rest

VLC-HiFi hands Android a float track. What reaches the HDMI after that is decided by the ROM, and stock ROMs cap it even when the hardware can do more. Measured on the TVE T10 (Android 10):

- **The sink.** The stock Allwinner primary audio HAL (`audio.primary.cupid.so`) hard-codes 44.1 kHz / S16, ignores the configuration AudioPolicy asks for, and reports no capabilities. The HDMI hardware under it accepts S16, S24 and S32, 1 to 8 channels, up to 192 kHz.
- **AudioFlinger.** Fed by that sink, the primary mixer thread runs PCM16 at 44.1 kHz. AudioFlinger itself is capable: Android 10 builds it with `kEnableExtendedPrecision = true`, so it mixes in float and can feed a 24-bit (`PCM_8_24`) or 32-bit sink.
- **AudioPolicy never sees HDMI audio.** `WiredAccessoryManager` only accepts extcon names matching `.*audio.*`; the board calls it `hdmi`. Its disconnect logic is also broken.
- **What fixed it on our ROM:** a primary HAL that honours a configured format (48 kHz, `PCM_8_24` / `S24_LE`), taken from the connected TV's EDID and the ALSA hardware. With it, the chain measured end to end is: FLAC 24/96, VLC float, SoXR VHQ to 48 kHz, AudioFlinger `PCM_FLOAT`, HAL `PCM_8_24`, ALSA `S24_LE` at 48 kHz.

The RK322x box (Android 7.1) has the same cap in the Rockchip HAL (44.1 kHz / PCM16); its 24-bit HAL is validated but not yet baked into the ROM.

**This is likely true of most Android devices, in any version.** The vendor HAL and audio policy decide the output format, and a PCM16 primary output is the common default. That is why the requests, bug reports, blog posts and news pieces below keep appearing: a better player alone cannot lift the cap. On a stock ROM, VLC-HiFi still gives the full-precision float path and the best resampler up to AudioFlinger; the last step to 24-bit needs the ROM changes above.

## Direct requests

| Where | When | Platform | What they asked | Answered by |
|---|---|---|---|---|
| [vlc-android #2514](https://code.videolan.org/videolan/vlc-android/-/issues/2514) | 2022-05-08, still open | Android 11 phone (Samsung One UI 3.1) | "Does it play HD Audio without downgrading?" (24-bit/192 kHz FLAC) | VLC-HiFi |
| [NVIDIA Shield forum](https://www.nvidia.com/en-us/geforce/forums/shield-tv/9/222836/playback-hd-audio-24bit-192khz-not-working/) | — | Android TV (Shield) | 24-bit/192 kHz playback reported downsampled to 16-bit/48 kHz | VLC-HiFi, VLC-3D-HiFi |
| [Audiokarma](https://audiokarma.org/forums/threads/will-vlc-player-play-96-24-music-files-at-96-24-resolution.592364/) | 2014-05-08 | Windows PC (compared with foobar2000) | "Will the VLC player play my 96/24 music files without down grading the resolution?"; VLC does not show the output resolution | A future desktop HiFi variant (SoXR default, show the output format) |
| [XDA Forums: HI-RES Audio 24 Bit](https://xdaforums.com/t/hi-res-audio-24-bit.4285003/) | — | Android (device not checked) | 24-bit output on Android | VLC-HiFi |
| [Kodi forum: box for bit-perfect output](https://forum.kodi.tv/showthread.php?tid=293066) | — | Android TV boxes | Which box outputs audio without resampling | VLC-HiFi, VLC-3D-HiFi |

## Communities to reach, with evidence rather than claims

- **XDA Forums:** where modified Android APKs are shared and trusted; a release thread with the measurement.
- **Head-Fi:** Android player and DAP threads.
- **Audio Science Review:** measurement-driven; the AudioFlinger-to-HAL trace is the argument.
- **Hydrogenaudio:** resampler quality; SoXR VHQ is their language.
- **Reddit:** r/audiophile, r/headphones, r/AndroidTV, r/nvidiashield.
- **Outlets explaining the topic:** [Android Authority's audiophile guide](https://www.androidauthority.com/android-audiophile-guide-3611225/), [Echobox: bit-perfect on Android, myth vs reality](https://ombs.io/guides/bit-perfect-playback-android/), [Darko.Audio](https://darko.audio/2025/11/qobuz-launches-android-tv-app-but-theres-a-catch/).

## How we reach them

- **Public posts in the threads, where each forum's rules allow it,** and announcement threads on XDA and Head-Fi. Old threads may have rules against reviving them; read them first.
- **No tracking individual askers across platforms or messaging them privately.** A public answer in the place they asked reaches them and everyone with the same question.
- **vlc-android #2514 cannot be answered from our blocked VideoLAN account.** The answer lives in our release notes instead.
- **Honest claims only:** Android mixes at 48 kHz on these boxes, so no "bit-perfect" promise. The claim is full precision end to end and the best resampler, with the stock-versus-HiFi measurement published alongside.
