# Referência: Python — Pre-Commit Quality Gate

## Mapeamento Completo por Step

| # | Categoria | Ferramenta | Comando base |
|---|-----------|-----------|--------------|
| 1 | Formatter | `ruff format` | `ruff format --check .` |
| 2 | Linter | `ruff check` + `mypy` | `ruff check . && mypy src/` |
| 3 | Security | `bandit` + `safety` | `bandit -r src/ && safety check` |
| 4 | Dead code | `vulture` | `vulture src/ --min-confidence 80` |
| 5 | Modernizer | `pyupgrade` | `pyupgrade --py311-plus **/*.py` |
| 6 | Conventions | custom grep | ver secao abaixo |
| 7 | Module hygiene | `pip-audit` + lock check | `pip-audit && git diff --exit-code requirements.txt` |
| 8 | Tests + cov | `pytest --cov` | `pytest --cov=src --cov-fail-under=90` |
| 9 | Race/async | `asyncio` debug | `PYTHONASYNCIODEBUG=1 pytest -x` |
| 10 | Integration | docker-compose + `responses`/WireMock | ver secao abaixo |
| 11 | Mutation | `mutmut` | `mutmut run && mutmut results` |
| 12 | Performance | `locust` ou `k6` | `locust --headless -u 10 -r 1 -t 30s` |
| 13 | Schema pipeline | `datamodel-codegen` / `protoc` | `datamodel-codegen --input openapi.yaml && git diff --exit-code` |
| 14 | Docker build | `docker build` | `docker build -t test-build .` |

---

## Instalação

```bash
pip install ruff mypy bandit safety vulture pyupgrade pip-audit \
            pytest pytest-cov pytest-asyncio mutmut locust
```

---

## Step 6 — Convention Guards

```bash
# Proibir print() em src/ (usar logging)
if grep -rn "^print(" --include="*.py" src/; then
  echo "[FAIL] print() proibido em src/ — use logging estruturado"
  exit 1
fi

# Proibir importar infra a partir do domain
if grep -rn "from infrastructure" --include="*.py" src/domain/; then
  echo "[FAIL] domain/ não pode importar infrastructure/"
  exit 1
fi

# Verificar sync de env-keys entre settings
DEV=$(grep -oP "os\.getenv\(['\"]?\K[A-Z_]+" src/config/dev.py | sort)
PROD=$(grep -oP "os\.getenv\(['\"]?\K[A-Z_]+" src/config/prod.py | sort)
if [[ "$DEV" != "$PROD" ]]; then
  echo "[FAIL] Env-keys fora de sincronia entre dev e prod"
  diff <(echo "$DEV") <(echo "$PROD")
  exit 1
fi
```

---

## Step 10 — Integration tests

```bash
# WireMock via docker-compose ou biblioteca responses/httpretty
docker-compose -f docker-compose.test.yml up -d wiremock
trap 'docker-compose -f docker-compose.test.yml down' EXIT

timeout 30 bash -c 'until curl -sf http://localhost:8080/__admin/health; do sleep 1; done'

pytest -m integration --timeout=120
```

---

## Step 11 — Mutation com mutmut

```bash
mutmut run --paths-to-mutate src/ --tests-dir tests/
SURVIVED=$(mutmut results | grep -c "survived" || true)
TOTAL=$(mutmut results | grep -cE "survived|killed" || true)

if [[ "$TOTAL" -gt 0 ]]; then
  SCORE=$(echo "scale=1; (($TOTAL - $SURVIVED) * 100) / $TOTAL" | bc)
  if (( $(echo "$SCORE < 70" | bc -l) )); then
    echo "[FAIL] Mutation score ${SCORE}% abaixo de 70%"
    exit 1
  fi
fi
```

---

## Step 12 — Performance com Locust

```bash
# locustfile.py deve existir em performance/
locust -f performance/locustfile.py \
  --headless -u 10 -r 2 -t 30s \
  --host http://localhost:8000 \
  --html performance/report.html \
  --exit-code-on-error 1
```

---

## Nota sobre Step 9 (Race/Async)

Python tem GIL — race conditions classicas nao existem da mesma forma.
Foco em:
- Bugs de `asyncio` (coroutines nao awaited, tasks perdidas)
- `PYTHONASYNCIODEBUG=1` expoe coroutines criadas mas nao aguardadas
- Considerar `pytest-asyncio` com `asyncio_mode=strict`
