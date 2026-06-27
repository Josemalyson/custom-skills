# Tracing Setup — Como capturar as chamadas HTTP do agente

Detalhamento das três opções de tracing mencionadas na Fase 5.

## Por que tracing é indispensável

Debug local mostra o **código rodando**. Tracing mostra a **conversa real entre seu agente e o LLM remoto**. São duas perspectivas complementares:

- Debug = perspectiva do harness
- Tracing = perspectiva da fronteira (sua API ↔ provider)

Você precisa das duas.

---

## Opção A — mitmproxy (universal, qualquer linguagem)

### Quando usar
- Projeto em linguagem que você não conhece bem
- Quer ver a request HTTP raw, sem filtro de biblioteca
- Quer capturar TODAS as requests (LLM, embeddings, web scraping, etc.)

### Instalação

```bash
# Via pip (recomendado)
pip install mitmproxy

# Via Homebrew (Mac)
brew install mitmproxy

# Via apt (Ubuntu/Debian)
sudo apt install mitmproxy
```

### Setup

1. Inicie o proxy com interface web:
   ```bash
   mitmweb --listen-port 8080
   ```

2. Em outro terminal, configure o agente para usar o proxy:
   ```bash
   export HTTPS_PROXY=http://localhost:8080
   export HTTP_PROXY=http://localhost:8080
   ```

3. **Crítico — instale o certificado SSL do mitmproxy:**
   ```bash
   # Após primeira execução, o cert estará em:
   ls ~/.mitmproxy/

   # Aponte o Python para ele:
   export SSL_CERT_FILE=~/.mitmproxy/mitmproxy-ca-cert.pem
   export REQUESTS_CA_BUNDLE=~/.mitmproxy/mitmproxy-ca-cert.pem

   # Para Node.js:
   export NODE_EXTRA_CA_CERTS=~/.mitmproxy/mitmproxy-ca-cert.pem
   ```

4. Abra a interface no navegador: `http://localhost:8081`

### Como usar

- Rode o agente normalmente. Cada request HTTPS aparece na interface.
- Filtre por `api.anthropic.com` ou `api.openai.com`.
- Clique em uma request para ver:
  - Headers
  - Body completo (JSON com messages, tools, system prompt)
  - Response com `stop_reason`, `content`, `usage`

### Truque útil — salvar todas as requests

```bash
mitmdump --listen-port 8080 -w /tmp/agent-session.mitm
```

Depois você pode replayar ou analisar offline:
```bash
mitmweb --listen-port 8080 -r /tmp/agent-session.mitm
```

### Filtros úteis no mitmweb

Na barra de filtros:
```
~u api.anthropic.com           # só Anthropic
~u "api\\.(anthropic|openai)"  # ambos
~m POST                        # só POSTs (chamadas LLM são POST)
```

---

## Opção B — Langfuse self-hosted

### Quando usar
- Projeto usa LangChain, LangGraph ou foi instrumentado para Langfuse
- Quer dashboard estruturado com árvore de invocação, custo, latência
- Vai usar continuamente, não só uma sessão

### Setup com Docker Compose

```bash
git clone https://github.com/langfuse/langfuse.git
cd langfuse
docker compose up -d
```

Acesse `http://localhost:3000`. Crie conta e organização.

### Configuração no projeto

Crie um projeto na UI do Langfuse e copie as chaves:

```bash
export LANGFUSE_PUBLIC_KEY=pk-lf-...
export LANGFUSE_SECRET_KEY=sk-lf-...
export LANGFUSE_HOST=http://localhost:3000
```

### Instrumentação automática para LangChain

Adicione 3 linhas ao código (ou via env vars se já é nativo):

```python
from langfuse.callback import CallbackHandler

handler = CallbackHandler()
# Use como callback em invokes
result = chain.invoke({"input": "..."}, config={"callbacks": [handler]})
```

### Instrumentação para SDK direto (Anthropic, OpenAI)

```python
from langfuse.openai import openai     # drop-in replacement
# ou
from langfuse.anthropic import Anthropic
```

### O que você vê no dashboard

- **Traces:** árvore completa de uma execução (chain → LLM → tool → chain)
- **Latência por step:** descobre onde o agente trava
- **Tokens por step:** custo real por etapa
- **Comparison view:** compare execuções do mesmo input com prompts diferentes
- **Sessions:** agrupa múltiplos traces da mesma conversa

