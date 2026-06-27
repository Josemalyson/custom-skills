# Decks

Um deck de slides é literalmente um conjunto de `<section>` + ~20 linhas de JS para arrow-key navigation. Não precisa de Keynote, PowerPoint, reveal.js, nada. Aponte o agente para um Slack thread ou um design doc e peça um deck navegável que você abre direto no browser — depois compartilha o `.html` por link.

## Quando usar este padrão

- "Faz um deck sobre X"
- "Apresentação para a reunião de Y"
- "Slides para o all-hands"
- "Lightning talk em 5 minutos"

## Quando NÃO usar (use o sub-padrão correspondente)

- Long form content que vai ser lido (não apresentado) → use `references/05-reports-research.md`
- Comparação lado-a-lado densa → use `references/01-exploration-planning.md`
- Tutorial passo-a-passo → use concept explainer em vez de deck

## Princípios

### 1. Um slide = uma ideia

Se um slide tem ≥3 ideias diferentes, ele vira dois slides. Density alta funciona em report, **falha em deck**.

### 2. Texto curto, visual maior

Não escreva parágrafos no slide. Escreva o título-ideia e, se necessário, 3-5 bullets de no máximo uma linha cada. Se precisa mais texto, é speaker note (ver abaixo).

### 3. Speaker notes embutidas, escondidas

Use `<details>` por slide, com display none por default e atalho de teclado pra mostrar (ex: tecla `s`). Permite o apresentador ter cola sem expor pro público.

### 4. Arrow-key navigation, mais nada

Esquerda / direita para navegar. `f` para fullscreen. `Esc` para sair de fullscreen. Não invente atalhos exóticos.

### 5. Cada slide é uma URL

`#1`, `#2`, etc. Permite linkar slide específico em mensagens. Sempre.

### 6. Print-friendly como fallback

`@media print { section { page-break-after: always; } }` — assim "Print to PDF" do browser gera deck PDF distribuível.

## Estrutura HTML

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>O caso para HTML > Markdown</title>
  <style>
    body { margin: 0; font-family: ui-sans-serif, system-ui, sans-serif; background: #0d0f12; color: #e6e8ea; }
    section.slide { width: 100vw; height: 100vh; padding: 6vh 8vw; box-sizing: border-box; display: none; flex-direction: column; justify-content: center; }
    section.slide.active { display: flex; }
    h1 { font-size: clamp(2rem, 5vw, 4rem); margin: 0 0 0.5em; }
    h2 { font-size: clamp(1.5rem, 3vw, 2rem); opacity: 0.8; margin: 0 0 1em; font-weight: normal; }
    ul { font-size: clamp(1rem, 1.6vw, 1.5rem); line-height: 1.8; }
    .notes { display: none; position: fixed; bottom: 1em; left: 1em; right: 1em; background: rgba(0,0,0,0.85); padding: 1em; font-size: 0.9rem; border-radius: 6px; }
    .notes.show { display: block; }
    nav.indicator { position: fixed; bottom: 1em; right: 1em; font-size: 0.85rem; opacity: 0.5; }
    @media print {
      section.slide { display: flex !important; page-break-after: always; }
      .notes, nav.indicator { display: none !important; }
    }
  </style>
</head>
<body>

<section class="slide" data-i="1">
  <h1>HTML é o novo Markdown</h1>
  <h2>Por que mudar o default em planos longos</h2>
  <details class="notes"><summary>Notes</summary>
    Abrir com a tese central. Mencionar que Markdown ainda tem lugar — não é "HTML sempre".
  </details>
</section>

<section class="slide" data-i="2">
  <h1>O problema</h1>
  <ul>
    <li>Planos passaram de 100 linhas</li>
    <li>Humano para de ler</li>
    <li>Colaboração quebra silenciosamente</li>
  </ul>
</section>

<!-- ... -->

<nav class="indicator"><span id="cur">1</span> / <span id="total">10</span></nav>

<script>
  const slides = document.querySelectorAll('.slide');
  let i = 0;
  document.getElementById('total').textContent = slides.length;
  
  const show = (n) => {
    i = (n + slides.length) % slides.length;
    slides.forEach((s, idx) => s.classList.toggle('active', idx === i));
    document.getElementById('cur').textContent = i + 1;
    history.replaceState(null, '', '#' + (i + 1));
  };
  
  const init = () => {
    const h = parseInt(location.hash.slice(1), 10) - 1;
    show(Number.isFinite(h) && h >= 0 ? h : 0);
  };
  
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ') show(i + 1);
    else if (e.key === 'ArrowLeft') show(i - 1);
    else if (e.key === 'f') document.documentElement.requestFullscreen();
    else if (e.key === 's') document.querySelectorAll('.notes').forEach(n => n.classList.toggle('show'));
  });
  
  window.addEventListener('hashchange', init);
  init();
</script>
</body>
</html>
```

## Slide types — biblioteca curta

### Title slide
Título grande, subtítulo, autor/data pequeno no canto.

### Section divider
Apenas o nome da seção, em fonte enorme, fundo de cor distinta. Marca transição entre blocos do deck.

### Bullet slide
3-5 bullets, no máximo uma linha cada.

### Quote slide
Citação grande, atribuição pequena. Use para abrir/fechar seção com força.

### Diagram slide
Um SVG grande centralizado, mínimo de texto. Diagrama explica, palavra só ancora.

### Comparison slide
2 ou 3 colunas. Headers iguais, conteúdo diferente. Use sparingly — se for ≥4 colunas, vira tabela em outro formato.

### Demo / code slide
Snippet de código, fonte mono grande, syntax highlighting básico. **Não cole 50 linhas** — só o trecho que faz sentido no contexto da fala.

### Q&A / closing
Endereço/contato, GitHub, próximos passos.

## Prompts que disparam este padrão

> Make a short deck (8-12 slides) on the case for HTML over Markdown when working with AI agents. Single HTML file with arrow-key navigation. Each slide is one idea max. Include speaker notes hidden behind the `s` key. Title slide, problem framing, 4-5 examples (one per slide), and a "try it" call-to-action at the end.

> Turn this Slack thread into a 6-slide lightning talk. Pull the key points, structure them as: title → problem → 3 examples → action items → closing. Single `.html`, arrow keys to navigate.

> Convert this RFC document into a slide deck for the design review. Group sections by slide. Each slide: section title + 3-4 bullets of the main idea. Move the long prose into speaker notes (toggle with `s`). 15 slides max.

## Armadilhas

- **Slides com 200 palavras** — vira documento, não deck. Speaker notes existem por isso.
- **Animação CSS gratuita** — fade-in em tudo cansa rápido. Use animação só onde reforça (revelar conceito gradualmente).
- **Cor que muda a cada slide** — dispersa atenção. Mantenha paleta consistente, varie tipo/layout.
- **Sem indicator de progresso** — apresentador e público perdem ritmo. Sempre `1 / N` em canto discreto.
- **Sem fallback de print** — alguém vai querer PDF. `@media print` resolve em 5 linhas.
