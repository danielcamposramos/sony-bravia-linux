# TabNews post — o critério aplicado, duas semanas depois — RASCUNHO 2026-09-20
# Sequência: este é o follow-up de docs/outreach/tabnews-post-slop.md (publicado 17/09/2026).
#
# DOUTRINA: matéria-prima. O dono reescreve na própria voz antes de publicar.
#
# Tese: no dia 17 eu defendi em público um critério — julgue o artefato, não a
# capa. Duas semanas depois eu tenho os números de sete projetos, e o critério
# pegou slop do MEU lado também. Essa é a parte que faltava.
#
# Formato TabNews: long-form, sem "?" no título, SEM TABELAS markdown, números
# cedo, primeira pessoa, fecho acionável. Segunda ~8h.

## Título — opções (sem "?")

1. 81 minutos, 41 minutos, e os cinco erros que o critério pegou do meu lado
2. Eu defendi um critério aqui há duas semanas, apliquei em sete projetos e ele me mordeu primeiro
3. O critério que eu defendi pegou o meu próprio slop antes de pegar o dos outros

## O post

---

#FATO: Há duas semanas eu vim aqui defender que slop se julga pelo conteúdo, não pela autoria.

Hoje eu tenho números de sete projetos upstream para mostrar, e o critério pegou coisa errada **minha**.

Começo pelo que é mais fácil de conferir, que é o relógio.

**HandBrake**, pull request #8100, aberto 16/09 às 05:45 UTC.

**Merge em 81 minutos.**

**Universal Media Server**, pull request #6330, aberto 19/09 às 02:35 UTC.

**Aprovado em 29 minutos, merge em 41**, com CI verde em Lint, Linux 22.04, Linux 24.04, Windows e os dois runners de macOS.

Os dois patches foram escritos com assistência de IA, e os dois foram declarados como tal.

Nenhum dos dois mantenedores perguntou uma única vez sobre isso.

Eles leram o diff.

### O que o relógio está medindo

Ler o artefato é **rápido**.

Um patch pequeno, derivado de uma especificação pública, com o teste junto, se resolve num café.

Julgar a capa é que é lento, porque não termina nunca: não existe evidência que encerre uma discussão sobre autoria, já que ela não é sobre o código.

Repara que eu não estou dizendo que os mantenedores foram levianos.

O galad87 do HandBrake tinha pedido um patch na issue original dele, a #5826.

O SubJunk do UMS leu as medições que eu tinha postado antes e perguntou, sem eu pedir, se eu tinha interesse em escrever o código.

Os dois sabiam exatamente o que estavam recebendo.

### O contra-exemplo, que é o caso interessante

No mpv o mesmo trabalho está parado.

E a política de lá é a mais estrita que eu encontrei: exige declaração, e desde 17/09 proíbe menção a IA em mensagem de commit e descrição de pull request.

Eu cumpri as duas.

O atrito não veio do código, veio da inferência de que quem usa assistência para escrever prosa não saberia responder à revisão. 

A própria thread desmentiu isso, porque eu respondi a oito comentários de revisão técnica, um por um.

Guarda essa, que ela vai importar daqui a pouco: **a fricção aconteceu justamente no projeto cuja regra eu já tinha cumprido**.

### Sete políticas, e o que realmente previu a recepção

Eu levantei a posição declarada de cada projeto sobre IA. 

O **mpv** tem a regra escrita mais dura: declaração obrigatória, e proibição de IA em commits e descrições.

O **Jellyfin** tem política pública detalhada, diz que "vibe coding puro será rejeitado" e exige que o autor explique a mudança com as próprias palavras.

O **mkvtoolnix** não tem política escrita por opção, e o mantenedor diz em issue aberta que é "muito cético", que não usa LLM, que não é "fundamentalmente contra o uso", e que exige que "você-humano entenda todas as mudanças, o efeito delas, e saiba explicar por que estão corretas".

O **HandBrake** não tem nada escrito.

O **Universal Media Server** também não.