### Equivalência LangSmith

Se o projeto já tem `LANGCHAIN_TRACING_V2=true`, ele vai mandar para LangSmith (cloud). Se você não tem conta paga, redirecione para Langfuse local — a API é parcialmente compatível.

---

## Opção C — OpenTelemetry (OTel)

### Quando usar
- Projeto já está instrumentado com OTel (cada vez mais comum)
- Quer integrar com observability stack existente (Grafana Tempo, Jaeger)
- Vai colocar em produção depois

### Setup mínimo com Grafana Tempo (local)

`docker-compose.yml`:

```yaml
services:
  tempo:
    image: grafana/tempo:latest
    command: ["-config.file=/etc/tempo.yaml"]
    volumes:
      - ./tempo.yaml:/etc/tempo.yaml
    ports:
      - "4317:4317"  # OTLP gRPC
      - "4318:4318"  # OTLP HTTP
      - "3200:3200"  # API

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
```

`tempo.yaml`:

```yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
        http:

storage:
  trace:
    backend: local
    local:
      path: /tmp/tempo/blocks
```

### Configurar o projeto para exportar

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_SERVICE_NAME=meu-agente
export OTEL_TRACES_EXPORTER=otlp
```

Se o projeto não está instrumentado, use auto-instrumentation:

```bash
# Python
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install
opentelemetry-instrument python entry.py
```

### Visualização

No Grafana (localhost:3001):
- Add Data Source → Tempo → URL: `http://tempo:3200`
- Explore → Tempo → Search traces

---

## Comparação rápida das três opções

| Critério | mitmproxy | Langfuse | OpenTelemetry |
|---|---|---|---|
| Setup time | 5 min | 15 min | 30 min |
| Linguagem-agnóstico | ✅ Total | ❌ Requer SDK | ✅ Padrão |
| Vê HTTP raw | ✅ | ❌ | ❌ |
| Dashboard com custo | ❌ | ✅ | Parcial |
| Árvore de invocação | ❌ | ✅ | ✅ |
| Boa para produção | ❌ | ✅ | ✅ |
| Boa para investigação ad-hoc | ✅ | ✅ | ✅ |

### Recomendação por cenário

- **"Quero entender o que está acontecendo agora":** mitmproxy
- **"Vou estudar esse projeto por semanas":** Langfuse
- **"Vou colocar isso em produção depois":** OpenTelemetry

---

## O que extrair dos traces (checklist)

Não importa qual ferramenta, capture estas informações:

- [ ] **Tamanho real do system prompt** (caracteres + tokens)
- [ ] **Total de tokens por turno** (input + output)
- [ ] **Latência por chamada LLM** (P50, P95)
- [ ] **Sequência de tool calls** (paralelas? sequenciais?)
- [ ] **Quantas iterações em média** (curto: 1-3, médio: 4-8, longo: 9+)
- [ ] **Taxa de erro de tools** (e o que o agente faz quando erra)
- [ ] **Distribuição de stop_reason** (`end_turn` vs `tool_use` vs `max_tokens`)

Esses números são o "perfil epidemiológico" do agente. Salve-os no Dossiê.

---

## Armadilhas comuns

**Certificado SSL falhando:**
A maior fonte de dor com mitmproxy. Sempre exporte os 3 env vars:
- `SSL_CERT_FILE`
- `REQUESTS_CA_BUNDLE`
- `NODE_EXTRA_CA_CERTS`

E confirme com `curl -x http://localhost:8080 https://api.anthropic.com` antes de rodar o agente.

**Langfuse com proxy/firewall:**
Em ambiente corporativo, garanta que `localhost:3000` está acessível e que o agente roda na mesma máquina.

**OTel exportando para o lugar errado:**
Se você tem `LANGCHAIN_TRACING_V2=true` E `OTEL_EXPORTER_OTLP_ENDPOINT` configurados, vai duplicar o tráfego. Escolha um.

**Esquecer de DESABILITAR proxy/tracing depois:**
Se você esquecer `HTTPS_PROXY` no env, requests subsequentes vão tentar passar pelo proxy. Sempre faça `unset HTTPS_PROXY` ao terminar.
