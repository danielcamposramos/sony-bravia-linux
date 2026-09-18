# Televisores Sony BRAVIA 3D (modelos 2011–2012): volver a ver películas 3D y fotos 3D, un proyecto de reparación de código abierto mantenido por su propietario

<!-- lang: es · canonical source: ../../README.md (English) · translated 2026-09-18 -->

Este proyecto devuelve la vida a los BRAVIA anteriores a Android (serie KDL, 2010–2012) después de que Sony apagara sus servicios en línea, todo dentro de la red doméstica del propietario. No se modifica el firmware ni se toca ningún DRM. El **derecho a reparar**, en la práctica.

## Por qué tu película 3D se ve plana

- Estos televisores **cambian a 3D automáticamente** solo cuando el **propio flujo de vídeo** lleva la información H.264 de "frame packing" (SEI).
- Los archivos 3D habituales (MKV lado a lado / arriba-abajo) solo llevan una etiqueta en el contenedor, que se pierde en cuanto un servidor DLNA envía el archivo. Resultado: dos imágenes lado a lado, sin 3D.
- **La solución (sin pérdidas, sin recodificar):** `tools/bravia_sei3d.py` escribe la SEI una sola vez en el archivo. A partir de ahí el televisor pasa a 3D por sí solo, también por DLNA. HandBrake ya incorporó la función (PR #8100, en la próxima versión). El perfil de Serviio incluido añade la SEI automáticamente al transcodificar.
- ¿Ojos invertidos? El televisor no permite intercambiar izquierda y derecha, pero un filtro de ffmpeg sí (`stereo3d=sbsl:sbsr`).

## Fotos 3D (lado a lado / JPS / MPO)

- Medido en KDL-46EX725 y KDL-46HX855: en el visor de fotos (DLNA o USB) el botón 3D solo ofrece la **"conversión 2D→3D"**. No hay opción lado a lado para fotos.
- El formato estándar de las cámaras 3D, **MPO**, desde un pendrive USB: Sony lo incluye en la tabla de compatibilidad de los modelos 2011 y algunos propietarios informan que funciona. Prueba en curso.
- Las fotos y vídeos anaglifos (gafas rojo/cian) se pueden convertir a lado a lado: `tools/bravia_anaglyph.py`.

## Modelos afectados

- Probados: **KDL-46EX725** (2011), **KDL-46HX855** (2012)
- Misma familia de placa: KDL-46EX724, KDL-40HX853, KDL-55HX753
- El problema de la señal 3D (SEI) afecta a cualquier televisor o proyector que detecta el 3D a partir del flujo (el mismo síntoma se ha reportado en Samsung).

## Documentación (en inglés)

- [Presentación del proyecto](../../README.md)
- [La señal 3D explicada](../3d-signalling-explainer.md)
- [Investigación: fotos 3D en BRAVIA](../3d-photos-on-bravia.md)
- [Guía para reproducirlo en casa](../build-your-own-bravia-portal.md)
- [Formatos 3D antiguos (anaglifo, entrelazado)](../legacy-3d-formats.md)

---

*Traducido del inglés el 18 de septiembre de 2026. Las correcciones de hablantes nativos son bienvenidas: abre un issue.*
