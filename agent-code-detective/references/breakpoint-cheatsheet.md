# Breakpoint Cheatsheet — Os 5 BPs Universais

Detalhamento de cada breakpoint usado na Fase 4 (Vigilância ao vivo).

## Visão geral

| # | Nome | Localização típica | Pergunta que responde |
|---|---|---|---|
| BP1 | Entrada | Entry point — função que recebe input | "Como o input chega?" |
| BP2 | Saída para LLM | Linha do `client.messages.create()` | "O que o agente diz ao modelo?" |
| BP3 | Retorno do LLM | Imediatamente após chamada LLM | "O que o modelo decidiu?" |
| BP4 | Execução de tool | Função real da tool | "O que a tool faz com o que o LLM pediu?" |
| BP5 | Decisão de parada | `if stop_reason == "..."` ou similar | "Por que o loop terminou?" |

---

## BP1 — Entrada (Entry point)

### Onde colocar
- **CLI:** primeira linha após receber `args` ou `input`
- **HTTP:** primeira linha do handler da rota
- **WebSocket:** primeira linha do handler de mensagem

### Variáveis a inspecionar
- `user_input` ou `message` — conteúdo, tipo, formato
- `session_id` ou `conversation_id` — sessão nova ou retomada?
- Headers/metadata da request (se HTTP)
- Estado inicial: histórico vazio ou carregado?

### Perguntas a responder
1. O input chega como string pura ou objeto estruturado?
2. Há pré-processamento antes de virar uma `Message`?
3. A sessão é stateful (continua de onde parou) ou stateless?

---

## BP2 — Saída para o LLM

### Onde colocar
A linha que faz a chamada HTTP para o provider. Padrões comuns:

```python
# Anthropic
response = client.messages.create(...)

# OpenAI
response = client.chat.completions.create(...)

# LangChain
response = llm.invoke(messages)
response = await llm.ainvoke(messages)

# Google
response = client.models.generate_content(...)
```

### Variáveis a inspecionar
- `messages` — **lista completa** sendo enviada (system + user + assistant + tool_result)
- `tools` — definições JSON Schema de cada tool disponível
- `system` — system prompt resolvido (variáveis interpoladas)
- `model` — qual modelo, qual versão (`claude-sonnet-4`, `gpt-4o`, etc.)
- `temperature`, `max_tokens`, `top_p` — hiperparâmetros
- `stop_sequences` (se houver)

### Perguntas a responder
1. Quão grande é o `messages` array? (cresce a cada iteração)
2. O system prompt é o mesmo a cada turno ou muda dinamicamente?
3. Todas as tools são enviadas sempre, ou há filtro contextual?
4. Quantos tokens estima-se que está indo? (use `tiktoken` ou similar)

### Dica avançada
Copie o JSON completo dessa request em um arquivo. Você pode replayá-la via `curl` direto na API para entender o comportamento isoladamente do código.

---

## BP3 — Retorno do LLM

### Onde colocar
Imediatamente após a linha de BP2. Se a chamada é `await`, coloque logo após.

### Variáveis a inspecionar
- `response.stop_reason` ou `response.choices[0].finish_reason`
  - `end_turn` / `stop` — modelo terminou normalmente
  - `tool_use` / `tool_calls` — modelo quer chamar tool(s)
  - `max_tokens` — bateu limite
  - `stop_sequence` — bateu sequência de parada
- `response.content` — blocos de texto + blocos de tool_use
- `response.usage.input_tokens` / `output_tokens` — custo real
- `response.id` — identificador único da chamada

### Perguntas a responder
1. Quais tipos de blocos vêm em `content`? (text, tool_use, thinking)
2. Quando o LLM escolhe tool_use, ele pede 1 ou N tools de uma vez?
3. O custo (tokens) está dentro do esperado?

### Observação crítica
Quando `stop_reason == "tool_use"`, **o LLM não executou nada**. Ele só decidiu o que pedir. O harness é quem vai executar (próximo passo: BP4).

---

## BP4 — Execução de tool

### Onde colocar
Dentro da função que **realmente executa** a tool. Atenção: pode haver várias camadas:

