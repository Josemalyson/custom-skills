#!/usr/bin/env python3
"""
K8s + VPS Investigation Report Generator
Consolida todos os outputs das ferramentas de investigação em um relatório HTML interativo.

Uso:
    python3 generate_report.py \
        --input-dir /tmp/investigation \
        --output /tmp/investigation/final_report.html \
        --cluster-name "prod-cluster" \
        --environment "production" \
        --investigator "joao.silva"
"""

import argparse
import json
import os
import sys
import re
import datetime
from pathlib import Path
from collections import defaultdict, Counter


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADERS — Cada função carrega e normaliza um artefato
# ─────────────────────────────────────────────────────────────────────────────

def safe_load_json(path):
    """Carrega JSON com fallback gracioso."""
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def safe_read_text(path):
    """Lê texto com fallback gracioso."""
    try:
        with open(path) as f:
            return f.read()
    except Exception:
        return ""


def load_popeye(input_dir):
    data = safe_load_json(f"{input_dir}/triage/popeye_report.json")
    if not data:
        return {"available": False}

    issues = []
    total = 0
    sanitizers = data.get("sanitizers", [])
    for s in sanitizers:
        for issue in (s.get("issues") or []):
            total += 1
            level = issue.get("level", 0)
            severity = ["INFO", "OK", "LOW", "MEDIUM", "HIGH", "CRITICAL"][min(level, 5)]
            issues.append({
                "tool": "Popeye",
                "resource": s.get("sanitizer", ""),
                "message": issue.get("message", ""),
                "severity": severity,
                "group": issue.get("group", ""),
            })

    return {
        "available": True,
        "score": data.get("score", 0),
        "grade": data.get("grade", "?"),
        "total_issues": total,
        "issues": issues,
    }


def load_trivy(input_dir):
    data = safe_load_json(f"{input_dir}/security/trivy_cluster.json")
    if not data:
        return {"available": False}

    findings = []
    severity_counts = Counter()

    results = data.get("Results") or []
    for finding in data.get("Findings", []):
        results.extend(finding.get("Results", []))
        
    for result in results:
        for vuln in (result.get("Vulnerabilities") or []):
            sev = vuln.get("Severity", "UNKNOWN")
            severity_counts[sev] += 1
            if sev in ("CRITICAL", "HIGH"):
                findings.append({
                    "tool": "Trivy",
                    "type": "vulnerability",
                    "cve": vuln.get("VulnerabilityID", ""),
                    "package": vuln.get("PkgName", ""),
                    "installed": vuln.get("InstalledVersion", ""),
                    "fixed": vuln.get("FixedVersion", "N/A"),
                    "severity": sev,
                    "title": vuln.get("Title", ""),
                    "target": result.get("Target", ""),
                })
        for misc in (result.get("Misconfigurations") or []):
            sev = misc.get("Severity", "UNKNOWN")
            severity_counts[sev] += 1
            findings.append({
                "tool": "Trivy",
                "type": "misconfiguration",
                "id": misc.get("ID", ""),
                "title": misc.get("Title", ""),
                "severity": sev,
                "message": misc.get("Message", ""),
                "resolution": misc.get("Resolution", ""),
                "target": result.get("Target", ""),
            })

    return {
        "available": True,
        "severity_counts": dict(severity_counts),
        "top_findings": sorted(findings, key=lambda x: ["CRITICAL","HIGH","MEDIUM","LOW","UNKNOWN"].index(x["severity"]) if x["severity"] in ["CRITICAL","HIGH","MEDIUM","LOW","UNKNOWN"] else 99)[:30],
        "total": sum(severity_counts.values()),
    }


def load_kubescape(input_dir):
    data = safe_load_json(f"{input_dir}/security/kubescape_report.json")
    if not data:
        return {"available": False}

    summary = data.get("summaryDetails", {})
    controls_summary = summary.get("controlsSummary", {})

    failed_controls = []
    for result in (data.get("Results") or []):
        if result.get("StatusInfo", {}).get("status") == "failed":
            failed_controls.append({
                "id": result.get("ControlID", ""),
                "name": result.get("Name", ""),
                "severity": result.get("Severity", ""),
                "remediation": result.get("Remediation", ""),
                "resources_failed": len(result.get("AssociatedData") or []),
            })

    return {
        "available": True,
        "risk_score": summary.get("score", 0),
        "failed_count": controls_summary.get("failedCount", len(failed_controls)),
        "passed_count": controls_summary.get("passedCount", 0),
        "failed_controls": failed_controls[:20],
    }


def load_kubebench(input_dir):
    text = safe_read_text(f"{input_dir}/security/kubebench_report.json")
    if not text:
        return {"available": False}

    fails = []
    warns = []
    passes = 0

    # Parse JSON output
    try:
        data = json.loads(text)
        for control in (data.get("Controls") or []):
            for test in (control.get("tests") or []):
                for result in (test.get("results") or []):
                    status = result.get("status", "")
                    if status == "FAIL":
                        fails.append({
                            "number": result.get("test_number", ""),
                            "description": result.get("test_desc", ""),
                            "remediation": result.get("remediation", ""),
                            "section": control.get("text", ""),
                        })
                    elif status == "WARN":
                        warns.append(result.get("test_desc", ""))
                    elif status == "PASS":
                        passes += 1
    except Exception:
        # Fallback: parse text output
        for line in text.split("\n"):
            if line.strip().startswith("[FAIL]"):
                fails.append({"description": line.replace("[FAIL]", "").strip(), "number": "", "remediation": "", "section": ""})
            elif line.strip().startswith("[WARN]"):
                warns.append(line.replace("[WARN]", "").strip())
            elif line.strip().startswith("[PASS]"):
                passes += 1

    return {
        "available": True,
        "total_fail": len(fails),
        "total_warn": len(warns),
        "total_pass": passes,
        "fails": fails[:20],
        "warns": warns[:10],
    }


