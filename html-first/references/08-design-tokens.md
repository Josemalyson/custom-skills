# Design Tokens & Anti-AI-Aesthetic

A maneira mais rápida de fazer um artefato HTML parecer "saída de LLM sem cuidado" é cair nos padrões visuais que LLMs convergem por default. Esta reference define o baseline tipográfico desta skill e enumera os anti-padrões a evitar ativamente.

## Anti-padrões — sinais de "default AI aesthetic"

Os seguintes elementos visuais sinalizam imediatamente "isso saiu de um LLM sem ajuste":

### Cores

- ❌ **Gradiente roxo → azul** (`linear-gradient(135deg, #667eea, #764ba2)`)
- ❌ **Indigo dominante** (`#4f46e5`, `#6366f1`, `#818cf8`, `#a5b4fc`) — uso de "três tons de indigo" em tudo
- ❌ **Dark mode com `#1a1a2e`** ou variantes "fundo escuro azulado neon"
- ❌ **Acentos neon** (`#00f5ff`, `#39ff14`) sem motivo
- ❌ **Cores random** — 7+ cores diferentes na página sem significado

### Efeitos

- ❌ **Glassmorphism gratuito** (`backdrop-filter: blur(10px)` em containers)
- ❌ **Sombra suave em tudo** (`box-shadow: 0 20px 60px rgba(0,0,0,0.1)`) — em cards, botões, headers, sem critério
- ❌ **Border-radius 1rem** universal em cards
- ❌ **Animação `fade-in-up`** em cada elemento ao carregar a página
- ❌ **Hover scale** (`transform: scale(1.05)`) em cards

### Tipografia

- ❌ **Font-weight 300** em texto de leitura
- ❌ **Letter-spacing negativo agressivo** em headers (`-0.05em`)
- ❌ **All-caps com tracking exagerado** em labels

### Conteúdo

- ❌ **Headers com emoji decorativo** (`✨ Visão Geral`, `🚀 Próximos Passos`, `📊 Métricas`)
- ❌ **Tag "Powered by AI"** ou similar no footer
- ❌ **Cards genéricos** "Feature 1 / Feature 2 / Feature 3" com lorem ipsum

### Estrutura

- ❌ **Hero gigante com gradiente** + 3 cards abaixo + "CTA Button" — vira landing page de SaaS qualquer

## Baseline tipográfico (use como ponto de partida)

```css
:root {
  /* Cores neutras, baseadas em escalas de cinza com matiz suave */
  --bg: #fafaf9;
  --bg-elevated: #ffffff;
  --bg-muted: #f4f4f3;
  --border: #e7e7e5;
  --text: #18181b;
  --text-muted: #6b6b70;
  --text-subtle: #9ca3af;

  /* Acento único — escolha UMA cor, não três */
  --accent: #0f766e;            /* teal-700; substituir pelo brand do projeto */
  --accent-bg: #ccfbf1;
  --accent-text: #134e4a;

  /* Semantic — só quando significam algo */
  --success: #15803d;
  --warning: #b45309;
  --danger: #b91c1c;
  --info: #1d4ed8;

  /* Tipografia */
  --font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, "JetBrains Mono", "Fira Code", "SF Mono", Menlo, Consolas, monospace;
  --font-serif: ui-serif, Georgia, "Times New Roman", serif;

  /* Escala tipográfica — modular, base 16px, ratio 1.25 */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;

  /* Espaçamento — base 4px */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;

  /* Radius — apenas 3 valores */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;

  /* Shadow — só quando necessário, evite sombras decorativas */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-focus: 0 0 0 3px rgba(15, 118, 110, 0.25);

  /* Motion */
  --transition: 150ms ease-out;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f0f10;
    --bg-elevated: #18181b;
    --bg-muted: #27272a;
    --border: #2d2d31;
    --text: #fafafa;
    --text-muted: #a1a1aa;
    --text-subtle: #71717a;
    --accent: #5eead4;
    --accent-bg: #134e4a;
    --accent-text: #ccfbf1;
  }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

/* Reset suave + base */
*, *::before, *::after { box-sizing: border-box; }

html { 
  font-size: 16px; 
  -webkit-text-size-adjust: 100%;
  scroll-behavior: smooth;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: 1.6;
  font-feature-settings: "kern", "liga", "calt";
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4, h5, h6 {
  margin: 0 0 var(--space-4);
  line-height: 1.25;
  font-weight: 600;
  letter-spacing: -0.011em;
}

h1 { font-size: var(--text-4xl); }
h2 { font-size: var(--text-2xl); margin-top: var(--space-10); }
h3 { font-size: var(--text-xl); margin-top: var(--space-6); }
h4 { font-size: var(--text-lg); }

p { margin: 0 0 var(--space-4); }

a {
  color: var(--accent);
  text-decoration: underline;
  text-underline-offset: 0.2em;
  text-decoration-thickness: 1px;
}
a:hover { text-decoration-thickness: 2px; }
a:focus-visible { outline: none; box-shadow: var(--shadow-focus); border-radius: var(--radius-sm); }

code {
  font-family: var(--font-mono);
  font-size: 0.9em;
  background: var(--bg-muted);
  padding: 0.125em 0.375em;
  border-radius: var(--radius-sm);
}

pre {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  background: var(--bg-muted);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  overflow-x: auto;
  line-height: 1.5;
}
pre code { background: transparent; padding: 0; }

table {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-4) 0;
}
th, td {
  text-align: left;
  padding: var(--space-3);
  border-bottom: 1px solid var(--border);
}
th {
  font-weight: 600;
  font-size: var(--text-sm);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

button {
  font-family: inherit;
  font-size: var(--text-sm);
  font-weight: 500;
  padding: var(--space-2) var(--space-4);
  background: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition);
}
button:hover { filter: brightness(1.08); }
button:focus-visible { outline: none; box-shadow: var(--shadow-focus); }
button:disabled { opacity: 0.5; cursor: not-allowed; }

input, textarea, select {
  font-family: inherit;
  font-size: var(--text-base);
  padding: var(--space-2) var(--space-3);
  background: var(--bg-elevated);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  transition: var(--transition);
}
input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: var(--shadow-focus);
}

/* Layout containers */
main {
  max-width: 72ch;
  margin: 0 auto;
  padding: var(--space-12) var(--space-6);
}

/* Para artefatos de dados / tabelas / dashboards, container mais largo: */
main.wide {
  max-width: 100ch;
}

main.full {
  max-width: 100%;
  padding: var(--space-8);
}
```

