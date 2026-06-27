# K8s Investigation Playbook — Referência Completa

## Tabela de Conteúdo
1. [FASE 1 — Triage Detalhado](#fase-1)
2. [FASE 2 — Segurança Detalhada](#fase-2)
3. [Kubectl Cheat Sheet para Investigação](#kubectl)
4. [Interpretação de Resultados por Tool](#interpretacao)

---

## FASE 1 — Triage Detalhado {#fase-1}

### Popeye — Interpretação de Output

O Popeye usa um sistema de grades (A → F) e scores (0-100):

```
A (≥90): Cluster bem configurado
B (75-89): Pequenos ajustes necessários
C (60-74): Problemas moderados — atenção
D (45-59): Problemas graves — ação necessária
F (<45):  Cluster com sérios problemas de configuração
```

**Categorias de linters que o Popeye verifica:**
- `po` (Pods): liveness/readiness probes, resources limits, image tags
- `svc` (Services): selector mismatches, ports sem endpoint
- `cm` (ConfigMaps): ConfigMaps referenciados mas inexistentes
- `sec` (Secrets): Secrets referenciados mas inexistentes
- `dp` (Deployments): replicas, strategy, progress deadline
- `rs` (ReplicaSets): orphaned replicasets
- `ns` (Namespaces): namespaces vazios, status
- `no` (Nodes): pressão de memória, disco, PID
- `rb/clusterroles` (RBAC): bindings com sujeitos inválidos

**Extrair findings críticos:**
```bash
# Só issues com severity >= WARNING
cat /tmp/investigation/triage/popeye_report.json | jq '
  .sanitizers[] |
  select(.issues != null) |
  {
    resource: .sanitizer,
    critical: [.issues[] | select(.level >= 3)],
    warnings: [.issues[] | select(.level == 2)]
  } |
  select((.critical | length) > 0 or (.warnings | length) > 0)
'
```

### K8s State Snapshot — Queries Importantes

```bash
# Pods não-running (CrashLoopBackOff, Pending, OOMKilled, etc.)
kubectl get pods --all-namespaces \
  --field-selector='status.phase!=Running' \
  -o json | jq '
  .items[] |
  {
    namespace: .metadata.namespace,
    name: .metadata.name,
    phase: .status.phase,
    reason: .status.containerStatuses[]?.state.waiting?.reason,
    restarts: .status.containerStatuses[]?.restartCount
  }
' > /tmp/investigation/triage/problematic_pods.json

# Nodes com condições anômalas
kubectl get nodes -o json | jq '
  .items[] |
  {
    name: .metadata.name,
    ready: (.status.conditions[] | select(.type=="Ready") | .status),
    conditions: [.status.conditions[] |
      select(.status != "False" and .type != "Ready" and .status != "Unknown") |
      {type, status, reason, message}
    ],
    allocatable: .status.allocatable,
    capacity: .status.capacity
  }
' > /tmp/investigation/triage/nodes_status.json

# Events de warning das últimas 2 horas
kubectl get events --all-namespaces \
  --field-selector='type=Warning' \
  --sort-by='.lastTimestamp' \
  -o json | jq '
  .items[] |
  select(.lastTimestamp > (now - 7200 | todate)) |
  {
    namespace: .metadata.namespace,
    name: .involvedObject.name,
    kind: .involvedObject.kind,
    reason: .reason,
    message: .message,
    count: .count,
    lastTimestamp: .lastTimestamp
  }
' > /tmp/investigation/triage/recent_warnings.json

# HPA sem targets (possível problema de metrics)
kubectl get hpa --all-namespaces -o json | jq '
  .items[] |
  select(.status.currentMetrics == null) |
  {namespace: .metadata.namespace, name: .metadata.name, status: .status}
' 2>/dev/null

# PVCs em estado não-Bound
kubectl get pvc --all-namespaces -o json | jq '
  .items[] | select(.status.phase != "Bound") |
  {namespace: .metadata.namespace, name: .metadata.name, phase: .status.phase}
'

# Services sem Endpoints
kubectl get endpoints --all-namespaces -o json | jq '
  .items[] |
  select(.subsets == null or .subsets == []) |
  {namespace: .metadata.namespace, name: .metadata.name}
'
```

### Análise de Resource Requests vs Limits

```bash
# Pods sem resource limits definidos — risco de OOM e CPU starvation
kubectl get pods --all-namespaces -o json | jq '
  .items[] | .spec.containers[] as $c |
  select($c.resources.limits == null or $c.resources.limits == {}) |
  {
    namespace: (.metadata.namespace),
    pod: (.metadata.name),
    container: $c.name,
    issue: "NO_LIMITS_DEFINED"
  }
' > /tmp/investigation/triage/pods_no_limits.json

# Namespace resource quotas e consumo atual
kubectl get resourcequota --all-namespaces -o json | jq '
  .items[] |
  {
    namespace: .metadata.namespace,
    name: .metadata.name,
    hard: .spec.hard,
    used: .status.used
  }
'
```

---

## FASE 2 — Segurança Detalhada {#fase-2}

### Trivy — Estratégia de Scan

**Priorização de imagens a escanear:**
```bash
# Listar todas as imagens únicas no cluster
kubectl get pods --all-namespaces -o jsonpath='{range .items[*]}{range .spec.containers[*]}{.image}{"\n"}{end}{end}' | \
  sort | uniq > /tmp/investigation/security/cluster_images.txt

# Escanear cada imagem individualmente (para clusters pequenos)
while IFS= read -r image; do
  sanitized=$(echo "$image" | tr '/:' '_')
  trivy image --format json \
    --output "/tmp/investigation/security/trivy_image_${sanitized}.json" \
    "$image" 2>/dev/null
done < /tmp/investigation/security/cluster_images.txt
```

**Extrair CVEs CRITICAL:**
```bash
cat /tmp/investigation/security/trivy_cluster.json | jq '
  .Results[]? |
  .Vulnerabilities[]? |
  select(.Severity == "CRITICAL") |
  {
    pkg: .PkgName,
    cve: .VulnerabilityID,
    installed: .InstalledVersion,
    fixed: .FixedVersion,
    score: .CVSS.nvd.V3Score,
    description: .Title
  }
' | jq -s 'sort_by(-.score) | .[0:20]' \
  > /tmp/investigation/security/trivy_critical_cves.json
```

### Kubescape — Análise por Control

```bash
# Listar controles com FAIL
cat /tmp/investigation/security/kubescape_report.json | jq '
  .Results[]? |
  select(.StatusInfo.status == "failed") |
  {
    control_id: .ControlID,
    name: .Name,
    severity: .Severity,
    resources_failed: (.AssociatedData | length),
    remediation: .Remediation
  }
' | jq -s 'sort_by(-.severity)' \
  > /tmp/investigation/security/kubescape_failed_controls.json

# RBAC analysis
kubescape scan control C-0015,C-0035,C-0036,C-0037,C-0063 \
  --format json --output /tmp/investigation/security/kubescape_rbac.json
```

### kube-bench — Parsing de Resultados

```bash
# Extrair só os FAILs
cat /tmp/investigation/security/kubebench_report.json | jq '
  .Controls[]? |
  .tests[]? |
  .results[]? |
  select(.status == "FAIL") |
  {
    test_number: .test_number,
    description: .test_desc,
    status: .status,
    remediation: .remediation,
    section: .section
  }
' > /tmp/investigation/security/kubebench_fails.json

# Sumário por seção
cat /tmp/investigation/security/kubebench_report.json | jq '
  {
    total_pass: [.Controls[]?.tests[]?.results[]? | select(.status=="PASS")] | length,
    total_fail: [.Controls[]?.tests[]?.results[]? | select(.status=="FAIL")] | length,
    total_warn: [.Controls[]?.tests[]?.results[]? | select(.status=="WARN")] | length
  }
'
```

### Falco — Análise de Eventos

```bash
# Parsear eventos por prioridade
# Formato: timestamp priority rule output
cat /tmp/investigation/security/falco_events.json | \
  python3 -c "
import sys, json, re
events = []
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        # Falco JSON format
        e = json.loads(line)
        events.append({
            'time': e.get('time', ''),
            'priority': e.get('priority', 'unknown'),
            'rule': e.get('rule', ''),
            'output': e.get('output', ''),
            'hostname': e.get('hostname', '')
        })
    except:
        pass

# Agrupar por regra
from collections import Counter
by_rule = Counter(e['rule'] for e in events)
critical = [e for e in events if e['priority'] in ('Critical', 'Error')]

print(json.dumps({
    'total_events': len(events),
    'by_priority': dict(Counter(e['priority'] for e in events)),
    'top_rules': by_rule.most_common(10),
    'critical_events': critical[:20]
}, indent=2))
" > /tmp/investigation/security/falco_summary.json
```

### RBAC Analysis Manual

```bash
# ClusterRoleBindings para cluster-admin
kubectl get clusterrolebindings -o json | jq '
  .items[] |
  select(.roleRef.name == "cluster-admin") |
  {
    binding: .metadata.name,
    subjects: .subjects,
    issue: "CLUSTER_ADMIN_BINDING"
  }
' > /tmp/investigation/security/rbac_cluster_admin.json

# ServiceAccounts com permissões excessivas
kubectl get clusterrolebindings,rolebindings --all-namespaces -o json | \
  jq '[.items[] | select(.subjects[]?.kind == "ServiceAccount")]' \
  > /tmp/investigation/security/rbac_sa_bindings.json

# Secrets acessíveis por ServiceAccounts
kubectl get serviceaccounts --all-namespaces -o json | jq '
  .items[] |
  select(.secrets | length > 5) |
  {namespace: .metadata.namespace, name: .metadata.name, secret_count: (.secrets | length)}
'
```

---

## Kubectl Cheat Sheet para Investigação {#kubectl}

```bash
# Ver logs de um pod com timestamp
kubectl logs <pod> -n <ns> --timestamps --since=1h

# Exec em pod problemático
kubectl exec -it <pod> -n <ns> -- /bin/sh

# Debug com imagem ephemeral
kubectl debug -it <pod> --image=busybox --target=<container>

# Ver todos os eventos relacionados a um pod
kubectl describe pod <pod> -n <ns> | grep -A 20 "Events:"

# Port-forward para investigação local
kubectl port-forward svc/<service> 8080:80 -n <ns>

# Forçar redeploy (útil após fix de config)
kubectl rollout restart deployment/<name> -n <ns>

# Ver recursos sem helm/kustomize
kubectl get all,cm,secret,ing,pvc,sa,rb,crb -n <ns>

# Network policy analysis
kubectl get networkpolicies --all-namespaces -o yaml

# Verificar se metrics-server está respondendo
kubectl top nodes
kubectl top pods --all-namespaces --sort-by=memory
```

---

## Interpretação de Resultados por Tool {#interpretacao}

### Popeye Score Guide

```
Score 95-100: Produção saudável
Score 80-94:  Atenção a alguns items, não crítico
Score 60-79:  Revisão necessária antes de novo deploy
Score 40-59:  Problemas que impactam estabilidade
Score < 40:   Cluster em risco — ação imediata
```

### Kubescape Risk Score Guide

```
0-30:   Alto Risco
31-60:  Risco Médio
61-80:  Risco Baixo-Médio
81-100: Postura Segura
```

### kube-bench Sections

```
Section 1: Control Plane Components
Section 2: Etcd
Section 3: Control Plane Configuration
Section 4: Worker Nodes
Section 5: Kubernetes Policies
```

### Falco Priority Levels

```
Emergency → Pânico — sistema comprometido
Alert     → Ação imediata necessária
Critical  → Evento crítico de segurança
Error     → Erro que requer atenção
Warning   → Comportamento suspeito
Notice    → Evento de segurança normal mas significativo
Info      → Informacional
Debug     → Debug only
```
