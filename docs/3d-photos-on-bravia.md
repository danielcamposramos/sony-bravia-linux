# 3D photos on a BRAVIA — what Sony says, in five markets, and what the sets do

A focused research lane inside act three
([legacy-3d-formats.md](legacy-3d-formats.md)). The question is the one
a person actually types into a search box: **how do I view a
side-by-side or JPS 3D photo on my Sony BRAVIA 3D TV?**

It is asked in every market Sony sold these sets in, it has never had a
straight answer, and Sony's own support pages contradict each other
across regions and generations. Below is what the sets do here,
measured, and what the documentation claims, sourced.

## What our own sets do (owner-measured 2026-09-18)

Both sets. Not one, and not inferred from the other.

| Path | KDL-46EX725 (2011) | KDL-46HX855 (2012) |
|---|---|---|
| full-width SBS `.jpg` over DLNA | flat, no 3D | **same** |
| half-width (frame-compatible) SBS `.jpg` | flat, no 3D | **same** |
| anaglyph→SBS output `.jpg` | flat, no 3D | **same** |
| **MPO bytes renamed `.jpg`** over DLNA | **flat, no 3D** | **same** |
| 3D button with a photo on screen | menu opens — **only 2D→3D conversion** | **same** |

The MPO-renamed test is the sharpest of these, because the delivery was
verified before the test: Serviio served the file as `image/jpeg` with
`DLNA.ORG_PN=JPEG_LRG`, a profile the set advertises, at **byte-exact
size with the `MPF` APP2 segment intact**. So the set received a real
stereo pair and still showed one flat view. Either its decoder does not
inspect `MPF`, or it dispatches on something other than the content —
the file extension in the resource URL being the obvious candidate,
which is the one lead still untested.

**The decisive point is the menu.** There is no side-by-side entry for
stills at all, only the synthetic 2D→3D upconversion. A photo cannot be
told to unpack, so no packing and no naming can succeed on this path.

## What Sony says — and it does not agree with itself

