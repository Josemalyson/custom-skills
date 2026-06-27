# Debug Configurations — Templates prontos para uso

Configurações de debug para `launch.json` (VSCode) e equivalentes em outros editores.

## Por que isso importa

A diferença entre debugar um agente bem ou mal está em **conseguir entrar nas bibliotecas** que ele usa. LangChain, OpenAI SDK, Anthropic SDK fazem muita coisa por baixo dos panos. Se você não consegue passo a passo dentro delas, está vendo metade do filme.

---

## Python — VSCode (debugpy)

### Configuração mínima recomendada

Crie `.vscode/launch.json` na raiz do projeto:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Agent: Debug entry point",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/<CAMINHO_DO_ENTRY>.py",
      "args": ["<argumento de teste se necessário>"],
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
        "PYTHONBREAKPOINT": "debugpy.breakpoint",
        "LANGCHAIN_TRACING_V2": "true",
        "LANGCHAIN_VERBOSE": "true",
        "ANTHROPIC_LOG": "debug"
      }
    }
  ]
}
```

### Flags críticas explicadas

| Flag | Por que importa |
|---|---|
| `"justMyCode": false` | Permite step into bibliotecas (LangChain, openai, anthropic). **Sem isso, você não vê metade do fluxo.** |
| `"console": "integratedTerminal"` | Você consegue interagir com prompts de input do CLI |
| `LANGCHAIN_VERBOSE=true` | Loga cada chamada de chain/agent do LangChain |
| `ANTHROPIC_LOG=debug` | SDK da Anthropic loga request/response inteiros |

### Configuração para FastAPI

```json
{
  "name": "Agent: Debug FastAPI",
  "type": "debugpy",
  "request": "launch",
  "module": "uvicorn",
  "args": [
    "main:app",
    "--host", "127.0.0.1",
    "--port", "8000",
    "--reload"
  ],
  "jinja": true,
  "justMyCode": false
}
```

### Configuração para pytest (debugar testes do projeto)

```json
{
  "name": "Agent: Debug test",
  "type": "debugpy",
  "request": "launch",
  "module": "pytest",
  "args": ["${file}", "-vvs"],
  "justMyCode": false,
  "console": "integratedTerminal"
}
```

Use para entender o agente debugando os próprios testes do projeto — geralmente os melhores caminhos de entrada.

---

## TypeScript / Node.js — VSCode

### Para projetos com `tsx` (mais comum hoje)

```json
{
  "name": "Agent: Debug TS",
  "type": "node",
  "request": "launch",
  "runtimeArgs": ["--import", "tsx", "--inspect"],
  "program": "${workspaceFolder}/src/<ENTRY>.ts",
  "args": ["<argumento de teste>"],
  "skipFiles": [],
  "outFiles": ["${workspaceFolder}/dist/**/*.js"]
}
```

### Para projetos com Bun (OpenCode, Claude Code, etc.)

```json
{
  "name": "Agent: Debug Bun",
  "type": "bun",
  "request": "launch",
  "program": "${workspaceFolder}/src/<ENTRY>.ts",
  "args": [],
  "console": "integratedTerminal",
  "watchMode": false,
  "skipFiles": []
}
```

Requer a extensão "Bun" da Oven instalada no VSCode.

### Flags críticas

| Flag | Por que importa |
|---|---|
| `"skipFiles": []` | Vazio = não pular nenhum arquivo (inclusive `node_modules`) |
| `"--inspect"` | Habilita o protocolo de debug do V8 |
| `"runtimeArgs": ["--import", "tsx"]` | Roda TS direto sem compilar |

### Atalho: debugar pelo terminal externo

Às vezes mais simples — em vez de `launch.json`:

```bash
# Inicie com inspect
node --inspect-brk --import tsx src/main.ts

# Em outro terminal, ou no Chrome:
chrome://inspect → Configure → adicione localhost:9229
```

---

## Rust — VSCode (CodeLLDB)

Para projetos como `goose` (Block) ou `plandex`:

```json
{
  "name": "Agent: Debug Rust",
  "type": "lldb",
  "request": "launch",
  "cargo": {
    "args": ["build", "--bin=<NOME_DO_BINARIO>"],
    "filter": {
      "name": "<NOME_DO_BINARIO>",
      "kind": "bin"
    }
  },
  "args": [],
  "cwd": "${workspaceFolder}"
}
```

Requer a extensão CodeLLDB instalada.

---

## Go — VSCode (Delve)

```json
{
  "name": "Agent: Debug Go",
  "type": "go",
  "request": "launch",
  "mode": "debug",
  "program": "${workspaceFolder}/cmd/<binario>",
  "args": []
}
```

---

## Alternativas a VSCode

### PyCharm / IntelliJ

- Run/Debug Configuration → Python
- Em "Working directory" aponte para raiz do projeto
- Em "Environment variables" adicione `PYTHONBREAKPOINT=debugpy.breakpoint`
- **Não esqueça:** Settings → Build, Execution, Deployment → Python Debugger → marque **"Step into library code"** (equivalente ao `justMyCode: false`)

### Cursor / Continue.dev

Mesma configuração do VSCode — ambos usam `.vscode/launch.json`.

### CLI puro com `pdb` (sem IDE)

Quando estiver em servidor remoto ou container sem GUI:

```python
# Adicione na linha onde quer parar:
import pdb; pdb.set_trace()

# Ou em Python 3.7+:
breakpoint()
```

Para debugpy remoto:

```python
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()
debugpy.breakpoint()
```

E no VSCode use `"request": "attach"` em vez de `"launch"`.

---

## Variáveis de ambiente úteis para debug de agentes

Adicione no `.env` ou no `env` do launch.json para ganhar visibilidade:

```bash
# LangChain / LangGraph
LANGCHAIN_TRACING_V2=true
LANGCHAIN_VERBOSE=true
LANGCHAIN_API_KEY=...           # se quiser usar LangSmith
LANGCHAIN_PROJECT=local-debug

# Anthropic
ANTHROPIC_LOG=debug

# OpenAI
OPENAI_LOG=debug

# LiteLLM (multi-provider)
LITELLM_LOG=DEBUG

# Pydantic AI
LOGFIRE_TOKEN=...               # se usar Logfire
```

---

## Checklist antes de começar a debugar

- [ ] `.vscode/launch.json` criado
- [ ] `justMyCode: false` (Python) ou `skipFiles: []` (TS) configurado
- [ ] Variáveis de ambiente sensíveis configuradas (`.env`)
- [ ] API keys do provider configuradas (Anthropic, OpenAI)
- [ ] Python venv ativado / `npm install` executado
- [ ] Conseguiu rodar o projeto sem debugger primeiro (sanity check)

Sem o sanity check de rodar primeiro, você vai confundir bug de configuração com problema de código.
