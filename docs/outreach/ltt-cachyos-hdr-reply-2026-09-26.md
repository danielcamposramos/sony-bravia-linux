<!-- POSTED 2026-09-26 by Daniel on the LTT thread "CachyOS updates proton
     with HDR autodetection" (Linux, macOS and Everything Not-Windows):
     findComment-16938910
     https://linustechtips.com/topic/1639121-cachyos-updates-proton-with-hdr-autodetection/?do=findComment&comment=16938910
     The four posters answered on their own point: the 3D comments (Mark
     Kaine, OddOod) and the HDR news from awesome-linux-hdr, with the honest
     limit stated (no HDR display here; the 12-bit link is deep colour on an
     SDR set). Mark Kaine was already answered on 3D today in "Is 3D gaming
     still a thing?", so this links there. The thread's Proton-CachyOS
     release went into awesome-linux-hdr the same day, as a reported entry.
     The text below is the draft as proposed; Daniel posts in his own words,
     so the posted text may differ. -->

@vonKordke good news for Linux HDR, and there is now a place to follow the whole chain: I keep awesome-linux-hdr, an evidence map from the specification to the photons (formats, DRM/KMS, drivers, compositors, apps, measurement), with every claim marked as specified, implemented, measured or only reported. Needing launch variables to force HDR detection is what it looks like when one layer in the chain decides on its own; the list tracks those, like the gamescope report of HDR falling back to an 8-bit link.

@Mark Kaine your "conversion for non HDR screens" is the gap the list names: Linux has the tone-mapping pieces (libplacebo and mpv do it for video in real time), but no dependable path that takes HDR to an SDR screen automatically, at full precision. Closing that is the roadmap there. It is proposed, not built; the first step is measured: a 12-bit HDMI link from nouveau to my 2012 Sony, with the patches on the kernel lists. And on 3D, you will like my answer in the other thread today: https://linustechtips.com/topic/1616265-is-3d-gaming-still-a-thing/?do=findComment&comment=16938907

@OddOod on 3D: it went somewhere and was left there. The TVs, the discs and the engines still do it; what stopped was the support. Half-Life 2's own VR renderer now draws real stereo for a 3D TV on Linux. And agreed on screenshots: tone-mapping HDR for a capture is the same missing piece as above.

@ItTakes2ToMango "piss poor software and compatibility" is the list's premise in fewer words: every layer has to carry the HDR signal, and one that quietly narrows it breaks the whole thing.

Honest note: I own no HDR display, so none of the HDR above is my measurement; the 12-bit link is deep colour on an SDR set, not HDR. The list says which claims are measured, by whom and on what.
awesome-linux-hdr: https://github.com/danielcamposramos/awesome-linux-hdr
The 3D side: https://github.com/danielcamposramos/sony-bravia-linux and https://github.com/danielcamposramos/awesome-stereoscopy
