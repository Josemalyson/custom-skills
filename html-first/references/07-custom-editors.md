# Custom Editors

O sub-padrão mais subestimado da abordagem HTML-first: **micro-apps descartáveis** para editar uma estrutura específica. Em vez de discutir com o agente em texto sobre como reordenar 30 itens, peça uma UI drag-and-drop que termina em "copy as JSON / Markdown" e cole o resultado de volta no próximo prompt.

> *"It's like this is not even personal software. This is like sub... it's like micro-software on top of micro-software."* — Thariq Shihipar

## Quando usar este padrão

- "Preciso reorganizar / repriorizar / triar essa lista"
- "Quero editar essas regras / config / flags"
- "Anota esse documento / transcript / diff"
- "Curadoria de dataset — aprovar / rejeitar / taggear"
- "Tunar valores difíceis de descrever em texto" (cores, easing, regex, cron, dimensões)
- "Comparar versões e escolher pedaços de cada"
- "Tuning de prompt com preview ao vivo"

## A invariável crítica: round-trip

**Toda micro-app desta categoria termina em exportação.** Sem botão "Copy as JSON" ou "Copy as Markdown" ou "Download diff", a UI é beco sem saída — o usuário interagiu, mas não pode reinjetar o resultado no fluxo do agente.

O loop completo:

```
Agent gera UI ─► Humano edita visualmente ─► Exporta (JSON/MD)
                                                  │
                              ◄───────────────────┘
                          (cola no próximo prompt)
```

Se a sua micro-app não fecha esse loop, ela está incompleta.

## Princípios

### 1. Disposable, não product

Esta UI **não é software de verdade**. Não vai ter usuários. Não precisa de tela de login, settings, dark mode toggle, internacionalização, error boundaries chiques. Foque no fluxo único pelo qual o usuário vai passar **uma vez**.

### 2. Pre-populate com best guess

Não entregue UI vazia esperando o usuário começar do zero. **Pré-popule** com a melhor estimativa que você (agente) consegue fazer dos dados. O usuário ajusta, não cria.

### 3. Estado em memória, exportável

Todo estado vive em variáveis JS / `useState` durante a sessão. Não use `localStorage` salvo se o usuário pedir explicitamente. O ponto é exportar e seguir, não persistir.

### 4. Um propósito por arquivo

Não tente fazer uma única HTML que faz triagem **e** edição de flags **e** annotação. Faça três `.html` se necessário. Disposable é barato.

### 5. Validate as constraints, warn don't block

Se o domínio tem regras (ex: "flag B só pode estar ON se flag A estiver ON"), mostre o aviso destacado mas **não bloqueie**. O usuário sabe o que está fazendo.

## Sub-padrões

### A. Triage / prioritization board

Drag-and-drop entre colunas (Now / Next / Later / Cut, ou Approve / Reject, ou MVP / V2 / Backlog).

Componentes:
- Cards com nome, descrição curta, badge de tipo/severity
- Colunas com count
- Pre-populated baseado no best guess do agente
- Export: "Copy as Markdown" gerando lista por coluna com rationale opcional

### B. Form-based config editor

Para feature flags, env vars, JSON/YAML com constraints.

Componentes:
- Toggles, dropdowns, number inputs por valor
- Agrupamento visual por área
- Dependency warnings inline (em amarelo, não bloqueante)
- Diff view: o que mudou em relação ao input original
- Export: "Copy diff" — só as chaves alteradas

### C. Prompt / template tuner

Editor de prompt à esquerda, preview ao vivo com sample inputs à direita.

Componentes:
- Textarea grande com syntax highlighting básico para variáveis `{var_name}`
- 2-3 sample inputs editáveis
- Re-render automático quando o template muda
- Token/character counter
- Export: "Copy prompt"

### D. Dataset curation

Aprovar / rejeitar / taggear rows de um dataset.

Componentes:
- Tabela ou cards stack, um item por vez
- Botões: Approve / Reject / Skip + custom tags
- Keyboard shortcuts (`a` / `r` / `s`)
- Progress bar (X de Y)
- Export: "Copy selected as JSONL" ou "Download .csv"

