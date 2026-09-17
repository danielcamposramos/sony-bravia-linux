# TabNews post — draft v2 (raw material, PT-BR, 2026-09-17)

# DOUTRINA: este texto é matéria-prima. O dono reescreve na própria
# voz antes de publicar — nada de texto de IA postado sem aprovação.
#
# v2 (revisão): abertura reordenada para o gancho mais forte (Rio de
# Janeiro), corpo expandido de ~1.100 para ~2.000 palavras (a faixa que
# rende ~10,8 TabCoins vs 2,22 de posts curtos), e três histórias
# técnicas que faltavam e que é o que audiência dev ranqueia: a
# reconstrução do schema perdido, a classe de arquivo invisível, e o
# custo real de manter o fonte no ar. Ver "Notas de revisão" no fim.
#
# Estudado o formato dos posts de maior sucesso do TabNews
# (fernandomorais "Baixei os 30 mil posts", andradeandrey "Analisei
# 6.380 posts"): long-form, primeira pessoa, números empilhados no
# opening, descobertas numeradas, caveats honestos, fechamento com
# artefatos reproduzíveis. Títulos com "?" rendem menos TabCoins.
# Melhor horário: segunda ~8h. NÃO usar tabelas markdown (o editor do
# TabNews não renderiza bem) — usar listas e blocos de código.

## Título — opções (sem "?")

1. **A Sony traduziu os apps da TV para português, subiu no servidor dela — e nunca listou para o Brasil. Achei o "Rio de Janeiro" no código.** (gancho nacional + evidência concreta)
2. **Os servidores da Sony ainda entregam os apps das TVs de 2011. Só o catálogo morreu — e o do Brasil sempre teve menos.** (fórmula fernandomorais: ação própria + achado provocativo)
3. Minhas TVs Sony de 2011 têm 3D ativo e 12 bits. A Sony desligou o resto — eu reconstruí, e o conserto do 3D foi mergeado no HandBrake.

## O post

---

Procurando por que o app de Relógio Mundial nunca apareceu na minha TV, abri o dicionário de tradução que a Sony publica no servidor dela. Trinta e uma línguas. O português está completo: os dias da semana abreviados, as mensagens de erro, e a lista de cidades de fuso horário — com **"Rio de Janeiro"** lá dentro.

Esse app nunca foi oferecido no Brasil.

A tradução estava pronta. Estava paga. Estava **no servidor da Sony, onde continua até hoje**. O que faltou foi uma linha num arquivo XML de catálogo dizendo à TV brasileira que o app existia.

Isso é o meio da história. O começo são duas TVs: uma **Sony KDL-46EX725 de 2011** e uma **KDL-46HX855 de 2012**. Pré-Android — a geração em que a BRAVIA rodava um Linux próprio da Sony (kernel 2.6.35, glibc 2.7, MIPS, navegador Presto da era Opera). Hardware absurdo para a época: X-Reality PRO com processamento de **12 bits**, **3D ativo** por óculos obturador, DLNA. A imagem ainda hoje dá banho em muita TV nova de entrada.

O fim, por enquanto, é que no dia 16 de setembro o **HandBrake mergeou um pull request meu** que faz o encoder x264 escrever um sinal de 3D que faltava nele desde 2013 — 81 minutos entre abrir e mergear, o tempo do CI rodar.

Os números, antes das histórias:

- **137 de 168 URLs** dos servidores de conteúdo da Sony ainda respondem em 2026 — os arquivos não morreram, o catálogo sim
- **8 apps** no catálogo de widgets da Europa, **2** no do Brasil, mesmo host, mesma geração de chassis
- **798 modelos KDL** listados hoje no serviço de fontes GPL da Sony, **zero** da geração 2010–2012 — um snapshot de 2014 mostra a geração lá, nominalmente
- **23 pacotes de fonte** era o que a Sony publicava para o meu grupo de modelos: kernel, toolchain MIPS, glibc, DirectFB, WebCore. Todos dão 404 hoje
- **~US$ 0,12 por mês** é o que custaria hospedar tudo isso em 2026
- **9 frentes** abertas upstream: 1 PR mergeado, 2 issues no FFmpeg, 1 issue + 1 PR no mpv, x265, StaxRip, BD3D2MK3D, LTT