def load_falco(input_dir):
    text = safe_read_text(f"{input_dir}/security/falco_events.json")
    summary_data = safe_load_json(f"{input_dir}/security/falco_summary.json")

    if summary_data:
        return {"available": True, **summary_data}

    if not text:
        return {"available": False}

    events = []
    for line in text.strip().split("\n"):
        try:
            e = json.loads(line)
            events.append(e)
        except Exception:
            pass

    by_priority = Counter(e.get("priority", "unknown") for e in events)
    top_rules = Counter(e.get("rule", "") for e in events).most_common(10)
    critical_events = [e for e in events if e.get("priority") in ("Critical", "Error")][:10]

    return {
        "available": True,
        "total_events": len(events),
        "by_priority": dict(by_priority),
        "top_rules": top_rules,
        "critical_events": critical_events,
    }


def load_lynis(input_dir):
    text = safe_read_text(f"{input_dir}/security/lynis_output.txt")
    warnings_data = safe_load_json(f"{input_dir}/security/lynis_warnings.json")

    if not text and not warnings_data:
        return {"available": False}

    hardening_index = 0
    match = re.search(r'Hardening index\s*:\s*(\d+)', text or "")
    if match:
        hardening_index = int(match.group(1))

    warnings = (warnings_data or {}).get("warnings", [])
    if not warnings:
        warnings = re.findall(r'!\s+(.+)', text or "")

    suggestions = []
    sugg_text = safe_read_text(f"{input_dir}/security/lynis_suggestions.txt")
    if sugg_text:
        suggestions = [s.strip() for s in sugg_text.split("\n") if s.strip()][:15]

    return {
        "available": True,
        "hardening_index": hardening_index,
        "hardening_grade": "EXCELLENT" if hardening_index >= 85 else "GOOD" if hardening_index >= 65 else "MEDIUM" if hardening_index >= 35 else "LOW",
        "warnings": warnings[:20],
        "suggestions": suggestions,
    }


def load_kubehunter(input_dir):
    data = safe_load_json(f"{input_dir}/security/kubehunter_report.json")
    if not data:
        return {"available": False}

    vulnerabilities = data.get("vulnerabilities", [])
    hunter_data = data.get("hunter_statistics", [])

    return {
        "available": True,
        "vulnerabilities": vulnerabilities[:15],
        "total": len(vulnerabilities),
        "hunters_run": len(hunter_data),
    }


def load_netdata(input_dir):
    alarms = safe_load_json(f"{input_dir}/performance/netdata_alarms.json")
    cpu_data = safe_load_json(f"{input_dir}/performance/netdata_system_cpu.json")

    if not alarms and not cpu_data:
        return {"available": False}

    active_alarms = []
    if alarms:
        for name, alarm in (alarms.get("alarms") or {}).items():
            if alarm.get("status") not in ("CLEAR", "UNDEFINED"):
                active_alarms.append({
                    "name": name,
                    "status": alarm.get("status"),
                    "chart": alarm.get("chart"),
                    "value": alarm.get("value"),
                    "units": alarm.get("units"),
                })

    return {
        "available": True,
        "active_alarms": active_alarms,
        "total_alarms": len(active_alarms),
    }


def load_bpftrace(input_dir):
    syscalls = safe_read_text(f"{input_dir}/performance/bpftrace_syscalls.txt")
    disk = safe_read_text(f"{input_dir}/performance/bpftrace_disk_latency.txt")
    network = safe_read_text(f"{input_dir}/performance/bpftrace_network.txt")

    if not syscalls and not disk:
        return {"available": False}

    return {
        "available": True,
        "syscalls_summary": syscalls[:2000] if syscalls else "Not available",
        "disk_latency": disk[:2000] if disk else "Not available",
        "network_summary": network[:1000] if network else "Not available",
    }


def load_system_snapshot(input_dir):
    snapshot = safe_load_json(f"{input_dir}/performance/system_snapshot.json")
    if snapshot:
        return {"available": True, **snapshot}
    return {"available": False}


def compute_risk_score(findings):
    """Calcula risk score geral de 0-100 (100 = mais seguro)."""
    weights = {"CRITICAL": 15, "HIGH": 8, "MEDIUM": 3, "LOW": 1}
    penalty = 0
    counts = Counter()

    for f in findings:
        sev = f.get("severity", "INFO")
        counts[sev] += 1
        penalty += weights.get(sev, 0)

    score = max(0, 100 - min(penalty, 100))
    return score, dict(counts)


def classify_severity(counts):
    if counts.get("CRITICAL", 0) > 0:
        return "CRITICAL", "#dc2626"
    elif counts.get("HIGH", 0) > 0:
        return "HIGH", "#ea580c"
    elif counts.get("MEDIUM", 0) > 0:
        return "MEDIUM", "#d97706"
    elif counts.get("LOW", 0) > 0:
        return "LOW", "#65a30d"
    return "INFO", "#2563eb"