### E. Annotation tool

Highlight + comment em documento, transcript, ou diff.

Componentes:
- Texto à esquerda, painel de anotações à direita
- Click-and-drag para selecionar trecho
- Comment inline ancorado ao range
- Severity ou tag por anotação
- Export: "Copy annotations as JSON" com `{ start, end, text, comment, tag }`

### F. Value picker (não-textual)

Para valores que **dói descrever em texto**: cor, easing curve, crop region, cron schedule, regex.

Componentes específicos por tipo:
- **Color**: HSL sliders + hex + alpha + preview em backgrounds claro/escuro
- **Easing**: `<input type="text">` com cubic-bezier + visual da curva + preview animado
- **Cron**: dropdowns por unidade + preview de "next 5 executions"
- **Regex**: textarea + sample text com matches destacados em real-time
- **Crop**: imagem + handles arrastáveis

Export sempre: "Copy <value>" para clipboard.

## Estrutura HTML — triage board

```html
<main class="board">
  <header>
    <h1>Triage: 30 tickets → Now / Next / Later / Cut</h1>
    <button id="export">Copy as Markdown</button>
  </header>

  <section class="columns">
    <article class="column" data-bucket="now">
      <h2>Now <span class="count">0</span></h2>
      <div class="cards" data-droppable></div>
    </article>
    <article class="column" data-bucket="next">
      <h2>Next <span class="count">0</span></h2>
      <div class="cards" data-droppable></div>
    </article>
    <article class="column" data-bucket="later">
      <h2>Later <span class="count">0</span></h2>
      <div class="cards" data-droppable></div>
    </article>
    <article class="column" data-bucket="cut">
      <h2>Cut <span class="count">0</span></h2>
      <div class="cards" data-droppable></div>
    </article>
  </section>

  <template id="card-tpl">
    <div class="card" draggable="true">
      <div class="card-id"></div>
      <div class="card-title"></div>
      <div class="card-meta"></div>
      <textarea placeholder="Rationale (optional)"></textarea>
    </div>
  </template>

  <script>
    // Pre-populated data, best-guess bucket
    const tickets = [
      { id: 'TKT-1', title: 'Fix auth token leak', meta: 'P0 / security', bucket: 'now' },
      { id: 'TKT-2', title: 'Refactor billing module', meta: 'P2 / tech-debt', bucket: 'later' },
      // ... 28 more
    ];

    const render = () => {
      document.querySelectorAll('[data-droppable]').forEach(d => d.innerHTML = '');
      tickets.forEach(t => {
        const node = document.getElementById('card-tpl').content.cloneNode(true);
        node.querySelector('.card-id').textContent = t.id;
        node.querySelector('.card-title').textContent = t.title;
        node.querySelector('.card-meta').textContent = t.meta;
        const card = node.querySelector('.card');
        card.dataset.id = t.id;
        document.querySelector(`[data-bucket="${t.bucket}"] [data-droppable]`).appendChild(node);
      });
      updateCounts();
    };

    const updateCounts = () => {
      document.querySelectorAll('.column').forEach(c => {
        c.querySelector('.count').textContent = c.querySelectorAll('.card').length;
      });
    };

    // Drag-and-drop (HTML5 native)
    document.addEventListener('dragstart', e => {
      if (e.target.classList.contains('card')) {
        e.dataTransfer.setData('text/plain', e.target.dataset.id);
      }
    });
    document.querySelectorAll('[data-droppable]').forEach(zone => {
      zone.addEventListener('dragover', e => e.preventDefault());
      zone.addEventListener('drop', e => {
        e.preventDefault();
        const id = e.dataTransfer.getData('text/plain');
        const card = document.querySelector(`.card[data-id="${id}"]`);
        const bucket = e.currentTarget.closest('.column').dataset.bucket;
        e.currentTarget.appendChild(card);
        const t = tickets.find(t => t.id === id);
        if (t) t.bucket = bucket;
        updateCounts();
      });
    });

    document.getElementById('export').addEventListener('click', async () => {
      const buckets = ['now', 'next', 'later', 'cut'];
      const labels = { now: 'Now', next: 'Next', later: 'Later', cut: 'Cut' };
      let md = '';
      buckets.forEach(b => {
        const cards = [...document.querySelectorAll(`[data-bucket="${b}"] .card`)];
        if (cards.length === 0) return;
        md += `## ${labels[b]}\n\n`;
        cards.forEach(c => {
          const rationale = c.querySelector('textarea').value.trim();
          md += `- **${c.dataset.id}** — ${c.querySelector('.card-title').textContent}`;
          if (rationale) md += ` _(${rationale})_`;
          md += '\n';
        });
        md += '\n';
      });
      await navigator.clipboard.writeText(md);
      const btn = document.getElementById('export');
      const orig = btn.textContent;
      btn.textContent = 'Copied!';
      setTimeout(() => btn.textContent = orig, 1500);
    });

    render();
  </script>