### 1. Os servidores ainda estão no ar — o que morreu foi o catálogo

A plataforma de widgets (AppliCast) buscava conteúdo em `applicast.ga.sony.net`. Esse host **ainda responde em 2026** e ainda entrega os pacotes originais, com as assinaturas criptográficas originais intactas. Cada país tinha um XML de catálogo que dizia à TV o que existia.

O catálogo europeu lista 8 apps ([vivo](https://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_EU_ALL_eng.xml), [snapshot](https://web.archive.org/web/20260917210301/https://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_EU_ALL_eng.xml)); o brasileiro lista 2 ([vivo](https://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_LA_BRA_por.xml), [snapshot](https://web.archive.org/web/20260917204700/https://applicast.ga.sony.net/WidgetContents/SNY_WidgetGallery/AZ3/Catalog_LA_BRA_por.xml)). Até o catálogo da geração de 2010 continua lá, datado internamente de 21/04/2010 — um arquivo de dezesseis anos ainda sendo servido.

Não é um caso de arquivo perdido. Foi desligada a camada que **avisa a TV que o conteúdo existe**.

### 2. O caso brasileiro: pronto, traduzido, e nunca listado

Dos cinco apps que o Brasil não recebeu:

- Quatro (Calculadora, Alarme, Calendário, Relógio Analógico) **não têm nenhum texto dependente de idioma**. Uma calculadora não tem palavra nenhuma. Não existia custo de localização a economizar
- Os manifests da própria Sony carregam **nomes localizados em 30 idiomas**, português incluso — `Calculadora` está lá no [info.xml vivo](https://applicast.ga.sony.net/WidgetBundles/SNY_BasicCalculator/info.xml) ([snapshot](https://web.archive.org/web/20260917204708/https://applicast.ga.sony.net/WidgetBundles/SNY_BasicCalculator/info.xml))
- O Relógio Mundial traz o dicionário de **31 idiomas** com o português completo, Rio de Janeiro incluído ([dic.txt vivo](https://applicast.ga.sony.net/WidgetBundles/SNY_WorldClock/dic.txt), [snapshot](https://web.archive.org/web/20260917204715/https://applicast.ga.sony.net/WidgetBundles/SNY_WorldClock/dic.txt))

Eu apontei a TV para um catálogo servido por mim, com os arquivos originais da Sony. **Os cinco apps instalaram e rodam.** As assinaturas validam — porque os arquivos são da Sony, byte a byte, baixados do servidor da Sony. Não tem nada quebrado, nada forjado, nada de DRM. Só um catálogo diferente.

### 3. O schema que não existe mais em lugar nenhum

O Relógio Mundial instalou e abriu pedindo configuração — e a tela de configuração vinha vazia. O motivo é a parte que acho que mais interessa a quem programa.

Widgets dessa era declaram a tela de ajustes num `preference.xml` que **o engine da TV lê, não o widget**. Esse arquivo não está no manifest assinado e **nenhum código do bundle o referencia**. Ou seja: é invisível para qualquer scraper que siga referências. Você só acha pedindo pelo nome.

Para o Alarme, o arquivo ainda estava no servidor da Sony — baixei, servi, funcionou. Para o Relógio Mundial, ele **não existe mais em lugar nenhum**: nem no servidor vivo, nem no Internet Archive, nem em nenhum mirror. O widget sobreviveu; o schema de configuração dele não.

Então reconstruí a partir do código do próprio widget, que diz exatamente o que espera:

```js
/******* Get Preference Setting from preference.xml *******/
function checkPreference() {
    var tmp_timezone = getStoredValue("Item1");
    var tmp_dst      = getStoredValue("Item2");
    var tmp_ampm     = getStoredValue("Item3");
    if (tmp_timezone == null) { Error_Message(1); }
```

Três slots, e o resto do arquivo fixa os domínios. `gmt_hour = local_time - timezone - dstArray[0]`, mais testes de sinal `if (timezone>0)` — é aritmética com sinal, então `Item1` é **offset de GMT em horas**, não índice de cidade. As constantes se nomeiam sozinhas: `_DST_OFF=0/_DST_ON=1`, `_AMPM_OFF=0/_AMPM_ON=1`.

Essa distinção importa: ler `Item1` como índice de cidade daria um XML que instala, parseia e produz um relógio **silenciosamente quatro horas errado** — o tipo de bug que você descobre meses depois e nunca rastreia.

1.681 bytes de XML escrito à mão, nenhum arquivo assinado tocado, assinatura original da Sony continua validando. A tela de ajustes abriu com as três opções e o relógio funcionou.

Foi a primeira coisa do projeto que não foi *recuperada*, e sim **reconstruída** — ler as expectativas da máquina no código dela e escrever a metade que faltava.

### 4. A lição de scraping: arquivos que ninguém referencia

O relógio voltou a configurar e ainda mostrava um ícone de "carregando" no lugar da arte. Mesma classe de problema, causa diferente.

Widgets dessa era montam quase todo caminho de asset por concatenação:

```js
loadImage(node, "./parts/flags/tz_" + (offset + 11) + ".png")
loadImage(node, "./parts/FullScreen/Daylight/Lightmap_" + month + "/" + (i+1) + ".png")
```

O nome do arquivo **não existe como literal em lugar nenhum do código**. `grep` por `.png` devolve meia dúzia de fundos e setas, e nenhum dos 22 tiles do mapa-múndi, nenhuma das 23 bandeiras, nenhum dos 288 frames do terminador de luz do dia. Listagem de diretório é negada. Não tem como descobrir por leitura.

A solução é percorrer o **template** em vez do literal: pegar os fragmentos entre aspas ao redor de cada `+` e expandir sobre o que o código em volta consegue produzir. Isso recuperou **349 arquivos** de uma vez só nesse widget, e 646 no conjunto todo.

E o erro que quase passou: expandi meses `1..12` e vieram onze pastas. Quase escrevi "dezembro sumiu do servidor da Sony". Não sumiu — `Date.getMonth()` do JavaScript é **zero-based**, o intervalo real é `Lightmap_0..11`, e a pasta que eu nunca pedi era **janeiro**. `Lightmap_0` dá 200; `Lightmap_12` dá 403.

Um conjunto curto que parece completo é pior que um buraco óbvio. A regra que ficou: **sempre sonde um índice fora do intervalo que você assumiu, e deixe o 403 do servidor te dizer onde é a borda.**

### 5. O 3D que falhava em silêncio — e o conserto que acabou no HandBrake

Essas TVs engatam 3D automático a partir de um sinal só: a SEI `frame_packing_arrangement` (H.264, payload 45) embutida no elementary stream. Elas **ignoram a tag StereoMode do Matroska** — a única que os rips padrão carregam. Todo vídeo 3D servido por DLNA roda flat, sem erro, num hardware que exibe 3D perfeito por outras entradas.

Na minha biblioteca: **43 de 44 títulos** tinham só a tag de container, e **0 de 44** tinham a SEI. Todos flat. O recurso nunca foi descontinuado oficialmente — ele só falha calado.

Levei diagnóstico + patch para o pipeline inteiro, encode → remux → player:

- **HandBrake: [PR #8100 mergeado](https://github.com/HandBrake/HandBrake/pull/8100)** em 16/09/2026 — o encoder agora escreve o sinal, fechando a issue #5826 deles
- **FFmpeg**: [bug #24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530) — arquivos com a tag *e* a SEI fazem a CLI abortar com `-17 EEXIST`, um bug de decode que o tracker deles não tinha — e [feature #24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531), um bitstream filter para injetar a SEI sem re-encodar
- **mpv**: [issue #18489](https://github.com/mpv-player/mpv/issues/18489) + [PR #18490](https://github.com/mpv-player/mpv/pull/18490), em review
- **x265** ([#970](https://github.com/Multicorewareinc/x265/issues/970)), **StaxRip** ([#1873](https://github.com/staxrip/staxrip/issues/1873)), e o fórum do **BD3D2MK3D** ([thread](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803756)), onde o próprio autor confirmou que players de hardware "suportam apenas o frame-packing e ignoram o stereo-mode do MKV" — e disse que o Samsung dele faz igual

De novo: **não tem DRM nessa história**. Era um metadado ausente num arquivo do próprio dono, servido pelo próprio dono, para a TV do próprio dono.

### 6. As fontes GPL, e quanto custaria mantê-las

O "Source Code Distribution Service" da Sony ([vivo](https://oss.sony.net/Products/Linux/common/search.html), [snapshot](https://web.archive.org/web/20260901004026/https://oss.sony.net/Products/Linux/common/search.html)) diz, nas palavras da Sony, que fornece o fonte de produtos "com Linux e outros softwares open source cuja licença exige a provisão do código-fonte", com cópias em mídia física "por três anos após o último envio do produto".

Hoje ele lista **798 modelos KDL — nenhum da geração 2010–2012**. Um [snapshot de outubro de 2014](https://web.archive.org/web/20141010061250/https://oss.sony.net/Products/Linux/TV/category03.html) mostra a geração listada nominalmente, KDL-46EX725 e KDL-46HX855 inclusos. A [página de download arquivada de 2015](https://web.archive.org/web/20150727011435/https://oss.sony.net/Products/Linux/TV/KDL-32CX520.html) lista os **23 pacotes**: kernel, `sony-cross-gcc-4.1.2`, glibc 2.7, DirectFB 1.3.0, WebCore, JavaScriptCore — o ambiente de build completo.

Todos dão **404 hoje**. O Internet Archive salvou os índices, não os arquivos. Não achei mirror no GitHub. O kernel existe, hoje, só no meu acervo offline.

E aqui vai a conta que eu acho que fecha o argumento. O kernel comprime para ~96 MB. O conjunto de pacotes é compartilhado entre grupos de modelos — 83 pacotes distintos cobrem toda a era KDL. **O corpus GPL inteiro dessa geração de TVs cabe em poucos gigabytes.** Em 2026 isso custa **US$ 0,10–0,15 por mês** em object storage, ou zero no Internet Archive e no GitHub Releases.

Ou seja: a obrigação de três anos não venceu por ser cara. Venceu no prazo, num momento em que cumpri-la custaria um café por ano — enquanto o mesmo serviço segue rodando para 798 outros modelos. O prazo é legítimo e é da Sony. O que eu acho discutível é a **proporcionalidade**: uma regra desenhada quando distribuir fonte significava prensar e postar mídia física hoje aposenta documentação cujo custo de armazenamento caiu quatro ordens de grandeza — de hardware que ainda está ligado na sala das pessoas.

### 7. O que eu construí no meio disso

As TVs hoje navegam a biblioteca inteira do meu servidor (Debian + Serviio) e tocam **todo formato de áudio da biblioteca** e os principais de vídeo. O app é um arquivo Python só, stdlib pura, HTML renderizado no servidor — o Presto de 2011 não roda SPA, não tem CORS, e estoura memória com página grande ("page too big to display" é uma tela real).

As restrições viraram o design:

- o player da era aceita **exatamente MP4 progressivo faststart**; TS ao vivo (o que o transcode DLNA padrão serve) é recusado — por isso a esteira de transcode vive no app, não no Serviio
- o Serviio amarra as URLs de `res` ao IP de quem navegou, então o app **faz proxy da mídia através de si mesmo** para que cliente de browse e cliente de fetch sejam o mesmo
- FLAC/WMA/OGG/MPC/WV saem por um pipe de conversão para MP3 ao vivo; MKV/AVI/WMV viram MP4 faststart em cache sob demanda
- navegação por setas do controle remoto, tudo em systemd, sobrevivendo a reboot

É o marco "VLC numa TV de 2011": atingido, verificado no aparelho, sem tocar num byte de firmware.

### 8. Verifique você mesmo

Tudo acima está citado a documento da própria Sony (vivo + snapshot) ou a merge/issue de projeto independente:

- **Repositório**: [github.com/danielcamposramos/sony-bravia-linux](https://github.com/danielcamposramos/sony-bravia-linux) — o mapa dos fronts vivos e arquivados está no README
- **Página de direitos do consumidor** (consumerrights.wiki, FULU Foundation): [Sony BRAVIA pre-Android Linux TVs (2011–2012)](https://consumerrights.wiki/index.php?title=Sony_BRAVIA_pre-Android_Linux_TVs_%282011-2012%29)
- **O caso do catálogo brasileiro**: `docs/withheld-by-catalog.md`
- **A saga das fontes GPL**: `docs/oss-source-recovery.md`
- **A reconstrução do schema**: `docs/worldclock-schema-reconstruction.md`
- **O diagnóstico do 3D**: `docs/3d-signalling-explainer.md`

### O que eu ainda não sei

Honestidade de método, porque o resto é receita:

- A remoção dos firmwares (janeiro de 2022) é **observação minha, ainda sem fonte independente**. Procurei snapshot da página de suporte da época e não achei
- Não sei **quando** a geração saiu do serviço de fontes. Sei que estava em 2014 e não está hoje; a cobertura do Archive entre 2016 e 2024 é rala
- Os pacotes com patch da Sony (`sony-target-dev-*`) parecem perdidos. Se alguém tiver um mirror, é o buraco que vale preencher

Se você tem um KDL-EX7xx/HX8xx (ou EX6xx/CX520/HX7xx da mesma geração) encostado: o painel e o 3D continuam ótimos, o conserto do 3D já está no HandBrake, e um manual de serviço da Sony cobre cinco tamanhos de tela do mesmo chassis — ou seja, o que vale para a minha TV vale para a geração inteira. Relatos de outros modelos são bem-vindos.

---

## Notas de revisão (v2 — não fazem parte do post)

O que mudou do v1, e por quê:

1. **Abertura reordenada.** O v1 abria com o HandBrake (credencial forte, mas abstrata). O v2 abre com o "Rio de Janeiro" no dicionário — gancho nacional, concreto, e é a única parte da história que um leitor brasileiro sente no estômago. A credencial do HandBrake entra logo depois, como fecho do parágrafo de abertura, que é onde ela funciona melhor: prova que o autor não é só indignado, é alguém cujo diagnóstico passou por review de terceiros.
2. **Duas seções técnicas novas (3 e 4).** A reconstrução do `preference.xml` e a classe de arquivo invisível. São as histórias mais "dev" do projeto — código real, raciocínio real, e um erro meu documentado (o off-by-one do mês zero-based). Audiência de dev ranqueia processo e erro admitido acima de resultado.
3. **A conta de custo (seção 6).** "US$ 0,12 por mês" é o número mais citável do post inteiro e fecha o argumento sem precisar de indignação.
4. **Seção 7 expandida** com as restrições técnicas reais (faststart, o proxy por causa do bind de IP, o limite de memória do Presto). No v1 era um parágrafo genérico.
5. **Tamanho**: ~1.100 → ~2.000 palavras, a faixa que a análise do andradeandrey aponta como a de maior média de TabCoins.

Pendências de publicação:

- **Reescrever na própria voz antes de postar.** Continua valendo, e mais ainda no v2: quanto melhor o texto, mais suspeito ele fica se não soar como você
- **Horário**: segunda ~8h
- **Título**: sem "?" — a opção 1 é a mais forte para o TabNews; a 2 é a mais segura
- **Formato**: sem tabelas markdown; o rascunho já evita
- **DECISÃO PENDENTE — assumir ou não o uso de IA.** O TabNews está saturado de texto com cheiro de IA e reage mal. Três caminhos: (a) não mencionar e reescrever a ponto de soar inteiramente seu; (b) uma linha honesta no fim ("pesquisa feita com parceiros de IA sob direção e verificação minha no hardware"); (c) transformar isso em parte do post. Vale lembrar que essa questão já apareceu no upstream — num dos PRs a discussão saiu do código e foi para a autoria do texto, e o que resolveu foi responder só com fato técnico verificável. O mesmo princípio serve aqui: **o post é verificável linha a linha, e é isso que o defende.** A escolha é sua; a (b) é a que eu acho mais difícil de usar contra você depois
