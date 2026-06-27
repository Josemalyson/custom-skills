# learning-trail

Skill para geração de trilhas de aprendizado no padrão **spine + nerves** com validação atômica de recursos.

## O que faz

Dado um assunto qualquer, gera um arquivo `.md` estruturado como:
- **Coluna vertebral**: estações sequenciais de conhecimento (5-10 min cada)
- **Nervos**: recursos externos validados por conteúdo (links que o agente leu/transcreveu antes de recomendar)
- **Boss final**: 5 perguntas socráticas de validação

## Instalação

### Claude Code (CLI)
```bash
# Copie a pasta para o diretório de skills do Claude Code
cp -r learning-trail ~/.claude/skills/

# Ou instale via .skill bundle
claude skill install learning-trail.skill
```

### Harness customizado
```bash
# Coloque a pasta no diretório de skills do seu harness
cp -r learning-trail /caminho/do/seu/harness/skills/
```

## Como usar

Após instalado, acione a skill com qualquer um destes padrões:

**PT-BR:**
```
quero aprender Kubernetes
me ensina o que é RAG
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

A skill gera um arquivo em `./trilhas/{slug-do-topico}.md` com:

- Frontmatter YAML (metadata, DAG de pré-requisitos/próximos passos)
- Mapa da trilha (tabuleiro completo antes de começar)
- Estações sequenciais com nervos validados
- Seção de auditoria (quantos candidatos inspecionados, aprovados, reprovados)

## Arquitetura de validação

Cada recurso recomendado passou por **validação atômica**:
1. Fetch obrigatório do conteúdo real
2. Extração de material substantivo (transcript para vídeos, abstract+conclusão para papers, conteúdo completo para tutoriais)
3. Validação contra 3 critérios: cobertura do subtópico, profundidade adequada, atualidade
4. Commit com trecho-prova documentado no arquivo final

## Requisitos do harness

Para funcionar completamente:
- `web_search` + `web_fetch` (obrigatórios)
- Acesso a transcripts do YouTube: `youtube-transcript-api`, `yt-dlp`, ou Whisper
- Sub-agent/Task tool (opcional, mas recomendado para paralelizar validação)

## Versão

v3.0 — trust by inspection (validação atômica por conteúdo)
