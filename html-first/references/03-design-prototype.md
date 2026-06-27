# Design & Prototype

HTML **é** o meio em que design systems acabam vivendo no produto. Logo, é o formato natural para falar sobre ele. Tokens viram swatches, componentes viram contact sheets, e o artefato pode ser realimentado como contexto pro próximo prompt.

## Quando usar este padrão

- "Mockup da tela X" / "Design preliminar"
- "Design system" / "Tokens" / "Style guide"
- "Variantes do componente Y" (todos os tamanhos, estados, intents)
- "Protótipo dessa animação / transição"
- "Como uma feature ficaria visualmente"

## Três sub-padrões

### A. Living Design System (`design_system.html`)

Artefato que serve duas audiências ao mesmo tempo:

- **Humano**: vê cor, tipo, espaçamento, componente real
- **Agente**: lê em sessões futuras como contexto canônico de "como essa app se veste"

Estrutura:

1. **Color palette** — swatches com nome do token, hex, uso recomendado, contraste vs background
2. **Typography scale** — todas as escalas com nome (h1, h2, body, caption) renderizadas de verdade
3. **Spacing system** — barras visuais com `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64`, nome e valor
4. **Radii & shadows** — exemplos visuais
5. **Component sheet** — botão (todos states), input, card, modal, etc., cada um renderizado
6. **Do's and don'ts** — exemplos certo/errado lado-a-lado
7. **CSS tokens** em `<details>` no fim — exportável

Característica crítica: **cada elemento é HTML real**, não imagem. Inspeciona-se com devtools. Copia-se o código.

### B. Component Variant Sheet

Para revisar **um** componente em **todas** as suas combinações de uma vez.

Estrutura:

- Grid com todas as combinações de `size × intent × state`
- Cada célula com label do que é (ex: "primary / medium / hover")
- Background da grid em duas cores (light / dark) para verificar contraste
- Botão "copy CSS" por variante

### C. Animation Sandbox (prototyping)

Animação **não pode ser descrita**, tem que ser sentida. Página com a transição isolada + controles para tunar parâmetros em tempo real.

Estrutura:

1. O elemento sendo prototipado, isolado em um palco
2. Controles ao lado:
   - Duration (slider 50–2000ms)
   - Easing (select com `ease`, `ease-in-out`, `cubic-bezier(...)`)
   - Trigger (botão "play" + opção "loop")
3. **Live preview** que atualiza ao mexer nos controles
4. **Code output** que mostra o CSS/JS atual
5. **"Copy parameters"** quando o usuário encontrar o que gostou

### Clickable Flow (prototyping de interação)

Várias telas linkadas, suficiente fidelidade para sentir o fluxo de interação completo. Cada tela é uma `<section>` com `id`, links entre elas via âncoras ou JS leve.

## Estrutura HTML — design system

```html
<main>
  <header>
    <h1>Design System: <span id="project">Acme App</span></h1>
    <p>Single source of truth para tokens, tipografia, espaçamento e componentes.</p>
  </header>

  <section id="colors">
    <h2>Colors</h2>
    <div class="swatch-grid">
      <article class="swatch" style="--c: #2563eb;">
        <div class="chip"></div>
        <code>--color-primary</code>
        <code>#2563eb</code>
        <small>AA on white: 4.78 ✓</small>
      </article>
      <!-- ... -->
    </div>
  </section>

  <section id="type">
    <h2>Typography</h2>
    <div class="type-sample" style="font-size: var(--text-xxl);">Display XXL — 3rem</div>
    <div class="type-sample" style="font-size: var(--text-xl);">Display XL — 2.25rem</div>
    <!-- ... -->
  </section>

  <section id="spacing">
    <h2>Spacing</h2>
    <div class="spacer-row" data-value="4">4px</div>
    <div class="spacer-row" data-value="8">8px</div>
    <!-- ... barras de comprimento proporcional -->
  </section>

  <section id="components">
    <h2>Components</h2>
    <article class="component-block">
      <h3>Button</h3>
      <div class="variant-grid">
        <div class="variant"><button class="btn primary">Primary</button><small>primary / default</small></div>
        <div class="variant"><button class="btn primary" disabled>Primary</button><small>primary / disabled</small></div>
        <!-- ... -->
      </div>
    </article>
  </section>

  <details>
    <summary>Export CSS tokens</summary>
    <pre><code>
:root {
  --color-primary: #2563eb;
  --color-bg: #ffffff;
  /* ... */
}
    </code></pre>
  </details>
</main>
```

## Estrutura HTML — animation sandbox

```html
<main class="sandbox">
  <section class="stage">
    <button id="play" class="prototype-button">Click me</button>
  </section>

  <aside class="controls">
    <label>Duration: <input type="range" id="dur" min="50" max="2000" value="300"> <output for="dur">300</output>ms</label>
    <label>Easing: 
      <select id="ease">
        <option>ease</option>
        <option>ease-in</option>
        <option>ease-out</option>
        <option>ease-in-out</option>
        <option>cubic-bezier(0.4, 0, 0.2, 1)</option>
      </select>
    </label>
    <button id="trigger">Play</button>
    <pre id="output"><code>/* CSS atualiza aqui */</code></pre>
    <button id="copy">Copy parameters</button>
  </aside>
</main>
```

## Prompts que disparam este padrão

> Build a `design_system.html` from this codebase. Read the CSS in `<path>`, extract color tokens, typography scale, spacing values, and the 6 most used components. Render each visually — not as a list of values, as real swatches, real type samples, real buttons. End with a `<details>` block that exports the tokens as CSS custom properties.

> Show me every variant of the `<Button>` component in one page. All sizes × all intents × all states (default / hover / focus / disabled / loading). Background should toggle light/dark. Add a "copy CSS" button per variant.

> I want to prototype a "click → animate → settle" interaction on the checkout button. Single HTML file: the button in isolation, sliders for duration, easing curve, and translate distance. Live preview, code output, "copy parameters" button.

## Patterns para extrair design system de codebase existente

(Ver também `references/09-design-system-extraction.md`)

Quando o pedido é "extraia o design system desse projeto":

1. **Leia** os arquivos de tema, CSS, tokens, styled-components, tailwind config
2. **Identifique** os valores recorrentes (não os "design tokens canônicos", mas os que **realmente** se usam)
3. **Categorize** em color / type / space / radius / shadow / motion
4. **Renderize** cada um visualmente
5. **Sinalize divergências** — "Encontrei 4 tons de cinza similares, sugiro consolidar em 2"

## Armadilhas

- **Default AI gradients** — uma das maneiras mais rápidas de fazer um design system "parecer LLM" é colocar gradiente roxo-azul em tudo. Use cores **do projeto**, não de paleta default.
- **Componentes só visuais, sem estado** — botão sempre em rest. Mostre hover/focus/disabled/loading também.
- **Tokens com nomes ruins** — `--gray-500` é OK, `--text-secondary` é melhor. Use semantic naming quando o uso é claro.
- **Spacing arbitrário** — `--space-13` não existe se seu sistema é 4/8/12/16/24. Não invente steps no meio.
- **Animação sem `prefers-reduced-motion`** — sempre respeite.
