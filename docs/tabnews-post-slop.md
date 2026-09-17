# TabNews post — ensaio sobre slop (matéria-prima, PT-BR, 2026-09-17)

# DOUTRINA: matéria-prima. O dono reescreve na própria voz antes de
# publicar.
#
# Tese: slop sempre existiu. A IA não mudou a natureza dele, mudou a
# taxa. E a comunidade dev já resolveu exatamente esse problema uma vez
# — com a palavra "hacker" — e resolveu julgando CONDUTA, não
# ferramenta. Espinha dorsal: docs/judging-by-the-cover.md.
#
# Formato TabNews: long-form, sem "?" no título, SEM TABELAS markdown,
# números cedo, primeira pessoa, fecho com algo acionável. Segunda ~8h.
#
# Relação com os outros dois posts: este é o ensaio conceitual e pode
# ir PRIMEIRO ou DEPOIS do post do caso Sony. Se for depois, vira a
# defesa teórica do que já foi mostrado na prática. Se for antes, o
# post da Sony vira a prova do que este aqui argumenta. Minha sugestão
# está nas notas do fim.

## Título — opções (sem "?")

1. **Slop não nasceu com a IA. Em 2020, 172 mil pull requests de lixo foram feitos por humanos — por uma camiseta.**
2. **O que é slop, de onde veio e para onde vai: a comunidade já resolveu esse problema uma vez, e chamou de white hat**
3. **A gente não baniu o nmap porque criminoso usa nmap**

## O post

---

Em outubro de 2020, o Hacktoberfest quase quebrou o open source.

A regra era: quatro pull requests em projetos open source e você ganha uma camiseta. O resultado, pelos números do recap oficial da própria DigitalOcean:

- **34.595** pull requests não aceitos por nenhum mantenedor
- **9.598** marcados explicitamente como spam ou inválidos
- **172.599** enviados para repositórios que decidiram **não participar** do evento
- **17.260** para repositórios que a própria DigitalOcean excluiu

Mantenedores relataram "PRs completamente inúteis, tipo adicionar um ponto e vírgula no README só para completar o #Hacktoberfest". Um deles descreveu o evento como "um ataque de negação de serviço distribuído, patrocinado por uma empresa, contra a comunidade open source". No meio do evento a DigitalOcean mudou a regra para opt-in: repositório só contava se o mantenedor pedisse.

Guarde a data: **2020**. Nenhum modelo de linguagem envolvido. Nenhuma IA. Duzentos mil pull requests de lixo, gerados por seres humanos, motivados por uma camiseta.

Esse é o maior evento de slop da história do open source, e ele é 100% humano.

### O que slop é, de verdade

Slop não é "texto de IA". Slop é uma propriedade do **trabalho**:

- afirmação que não dá para verificar
- enchimento — volume sem conteúdo checável
- baixa densidade de informação por parágrafo
- confiança performada no lugar de evidência
- e, o pior de todos, **custo transferido**: quem escreve gasta pouco, quem lê gasta muito

Repare que nada nessa lista diz quem escreveu. Slop é sobre o que está no texto, não sobre o que estava na cadeira.

Por isso todas as línguas já tinham um ditado para isso muito antes de existir computador. Em português a gente tem dois, e são bons: **"não julgue um livro pela capa"** e **"o hábito não faz o monge"**. O segundo é medieval — vinha em latim, *habitus non facit monachum* —, e é literalmente sobre isso: a roupa não prova o conteúdo. Shakespeare escreveu a mesma ideia como "nem tudo que reluz é ouro". O Evangelho de Mateus resolveu no critério: *pelos seus frutos os conhecereis*.

Séculos de gente avisando que cobertura não é conteúdo. E a nossa geração conseguiu inventar a única heurística que julga exatamente a capa.

### Uma história curta do slop, sem IA nenhuma

Antes de 2022 o slop já tinha genealogia longa:

- **Content farms e SEO spam**: artigos escritos para ranquear, não para informar. A Demand Media chegou a produzir milhares de artigos por dia; o Google gastou uma década criando o Panda e sucessores para conter
- **Paper mills acadêmicos**: artigos gerados ou comprados para inflar currículo. O SCIgen — um gerador de papers *aleatórios* do MIT — teve trabalhos aceitos em conferências. Em 2005
- **"Me too" em issue tracker**: o comentário que só custa a quem lê
- **Copy-paste de Stack Overflow** em produção, sem entender a resposta
- **Documentação corporativa** de quarenta páginas que não responde uma pergunta
- **Cargo cult**: código copiado de tutorial que funciona por acidente
- **E o Hacktoberfest 2020**, que é o caso limite porque teve métrica, incentivo e escala

Nenhum desses precisou de IA. Todos têm a mesma assinatura: **o custo foi jogado para o lado do leitor**.

