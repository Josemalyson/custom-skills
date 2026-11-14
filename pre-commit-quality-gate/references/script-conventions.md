# Script conventions

Reference for `pre-commit-quality-gate` Step 3: convention guards (step 6), SKIP vars and the soft-skip pattern.

## Convention guards (step 6)

If `AGENTS.md` or `CONVENTIONS.md` exists, extract rules and encode as grep checks. Otherwise generate commented placeholders with common patterns for the detected language.

Four rule types:
1. **Prohibited patterns** — banned calls (`console.log`, `print()`, global loggers)
2. **Required patterns** — every handler has injected logger, every endpoint has auth
3. **Config sync** — env-keys consistent across environments
4. **Architectural invariants** — domain doesn't import infra

## SKIP var conventions

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