# ─────────────────────────────────────────────────────────────────────────────
# HTML REPORT GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_html(data, args):
    popeye = data["popeye"]
    trivy = data["trivy"]
    kubescape = data["kubescape"]
    kubebench = data["kubebench"]
    falco = data["falco"]
    lynis = data["lynis"]
    kubehunter = data["kubehunter"]
    netdata = data["netdata"]
    bpftrace = data["bpftrace"]
    snapshot = data["snapshot"]

    all_findings = []
    if trivy.get("available"):
        all_findings.extend(trivy.get("top_findings", []))
    if popeye.get("available"):
        all_findings.extend(popeye.get("issues", []))

    risk_score, sev_counts = compute_risk_score(all_findings)
    overall_status, status_color = classify_severity(sev_counts)

    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    def sev_badge(sev):
        colors = {
            "CRITICAL": "#dc2626", "HIGH": "#ea580c",
            "MEDIUM": "#d97706", "LOW": "#65a30d", "INFO": "#2563eb"
        }
        c = colors.get(sev, "#6b7280")
        return f'<span class="badge" style="background:{c}">{sev}</span>'

    def tool_status(tool_data, name):
        if tool_data.get("available"):
            return f'<span class="tool-ok">✓ {name}</span>'
        return f'<span class="tool-miss">✗ {name} (não disponível)</span>'

    def escape(s):
        return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

    # Build findings table rows
    findings_rows = ""
    sorted_findings = sorted(
        all_findings,
        key=lambda x: ["CRITICAL","HIGH","MEDIUM","LOW","INFO","UNKNOWN"].index(x.get("severity","UNKNOWN")) if x.get("severity","UNKNOWN") in ["CRITICAL","HIGH","MEDIUM","LOW","INFO","UNKNOWN"] else 99
    )[:50]

    for f in sorted_findings:
        msg = escape(f.get("title") or f.get("message") or f.get("description", ""))[:120]
        findings_rows += f"""
        <tr>
            <td>{sev_badge(f.get('severity','?'))}</td>
            <td><code>{escape(f.get('tool',''))}</code></td>
            <td>{escape(f.get('type','') or f.get('resource',''))}</td>
            <td>{escape(f.get('cve','') or f.get('id','') or '-')}</td>
            <td title="{msg}">{msg[:80]}{'...' if len(msg)>80 else ''}</td>
        </tr>
        """

    # Kubescape failed controls rows
    ks_rows = ""
    for c in kubescape.get("failed_controls", []):
        ks_rows += f"""
        <tr>
            <td><code>{escape(c.get('id',''))}</code></td>
            <td>{escape(c.get('name',''))}</td>
            <td>{sev_badge('HIGH' if c.get('severity',0) >= 7 else 'MEDIUM')}</td>
            <td>{c.get('resources_failed',0)}</td>
            <td title="{escape(c.get('remediation',''))}">{escape(c.get('remediation',''))[:100]}...</td>
        </tr>
        """

    # kube-bench fails rows
    kb_rows = ""
    for f in kubebench.get("fails", []):
        kb_rows += f"""
        <tr>
            <td><code>{escape(f.get('number',''))}</code></td>
            <td>{escape(f.get('section',''))}</td>
            <td>{escape(f.get('description',''))}</td>
            <td class="small-text">{escape(f.get('remediation',''))[:150]}</td>
        </tr>
        """

    # Falco events rows
    falco_rules_rows = ""
    for rule, count in (falco.get("top_rules") or []):
        falco_rules_rows += f"""
        <tr>
            <td>{escape(rule)}</td>
            <td><strong>{count}</strong></td>
        </tr>
        """

    # Lynis warnings rows
    lynis_rows = ""
    for w in lynis.get("warnings", []):
        lynis_rows += f"<li>{escape(w)}</li>"

    # Popeye summary rows
    popeye_rows = ""
    issues_by_resource = defaultdict(list)
    for issue in popeye.get("issues", []):
        issues_by_resource[issue.get("resource","")].append(issue)
    for resource, issues in list(issues_by_resource.items())[:15]:
        high = sum(1 for i in issues if i["severity"] in ("CRITICAL","HIGH"))
        med = sum(1 for i in issues if i["severity"] == "MEDIUM")
        low = sum(1 for i in issues if i["severity"] in ("LOW","INFO"))
        popeye_rows += f"""
        <tr>
            <td><code>{escape(resource)}</code></td>
            <td>{len(issues)}</td>
            <td><span style="color:#dc2626">{high}</span> / <span style="color:#d97706">{med}</span> / <span style="color:#65a30d">{low}</span></td>
        </tr>
        """

    # Netdata alarms rows
    nd_rows = ""
    for alarm in netdata.get("active_alarms", []):
        nd_rows += f"""
        <tr>
            <td>{sev_badge('HIGH' if alarm.get('status') == 'CRITICAL' else 'MEDIUM')}</td>
            <td>{escape(alarm.get('name',''))}</td>
            <td><code>{escape(alarm.get('chart',''))}</code></td>
            <td>{escape(alarm.get('value',''))} {escape(alarm.get('units',''))}</td>
        </tr>
        """

    # Kubehunter rows
    kh_rows = ""
    for vuln in kubehunter.get("vulnerabilities", []):
        kh_rows += f"""
        <tr>
            <td>{sev_badge(vuln.get('severity','HIGH').upper())}</td>
            <td>{escape(vuln.get('vulnerability',''))}</td>
            <td>{escape(vuln.get('location',''))}</td>
            <td class="small-text">{escape(str(vuln.get('evidence',''))[:100])}</td>
        </tr>
        """

    # Quick wins / roadmap
    quick_wins = []
    medium_term = []
    long_term = []

    if trivy.get("severity_counts", {}).get("CRITICAL", 0) > 0:
        quick_wins.append("🔴 Atualizar imagens com CVEs CRITICAL (trivy scan detectou vulnerabilidades críticas)")
    if kubebench.get("total_fail", 0) > 5:
        quick_wins.append("🔴 Aplicar remediações do kube-bench (falhas no CIS Kubernetes Benchmark)")
    if popeye.get("grade", "A") in ("D", "F"):
        quick_wins.append("🟠 Corrigir misconfigurations identificadas pelo Popeye (grade " + popeye.get("grade","?") + ")")
    if lynis.get("hardening_index", 100) < 50:
        quick_wins.append("🟠 Aplicar hardening básico de sistema (Lynis score: " + str(lynis.get("hardening_index", 0)) + "/100)")

    if not falco.get("available"):
        medium_term.append("📦 Instalar Falco para runtime security detection contínua")
    if not kubehunter.get("available"):
        medium_term.append("🔍 Executar kube-hunter para pentesting do cluster (requer autorização)")
    if kubescape.get("risk_score", 100) < 60:
        medium_term.append("🔒 Implementar controles do Kubescape (risk score: " + str(kubescape.get("risk_score",0)) + ")")

    long_term.append("📊 Implementar stack de observabilidade completa (Prometheus + Grafana + Loki)")
    long_term.append("🛡️ Implementar Network Policies para micro-segmentação de namespaces")
    long_term.append("🔐 Habilitar OPA/Gatekeeper para policy enforcement em admission control")
    long_term.append("🔑 Implementar rotação automática de secrets (External Secrets Operator + Vault)")

    quick_wins_html = "\n".join(f"<li>{w}</li>" for w in quick_wins) or "<li>Nenhum item crítico identificado ✓</li>"
    medium_html = "\n".join(f"<li>{w}</li>" for w in medium_term)
    long_html = "\n".join(f"<li>{w}</li>" for w in long_term)

    # Tools status bar
    tools_html = " | ".join([
        tool_status(popeye, "Popeye"),
        tool_status(trivy, "Trivy"),
        tool_status(kubescape, "Kubescape"),
        tool_status(kubebench, "kube-bench"),
        tool_status(falco, "Falco"),
        tool_status(lynis, "Lynis"),
        tool_status(kubehunter, "kube-hunter"),
        tool_status(netdata, "Netdata"),
        tool_status(bpftrace, "bpftrace"),
    ])

    # Trivy severity chart data
    trivy_counts = trivy.get("severity_counts", {})
    trivy_chart_data = json.dumps({
        "labels": ["CRITICAL","HIGH","MEDIUM","LOW"],
        "values": [
            trivy_counts.get("CRITICAL", 0),
            trivy_counts.get("HIGH", 0),
            trivy_counts.get("MEDIUM", 0),
            trivy_counts.get("LOW", 0),
        ],
        "colors": ["#dc2626","#ea580c","#d97706","#65a30d"]
    })

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Investigation Report — {escape(args.cluster_name)}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  :root {{
    --bg: #0f172a; --surface: #1e293b; --surface2: #334155;
    --text: #e2e8f0; --text-muted: #94a3b8; --border: #475569;
    --accent: #3b82f6; --critical: #dc2626; --high: #ea580c;
    --medium: #d97706; --low: #65a30d; --ok: #22c55e;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; font-size: 14px; line-height: 1.6; }}
  .header {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-bottom: 1px solid var(--border); padding: 24px 32px; position: sticky; top: 0; z-index: 100; }}
  .header h1 {{ font-size: 22px; font-weight: 700; color: #f1f5f9; }}
  .header .meta {{ font-size: 12px; color: var(--text-muted); margin-top: 4px; }}
  .nav {{ display: flex; gap: 8px; margin-top: 16px; flex-wrap: wrap; }}
  .nav a {{ color: var(--text-muted); text-decoration: none; padding: 4px 12px; border-radius: 20px; border: 1px solid var(--border); font-size: 12px; transition: all .2s; }}
  .nav a:hover {{ background: var(--surface2); color: var(--text); }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 24px 32px; }}
  .section {{ margin-bottom: 40px; }}
  .section-title {{ font-size: 18px; font-weight: 700; color: #f1f5f9; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; border-left: 4px solid var(--accent); padding-left: 12px; }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 16px; }}
  .card-title {{ font-size: 14px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: .05em; margin-bottom: 12px; }}
  .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
  .grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}
  @media (max-width: 900px) {{ .grid-3, .grid-2 {{ grid-template-columns: 1fr; }} }}
  .score-circle {{ display: flex; flex-direction: column; align-items: center; justify-content: center; width: 120px; height: 120px; border-radius: 50%; margin: 0 auto 12px; font-size: 32px; font-weight: 800; }}
  .metric-big {{ font-size: 36px; font-weight: 800; }}
  .metric-label {{ font-size: 12px; color: var(--text-muted); margin-top: 4px; }}
  .badge {{ display: inline-block; color: white; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; letter-spacing: .04em; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: left; padding: 10px 12px; color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: .05em; border-bottom: 1px solid var(--border); }}
  td {{ padding: 10px 12px; border-bottom: 1px solid var(--surface2); vertical-align: top; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: var(--surface2); }}
  code {{ background: var(--surface2); padding: 1px 6px; border-radius: 4px; font-family: 'Cascadia Code', 'Fira Code', monospace; font-size: 12px; color: #93c5fd; }}
  pre {{ background: #020617; padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 12px; color: #94a3b8; line-height: 1.8; border: 1px solid var(--border); white-space: pre-wrap; word-break: break-word; }}
  .tool-ok {{ color: var(--ok); font-size: 12px; }}
  .tool-miss {{ color: var(--text-muted); font-size: 12px; }}
  .tools-bar {{ background: var(--surface2); padding: 10px 16px; border-radius: 8px; display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 24px; }}
  .progress-bar {{ background: var(--surface2); border-radius: 100px; height: 8px; overflow: hidden; margin-top: 8px; }}
  .progress-fill {{ height: 100%; border-radius: 100px; transition: width .5s; }}
  .status-bar {{ display: flex; align-items: center; gap: 12px; padding: 16px; border-radius: 10px; border-left: 4px solid; margin-bottom: 24px; }}
  details {{ margin-top: 8px; }}
  summary {{ cursor: pointer; color: var(--accent); font-size: 13px; }}
  summary:hover {{ color: #60a5fa; }}
  ul {{ list-style: disc; padding-left: 20px; }}
  li {{ margin-bottom: 6px; }}
  .small-text {{ font-size: 11px; color: var(--text-muted); }}
  .chart-container {{ position: relative; height: 200px; }}
  .flex-center {{ display: flex; align-items: center; justify-content: center; gap: 24px; }}
  .separator {{ margin: 32px 0; border: none; border-top: 1px solid var(--border); }}
</style>
</head>
<body>

<div class="header">
  <h1>🔭 Investigation Report — {escape(args.cluster_name)}</h1>
  <div class="meta">
    Environment: <strong>{escape(args.environment)}</strong> &nbsp;|&nbsp;
    Generated: <strong>{ts}</strong> &nbsp;|&nbsp;
    Investigator: <strong>{escape(args.investigator)}</strong>
  </div>
  <nav class="nav">
    <a href="#summary">Executive Summary</a>
    <a href="#triage">Triage</a>
    <a href="#security">Segurança</a>
    <a href="#performance">Performance</a>
    <a href="#findings">Findings</a>
    <a href="#roadmap">Roadmap</a>
  </nav>
</div>

<div class="container">

  <!-- Tools Status Bar -->
  <div class="tools-bar">
    {tools_html}
  </div>

  <!-- ────────────────────────────────────────────────────────── -->
  <!-- 1. EXECUTIVE SUMMARY                                       -->
  <!-- ────────────────────────────────────────────────────────── -->
  <section class="section" id="summary">
    <h2 class="section-title">📊 Executive Summary</h2>

    <div class="status-bar" style="background: rgba({'220,38,38' if overall_status == 'CRITICAL' else '234,88,12' if overall_status == 'HIGH' else '217,119,6' if overall_status == 'MEDIUM' else '34,197,94'},.1); border-color: {status_color}">
      <div>
        <div style="font-size:24px; font-weight:800; color:{status_color}">{overall_status}</div>
        <div class="metric-label">Overall Risk Level</div>
      </div>
      <div style="flex:1"></div>
      <div style="text-align:center">
        <div class="metric-big" style="color:{status_color}">{risk_score}</div>
        <div class="metric-label">Security Score / 100</div>
      </div>
    </div>

    <div class="grid-3">
      <div class="card" style="text-align:center">
        <div class="card-title">Critical Findings</div>
        <div class="metric-big" style="color:var(--critical)">{sev_counts.get('CRITICAL',0)}</div>
        <div class="metric-label">Ação imediata necessária</div>
      </div>
      <div class="card" style="text-align:center">
        <div class="card-title">High Findings</div>
        <div class="metric-big" style="color:var(--high)">{sev_counts.get('HIGH',0)}</div>
        <div class="metric-label">Resolver esta sprint</div>
      </div>
      <div class="card" style="text-align:center">
        <div class="card-title">Medium + Low</div>
        <div class="metric-big" style="color:var(--medium)">{sev_counts.get('MEDIUM',0) + sev_counts.get('LOW',0)}</div>
        <div class="metric-label">Backlog técnico</div>
      </div>
    </div>

    <div class="grid-3">
      <div class="card" style="text-align:center">
        <div class="card-title">Popeye Grade</div>
        <div class="metric-big" style="color:{'#dc2626' if popeye.get('grade','F') in ('D','F') else '#d97706' if popeye.get('grade','?') == 'C' else '#22c55e'}">{popeye.get('grade', 'N/A')}</div>
        <div class="metric-label">Cluster Health (score: {popeye.get('score', 'N/A')})</div>
      </div>
      <div class="card" style="text-align:center">
        <div class="card-title">Kubescape Risk</div>
        <div class="metric-big" style="color:{'#dc2626' if kubescape.get('risk_score',100) < 30 else '#d97706' if kubescape.get('risk_score',100) < 60 else '#22c55e'}">{kubescape.get('risk_score', 'N/A')}</div>
        <div class="metric-label">Risk Score (100 = seguro)</div>
      </div>
      <div class="card" style="text-align:center">
        <div class="card-title">Lynis Hardening</div>
        <div class="metric-big" style="color:{'#22c55e' if lynis.get('hardening_index',0) >= 65 else '#d97706' if lynis.get('hardening_index',0) >= 35 else '#dc2626'}">{lynis.get('hardening_index', 'N/A')}</div>
        <div class="metric-label">Hardening Index ({lynis.get('hardening_grade','N/A')})</div>
      </div>
    </div>
  </section>

  <hr class="separator">

  <!-- ────────────────────────────────────────────────────────── -->
  <!-- 2. TRIAGE                                                  -->
  <!-- ────────────────────────────────────────────────────────── -->
  <section class="section" id="triage">
    <h2 class="section-title">🔍 Triage — Health Check</h2>

    <div class="grid-2">
      <!-- Popeye -->
      <div class="card">
        <div class="card-title">Popeye — Cluster Sanitizer</div>
        {'<p style="color:var(--text-muted)">Ferramenta não disponível</p>' if not popeye.get('available') else f"""
        <div class="flex-center" style="justify-content:flex-start; gap:24px; margin-bottom:12px">
          <div style="text-align:center">
            <div style="font-size:48px; font-weight:900; color:{'#dc2626' if popeye.get('grade') in ('D','F') else '#d97706' if popeye.get('grade') == 'C' else '#22c55e'}">{popeye.get('grade','?')}</div>
            <div class="metric-label">Grade</div>
          </div>
          <div>
            <div class="metric-big">{popeye.get('total_issues',0)}</div>
            <div class="metric-label">Total Issues</div>
          </div>
        </div>
        <table>
          <thead><tr><th>Resource</th><th>Total</th><th>C/H / M / L</th></tr></thead>
          <tbody>{popeye_rows}</tbody>
        </table>
        """}
      </div>

      <!-- kube-bench summary -->
      <div class="card">
        <div class="card-title">kube-bench — CIS Benchmark</div>
        {'<p style="color:var(--text-muted)">Ferramenta não disponível</p>' if not kubebench.get('available') else f"""
        <div class="flex-center" style="gap:32px; margin-bottom:16px">
          <div style="text-align:center">
            <div class="metric-big" style="color:var(--ok)">{kubebench.get('total_pass',0)}</div>
            <div class="metric-label">PASS</div>
          </div>
          <div style="text-align:center">
            <div class="metric-big" style="color:var(--critical)">{kubebench.get('total_fail',0)}</div>
            <div class="metric-label">FAIL</div>
          </div>
          <div style="text-align:center">
            <div class="metric-big" style="color:var(--medium)">{kubebench.get('total_warn',0)}</div>
            <div class="metric-label">WARN</div>
          </div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" style="width:{int(kubebench.get('total_pass',0)/(kubebench.get('total_pass',0)+kubebench.get('total_fail',1))*100)}%; background:var(--ok)"></div>
        </div>
        <div class="small-text" style="margin-top:6px">Compliance: {int(kubebench.get('total_pass',0)/(kubebench.get('total_pass',0)+kubebench.get('total_fail',1)+1)*100)}%</div>
        """}
      </div>
    </div>
  </section>

  <hr class="separator">

  <!-- ────────────────────────────────────────────────────────── -->
  <!-- 3. SECURITY                                                -->
  <!-- ────────────────────────────────────────────────────────── -->
  <section class="section" id="security">
    <h2 class="section-title">🛡️ Auditoria de Segurança</h2>

    <!-- Trivy -->
    <div class="card">
      <div class="card-title">Trivy — Vulnerabilities & Misconfigurations</div>
      {'<p style="color:var(--text-muted)">Ferramenta não disponível</p>' if not trivy.get('available') else f"""
      <div class="grid-2">
        <div>
          <div class="chart-container">
            <canvas id="trivyChart"></canvas>
          </div>
        </div>
        <div>
          <table>
            <thead><tr><th>Severity</th><th>Count</th></tr></thead>
            <tbody>
              {''.join(f'<tr><td>{sev_badge(sev)}</td><td><strong>{trivy_counts.get(sev,0)}</strong></td></tr>' for sev in ['CRITICAL','HIGH','MEDIUM','LOW'])}
            </tbody>
          </table>
        </div>
      </div>
      <details style="margin-top:16px">
        <summary>Ver Top {len(trivy.get('top_findings',[]))} findings (CRITICAL + HIGH)</summary>
        <table style="margin-top:10px">
          <thead><tr><th>Sev</th><th>CVE/ID</th><th>Package</th><th>Installed</th><th>Fixed In</th><th>Target</th></tr></thead>
          <tbody>{''.join(f"<tr><td>{sev_badge(f.get('severity','?'))}</td><td><code>{escape(f.get('cve','') or f.get('id',''))}</code></td><td>{escape(f.get('package','') or f.get('title','')[:40])}</td><td><code>{escape(f.get('installed',''))}</code></td><td><code style='color:var(--ok)'>{escape(f.get('fixed','N/A'))}</code></td><td class='small-text'>{escape(f.get('target',''))[:50]}</td></tr>" for f in trivy.get('top_findings',[]))}</tbody>
        </table>
      </details>
      """}
    </div>

    <!-- Kubescape -->
    <div class="card">
      <div class="card-title">Kubescape — Compliance & Risk Scoring</div>
      {'<p style="color:var(--text-muted)">Ferramenta não disponível</p>' if not kubescape.get('available') else f"""
      <div style="margin-bottom:16px">
        <div style="display:flex; gap:24px; align-items:center">
          <div>
            <div class="metric-big" style="color:{'#dc2626' if kubescape.get('risk_score',100) < 30 else '#d97706' if kubescape.get('risk_score',100) < 60 else '#22c55e'}">{kubescape.get('risk_score','N/A')}</div>
            <div class="metric-label">Risk Score</div>
          </div>
          <div>
            <div class="metric-big" style="color:var(--critical)">{kubescape.get('failed_count',0)}</div>
            <div class="metric-label">Controls Failed</div>
          </div>
          <div>
            <div class="metric-big" style="color:var(--ok)">{kubescape.get('passed_count',0)}</div>
            <div class="metric-label">Controls Passed</div>
          </div>
        </div>
      </div>
      <details>
        <summary>Ver failed controls ({len(kubescape.get('failed_controls',[]))} mostrados)</summary>
        <table style="margin-top:10px">
          <thead><tr><th>ID</th><th>Control</th><th>Sev</th><th>Resources</th><th>Remediation</th></tr></thead>
          <tbody>{ks_rows}</tbody>
        </table>
      </details>
      """}
    </div>

    <!-- Falco + Lynis side by side -->
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Falco — Runtime Security Events</div>
        {'<p style="color:var(--text-muted)">Falco não instalado. <code>helm install falco falcosecurity/falco -n falco --create-namespace</code></p>' if not falco.get('available') else f"""
        <div class="metric-big">{falco.get('total_events',0)}</div>
        <div class="metric-label" style="margin-bottom:12px">Events capturados</div>
        <table>
          <thead><tr><th>Regra</th><th>Ocorrências</th></tr></thead>
          <tbody>{falco_rules_rows}</tbody>
        </table>
        """}
      </div>

      <div class="card">
        <div class="card-title">Lynis — System Hardening Audit</div>
        {'<p style="color:var(--text-muted)">Lynis não disponível nos nodes</p>' if not lynis.get('available') else f"""
        <div style="display:flex; gap:24px; align-items:center; margin-bottom:16px">
          <div style="text-align:center">
            <div class="metric-big" style="color:{'#22c55e' if lynis.get('hardening_index',0) >= 65 else '#d97706' if lynis.get('hardening_index',0) >= 35 else '#dc2626'}">{lynis.get('hardening_index',0)}</div>
            <div class="metric-label">Hardening Index</div>
          </div>
          <div style="flex:1">
            <div style="color:{'#22c55e' if lynis.get('hardening_grade') == 'EXCELLENT' else '#d97706' if lynis.get('hardening_grade') in ('GOOD','MEDIUM') else '#dc2626'}; font-weight:700">{lynis.get('hardening_grade','N/A')}</div>
            <div class="progress-bar" style="margin-top:8px">
              <div class="progress-fill" style="width:{lynis.get('hardening_index',0)}%; background:{'#22c55e' if lynis.get('hardening_index',0)>=65 else '#d97706' if lynis.get('hardening_index',0)>=35 else '#dc2626'}"></div>
            </div>
          </div>
        </div>
        <div class="card-title">Warnings ({len(lynis.get('warnings',[]))})</div>
        <ul style="font-size:12px; color:var(--text-muted)">{lynis_rows}</ul>
        """}
      </div>
    </div>

    <!-- kube-hunter + kube-bench fails -->
    <div class="grid-2">
      <div class="card">
        <div class="card-title">kube-hunter — Penetration Testing</div>
        {'<p style="color:var(--text-muted)">kube-hunter não executado (requer autorização)</p>' if not kubehunter.get('available') else f"""
        <div class="metric-big" style="color:{'var(--critical)' if kubehunter.get('total',0) > 0 else 'var(--ok)'}">{kubehunter.get('total',0)}</div>
        <div class="metric-label" style="margin-bottom:12px">Vulnerabilidades encontradas</div>
        <table>
          <thead><tr><th>Sev</th><th>Vulnerability</th><th>Location</th><th>Evidence</th></tr></thead>
          <tbody>{kh_rows or '<tr><td colspan=4 style="color:var(--ok)">Nenhuma vulnerabilidade crítica encontrada ✓</td></tr>'}</tbody>
        </table>
        """}
      </div>

      <div class="card">
        <div class="card-title">kube-bench — CIS Benchmark Fails</div>
        {'<p style="color:var(--text-muted)">kube-bench não disponível</p>' if not kubebench.get('available') else f"""
        <table>
          <thead><tr><th>#</th><th>Seção</th><th>Check</th><th>Remediação</th></tr></thead>
          <tbody>{kb_rows or '<tr><td colspan=4 style="color:var(--ok)">Nenhum fail detectado ✓</td></tr>'}</tbody>
        </table>
        """}
      </div>
    </div>
  </section>

  <hr class="separator">

  <!-- ────────────────────────────────────────────────────────── -->
  <!-- 4. PERFORMANCE                                             -->
  <!-- ────────────────────────────────────────────────────────── -->
  <section class="section" id="performance">
    <h2 class="section-title">⚡ Análise de Performance</h2>

    <div class="grid-2">
      <!-- Netdata -->
      <div class="card">
        <div class="card-title">Netdata — Active Alarms</div>
        {'<p style="color:var(--text-muted)">Netdata não disponível. <code>wget -O /tmp/nd.sh https://get.netdata.cloud/kickstart.sh && sh /tmp/nd.sh</code></p>' if not netdata.get('available') else f"""
        <div class="metric-big" style="color:{'var(--critical)' if netdata.get('total_alarms',0) > 3 else 'var(--medium)' if netdata.get('total_alarms',0) > 0 else 'var(--ok)'}">{netdata.get('total_alarms',0)}</div>
        <div class="metric-label" style="margin-bottom:12px">Alarmes ativos</div>
        <table>
          <thead><tr><th>Sev</th><th>Alarm</th><th>Chart</th><th>Value</th></tr></thead>
          <tbody>{nd_rows or '<tr><td colspan=4 style="color:var(--ok)">Nenhum alarme ativo ✓</td></tr>'}</tbody>
        </table>
        """}
      </div>

      <!-- bpftrace -->
      <div class="card">
        <div class="card-title">bpftrace — eBPF Tracing Results</div>
        {'<p style="color:var(--text-muted)">bpftrace não disponível. <code>apt-get install bpftrace</code></p>' if not bpftrace.get('available') else f"""
        <details open>
          <summary>Top Syscalls por Processo</summary>
          <pre>{escape(bpftrace.get('syscalls_summary','N/A'))}</pre>
        </details>
        <details style="margin-top:8px">
          <summary>Disk I/O Latency Histogram</summary>
          <pre>{escape(bpftrace.get('disk_latency','N/A'))}</pre>
        </details>
        """}
      </div>
    </div>

    <!-- System Snapshot -->
    {'<div class="card"><div class="card-title">System Snapshot</div><pre>' + escape(str(snapshot)) + '</pre></div>' if snapshot.get('available') else ''}
  </section>

  <hr class="separator">

  <!-- ────────────────────────────────────────────────────────── -->
  <!-- 5. CONSOLIDATED FINDINGS                                   -->
  <!-- ────────────────────────────────────────────────────────── -->
  <section class="section" id="findings">
    <h2 class="section-title">📋 Findings Consolidados</h2>
    <div class="card">
      <div class="card-title">Top 50 Findings — Ordenados por Severidade</div>
      <table>
        <thead>
          <tr><th>Severity</th><th>Tool</th><th>Type</th><th>ID</th><th>Finding</th></tr>
        </thead>
        <tbody>
          {findings_rows or '<tr><td colspan=5 style="color:var(--ok)">Nenhum finding identificado ✓</td></tr>'}
        </tbody>
      </table>
    </div>
  </section>

  <hr class="separator">

  <!-- ────────────────────────────────────────────────────────── -->
  <!-- 6. ROADMAP DE REMEDIAÇÃO                                   -->
  <!-- ────────────────────────────────────────────────────────── -->
  <section class="section" id="roadmap">
    <h2 class="section-title">🗺️ Roadmap de Remediação</h2>
    <div class="grid-3">
      <div class="card">
        <div class="card-title" style="color:var(--critical)">⚡ Quick Wins (< 1 dia)</div>
        <ul>{quick_wins_html}</ul>
      </div>
      <div class="card">
        <div class="card-title" style="color:var(--medium)">📅 Médio Prazo (1-7 dias)</div>
        <ul>{medium_html}</ul>
      </div>
      <div class="card">
        <div class="card-title" style="color:var(--accent)">🏗️ Longo Prazo (projetos)</div>
        <ul>{long_html}</ul>
      </div>
    </div>
  </section>

  <hr class="separator">

  <!-- Footer -->
  <div style="text-align:center; color:var(--text-muted); font-size:12px; padding:16px 0">
    Generated by <strong>k8s-vps-investigation skill</strong> &nbsp;|&nbsp;
    {ts} &nbsp;|&nbsp;
    Tools: K9s · Trivy · Kubescape · kube-bench · Falco · Popeye · kube-hunter · Netdata · Glances · Lynis · bpftrace · Kubeshark
  </div>

</div>

<script>
// Trivy donut chart
const trivyData = {trivy_chart_data};
const ctx = document.getElementById('trivyChart');
if (ctx) {{
  new Chart(ctx, {{
    type: 'doughnut',
    data: {{
      labels: trivyData.labels,
      datasets: [{{ data: trivyData.values, backgroundColor: trivyData.colors, borderWidth: 2, borderColor: '#1e293b' }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ position: 'right', labels: {{ color: '#e2e8f0', font: {{ size: 11 }} }} }},
        tooltip: {{ callbacks: {{ label: (ctx) => ` ${{ctx.label}}: ${{ctx.raw}}` }} }}
      }}
    }}
  }});
}}
</script>
</body>
</html>"""

    return html


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="K8s + VPS Investigation Report Generator")
    parser.add_argument("--input-dir", default="/tmp/investigation", help="Diretório com os artefatos de investigação")
    parser.add_argument("--output", default="/tmp/investigation/final_report.html", help="Path do relatório HTML gerado")
    parser.add_argument("--cluster-name", default="kubernetes-cluster", help="Nome do cluster")
    parser.add_argument("--environment", default="production", help="Ambiente (production/staging/dev)")
    parser.add_argument("--investigator", default="investigator", help="Nome do responsável pela investigação")
    args = parser.parse_args()

    print(f"📂 Loading artifacts from: {args.input_dir}")

    data = {
        "popeye": load_popeye(args.input_dir),
        "trivy": load_trivy(args.input_dir),
        "kubescape": load_kubescape(args.input_dir),
        "kubebench": load_kubebench(args.input_dir),
        "falco": load_falco(args.input_dir),
        "lynis": load_lynis(args.input_dir),
        "kubehunter": load_kubehunter(args.input_dir),
        "netdata": load_netdata(args.input_dir),
        "bpftrace": load_bpftrace(args.input_dir),
        "snapshot": load_system_snapshot(args.input_dir),
    }

    # Print availability summary
    for tool, tool_data in data.items():
        status = "✓" if tool_data.get("available") else "✗ (not available)"
        print(f"  {tool:15} {status}")

    print(f"\n🔨 Generating HTML report...")
    html = generate_html(data, args)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(args.output) / 1024
    print(f"✅ Report generated: {args.output} ({size_kb:.1f} KB)")
    print(f"🌐 Open in browser: file://{os.path.abspath(args.output)}")


if __name__ == "__main__":
    main()
