# VPS / Linux Server Investigation Playbook — Referência Completa

## Tabela de Conteúdo
1. [Segurança — Lynis + rkhunter](#seguranca)
2. [Performance — Netdata + bpftrace + sysstat](#performance)
3. [Análise de Processos e Rede](#processos-rede)
4. [Investigação de Incidentes Ativos](#incidentes)
5. [Hardening Checklist](#hardening)

---

## Segurança {#seguranca}

### Lynis — Audit Completo

```bash
# Instalar (se necessário)
apt-get install lynis -y  # Debian/Ubuntu
yum install lynis -y      # RHEL/CentOS

# Rodar audit completo (silencioso, sem interação)
lynis audit system \
  --quick \
  --no-colors \
  --quiet \
  --log-file /tmp/investigation/security/lynis.log \
  --report-file /tmp/investigation/security/lynis.dat \
  2>&1 | tee /tmp/investigation/security/lynis_output.txt

# Extrair métricas chave
HARDENING_INDEX=$(grep "Hardening index" /tmp/investigation/security/lynis_output.txt | awk '{print $NF}')
echo "Hardening Index: $HARDENING_INDEX"

# Extrair warnings estruturados
grep -E "^\[WARNING\]|\! " /tmp/investigation/security/lynis_output.txt | \
  python3 -c "
import sys, json
warnings = []
for line in sys.stdin:
    line = line.strip()
    if line.startswith('[WARNING]') or line.startswith('!'):
        warnings.append(line.lstrip('[WARNING]!').strip())
print(json.dumps({'warnings': warnings, 'count': len(warnings)}))
" > /tmp/investigation/security/lynis_warnings.json

# Extrair sugestões de hardening
grep "Suggestion" /tmp/investigation/security/lynis.log | \
  awk -F'|' '{print $2}' | sort | uniq \
  > /tmp/investigation/security/lynis_suggestions.txt
```

**Categorias de checks do Lynis:**
- `BOOT` — Bootloader security
- `AUTH` — Authentication mechanisms (PAM, sudo, SSH)
- `CRYPT` — Cryptography (SSL/TLS, LUKS)
- `FIRE` — Firewall (iptables, nftables, ufw)
- `KRNL` — Kernel hardening (sysctl)
- `LOGG` — Logging (auditd, syslog)
- `NETW` — Network configuration
- `PKGS` — Package updates e vulnerabilidades
- `PROC` — Running processes
- `STRG` — Storage e filesystems
- `USRS` — Users e grupos

**Score de Hardening:**
```
0-34:   Hardening Baixo — servidor vulnerável
35-64:  Hardening Médio — melhorias necessárias
65-84:  Hardening Bom — configuração sólida
85-100: Hardening Excelente — bem endurecido
```

### SSH Security Audit

```bash
# Verificar configurações críticas do SSH
python3 -c "
import re, json

issues = []
with open('/etc/ssh/sshd_config', 'r') as f:
    config = f.read()

checks = {
    'PermitRootLogin': ('yes', 'CRITICAL: Root login permitido via SSH'),
    'PasswordAuthentication': ('yes', 'HIGH: Autenticação por senha habilitada'),
    'PermitEmptyPasswords': ('yes', 'CRITICAL: Senhas vazias permitidas'),
    'X11Forwarding': ('yes', 'MEDIUM: X11 Forwarding habilitado'),
    'Protocol': ('1', 'HIGH: Protocolo SSH v1 em uso'),
    'MaxAuthTries': (None, 'MEDIUM: MaxAuthTries não definido'),
}

for param, (bad_value, message) in checks.items():
    match = re.search(rf'^{param}\s+(\S+)', config, re.MULTILINE | re.IGNORECASE)
    if bad_value is None and not match:
        issues.append({'param': param, 'issue': message, 'severity': message.split(':')[0]})
    elif match and (bad_value and match.group(1).lower() == bad_value.lower()):
        issues.append({'param': param, 'value': match.group(1), 'issue': message, 'severity': message.split(':')[0]})

print(json.dumps({'ssh_issues': issues}, indent=2))
" > /tmp/investigation/security/ssh_audit.json
```

### Usuários e Autenticação

```bash
# Usuários com shell de login (potencialmente perigoso)
getent passwd | awk -F: '$7 !~ /nologin|false|sync/ {print $1":"$3":"$6":"$7}' \
  > /tmp/investigation/security/users_with_shell.txt

# Usuários com UID 0 (root equivalente)
awk -F: '($3 == "0") {print $1}' /etc/passwd \
  > /tmp/investigation/security/uid0_users.txt

# Sudo permissions
cat /etc/sudoers 2>/dev/null | grep -v "^#\|^$" \
  > /tmp/investigation/security/sudo_config.txt

# Verificar SUID/SGID em binários (potencial escalação de privilégio)
find / -perm -4000 -o -perm -2000 2>/dev/null | \
  grep -v proc | sort \
  > /tmp/investigation/security/suid_sgid_files.txt

# Contas com senha em branco
awk -F: '($2 == "" || $2 == "!") {print $1}' /etc/shadow 2>/dev/null \
  > /tmp/investigation/security/empty_password_users.txt
```

### Firewall e Rede

```bash
# Estado do firewall
{
  echo "=== UFW ==="
  ufw status verbose 2>/dev/null
  echo "=== IPTABLES ==="
  iptables -L -n -v 2>/dev/null
  echo "=== NFTABLES ==="
  nft list ruleset 2>/dev/null
} > /tmp/investigation/security/firewall_status.txt

# Portas abertas e processos ouvindo
ss -tlnp > /tmp/investigation/security/listening_ports.txt
# Formato: State Recv-Q Send-Q Local-Address:Port Peer-Address:Port Process

# Conexões estabelecidas (detectar conexões suspeitas)
ss -tnp state established > /tmp/investigation/security/active_connections.txt

# Verificar se há portas abertas inesperadamente
ss -tlnp | grep -v '127.0.0.1\|::1' | \
  awk 'NR>1 {print $4, $6}' | sort \
  > /tmp/investigation/security/external_ports.txt
```

---

## Performance {#performance}

### Netdata — Coleta de Métricas

```bash
NETDATA="http://localhost:19999/api/v1"

# Lista de charts disponíveis
curl -s "${NETDATA}/charts" | jq '[.charts | keys[] | select(startswith("system."))]' \
  > /tmp/investigation/performance/netdata_charts.json

# Coleta das métricas principais (últimos 60 minutos)
for chart in system.cpu system.ram system.io system.net system.load; do
  sanitized="${chart//./_}"
  curl -s "${NETDATA}/data?chart=${chart}&points=60&format=json" \
    > "/tmp/investigation/performance/netdata_${sanitized}.json"
done

# Alertas ativos
curl -s "${NETDATA}/alarms?active" \
  > /tmp/investigation/performance/netdata_alarms.json

# Anomaly rates (se disponível)
curl -s "${NETDATA}/data?chart=anomaly_detection.anomaly_rate&points=60&format=json" \
  > /tmp/investigation/performance/netdata_anomaly.json 2>/dev/null

echo "Netdata metrics collected."
```

### bpftrace — Scripts de Investigação

**CPU Profiling:**
```bash
# Flame graph data (30 segundos de CPU profiling)
timeout 30 bpftrace -e '
  profile:hz:99 { @[kstack, ustack, comm] = count(); }
  END { print(@); }
' > /tmp/investigation/performance/bpftrace_cpu_profile.txt 2>/dev/null

# Top funções do kernel por tempo de execução
timeout 30 bpftrace -e '
  kprobe:* { @start[tid, func] = nsecs; }
  kretprobe:* /@start[tid, func]/
  { @us[func] = sum((nsecs - @start[tid, func])/1000);
    delete(@start[tid, func]); }
  END { print(@us); clear(@us); }
' > /tmp/investigation/performance/bpftrace_kernel_funcs.txt 2>/dev/null
```

**Disk I/O Investigation:**
```bash
# Latência de leitura por processo (histograma)
timeout 60 bpftrace -e '
  tracepoint:block:block_rq_issue { @start[args->dev, args->sector] = nsecs; }
  tracepoint:block:block_rq_complete
  /@start[args->dev, args->sector]/
  {
    @latency_ms[comm] = hist((nsecs - @start[args->dev, args->sector]) / 1000000);
    delete(@start[args->dev, args->sector]);
  }
' > /tmp/investigation/performance/bpftrace_disk_latency.txt 2>/dev/null

# Arquivos mais acessados
timeout 30 bpftrace -e '
  tracepoint:syscalls:sys_enter_openat { @[str(args->filename), comm] = count(); }
  END { print(@); }
' 2>/dev/null | sort -rn -k3 | head -20 \
  > /tmp/investigation/performance/bpftrace_top_files.txt
```

**Network Investigation:**
```bash
# Conexões novas por processo (30 segundos)
timeout 30 bpftrace -e '
  tracepoint:syscalls:sys_enter_connect {
    @[comm, pid] = count();
  }
' > /tmp/investigation/performance/bpftrace_connects.txt 2>/dev/null

# Bytes enviados por processo
timeout 30 bpftrace -e '
  tracepoint:syscalls:sys_enter_sendto {
    @bytes_sent[comm] = sum(args->len);
  }
  tracepoint:syscalls:sys_enter_recvfrom {
    @bytes_recv[comm] = sum(args->len);
  }
' > /tmp/investigation/performance/bpftrace_network_bytes.txt 2>/dev/null
```

**Memory Investigation:**
```bash
# OOM events
timeout 30 bpftrace -e '
  tracepoint:oom:mark_victim {
    printf("OOM VICTIM: pid=%d comm=%s\n", args->pid, str(args->comm));
    @victims[str(args->comm)] = count();
  }
' > /tmp/investigation/performance/bpftrace_oom.txt 2>/dev/null

# Page faults por processo
timeout 30 bpftrace -e '
  software:page-faults:1 { @[comm] = count(); }
  END { print(@); }
' > /tmp/investigation/performance/bpftrace_pagefaults.txt 2>/dev/null
```

### Glances — Snapshot Detalhado

```bash
# Exportar para JSON (modo não-interativo)
python3 -c "
try:
    import glances_api
    # Via API se servidor já rodando
    import urllib.request, json
    data = json.loads(urllib.request.urlopen('http://localhost:61208/api/3/all').read())
    with open('/tmp/investigation/performance/glances_full.json', 'w') as f:
        json.dump(data, f, indent=2)
    print('Glances API collected')
except:
    print('Glances API not available, using CLI snapshot')
" 2>/dev/null

# Fallback: coleta manual dos dados equivalentes
python3 -c "
import json, subprocess, os, time

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except:
        return ''

data = {
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
    'uptime': run('uptime'),
    'cpu': run('mpstat 1 1 | tail -1'),
    'memory': run('free -m'),
    'disk': run('df -h'),
    'load': run('cat /proc/loadavg'),
    'top_cpu': run('ps aux --sort=-%cpu | head -11'),
    'top_mem': run('ps aux --sort=-%mem | head -11'),
    'network': run('ss -s'),
    'io': run('iostat -x 1 2 | tail -n +4'),
}

with open('/tmp/investigation/performance/system_snapshot.json', 'w') as f:
    json.dump(data, f, indent=2)

print('System snapshot collected')
"
```

---

## Análise de Processos e Rede {#processos-rede}

```bash
# Processos com maior consumo de recursos
ps aux --sort=-%cpu | head -20 > /tmp/investigation/performance/top_cpu_procs.txt
ps aux --sort=-%mem | head -20 > /tmp/investigation/performance/top_mem_procs.txt

# Processos órfãos (PPID=1 mas não esperado)
ps --ppid 1 -o pid,ppid,comm,args | grep -v -E "systemd|init|kernel|kthreadd"

# Análise de memória do sistema
cat /proc/meminfo > /tmp/investigation/performance/meminfo.txt
cat /proc/vmstat > /tmp/investigation/performance/vmstat.txt

# I/O wait por dispositivo
iostat -x 1 5 > /tmp/investigation/performance/iostat.txt

# Verificar processos que mais usam swap
for pid in $(ls /proc | grep -E '^[0-9]+$'); do
  swap=$(grep VmSwap /proc/$pid/status 2>/dev/null | awk '{print $2}')
  if [ ! -z "$swap" ] && [ "$swap" != "0" ]; then
    comm=$(cat /proc/$pid/comm 2>/dev/null)
    echo "$swap KB - $comm (PID: $pid)"
  fi
done | sort -rn | head -10 > /tmp/investigation/performance/swap_usage.txt

# Arquivos deletados ainda abertos (file descriptor leak)
lsof 2>/dev/null | grep deleted | head -30 \
  > /tmp/investigation/performance/deleted_open_files.txt
```

---

## Investigação de Incidentes Ativos {#incidentes}

```bash
# Últimas entradas nos logs de sistema
journalctl -n 500 --no-pager -p err \
  > /tmp/investigation/security/journal_errors.txt

# Verificar logins recentes e falhas
last -n 50 > /tmp/investigation/security/recent_logins.txt
lastb -n 50 2>/dev/null > /tmp/investigation/security/failed_logins.txt

# Auth log
grep -E "Failed|Invalid|error|Warning" /var/log/auth.log 2>/dev/null | \
  tail -100 > /tmp/investigation/security/auth_issues.txt

# Verificar scheduled tasks suspeitas
crontab -l 2>/dev/null > /tmp/investigation/security/user_crontab.txt
ls /etc/cron* /var/spool/cron 2>/dev/null >> /tmp/investigation/security/user_crontab.txt

# Módulos do kernel carregados (detectar rootkits)
lsmod | sort > /tmp/investigation/security/kernel_modules.txt

# Integrity de binários críticos (checksums)
for bin in /bin/ps /bin/ls /bin/netstat /usr/bin/ss /sbin/iptables; do
  if [ -f "$bin" ]; then
    sha256sum "$bin"
  fi
done > /tmp/investigation/security/binary_checksums.txt
```

---

## Hardening Checklist Automatizado {#hardening}

```bash
# Gerar checklist de hardening rápido
python3 -c "
import os, subprocess, json

def check(cmd, description, expected=True):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        passed = (result.returncode == 0) == expected
        return {'check': description, 'status': 'PASS' if passed else 'FAIL', 'output': result.stdout.strip()[:200]}
    except Exception as e:
        return {'check': description, 'status': 'ERROR', 'output': str(e)}

checks = [
    ('grep -i \"PermitRootLogin no\" /etc/ssh/sshd_config', 'SSH: PermitRootLogin desabilitado'),
    ('grep -i \"PasswordAuthentication no\" /etc/ssh/sshd_config', 'SSH: PasswordAuthentication desabilitado'),
    ('systemctl is-active ufw || systemctl is-active firewalld', 'Firewall ativo'),
    ('sysctl kernel.dmesg_restrict | grep -q 1', 'Kernel: dmesg_restrict=1'),
    ('sysctl net.ipv4.ip_forward | grep -q 0', 'Kernel: ip_forward desabilitado'),
    ('sysctl kernel.randomize_va_space | grep -q 2', 'Kernel: ASLR habilitado (nivel 2)'),
    ('systemctl is-active fail2ban', 'Fail2ban ativo'),
    ('systemctl is-active auditd', 'Auditd ativo'),
    ('[ -n \"\$(find /tmp -perm -4000 2>/dev/null)\" ]', 'Sem SUID em /tmp', False),
    ('sysctl net.ipv4.conf.all.accept_source_route | grep -q 0', 'Source routing desabilitado'),
    ('sysctl net.ipv4.conf.default.rp_filter | grep -q 1', 'Reverse path filtering ativo'),
    ('sysctl net.ipv4.icmp_ignore_bogus_error_responses | grep -q 1', 'ICMP bogus responses ignoradas'),
    ('grep -q \"^TMOUT\" /etc/profile /etc/bash.bashrc 2>/dev/null', 'Session timeout configurado'),
    ('grep -q \"^net.core.bpf_jit_harden=2\" /etc/sysctl.d/*.conf /etc/sysctl.conf 2>/dev/null', 'BPF JIT hardening'),
]

results = [check(cmd, desc, exp if len(c:=(cmd, desc, exp)) == 3 else True) for cmd, desc, *exp_list in [(c[0], c[1], *([c[2]] if len(c)==3 else [True])) for c in [(cmd, desc) + ((expected,) if 'expected' in dir() else ()) for cmd, desc in [(cmd, desc) for cmd, desc, *_ in checks]]] for expected in ([exp_list[0]] if exp_list else [True])]

# Simpler approach:
results = []
for item in checks:
    cmd, desc = item[0], item[1]
    expected = item[2] if len(item) > 2 else True
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
    passed = (result.returncode == 0) == expected
    results.append({'check': desc, 'status': 'PASS' if passed else 'FAIL'})

summary = {'passed': sum(1 for r in results if r['status']=='PASS'),
           'failed': sum(1 for r in results if r['status']=='FAIL'),
           'checks': results}

with open('/tmp/investigation/security/hardening_checklist.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f\"Hardening checks: {summary['passed']} PASS, {summary['failed']} FAIL\")
"
```
