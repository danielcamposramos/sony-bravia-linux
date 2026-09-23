# VLC-HiFi and VLC-3D-HiFi: who is asking

People who asked, in public, for what our VLC builds now do. Gathered 2026-09-23. Each entry says which build answers it.

**The builds:**
- **VLC with the 3D fix** (all platforms): VLC detects the H.264 frame-packing SEI and keeps it through transcoding. Released: [3.0.24-3d1](https://github.com/danielcamposramos/vlc/releases/tag/3.0.24-3d1).
- **VLC-HiFi** (Android, in preparation): full-precision audio path, float from decoder to AudioTrack, 24-bit at the HAL, SoXR at its highest quality, measured on a TV box (24/96 FLAC in, `S24_LE`/48 kHz out).
- **VLC-3D-HiFi** (Android, in preparation): both. For the ultimate 3D cinema experience with high-definition audio, on the boxes that drive 3D televisions.

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
