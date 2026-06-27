# Pre-Commit Quality Gate — Go gRPC Pipeline

> **Arquivo:** `.githooks/pre-commit`
> **Projeto:** hub-contas (Go + gRPC)
> **Filosofia:** fail-fast do mais barato ao mais caro — erros rápidos bloqueiam antes de executar steps pesados

---

## Visão Geral

Pipeline de qualidade de código em **14 etapas** que executa automaticamente antes de cada `git commit`.
A estratégia de ordenação é deliberada: steps baratos e rápidos primeiro, steps pesados e com dependências externas por último.

O script usa `set -euo pipefail`:
- `-e` → qualquer erro aborta o script imediatamente
- `-u` → variáveis não definidas causam erro
- `-o pipefail` → falha em qualquer parte de um pipe propaga o erro

---

## As 14 Etapas

### Step 1 — `gofmt` · Formatação do código

**O que faz:** Valida que todo o código Go segue o padrão oficial de formatação `gofmt`.

**Exclusões:** `pb/` e `*.pb.go` — arquivos gerados automaticamente pelo protoc.

**Por que existe:** Elimina ruído de formatação nos diffs e discussões de estilo no code review.

**Falha se:** qualquer arquivo fora das exclusões estiver fora do padrão.

---

### Step 2 — `golangci-lint` · Qualidade de código

**O que faz:** Executa o meta-linter do ecossistema Go, agregando dezenas de linters (staticcheck, errcheck, gosimple, etc.) em uma única execução.

**Por que existe:** Detecta bugs sutis, más práticas e violações de convenção que o compilador não rejeita.

**Falha se:** qualquer linter configurado no `.golangci.yml` reportar violação.

---

### Step 3 — `govulncheck` · Scan de vulnerabilidades conhecidas

**O que faz:** Escaneia o código contra o banco de dados de vulnerabilidades do Go (vuln.go.dev).

**Comportamento diferenciado:**
- Vulnerabilidades em `stdlib` → **warn** (não bloqueia)
- Vulnerabilidades em dependências de terceiros alcançáveis → **fail** (bloqueia)

**Variável de controle:** `SKIP_GOVULNCHECK=1` → pula (padrão: executa)

---

### Step 4 — `deadcode` · Detecção de código morto

**O que faz:** Analisa o grafo de chamadas para identificar funções e métodos nunca chamados.

**Detalhe:** A análise inclui os testes como raízes — código usado apenas em testes não é considerado morto.

**Por que existe:** Código morto aumenta superfície de manutenção e pode mascarar bugs.

---

### Step 5 — `modernize` · Idiomas modernos de Go

**O que faz:** Detecta padrões substituídos por idiomas mais modernos da linguagem.

**Modo:** Report-only — não bloqueia. Exclusão de `pb/`.

---

### Step 6 — `convention guards` · Guardas de convenção arquitetural

**O que faz:** Valida estáticos definidos no `AGENTS.md` do projeto:

| Regra | Descrição |
|-------|-----------|
| `no zap.L()` | Proibido usar logger global — deve-se usar logger injetado |
| `no direct status.Error` | Handlers não criam erros gRPC diretamente — usa camada de erros padronizada |
| `infra env-keys sync` | Env-keys em sincronia entre `dev`, `hom` e `prod` |
| `X0_BASE_URL sem /contas/v1` | URL base não inclui o path — responsabilidade do cliente |

**Por que existe:** Automatiza revisão de padrões arquiteturais que seriam detectados só no code review humano.

---

### Step 7 — `go mod hygiene` · Higiene de módulos

**O que faz:**
1. `go.mod` e `go.sum` estão tidy (sem dependências fantasma ou ausentes)
2. Invariantes do `orchestrion.tool.go` validados (positivos e negativos)

**Falha se:** `go mod tidy` gerar qualquer diferença ou invariantes violados.

---

### Step 8 — `go test + cov` · Testes unitários + cobertura

**O que faz:** Executa a suíte de testes unitários e valida cobertura de statement **≥ 90%** nos pacotes de negócio.

**Falha se:** algum teste falhar **ou** cobertura cair abaixo de 90%.

---

### Step 9 — `go test -race` · Detector de data race

**O que faz:** Executa os testes com o race detector do Go (`-race`), detectando condições de corrida em acessos concorrentes.

**Auto-skip:** sem compilador C (CGO disabled) — race detector requer CGO.

**Variável de controle:** `SKIP_RACE=1` → pula (padrão: executa)

---

### Step 10 — Testes de integração · WireMock

**O que faz:** Sobe dependências externas mockadas via WireMock e executa testes de **fluxos completos de ponta a ponta**.

**Como funciona:**
1. `docker-compose up` sobe WireMock com os stubs HTTP das APIs downstream
2. Testes marcados com tag `integration` executam contra os mocks
3. Valida contratos de integração sem dependência de ambientes reais (dev/hom)

**Estrutura esperada:**
```
testdata/wiremock/
  mappings/     ← stubs HTTP (JSON)
  __files/      ← response bodies
docker-compose.test.yml
```

**Auto-skip:** Docker indisponível → soft-skip (warn, não fail).

**Variável de controle:** `SKIP_INTEGRATION=1` → pula (padrão: executa)

**Por que existe:** Steps unitários (8 e 9) testam em isolamento. Este step valida o comportamento real do serviço integrando com suas dependências mockadas.

---

### Step 11 — Testes de mutação · Qualidade da suíte de testes

**O que faz:** Injeta mutações no código de produção (inverte condições, remove returns, altera operadores) e verifica se os testes detectam.

