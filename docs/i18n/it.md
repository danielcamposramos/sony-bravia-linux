# Televisori Sony BRAVIA 3D (modelli 2011–2012): rivedere film 3D e foto 3D, un progetto di riparazione open source gestito dal proprietario

<!-- lang: it · canonical source: ../../README.md (English) · translated 2026-09-18 -->

Questo progetto riporta in vita i BRAVIA precedenti ad Android (serie KDL, 2010–2012) dopo che Sony ne ha spento i servizi online, interamente sulla rete di casa del proprietario. Il firmware non viene modificato e nessun DRM viene toccato. Il **diritto alla riparazione**, in pratica.

## Cercavi questo?

Questa pagina risponde a domande come:

- "Leggere .mkv 3D tramite porta USB sul Bravia"
- "Film in 3D su chiavetta USB: il televisore non va in 3D"
- "Visualizzazione foto 3D (.mpo) sul Sony Bravia"
- "Il 3D funziona solo in HDMI?"
- "Formato 3D Fianco a Fianco: l'immagine resta divisa"

## Perché il tuo film 3D si vede piatto

- Questi televisori **passano automaticamente in 3D** solo se il **flusso video stesso** contiene l'informazione H.264 di "frame packing" (SEI).
- I file 3D comuni (MKV fianco a fianco / sopra-sotto) hanno solo un'etichetta nel contenitore, che si perde appena un server DLNA trasmette il file. Risultato: due immagini affiancate, niente 3D.
- **La soluzione (senza perdita, senza ricodifica):** `tools/bravia_sei3d.py` scrive la SEI una sola volta nel file. Da lì in poi il televisore passa in 3D da solo, anche via DLNA. HandBrake ha integrato la funzione (PR #8100, nella prossima versione). Il profilo Serviio incluso aggiunge la SEI automaticamente durante la transcodifica.
- Occhi invertiti? Il televisore non permette di scambiare sinistra e destra, un filtro di ffmpeg sì (`stereo3d=sbsl:sbsr`).

## Foto 3D (fianco a fianco / JPS / MPO)

- Misurato su KDL-46EX725 e KDL-46HX855: nel visualizzatore di foto (DLNA o USB) il tasto 3D offre **solo la "conversione 2D→3D"**. Non esiste un'opzione fianco a fianco per le foto.
- Il formato standard delle fotocamere 3D, **MPO**, da chiavetta USB: indicato da Sony nelle tabelle di compatibilità dei modelli 2011 e segnalato come funzionante da alcuni proprietari. Test in corso.
- Foto e video anaglifi (occhiali rosso/ciano) possono essere convertiti in fianco a fianco: `tools/bravia_anaglyph.py`.

## Modelli interessati

- Testati: **KDL-46EX725** (2011), **KDL-46HX855** (2012)
- Stessa famiglia di scheda: KDL-46EX724, KDL-40HX853, KDL-55HX753
- Il problema del segnale 3D (SEI) riguarda qualsiasi televisore o proiettore che riconosce il 3D dal flusso (lo stesso sintomo è segnalato anche su Samsung).

## Documentazione (in inglese)

- [Panoramica del progetto](../../README.md)
- [Il segnale 3D spiegato](../3d-signalling-explainer.md)
- [Ricerca: foto 3D sui BRAVIA](../3d-photos-on-bravia.md)
- [Guida per replicarlo a casa](../build-your-own-bravia-portal.md)
- [Vecchi formati 3D (anaglifo, interlacciato)](../legacy-3d-formats.md)

---

*Tradotto dall'inglese il 18 settembre 2026. Le correzioni da parte di madrelingua sono benvenute: apri una issue.*
