# Exploration & Planning

Para quando o usuário ainda não sabe o que quer (exploration) ou já sabe e precisa de um plano executável (planning). Em ambos os casos, HTML vence Markdown porque o humano consegue **comparar visualmente** opções e **navegar** o plano sem rolar 1000 linhas.

## Quando usar este padrão

- "Compare X abordagens para Y"
- "Quero brainstorm de 5-6 ideias diferentes"
- "Crie um plano de implementação para Z"
- "Spec / design doc para a feature W"
- "Não sei qual direção tomar, me mostra opções"

## Princípios

### Para exploration (múltiplas opções)

- **3-6 opções é o sweet spot** — menos não compensa o esforço de comparar, mais cansa
- **Variar nos eixos certos**: layout, abordagem técnica, trade-off (não só cor)
- **Trade-off explícito por opção**: cada card termina com "Por que escolher esta" e "Por que não"
- **Lado-a-lado, não em pilha** — usar CSS Grid `repeat(auto-fit, minmax(280px, 1fr))`
- **Label visível em cada opção** com qual trade-off ela está fazendo

### Para planning (plano executável)

Um plano de implementação que vale o nome contém **obrigatoriamente**:

1. **TL;DR** no topo (3-5 bullets, o que vai mudar e por quê)
2. **Timeline visual** — milestones em barra ou Gantt simples (SVG ou CSS)
3. **Data flow / arquitetura** — diagrama, não prosa
4. **Mockups inline** — pelo menos sketch das telas/interfaces afetadas
5. **Code excerpts** — os trechos críticos, comentados
6. **Risk table** — risco | probabilidade | mitigação
7. **Definition of Done** — o que tem que estar verdadeiro pra fechar
8. **Open questions** — o que falta decidir, com você ou com o time

Se algum dos 8 não couber, é porque o plano está incompleto, não porque "não precisa".

## Estrutura HTML recomendada

### Exploration (comparação lado-a-lado)

```html
<main>
  <header>
    <h1>Comparação: 4 abordagens para X</h1>
    <p>Critérios: complexidade de implementação, latência, custo de operação.</p>
  </header>

  <section class="grid grid-cols-auto">
    <article class="option">
      <h2>Opção 1: <span class="approach">Approach A</span></h2>
      <div class="diagram"><!-- SVG inline --></div>
      <h3>Trade-off</h3>
      <p>Otimiza por <strong>X</strong>, sacrifica <strong>Y</strong>.</p>
      <h3>Quando escolher</h3>
      <ul><li>...</li></ul>
      <h3>Quando não escolher</h3>
      <ul><li>...</li></ul>
      <details><summary>Code sketch</summary><pre><code>...</code></pre></details>
    </article>
    <!-- repetir para opções 2, 3, 4 -->
  </section>

  <aside class="recommendation">
    <h2>Recomendação</h2>
    <p>Para o contexto descrito, <strong>Opção 2</strong> porque...</p>
  </aside>
</main>
```

### Planning (plano executável)

```html
<main>
  <header>
    <h1>Plano de Implementação: Feature W</h1>
    <nav class="toc">
      <a href="#tldr">TL;DR</a>
      <a href="#timeline">Timeline</a>
      <a href="#arch">Arquitetura</a>
      <a href="#mockups">Mockups</a>
      <a href="#code">Code</a>
      <a href="#risks">Riscos</a>
      <a href="#dod">Definition of Done</a>
      <a href="#questions">Open Questions</a>
    </nav>
  </header>

  <section id="tldr"><h2>TL;DR</h2><ul>...</ul></section>
  <section id="timeline"><h2>Timeline</h2><!-- SVG Gantt --></section>
  <section id="arch"><h2>Arquitetura</h2><!-- SVG diagram --></section>
  <section id="mockups"><h2>Mockups</h2><!-- inline SVG ou HTML mock --></section>
  <section id="code"><h2>Code excerpts</h2><pre><code>...</code></pre></section>
  <section id="risks">
    <h2>Riscos</h2>
    <table>
      <thead><tr><th>Risco</th><th>Prob.</th><th>Impacto</th><th>Mitigação</th></tr></thead>
      <tbody><tr>...</tr></tbody>
    </table>
  </section>
  <section id="dod"><h2>Definition of Done</h2><ul>...</ul></section>
  <section id="questions"><h2>Open Questions</h2><ol>...</ol></section>
</main>
```

## Prompt patterns que disparam este padrão

Use estas formulações ao perguntar ao agente (ou quando esta skill é invocada, gere algo equivalente):

> Generate 4 distinctly different approaches to <problem>. Vary on architecture, complexity, and trade-off — not aesthetics. Lay them out as a single HTML file in a grid I can scan. Each card: 1-line tagline, inline diagram, "when to pick", "when not to pick", and a code sketch in `<details>`. End with your recommendation in an `<aside>` and the rationale.

> Create a thorough implementation plan in a single HTML file. Include TL;DR, milestones on a visual timeline, an inline architecture diagram, at least two UI mockups (sketch fidelity is fine), code excerpts for the risky parts, a risk table, a definition of done, and a list of open questions. Make it scannable in 60 seconds.

## Patterns específicos para arquitetura distribuída / Cloud

Quando o plano envolve sistema distribuído, K8s, multi-region, ou similar:

- **Sequence diagram** para fluxos de requisição (SVG com lanes)
- **Component diagram** (C4 nível 2/3) — boxes representando services
- **Deploy topology** — node, namespace, pod (use cores consistentes para indicar layer)
- **Blast radius** explícito — "se X cair, o que para?"
- **Cost note** por componente quando relevante (especialmente em AWS)

## Patterns específicos para GenAI / LLM features

Quando o plano envolve LLMs, RAG, agents:

- **Sequence diagram** com tokens flow (user → retrieval → prompt → model → parsing → output)
- **Prompt structure visual** — mostra system / user / tools / context boundaries
- **Eval matrix** — métrica × baseline × proposta
- **Latency budget breakdown** — onde o tempo é gasto
- **Cost per call** estimado, com sensibilidade a context length

## Armadilhas comuns

- **Cards iguais** — se todas as opções parecem iguais visualmente, a comparação não está fazendo seu trabalho. Diferencie tipograficamente as ênfases de cada opção.
- **Plano sem mockup** — humano não consegue revisar o que vai ser construído sem ver. Mesmo sketch ruim é melhor que nada.
- **Risk table vazia ou de uma linha** — sinal de que o autor não pensou nos modos de falha. Sempre 3+ linhas; se não conseguir, peça mais contexto antes.
- **Open Questions ocultas** — se houver dúvida real, declare-a em lugar visível. Plano que finge não ter dúvidas é plano frágil.
