# Learning Trail Templates 6.0

## Escolha padrão

- **TEMPLATE_ENHANCED.html**: publicação web. É a experiência recomendada quando o aluno terá conexão.
- **TEMPLATE_OFFLINE.html**: distribuição, impressão, arquivamento, LMS restrito e abertura local.

Os dois arquivos compartilham a mesma estrutura HTML, os mesmos placeholders obrigatórios e os mesmos controles de progresso, busca, navegação e tema.

## Progressive enhancement

A versão Enhanced mantém o conteúdo funcional antes de qualquer download externo e carrega recursos somente quando encontra os seletores correspondentes:

| Conteúdo | Seletor | Recurso |
|---|---|---|
| Código | `pre[data-language]` | Shiki 4.3.1 |
| Diagramas | `.mermaid` | Mermaid 11.16.0 |
| Fórmula inline | `[data-math]` | KaTeX 0.16.22 |
| Fórmula em bloco | `[data-math-block]` | KaTeX 0.16.22 |

Inter e Geist Mono são carregadas pelo Google Fonts. Se a rede falhar, as fontes de sistema e os blocos textuais preservam a leitura.

## Compatibilidade

O conjunto de placeholders da versão anterior foi preservado. Os blocos ricos são opcionais e documentados por comentários dentro de cada template.

## Princípios de DESIGN.md aplicados

- layout documental em três colunas;
- Inter para interface e Geist Mono para código;
- mint como acento semântico, não decorativo;
- superfícies planas, hairlines e raios moderados;
- hero atmosférico e conteúdo principal denso;
- prioridade para leitura longa, teclado, impressão e reduced motion.