**"Not supported at all."** Sony's own article, same number across
regions, states that 3D photos and films cannot be played from a USB
stick or the home network:
[DE 00129654](https://www.sony.de/electronics/support/articles/00129654),
[RU 00129654](https://www.sony.ru/electronics/support/articles/00129654).

**"MPO is the supported 3D photo format."** Other Sony pages describe
MPO (`.mpo`) as *the* 3D photo format for USB playback, with
per-model variation:
[RU S700023021](https://www.sony.ru/electronics/support/articles/S700023021),
[BR 00013979](https://www.sony.com.br/electronics/support/articles/00013979),
and the 2011-model USB compatibility charts
([MEA/AP 00180404](https://www.sony-mea.com/en/electronics/support/articles/00180404)).
The Japanese knowledge base has the most specific page of all, covering
exactly our generations:
[S1206199004299 — "which formats (extensions) does BRAVIA support over
USB? (2010–2012 models)"](https://knowledge.support.sony.jp/electronics/support/articles/S1206199004299).

**"Side-by-side is HDMI-only."** Sony customer care, relayed in the UK
community, says the side-by-side option is available only on an HDMI
input, and that early 3D sets could not play 3D video from USB at all:
[playing 3D movies from a USB stick](https://community.sony.co.uk/t5/other-tvs/playing-3d-movies-from-a-usb-stick/td-p/1506818).
This matches our measurement exactly, and it is the only one of the
three claims that does.

**"Not on Android TVs."** For the later generation Sony is explicit that
3D stills in `.mpo` cannot be viewed at all
([how to watch 3D on Android TV, 00172421](https://www.sony.co.uk/electronics/support/articles/00172421)),
and Italian owners report precisely that on newer hardware
([KD-65ZD9 does not read MPO](https://community.sony.it/t5/televisori/kd-65zd9-non-legge-immagini-3d-con-estensione-mpo/td-p/2534714)).
Italy also has the question asked in its purest form, as a support
article title: [*can my TV display "Side by side" and "Over under" 3D
content stored on a USB device?*](https://www.sony.it/electronics/support/articles/00069624)

**The community answer is a workaround, never a fix.** The recurring
advice across markets is to play the file from something else over
HDMI and let the TV's 3D menu unpack it there, or to rename JPS to JPG
and accept a flat 2D photo. The Sony US thread the owner archived is
titled, in its own words, *"is there any way to view 3D photos (JPS or
MPO) on a Sony BRAVIA"* — captured to the owner's private research
archive (Sony folder, HTML + PDF) rather than reproduced here.

## The Sony pages, archived

Every Sony support page cited above refuses automated fetching (HTTP
403); this repo does not work around that. The owner captured each one
by hand on 2026-09-18, so the claims stay checkable if Sony withdraws
them — which, for 2011 hardware, is a matter of when.

| Page | Claim | Snapshot |
|---|---|---|
| [DE 00129654](https://www.sony.de/electronics/support/articles/00129654) | 3D photos/films do not play from USB or home network | [2026-09-18](https://web.archive.org/web/20260918105103/https://www.sony.de/electronics/support/articles/00129654) |
| [RU 00129654](https://www.sony.ru/electronics/support/articles/00129654) | same article, Russian | [2026-09-18](https://web.archive.org/web/20260918104856/https://www.sony.ru/electronics/support/articles/00129654) |
| [IT 00069624](https://www.sony.it/electronics/support/articles/00069624) | the question itself, as an article title | [2026-09-18](https://web.archive.org/web/20260918104735/https://www.sony.it/electronics/support/articles/00069624) |
| [RU S700023021](https://www.sony.ru/electronics/support/articles/S700023021) | MPO is the 3D photo format over USB | [2024-03-02](https://web.archive.org/web/20240302201917/https://www.sony.ru/electronics/support/articles/S700023021) (earlier capture already existed) |
| [BR 00013979](https://www.sony.com.br/electronics/support/articles/00013979) | 3D photos via USB: formats and devices | [2026-09-18](https://web.archive.org/web/20260918104336/https://www.sony.com.br/electronics/support/articles/00013979) |
| [MEA 00180404](https://www.sony-mea.com/en/electronics/support/articles/00180404) | USB compatibility charts, **2011 models** | [2026-09-18](https://web.archive.org/web/20260918102410/https://www.sony-mea.com/en/electronics/support/articles/00180404) |
| [AP 00180404](https://www.sony-asia.com/electronics/support/articles/00180404) | same, Asia-Pacific | [2026-09-18](https://web.archive.org/web/20260918102640/https://www.sony-asia.com/electronics/support/articles/00180404) |
| [FY11 CX520 i-Manual, USB](https://www.sony-asia.com/microsite/bravia_i-manuals/FY11/SG/eng/CX520_DF/nt_usb_ga.html) | 2011 generation USB page | [2026-09-18](https://web.archive.org/web/20260918103825/https://www.sony-asia.com/microsite/bravia_i-manuals/FY11/SG/eng/CX520_DF/nt_usb_ga.html) |
| [FY12 HX850 i-Manual, USB](https://helpguide.sony.net/apmig/bravia_i-manuals/FY12/HX850/GA/usb_europe_ga_twn.html) | the HX855's own generation — **never mentions 3D** | [2026-09-18](https://web.archive.org/web/20260918103148/https://helpguide.sony.net/apmig/bravia_i-manuals/FY12/HX850/GA/usb_europe_ga_twn.html) |
| [UK 00172421](https://www.sony.co.uk/electronics/support/articles/00172421) | Android TV: `.mpo` stills **cannot** be viewed | [2026-09-18](https://web.archive.org/web/20260918104145/https://www.sony.co.uk/electronics/support/articles/00172421) |

The Japanese knowledge-base page (S1206199004299, 2010–2012 USB
formats), the JP i-manual pages and the forum mirrors are held in the
owner's private research archive or are no longer online; they are
cited by title only.

## What owners reported, market by market

A forum sweep in Italian, French, Spanish and Portuguese (2026-09-18).
Sony's regional communities (`community.sony.it/.fr/.es/.pt`, one
platform) return 403 to every page, so most Sony-community items below
were read **only through the search index**: the thread, its title and
its substance are real, but the post was not opened and its date is
unverified. They are marked **INDEX**. Pages actually read are marked
**VERIFIED**. INDEX items are leads to confirm in a browser before
anyone quotes them.

**The finding that reframes the photo question — MPO stills did work on
the KDL generation, from USB (INDEX, Italian).** A Fuji Real 3D owner
reports the camera's full-HD MPO stills *"correttamente interpretato da
Sony (bellissime!)"* on a BRAVIA, while its 3D video did not play from
USB
([thread](https://community.sony.it/t5/televisori/visualizzare-i-video-3d-di-fuji-real-3d-su-bravia/td-p/1958137)).
A second thread traces a Sony Bloggie 3D MPO failure to malformed
files that displayed correctly after a plain re-save on a PC, and
states MPO from other 3D cameras was read correctly
([thread](https://community.sony.it/t5/videocamere/visualizzazione-foto-3d-mpo-fatte-con-bloggie-3d/td-p/313441)).
That agrees with Sony's 2011 USB charts, and it means **our test so far
asked the wrong question**: we delivered MPO bytes over DLNA under a
`.jpg` name. What these owners describe is a real `.mpo` file on a USB
stick. That test is staged and not yet run.

**Then it was taken away (INDEX, Italian).** On the Android generation
a KD-65ZD9 owner reports the folder of `.mpo` files as simply *empty*;
the stills render only when the same stick goes into an Oppo UDP-205
over HDMI
([thread](https://community.sony.it/t5/televisori/kd-65zd9-non-legge-immagini-3d-con-estensione-mpo/td-p/2534714)).
Sony's own Android-era article says the same in plain words (UK
00172421, above). If the KDL reports hold, that is a **documented
capability regression on the same brand**, noticed by owners in more
than one language.

**Video: the procedure was common knowledge, the outcome was not.**
Across IT/ES/FR/PT the recipe is identical — play the file, press 3D,
pick *Fianco a Fianco / Lado a Lado / Côte à côte* — and several threads
report it working from USB. An equal number were told 3D is offered
only on an HDMI input, including an EX720 owner whose same file played
in 3D on a Samsung
([IT, INDEX](https://community.sony.it/t5/televisori/chiarimenti-su-visualizzazione-in-3d/td-p/365264)).
Underneath most failures sat the container, not the stereo: MKV refused
over USB, FAT32 only (a 4 GB ceiling that rules out a real 3D rip), and
DivX refusals owners read as licensing
([HardWare.fr, KDL-46HX750, Dec 2012, VERIFIED](https://forum.hardware.fr/hfr/VideoSon/Traitement-Video/film-sony-bravia-sujet_138759_1.htm);
[ForoCoches, 2015, VERIFIED](https://forocoches.com/foro/showthread.php?t=4316746)).
DLNA did better than USB: the working Spanish answer was PS3 Media
Server over Wi-Fi with the menu on *Lado a Lado*
([ES, INDEX](https://community.sony.es/t5/televisores/peliculas-3d-descargadas-de-internet/td-p/279007)).

**German, VERIFIED (hifi-forum.de) — the campaign's own problem, in
2012.** A KDL-46EX727 owner asks how to watch his 3D Blu-ray rips (ISO
and MKV) from the PC on the TV, is steered away from USB and toward
**DLNA through Serviio** — the exact stack this repository runs — and
the thread never reports reaching 3D
([*3D iso und mkv*, ~Jan 2012](http://www.hifi-forum.de/viewthread-144-6784.html)).
That is the founding problem of the whole signalling campaign, asked in
German fourteen years ago, stopping exactly where the missing SEI stops
everyone. A companion thread from a **KDL-40EX725** owner (Sep 2011)
confirms the video 3D menu offers *Nebeneinander* and *Untereinander*
as manual formats
([thread](http://www.hifi-forum.de/viewthread-144-6530.html)) — the
side-by-side entry that the photo menu, on the same sets, does not
have.

**Dutch and Polish yielded nothing confirmable.** tweakers.net cannot
be fetched from here at all, and the Polish forums returned only
off-topic EX720 threads. Stated plainly rather than padded.

**Japanese, VERIFIED (Yahoo!知恵袋) — the clearest first-hand failure.**
A KDL-46HX800 owner (February 2012) loads 3D photos from a Nintendo
3DS, which writes MPO, through a USB SD-card reader: no 3D. The best
answer says USB is probably not recognised as 3D and to use HDMI or a
PS3
([q1181508851](https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q1181508851)).
An HX800 owner confirms the menu's *左右分割方式 / 上下分割方式*
(side-by-side / top-bottom) for broadcast and HDMI
([q1052618940](https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q1052618940)),
and an HX720 owner saw those entries missing on a Blu-ray input until a
bad HDMI cable was replaced
([q1165065376](https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q1165065376)):
the menu's contents depend on the input. Keep the dates straight: the
HX800 is a **2010** set, a generation before the 2011 USB charts that
list MPO, so it does not settle the question for our 2011/2012 sets —
it sharpens it. And a finding about language rather than hardware:
**Japanese owners never search for "MPO"** — zero results on 知恵袋 —
they write 3D写真, or 3DSの3D写真.

**Traditional Chinese, INDEX only (Mobile01 refuses fetching).** A 2013
owner loads self-shot side-by-side JPGs through an SD-card reader and
the 3D menu offers only Off and 2D-simulated-3D
([thread](https://www.mobile01.com/topicdetail.php?f=257&t=3204570)) —
the result measured on our sets, reported independently.

**Korean: nothing substantive.** The likely venues (DVDPrime, Naver)
sit behind bot checks that were not worked around.

**Across every market swept, nobody reported native 3D from USB or
DLNA on this generation.** Every thread that ends resolved ends on HDMI
or an external player.

**One unmet need, verified: the eye swap.** A BRAVIA owner with a
swapped-eye SBS rip: *"mi tele sony bravia no dispone de ese cambio de
sentido"* — the set plays the file and offers no way to flip left and
right, so the advice was to wear the glasses backwards
([ForoDVD, Feb 2013, VERIFIED](https://www.forodvd.com/tema/116691-problema-con-peli-3d/)).
Brazilian owners hit the same wall
([Adrenaline, INDEX](https://forum.adrenaline.com.br/threads/tem-como-ver-3d-em-filmes-baixados.517899/)).
It is a one-filter fix on our side (`stereo3d=sbsl:sbsr`), and it
belongs in the 3D catalogue as a per-file flag.

**Portuguese (Brazil) is under-evidenced for a mechanical reason**:
the two big Brazilian forums sit behind Cloudflare, and the 2011 Yahoo
Respostas threads — including one titled *"Não consigo assistir vídeo
3D pela minha Sony 3D Bravia 725"* (Oct 2011, an EX725-class set) — died
with the service in 2021. No Latin-American thread on SBS or MPO
surfaced at all. The Spanish-language discussion of this era is
effectively all Spain.

## What this adds up to

**The capability was documented into existence and then never wired to
the photo path.** MPO is named as a supported format in Sony's own
compatibility material for 2010–2012 sets, including ours, while the
support article in two other languages says 3D stills do not play from
USB or the network at all, and the sets themselves offer no
side-by-side option for a photo in the 3D menu. All three statements
are Sony's. Only the third is testable here, and it is the one that
holds.

This is the same shape as the rest of this project, one layer further
in. The panel does stereo. The decoder can read the formats. **The
photo path was simply never connected to the 3D switch**, and the
documentation gap let that pass unnoticed for fifteen years in five
languages. Compare
[regional-documentation-asymmetry.md](regional-documentation-asymmetry.md)
— the pattern is not new, only newly pointed at photographs.

Worth keeping in proportion: stereo photography is not a modern
gimmick that the format war forgot. Wheatstone described the
stereoscope in 1838 and Daguerre announced photography in 1839, so
stereo is as old as the photograph itself. What broke is younger than
either.

## Still open, in order

1. **USB with a real `.MPO` extension — now the decisive test.** Sony's
   2011 USB charts list MPO, and Italian owners of the same generation
   report MPO stills displaying in 3D from a stick. Staged at
   `/mnt/arquivos/Fotos3D-USB/` — 11 `.MPO`, 11 original `.jps`,
   upper/lower-case probes, three JPEG controls. **Restaged (v2)** after
   the sweeps: the MPOs now sit where a camera puts them
   (`DCIM/100MSDCF/DSC000nn.MPO`, the folder layout Sony's manual
   requires for camera photos) and carry Exif plus a per-view MP
   attribute IFD, as camera MPOs do, so a "no" cannot be blamed on the
   files. The best control of all is a photo shot in 3D on the owner's
   own Optimus 3D or a 3DS. If it works, the
   network path failed only because Serviio and the set's DLNA profile
   list cannot carry `.mpo` — and the portal can hand the set a stick's
   worth of MPOs another way.
2. **The resource-URL extension hypothesis.** The DLNA test delivered
   correct MPO bytes under a `.jpg` URL. If the set dispatches on the
   URL's extension rather than the content, a `.mpo` resource URL might
   change the outcome — worth one probe through our own app, which
   controls its URLs completely, before concluding DLNA is closed.
3. **Pull the two WAF-blocked Sony pages by hand** (JP S1206199004299
   and 00180404) into the private archive. They are the closest thing
   to an authoritative format list for exactly these model years, and
   automated fetching is refused — deliberately not worked around.
