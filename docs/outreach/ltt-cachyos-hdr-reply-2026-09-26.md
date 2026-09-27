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

## Follow-ups, 2026-09-27

vonKordke asked "is there at least a human behind this ai generated response?" and ItTakes2ToMango answered "....Sigh". Nobody disputed a fact in the reply. Daniel answered in his own words ("What do you mean?", "?", then a link to his LinkedIn profile, saying he does not need to prove he is human and that he had crafted an answer for each member).

Then Daniel answered vonKordke's earlier "old man rambling" post to Mark Kaine with measurements (findComment-16939040,
https://linustechtips.com/topic/1639121-cachyos-updates-proton-with-hdr-autodetection/?do=findComment&comment=16939040):

```
Glad it works on yours, and that is exactly the point Mark and ItTakes2ToMango made: it works when every layer of your stack handles it, and on Linux that still depends on who made your GPU and which driver you run.

I measured it on one TV, which is SDR, so this is deep colour, the link HDR rides on, not HDR itself. Same TV, read on its own on-screen info:
amdgpu trains the HDMI link at 12 bits.
NVIDIA's proprietary driver on Linux caps it at 10 bits by default, while the same card on Windows drives 12.
Stock nouveau stays at 8 bits on HDMI.

On nouveau, Mohamed Ahmed is doing the real work: his branch brings 12-bit HDMI with proper bandwidth validation, and the nouveau maintainer chose it over my own series, which lacked that part. So I moved my work onto his branch: a small HDMI compliance fix, tested on two Sony sets, and a YCbCr output port, which HDR10 needs and which stock nouveau does not have yet. Both are offered to him in a merge request.

So Mark's point stands: it is not the panels, it is the support, and it is uneven across makers, kernels and drivers. Where each one stands, with the evidence: https://github.com/danielcamposramos/awesome-linux-hdr
```

Sources: the 12/10/8 readings, `docs/research/liverecon/nv-vs-amd-deepcolor-osd-2026-09-22.md` (TV OSD on both inputs, 2026-09-22; Windows 12-bit proven from Daniel's own use) and the stock-nouveau and Mohamed-branch runs in `docs/upstream/issue-tracker.md` (runs 30-34, mohamexiety/nouveau!1).

Moderation, 2026-09-27: moderator SansVarnic cleaned the whole personal exchange ("-= Cleaned =-"), on both sides: the "is there a human" and "Sigh" posts and Daniel's reply with his LinkedIn profile. The substantive replies stand: the answer to each member and the measured reply (16939040).
