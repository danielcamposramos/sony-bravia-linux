# TabNews post — draft (raw material, PT-BR, 2026-09-17)

# DOUTRINA: este texto é matéria-prima. O dono reescreve na própria
# voz antes de publicar — nada de texto de IA postado sem aprovação.
# Estudado o formato dos posts de maior sucesso do TabNews
# (fernandomorais "Baixei os 30 mil posts", andradeandrey "Analisei
# 6.380 posts"): long-form, primeira pessoa, números empilhados no
# opening, descobertas numeradas, caveats honestos, fechamento com
# artefatos reproduzíveis. Títulos com "?" rendem menos TabCoins.
# Melhor horário: segunda ~8h. NÃO usar tabelas markdown (o editor do
# TabNews não renderiza bem) — usar listas e blocos de código.

## Título — opções (sem "?")

1. **Os servidores da Sony ainda entregam os apps das TVs de 2011. Só o catálogo morreu — e o do Brasil sempre teve menos.** (fórmula fernandomorais: ação própria + achado provocativo, separados por ponto)
2. Minhas TVs Sony de 2011 têm processamento de 12 bits e 3D ativo. A Sony desligou todo o resto — então eu reconstruí, e o conserto do 3D foi mergeado no HandBrake.
3. A Sony localizou os apps dela em português, subiu nos servidores dela — e nunca listou para o Brasil. Eu documentei tudo, com os arquivos dela como evidência.

## O post

---

No dia 16 de setembro o HandBrake mergeou um pull request meu que faz o encoder x264 escrever um sinal de 3D que faltava nele desde 2013. O motivo do patch são as minhas duas TVs: uma **Sony KDL-46EX725 de 2011** e uma **KDL-46HX855 de 2012**.

Elas são pré-Android — a geração em que a BRAVIA ainda rodava um Linux próprio da Sony (kernel 2.6.35, glibc 2.7, MIPS, navegador Presto da era Opera). O hardware é absurdo para a época: X-Reality PRO com processamento de **12 bits**, **3D ativo** por óculos obturador, DLNA. A qualidade de imagem ainda hoje dá banho em muita TV nova de entrada. A resposta da Sony para esse hardware foi desligar tudo: os serviços "smart" morreram, os firmwares saíram do site de suporte (janeiro de 2022), e até as **fontes GPL** sumiram do serviço de distribuição de código da própria Sony.

Aí começa o mês de pesquisa que virou um repositório público, nove frentes abertas em projetos upstream e uma página de direitos do consumidor. Os números primeiro:

- **2 TVs**: KDL-46EX725 (2011, chassis AZ2-F) e KDL-46HX855 (2012, chassis AZ3F) — a geração EX7xx/HX8xx
- **137 de 168 URLs** dos servidores de conteúdo da Sony ainda respondem em 2026 — os arquivos não morreram, o catálogo sim
- **8 apps** no catálogo de widgets da Europa, **2** no do Brasil — e os apps "extras" estavam prontos e localizados em português nos servidores da Sony
- **798 modelos KDL** listados hoje no serviço de fontes GPL da Sony, **zero** da geração 2010–2012; um snapshot de 2014 mostra que a geração estava lá
- **1 PR mergeado no HandBrake** (#8100), 2 issues no FFmpeg, 1 issue + 1 PR no mpv em review, e mais x265, StaxRip, BD3D2MK3D e um guia no fórum do LTT

### 1. Os servidores da Sony ainda estão no ar — o que morreu foi o catálogo

A plataforma de widgets (AppliCast) buscava o conteúdo em `applicast.ga.sony.net`. Esse host **ainda responde em 2026** e ainda entrega os pacotes originais, com as assinaturas criptográficas originais. Cada país tinha um XML de catálogo que dizia à TV o que existia. O catálogo europeu lista 8 apps ([documento vivo](https://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_EU_ALL_eng.xml), [snapshot](https://web.archive.org/web/20260917210301/https://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_EU_ALL_eng.xml)); o brasileiro lista 2 ([documento vivo](https://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_LA_BRA_por.xml), [snapshot](https://web.archive.org/web/20260917204700/https://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_LA_BRA_por.xml)). Até o catálogo da geração anterior (2010) continua lá, datado internamente de 21/04/2010.

Ou seja: não é um caso de "arquivos perdidos". Foi desligada a camada que **avisava a TV que os apps existem**. O hardware continua perfeito; a TV só não sabe mais que tem conteúdo disponível.

### 2. O caso brasileiro: localizado, pronto, e nunca listado

Aqui está o achado que mais me incomodou. Dos apps que o Brasil não recebeu:

- Quatro deles (Calculadora, Alarme, Calendário, Relógio Analógico) **não têm nenhum texto dependente de idioma** — não havia motivo técnico para segurar
- Os manifests da própria Sony carregam **nomes localizados em 30 idiomas**, português incluso — `Calculadora` está lá no [info.xml vivo](https://applicast.ga.sony.net/WidgetBundles/SNY_BasicCalculator/info.xml) ([snapshot](https://web.archive.org/web/20260917204708/https://applicast.ga.sony.net/WidgetBundles/SNY_BasicCalculator/info.xml))
- O World Clock traz um dicionário de **31 idiomas** com as entradas em português completas — incluindo **"Rio de Janeiro" na lista de cidades de timezone** ([dic.txt vivo](https://applicast.ga.sony.net/WidgetBundles/SNY_WorldClock/dic.txt), [snapshot](https://web.archive.org/web/20260917204715/https://applicast.ga.sony.net/WidgetBundles/SNY_WorldClock/dic.txt))

A Sony **terminou** a localização, **subiu** nos servidores dela — e o catálogo brasileiro nunca listou esses apps. A TV foi abandonada nesse estado, e a evidência fica nos arquivos da própria Sony, que agora estão também no Internet Archive (os links em `http://` davam 503; em `https://` respondem).

### 3. O 3D que falhava em silêncio — e o conserto que acabou no HandBrake

Essas TVs só engatam o 3D automático a partir de um sinal: a SEI `frame_packing_arrangement` (H.264, payload 45) embutida no elementary stream. Elas **ignoram a tag StereoMode do Matroska** — a única que os rips padrão carregam. Resultado: todo vídeo 3D servido por DLNA roda "flat", sem mensagem de erro, num hardware que exibe 3D perfeito por outras entradas. O recurso não foi descontinuado oficialmente; ele simplesmente falha em silêncio.

O diagnóstico foi reverso (captura de tráfego + spec H.264) e o conserto é escrever a SEI que falta no encode. Eu levei diagnóstico + patch para as nove ferramentas do pipeline encode → remux → player:

- **HandBrake: [PR #8100 mergeado](https://github.com/HandBrake/HandBrake/pull/8100)** em 16/09/2026 — o encoder agora escreve o sinal; fecha a issue #5826 deles, aberta desde 2019
- **FFmpeg**: [bug #24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530) (CLI aborta com `-17 EEXIST`) e [feature #24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531) (bitstream filter para injetar a SEI)
- **mpv**: [issue #18489](https://github.com/mpv-player/mpv/issues/18489) + [PR #18490](https://github.com/mpv-player/mpv/pull/18490) em review
- **x265** ([#970](https://github.com/Multicorewareinc/x265/issues/970)), **StaxRip** ([#1873](https://github.com/staxrip/staxrip/issues/1873)), o fórum do **BD3D2MK3D** ([thread](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803756)) — onde o próprio autor confirmou que players de hardware "suportam apenas o frame-packing e ignoram o stereo-mode do MKV" — e o guia que o vídeo do teatro 3D do LTT prometeu e nunca entregou ([meu post](https://linustechtips.com/topic/1589907-i-built-a-3d-theater-in-my-basement/?do=findComment&comment=16936161))

Detalhe importante: **não tem DRM nem copy-protection nessa história**. O problema era um metadado ausente num arquivo do próprio dono, servido pro próprio dono.

### 4. As fontes GPL que a Sony listava em 2014 e não lista mais

O "Source Code Distribution Service" da Sony ([ainda no ar](https://oss.sony.net/Products/Linux/common/search.html), [snapshot](https://web.archive.org/web/20260901004026/https://oss.sony.net/Products/Linux/common/search.html)) diz, nas palavras da própria Sony, que fornece o fonte de "produtos Sony com Linux e outros softwares open source cuja licença exige a provisão do código-fonte", com cópias em mídia física "por três anos após o último envio do produto".

Hoje ele lista **798 modelos KDL — nenhum da geração 2010–2012**. Mas um [snapshot de outubro de 2014](https://web.archive.org/web/20141010061250/https://oss.sony.net/Products/Linux/TV/category03.html) mostra a geração listada nominalmente, incluindo KDL-46EX725 e KDL-46HX855. E a [página de download arquivada de 2015](https://web.archive.org/web/20150727011435/https://oss.sony.net/Products/Linux/TV/KDL-32CX520.html) lista **23 pacotes de fonte** para o grupo de modelos do EX725: kernel, toolchain MIPS, glibc, DirectFB, WebCore e JavaScriptCore — o ambiente de build completo.

Os links de download daquela página dão **404 no servidor vivo** hoje, e o Internet Archive capturou os índices, mas não os arquivos. O kernel que roda na TV existe, hoje, só no meu acervo offline — e a TV continua rodando os binários dele.

### 5. O que eu construí enquanto isso

Enquanto documentava o abandono, resolvi o lado prático: as TVs hoje navegam a biblioteca de mídia inteira do meu servidor (Debian + Serviio) e tocam **todos os formatos de áudio e os principais de vídeo**, com um app era-lean em Python puro stdlib, HTML server-rendered (o navegador Presto de 2011 não roda SPA), transcode sob demanda pro que a TV não toca nativo, tudo em systemd sobrevivendo a reboot. É o marco "VLC numa TV de 2011": atingido, dono-verificado, sem tocar num byte do firmware.

### 6. Verifique tudo você mesmo

Tudo acima está citado a documento da própria Sony (vivo + snapshot) ou a merge/issue de projeto independente:

- **Repositório**: [github.com/danielcamposramos/sony-bravia-linux](https://github.com/danielcamposramos/sony-bravia-linux) — o mapa dos fronts vivos e arquivados está no README
- **O diagnóstico técnico do 3D em profundidade**: `docs/3d-signalling-explainer.md` no repositório
- **A página de direitos do consumidor** (consumerrights.wiki, da FULU Foundation): [Sony BRAVIA pre-Android Linux TVs (2011–2012)](https://consumerrights.wiki/index.php?title=Sony_BRAVIA_pre-Android_Linux_TVs_%282011-2012%29) — atualizada com as evidências acima
- **O caso do catálogo brasileiro** detalhado: `docs/withheld-by-catalog.md`
- **A saga das fontes GPL**: `docs/oss-source-recovery.md`

### O que eu ainda não sei

Honestidade de método, porque o resto do post é todo receita: a remoção dos firmwares (janeiro de 2022) é observação minha, ainda sem fonte independente — estou atrás de um snapshot da página de suporte da época. E não há nada de DRM nenhuma parte disso; é hardware meu, LAN minha, mídia minha.

Se você tem um KDL-EX7xx/HX8xx (ou EX6xx/CX520/HX7xx da mesma geração) encostado: o painel e o 3D continuam ótimos, e o conserto do 3D já está no HandBrake — ou no injector de SEI do repositório, se você não quer re-encodar. Relatos de outros modelos são bem-vindos; a tabela de cobertura por geração vive no README.

---

## Notas de publicação (não fazem parte do post)

- **Reescrever na própria voz antes de postar** (doutrina do projeto; o TabNews é hostil a texto com cheiro de IA — ver o post "TabNews virou um amontoado de Pitch + Bolha de IA")
- **Horário**: segunda-feira ~8h tem a maior média de TabCoins (análise andradeandrey, 6.380 posts de 2025)
- **Título sem "?"**: títulos com interrogação rendem mais comentários, mas MENOS TabCoins
- **Formato**: o editor do TabNews não renderiza tabelas markdown bem — manter listas e links; o rascunho acima já evita tabelas
- **Links**: conferir os snapshots em `https://` (a forma `http://` dá 503); a página do wiki com parênteses precisa de `%28 %29` no link, já resolvido acima
- **Tamanho**: long-form performa (2.000+ palavras ~ 10,8 TabCoins de média vs 2,22 de posts curtos); este rascunho está em ~1.100 palavras de corpo — ao reescrever na própria voz, o caminho natural é expandir as seções 3 e 5 com detalhe técnico, que é o que a audiência de dev mais ranqueia