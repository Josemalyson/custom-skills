---
name: learning-trail
description: "Use esta skill SEMPRE que o usuário pedir para estudar, aprender, explorar, entender ou gerar uma trilha/aula/roadmap sobre um assunto. Gera um arquivo Markdown estruturado como narrativa linear de estações curtas (coluna vertebral) com recursos externos VALIDADOS POR CONTEÚDO (nervos). O agente atua como núcleo validador: lê/transcreve cada recurso antes de recomendá-lo, garantindo que cada link entregue exatamente o que promete. Triggers PT-BR: 'quero aprender X', 'me ensina X', 'gera trilha de X', 'estudar X', 'roadmap de X', 'aula de X'. Triggers EN: 'teach me X', 'learn X', 'study X', 'roadmap for X'. NÃO usar para: tarefas de código, debugging, perguntas factuais isoladas, conversa casual."
version: 3.0
---

# Learning Trail Generator

Gera um arquivo `.md` no padrão **spine + nerves** com **validação atômica de recursos**.

## Arquitetura de confiança

Esta skill opera no modelo **trust by inspection**, não *trust by reputation*. Significa:

- **Não** filtra fontes por whitelist estática antes da busca.
- **Sim** valida o conteúdo real de cada candidato antes de recomendá-lo.
- Cada recurso recomendado é uma **transação atômica**: ou foi inspecionado e aprovado, ou não entra na trilha. Sem nervos "meia-bomba".

Reputação histórica de uma fonte é usada apenas como tie-breaker entre candidatos equivalentes — nunca como filtro bloqueante. Um blog desconhecido pode ser excelente; um venue famoso pode estar desatualizado no subtópico específico.

## Metáfora operacional

Jogo de tabuleiro:
- **Tabuleiro** = mapa da trilha (visível antes de começar)
- **Casas** = estações de conhecimento (4 a 10 por trilha)
- **Caminhos laterais** = nervos (recursos VALIDADOS de aprofundamento)
- **Boss final** = 5 perguntas socráticas

## Princípio fundamental

Você é o **núcleo validador**. Não escreve enciclopédia do tópico — escreve a **narrativa do raciocínio** (estações) e **prova** que cada recurso recomendado entrega o que promete (validação).

## Regras invioláveis

1. **PROIBIDO usar memória como fonte primária.** Todo conteúdo factual deve ser validado por busca web na sessão atual.
2. **PROIBIDO recomendar recurso não-validado.** Se não conseguiu ler/transcrever, não entra.
3. **Idioma detectado.** Detecte da requisição inicial e gere o arquivo inteiro nesse idioma.
4. **Sem gabarito.** Checks e perguntas finais são socráticos.
5. **Nada é imposto.** Projeto prático e próximo tópico são sempre perguntados.
6. **Estações são pequenas.** 5-10 min de leitura cada. Maior que isso, quebre.

---

## Workflow do agente

### Fase 1 — Captura e clarificação

1. Receba o assunto e detecte o idioma.
2. Pergunte interativamente:
   - "Quer plano automático ou prefere customizar (nº de estações, foco em teoria/prática)?"
   - "Tem fontes específicas que gostaria de incluir? (PDFs, livros, links, repositórios). Se sim, me passe agora."

### Fase 2 — Mapeamento (busca exploratória)

Busca AMPLA, sem filtro de whitelist. Objetivo: ter universo grande de candidatos para validar depois.

Execute nesta ordem:

1. **Validação do tópico:** terminologia atual, escopo, estado.
2. **Mapeamento da narrativa:** "[topic] explained step by step", "[topic] fundamentals", "how to teach [topic]".
3. **Pré-requisitos:** "prerequisites for [topic]" — alimenta o DAG anterior.
4. **Próximos passos:** "advanced topics after [topic]" — alimenta o DAG posterior.
5. **Candidatos a recurso (busca larga):**
   - Vídeos: mínimo 8 candidatos. NÃO filtre por canal nesta fase.
   - Papers: mínimo 6 candidatos. Busque em arXiv, Google Scholar, Semantic Scholar.
   - Tutoriais: mínimo 8 candidatos. NÃO filtre por blog/site.
   - Livros: mínimo 6 candidatos.

