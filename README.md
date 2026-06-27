# Custom Skills

> Production-ready AI agent skill bundles for Claude Code, custom harnesses, and any LLM-based coding assistant.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/josemalyson/custom-skills/pulls)
[![Issues](https://img.shields.io/github/issues/josemalyson/custom-skills)](https://github.com/josemalyson/custom-skills/issues)

A curated collection of **5 battle-tested skills** that teach AI agents how to perform complex, multi-step tasks with high quality. Each skill is a self-contained "behavior module" with structured prompts, reference materials, and ready-to-use templates.

---

## Why Custom Skills?

Most AI coding assistants are powerful but generic. They lack domain-specific workflows for security investigations, code architecture analysis, learning path generation, and more. **Custom Skills bridges this gap** by providing:

- **Structured methodologies** — not just prompts, but complete multi-phase workflows
- **Production-ready tooling** — real scripts, templates, and report generators
- **Battle-tested references** — curated knowledge bases that agents load on-demand
- **Interoperable design** — skills that reference and enhance each other

---

## Skills Overview

| Skill | Purpose | Triggers On |
|-------|---------|-------------|
| [agent-code-detective](#agent-code-detective) | Investigate and map any AI agent open-source project | "understand project X", "investigate codebase" |
| [html-first](#html-first) | Generate self-contained HTML artifacts for visual tasks | "compare approaches", "design mockup", "code review" |
| [k8s-investigation](#k8s-investigation) | Deep RCA, security, and performance analysis for K8s/VPS | "investigate cluster", "security audit", "performance issue" |
| [learning-trail](#learning-trail) | Generate validated learning paths with resource verification | "learn X", "create study guide", "learning trail" |
| [pre-commit-quality-gate](#pre-commit-quality-gate) | Auto-generate 14-step pre-commit pipelines for any stack | "pre-commit hooks", "quality gate", "code quality" |

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/josemalyson/custom-skills.git
cd custom-skills
```

### 2. Install Skills

Copy the desired skill folder to your agent's skill directory:

```bash
# For Claude Code
cp -r learning-trail ~/.claude/skills/

# Or install all skills at once
cp -r */ ~/.claude/skills/
```

### 3. Start Using

Skills are **automatically triggered** based on natural language. For example:

```bash
# These phrases activate the corresponding skill:
"Me ajuda a entender o projeto OpenHands"  → agent-code-detective
"Compare React, Vue, and Svelte"          → html-first
"Quero aprender Kubernetes do zero"        → learning-trail
"Audit my cluster for vulnerabilities"    → k8s-investigation
"Set up pre-commit hooks for this repo"   → pre-commit-quality-gate
```

---

## Skills Deep Dive

### Agent Code Detective

**The systematic methodology for reverse-engineering any AI agent codebase.**

Turns your agent into a "code detective" that can map architectures of projects like OpenHands, Aider, Cline, LangGraph, CrewAI, and more.

#### 6-Phase Workflow

| Phase | Time | Description |
|-------|------|-------------|
| 1. Territory Reconnaissance | 15 min | Read README, analyze dependencies, map folder structure |
| 2. Entry Point | 30 min | Locate execution start, classify as CLI/HTTP/SDK/Worker |
| 3. Follow the Trail | 1h | Find 6 universal components using grep patterns |
| 4. Live Surveillance | 1-2h | Debug with 5 universal breakpoints |
| 5. X-Ray Tracing | 30 min | Capture HTTP calls to LLM providers |
| 6. Validate by Modifying | 1h | Make 3+ experiments to confirm understanding |

#### Output

A structured `docs/investigation.md` dossier with:
- Identity and entry point analysis
- 6 core components (Agent loop, LLM client, Tool registry, Memory/State, Prompt manager)
- End-to-end flow visualization
- Observed patterns and architectural decisions
- Transferable learnings

#### References

- `breakpoint-cheatsheet.md` — 5 universal breakpoints with inspection variables
- `debug-configs.md` — VSCode launch.json for Python, TypeScript, Rust, Go
- `dossier-template.md` — Complete investigation report template
- `tracing-setup.md` — mitmproxy, Langfuse, OpenTelemetry guides

---

### HTML First

**Self-contained HTML artifacts for spatial, visual, and interactive tasks.**

Based on the thesis "HTML is the new Markdown" — when a task benefits from layout, color, real diagrams, or interactivity, produce a single-file HTML artifact instead of linear Markdown.

#### When It Triggers

- **Comparison/Planning** — "compare X approaches", "implementation plan"
- **Code Reviews** — "review this PR", "analyze these changes"
- **Design** — "mockup", "design system", "animation"
- **Diagrams** — "architecture diagram", "sequence diagram"
- **Reports** — "status report", "post-mortem"
- **Slides** — "deck", "presentation"
- **Custom Editors** — "drag and drop", "triage tool"

#### Universal Rules

1. **Single-file, self-contained** — all CSS/JS inline, no CDN dependencies
2. **Mobile-responsive** — CSS Grid/Flexbox, `clamp()`, touch targets ≥ 44px
3. **Accessible** — semantic HTML, WCAG AA contrast, aria-labels
4. **No "AI aesthetic"** — no purple-blue gradients, no glassmorphism
5. **Respect existing design systems** if present

#### Templates (8)

| Template | Use Case |
|----------|----------|
| `_base.html` | Foundation with CSS custom properties and dark mode |
| `comparison-grid.html` | 2-6 options side-by-side with trade-offs |
| `implementation-plan.html` | Timeline + mockups + code + risk table |
| `pr-review.html` | Diff annotated + margin notes + severity tags |
| `status-report.html` | What shipped / what slipped / metrics |
| `concept-explainer.html` | TL;DR + collapsibles + glossary hover |
| `slide-deck.html` | `<section>` + arrow-key navigation + speaker notes |
| `custom-editor.html` | Toggle/drag/form + "copy as JSON/Markdown" |

---

### K8s Investigation

**360-degree deep investigation for Kubernetes clusters and VPS servers.**

Orchestrates 12 elite tools for Root Cause Analysis, Kernel Performance, Runtime Security, and Pentesting.

#### The 12 Tools

| Category | Tools |
|----------|-------|
| Observability | Glances, Netdata, Popeye, K9s |
| Network & Tracing | Kubeshark, bpftrace |
| Vulnerability & Compliance | Trivy, Kubescape, kube-bench, Lynis |
| Active Defense | Falco, kube-hunter |

#### 4-Phase Workflow

1. **Observability & Health** — Metrics, cluster scan, context validation
2. **Network & Tracing** — L7 traffic analysis, kernel-level bottleneck tracing
3. **Vulnerability & Compliance** — CVE scanning, NSA/CIS benchmarks, OS hardening
4. **Active Defense & Runtime** — Runtime security events, internal pentest

#### Output

An interactive HTML report (`/tmp/investigation/ultimate_report.html`) with:
- Executive RCA tab
- Threat Intelligence dashboard
- Deep Performance metrics
- Runtime Security events
- Risk score 0-100

#### Key Files

- `generate_report.py` — 1048-line Python report generator with Chart.js
- `install_tools.sh` — Auto-installs 9 tools to `~/.local/bin`
- `k8s-playbook.md` — K8s triage and security reference (383 lines)
- `vps-playbook.md` — VPS/Linux investigation reference (431 lines)

---

### Learning Trail

**Validated learning paths with atomic resource verification.**

Generates structured learning trails in a "spine + nerves" pattern where every recommended resource is verified by reading/transcribing before inclusion.

#### Core Principle: Trust by Inspection

No static whitelists. Each resource is an atomic transaction: either inspected and approved, or it does not enter the trail.

#### 7-Phase Workflow

1. **Capture & Clarification** — Detect language, ask about customization
2. **Exploratory Mapping** — Broad web search (34+ candidates)
3. **Spine Design** — 4-10 stations based on topic type
4. **Atomic Resource Validation** — Mandatory fetch + extraction + validation
5. **Nerve Distribution** — 1-3 validated resources per station
6. **File Generation** — Saves to `./trilhas/{slug}.md` with YAML frontmatter
7. **Post-generation Conversation** — Offers practical project plan

#### Output Format

Markdown with:
- YAML frontmatter (metadata, DAG of prerequisites/next steps)
- Map visualization
- Sequential stations with validated nerves
- Boss final (5 socratic questions)
- Audit trail of validation process

---

### Pre-commit Quality Gate

**Auto-generated 14-step pre-commit pipelines for any tech stack.**

Shift-left quality gate that fingerprints a project's stack and generates a fail-fast pipeline with 14 ordered steps (cheap to expensive).

#### How It Works

1. **Fingerprint** — Scan for manifests, configs, conventions, CI pipelines
2. **Load Reference** — Match language-specific tool mappings
3. **Generate Pipeline** — Fill template with concrete tools
4. **Install & Verify** — Create `.githooks/`, chmod, dry-run

#### The 14 Steps

| # | Category | Purpose | Mode |
|---|----------|---------|------|
| -1 | Secret scanner | Gitleaks — credential leak prevention | fail |
| 0 | Branch name | Git Flow / trunk-based validation | fail |
| 1 | Formatter | Style normalization (gofmt, ruff, prettier) | fail |
| 2 | Linter | Static quality (golangci-lint, ruff, eslint) | fail |
| 3 | Security scan | Dependency vulnerabilities | fail |
| 4 | Dead code | Unreachable code detection | fail |
| 5 | Modernizer | Modern idioms (report-only) | warn |
| 6 | Convention guards | Team architectural rules | fail |
| 7 | Module hygiene | Lock files and manifest integrity | fail |
| 8 | Tests + coverage | Unit suite + threshold (90% default) | fail |
| 9 | Race/concurrency | Data races, async bugs | fail |
| 10 | Integration tests | End-to-end flows | fail |
| 11 | Mutation tests | Test suite quality | fail |
| 12 | Performance tests | Latency/throughput | fail |
| 13 | Schema pipeline | Stub regeneration | fail |
| 14 | Build validation | Production Dockerfile (OFF by default) | fail |

#### Supported Languages

- **Go** — gofmt, golangci-lint, govulncheck, deadcode, modernize, k6
- **Python** — ruff, mypy, bandit, safety, vulture, pytest, mutmut, locust
- **Node.js** — prettier, eslint, typescript, knip, jest/vitest, stryker, k6
- **Java** — google-java-format, checkstyle, spotbugs, OWASP, JaCoCo, pitest, gatling

---

## Project Structure

```
custom-skills/
├── README.md                           # This file
│
├── agent-code-detective/
│   ├── SKILL.md                        # Skill definition (270 lines)
│   └── references/
│       ├── breakpoint-cheatsheet.md    # Universal breakpoints
│       ├── debug-configs.md            # VSCode configurations
│       ├── dossier-template.md         # Investigation report template
│       └── tracing-setup.md            # mitmproxy/Langfuse/OTel guides
│
├── html-first/
│   ├── SKILL.md                        # Skill definition (187 lines)
│   ├── references/                     # 9 category references
│   └── templates/                      # 8 HTML templates
│
├── k8s-investigation/
│   ├── SKILL.md                        # Skill definition (59 lines)
│   ├── generate_report.py              # HTML report generator (1048 lines)
│   ├── install_tools.sh                # Tool auto-installer
│   ├── k8s-playbook.md                 # K8s investigation reference
│   └── vps-playbook.md                 # VPS/Linux reference
│
├── learning-trail/
│   ├── SKILL.md                        # Skill definition (423 lines)
│   ├── README.md                       # Installation docs
│   └── LICENSE.txt                     # MIT License
│
└── pre-commit-quality-gate/
    ├── SKILL.md                        # Skill definition (154 lines)
    ├── template.sh                     # Parameterized pipeline (178 lines)
    ├── pre-commit-quality-gate-doc.md  # Detailed documentation
    ├── go.md                           # Go tool mappings
    ├── python.md                       # Python tool mappings
    ├── nodejs.md                       # Node.js tool mappings
    └── java.md                         # Java tool mappings
```

---

## Architecture Principles

### 1. Fail-Fast Ordering
Cheap checks first, expensive last. The pre-commit pipeline runs secret scanning before mutation testing.

### 2. Trust by Inspection
Validate resources by reading them, not by reputation. The learning-trail skill verifies every URL before recommending.

### 3. Follow the Data
Read code by tracing execution flow, not top-to-bottom. The code-detective uses breakpoints, not line-by-line reading.

### 4. Single-File, Self-Contained
No external dependencies required for output artifacts. HTML templates work offline.

### 5. Soft-Skip Over Hard-Fail
Infrastructure-dependent steps warn instead of blocking. The pre-commit pipeline gracefully handles missing tools.

### 6. Atomic Transactions
Each recommendation either passes all validation steps or is rejected. No partial approvals.

---

## Contributing

Contributions are welcome! Here's how to add a new skill:

### 1. Fork & Clone

```bash
git clone https://github.com/josemalyson/custom-skills.git
cd custom-skills
```

### 2. Create Your Skill

```bash
mkdir my-new-skill
touch my-new-skill/SKILL.md
mkdir my-new-skill/references
```

### 3. Follow the Structure

```markdown
---
name: my-new-skill
description: >
  Trigger phrases that activate this skill.
  Be specific about when it should activate.
---

# My New Skill

## Overview
What this skill does and why it exists.

## Workflow
Phase-by-phase instructions.

## References
Links to supporting documents in references/ folder.
```

### 4. Submit a PR

- Add your skill folder
- Update this README's Skills Overview table
- Include at least one reference document
- Test with your target AI agent

---

## Roadmap

- [ ] Add `api-design` skill for REST/GraphQL API design patterns
- [ ] Add `database-optimization` skill for query tuning and schema design
- [ ] Add `testing-strategy` skill for test pyramid implementation
- [ ] Add `ci-cd-pipeline` skill for GitHub Actions/GitLab CI workflows
- [ ] Create a skill registry website for discovery
- [ ] Add skill versioning and compatibility matrix

---

## Frequently Asked Questions

### What AI agents are compatible?

These skills work with any LLM-based coding assistant that supports structured instructions:
- **Claude Code** (Anthropic) — native support
- **Custom harnesses** — adapt the SKILL.md format
- **GitHub Copilot** — with AGENTS.md integration
- **OpenAI Codex** — with instruction files

### Can I modify the skills?

Yes! Each skill is a self-contained Markdown file with references. Modify the workflow, add phases, or adjust trigger phrases to match your needs.

### Do I need to install all skills?

No. Install only the skills you need. Each skill is independent and can be used standalone.

### How do skills trigger?

Skills activate based on **trigger phrases** in the `description` field of the YAML frontmatter. When your prompt matches these phrases, the agent loads the skill automatically.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Acknowledgments

- **Thariq Shihipar** — "HTML is the new Markdown" thesis (Claude Code team, Anthropic)
- **Matt Pocock** — Engineering skills patterns and deep module vocabulary
- **The Open Source Community** — For inspiration from tools like Trivy, Kubescape, golangci-lint, and more

---

## Support

- **Issues**: [GitHub Issues](https://github.com/josemalyson/custom-skills/issues)
- **Pull Requests**: [GitHub PRs](https://github.com/josemalyson/custom-skills/pulls)
- **Discussions**: [GitHub Discussions](https://github.com/josemalyson/custom-skills/discussions)

---

<p align="center">
  <b>Built with care for the AI agent community</b>
</p>
