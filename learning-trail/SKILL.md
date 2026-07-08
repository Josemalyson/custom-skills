---
name: learning-trail
description: Use esta skill SEMPRE que o usuário mencionar que deseja estudar, aprender, explorar, entender ou pedir uma trilha, aula ou roadmap sobre qualquer assunto, mesmo que não cite explicitamente "trilha de aprendizado". A skill cria um guia linear e multimodal com leitura, vídeos, podcasts/áudio, tutoriais práticos, livros e sinais recentes de comunidade, todos avaliados rigorosamente por inspeção. Gera um JSON canônico (`trail.json`) e um HTML autocontido (`index.html`) com CSS/JS embutidos, progresso local via localStorage e tema claro/escuro. Evite usá-la apenas para tarefas de código ou dúvidas pontuais, mas para qualquer jornada de aprendizado, acione-a imediatamente!
---

# Learning Trail Generator

Bem-vindo à skill Learning Trail Generator. O seu objetivo aqui é ajudar o usuário a aprender um tema aprofundadamente. Para isso, você gerará um JSON canônico (`trail.json`) e um HTML autocontido (`index.html`) no padrão **spine + nerves** (espinha e nervos), no qual a maior força está em você validar e inspecionar cada recurso sugerido.

A trilha deve ser completa para aprendizado visual, prático, auditivo e textual. Dois links soltos não são uma trilha: use um mix multimodal de vídeos, podcasts/áudio, tutoriais práticos, artigos recentes, discussões qualificadas de X/Reddit e livros opcionais.

## Arquitetura de Confiança (Trust by Inspection)

A essência desta skill é construir confiança através da inspeção do conteúdo real, e não apenas por reputação ou intuição. Por isso:
- Nós não filtramos fontes usando whitelists estáticas. Qualquer fonte pode ser ótima se o conteúdo for bom.
- Inspecionamos ativamente cada candidato a recurso (lendo o texto, transcrições ou PDFs) antes de incluí-lo na trilha.
- Cada recomendação é incluída apenas se puder ser validada como cobrindo o tema específico exigido, com o nível de profundidade correto.
- Isso evita que o usuário receba links quebrados ou desatualizados, garantindo uma trilha sólida.

A reputação da fonte serve apenas como desempate, mas o conteúdo vem em primeiro lugar.

## O Modelo Mental

Pense na trilha como um jogo de tabuleiro:
- **Tabuleiro:** O mapa da trilha, apresentado antes de começar.
- **Casas (Estações):** A espinha dorsal do conhecimento (idealmente de 4 a 10 estações breves, ~5-10 min de leitura cada).
- **Caminhos Laterais (Nervos):** Recursos validados para aprofundamento, alternando leitura, vídeo, áudio, comunidade e prática.
- **Labs/Tutoriais:** Pequenas entregas práticas para fixar o conteúdo, mesmo em temas conceituais.
- **Desafio Final:** Perguntas socráticas para auto-avaliação (sem gabaritos!).

## Como conduzir a sessão (Workflow)

Siga estas fases passo a passo.

### Fase 1 — Captura e Clarificação (Perguntas Iterativas)

Ao receber a solicitação de aprendizado, identifique o idioma do usuário.
Antes de começar a pesquisa, **faça perguntas iterativas até entender totalmente o que o usuário deseja**. As perguntas devem cobrir:

1. **Plano:** Ele prefere que você monte o plano automaticamente ou quer customizar (tamanho, foco teórico vs prático)?
2. **Materiais:** Ele possui algum link, PDF ou material específico que gostaria de incluir na trilha?
3. **Nível:** Qual o nível de profundidade desejado? (iniciante, intermediário, avançado)
4. **Foco:** Prefere uma trilha mais teórica (conceitos, papers), prática (ferramentas, código) ou balanceada?
5. **Extensão:** Quantas estações (tópicos) ele idealiza? (curta: 3-4, média: 5-7, longa: 8-10)
6. **Modo de aprendizado:** Ele prefere mais vídeo, leitura, prática, áudio/podcast ou um mix balanceado?

**Importante:** Não pergunte tudo de uma vez. Vá em sequência, adaptando as perguntas com base nas respostas anteriores. Se o usuário pedir para montar automaticamente, use o padrão balanceado: visual + prático + textual + áudio + comunidade recente.

### Fase 2 — Busca Exploratória