A **Consumer Rights Wiki** tem a política mais pragmática que eu li: assistência permitida, toda citação tem que ser conferida contra a página que ela aponta, e slop óbvio é revertido na hora.

E o **Codeberg**, que é a forja e não um projeto, tem a linha institucional mais dura de todas: os membros votaram por proibir projetos compostos majoritariamente de código gerado.

Agora o resultado.

Merge: HandBrake e UMS, os dois sem política nenhuma.

Engajamento técnico mais profundo: mkvtoolnix, hospedado justamente no Codeberg, a forja da linha mais dura.

Parado: mpv, a política mais estrita, e a única que eu já tinha cumprido antes de mandar.

**A severidade da política não previu nada.**

O que variou foi o artefato.

Para o mkvtoolnix eu mandei quatro arquivos sintéticos e uma tabela de mapeamento que se confere com um comando de ffprobe.

Para o HandBrake e o UMS eu mandei código, onde o diff é o argumento.

Para o mpv eu mandei um patch embrulhado em explicação, e **a explicação virou o assunto**.

Arquivo de amostra não tem estilo de escrita para alguém implicar.

### A parte que me custou, e que é o ponto deste post

Eu mantenho uma lista pública de recursos de estereoscopia.

Parte dela foi escrita com um modelo diferente, num lote que eu não tinha conferido linha a linha.

Eu mandei conferir. 

Deu cinco erros de fato.

O **HDMI Forum** estava creditado pela especificação HDMI 1.4a, de 2010. O HDMI Forum só foi fundado em 2011. Quem publicou a 1.4a foi a HDMI Licensing.

O **VR180** estava descrito como par equirretangular. A especificação do próprio Google exige projeção em malha, justamente para carregar o quadro olho-de-peixe como a câmera gravou.

O **Vectograph** estava creditado ao Edwin Land. Quem desenvolveu foi o Joseph Mahler, na Polaroid do Land.

O **LG Optimus 3D** estava descrito como tendo saído de fábrica com o 3D Game Converter. O conversor chegou meses depois, numa atualização de manutenção.

E um link do manual da **JVC** respondia **HTTP 200** enquanto redirecionava calado para a home institucional. Link que parece vivo e não tem nada dentro.

Cinco erros, num texto que saiu com o meu nome.

Eu não descobri isso porque alguém me pegou.

Descobri porque **o critério que eu defendi aqui no dia 17 vale para mim primeiro**, e aplicar ele em cima do meu próprio texto era a única coisa honesta a fazer depois de escrever aquele post.

### E teve um caso pior, que é o mais instrutivo

Numa das minhas edições na wiki, um revisor marcou uma citação minha com "citação necessária".

Eu perguntei para um modelo se a frase estava no artigo citado. 

Ele respondeu que sim, e **citou de volta palavras diferentes, com o trecho principal entre colchetes**.

Isso é o formato de uma confirmação inventada.

Eu baixei a página crua e procurei o texto na mão.

A frase estava lá, literal, palavra por palavra. 

O modelo estava certo por acidente, e a confirmação dele não valia nada de qualquer jeito.

Essa é a linha mais útil de toda a política da Consumer Rights Wiki, e eu vou reescrever ela do jeito que eu aprendi na prática: **não deixe a ferramenta corrigir a própria prova**.

### Enquanto isso, o slop humano continua ali, sem ninguém para revertê-lo

Enquanto eu conferia o meu lado, apareceu o outro.

A **Wikipédia em russo** se contradiz sozinha sobre o sistema Стерео-70: um artigo diz 1963, o artigo dedicado ao sistema diz concluído em 1965 com filmes a partir de 1966. Dois textos humanos, na mesma wiki, discordando há anos.

O **dvdforum.org não resolve mais em DNS**. O **dvdcca.org está com certificado quebrado**. As duas entidades que criaram e administraram o código de região de DVD estão inalcançáveis. As fontes primárias de um esquema de DRM simplesmente evaporaram.

