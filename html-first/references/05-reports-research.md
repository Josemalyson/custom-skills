# Reports & Research

Dois cenários, mesma família de problema: **texto longo que ninguém lê**. Tanto reports recorrentes (status semanal, post-mortem, incident review) quanto materiais educacionais (concept explainers, tutoriais) ganham massivamente em HTML porque podem usar estrutura navegável, chart inline, glossário hover, sections colapsáveis.

## Quando usar este padrão

- "Weekly status / status report / update"
- "Post-mortem / incident report / RCA"
- "Explica como X funciona" (em profundidade)
- "Tutorial / aprenda Y"
- "Documentação técnica para esse recurso"
- "Summary do trabalho da semana"

## Sub-padrão A: Status Report (semanal/sprint)

Formato curto, scanneável em 30 segundos por gente ocupada.

Estrutura mínima:

1. **Header**: nome do time, período, owner do report
2. **TL;DR** em 3-5 bullets — "What you need to know if you read nothing else"
3. **Shipped** — o que foi entregue, com link pro PR/feature
4. **In flight** — em andamento, com % e blockers se houver
5. **Slipped / at risk** — o que escorregou, por quê, plano de recuperação
6. **Metrics chart** — um único chart com a métrica que importa pro time (uptime, latency, signups, revenue, etc.)
7. **Mentions** — quem fez algo notável (humanos motivam)

**Anti-padrão**: status como Markdown bullet-list de 200 itens. Ninguém lê. Use chart pra a métrica e prosa curta pro contexto.

## Sub-padrão B: Post-mortem / Incident Report

Para incidente de produção. **Blameless**, focado em sistema, não em pessoa.

Estrutura obrigatória:

1. **One-liner**: "<service> ficou indisponível por <duração> em <data>, afetando <X% / N users>"
2. **Timeline visual** — barra horizontal com tempo, eventos marcados (detection, escalation, mitigation, resolution). Anotações nos pontos críticos.
3. **What happened** (factual, sem culpa)
4. **Why it happened** (causa raiz, idealmente 5 whys)
5. **Why our defenses failed** (alertas? circuit breakers? rollback automático? por que não pegaram?)
6. **Impact** quantitativo (requests perdidas, revenue, SLO budget consumido)
7. **What went well** (sim, sempre tem algo — destaque)
8. **Action items** — tabela com `ação | owner | prazo | status`. Sem ação sem owner.
9. **Lessons learned** — para o time, generalizável

## Sub-padrão C: Concept Explainer

Para ensinar algo conceitualmente. Pode incluir interatividade (concept toy) se ajudar.

Estrutura:

1. **TL;DR / "If you only read this..."** no topo
2. **Why this exists** — qual problema resolve
3. **The mental model** — diagrama ou ilustração SVG, idealmente interativo
4. **Walkthrough** — passo a passo com código real (tabs entre linguagens se aplicável)
5. **Comparison** — quando comparado a alternativas (tabela ou cards)
6. **Common pitfalls** — armadilhas que iniciantes encontram
7. **Glossary** com hover/tooltip para termos
8. **Further reading** — links para fontes primárias

## Sub-padrão D: Feature Deep-dive (interno)

Quando alguém pergunta "como funciona X no nosso sistema?" e você quer responder de uma vez por todas.

Estrutura:

1. **TL;DR box** colorido no topo
2. **Request path diagram** (SVG, do entry point ao response)
3. **Code snippets**, 3-5 dos pontos críticos, anotados
4. **Config knobs** — quais env vars, feature flags, configs afetam o comportamento
5. **Gotchas** — "Coisas que parecem bug mas são by design", "Comportamento contraintuitivo", "Quando isso quebra"
6. **Where to look in logs / dashboards** — para debug futuro
7. **Owner / contact** — quem manter

## Estrutura HTML — concept explainer

