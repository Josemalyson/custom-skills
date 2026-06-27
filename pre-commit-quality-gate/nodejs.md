# Referência: Node.js / TypeScript — Pre-Commit Quality Gate

## Mapeamento Completo por Step

| # | Categoria | Ferramenta | Comando base |
|---|-----------|-----------|--------------|
| 1 | Formatter | `prettier` ou `biome` | `prettier --check .` |
| 2 | Linter | `eslint` + `tsc --noEmit` | `eslint . --max-warnings 0 && tsc --noEmit` |
| 3 | Security | `npm audit` | `npm audit --audit-level=high` |
| 4 | Dead code | `knip` | `knip` |
| 5 | Modernizer | `eslint-plugin-unicorn` | embutido no eslint (report-only) |
| 6 | Conventions | custom grep/eslint rules | ver secao abaixo |
| 7 | Module hygiene | lock check | `npm ci --dry-run && git diff --exit-code package-lock.json` |
| 8 | Tests + cov | `jest --coverage` ou `vitest` | `jest --coverage --coverageThreshold=...` |
| 9 | Race/async | unhandled promises | `--detectOpenHandles --forceExit` |
| 10 | Integration | docker-compose + `msw` / WireMock | ver secao abaixo |
| 11 | Mutation | `stryker` | `npx stryker run` |
| 12 | Performance | `k6` ou `autocannon` | `k6 run performance/smoke.js` |
| 13 | Schema pipeline | `openapi-generator` / `protoc` | `openapi-generator-cli generate && git diff --exit-code` |
| 14 | Docker build | `docker build` | `docker build -t test-build .` |

---

## Instalação

```bash
npm install --save-dev prettier eslint typescript knip jest @types/jest \
                         stryker-cli @stryker-mutator/core \
                         @stryker-mutator/jest-runner
npm install --global k6   # ou via brew install k6
```

---

## Step 6 — Convention Guards

```bash
# Proibir console.log em src/
if grep -rn "console\.log(" --include="*.ts" src/; then
  echo "[FAIL] console.log() proibido — use o logger estruturado"
  exit 1
fi

# Proibir 'any' explícito
if grep -rn ": any" --include="*.ts" src/; then
  echo "[FAIL] Tipo 'any' explícito proibido"
  exit 1
fi

# Services nao importam controllers
if grep -rn "from.*controller" --include="*.ts" src/services/; then
  echo "[FAIL] services/ nao pode importar controllers/"
  exit 1
fi
```

---

## Step 8 — Cobertura

```bash
jest --coverage --coverageThreshold='{
  "global": {
    "statements": 90,
    "branches": 80,
    "functions": 90,
    "lines": 90
  }
}'
```

---

## Step 10 — Integration tests

```bash
# MSW (Mock Service Worker) para Node.js — alternativa ao WireMock
# Ou WireMock via docker-compose

docker-compose -f docker-compose.test.yml up -d wiremock
trap 'docker-compose -f docker-compose.test.yml down' EXIT

timeout 30 bash -c 'until curl -sf http://localhost:8080/__admin/health; do sleep 1; done'

# Testes com tag de integração
npx jest --testPathPattern="integration" --runInBand
```

---

## Step 11 — Mutation com Stryker

```bash
# stryker.config.json deve existir na raiz
npx stryker run

# Extrair score
SCORE=$(cat reports/mutation/mutation.json | \
  node -e "const d=require('/dev/stdin'); \
  console.log(Math.round(d.metrics.mutationScore))")
if [[ "$SCORE" -lt 70 ]]; then
  echo "[FAIL] Mutation score ${SCORE}% abaixo de 70%"
  exit 1
fi
```

---

## Step 12 — Performance com k6

```bash
# Subir app local
docker-compose -f docker-compose.test.yml up -d app
trap 'docker-compose -f docker-compose.test.yml down' EXIT

timeout 60 bash -c 'until curl -sf http://localhost:3000/health; do sleep 2; done'

k6 run --env BASE_URL=http://localhost:3000 performance/smoke.js
```

---

## Notas Específicas de Node.js/TypeScript

- **`package-lock.json` vs `yarn.lock` vs `pnpm-lock.yaml`:** adaptar step 7 ao gerenciador
- **ESM vs CJS:** garantir que jest/vitest suporta o tipo de módulo do projeto
- **`--detectOpenHandles`:** obrigatório em Jest para detectar conexoes abertas
- **Stryker + Jest:** configurar `stryker.config.json` para usar `@stryker-mutator/jest-runner`
- **Monorepo (turborepo/nx):** adaptar commands para rodar apenas nos pacotes modificados via `--filter`