### Então o que a IA mudou de fato

Uma coisa só, e ela é séria: **a taxa**.

Slop humano tem um freio natural — dá trabalho. Escrever quarenta páginas ruins ainda custa dias. O modelo de linguagem tirou esse freio. Agora dá para produzir volume plausível em segundos, e plausível é pior que ruim: ruim você descarta em dez segundos, plausível você precisa **ler para descobrir**.

E é aí que a heurística da capa aparece, e eu preciso ser justo com ela: **julgar pela capa é triagem racional quando a fila é infinita**. A atenção de mantenedor é o recurso mais escasso do open source. Se chegam dez contribuições e três têm cheiro de máquina, descartar as três pelo cheiro é barato e acerta na maioria. Não é preconceito, é orçamento.

O problema é que heurística de triagem erra em silêncio, e erra justamente no caso que mais importa: a contribuição que **veio pronta**, medida, reproduzível — e com o cheiro errado.

### A comunidade já resolveu esse problema uma vez

E resolveu bem. Aconteceu com a palavra **hacker**.

"Hacker" nasceu no MIT significando quem entende um sistema fundo o suficiente para fazê-lo fazer coisas que ninguém previu. Nos anos 80 a imprensa sequestrou o termo e transformou em "criminoso digital". Por uns bons anos, dizer "eu sou hacker" numa entrevista de emprego era confissão.

Repare no que a comunidade **não** fez:

- não baniu a palavra
- não baniu a habilidade
- não baniu as ferramentas
- ninguém proibiu o `nmap` porque criminoso usa `nmap`
- ninguém proibiu engenharia reversa porque pirata usa engenharia reversa

O que a comunidade fez foi criar um eixo **de conduta** e parar de julgar pelo eixo da ferramenta: black hat, white hat, grey hat. E a definição de white hat nunca teve nada a ver com qual ferramenta você usa. Tem a ver com:

- **autorização** — você tinha permissão de mexer nisso
- **divulgação** — você conta o que fez e como
- **reprodutibilidade** — o outro lado consegue confirmar
- **responsabilidade** — o relatório vai para quem pode consertar, antes de ir para a plateia

Duas pessoas rodam exatamente o mesmo scanner na mesma rede. Uma é crime, a outra é profissão. **A ferramenta é idêntica; o que separa é a conduta.**

Agora troque "scanner" por "modelo de linguagem" e leia de novo.

### O white hat da era da IA

Se o paralelo vale — e eu acho que vale —, então a pergunta útil não é "isso foi escrito com IA". É a mesma lista de sempre:

- **Dá para verificar?** Tem link para documento primário, comando que eu possa rodar, número que eu possa conferir
- **Foi medido onde importa?** Rodou em máquina real, com resultado anotado, ou é plausibilidade de texto
- **A afirmação é específica o suficiente para estar errada?** Slop é vago de propósito, porque vago não pode ser refutado
- **Quem assina responde?** Numa review, a pessoa aparece, entende o próprio patch, defende ou corrige
- **O método está aberto?** Não como penitência — como cortesia com quem vai revisar

Isso é exatamente o que a gente já cobra de pentester. Não inventei nada.

E tem o outro lado da lâmina, que é a parte que me obriga: **IA não lava nada**. Se eu assino, aguenta o mesmo teste. Contribuição assistida que não é verificável não vira boa porque eu declarei a assistência — vira slop com nota de rodapé. A declaração não é um passe; é o contrário, é assumir o ônus.

### O caso Zig: uma porta fechada, e o bug que ninguém tinha nomeado

A política de contribuição do Zig (2026) não aceita **nenhum** conteúdo gerado, editado, ou sequer **depurado** com assistência de IA. A avaliação pública da liderança é que contribuição assistida por IA é *"invariably garbage"* — invariavelmente lixo.

Eu compilo um projeto hiper-modular grande: ~1.800 módulos nomeados, ~2.300 arquivos analisados como uma unidade de compilação só. O Zig 0.16.0 oficial **nunca compilou** isso. Depois de 2+ horas, todas as vezes, morria com um **SIGSEGV silencioso** — binário de release stripped, então a falha não dizia nem onde tinha sido.

Diagnosticado em parceria com IA, com reprodução controlada **sete vezes** em dois builds independentes com o mesmo final de backtrace: o `InternPool` do frontend usa um sentinela `u32` `0xFFFFFFFF` ("none") que, num caminho de exaustão, é **dereferenciado como índice vivo** numa tabela de elementos de 8 bytes. O endereço da falha decompõe exatamente como `base + 0xFFFFFFFF * 8`. Duas issues upstream parecidas foram reproduzidas localmente e **descartadas por um discriminador** — não era nenhuma delas.