```
agent_loop.execute_tool_call(tool_use_block)
  └─> tool_registry.dispatch(name, input)
       └─> tool_function(input)   ← AQUI é BP4
```

Procure por padrões:
```python
# LangChain
@tool
def my_function(...): ← BP4 dentro
    
# Pydantic AI
@agent.tool_plain
def my_function(...): ← BP4 dentro

# Function calling manual
def execute_tool(name, args):
    if name == "x":
        return x_implementation(args) ← BP4 dentro
```

### Variáveis a inspecionar
- `tool_name` — qual tool foi escolhida
- `tool_input` — parâmetros que o LLM gerou (dict/JSON)
- Estado do mundo antes da execução (se relevante: filesystem, DB)
- `tool_result` — o que volta (após a função executar)
- Tempo de execução da tool

### Perguntas a responder
1. Os parâmetros que o LLM gerou são válidos? Há validação (Pydantic)?
2. O resultado retorna como string, dict, ou objeto estruturado?
3. Se a tool falhar, o erro é capturado e retornado ao LLM como `tool_result`?
4. A tool tem side effects (escrita em disco, DB)? São idempotentes?

### Dica de ouro
Esta é a fronteira mais perigosa de um agente. Toda exploit de prompt injection acontece aqui. Veja como a tool valida o input antes de executar comandos do "mundo real".

---

## BP5 — Decisão de parada do loop

### Onde colocar
A linha que decide se o loop continua ou termina. Padrões comuns:

```python
# Padrão A — checagem de stop_reason
if response.stop_reason == "end_turn":
    break    ← BP5

# Padrão B — contador de iterações
if iteration >= max_iterations:
    break    ← BP5

# Padrão C — flag de done
while not state.done:    ← BP5
    ...

# LangGraph
def should_continue(state) -> str:
    if state.messages[-1].tool_calls:    ← BP5
        return "continue"
    return "end"
```

### Variáveis a inspecionar
- Contador atual de iterações vs limite
- `stop_reason` da última resposta
- Estado interno (`done`, `finished`, `complete`)
- Mensagens acumuladas no histórico

### Perguntas a responder
1. Há limite máximo de iterações? Qual?
2. O que acontece se atingir o limite? (warning? exception? trunca?)
3. Há condições de stop além de `end_turn`? (ex: detectar loop infinito)
4. Como o estado é resetado entre sessões diferentes?

### Sintoma de problema
Se você nunca chega em BP5 com `end_turn`, o agente está iterando até o limite — geralmente sinal de prompt mal calibrado ou tool retornando erro permanente.

---

## Padrão de uso completo dos 5 BPs

Execução típica de um teste com 1 tool:

```
BP1  → input chega
       ↓
BP2  → primeira chamada LLM (com tools disponíveis)
       ↓
BP3  → LLM retorna stop_reason = "tool_use"
       ↓
BP4  → tool executa, retorna resultado
       ↓
BP5  → checa: continuar? sim, pois ainda há tool_result a ser processado
       ↓
BP2  → segunda chamada LLM (agora com tool_result no histórico)
       ↓
BP3  → LLM retorna stop_reason = "end_turn"
       ↓
BP5  → checa: continuar? não, sai do loop
       ↓
       resposta final ao usuário
```

Esse fluxo de 7 pontos é o "DNA" de qualquer agente moderno.

---

## Como saber se você posicionou os BPs corretamente

Após executar Teste 1 (sem tool):
- BP1: 1 hit
- BP2: 1 hit
- BP3: 1 hit
- BP4: 0 hits
- BP5: 1 hit

Após Teste 2 (1 tool):
- BP1: 1 hit
- BP2: 2 hits
- BP3: 2 hits
- BP4: 1 hit
- BP5: 2 hits

Após Teste 3 (3 tools em sequência):
- BP1: 1 hit
- BP2: 4 hits
- BP3: 4 hits
- BP4: 3 hits
- BP5: 4 hits

Se os números não baterem, seus breakpoints estão no lugar errado — refaça a localização.
