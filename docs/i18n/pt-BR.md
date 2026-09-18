# TVs Sony BRAVIA 3D (modelos 2011–2012): assistir de novo a filmes 3D e fotos 3D, um projeto de reparo open source mantido pelo próprio dono

<!-- lang: pt-BR · canonical source: ../../README.md (English) · translated 2026-09-18 -->

Este projeto devolve a vida às BRAVIA anteriores ao Android (série KDL, 2010–2012) depois que a Sony desligou os serviços online delas, tudo dentro da rede de casa do dono. Nenhum firmware é alterado e nenhum DRM é tocado. É o **direito ao reparo** na prática.

## Por que o seu filme 3D aparece chapado

- Essas TVs só **entram em 3D sozinhas** quando o **próprio fluxo de vídeo** traz a informação H.264 de "frame packing" (SEI).
- Os arquivos 3D comuns (MKV lado a lado / em cima e embaixo) só carregam uma etiqueta no contêiner, que se perde quando um servidor DLNA envia o arquivo. Resultado: duas imagens lado a lado, sem 3D.
- **A solução (sem perda, sem recodificar):** o `tools/bravia_sei3d.py` grava a SEI uma única vez no arquivo. Depois disso a TV entra em 3D sozinha, inclusive por DLNA. O HandBrake já incorporou a função (PR #8100, na próxima versão). O perfil do Serviio incluído adiciona a SEI automaticamente ao converter.
- Olhos trocados? A TV não deixa inverter esquerdo e direito, mas um filtro do ffmpeg deixa (`stereo3d=sbsl:sbsr`).

## Fotos 3D (lado a lado / JPS / MPO)

- Medido na KDL-46EX725 e na KDL-46HX855: no visualizador de fotos (DLNA ou USB), o botão 3D só oferece a **"conversão 2D→3D"**. Não existe opção lado a lado para fotos.
- O formato padrão das câmeras 3D, **MPO**, pelo pendrive: a Sony lista na tabela de compatibilidade dos modelos 2011 e há donos relatando que funciona. Teste em andamento.
- Fotos e vídeos anáglifos (óculos vermelho/ciano) podem ser convertidos para lado a lado: `tools/bravia_anaglyph.py`.

## Modelos afetados

- Testados: **KDL-46EX725** (2011), **KDL-46HX855** (2012)
- Mesma família de placa: KDL-46EX724, KDL-40HX853, KDL-55HX753
- O problema do sinal 3D (SEI) vale para qualquer TV ou projetor que detecta o 3D pelo fluxo de vídeo (o mesmo sintoma é relatado em TVs Samsung).

## Documentação (em inglês)

- [Visão geral do projeto](../../README.md)
- [O sinal 3D explicado](../3d-signalling-explainer.md)
- [Pesquisa: fotos 3D na BRAVIA](../3d-photos-on-bravia.md)
- [Guia para montar na sua casa](../build-your-own-bravia-portal.md)
- [Formatos 3D antigos (anáglifo, entrelaçado)](../legacy-3d-formats.md)

---

*Traduzido do inglês em 18 de setembro de 2026. Correções de falantes nativos são muito bem-vindas: abra uma issue.*
