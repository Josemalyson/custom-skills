# Design System Extraction

Padrão para quando o usuário quer que o agente **leia o codebase existente** e gere um `design_system.html` que serve tanto pra humano consultar quanto pra agente carregar em sessões futuras como contexto canônico de "como essa app se veste".

> *"You can point Claude at a project folder or even multiple GitHub repositories (like your marketing site and your app) and ask it to extract the design system. It will analyze the CSS, components, and styling to understand your app's visual language."* — Thariq Shihipar

## Quando usar este padrão

- "Extrai o design system desse projeto"
- "Quais são os tokens / cores / fonts do meu app?"
- "Cria um style guide a partir do código"
- "Quero um design_system.html que eu possa passar como contexto pra você depois"

## Fluxo

### 1. Mapear arquivos de estilo

Procure por (em ordem de prioridade):

1. **Tokens explícitos**: `theme.json`, `tokens.css`, `design-tokens.json`, `tailwind.config.js`, `theme.ts`
2. **CSS variables / custom properties**: `:root { --color-... }` em qualquer `.css`
3. **Styled-components / Emotion**: `theme = { colors: {...} }`
4. **Tailwind**: classes utility no JSX/TSX/Vue
5. **SCSS / LESS variables**: `$primary`, `@primary`
6. **CSS-in-JS**: objeto de estilo em `style={{...}}`

### 2. Extrair os valores **que realmente se usam**

Não confunda "valor declarado" com "valor usado". Se o `tailwind.config.js` define 24 cores mas 18 nunca aparecem em nenhum componente, ignore as 18. Reporte como "encontrei mas estão dead". O design system bom mostra o que **vive**.

Métricas para contagem:
- Quantos componentes/páginas usam cada token
- Distribuição de uso (sparkline ou bar minúsculo)

### 3. Identificar inconsistências

Se você encontra 4 cinzas similares (`#1a1a1a`, `#1c1c1c`, `#202020`, `#1e1e1f`) usados aleatoriamente, **destaque**. Inconsistência é informação valiosa pro usuário.

Tipos comuns:
- Cores próximas (mesma cor visual em 3 hex diferentes)
- Spacing arbitrário entre os steps oficiais (`8`, `12`, `13px`, `16`)
- Font sizes que não estão na escala (`13px`, `17px`)
- Border radius diferentes em componentes similares

### 4. Categorizar

Estrutura recomendada do arquivo gerado:

1. **Colors** — primary, secondary, semantic (success/danger/warning/info), surfaces, text
2. **Typography** — escala, weights, line-heights, fonts em uso
3. **Spacing** — todos os steps usados, com gráfico de uso
4. **Radii** — todos os valores
5. **Shadows** — elevações em uso
6. **Motion** — duração/easing
7. **Components** — render real de cada componente identificado (button, input, card, modal, etc.)
8. **Inconsistencies** — lista das divergências encontradas, com sugestão de consolidação

### 5. Renderizar cada categoria visualmente

**Não** liste valores. **Renderize**:

- Cor: swatch grande com hex, nome do token, exemplos de uso ("Used in: Button.primary, Link.default")
- Tipo: o nome da escala, renderizado no tamanho real
- Espaço: barras horizontais proporcionais com tick em px
- Componente: o componente em si, em vários estados

### 6. Export embutido

`<details>` no fim com:
- CSS custom properties exportáveis
- Tailwind config exportável (se o projeto usa Tailwind)
- Token JSON exportável (formato `style-dictionary`)

Botão "Copy" por cada formato.

## Estrutura HTML