Realize uma busca ampla pelo assunto para entender o contexto geral e encontrar os melhores candidatos a materiais.
- Procure os conceitos fundamentais, pré-requisitos e tópicos mais avançados para montar a ordem da trilha (a espinha).
- Colete candidatos em quantidade suficiente para reprovar sem empobrecer a trilha. Para trilhas médias/longas, busque pelo menos 25-40 candidatos antes da validação.

**Cobertura multimodal obrigatória:**

Direcione a busca exploratória para estes tipos de fonte. Não trate a lista como whitelist; mantenha o princípio de que o conteúdo vem em primeiro lugar.

1. **Leitura profunda** — documentação oficial, papers, RFCs, whitepapers, posts técnicos extensos e livros.
2. **Vídeo** — aulas, talks, conference talks, demos e walkthroughs. Priorize transcrição, capítulos ou descrição verificável.
3. **Áudio/podcast** — episódios, entrevistas e painéis com especialistas. Priorize transcrição, show notes ou timestamps.
4. **Tutoriais práticos/labs** — codelabs, quickstarts, notebooks, repositórios didáticos, hands-on guides, exercises e projetos pequenos.
5. **Comunidade recente** — X/Twitter, Reddit, Hacker News, GitHub Discussions/Issues e newsletters recentes. Use para capturar debate atual, armadilhas, mudanças recentes e prática de campo; não use como única fonte de verdade.
6. **Livros** — livros seminais, livros modernos e capítulos específicos. Valide por sumário, sample, reviews qualificadas ou citações confiáveis.

**Metas mínimas de candidatos antes da validação:**

- 6-10 leituras profundas.
- 6-10 vídeos.
- 3-6 podcasts/áudios quando o tema permitir.
- 5-8 tutoriais práticos/labs.
- 5-10 sinais recentes de comunidade, preferencialmente dos últimos 30-180 dias para tecnologia ativa.
- 3-5 livros ou capítulos relevantes.

### Fase 3 — Desenho da Espinha (Estações)

Determine a sequência lógica do aprendizado.
Se for uma ferramenta prática, talvez 4-5 estações sejam suficientes. Se for um conceito complexo, 7-10. Mais que 10 pode ser exaustivo; sugira quebrar em sub-trilhas.
Cada estação precisa de uma narrativa: introduza o problema, desenvolva a ideia, mostre limitações e conclua.

Inclua uma **entrega prática** por estação sempre que for possível: experimento, mini-lab, checklist aplicado, prompt de investigação, exercício de código, diagrama, leitura de código, configuração local ou comparação crítica. Se uma estação for puramente conceitual, a entrega prática pode ser uma pergunta de modelagem ou exercício de explicação.

### Fase 4 — Validação Atômica de Recursos (O Coração da Skill)

Esta é a etapa mais crítica. Para que a trilha seja incrivelmente útil, precisamos ter certeza de que o que recomendamos é excelente.

Para cada tópico a ser aprofundado (slot de nervo):
1. **Busque o conteúdo:** Use ferramentas de fetch para ler a URL do artigo/paper ou obter a transcrição de um vídeo.
2. **Avalie o conteúdo:** Ele cobre especificamente o subtópico da estação? A profundidade está adequada para o nível da trilha? É atual (especialmente em tecnologia)?
3. **Avalie a autoridade do autor (para blogs, X, Reddit e comunidade):** Quando o recurso for um blog post, thread/post do X, Reddit, HN ou GitHub, confirme quem fala, qual contexto sustenta a afirmação e se há evidência técnica. Se não for possível validar autoridade, evidência ou consenso mínimo, descarte ou registre apenas como "sinal fraco" fora dos nervos principais.
4. Se a resposta for "sim" para todos, o recurso é aprovado.
5. **Extraia a prova:** Separe 1 ou 2 frases do próprio conteúdo que evidenciam a relevância dele para o subtópico. Isso será exibido na trilha para dar contexto ao usuário.
6. **Classifique a modalidade:** leitura, vídeo, áudio, tutorial/lab, comunidade recente ou livro.
7. **Registre no inventário:** Todo candidato pesquisado deve ser registrado no array `resources[]` do JSON com status `approved`, `rejected`, `backup` ou `weak_signal` e um motivo curto da decisão.
8. Seja resiliente. Tente validar vários materiais até ter boas opções por estação.

**Gates de qualidade e variedade:**