Não era "seu projeto é grande demais". Era um estouro de espaço de índices que o compilador **não nomeava**.

O resultado, medido: antes, nunca terminava. Depois, o mesmo workload compila em **46 minutos**, seis builds completos consecutivos, zero OOM. A falha silenciosa virou panic nomeado com o remédio impresso. E o harness do próprio fork registra **22 linhas verdes e 2 vermelhas** — as duas vermelhas são flags que já vêm desligadas por padrão porque regrediram ~6,5%, e o README diz isso em voz alta, junto com o que ainda não foi medido.

Agora a parte que interessa para este ensaio: **eu não ofereci nada disso ao upstream.**

A porta está fechada por política declarada, e política de projeto é do projeto. Respeitei. Virou um fork MIT, com LICENSE e README originais preservados, cadeia de crédito humano+IA num `PROVENANCE.md`, e um `CONTRIBUTING-AI.md` explicando o rito de quem quiser contribuir assim ali. ([O post completo](https://www.tabnews.com.br/danielramos/cgm-zig-o-fork-do-zig-que-nasceu-no-lixao-e-compila-o-que-o-original-nao-compilava), se quiser os detalhes técnicos.)

Não conto isso como "eles estavam errados e eu certo". Conto porque é a diferença exata entre os dois eixos. A política deles julgou a **ferramenta**, e o efeito colateral foi que um bug real do compilador deles continuou sem nome. Eu julguei a **conduta** — porta fechada se respeita — e o trabalho existe do lado de fora, verificável por quem quiser.

### O outro lado da mesma semana

#### O experimento controlado que eu não pedi para ter

Este mês eu vivi os dois lados na mesma semana, com o mesmo trabalho.

Passei semanas fazendo engenharia reversa de por que TVs 3D da era 2011 não engatam 3D com arquivos que têm a marcação 3D. A resposta é que o hardware lê só um sinal dentro do stream H.264 e ignora a tag do container — a única que os rips carregam. Fiz o diagnóstico, medi em máquina real, escrevi o patch. Com parceiros de IA, dirigindo e verificando no hardware.

Num projeto, olharam **o código**. Revisaram o patch, aceitaram o diagnóstico, mergearam em **81 minutos** — o tempo do CI rodar.

Em outro, a discussão saiu do código antes de chegar nele e foi para a autoria do texto. A contribuição mais checável do thread era a assistida por IA — comandos de reprodução, tabela de nove arquivos antes/depois, contagem medida em arquivo real. E a entrada menos checável do thread inteiro foi um meme de 529×95 pixels dizendo "texto demais, desculpa, mas não me importo". Zero conteúdo técnico. Nada para conferir.

Mesma pessoa, mesma semana, mesma assistência, mesmo patch. Um projeto julgou o artefato. O outro julgou a capa.

Não estou contando isso como mágoa — o segundo projeto voltou ao código depois, fez perguntas técnicas boas, e eu respondi uma por uma. Conto porque é o experimento mais limpo que eu poderia ter: **a variável que mudou não foi a qualidade do trabalho.**

### De onde vem o slop de IA, na real

Aqui está a parte que eu acho que a gente não fala o suficiente.

Os modelos foram treinados em texto humano. O enchimento que eles produzem, eles aprenderam. A confiança falsa, o parágrafo que não diz nada, o relatório de bug de quarenta linhas sem um passo de reprodução — **isso tudo é nosso**. A máquina não inventou o estilo; ela é um espelho muito rápido.

**Slop de IA é slop humano repetido.** Mais rápido, mais barato, em mais lugares — mas não é uma espécie nova. É a nossa, escalada.

O que me deixa moderadamente otimista é a consequência disso: se slop sempre foi o mesmo problema, então as defesas que já funcionavam continuam funcionando. Passo de reprodução. Número medido. Afirmação específica. Fonte primária. Nada disso é novo, e nada disso pergunta quem escreveu.

### Para onde isso vai

Meu palpite, e é palpite:

O equilíbrio não vai ser "IA banida". Vai ser **a régua de evidência subindo por contribuição**. Repositórios vão pedir, cada vez mais explicitamente, o que os bons já pediam: como reproduzir, o que foi medido, em qual máquina, qual afirmação exatamente você está fazendo.

E isso é bom até para o problema velho. A régua que filtra slop de IA filtra o "me too", o PR de ponto e vírgula, o relatório sem passo de reprodução. **Não existe régua que filtre slop de IA e deixe passar slop humano** — porque é a mesma coisa medida no mesmo eixo.

A cura para revisão cara não é julgar mais cego. É **livro mais barato de abrir**: post mais curto, comando que roda, resultado medido, afirmação que dá para refutar.

E se você está do lado de quem contribui com assistência de IA: a régua vale para você primeiro. Entregue um livro que valha a pena abrir, e a capa para de importar.

### Uma palavra sobre chamar coisa de lixo

Eu moro na **Cidade Estrutural**, no DF — a comunidade que cresceu ao lado do que foi, até fechar em 2018, um dos maiores lixões a céu aberto do planeta.

Quem trabalhou ali, os catadores, sustentou família **achando valor no que todo mundo jogou fora**. E é bom lembrar por que essa função existe: cidade sem quem recolhe e separa adoece. Fede rápido, e fede muito.

Quando um projeto declara uma categoria inteira de contribuição como "invariavelmente lixo" e tranca a porta, ele está fazendo uma coisa que toda cidade aprende do jeito difícil que não funciona: confundir **o monte** com **o que tem dentro do monte**. Tem lixo no monte, claro — a maior parte é. Mas quem pega, separa e acha o que presta não está abaixo da cidade. É o que mantém a cidade de pé.

Eu não digo isso como metáfora de LinkedIn. Digo do lugar onde eu moro, olhando para onde o lixão era.

E é exatamente a mesma operação que a gente está discutindo neste post inteiro: **separar**. Slop de substância, capa de conteúdo, ferramenta de conduta. Quem se recusa a separar não está sendo rigoroso — está terceirizando o trabalho de triagem para "não olhar".

> *"Tenha fé, porque até no lixão nasce flor."* — Mano Brown, Racionais MC's

E repara no verbo, que é o ponto: ele não diz que a flor **cresce** lá. Diz que **nasce** — no único lugar onde nada deveria nascer.

*Talk is cheap. Show me the code.* — essa é de 2000, e não era sobre IA.

---

## Notas (não fazem parte do post)

**Dado honesto sobre alcance:** o post do cgm-zig, tecnicamente o melhor
argumento que você já publicou lá, ficou em **1 TabCoin e 0 comentários**
(publicado 31/08/2026). Isso não é julgamento da qualidade — é sinal de
que o problema não é o conteúdo, é o gancho e a descoberta. O título
exige que o leitor já se importe com Zig antes de clicar. Este ensaio
tenta o contrário: abre com um número que qualquer dev entende
(172 mil PRs de lixo por uma camiseta) e só depois pede atenção para os
casos. Vale também revisar o horário — a análise do andradeandrey aponta
segunda ~8h, e 31/08 caiu num domingo.

**Fontes a conferir antes de postar** (todas verificadas em 17/09/2026, mas confira os links ao publicar):

- Números do Hacktoberfest 2020: recap oficial da DigitalOcean (34.595 / 9.598 / 172.599 / 17.260). Cobertura de imprensa: The Register, 01/10/2020. A crítica "corporate-sponsored DDoS against open source" é do Domenic Denicola (domenic.me/hacktoberfest)
- SCIgen (MIT, 2005) — gerador de papers aleatórios com trabalhos aceitos em conferência. Vale conferir o caso específico antes de citar
- "Talk is cheap. Show me the code." — Linus Torvalds, lista do kernel, 25/08/2000
- *Habitus non facit monachum* — provérbio medieval pan-europeu
- Os dois casos upstream (merge em 81 minutos vs. discussão de autoria) estão documentados em `docs/judging-by-the-cover.md` e `docs/worldclock-schema-reconstruction.md` no repositório
- Caso Zig: a política de contribuição e a frase "invariably garbage" precisam ser citadas com link para a fonte pública original ao publicar — o seu próprio post do cgm-zig já as referencia, mas um link direto para a política/declaração é mais forte num ensaio que argumenta sobre julgar pela evidência
- Os números do cgm-zig (1.800 módulos, 7 reproduções, `base + 0xFFFFFFFF * 8`, 46 minutos, 22 verdes / 2 vermelhas) saem do seu post e do README do fork

**Ordem de publicação — minha sugestão:** publicar **este ensaio primeiro**, e o post do caso Sony depois, alguns dias à frente.

Razão: se o caso Sony vier primeiro, a seção sobre IA dentro dele parece defesa antecipada de quem sabe que vai ser questionado. Se o ensaio vier primeiro, ele estabelece o critério **antes** de você ter pele em jogo — e aí o post da Sony vira simplesmente a aplicação do critério que você já defendeu em público. O ensaio também é mais fácil de circular sozinho: não depende de ninguém se importar com TV de 2011.

**Risco conhecido:** este post pode atrair a discussão "então você está defendendo o uso de IA". A defesa está no próprio texto e precisa sobreviver à reescrita na sua voz — é a parte do "a lâmina corta para o meu lado": você está *subindo* a régua para si mesmo, não pedindo isenção. Se essa parte enfraquecer no reword, o post perde a espinha.

**Não use tabelas markdown.** A tabela 2×2 de slop (autoria × informação) do documento original foi convertida em listas de propósito.
