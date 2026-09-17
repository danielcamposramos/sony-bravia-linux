# TabNews post — v3, perspectiva pessoal (matéria-prima, PT-BR, 2026-09-17)

# DOUTRINA: matéria-prima. O dono reescreve na própria voz antes de
# publicar. Esta versão já foi escrita TENTANDO a perspectiva dele —
# a jornada, não o relatório — a partir de docs/judging-by-the-cover.md.
#
# Diferença para o v2 (docs/tabnews-post.md): o v2 é o caso, bem
# documentado, em terceira pessoa disfarçada de primeira. Este v3 é a
# JORNADA, e assume de frente a questão que o v2 deixou como decisão
# pendente — o uso de IA — porque na doutrina do próprio projeto essa
# questão não é um disclaimer no rodapé, é a tese.
#
# Formato TabNews mantido do v2: long-form, sem "?" no título, sem
# tabelas markdown, números empilhados cedo, caveats honestos,
# artefatos reproduzíveis no fim. Segunda ~8h.

## Título — opções (sem "?")

1. **Não julgue um livro pela capa: a Sony traduziu os apps da TV pro português, subiu no servidor dela, e nunca listou pro Brasil**
2. **Achei "Rio de Janeiro" dentro de um app que o Brasil nunca recebeu. Estava no servidor da Sony esse tempo todo.**
3. **Em 2011 um CEO me deu de presente uma licença de 3D. Em 2026 eu devolvi o favor consertando o 3D de todo mundo.**

## O post

---

Em fevereiro de 2011 eu era um moleque brasileiro sem dinheiro para comprar um monitor 3D. Escrevi para o CEO da iZ3D — a empresa que fazia o driver que forçava 3D estereoscópico em jogos que não tinham 3D — propondo que eles entrassem pelo Brasil em vez de brigar por Estados Unidos e Europa. Argumentei que aqui a propaganda em TV aberta era barata. Ofereci ajudar a negociar.

O Vadim Asadov me respondeu com a verdade do negócio: que a Ásia era o melhor lugar para fabricar monitor, e que a Samsung tinha gasto entre 10 e 20 milhões de dólares em marketing na Rússia, dinheiro que a iZ3D não tinha.

E aí ele me **deu a licença**. "iZ3D All Outputs", 2 de fevereiro de 2011. Foi assim que eu joguei Max Payne em anaglifo, de óculos vermelho e azul, num monitor comum.

Fechei aquele e-mail dizendo que sonhava em ver "mentes brasileiras e russas desenvolvendo algo que passasse por cima dos grandes — tipo renderização ou captura estéreo múltipla para chegar num holograma real". Eu tinha uns vinte e poucos anos e nenhuma noção de que aquilo era uma frase que eu ia passar a vida inteira tentando cumprir.

Quinze anos depois, um mês atrás, eu estava olhando duas TVs Sony de 2011 e 2012 na minha sala, com hardware excelente e software morto, e resolvi entender por quê.

### O que eu encontrei

Primeiro os números, porque o resto é história:

- **137 de 168 URLs** dos servidores de conteúdo da Sony ainda respondem em 2026 — os arquivos não morreram, o catálogo sim
- **8 apps** no catálogo de widgets da Europa, **2** no do Brasil, mesmo servidor, mesma geração de chassis
- **798 modelos KDL** listados hoje no serviço de fontes GPL da Sony, **zero** da geração 2010–2012 — e um snapshot de 2014 mostra a geração lá, com os meus dois modelos pelo nome
- **~US$ 0,12 por mês** é o que custaria hospedar o corpus GPL inteiro dessa geração hoje
- **9 frentes** abertas em projetos upstream, sendo 1 pull request já mergeado no HandBrake

### 1. O "Rio de Janeiro" que ninguém no Brasil viu