- Cada estação deve ter **no mínimo 4 nervos validados** quando o tema permitir材料 disponível real de materiais.
- Quando existir vídeo bom e validável para uma estação, incluir **ao menos 1 vídeo** naquela estação.
- Se não existir vídeo validável, registrar a lacuna na auditoria da estação e compensar com outra modalidade.
- Uma estação só pode ter menos de 4 nervos quando a auditoria explicar a lacuna e documentar tentativa de busca complementar.
- Evite repetir sempre o mesmo tipo de recurso. Uma estação ideal combina: 1 leitura forte, 1 vídeo ou áudio, 1 recurso prático e 1 de comunidade ou livro.
- A trilha completa deve conter, quando o tema permitir: pelo menos 4 vídeos, 2 podcasts/áudios, 3 tutoriais/labs, 3 sinais recentes de comunidade, 2 livros opcionais e leitura profunda suficiente para fundamentar a espinha.
- Não finalize uma trilha média/longa com apenas dois links ou apenas documentação. Isso é insuficiente para aprendizado real.
- Se uma modalidade não existir, estiver atrás de paywall, não tiver transcrição ou não puder ser validada, declare a lacuna na auditoria e compense com outra modalidade validada.
- Para fontes recentes, registre a data do post/artigo/discussão. Para X/Reddit, trate como termômetro de prática e debate, não como autoridade isolada.

#### Validação obrigatória de vídeos e YouTube

Vídeos do YouTube não podem ser recomendados apenas pelo título, canal ou reputação. Toda recomendação de vídeo do YouTube exige validação explícita:

1. **Buscar evidência de conteúdo:** transcript oficial, auto-transcript, capítulos, descrição substancial, slides, repo associado, timestamps ou show notes.
2. **Conferir cobertura específica:** O vídeo cobre o subtópico da estação, não apenas o tema geral? A profundidade é adequada?
3. **Registrar metadata:** canal, autor/apresentador, data de publicação quando disponível, duração e evidência extraída.
4. **Verificar afirmações técnicas:** Quando o vídeo for opinativo, antigo ou de comunidade, verifique afirmações importantes contra fonte primária.
5. **Métodos de validação aceitos:** `youtube_transcript`, `youtube_chapters`, `description`, `slides_repo`, `cross_check`, `show_notes`.
6. **Reprovar videos sem evidência:** Videos sem transcript, descrição substancial ou evidência suficiente devem ser reprovados, exceto se houver material complementar verificável que compense a lacuna.

#### Inventário completo de recursos pesquisados

Todo recurso pesquisado durante a Fase 2 e Fase 4 deve ser registrado, mesmo que não vire nervo principal:

- Manter um inventário de candidatos desde a busca exploratória no array `resources[]` do JSON.
- Classificar cada candidato como `approved`, `rejected`, `backup` ou `weak_signal`.
- Registrar motivo curto da decisão em `decision_reason`.
- Preservar recursos reprovados no inventário final, sem promovê-los como recomendação principal.
- Tratar o inventário como "fontes para mais estudos", deixando claro que nem tudo ali foi aprovado como nervo.
- Recursos `rejected` e `weak_signal` podem aparecer no inventário auditável, mas não podem aparecer como recomendação principal nem como "recurso para seguir" sem rótulo claro.

**Dica para uso de Sub-agentes:**
Se o seu ambiente suportar agentes paralelos (como Claude Code usando a tool de Task), você pode gerar sub-agentes para lerem e avaliarem os recursos paralelamente, o que acelera bastante o processo. Peça a eles para retornarem o veredicto (aprovado/reprovado) e o trecho de evidência (excerpt).

### Fase 5 — Escolha do Formato de Saída

Com a espinha montada e os nervos validados, **apresente ao usuário as opções de formato de saída** e peça que ele escolha:

**Opção A — Markdown (`.md`)**
- Arquivo leve, portátil, editável em qualquer editor.
- Inclui checkboxes estáticos `- [ ]` para progresso (não interativos).
- Template: `assets/trail_template.md`

**Opção B — HTML Autocontido (`index.html`)**
- Template único canônico: `assets/TEMPLATE.html`
- Layout responsivo autocontido, tema claro/escuro com alternância manual e detecção automática.
- Navegação lateral responsiva para desktop e mobile.
- Progresso local por estação via `localStorage`.
- JSON completo embutido em `<script type="application/json">` para auditoria e reuso.
- JavaScript vanilla (sem Alpine.js) para todas as interações.
- Funciona em `file://`, mobile e desktop.