```html
<main>
  <header>
    <h1>Design System — <span id="project">acme-app</span></h1>
    <p>Extraído de <code>./src/styles</code> e <code>./src/components</code>. <time>2026-05-21</time></p>
    <nav class="toc">
      <a href="#colors">Colors</a>
      <a href="#type">Typography</a>
      <a href="#space">Spacing</a>
      <a href="#radii">Radii</a>
      <a href="#shadows">Shadows</a>
      <a href="#motion">Motion</a>
      <a href="#components">Components</a>
      <a href="#inconsistencies">Inconsistencies <span class="badge">4</span></a>
      <a href="#export">Export</a>
    </nav>
  </header>

  <section id="colors">
    <h2>Colors</h2>
    <article class="color-group">
      <h3>Primary</h3>
      <div class="swatches">
        <div class="swatch">
          <div class="chip" style="background: #2563eb"></div>
          <dl>
            <dt>Token</dt><dd><code>--color-primary</code></dd>
            <dt>Hex</dt><dd><code>#2563eb</code></dd>
            <dt>Used in</dt><dd>12 components</dd>
            <dt>Contrast (white)</dt><dd>4.78 ✓ AA</dd>
          </dl>
        </div>
        <!-- ... -->
      </div>
    </article>
  </section>

  <section id="components">
    <h2>Components</h2>
    <article class="component">
      <h3>Button</h3>
      <p>3 variants × 4 states</p>
      <div class="variants">
        <div><button class="btn primary">Primary</button><code>primary / default</code></div>
        <div><button class="btn primary" disabled>Primary</button><code>primary / disabled</code></div>
        <!-- ... -->
      </div>
    </article>
  </section>

  <section id="inconsistencies">
    <h2>Inconsistencies <span class="count">4 found</span></h2>
    <article class="issue">
      <h3>Multiple near-identical grays</h3>
      <p>Found 4 grays differing by less than 5% lightness:</p>
      <ul>
        <li><code>#1a1a1a</code> in <code>Header.module.css</code></li>
        <li><code>#1c1c1c</code> in <code>Footer.module.css</code></li>
        <li><code>#202020</code> in <code>Sidebar.module.css</code></li>
        <li><code>#1e1e1f</code> in <code>Modal.module.css</code></li>
      </ul>
      <p><strong>Suggestion:</strong> Consolidate to single token <code>--color-surface-dark: #1c1c1c</code>.</p>
    </article>
    <!-- ... -->
  </section>

  <section id="export">
    <h2>Export</h2>
    <details>
      <summary>CSS Custom Properties</summary>
      <pre id="css-export"><code>:root { ... }</code></pre>
      <button onclick="copy('css-export')">Copy CSS</button>
    </details>
    <details>
      <summary>Tailwind Config</summary>
      <pre id="tw-export"><code>module.exports = { theme: { ... } }</code></pre>
      <button onclick="copy('tw-export')">Copy Tailwind config</button>
    </details>
    <details>
      <summary>Style Dictionary JSON</summary>
      <pre id="sd-export"><code>{ "color": { ... } }</code></pre>
      <button onclick="copy('sd-export')">Copy JSON</button>
    </details>
  </section>
</main>
```

## Prompts que disparam este padrão

> Read this project's styles in `./src` and produce a `design_system.html`. Find what colors, type sizes, spacing values, radii, shadows are actually used (not just declared). Render each visually — color swatches with usage count, type samples at real size, spacing bars proportionally. Flag inconsistencies. End with copyable exports in CSS, Tailwind, and Style Dictionary formats.

> I have a marketing site repo and an app repo. Extract the design system from both and put them side by side in a single HTML file, with divergences highlighted in a "consolidation suggestions" section.

> Use the existing `design_system.html` in this folder as the canonical reference, then generate the new <feature>. Match its tokens — don't introduce new colors or spacing values.

## Patterns para refresh contínuo

Design system extraído fica desatualizado. Sugira para o usuário:

- Salvar o `.html` como `docs/design_system.html` no repo
- Re-gerar quando houver mudança significativa em styles (a cada release maior?)
- Diff entre versões: gerar novo, comparar com antigo, mostrar o que adicionou/mudou

## Armadilhas

- **Tokens declarados ≠ tokens usados** — sempre conte ocorrências reais
- **Listar valores em vez de renderizar** — uma tabela com hex perde o ponto. Cor tem que ser vista
- **Ignorar inconsistências por educação** — a seção de inconsistências é onde o documento mais ajuda. Não suavize
- **Cores em RGB / HSL / hex misturadas** — normalize para hex no display (mantém comparação fácil); mostre os outros formatos em hover/copy
- **Components renderizados de imagem** — não. Renderize **o HTML/CSS real**. Inspeção tem que funcionar