Se o usuário forneceu fontes próprias, elas vão **direto para a Fase 3** (validação), pulando esta fase para esses itens.

### Fase 3 — Desenho da espinha (estações)

Defina sequência de estações com base na pesquisa exploratória:

| Tipo de tópico | Nº típico de estações |
|---|---|
| Skill prática (ex: "Dockerfile") | 4-5 |
| Conceito fundamental (ex: "O que é IA") | 5-7 |
| Tecnologia concreta (ex: "Kubernetes") | 7-10 |
| Padrão arquitetural (ex: "Event Sourcing") | 6-8 |
| Tema teórico denso (ex: "Teorema CAP") | 5-7 |

**Regra de ouro:** se ultrapassar 10, sugira sub-trilhas. Não infle.

**Estrutura narrativa:**
- Estação 1: o problema / motivação
- Intermediárias: desenvolvimento progressivo
- Penúltima: quando NÃO usar / limitações
- Última: síntese / como tudo se encaixa

### Fase 4 — Validação Atômica de Recursos (CORE DA SKILL)

> Esta é a parte mais importante. Cada recurso é uma transação ACID: ou passa por todas as etapas e commita, ou aborta e tenta outro candidato.

Para CADA slot de nervo necessário (típico: 8-15 nervos por trilha):

#### Passo 4.1 — Fetch obrigatório

Use `web_fetch` na URL do candidato. Confirme que retornou 200 e tem conteúdo substantivo.

#### Passo 4.2 — Extração de material substantivo

Por tipo de recurso:

**🎥 Vídeo (YouTube principalmente):**
- Obter transcript. Caminhos, em ordem de preferência:
  1. API/biblioteca de transcript do YouTube (`youtube-transcript-api`)
  2. `yt-dlp --write-auto-subs --skip-download` para baixar legendas
  3. Whisper local/API se as duas opções acima falharem
- Se nenhuma funcionar: validar via descrição completa do vídeo + 10 top comentários + cross-check com outras menções do vídeo na web.
- Se mesmo assim não conseguir validar conteúdo: **REPROVA** e busca outro.

**📚 Paper acadêmico:**
- Fetch do PDF (preferencial) ou HTML.
- Leitura obrigatória: abstract + introduction + conclusion.
- Idealmente: methodology summary se relevante.

**🛠 Tutorial/blog:**
- Fetch da página inteira.
- Se < 3000 palavras: leia tudo.
- Se ≥ 3000 palavras: leia introdução + heading principais + conclusão + uma seção do meio.

**📖 Livro:**
- Não é possível ler o livro inteiro. Validação por proxy:
  - Table of Contents (página oficial da editora ou Amazon "Look Inside")
  - 3 reviews qualificadas (Goodreads, Amazon, blogs técnicos)
  - Capítulo de amostra se disponível
  - Index/sumário verificando cobertura do subtópico

#### Passo 4.3 — Validação contra 3 critérios objetivos

Após extrair o material, responda explicitamente:

1. **Cobertura:** o recurso cobre o subtópico ESPECÍFICO da estação para a qual seria nervo? (não basta "fala do tema geral")
2. **Profundidade:** o nível do recurso (intro/intermediário/avançado) bate com o `level` da trilha e da estação?
3. **Atualidade:** para tópicos voláteis (cloud, AI, ferramentas modernas), o recurso é recente o bastante (≤ 3 anos para AI/ML, ≤ 5 anos para cloud nativo, sem limite para fundamentos atemporais)?

Se as 3 respostas forem **sim**, recurso APROVADO. Senão, REPROVADO.

#### Passo 4.4 — Sinais positivos (boost, não filtro)

