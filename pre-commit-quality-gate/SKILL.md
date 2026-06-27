---
name: pre-commit-quality-gate
description: >
  Shift-left quality gate — fingerprints the project stack and generates a fail-fast
  pre-commit pipeline automatically. Use when the user wants pre-commit hooks,
  local quality gates, or CI at the commit boundary. Also when another skill needs
  to enforce commit-time checks.
---

# Pre-Commit Quality Gate

**Shift-left**: move quality checks to the commit boundary so CI receives already-validated code. The agent **fingerprints** the project — scans for manifests, configs, and conventions — then generates a fail-fast pipeline ordered cheap → expensive. No questions unless the fingerprint is ambiguous.

## Step 1 — Fingerprint the project

Scan the working directory. Collect every signal before deciding anything.

| Signal | Detects |
|--------|---------|
| `go.mod` | Go |
| `package.json` (+ `tsconfig.json` for TS) | Node.js / TypeScript |
| `pom.xml` or `build.gradle` / `build.gradle.kts` | Java / Kotlin |
| `pyproject.toml` / `requirements.txt` / `setup.py` | Python |
| `Cargo.toml` | Rust |
| `*.proto` | gRPC schema pipeline (step 13) |
| `openapi.yaml` / `swagger.*` | OpenAPI schema pipeline (step 13) |
| `Dockerfile` | Docker build validation (step 14) |
| `docker-compose*.yml` | Integration test infra (steps 10-12) |
| `.golangci.yml` / `.eslintrc*` / `ruff.toml` / `checkstyle.xml` | Existing linter config — adopt, don't replace |
| `.github/workflows/` / `.gitlab-ci.yml` / `Jenkinsfile` | CI pipeline — align local steps with remote |
| `AGENTS.md` / `CONVENTIONS.md` | Convention guards source (step 6) |
| `.githooks/` / `.husky/` / `.git/hooks/pre-commit` | Existing hooks — warn before overwriting |
| Lock files (`go.sum`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`) | Package manager |
| `turborepo.json` / `nx.json` / workspace globs | Monorepo — scope steps to changed packages |

Also detect:
- **Test runner** from config or scripts (`jest`, `vitest`, `pytest`, `go test`, `mvn test`, `gradle test`)
- **Coverage tool** already configured (JaCoCo, c8, coverage.py, go tool cover)
- **Existing thresholds** in CI configs or tool configs — reuse them rather than imposing defaults

**Completion criterion**: a manifest printed to the user listing: detected language(s), package manager, test runner, linter, formatter, schemas, infra, and existing hooks. If any signal is ambiguous (e.g. both `pom.xml` and `package.json` present), ask only about the ambiguity — not the full questionnaire.

## Step 2 — Load language reference

Read the matching reference file from this skill's directory:

| Language | File |
|----------|------|
| Go | `go.md` |
| Python | `python.md` |
| Node.js / TypeScript | `nodejs.md` |
| Java / Kotlin | `java.md` |

Multi-language projects: load all matching references and merge tool mappings.

Resolve a concrete tool for each of the 14 categories. Where no equivalent exists for the detected language (e.g. race detector in Python), mark as `warn` or `skip` with a one-line justification — never leave a placeholder unresolved.

**Completion criterion**: every category in the table below has either a concrete tool+command or an explicit N/A with reason.

## Step 3 — Generate the pipeline

Use `template.sh` as the structural base. Fill every `{{placeholder}}` with tools from the fingerprint + reference.

### The 14 categories

| # | Category | Purpose | Mode |
|---|----------|---------|------|
| -1 | Secret scanner | Credential leak prevention (Gitleaks) | fail |
| 0 | Branch name | Git Flow / trunk-based pattern validation | fail |
| 1 | Formatter | Style normalization — eliminates diff noise | fail |
| 2 | Linter | Static quality — bugs and bad practices | fail |
| 3 | Security scan | Dependency vulnerabilities | fail (warn for stdlib) |
| 4 | Dead code | Unreachable / unused code | fail |
| 5 | Modernizer | Modern language idioms | warn (report-only) |
| 6 | Convention guards | Team architectural rules (custom) | fail |
| 7 | Module hygiene | Lock files and manifests integrity | fail |
| 8 | Tests + coverage | Unit suite + coverage threshold | fail |
| 9 | Race / concurrency | Data races, async bugs | fail (soft-skip when unsupported) |
| 10 | Integration tests | End-to-end flows via HTTP mocks | fail (soft-skip without Docker) |
| 11 | Mutation tests | Test suite quality validation | fail (soft-skip without Docker) |
| 12 | Performance tests | Latency / throughput regression | fail (soft-skip without Docker) |
| 13 | Schema pipeline | Stub regeneration / breaking changes | fail (only when schema files staged) |
| 14 | Build validation | Production Dockerfile | fail (OFF by default — `SKIP_DOCKER=0` enables) |
| n/a | commit-msg | Conventional Commits validation | fail |

### Generation rules

- `set -euo pipefail` always
- Strict order: -1 through 14
- Soft-skip (warn, not fail) for steps with infrastructure dependencies
- SKIP vars documented in the script header
- Log format: `[STEP N/14]`, `[SKIP]`, `[WARN]`, `[PASS]`, `[FAIL]`
- Adopt thresholds from existing configs; fall back to defaults only when none found (coverage: 90%, mutation: 70%, p95 < 200ms)

### Convention guards (step 6)

If `AGENTS.md` or `CONVENTIONS.md` exists, extract rules and encode as grep checks. Otherwise generate commented placeholders with common patterns for the detected language.

Four rule types:
1. **Prohibited patterns** — banned calls (`console.log`, `print()`, global loggers)
2. **Required patterns** — every handler has injected logger, every endpoint has auth
3. **Config sync** — env-keys consistent across environments
4. **Architectural invariants** — domain doesn't import infra

### SKIP var conventions

```bash
# SKIP pattern (ON by default, =1 disables)
SKIP_SECURITY=${SKIP_SECURITY:-0}
SKIP_RACE=${SKIP_RACE:-0}
SKIP_INTEGRATION=${SKIP_INTEGRATION:-0}
SKIP_MUTATION=${SKIP_MUTATION:-0}
SKIP_PERF=${SKIP_PERF:-0}
SKIP_SCHEMA=${SKIP_SCHEMA:-0}

# ENABLE pattern (OFF by default, =0 enables) — INVERTED semantics
SKIP_DOCKER=${SKIP_DOCKER:-1}
```

Soft-skip pattern for infrastructure dependencies:

```bash
if ! docker info &>/dev/null 2>&1; then
  echo "[WARN] Docker unavailable — step N soft-skipped"
  # continue, do not exit 1
fi
```

**Completion criterion**: `.githooks/pre-commit` and `.githooks/commit-msg` generated with all placeholders resolved — no `{{...}}` remaining. Scripts are syntactically valid bash (`bash -n .githooks/pre-commit` passes).

## Step 4 — Install and verify

1. Create `.githooks/` if absent
2. `chmod +x .githooks/pre-commit .githooks/commit-msg`
3. `git config core.hooksPath .githooks`
4. Print required tool installations with install commands
5. Dry-run: `bash .githooks/pre-commit` — observe output

**Completion criterion**: hook executes end-to-end. Steps with available tools show `[PASS]`. Steps missing tools show `[WARN]` or `[SKIP]` with install instructions. No syntax errors, no unresolved placeholders.

## Output

1. **`.githooks/pre-commit`** — executable pipeline with all steps adapted
2. **`.githooks/commit-msg`** — Conventional Commits validator
3. **Dependency checklist** — tools to install, with commands per detected language
4. **Installation command** — printed to the user

## References

- `go.md` — Go tool mapping
- `python.md` — Python tool mapping
- `nodejs.md` — Node.js / TypeScript tool mapping
- `java.md` — Java / Kotlin tool mapping
- `template.sh` — Parameterized script base
