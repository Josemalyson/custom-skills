# Diagrams & SVG

SVG inline dá ao agente uma **caneta de verdade**. Para qualquer pedido de diagrama — fluxograma, arquitetura, sequence, deploy topology, RAG flow — o output sai como SVG editável **dentro** do HTML, não como imagem que ninguém consegue tocar.

## Quando usar este padrão

- "Diagrama de X" / "Fluxograma de Y"
- "Arquitetura do sistema" / "Topologia"
- "Sequence diagram da requisição Z"
- "Como funciona o RAG" / "Fluxo do agente"
- "Pipeline de deploy" / "CI/CD flow"
- "Como o request flui de A até B"

## Por que SVG inline, não Mermaid

Mermaid é boa para diagrama de placeholder, **ruim para artefato final**: layout automático estoura, controle de estilo é limitado, hover/click annotations exigem hack. Para um artefato que vai ser **lido com atenção e compartilhado**, SVG manual ganha.

Use Mermaid quando: prototipagem rápida dentro de markdown, diagrama vai mudar de forma constantemente, ninguém vai estilizar.

Use SVG inline quando: artefato final, precisa de cor com significado, precisa de hover annotations, precisa estar mobile-responsive.

## Princípios para SVG inline

### 1. ViewBox, não width/height fixos

```html
<svg viewBox="0 0 1000 600" preserveAspectRatio="xMidYMid meet">
  <!-- ... -->
</svg>
```

E no CSS: `svg { width: 100%; height: auto; }` — assim escala em qualquer tela.

### 2. `<g>` com classes semânticas, não estilo inline

```html
<g class="node service" data-name="auth-service">
  <rect class="node-bg" x="0" y="0" width="120" height="60" rx="6"/>
  <text class="node-label" x="60" y="35">auth</text>
</g>
```

Estiliza no `<style>`. Permite hover, theme dark/light, mudança rápida.

### 3. Setas de verdade

Use `<marker>` para flechas, `<path>` para curvas (não `<line>` para tudo):

```html
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"/>
  </marker>
</defs>
<path d="M 100 50 Q 200 50 200 100" stroke="currentColor" fill="none" marker-end="url(#arrow)"/>
```

### 4. Hover / click annotations

```html
<g class="node" tabindex="0" onclick="document.querySelector('#desc-auth').scrollIntoView()">
  <title>auth-service — JWT issuance and validation</title>
  <!-- ... -->
</g>
```

`<title>` dá tooltip nativo. `onclick` permite navegação. `tabindex="0"` permite acessibilidade por teclado.

### 5. Cor com significado, não decoração

Defina um sistema de cor no início do SVG e mantenha consistente:

- **Layer de infra** (compute, network) — neutros frios
- **Layer de dados** (db, cache, queue) — neutros quentes
- **External / 3rd party** — diferenciado
- **Hot path** — cor de destaque única
- **Failure / error** — vermelho saturado, **só** quando algo está errado

Não use 7 cores diferentes só porque pode. Diagrama bom usa ≤4 cores significativas.

## Sub-padrões

### A. Sequence diagram

Para fluxos de requisição entre serviços, especialmente útil em arquitetura distribuída.

Estrutura: lanes verticais (uma por serviço), tempo desce, mensagens são setas horizontais entre lanes. Cada mensagem tem label. Ativações são retângulos finos sobre a lane.

```html
<svg viewBox="0 0 800 600">
  <!-- Lanes -->
  <g class="lanes">
    <line x1="100" y1="40" x2="100" y2="560" class="lane"/>
    <text x="100" y="30" text-anchor="middle">Client</text>
    
    <line x1="300" y1="40" x2="300" y2="560" class="lane"/>
    <text x="300" y="30" text-anchor="middle">Gateway</text>
    
    <line x1="500" y1="40" x2="500" y2="560" class="lane"/>
    <text x="500" y="30" text-anchor="middle">Auth Service</text>
    
    <line x1="700" y1="40" x2="700" y2="560" class="lane"/>
    <text x="700" y="30" text-anchor="middle">Token Store</text>
  </g>
  
  <!-- Messages -->
  <g class="messages">
    <line x1="100" y1="80" x2="300" y2="80" marker-end="url(#arrow)"/>
    <text x="200" y="75" text-anchor="middle">POST /login</text>
    <!-- ... -->
  </g>
</svg>
```