**IMPORTANTE:** Apresente as 2 opções com uma breve descrição de cada (como acima) e aguarde a escolha.

### Fase 6 — Geração do Arquivo

Com o formato escolhido pelo usuário:

#### Diretório de saída

Criar um diretório por assunto antes de escrever os arquivos:
- Padrão: `./trilhas/{slug}/`, onde `{slug}` é derivado do título da trilha.

#### Passo 1 — Gerar o JSON canônico

Construa primeiro a estrutura JSON completa seguindo o schema em `assets/trail_schema.example.json`. O JSON deve conter:
- `schema` e `schema_version` para versionamento.
- `meta` com id, slug, título, idioma, nível, datas e versão do template.
- `summary` com contagens deriváveis de `stations[]` e `resources[]`.
- `progress` com configuração de localStorage.
- `stations[]` com nervos referenciando `resource_id` de `resources[]`.
- `resources[]` com todos os candidatos pesquisados (aprovados, reprovados, backup, weak_signal).
- `boss_final`, `additional_resources`, `next_steps`, `audit`.

Regras do contrato JSON:
- Todo `stations[].nerves[].resource_id` e todo `additional_resources[].resource_id` deve existir em `resources[]`.
- Apenas recursos `approved` podem aparecer em `stations[].nerves[]`.
- Recursos `backup` podem aparecer em `additional_resources[]`.
- Todo recurso `video` aprovado de YouTube deve ter pelo menos um método de validação.
- Contagens em `summary` e `audit` devem ser deriváveis de `stations[]` e `resources[]`.
- `meta.id` é a chave estável do progresso. Alterar `meta.id` reseta o progresso do usuário.

Salvar como `./trilhas/{slug}/trail.json`.

#### Passo 2 — Gerar o HTML autocontido

Usar o template `assets/TEMPLATE.html` como base e preencher com o conteúdo da trilha:
- O HTML final deve ser autocontido: CSS embutido, JS inline (vanilla), JSON embutido em `<script type="application/json" id="trail-data">`.
- Não deixar dependências obrigatórias de rede no `index.html` final. Evitar CDN, `fetch()`, renderer externo, iframe ou arquivo local obrigatório.
- O HTML não deve usar Alpine.js — toda interação é feita com JavaScript vanilla.
- O conteúdo principal deve estar semanticamente presente no HTML. JavaScript é melhoria progressiva.
- Gerar todo o conteúdo semanticamente: hero, navegação, estações, nervos, boss final, auditoria e inventário.
- Evitar repetir grandes blocos HTML por estação ou nervo durante a geração.
- Garantir escaping de texto ao gerar HTML para evitar markup quebrado quando dados tiverem caracteres especiais.
- Garantir que a trilha continue legível quando o JavaScript estiver indisponível.

Salvar como `./trilhas/{slug}/index.html`.

#### Passo 3 — Gerar Markdown (se solicitado)

Se o usuário escolheu Markdown, gerar `./trilhas/{slug}/trail.md` usando `assets/trail_template.md` como referência estrutural, refletindo:
- Mínimo de 4 nervos por estação quando possível.
- Vídeo obrigatório quando existir.
- Seção "Todos os recursos pesquisados" com status de cada um.
- Lacunas por estação.
- Checkboxes estáticos `- [ ]` para progresso (não interativos).

### Fase 7 — Fechamento

Avise ao usuário que a trilha foi gerada e forneça estatísticas curtas: número de estações, nervos validados, vídeos, podcasts/áudios, tutoriais/labs, leituras profundas, fontes recentes, livros, estimativa de leitura/assistir/ouvir/praticar e o formato escolhido.
Mencione que o progresso local está disponível no HTML via `localStorage`.
Pergunte se ele deseja gerar em outro formato também, ou se está satisfeito.
Deixe o usuário guiar os próximos passos, sugerindo se ele gostaria de conversar mais, criar um projeto prático para fixar ou avançar para um próximo tema, mas não imponha as etapas automaticamente.

## Pontos Importantes para a Interação

- Procure não gerar conceitos inteiros "de cabeça"; busque validação, para garantir que as informações são frescas e exatas.
- Se o usuário não gostar de alguma seção, adapte-a iterativamente.
- Faça o processo ser transparente: mostre brevemente ao usuário quando você estiver descartando um link por ele ser inadequado, pois isso demonstra o valor da curadoria que você está fazendo.
