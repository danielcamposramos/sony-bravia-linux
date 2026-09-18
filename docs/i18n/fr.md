# Téléviseurs Sony BRAVIA 3D (modèles 2011–2012) : relire les films 3D et les photos 3D, un projet de réparation open source mené par le propriétaire

<!-- lang: fr · canonical source: ../../README.md (English) · translated 2026-09-18 -->

Ce projet redonne vie aux BRAVIA d'avant Android (série KDL, 2010–2012) après l'arrêt de leurs services en ligne par Sony, entièrement sur le réseau domestique du propriétaire. Aucun firmware n'est modifié, aucun DRM n'est touché. Le **droit à la réparation**, en pratique.

## Pourquoi votre film 3D s'affiche à plat

- Ces téléviseurs ne **basculent automatiquement en 3D** que si le **flux vidéo lui-même** contient l'information H.264 de « frame packing » (SEI).
- Les fichiers 3D courants (MKV côte à côte / dessus-dessous) ne portent qu'une étiquette dans le conteneur, qui disparaît dès qu'un serveur DLNA diffuse le fichier. Résultat : deux images côte à côte, pas de 3D.
- **La solution (sans perte, sans réencodage) :** `tools/bravia_sei3d.py` écrit la SEI une seule fois dans le fichier. Ensuite, le téléviseur passe tout seul en 3D, y compris en DLNA. HandBrake a intégré la fonction (PR #8100, dans la prochaine version). Le profil Serviio fourni ajoute la SEI automatiquement lors du transcodage.
- Yeux inversés ? Le téléviseur ne sait pas permuter gauche et droite, un filtre ffmpeg le fait (`stereo3d=sbsl:sbsr`).

## Photos 3D (côte à côte / JPS / MPO)

- Mesuré sur KDL-46EX725 et KDL-46HX855 : dans la visionneuse de photos (DLNA ou USB), la touche 3D ne propose **que la « conversion 2D→3D »**. Il n'existe aucune option côte à côte pour les photos.
- Le format standard des appareils photo 3D, **MPO**, depuis une clé USB : indiqué par Sony dans la liste de compatibilité des modèles 2011 et signalé par des propriétaires. Test en cours.
- Les photos et vidéos anaglyphes (lunettes rouge/cyan) peuvent être converties en côte à côte : `tools/bravia_anaglyph.py`.

## Modèles concernés

- Testés : **KDL-46EX725** (2011), **KDL-46HX855** (2012)
- Même famille de carte : KDL-46EX724, KDL-40HX853, KDL-55HX753
- Le problème du signal 3D (SEI) concerne tout téléviseur ou vidéoprojecteur qui détecte la 3D à partir du flux (le même symptôme est signalé chez Samsung).

## Documentation (en anglais)

- [Présentation du projet](../../README.md)
- [Le signal 3D expliqué](../3d-signalling-explainer.md)
- [Enquête : photos 3D sur BRAVIA](../3d-photos-on-bravia.md)
- [Guide pour reproduire chez soi](../build-your-own-bravia-portal.md)
- [Anciens formats 3D (anaglyphe, entrelacé)](../legacy-3d-formats.md)

---

*Traduit de l'anglais le 18 septembre 2026. Les corrections de locuteurs natifs sont les bienvenues : ouvrez une issue.*