Após aprovação, use estes sinais para priorizar entre recursos aprovados equivalentes:
- Canal/autor com histórico técnico forte (3Blue1Brown, Karpathy, Fowler, Kleppmann, ByteByteGo, etc.)
- Venue acadêmico reconhecido (NeurIPS, ICML, USENIX, SIGCOMM, etc.)
- Editora técnica (O'Reilly, Manning, Addison-Wesley, MIT Press, etc.)
- Docs oficiais do projeto (sempre boost máximo)

Esses sinais NÃO bloqueiam recursos sem eles — apenas desempatam.

#### Passo 4.5 — Persistência e desistência

- Por slot, tente até **10 candidatos** antes de desistir.
- Meta: 3 aprovados por tipo de recurso (3 vídeos, 3 papers, 3 tutoriais, 3 livros).
- Se chegou em 10 sem 3 aprovados: pare e documente honestamente no arquivo final:
  > *Validamos N recursos deste tipo após inspecionar 10 candidatos. Recomendação: forneça fontes manualmente na próxima execução para enriquecer este slot.*

#### Passo 4.6 — Commit transacional

Quando aprovado, registre no objeto do recurso:
- URL
- Título
- Autor/Canal/Editora
- Trecho-chave validado (1-2 frases extraídas do material que provam a cobertura)
- Critério de aprovação (qual subtópico da estação ele aprofunda)
- Timestamp da validação

### Fase 5 — Distribuição dos nervos por estação

Com a pool de recursos aprovados, distribua como nervos contextuais por estação. Regras:

- 1 a 3 nervos por estação.
- Cada nervo aprofunda um ponto **específico** da estação (não o tema geral).
- Diversidade de mídia por estação quando possível.
- Recursos aprovados que não viraram nervo → bloco "Recursos adicionais" no final.

### Fase 6 — Geração do arquivo

Salve em `./trilhas/{slug}.md`. Slug: kebab-case ASCII. Use o template da próxima seção.

### Fase 7 — Conversa pós-geração

> "Trilha gerada em `./trilhas/{slug}.md`. São {N} estações, {M} nervos validados, ~{X} min de leitura. Quando você terminar e responder mentalmente as 5 perguntas finais, me avise. Aí eu te ofereço: (a) gerar um plano de projeto prático sobre o que você aprendeu, ou (b) executar a skill novamente para o próximo tópico."

**Nunca gere projeto prático automaticamente. Nunca avance para o próximo tópico sem confirmação.**

---

## 🤖 Padrão de sub-agente (opcional, mas recomendado)

Para harnesses que suportam sub-agents (Claude Code com Task tool, LangGraph, OpenAgents, etc.), paralelize a Fase 4:

```
for each candidate in candidates:
    spawn_subagent({
      task: f"""
        Read URL: {candidate.url}
        Goal: validate if this resource teaches "{station.subtopic}" at "{level}".
        Steps:
          1. Fetch full content (or transcript if YouTube)
          2. Extract material per type rules in learning-trail SKILL
          3. Answer: covers subtopic? appropriate depth? recent enough?
          4. If approved: extract 1-2 sentence validated excerpt
          5. Return: {approved: bool, excerpt: str, reason: str}
      """,
      tools: [web_fetch, web_search, youtube_transcript]
    })
```

**Vantagens:**
- Paraleliza validação (10 candidatos validados em ~tempo de 1)
- Isola contexto (transcripts e PDFs não inflam o agente principal)
- Cada sub-agent é descartável após retornar veredicto

Se o harness NÃO suporta sub-agents, execute sequencialmente — funciona, só é mais lento.

---

## Template do arquivo gerado

````markdown
---
id: {slug}
topic: {Título exatamente como o usuário pediu}
language: {pt-BR | en | es | ...}
level: {beginner | intermediate | advanced}
stations_count: {N}
nerves_validated: {M}
estimated_reading_minutes: {soma das estações}
estimated_full_minutes: {leitura + tempo de todos os nervos}
tags: [{tag1}, {tag2}]
prerequisites: [{id-anterior-1}, {id-anterior-2}]
next_steps: [{id-proximo-1}, {id-proximo-2}, {id-proximo-3}]
created_at: {YYYY-MM-DD}
sources_validated_at: {YYYY-MM-DD}
generated_by: learning-trail-skill@v3.0
---

# {Título}

## 🎯 O que você vai conseguir fazer ao final

{3-5 linhas. Habilidades concretas que o aluno terá ao chegar no fim da trilha.}

## 🧱 Pré-requisitos

{Se vazio: "Nenhum — trilha de entrada".}

- [[{id-anterior}]] — {1 linha de por que importa}

## 🗺 Mapa da Trilha

| # | Estação | Tempo leitura | Nervos |
|---|---------|---------------|--------|
| 1 | {Título estação 1} | ~{X} min | {n} |
| 2 | {Título estação 2} | ~{X} min | {n} |
| ... | ... | ... | ... |
| N | {Título estação N} | ~{X} min | {n} |

**Boss final:** 5 perguntas socráticas de validação.

**Tempo total estimado:** ~{X} min lendo + ~{Y} h se seguir todos os nervos.

**Recursos validados:** {M} nervos passaram por inspeção atômica de conteúdo.

## 📖 Se você quiser ir longe (livros opcionais)

> Livros não são pré-requisito para concluir a trilha. São investimentos para quem se apaixonar pelo tema. Validados via Table of Contents + reviews qualificadas.

### {Título}
- **Autor(es):** {nomes}
- **Editora:** {nome}
- **Foco:** {introdutório | referência | avançado}
- **Por que ler:** {1-2 linhas baseadas na ToC validada}
- 🔍 **Validado:** {trecho-chave da ToC ou review que prova relevância}

{Repetir para os 3 livros.}

---

## 🎯 Estação 1 de {N}: {Título narrativo}

> ⏱ ~{X} min leitura • 🔌 {Y} nervo(s) validado(s)

{Parágrafo narrativo de 3-6 linhas. Conecta com estação anterior (se houver). Termina com tensão.}

**🔌 Nervos:**

- 🎥 [{Título}]({url}) — *{Canal}, {duração}*
  - **quando seguir:** {1 frase contextual}
  - 🔍 **validado:** {trecho extraído do transcript/conteúdo que prova cobertura específica do subtópico — ex: "transcript confirma cobertura de Q/K/V e multi-head attention nos minutos 7-14"}

- 📚 [{Título}]({url}) — *{Autores}, {ano}, {venue}*
  - **quando seguir:** {1 frase}
  - 🔍 **validado:** {trecho do abstract ou conclusão que prova relevância}

**🧭 Check de avanço:**
> Antes de seguir: {pergunta socrática binária}. Se não, releia ou veja o nervo {X}.

[Estação 2 →](#-estação-2-de-n-título)

---

{... estações intermediárias seguem o mesmo padrão ...}

---

## 🎯 Estação {N} de {N}: Síntese — como tudo se encaixa

> ⏱ ~{X} min leitura

{Recapitula a jornada, conecta os pontos. Prepara o boss final.}

[← Estação {N-1}](#)

---

## 🏁 Boss Final: 5 perguntas socráticas

> Sem gabarito. Responda mentalmente ou por escrito.

1. **Conceitual:** {pergunta sobre fundamentos}
2. **Conceitual:** {pergunta sobre diferenciação}
3. **Aplicada:** {cenário X — como usaria Y?}
4. **Aplicada:** {descreva sistema real onde isso resolveria um problema}
5. **Crítica:** {quando isso é escolha errada? Que sinais indicariam outra abordagem?}

---

## ➡️ Próximos passos sugeridos

- [[{id-proximo-1}]] — {1 linha do porquê}
- [[{id-proximo-2}]] — {1 linha do porquê}
- [[{id-proximo-3}]] — {1 linha do porquê}

## 📦 Recursos adicionais (validados, sem virar nervo)

- 🎥 [{Título}]({url}) — 🔍 validado: {trecho curto}
- 📚 [{Título}]({url}) — 🔍 validado: {trecho curto}
- 🛠 [{Título}]({url}) — 🔍 validado: {trecho curto}

## 📌 Fontes adicionais informadas pelo usuário

{Se houver. Senão, omita.}

## 🔍 Auditoria da validação

- Candidatos inspecionados: {número total que passaram pela Fase 4}
- Aprovados: {número que viraram nervos ou recursos adicionais}
- Reprovados: {número que falharam em cobertura/profundidade/atualidade}
- Lacunas declaradas: {liste se algum slot não atingiu meta de 3 aprovados}

---

*Gerado por `learning-trail` skill v3.0 em {timestamp}. Cada recurso passou por inspeção atômica de conteúdo (trust by inspection). Links validados na data acima — re-execute a skill se trilha tiver > 6 meses.*
````

---

## Heurísticas pedagógicas

### Como escrever o parágrafo narrativo de uma estação

1. **Conecte com a anterior:** "Até aqui você viu X. Agora..."
2. **Um conceito por estação.** Se aparecer mais de um, quebre.
3. **Termine com tensão.** Última frase cria a pergunta que a próxima estação ou o nervo responde.
4. **Evite definições enciclopédicas.** "X é Y" é fraco. "X resolve o problema de Y porque..." é forte.

### Como escolher os nervos

1. **Contexto explícito sempre** — "quando seguir: [motivo]".
2. **Granularidade compatível.** Vídeo de 30 min ≠ nervo de uma estação. Vai pra "Recursos adicionais".
3. **Diversidade de mídia** quando possível.
4. **Trecho validado obrigatório.** Sem prova de leitura/transcrição, não vira nervo.

### Como escrever o check de avanço

- Binário (sim/não).
- Com fallback explícito.
- Pergunta de produção: "Você consegue **explicar** X" > "Você lembra de X".

### Como escrever as 5 perguntas do boss final

- 2 conceituais + 2 aplicadas + 1 crítica.
- Devem exigir integração de múltiplas estações.
- **Sem gabarito. Nunca.**

---

## Anti-padrões (NÃO FAÇA)

- ❌ Recomendar recurso sem ter lido o conteúdo real.
- ❌ Confiar em título + snippet de busca como prova de relevância.
- ❌ Filtrar candidatos por whitelist antes da validação.
- ❌ Preencher slot com recurso reprovado por falta de opções (declare lacuna).
- ❌ Escrever "explicação inteira" do tópico sem buscar nada.
- ❌ Criar estação enciclopédica longa (> 10 min de leitura).
- ❌ Listar nervo sem o campo "validado:".
- ❌ Inflar para 12+ estações em vez de sugerir sub-trilhas.
- ❌ Dar gabarito de check ou pergunta final.
- ❌ Gerar projeto prático ou pular para próximo tópico sem o usuário pedir.
- ❌ Misturar idiomas na estrutura.
- ❌ Inventar URLs, autores, papers ou trechos. Em dúvida → omita.

---

## Exemplo de invocação correta

**Usuário:** "quero entender Service Mesh"

**Agente (em ordem):**
1. Detecta idioma: `pt-BR`.
2. Pergunta: "Automático ou customizado?" → "auto". "Fontes próprias?" → "não".
3. **Fase 2:** busca AMPLA — 12 vídeos candidatos, 8 papers, 14 tutoriais, 9 livros.
4. **Fase 3:** desenha espinha (7 estações).
5. **Fase 4:** valida cada candidato individualmente.
   - Vídeo "Service Mesh in 100 Seconds" (Fireship) → transcript baixado → cobre só visão geral → APROVADO para Estação 1 mas não E3.
   - Vídeo "Istio Architecture Deep Dive" (canal pequeno) → transcript baixado → cobre detalhadamente data/control plane → APROVADO para Estação 4 (não tem o "boost" do canal famoso, mas conteúdo passa).
   - Paper "The Service Mesh: What Every Software Engineer Should Know" → abstract+conclusão lidos → APROVADO para Estação 7.
   - Tutorial "Istio em 30 min" (blog desconhecido) → conteúdo lido → desatualizado (Istio 1.6, atual é 1.20) → REPROVADO. Busca substituto.
   - ... até completar 3 aprovados por tipo.
6. **Fase 5:** distribui nervos contextualmente por estação.
7. **Fase 6:** gera `./trilhas/service-mesh.md` com cada nervo carregando seu trecho validado.
8. **Fase 7:** "Trilha pronta. Projeto prático ou próximo tópico?"
