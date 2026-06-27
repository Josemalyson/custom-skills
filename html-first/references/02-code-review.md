# Code Review & Understanding

Diff e call-graph carregam **informação espacial** — Markdown flatten essa informação. HTML permite renderizar a mudança como diff anotado, desenhar o módulo como caixas e flechas, e escrever a descrição de PR que reviewers efetivamente leem.

## Quando usar este padrão

- "Revise esse PR / commit / branch"
- "Crie um writeup do PR para os reviewers"
- "Explica esse módulo / pacote / serviço"
- "Mapeia esse codebase"
- "Por que tem tanta latência aqui — me ajuda a ler o código"

## Três sub-padrões

### A. Annotated Pull Request (diff anotado)

Para **revisar** um PR alheio ou auditar uma mudança própria.

Estrutura:

1. **Header** com TL;DR do que o PR faz, número de arquivos, +X/-Y linhas, score de risco
2. **Files changed** como navegação lateral colável (clica e pula)
3. **Diff renderizado** lado-a-lado (não unified) — esquerda = antes, direita = depois
4. **Margin annotations** — comentários do reviewer na margem direita, ancorados em linhas
5. **Severity tags** — `info`, `nit`, `suggestion`, `blocker` com cores distintas (não red/orange/yellow random — escolha um sistema consistente)
6. **Jump-to-finding** — lista de findings no topo, click navega ao ponto

Cores convencionais para diff (do GitHub, mantenha):
- Add: bg `#e6ffec` (light) / `#0d3318` (dark), border `#28a745`
- Del: bg `#ffeef0` (light) / `#3d1212` (dark), border `#d73a49`
- Context: bg neutro
- Anotação: borda esquerda com cor da severity, sem invadir o diff

### B. PR Writeup (do autor para reviewers)

Escrito **pelo autor da mudança**, antes do review, para reduzir o "what is this PR even doing" effect.

Estrutura:

1. **Motivation** — qual problema, link pro ticket/issue
2. **Before / After** — comparação visual lado-a-lado quando relevante (UI, métricas, comportamento)
3. **File-by-file tour** — para cada arquivo modificado, **1-2 frases** do *why* (não do *what* — o diff já mostra o what)
4. **Where to focus the review** — "Pessoal de X, olhem com atenção o arquivo Y nas linhas Z"
5. **Out of scope** — o que esse PR explicitamente **não** faz
6. **Testing** — como você testou, o que ainda falta testar
7. **Rollout plan** — feature flag? migration? rollback strategy?

### C. Module Map (entendimento de código)

Para **navegar** um codebase desconhecido. Saída visual + leitura.

Estrutura:

1. **Entry points** listados no topo — onde a execução começa
2. **Box-and-arrow diagram** — módulos como boxes, dependências como arrows
3. **Hot path destacado** — o caminho da requisição típica, em cor distinta
4. **Hover/click annotations** — clicar em um box mostra o que aquele módulo faz, em quais arquivos
5. **Glossary** — termos do domínio que aparecem no código, definidos em hover
6. **Footnotes** com snippets dos pontos-chave (5-15 linhas cada, não o módulo inteiro)

## Estrutura HTML — diff anotado

```html
<main class="diff-view">
  <header>
    <h1>PR #1234: <code>refactor(auth): JWT → opaque tokens</code></h1>
    <dl class="meta">
      <dt>Files</dt><dd>12</dd>
      <dt>Changes</dt><dd>+340 / −210</dd>
      <dt>Risk</dt><dd class="risk-medium">Medium</dd>
    </dl>
    <nav>
      <h2>Findings (5)</h2>
      <ol>
        <li><a href="#f1" class="sev-blocker">Race condition in token rotation</a></li>
        <li><a href="#f2" class="sev-suggestion">Consider extracting retry logic</a></li>
        <!-- ... -->
      </ol>
    </nav>
  </header>

  <article class="file" id="file-auth-service">
    <h2><code>auth-service.ts</code></h2>
    <div class="diff-split">
      <pre class="before"><code>... antes ...</code></pre>
      <pre class="after"><code>... depois ...</code></pre>
    </div>
    <aside class="annotations">
      <div id="f1" class="annotation sev-blocker" data-line="142">
        <strong>Blocker</strong>: Se duas requests rotacionarem ao mesmo tempo, o second wins e a primeira loga out. Precisa de lock.
      </div>
    </aside>
  </article>
  <!-- repetir por arquivo -->
</main>
```

## Estrutura HTML — module map

```html
<main>
  <header>
    <h1>Module Map: <code>billing/</code></h1>
    <p>Entry: <code>billing/api/handler.ts</code> → request lifecycle</p>
  </header>

  <section class="diagram">
    <!-- SVG com nodes posicionados absolutamente -->
    <svg viewBox="0 0 1000 600">
      <g class="node hot-path" data-module="handler">
        <rect x="50" y="100" width="120" height="60" rx="6"/>
        <text x="110" y="135" text-anchor="middle">handler</text>
      </g>
      <!-- arrows, outros nodes -->
    </svg>
  </section>

  <section class="modules">
    <article id="m-handler">
      <h2>handler</h2>
      <p><strong>O que faz:</strong> Parse request, validate, route to service.</p>
      <p><strong>Arquivos:</strong> <code>handler.ts</code>, <code>validators.ts</code></p>
      <details>
        <summary>Key snippet</summary>
        <pre><code>...</code></pre>
      </details>
    </article>
    <!-- ... -->
  </section>
</main>
```

## Prompts que disparam este padrão

> Help me review this PR by creating an HTML artifact. I'm not familiar with the <subsistema> logic, so focus on that. Render the actual diff in two columns with inline margin annotations, color-code findings by severity (blocker / suggestion / nit / info), and add a "Findings" list at the top that jumps to each finding.

> Write the PR description for the change I just made. Single HTML file: motivation linked to <ticket>, before/after comparison, a file-by-file tour with one-line *why* per file, where reviewers should focus, what's out of scope, how I tested it, and the rollout plan.

> Read the <module> directory and produce an HTML module map. Diagram the boxes and arrows, highlight the hot path for <typical request>, list entry points, and add hover annotations explaining what each box does. Include key code snippets in `<details>` collapsibles.

## Armadilhas

- **Diff unified** em vez de split — em telas wide, perde-se a comparação. Use split, com fallback mobile (acima de 720px split, abaixo unified).
- **Severity como ranking de cor random** — defina um sistema: blocker (vermelho saturado), suggestion (azul), nit (cinza), info (verde-azulado). Mantenha consistente.
- **"File-by-file tour" repetindo o diff** — descreva o *why*, não o *what*. Se o file-by-file tour for igual ao diff, está redundante.
- **Module map gigante** — se o codebase tem 50+ módulos, faça um por sub-sistema, não um monolítico ilegível.
- **Annotations soltas** — sempre ancorar a linha específica via `data-line` ou `id` no nó do diff.
