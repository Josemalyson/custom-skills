# Relatório — Learning Trail Templates 6.0

## Decisão de experiência

O `TEMPLATE_ENHANCED.html` é a distribuição recomendada para publicação web. O `TEMPLATE_OFFLINE.html` é a distribuição de confiabilidade máxima. `TEMPLATE.html` aponta para a versão Enhanced para preservar compatibilidade com o workflow existente.

## Sistema de design aplicado

- arquitetura documental em três colunas: mapa / leitura / TOC;
- Inter para interface e Geist Mono para código;
- mint `#00d4a4` como acento semântico;
- superfícies planas, bordas hairline e raios moderados;
- hero atmosférico separado da área documental densa;
- dark mode, impressão, foco visível e reduced motion.

## Enhanced

Recursos são carregados apenas quando o seletor existe:

- `pre[data-language]` → Shiki 4.3.1;
- `.mermaid` → Mermaid 11.16.0;
- `[data-math]` e `[data-math-block]` → KaTeX 0.16.22;
- Inter e Geist Mono → Google Fonts.

A falha de qualquer CDN preserva o conteúdo original em texto/código.

## Offline

- nenhuma origem externa;
- sprite SVG embutido;
- fontes de sistema;
- código, diagramas e fórmulas permanecem legíveis como conteúdo bruto;
- todos os controles principais continuam locais.

## Validação estrutural

| Verificação | Offline | Enhanced |
|---|---:|---:|
| Placeholders semânticos | 23 | 23 |
| Contrato idêntico ao template-base | Sim | Sim |
| IDs duplicados | 0 | 0 |
| Links internos quebrados | 0 | 0 |
| Botões sem `type` | 0 | 0 |
| Scripts com erro de sintaxe | 0 | 0 |
| Origens externas | 0 | 4 |

A captura visual automatizada não foi concluída porque o Chromium do ambiente bloqueou navegação `file://` e `localhost` por política administrativa. A validação DOM, links, placeholders e sintaxe foi concluída.