</main>
```

## Estrutura HTML — prompt tuner com live preview

```html
<main class="tuner">
  <section class="editor">
    <label>Template</label>
    <textarea id="tpl">You are {role}. Answer about {topic} in {style} style.</textarea>
    <small id="tcount">0 chars · ~0 tokens</small>
  </section>

  <section class="samples">
    <h2>Sample inputs</h2>
    <div class="sample">
      <label>role</label><input data-var="role" value="a senior SRE">
      <label>topic</label><input data-var="topic" value="incident postmortems">
      <label>style</label><input data-var="style" value="terse, blameless">
    </div>
    <h3>Filled</h3>
    <pre id="filled"></pre>
  </section>

  <button id="copy-tpl">Copy template</button>

  <script>
    const tpl = document.getElementById('tpl');
    const filled = document.getElementById('filled');
    const inputs = document.querySelectorAll('[data-var]');
    const tcount = document.getElementById('tcount');

    const render = () => {
      const vars = {};
      inputs.forEach(i => vars[i.dataset.var] = i.value);
      let out = tpl.value;
      Object.entries(vars).forEach(([k, v]) => {
        out = out.replaceAll(`{${k}}`, v);
      });
      filled.textContent = out;
      const chars = tpl.value.length;
      tcount.textContent = `${chars} chars · ~${Math.ceil(chars / 4)} tokens`;
    };

    [tpl, ...inputs].forEach(el => el.addEventListener('input', render));
    document.getElementById('copy-tpl').addEventListener('click', () => navigator.clipboard.writeText(tpl.value));
    render();
  </script>
</main>
```

## Prompts que disparam este padrão

> I need to reprioritize these 30 Linear tickets. Make me an HTML file with each ticket as a draggable card across Now / Next / Later / Cut columns. Pre-sort them by your best guess based on labels. Add a "copy as Markdown" button that exports the final ordering with a one-line rationale per bucket. Keyboard shortcut for "approve current bucket".

> Here's our feature flag config. Build a form-based editor for it: group flags by area, show dependencies between them, warn me (don't block) if I enable a flag whose prerequisite is off. Add a "copy diff" button that exports just the changed keys.

> I'm tuning this system prompt. Make a side-by-side editor: editable prompt on the left with variable slots `{var}` highlighted, three sample inputs on the right that re-render the filled template live. Add a character/token counter and a copy button.

> Build me a regex tester. Textarea for the pattern, textarea for sample text, highlights matches in real-time with capture groups colored. Show count of matches. Export: "copy as JS regex" or "copy as Python re".

## Armadilhas

- **Esquecer o export** — UI sem export é loop quebrado. Trate como bug crítico.
- **Sem pre-populate** — UI vazia desincentiva uso. Sempre best-guess.
- **Validação como bloqueio** — `disabled` em botões quando "regra X foi violada". Avise, não impeça.
- **Tentar reuso** — esta UI vai ser usada uma vez. Não generalize. Não componentize. Não adicione configurações.
- **Drag-and-drop sem keyboard fallback** — acessibilidade. Sempre permita mover via teclado também (arrow keys + space).
- **Clipboard API sem fallback** — `navigator.clipboard.writeText` falha em `file://` em alguns browsers. Tenha fallback com `<textarea>` invisível + `document.execCommand('copy')`.