### B. C4-style component diagram

Boxes para serviços, arrows para dependências, anotação na arrow para o tipo de chamada (HTTP, gRPC, async event).

Convenção:
- **Person / external system** — formato distinto (ícone humano simples, ou retângulo tracejado)
- **System boundary** — retângulo grande agrupando os componentes internos
- **Container** — retângulo arredondado com tech inline (`API [Node.js]`)

### C. Deploy topology (K8s/Cloud)

Para visualizar pods, namespaces, nodes, services, ingress.

Sugestão: **agrupar visualmente** por nível de containment (cloud → region → AZ → cluster → namespace → pod). Setas para indicar tráfego (cliente → ingress → service → pod).

### D. Pipeline de CI/CD

Etapas em sequência horizontal, cada uma com:
- Nome
- Duração típica
- O que roda
- Onde quebrou no histórico recente (em vermelho, link pro log)

### E. RAG / Agent flow (GenAI)

Para visualizar pipelines de LLM:

- **User query** → **Embedding** → **Vector search** → **Re-ranking** → **Context assembly** → **Prompt build** → **LLM call** → **Output parsing** → **Tool call?** → **Response**

Cada etapa tem latência típica, custo, e modo de falha. Para agents: loop de tool calls deve ficar visualmente óbvio (seta voltando ao "LLM call").

### F. Annotated flowchart (com path de falha)

Não só o happy path. **Toda decisão importante** tem branch de erro/edge case, em cor distinta. Click em qualquer step abre `<details>` com o que acontece especificamente naquele step (timing, logs, código).

## Prompts que disparam este padrão

> Generate an architecture diagram for <system> as a single HTML file. Use inline SVG (not Mermaid). C4 level 2: containers grouped by system boundary. Color by layer (compute = cool gray, data = warm gray, external = blue). Add hover tooltips with the tech and purpose of each container. End with a description list mapping each container to its repo / responsibility.

> Draw the sequence diagram for the <X> request lifecycle, from client to database and back. Inline SVG, lanes vertical, time goes down. Each message labeled with payload shape. Annotate latency contributions per step. Add a "failure paths" section below with the same lanes but red arrows for the timeout / 500 case.

> Visualize our RAG pipeline as an inline SVG flowchart. Steps: query → embed → vector search → rerank → context assembly → LLM → parse → respond. For each step: typical latency, cost (USD per 1k calls), and the failure modes. Make the loop for tool calls visible if applicable.

## Patterns para diagramas grandes

Se o diagrama tem mais de ~30 nodes, ele provavelmente está fazendo coisa demais. Opções:

1. **Quebre em múltiplos diagramas** — overview no topo, drill-down em `<details>` por sub-sistema
2. **Use camadas** — toggle de "mostrar apenas layer X" via JS leve
3. **Use viewBox grande + zoom CSS** — `<svg>` em container com `overflow: auto`
4. **Foque no hot path** — desabilite (opacidade 0.3) o que não é o caminho principal

## Armadilhas

- **Cores random** — três tons de azul que não significam nada. Defina sistema antes.
- **Layout automático sem revisão** — se for usar Mermaid ou similar, ainda assim revise visualmente. Sobreposição de labels é comum.
- **Sem fallback responsivo** — em mobile, diagrama complexo precisa de pan/zoom ou versão "lista" alternativa.
- **Texto curto demais nos boxes** — `auth` em vez de `auth-service` é apertado pra usuário externo entender. Use o nome completo.
- **Falta de legend** — se você tem 4 cores significativas, defina-as em uma legend no canto.
