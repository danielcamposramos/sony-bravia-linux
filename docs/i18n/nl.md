# Sony BRAVIA 3D-televisies (modellen 2011–2012): weer 3D-films en 3D-foto's afspelen, een open-source reparatieproject van de eigenaar zelf

<!-- lang: nl · canonical source: ../../README.md (English) · translated 2026-09-18 -->

Dit project brengt de BRAVIA-televisies van vóór Android (KDL-serie, 2010–2012) weer tot leven nadat Sony hun onlinediensten heeft uitgeschakeld, volledig binnen het thuisnetwerk van de eigenaar. De firmware wordt niet aangepast en er wordt niet aan DRM gekomen. **Recht op reparatie**, in de praktijk.

## Waarom je 3D-film plat wordt weergegeven

- Deze televisies **schakelen alleen automatisch naar 3D** als de **videostream zelf** de H.264-informatie "frame packing" (SEI) bevat.
- Gangbare 3D-bestanden (MKV side-by-side / top-bottom) hebben alleen een label in de container, en dat gaat verloren zodra een DLNA-server het bestand verstuurt. Resultaat: twee beelden naast elkaar, geen 3D.
- **De oplossing (verliesvrij, zonder hercoderen):** `tools/bravia_sei3d.py` schrijft de SEI eenmalig in het bestand. Daarna schakelt de televisie vanzelf naar 3D, ook via DLNA. HandBrake heeft de functie overgenomen (PR #8100, in de volgende versie). Het meegeleverde Serviio-profiel voegt de SEI automatisch toe bij het transcoderen.
- Ogen verwisseld? De televisie kan links en rechts niet omwisselen, een ffmpeg-filter wel (`stereo3d=sbsl:sbsr`).

## 3D-foto's (side-by-side / JPS / MPO)

- Gemeten op KDL-46EX725 en KDL-46HX855: in de fotoweergave (DLNA of USB) biedt de 3D-knop **alleen "2D→3D-conversie"**. Er is geen side-by-side-optie voor foto's.
- Het standaardformaat van 3D-camera's, **MPO**, vanaf een USB-stick: Sony vermeldt het in de compatibiliteitstabel voor 2011-modellen en eigenaren melden dat het werkt. De test loopt.
- Anaglief-foto's en -video's (rood/cyaan bril) kunnen worden omgezet naar side-by-side: `tools/bravia_anaglyph.py`.

## Betrokken modellen

- Getest: **KDL-46EX725** (2011), **KDL-46HX855** (2012)
- Dezelfde bordfamilie: KDL-46EX724, KDL-40HX853, KDL-55HX753
- Het 3D-signaalprobleem (SEI) geldt voor elke televisie en projector die 3D uit de videostream herkent (hetzelfde symptoom wordt ook bij Samsung gemeld).

## Documentatie (Engels)

- [Projectoverzicht](../../README.md)
- [Het 3D-signaal uitgelegd](../3d-signalling-explainer.md)
- [Onderzoek: 3D-foto's op de BRAVIA](../3d-photos-on-bravia.md)
- [Handleiding om het zelf te bouwen](../build-your-own-bravia-portal.md)
- [Oude 3D-formaten (anaglief, interlaced)](../legacy-3d-formats.md)

---

*Op 18 september 2026 vertaald uit het Engels. Correcties van moedertaalsprekers zijn welkom: open een issue.*
