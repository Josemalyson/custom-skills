---
name: learning-trail
description: Use esta skill SEMPRE que o usuário mencionar que deseja estudar, aprender, explorar, entender ou pedir uma trilha, aula ou roadmap sobre qualquer assunto, mesmo que não cite explicitamente "trilha de aprendizado". A skill cria um guia linear e multimodal com leitura, vídeos, podcasts/áudio, tutoriais práticos, livros e sinais recentes de comunidade como X/Reddit, todos avaliados rigorosamente por inspeção. O usuário pode escolher entre saída Markdown ou 4 templates HTML diferentes (completo, minimalista, timeline, feed mobile). Evite usá-la apenas para tarefas de código ou dúvidas pontuais, mas para qualquer jornada de aprendizado, acione-a imediatamente!
---

# Learning Trail Generator

Bem-vindo à skill Learning Trail Generator. O seu objetivo aqui é ajudar o usuário a aprender um tema aprofundadamente. Para isso, você gerará um arquivo `.md` ou `.html` no padrão **spine + nerves** (espinha e nervos), no qual a maior força está em você validar e inspecionar cada recurso sugerido.

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
7. Seja resiliente. Tente validar vários materiais até ter boas opções por estação.

**Gates de qualidade e variedade:**

- Cada estação deve ter no mínimo 2 nervos validados. Prefira 3-4 quando houver bons materiais.
- Evite repetir sempre o mesmo tipo de recurso. Uma estação ideal combina: 1 leitura forte, 1 vídeo ou áudio e 1 recurso prático ou de comunidade.
- A trilha completa deve conter, quando o tema permitir: pelo menos 4 vídeos, 2 podcasts/áudios, 3 tutoriais/labs, 3 sinais recentes de comunidade, 2 livros opcionais e leitura profunda suficiente para fundamentar a espinha.
- Não finalize uma trilha média/longa com apenas dois links ou apenas documentação. Isso é insuficiente para aprendizado real.
- Se uma modalidade não existir, estiver atrás de paywall, não tiver transcrição ou não puder ser validada, declare a lacuna na auditoria e compense com outra modalidade validada.
- Para fontes recentes, registre a data do post/artigo/discussão. Para X/Reddit, trate como termômetro de prática e debate, não como autoridade isolada.

**Dica para uso de Sub-agentes:**
Se o seu ambiente suportar agentes paralelos (como Claude Code usando a tool de Task), você pode gerar sub-agentes para lerem e avaliarem os recursos paralelamente, o que acelera bastante o processo. Peça a eles para retornarem o veredicto (aprovado/reprovado) e o trecho de evidência (excerpt).

### Fase 5 — Escolha do Formato de Saída

Com a espinha montada e os nervos validados, **apresente ao usuário as opções de formato de saída** e peça que ele escolha:

**Opção A — Markdown (`.md`)**
- Arquivo leve, portátil, editável em qualquer editor.
- Template: `assets/trail_template.md`

**Opção B — HTML Interativo Completo (`TEMPLATE.html`)**
- Sidebar com navegação, dark mode automático + botão manual, Alpine.js + Tailwind via CDN.
- Ideal para desktop, visual rico com navegaçao entre estações.

**Opção C — HTML Minimalista para Leitura (`TEMPLATE_MINIMAL.html`)**
- Design limpo, tipografia serifada para leitura focada, dark mode automático.
- Ideal para impressão ou leitura prolongada.

**Opção D — HTML Linha do Tempo (`TEMPLATE_TIMELINE.html`)**
- Visual em timeline vertical, cards de nervos em grid, dark mode automático.
- Ideal para progressão visual do aprendizado.

**Opção E — HTML Feed Mobile-First (`TEMPLATE_FEED.html`)**
- Estilo feed de rede social, navegação inferior, otimizado para celular.
- Ideal para consumo em dispositivos móveis.

**IMPORTANTE:** Apresente todas as 5 opções com uma breve descrição de cada (como acima) e aguarde a escolha.

### Fase 6 — Geração do Arquivo

Com o formato escolhido pelo usuário:

- Se **Markdown**: gere `./trilhas/{slug}.md` usando `assets/trail_template.md` como referência estrutural.
- Se **HTML**: preencha o template escolhido (`TEMPLATE.html`, `TEMPLATE_MINIMAL.html`, `TEMPLATE_TIMELINE.html` ou `TEMPLATE_FEED.html`) com todo o conteúdo da trilha (estações, entregas práticas, nervos multimodais, checks, boss final, recursos adicionais, livros, auditoria e lacunas) e salve em `./trilhas/{slug}.html`.

Certifique-se de substituir **todos** os placeholders `{...}` do template pelos valores reais da trilha. Inclua um resumo do mix multimodal: quantos vídeos, áudios/podcasts, tutoriais/labs, leituras profundas, livros e fontes recentes foram aprovados.

### Fase 7 — Fechamento

Avise ao usuário que a trilha foi gerada e forneça estatísticas curtas: número de estações, nervos validados, vídeos, podcasts/áudios, tutoriais/labs, leituras profundas, fontes recentes, livros, estimativa de leitura/assistir/ouvir/praticar e o formato escolhido.
Pergunte se ele deseja gerar em outro formato também, ou se está satisfeito.
Deixe o usuário guiar os próximos passos, sugerindo se ele gostaria de conversar mais, criar um projeto prático para fixar ou avançar para um próximo tema, mas não imponha as etapas automaticamente.

## Pontos Importantes para a Interação

- Procure não gerar conceitos inteiros "de cabeça"; busque validação, para garantir que as informações são frescas e exatas.
- Se o usuário não gostar de alguma seção, adapte-a iterativamente.
- Faça o processo ser transparente: mostre brevemente ao usuário quando você estiver descartando um link por ele ser inadequado, pois isso demonstra o valor da curadoria que você está fazendo.