E as páginas de suporte da **Sony** trazem **1918** ocorrências de número de modelo por página, em três significados diferentes, sendo que um deles é uma caixa de busca de "digite o modelo da sua TV" que tem exatamente a cara de uma lista de modelos afetados. Eu quase publiquei 367 modelos como se fossem lista oficial.

Nada disso foi escrito por IA.

É apodrecimento de informação feito por gente, sustentado por gente, e não existe seção de política em lugar nenhum listando os "sinais comuns de escrita humana descuidada".

### O ponto, e é uma pergunta desconfortável

A política da wiki tem uma seção chamada "sinais comuns de escrita de IA": travessão demais, palavra-indicador demais, negrito demais, estilo fofo demais.

Não existe a seção equivalente para o descuido humano.

E o modo de falha é **o mesmo**, medido no mesmo eixo, pego pela **mesma** checklist.

Um lado ganhou heurística de aparência.

O outro ganhou "não sejam exagerados".

Eu não estou pedindo para tirarem a seção de IA, que ela descreve coisa real e eu uso ela como checklist contra os meus próprios rascunhos.

Estou dizendo que ela descreve **escrita descuidada**, não descreve **ferramenta**, e que ela deveria se chamar assim.

### O que eu faço agora, na prática

Declaro a assistência mesmo onde ninguém exige.

Confiro toda citação abrindo a página, e se a página bloqueia robô eu **paro** e peço para um humano abrir, sem forjar user-agent.

Não coloco entre aspas nenhuma frase que eu não li com os meus olhos na fonte. Quando a fonte estava bloqueada para mim, eu citei mesmo assim e **parafraseei em vez de citar**, porque aspas não verificadas é a única coisa que não pode chegar num artigo.

E quando eu erro, como eu errei nessas cinco entradas, eu corrijo com o commit explicando o que a fonte não sustentava.

O critério é esse, e ele não tem exceção para o autor.

A lâmina corta para o meu lado primeiro, e nas últimas duas semanas ela cortou.

*Talk is cheap. Show me the code.*

---

## Notas (não fazem parte do post)

**Tudo que está no post foi conferido em 20/09/2026, mas confira ao publicar:**

- HandBrake #8100: `created_at` 2026-09-16T05:45:34Z, `merged_at` 2026-09-16T07:06:47Z, pela API do GitHub. 81 minutos exatos.
- UMS #6330: os tempos de 29 e 41 minutos e o CI verde estão em `docs/judging-by-the-cover.md`, seção "The merge clock".
- As sete políticas estão tabeladas em `docs/judging-by-the-cover.md`, seção "Seven policies". **Converti para lista, sem tabela markdown, conforme a nota do post anterior.**
- Os cinco erros da lista e as correções estão nos commits `b8b7ff7` e `387ba36` do repositório awesome-stereoscopy.
- O episódio da confirmação inventada e a correção estão em `docs/wiki/POSTED.md`, segunda rodada.
- Стерео-70, dvdforum.org e dvdcca.org: apurados nesta sessão. O DNS e o certificado valem reconferir na hora de publicar, porque isso muda.
- A política da Consumer Rights Wiki é pública em `Consumer Rights Wiki:AI usage policy`, e a discussão que eu abri está na página de discussão dela.

**Relação com o post anterior:** aquele estabeleceu o critério, este presta contas dele. A ordem importa, e ela já está certa: o critério foi defendido **antes** de eu ter os números, então o post de hoje não é defesa, é resultado.

**O risco conhecido mudou.** No post anterior o risco era parecer que você defende o uso de IA. Neste, o risco é o oposto: parecer humildade performática, aquele "olha como eu sou honesto". A defesa contra isso é que os cinco erros são **específicos, nomeados e já corrigidos em commit público**, com link. Erro com hash não é performance.

**Sugestão de corte, se ficar longo:** a seção das sete políticas é a mais fácil de encurtar para três exemplos (mpv, mkvtoolnix, HandBrake), porque o argumento sobrevive com eles.