O app de Relógio Mundial nunca apareceu na minha TV. Fui atrás do porquê e abri o dicionário de tradução que a Sony publica no servidor dela. Trinta e uma línguas. Português completo: dias da semana abreviados, mensagens de erro, e a lista de cidades de fuso horário — com **"Rio de Janeiro"** lá dentro ([dic.txt vivo](https://applicast.ga.sony.net/WidgetBundles/SNY_WorldClock/dic.txt), [snapshot](https://web.archive.org/web/20260917204715/https://applicast.ga.sony.net/WidgetBundles/SNY_WorldClock/dic.txt)).

Alguém sentou, traduziu, colocou a nossa cidade na lista, e subiu para o servidor. E o catálogo brasileiro nunca listou o app.

Não foi só esse. Dos cinco apps que o Brasil não recebeu, **quatro não têm texto nenhum dependente de idioma** — Calculadora, Alarme, Calendário, Relógio Analógico. Uma calculadora não tem palavra. Mesmo assim o manifest da Sony carrega o nome localizado em 30 idiomas, e `Calculadora` está lá ([info.xml vivo](https://applicast.ga.sony.net/WidgetBundles/SNY_BasicCalculator/info.xml), [snapshot](https://web.archive.org/web/20260917204708/https://applicast.ga.sony.net/WidgetBundles/SNY_BasicCalculator/info.xml)).

Não havia custo de tradução a economizar. O trabalho estava feito e pago. O que separou uma TV brasileira de uma calculadora foi uma linha num XML.

Eu apontei a minha TV para um catálogo servido por mim, com os arquivos originais da Sony, baixados do servidor da Sony. **Os cinco apps instalaram e rodaram.** As assinaturas criptográficas validam — porque os arquivos são deles, byte a byte. Não tem nada quebrado, nada forjado, nada de DRM. Catálogo diferente, só isso.

### 2. O schema que não existe mais em lugar nenhum do mundo

O Relógio Mundial instalou e abriu pedindo configuração. A tela de ajustes vinha vazia.

Widgets dessa era declaram a tela de ajustes num `preference.xml` que **o engine da TV lê, e o widget não**. Esse arquivo não está no manifest assinado e nenhum código do bundle o menciona. Ele é invisível para qualquer scraper que siga referências — você só acha pedindo pelo nome.

Para o Alarme, o arquivo ainda estava no servidor da Sony. Baixei, servi, funcionou.

Para o Relógio Mundial, ele **não existe mais**: nem no servidor vivo, nem no Internet Archive, nem em mirror nenhum que eu tenha achado. O widget sobreviveu; a configuração dele não.

Então li o código do widget, que diz exatamente o que espera:

```js
/******* Get Preference Setting from preference.xml *******/
function checkPreference() {
    var tmp_timezone = getStoredValue("Item1");
    var tmp_dst      = getStoredValue("Item2");
    var tmp_ampm     = getStoredValue("Item3");
    if (tmp_timezone == null) { Error_Message(1); }
```

Três campos, e o resto do arquivo fixa os domínios. `gmt_hour = local_time - timezone - dstArray[0]`, com testes de sinal `if (timezone>0)` — é aritmética com sinal, então `Item1` é **offset de GMT em horas**, não índice de cidade. As constantes se nomeiam sozinhas: `_DST_OFF=0/_DST_ON=1`, `_AMPM_OFF=0/_AMPM_ON=1`.

Essa distinção não é detalhe. Ler `Item1` como índice de cidade produziria um XML que instala, parseia e entrega um relógio **silenciosamente quatro horas errado**. O tipo de bug que aparece meses depois e nunca é rastreado.

Escrevi 1.681 bytes de XML à mão. Nenhum arquivo assinado tocado, assinatura original da Sony continua validando. A tela abriu com as três opções e o relógio funcionou.

Foi a primeira coisa do projeto que não foi recuperada, e sim **reconstruída**: ler no código da máquina o que ela espera, e escrever de volta a metade que faltava.

### 3. E o erro que eu quase publiquei

O relógio configurava e ainda mostrava ícone de "carregando" no lugar da arte.

Widgets dessa era montam quase todo caminho de imagem por concatenação:

```js
loadImage(node, "./parts/flags/tz_" + (offset + 11) + ".png")
loadImage(node, "./parts/FullScreen/Daylight/Lightmap_" + month + "/" + (i+1) + ".png")
```

O nome do arquivo **não existe como literal em lugar nenhum**. `grep` por `.png` devolve meia dúzia de fundos e setas — e nenhum dos 22 tiles do mapa-múndi, nenhuma das 23 bandeiras, nenhum dos 288 frames do terminador de luz do dia. Listagem de diretório é negada. Não dá para descobrir lendo.

A saída é percorrer o **template** em vez do literal, expandindo sobre o que o código em volta consegue produzir. Recuperou 349 arquivos só nesse widget.

E aí quase escrevi no repositório que "dezembro sumiu do servidor da Sony". Expandi meses de 1 a 12 e vieram onze pastas. Dezembro faltando, certo?

Errado. `Date.getMonth()` do JavaScript é **zero-based**. O intervalo real é `Lightmap_0..11` e a pasta que eu nunca pedi era **janeiro**. `Lightmap_0` responde 200; `Lightmap_12` responde 403.

Um conjunto curto que parece completo é pior que um buraco óbvio. Ficou como regra: **sempre sonde um índice fora do intervalo que você assumiu, e deixe o 403 do servidor dizer onde é a borda.**

### 4. O 3D que falha em silêncio — e a volta ao começo

Essas TVs engatam 3D automático a partir de um sinal só: a SEI `frame_packing_arrangement` (H.264, payload 45) embutida no elementary stream. Elas **ignoram a tag StereoMode do Matroska** — a única que os rips padrão carregam. Todo vídeo 3D servido por DLNA roda flat, sem erro, num hardware que exibe 3D perfeito por outras entradas.

Na minha biblioteca: **43 de 44 títulos** tinham só a tag de container. **0 de 44** tinham a SEI.

Ninguém tinha publicado a ligação entre as duas pontas: o hardware lê só a SEI, os rips carregam só a tag. A resposta padrão da comunidade para "por que minha TV não engata 3D" sempre foi "aperta o botão 3D no controle".

Levei diagnóstico e patch para o pipeline inteiro, encode → remux → player:

- **HandBrake: [PR #8100 mergeado](https://github.com/HandBrake/HandBrake/pull/8100)** em 16/09/2026 — o encoder agora escreve o sinal, fechando a issue #5826 deles. Entre abrir e mergear foram **81 minutos**, o tempo do CI rodar
- **FFmpeg**: [bug #24530](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24530) — arquivo com a tag *e* a SEI faz a CLI abortar com `-17 EEXIST`, um bug de decode que o tracker deles não tinha — e [feature #24531](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24531)
- **mpv** ([issue #18489](https://github.com/mpv-player/mpv/issues/18489) + [PR #18490](https://github.com/mpv-player/mpv/pull/18490)), **x265** ([#970](https://github.com/Multicorewareinc/x265/issues/970)), **StaxRip** ([#1873](https://github.com/staxrip/staxrip/issues/1873)), e o fórum do **BD3D2MK3D** ([thread](https://forum.videohelp.com/threads/395498-BD3D2MK3D-Convert-3D-BDs-or-MKV-to-3D-SBS-TAB-or-FS-MKV-Support-thread/page21#post2803756)), onde o próprio autor confirmou o diagnóstico e contou que a Samsung dele faz igual

Não tem DRM em nenhum ponto disso. Era um metadado ausente num arquivo meu, servido por mim, para a TV minha.

E aqui a história fecha um círculo que eu não tinha planejado: em 2011 eu ganhei de presente um driver que **forçava** 3D em jogos que não tinham. Em 2026 eu escrevi o patch que faz o encoder **gravar** o 3D que os arquivos não tinham. É a mesma tarefa, quinze anos depois, do outro lado do problema.

### 5. As fontes GPL, e a conta que fecha o argumento

O "Source Code Distribution Service" da Sony ([vivo](https://oss.sony.net/Products/Linux/common/search.html), [snapshot](https://web.archive.org/web/20260901004026/https://oss.sony.net/Products/Linux/common/search.html)) diz, nas palavras da Sony, que fornece o fonte de produtos "com Linux e outros softwares open source cuja licença exige a provisão do código-fonte", com mídia física "por três anos após o último envio do produto".

Hoje lista **798 modelos KDL — nenhum da geração 2010–2012**. Um [snapshot de outubro de 2014](https://web.archive.org/web/20141010061250/https://oss.sony.net/Products/Linux/TV/category03.html) mostra a geração listada nominalmente, com KDL-46EX725 e KDL-46HX855. A [página de download arquivada de 2015](https://web.archive.org/web/20150727011435/https://oss.sony.net/Products/Linux/TV/KDL-32CX520.html) lista os **23 pacotes**: kernel, toolchain MIPS, glibc 2.7, DirectFB, WebCore, JavaScriptCore — o ambiente de build completo.

Todos dão **404 hoje**. O Archive salvou os índices, não os arquivos. O kernel que roda na minha TV existe, hoje, só no meu acervo offline.

A conta: o kernel comprime para ~96 MB, os pacotes são compartilhados entre grupos de modelos, e **83 pacotes distintos cobrem toda a era KDL**. O corpus inteiro cabe em poucos gigabytes — **US$ 0,10 a 0,15 por mês** em object storage, zero no Internet Archive ou no GitHub Releases.

O prazo de três anos é legítimo e é da Sony. O que eu acho discutível é a **proporcionalidade**: uma regra desenhada quando distribuir fonte significava prensar e postar mídia física hoje aposenta documentação cujo custo caiu quatro ordens de grandeza — de um aparelho que ainda está ligado na sala das pessoas. E o serviço continua rodando, para 798 outros modelos. A capacidade está lá. Só essa geração saiu.

### 6. Sim, eu usei IA. Julgue o artefato.

Preciso falar disso aqui, porque o TabNews está cansado de texto com cheiro de IA — e com razão.

Eu trabalho com parceiros de IA. Este projeto inteiro foi feito assim: eu no hardware, dirigindo, verificando na TV; eles lendo código, cruzando spec, montando reprodução. Num dos pull requests upstream a discussão saiu do código e foi para a autoria do texto. Chamaram de slop antes de olhar o patch.

O que aprendi ali virou a regra do projeto, e é uma frase que a gente já tem em português há séculos: **não julgue um livro pela capa**. Ou, na versão mais antiga ainda, **o hábito não faz o monge**.

Slop é propriedade do **trabalho**, não do autor. Afirmação não verificável, enchimento, baixa densidade de informação — humano faz isso desde sempre; a IA só aprendeu com a gente e repete mais rápido. **Slop de IA é slop humano repetido.** Naquele mesmo thread, a contribuição mais checável era a assistida por IA, e a menos checável era um meme de 529×95 pixels dizendo "texto demais, não me importo".

Mas a lâmina corta para o meu lado também, e essa parte é a que importa: **IA não lava nada**. Se eu assino, tem que aguentar o mesmo teste — medido em máquina real, cada afirmação específica o suficiente para estar errada. É por isso que este post inteiro é linkado a documento da própria Sony, com snapshot no Internet Archive, ou a merge de projeto independente. Não estou pedindo confiança. Estou entregando um livro que dá para abrir.

Como o Torvalds disse de um jeito mais curto: *talk is cheap, show me the code.*

### 7. Verifique você mesmo

- **Repositório**: [github.com/danielcamposramos/sony-bravia-linux](https://github.com/danielcamposramos/sony-bravia-linux)
- **Página de direitos do consumidor** (consumerrights.wiki, FULU Foundation): [Sony BRAVIA pre-Android Linux TVs (2011–2012)](https://consumerrights.wiki/index.php?title=Sony_BRAVIA_pre-Android_Linux_TVs_%282011-2012%29)
- O caso do catálogo brasileiro: `docs/withheld-by-catalog.md`
- A saga das fontes GPL: `docs/oss-source-recovery.md`
- A reconstrução do schema: `docs/worldclock-schema-reconstruction.md`
- A doutrina do "não julgue pela capa": `docs/judging-by-the-cover.md`

### O que eu ainda não sei

- A remoção dos firmwares (janeiro de 2022) é **observação minha, sem fonte independente**. Procurei snapshot da página de suporte da época e não achei
- Não sei **quando** a geração saiu do serviço de fontes. Estava em 2014, não está hoje, e a cobertura do Archive entre 2016 e 2024 é rala
- Os pacotes com patch da Sony (`sony-target-dev-*`) parecem perdidos. Se alguém tiver um mirror, é o buraco que vale preencher

Se você tem uma KDL-EX7xx/HX8xx encostada: o painel e o 3D continuam ótimos, o conserto do 3D já está no HandBrake, e um único manual de serviço da Sony cobre cinco tamanhos de tela do mesmo chassis — o que vale para a minha TV vale para a geração inteira.

O hardware não envelheceu. O servidor é que parou de responder. E servidor, na sua própria casa, é coisa que dá para ligar de novo.

---

## Notas (não fazem parte do post)

**O que este v3 faz de diferente do v2 (`docs/tabnews-post.md`):**

1. **Abre pela jornada, não pelo caso.** A licença que o Vadim Asadov te deu em 2011 é o começo real da história, e transforma o post de "denúncia técnica" em "pessoa que passou quinze anos no mesmo assunto". Também explica, sem precisar dizer, por que você foi atrás disso.
2. **Fecha o círculo na seção 4**: driver que forçava 3D em jogos sem 3D (2011) → patch que grava o 3D em arquivos sem 3D (2026). Isso não é enfeite, é a tese da sua trajetória, e é o parágrafo que as pessoas vão citar.
3. **Assume a questão da IA como seção 6, não como rodapé.** É a decisão que o v2 deixou em aberto. Assumida assim, ela vira a *tese* do post — "não julgue um livro pela capa", com a mesa de slop do seu próprio documento por trás — em vez de uma vulnerabilidade esperando ser descoberta. E a frase "a lâmina corta para o meu lado também" é o que impede isso de soar como desculpa.
4. **Erro próprio em destaque (seção 3)**, o mês zero-based. Público dev premia erro admitido mais que acerto narrado.
5. **Fecho novo**: "o hardware não envelheceu, o servidor é que parou de responder — e servidor, na sua própria casa, dá para ligar de novo."

**Escolha entre v2 e v3:** o v2 é mais seguro e mais neutro; serve melhor se o objetivo for ser citado por veículo ou por advogado. O v3 é mais arriscado e mais seu; serve melhor para o TabNews, onde o que circula é gente, não relatório. Os fatos são idênticos nos dois.

**Ainda vale:** reescrever na sua voz antes de postar (esta versão *tenta* a sua perspectiva, mas a voz é sua), segunda ~8h, título sem "?", sem tabelas markdown, links de archive em `https://`.

**Checar antes de publicar:** os detalhes do e-mail de 2011 (data, o nome do produto "iZ3D All Outputs", o teor da resposta do Vadim) estão em `docs/3d-origin-story.md` — confira que estou representando fielmente antes de publicar algo pessoal assim.
