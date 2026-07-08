# learning-trail

Skill para geracao de trilhas de aprendizado no padrao **spine + nerves** com validacao atomica de recursos e cobertura multimodal: leitura, video, audio/podcast, pratica, livros e comunidade recente.

## O que faz

Dado um assunto qualquer, gera um JSON canonico (`trail.json`) e um HTML autocontido (`index.html`) estruturados como:
- **Coluna vertebral**: estacoes sequenciais de conhecimento (5-10 min cada)
- **Nervos multimodais**: recursos externos validados por conteudo (links que o agente leu, transcreveu, ouviu via transcript/show notes ou inspecionou antes de recomendar)
- **Entregas praticas**: tutorial, lab, exercicio, checklist ou mini-projeto para fixar cada estacao
- **Boss final**: 5 perguntas socraticas de validacao
- **Progresso local**: tracking por estacao via `localStorage`, sem backend

## Instalacao

### Claude Code (CLI)
```bash
# Copie a pasta para o diretorio de skills do Claude Code
cp -r learning-trail ~/.claude/skills/

# Ou instale via .skill bundle
claude skill install learning-trail.skill
```

### Harness customizado
```bash
# Coloque a pasta no diretorio de skills do seu harness
cp -r learning-trail /caminho/do/seu/harness/skills/
```

## Como usar

Apos instalado, acione a skill com qualquer um destes padroes:

**PT-BR:**
```
quero aprender Kubernetes
me ensina o que e RAG
gera trilha de Service Mesh
estudar Terraform
```

**EN:**
```
teach me about transformers
learn kubernetes
generate roadmap for event sourcing
```

## Output

A skill gera uma pasta por assunto em `./trilhas/{slug}/`:

| Arquivo | Descricao |
|---------|-----------|
| `index.html` | HTML autocontido com CSS/JS embutidos, JSON integrado e progresso local |
| `trail.json` | Dados completos da trilha no schema `learning-trail/v1` |
| `trail.md` | Versao Markdown (opcional, quando usuario escolhe) |

### Funcionalidades do HTML

- **Tema claro/escuro**: deteccao automatica do sistema + toggle manual
- **Responsivo**: funciona em desktop, tablet e mobile
- **Progresso local**: checkboxes por estacao, persistidos em `localStorage`
- **`file://` friendly**: abre corretamente sem servidor local
- **Acessivel**: HTML semantico legivel com JavaScript desabilitado
- **Stack**: Tailwind CSS (CDN), Phosphor Icons (CDN), JavaScript vanilla (sem Alpine.js)

### Contrato JSON (`trail.json`)

Schema versionado em `assets/trail_schema.example.json` com:
- `meta`: id, slug, titulo, idioma, nivel, datas
- `stations[]`: estacoes com nervos referenciando `resource_id`
- `resources[]`: todos os candidatos pesquisados (aprovados, reprovados, backup, weak_signal)
- `progress`: configuracao de localStorage
- `audit`: contagens derivaveis de stations e resources

## Arquitetura de validacao

Cada recurso recomendado passou por **validacao atomica**:
1. Fetch obrigatorio do conteudo real
2. Extracao de material substantivo (transcript para videos, abstract+conclusao para papers, conteudo completo para tutoriais)
3. Validacao contra 3 criterios: cobertura do subtopico, profundidade adequada, atualidade
4. Commit com trecho-prova documentado no arquivo final
5. Auditoria de cobertura multimodal para evitar trilhas pobres com poucos links ou so leitura

### Validacao de YouTube

Videos do YouTube exigem validacao obrigatoria:
- Transcript oficial ou auto-transcript
- Capitulos ou descricao substancial
- Slides ou repo associado
- Verificacao cruzada para videos opinativos

### Inventario completo

Todos os candidatos pesquisados aparecem no inventario final, mesmo que nao sejam nervos principais:
- `approved`: virou nervo principal
- `rejected`: nao atendeu criterios (aparece com rotulo)
- `backup`: recurso util mas nao essencial
- `weak_signal`: opiniao sem evidencia tecnica

## Estrutura de arquivos

```
learning-trail/
├── SKILL.md                    # Definicao completa da skill
├── README.md                   # Este arquivo
├── assets/
│   ├── TEMPLATE.html           # Template HTML autocontido
│   ├── trail_template.md       # Template Markdown
│   └── trail_schema.example.json  # Schema do JSON canonico
└── fixtures/                   # Exemplos reais para validacao
    └── trilhas/
        └── git-avancado/
            ├── trail.json
            └── index.html
```

## Requisitos do harness

Para funcionar completamente:
- `web_search` + `web_fetch` (obrigatorios)
- Acesso a transcripts do YouTube: `youtube-transcript-api`, `yt-dlp`, ou Whisper
- Acesso a transcricoes/show notes de podcasts quando houver audio recomendado
- Busca em fontes recentes de comunidade (X/Reddit/HN/GitHub) quando o tema exigir atualidade
- Sub-agent/Task tool (opcional, mas recomendado para paralelizar validacao)

## Versao

v4.0 — JSON-first, HTML autocontido com Tailwind, progresso local, validacao obrigatoria de YouTube, inventario completo
