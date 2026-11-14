# Ferramentas da skill `pre-commit-quality-gate`

Tudo que a skill usa, conforme o SKILL.md. Ferramenta nova: crie em `scripts/` desta skill ou cite uma existente (regra da skill `criar-skill`). Sem segredos; credenciais só por env vars.

| Ferramenta | Onde está | Como checar que existe |
|---|---|---|
| git (`core.hooksPath`) | sistema | `git --version` |
| bash (`bash -n` para validar o hook) | sistema | `bash --version` |
| Gitleaks (step -1) | CLI | `command -v gitleaks` |
| Docker (steps 10–12 e 14, soft-skip sem ele) | sistema | `docker info` |
| Ferramentas por linguagem (formatter, linter, testes, cobertura…) | `references/go.md`, `python.md`, `nodejs.md`, `java.md` | o hook gerado imprime o que falta instalar |
| Base do script | `scripts/template.sh` | `test -f scripts/template.sh` |
| Convenções do script | `references/script-conventions.md` | `test -f references/script-conventions.md` |

> Criado em 2026-11-07 a partir do SKILL.md (sem acrescentar ferramentas que ele não cita); revise se a skill mudar.
