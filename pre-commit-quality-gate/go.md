# Referência: Go — Pre-Commit Quality Gate

## Mapeamento Completo por Step

| # | Categoria | Ferramenta | Comando base |
|---|-----------|-----------|--------------|
| 1 | Formatter | `gofmt` | `gofmt -l ./... \| grep -v pb/ \| grep -v .pb.go` |
| 2 | Linter | `golangci-lint` | `golangci-lint run ./...` |
| 3 | Security | `govulncheck` | `govulncheck ./...` |
| 4 | Dead code | `deadcode` | `deadcode -test ./...` |
| 5 | Modernizer | `modernize` | `modernize -diff ./... 2>&1 \| grep -v pb/` |
| 6 | Conventions | custom grep/AST | ver secao abaixo |
| 7 | Module hygiene | `go mod tidy` | `go mod tidy && git diff --exit-code go.mod go.sum` |
| 8 | Tests + cov | `go test` | `go test -coverprofile=coverage.out ./...` |
| 9 | Race detector | `go test -race` | `go test -race ./...` |
| 10 | Integration | docker-compose + WireMock | ver secao abaixo |
| 11 | Mutation | `gremlins` | `gremlins unleash ./...` |
| 12 | Performance | `k6` | `k6 run performance/smoke.js` |
| 13 | Schema pipeline | `buf` ou `protoc` | `buf generate && git diff --exit-code` |
| 14 | Docker build | `docker build` | `docker build --build-arg ... -t test-build .` |

---

## Instalação de Ferramentas

```bash
# Core Go tools
go install golang.org/x/vuln/cmd/govulncheck@latest
go install golang.org/x/tools/cmd/deadcode@latest
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Mutation testing
go install github.com/go-gremlins/gremlins/cmd/gremlins@latest

# Performance testing
brew install k6               # macOS
# ou: https://k6.io/docs/getting-started/installation/

# Proto
brew install bufbuild/buf/buf
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```

---

## Step 6 — Convention Guards

```bash
# ── Proibir logger global zap (usar logger injetado) ──────────
if gofmt -l . | xargs grep -l "zap\.L()" 2>/dev/null | grep -v pb/; then
  echo "[FAIL] zap.L() proibido — use logger injetado via dependência"
  exit 1
fi

# ── Proibir status.Error direto em handlers ───────────────────
if grep -rn "status\.Error(" --include="*.go" internal/handler/ 2>/dev/null; then
  echo "[FAIL] status.Error() direto em handler — use a camada de erros padronizada"
  exit 1
fi

# ── Sincronização de env-keys entre ambientes ─────────────────
DEV_KEYS=$(grep -oP 'os\.Getenv\("\K[^"]+' config/dev.go 2>/dev/null | sort)
PROD_KEYS=$(grep -oP 'os\.Getenv\("\K[^"]+' config/prod.go 2>/dev/null | sort)
if [[ "$DEV_KEYS" != "$PROD_KEYS" ]]; then
  echo "[FAIL] Env-keys fora de sincronia entre dev e prod"
  diff <(echo "$DEV_KEYS") <(echo "$PROD_KEYS")
  exit 1
fi

# ── X0_BASE_URL não deve conter /contas/v1 ────────────────────
if grep -rn 'X0_BASE_URL.*contas/v1' --include="*.go" .; then
  echo "[FAIL] X0_BASE_URL não deve incluir /contas/v1 — responsabilidade do cliente"
  exit 1
fi
```

---

## Step 8 — Cobertura com limiar

```bash
go test -coverprofile=coverage.out ./...

COVERAGE=$(go tool cover -func=coverage.out \
  | grep "^total:" | awk '{print $3}' | sed 's/%//')
THRESHOLD=${COV_THRESHOLD:-90}

if (( $(echo "$COVERAGE < $THRESHOLD" | bc -l) )); then
  echo "[FAIL] Cobertura ${COVERAGE}% abaixo do limiar de ${THRESHOLD}%"
  go tool cover -func=coverage.out | grep -v "100.0%"
  exit 1
fi
echo "[PASS] Cobertura ${COVERAGE}%"
```

---

## Step 10 — Integration tests com WireMock

```bash
# Estrutura esperada no projeto:
# testdata/wiremock/mappings/   ← stubs HTTP (JSON)
# testdata/wiremock/__files/    ← response bodies
# docker-compose.test.yml

# Sobe WireMock
docker-compose -f docker-compose.test.yml up -d wiremock
trap 'docker-compose -f docker-compose.test.yml down --remove-orphans' EXIT

# Aguarda WireMock estar healthy
timeout 30 bash -c 'until curl -sf http://localhost:8080/__admin/health; do sleep 1; done'

# Executa testes de integração (tag obrigatória)
go test -tags=integration -timeout=120s ./...
```