## Princípios derivados

### 1. Cor única de acento, não paleta

Se o projeto não tem cor de marca conhecida, **escolha uma** (teal, verde-floresta, bordô, mostarda — algo distinto de indigo). Use-a para link, botão primário, destaque. Tudo o resto é neutro.

### 2. Espaço em branco generoso

Padding 48px+ em containers grandes, line-height 1.6+ em texto de leitura. Texto comprimido é o segundo maior sinal de "default AI aesthetic".

### 3. Tipografia do sistema

Use `ui-sans-serif, system-ui` em vez de carregar fonte web. Renderiza nativo, é mais rápido, e fica visualmente coerente com o sistema do leitor.

### 4. Hierarquia por tamanho + peso, não por cor

H1 grande, H2 médio, H3 pequeno — todos na mesma cor. Não use roxo para H1 e azul para H2.

### 5. Sombra só funcional

Sombra para indicar elevação real (modal, dropdown, sticky header). Não para "deixar bonito".

### 6. Border-radius parcimonioso

`0.25rem` em inputs, `0.375rem` em cards/botões, `0.5rem` em containers grandes. Não use `1rem` em tudo — vira default AI look imediato.

### 7. Largura de leitura controlada

Para texto longo: `max-width: 72ch`. Texto que estica até 1920px de largura é ilegível.

### 8. Dark mode por preferência, não toggle gratuito

Suporte `prefers-color-scheme: dark` mas **não** adicione botão de toggle salvo se o conteúdo se beneficiar (ex: visualização de cor, demo de UI). Toggle de tema em status report é ruído.

## Quando desviar do baseline

O baseline existe para que **a estrutura** do conteúdo carregue a comunicação. Desvie quando:

- O projeto tem design system próprio (use-o)
- O conteúdo exige paleta específica (visualização de dados com cor categórica)
- O artefato é uma exploração visual deliberada (mockup com paleta proposta)
- O usuário pediu estilo específico ("faça com cara retrô", "estilo terminal")

Mas **nunca** desvie por "fica mais bonito assim" — isso é o caminho direto pro default AI aesthetic.

## Test rápido: este artefato parece "saída de LLM"?

Se a resposta a qualquer das perguntas abaixo for "sim", revise:

- [ ] Tem gradiente roxo-azul em algum lugar?
- [ ] Tem mais de 4 cores significativas?
- [ ] Cards têm sombra suave + border-radius grande + tudo igual?
- [ ] Tem emoji em headers?
- [ ] Header é um "hero" gigante com CTA button?
- [ ] Tem animação que aparece ao carregar?
- [ ] Tem `backdrop-filter: blur` em algum container?
- [ ] Font-weight default é 300 ou 400 em texto de leitura?
- [ ] Container principal estende-se a 100% sem max-width?
- [ ] Todos os botões têm a mesma cor brilhante de fundo?

Idealmente: zero checkmarks.