```html
<main>
  <header>
    <h1>Consistent Hashing</h1>
    <p class="subtitle">How to distribute keys across nodes without redistributing everything when a node joins or leaves.</p>
  </header>

  <aside class="tldr">
    <strong>TL;DR:</strong> Hash both keys and nodes onto the same ring. Each key goes to the next node clockwise. Adding/removing a node only moves keys between adjacent nodes.
  </aside>

  <nav class="toc">
    <a href="#why">Why</a>
    <a href="#model">The Ring</a>
    <a href="#walk">Walkthrough</a>
    <a href="#vs">vs Modulo Hashing</a>
    <a href="#pitfalls">Pitfalls</a>
    <a href="#glossary">Glossary</a>
  </nav>

  <section id="model">
    <h2>The Ring</h2>
    <p>Click any node to remove it. Click empty space to add one.</p>
    <div class="interactive-ring">
      <svg viewBox="0 0 400 400"><!-- ring com nodes e keys --></svg>
    </div>
  </section>

  <section id="walk">
    <h2>Walkthrough</h2>
    <div class="tabs">
      <button data-tab="js" class="active">JavaScript</button>
      <button data-tab="py">Python</button>
      <button data-tab="go">Go</button>
    </div>
    <pre class="tab-content active" id="tab-js"><code>...</code></pre>
    <pre class="tab-content" id="tab-py"><code>...</code></pre>
    <pre class="tab-content" id="tab-go"><code>...</code></pre>
  </section>

  <section id="glossary">
    <h2>Glossary</h2>
    <dl>
      <dt>Virtual node</dt>
      <dd>Replica of a real node hashed at multiple positions on the ring, to improve load distribution.</dd>
    </dl>
  </section>
</main>
```

## Estrutura HTML — incident timeline

```html
<main>
  <header>
    <h1>Incident #2026-052: Checkout 500s</h1>
    <dl class="meta">
      <dt>Duration</dt><dd>47 minutes</dd>
      <dt>Impact</dt><dd>~3,200 failed checkouts, ~$48k revenue lost</dd>
      <dt>Severity</dt><dd class="sev-2">SEV-2</dd>
      <dt>Detection</dt><dd>Alerted (Datadog), 4 min after start</dd>
    </dl>
  </header>

  <section class="timeline">
    <h2>Timeline</h2>
    <svg viewBox="0 0 1000 200">
      <!-- barra de tempo com marcadores -->
      <rect x="0" y="80" width="1000" height="40" fill="var(--c-track)"/>
      <g class="event" data-time="14:02">
        <circle cx="100" cy="100" r="6" fill="var(--c-detection)"/>
        <text x="100" y="70" text-anchor="middle">Detection</text>
      </g>
      <!-- ... -->
    </svg>
  </section>

  <section>
    <h2>Action Items</h2>
    <table>
      <thead><tr><th>Action</th><th>Owner</th><th>Due</th><th>Status</th></tr></thead>
      <tbody>
        <tr><td>Add circuit breaker on payment-svc → fraud-svc</td><td>@alice</td><td>2026-06-01</td><td>Open</td></tr>
        <!-- ... -->
      </tbody>
    </table>
  </section>
</main>
```

## Patterns para charts simples inline

Para um gráfico de status report ou métrica, **não puxe Chart.js**. Faça SVG manual — 30 linhas resolvem 90% dos casos:

```html
<svg viewBox="0 0 400 200" class="chart-line">
  <!-- eixos -->
  <line x1="40" y1="170" x2="380" y2="170" class="axis"/>
  <line x1="40" y1="20" x2="40" y2="170" class="axis"/>
  
  <!-- linha -->
  <polyline points="40,150 80,140 120,120 160,100 200,90 240,85 280,70 320,60 360,50" 
            class="series-line"/>
  
  <!-- pontos -->
  <circle cx="40" cy="150" r="3"/>
  <!-- ... -->
  
  <!-- labels -->
  <text x="40" y="190" class="x-label">Mon</text>
  <!-- ... -->
</svg>
```

Para chart mais complexo (multi-series, hover, zoom), aí compensa carregar uma lib leve (Chart.js, ApexCharts) via CDN.

## Prompts que disparam este padrão

> Write the platform team weekly status as a single HTML file. TL;DR in 4 bullets, shipped (4 PRs with links), in flight (3 items with % done), slipped (1 thing — explain), and one inline SVG chart showing API p95 latency over the past 7 days.

> Generate the post-mortem for incident <X>. Visual timeline with detection / escalation / mitigation / resolution marked. What happened, root cause (5 whys), why defenses didn't catch it, impact, what went well, action items table with owners and dates.

> Don't understand how our rate limiter works. Read <files>. Produce a single HTML explainer: TL;DR, request path diagram, the 3-4 key code snippets annotated, config knobs that affect behavior, gotchas section at the bottom.

## Armadilhas

- **Status report como wall of bullets** — humanos param de ler. Use prosa + 1-2 charts.
- **Post-mortem com tom de blame** — sistema, não pessoa. "The deploy was missing X" não "Alice forgot to add X".
- **Action items sem owner** — vira lista de desejos. Sempre owner + prazo + status.
- **Explainer sem TL;DR** — leitor que está aqui só pra ter ideia geral abandona. Sempre TL;DR no topo.
- **Glossário em página separada** — perde-se. Use `<dl>` no fim, ou `<dfn>` com hover na própria página.
- **Chart com 6 séries em 200px** — ilegível. Quebre em chart pequenos multiples (one chart per series).