**Exemplo de stub WireMock (`testdata/wiremock/mappings/downstream-api.json`):**
```json
{
  "request": {
    "method": "POST",
    "urlPattern": "/api/v1/payment"
  },
  "response": {
    "status": 200,
    "jsonBody": { "transactionId": "txn-123", "status": "approved" },
    "headers": { "Content-Type": "application/json" }
  }
}
```

**Tag nos testes Go:**
```go
//go:build integration

package integration_test

func TestPaymentFlow(t *testing.T) { ... }
```

---

## Step 11 — Mutation tests com gremlins

```bash
# Instalar
go install github.com/go-gremlins/gremlins/cmd/gremlins@latest

# Executar (exclui pb/ e arquivos gerados)
gremlins unleash \
  --tags unit \
  --exclude-files "pb/,*.pb.go,*_gen.go" \
  ./...

# Extrair mutation score e validar threshold
MUTATION_SCORE=$(gremlins unleash ./... 2>&1 \
  | grep -oP 'Mutation score: \K[\d.]+')
MUTATION_THRESHOLD=${MUTATION_THRESHOLD:-70}

if (( $(echo "$MUTATION_SCORE < $MUTATION_THRESHOLD" | bc -l) )); then
  echo "[FAIL] Mutation score ${MUTATION_SCORE}% abaixo de ${MUTATION_THRESHOLD}%"
  echo "       Mutantes que sobreviveram indicam testes sem asserções reais."
  exit 1
fi
echo "[PASS] Mutation score ${MUTATION_SCORE}%"
```

**O que gremlins muta:**
- Condicionais: `==` → `!=`, `>` → `>=`
- Aritméticos: `+` → `-`, `*` → `/`
- Lógicos: `&&` → `||`
- Returns: remove statements de retorno de erro

---

## Step 12 — Performance tests com k6

```bash
# Sobe o serviço local para teste de performance
docker-compose -f docker-compose.test.yml up -d app
trap 'docker-compose -f docker-compose.test.yml down --remove-orphans' EXIT

# Aguarda app estar healthy
timeout 60 bash -c 'until curl -sf http://localhost:8081/health; do sleep 2; done'

# Executa cenário de performance
k6 run \
  --env BASE_URL=http://localhost:8081 \
  performance/smoke.js
```

**Exemplo de script k6 (`performance/smoke.js`):**
```javascript
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],
    http_req_failed:   ['rate<0.01'],
  },
};

export default function () {
  const res = http.post(
    `${__ENV.BASE_URL}/contas/v1/payment`,
    JSON.stringify({ amount: 100 }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(res, { 'status 200': (r) => r.status === 200 });
}
```

---

## Step 13 — Schema pipeline (só quando *.proto staged)

```bash
SCHEMA_STAGED=$(git diff --cached --name-only --diff-filter=ACM | grep '\.proto$' || true)

if [[ -n "$SCHEMA_STAGED" ]]; then
  echo "Proto files staged: $SCHEMA_STAGED"
  buf generate
  git add .
  git diff --exit-code -- '*.pb.go' || {
    echo "[FAIL] Stubs gerados diferem dos esperados — verifique o buf.gen.yaml"
    exit 1
  }
fi
```

---

## Soft-skip Helpers

```bash
has_docker()     { docker info &>/dev/null 2>&1; }
has_cgo()        { [[ "$(go env CGO_ENABLED)" == "1" ]]; }
has_goproxy()    { curl -sf --max-time 3 "${GOPROXY%%,*}" &>/dev/null; }
has_aws_creds()  { [[ -n "${AWS_ACCESS_KEY_ID:-}" && -n "${AWS_SECRET_ACCESS_KEY:-}" ]]; }
```

---

## Notas Específicas de Go

- **Exclusões:** `pb/` e `*.pb.go` em gofmt, lint, modernize e mutation
- **`orchestrion.tool.go`:** se Datadog Orchestrion, validar invariantes no step 7
- **`GOFLAGS` e módulos privados:** garantir `GONOSUMCHECK` no ambiente
- **`go generate`:** se `//go:generate` existe, rodar antes dos testes (step 7 ou 8)
- **Tags de build:** separar testes unitários (`unit`) vs integração (`integration`)
