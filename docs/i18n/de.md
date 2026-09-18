# Sony BRAVIA 3D-Fernseher (Modelle 2011–2012): 3D-Filme und 3D-Fotos wieder abspielen, ein quelloffenes Reparaturprojekt des Besitzers

<!-- lang: de · canonical source: ../../README.md (English) · translated 2026-09-18 -->

Dieses Projekt belebt die BRAVIA-Fernseher der Vor-Android-Zeit (KDL-Serie, 2010–2012) wieder, nachdem Sony ihre Online-Dienste abgeschaltet hat, und zwar vollständig im eigenen Heimnetz des Besitzers. Die Firmware wird nicht verändert, DRM wird nicht angetastet. **Recht auf Reparatur**, praktisch umgesetzt.

## Warum Ihr 3D-Film nur flach läuft

- Diese Fernseher schalten **nur dann automatisch auf 3D**, wenn der **Videostrom selbst** die H.264-Kennung „Frame Packing“ (SEI) enthält.
- Übliche 3D-Dateien (MKV Side-by-Side / Top-and-Bottom) tragen nur eine Kennung im Container, und die geht verloren, sobald ein DLNA-Server die Datei ausliefert. Ergebnis: zwei Bilder nebeneinander, kein 3D.
- **Die Lösung (verlustfrei, ohne Neukodierung):** `tools/bravia_sei3d.py` schreibt die SEI einmalig in die Datei. Danach schaltet der Fernseher auch über DLNA von selbst auf 3D. HandBrake hat die Funktion übernommen (PR #8100, ab der nächsten Version). Das mitgelieferte Serviio-Profil fügt die SEI beim Transkodieren automatisch hinzu.
- Linkes und rechtes Auge vertauscht? Der Fernseher kann die Seiten nicht tauschen, ein ffmpeg-Filter schon (`stereo3d=sbsl:sbsr`).

## 3D-Fotos (Side-by-Side / JPS / MPO)

- Gemessen an KDL-46EX725 und KDL-46HX855: Im Foto-Betrachter (DLNA oder USB) bietet die 3D-Taste **nur die „2D→3D-Umwandlung“** an. Eine Side-by-Side-Option für Fotos gibt es nicht.
- Das Standardformat der 3D-Kameras, **MPO**, vom USB-Stick: laut Sonys Kompatibilitätsliste für 2011er-Modelle unterstützt und von Besitzern berichtet. Der Test läuft.
- Anaglyphen-Fotos und -Videos (Rot/Cyan-Brille) lassen sich in Side-by-Side umwandeln: `tools/bravia_anaglyph.py`.

## Betroffene Modelle

- Getestet: **KDL-46EX725** (2011), **KDL-46HX855** (2012)
- Gleiche Platinenfamilie: KDL-46EX724, KDL-40HX853, KDL-55HX753
- Das 3D-Signal-Problem (SEI) betrifft jeden Fernseher und Projektor, der 3D aus dem Videostrom erkennt (dasselbe Symptom wird auch bei Samsung berichtet).

## Weitere Dokumentation (Englisch)

- [Projektübersicht](../../README.md)
- [Die 3D-Kennung erklärt](../3d-signalling-explainer.md)
- [Recherche: 3D-Fotos auf dem BRAVIA](../3d-photos-on-bravia.md)
- [Anleitung zum Nachbauen](../build-your-own-bravia-portal.md)
- [Alte 3D-Formate (Anaglyphen, Zeilen-Interlace)](../legacy-3d-formats.md)

---

*Am 18. September 2026 aus dem Englischen übersetzt. Korrekturen von Muttersprachlern sind sehr willkommen, bitte ein Issue eröffnen.*