**Por que isso importa:**
- Cobertura de 90% (step 8) pode ser falsa segurança — testes sem asserções cobrem linhas mas não detectam bugs
- Mutation testing mede se os testes **realmente falham quando o código está errado**
- Um mutante que **sobrevive** (teste não detecta) = falha na suíte de testes

**Threshold:** mutation score ≥ 70% (configurável).

**Auto-skip:** Docker indisponível → soft-skip.

**Variável de controle:** `SKIP_MUTATION=1` → pula (padrão: executa)

**Por que existe:** É a camada de meta-validação — valida não o código, mas a qualidade dos próprios testes.

---

### Step 12 — Testes de performance · Limites de latência e throughput

**O que faz:** Executa cenários de carga contra o serviço local ou via docker-compose e valida thresholds de performance.

**Thresholds típicos:**
- `p95 < 200ms` — latência no percentil 95
- `p99 < 500ms` — latência no percentil 99
- `error_rate < 1%` — taxa de erro máxima
- `throughput > N rps` — requisições por segundo mínimas

**Auto-skip:** Docker indisponível → soft-skip.

**Variável de controle:** `SKIP_PERF=1` → pula (padrão: executa)

**Por que existe:** Detecta regressões de performance antes do merge. Um commit que dobra a latência é descoberto localmente, não em produção.

---

### Step 13 — `proto pipeline` · Regeneração de stubs gRPC

**O que faz:** Quando arquivos `*.proto` estão staged:
1. Regenera stubs e descriptors a partir dos `.proto`
2. Atualiza o `kubernetes.yml` com as definições atualizadas

**Comportamento:** Executa **apenas quando há `*.proto` staged**.

**Variável de controle:** `SKIP_PROTO=1` → força skip

**Por que existe:** Garante que stubs gerados estejam sempre em sincronia com os contratos proto. Elimina o risco de commitar proto atualizado com stubs desatualizados.

---

### Step 14 — `Docker build` · Validação do Dockerfile de produção

**O que faz:** Build completo do Dockerfile de produção para validar que a imagem buildaria com sucesso.

**OFF por padrão** — é o único step habilitado explicitamente (`SKIP_DOCKER=0`).

**Motivo:** Lento e requer AWS credentials + acesso ao artifactory privado (GOPROXY).

**Auto-skip quando:**
- GOPROXY (artifactory) inacessível — fora da VPN
- Credenciais `AWS_*` ausentes

**Variável de controle:** `SKIP_DOCKER=0` → **habilita** (padrão: OFF — semântica inversa!)

---

## Mapa de Variáveis de Controle

> **A semântica NÃO é uniforme — leia com cuidado.**

| Variável | Step | Padrão | Semântica |
|----------|------|--------|-----------|
| `SKIP_GOVULNCHECK=1` | 3 | **Executa** | =1 pula |
| `SKIP_RACE=1` | 9 | **Executa** (auto-skip sem CGO) | =1 pula |
| `SKIP_INTEGRATION=1` | 10 | **Executa** (auto-skip sem Docker) | =1 pula |
| `SKIP_MUTATION=1` | 11 | **Executa** (auto-skip sem Docker) | =1 pula |
| `SKIP_PERF=1` | 12 | **Executa** (auto-skip sem Docker) | =1 pula |
| `SKIP_PROTO=1` | 13 | **Executa** só se `*.proto` staged | =1 força skip |
| `SKIP_DOCKER=0` | 14 | **OFF** | =0 **habilita** (inverso!) |

---

## Comportamento de Soft-Skip

Steps com dependência de infraestrutura fazem **soft-skip** (warn, não fail) quando:
- Docker daemon está indisponível
- Artifactory (GOPROXY) inacessível — fora da VPN
- Credenciais `AWS_*` ausentes

Garante que desenvolvedores possam commitar sem VPN ou Docker rodando, sem bloquear o fluxo local.

---

## Instalação

```bash
# Opção 1 — git config
git config core.hooksPath .githooks

# Opção 2 — via Makefile
make -C app setup-hooks
```

---

## Ordem Estratégica dos 14 Steps

```
Custo / Tempo
    |
    |  14. Docker build            ++++++++++++++++++ (opcional, AWS req.)
    |  12. Performance tests       ++++++++++++++++
    |  11. Mutation tests          +++++++++++++
    |  10. Integration (WireMock)  +++++++++
    |   9. go test -race           ++++++++
    |   8. go test + cov           ++++++++
    |  13. proto pipeline          +++++++ (só se .proto staged)
    |   7. go mod hygiene          ++++++
    |   6. convention guards       +++++
    |   5. modernize               ++++
    |   4. deadcode                ++++
    |   3. govulncheck             +++
    |   2. golangci-lint           +++
    |   1. gofmt                   +
    +----------------------------------------------- Step
```

---

## Impacto Arquitetural

Este pipeline representa um **shift-left radical de qualidade**:

| Camada | Steps | O que garante |
|--------|-------|---------------|
| Estilo e convenção | 1, 2, 5, 6 | Código consistente sem revisão manual |
| Segurança | 3 | Vulnerabilidades conhecidas bloqueadas antes do repositório |
| Estrutura | 4, 7 | Código limpo, dependências íntegras |
| Correção unitária | 8, 9 | Comportamento correto + sem race conditions |
| Correção integrada | 10 | Contratos com dependências externas validados |
| Qualidade dos testes | 11 | A suíte de testes realmente detecta bugs |
| Performance | 12 | Nenhuma regressão de latência/throughput chega ao merge |
| Contratos gRPC | 13 | Stubs sempre sincronizados com os .proto |
| Build | 14 | Dockerfile de produção validado antes do CI/CD |

O CI/CD recebe código que já passou por um pipeline de qualidade equivalente ao de integração, reduzindo drasticamente falhas na pipeline remota.
