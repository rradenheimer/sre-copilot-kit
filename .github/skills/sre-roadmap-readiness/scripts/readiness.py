#!/usr/bin/env python3
"""Roadmap readiness: which advanced capabilities (R1-R12) a client's data and controls can support today.

  readiness.py READINESS.yaml [--json]
READINESS.yaml lists evidence files (paths relative to the repository root) and facts confirmed by people:
  client: CODE
  files:    {deployments: ..., incidents: ..., telemetry_series: ..., sli_daily: ..., slo_spec: ...,
             alert_events: ..., postmortems_dir: ..., runbooks_dir: ...}
  facts:    {hooks_verified: bool, plugin_packaging: bool, telemetry_read_access: bool,
             gates_pipeline_enabled: bool, service_topology_available: bool, tracing_coverage_pct: int,
             agent_in_production: bool, control_map_verified: bool, audit_retention_days: int}
Each item gets Ready, Partial (some prerequisites met) or Not ready, with the unmet prerequisites.
Linters from sibling skills are used when present; otherwise that check is reported as unverified.
Exit 0 always on valid input (readiness is information, not a gate); 2 on input error.
"""
import argparse, glob, json, os, subprocess, sys
from datetime import date
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.abspath(os.path.join(HERE, "..", ".."))
ITEMS = os.path.join(HERE, "..", "references", "roadmap-items.yaml")


def jload(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def lint_clean(script_rel, files):
    """Return (clean_count, total, verified) using a sibling skill's linter (exit 0 = no High findings)."""
    script = os.path.join(SKILLS, script_rel)
    if not files:
        return 0, 0, True
    if not os.path.exists(script):
        return 0, len(files), False
    clean = sum(1 for f in files if subprocess.run([sys.executable, script, f], capture_output=True, timeout=60).returncode == 0)
    return clean, len(files), True


def gather(cfg, root):
    f = {k: os.path.join(root, v) for k, v in (cfg.get("files") or {}).items() if v}
    ev = {"facts": cfg.get("facts") or {}}
    if "deployments" in f and os.path.exists(f["deployments"]):
        deps = jload(f["deployments"])
        inc = jload(f["incidents"]) if "incidents" in f and os.path.exists(f["incidents"]) else []
        caused = {str(i.get("deployment_id")) for i in inc if i.get("deployment_id")}
        ev["deployments"] = len(deps)
        ev["attribution_known"] = any("caused_incident" in d for d in deps) or bool(caused)
        ev["change_failures"] = sum(1 for d in deps if d.get("caused_incident") or str(d.get("id")) in caused)
    if "incidents" in f and os.path.exists(f["incidents"]):
        ev["incidents"] = len(jload(f["incidents"]))
    if "telemetry_series" in f and os.path.exists(f["telemetry_series"]):
        ds = sorted(date.fromisoformat(r["date"][:10]) for r in jload(f["telemetry_series"]))
        ev["telemetry_days"] = (ds[-1] - ds[0]).days + 1 if ds else 0
    if "sli_daily" in f and os.path.exists(f["sli_daily"]):
        ev["sli_days"] = len(jload(f["sli_daily"]))
    if "slo_spec" in f and os.path.exists(f["slo_spec"]):
        ev["slos"] = len((yaml.safe_load(open(f["slo_spec"], encoding="utf-8")) or {}).get("slos") or [])
    if "alert_events" in f and os.path.exists(f["alert_events"]):
        ev["alert_events"] = len(jload(f["alert_events"]))
    if "postmortems_dir" in f:
        pms = sorted(glob.glob(os.path.join(f["postmortems_dir"], "*.md")))
        ev["postmortems"], ev["postmortems_total"], ev["postmortem_lint_verified"] = lint_clean("sre-postmortem-author/scripts/postmortem_lint.py", pms)
    if "runbooks_dir" in f:
        rbs = sorted(glob.glob(os.path.join(f["runbooks_dir"], "*.md")))
        ev["clean_runbooks"], ev["runbooks_total"], ev["runbook_lint_verified"] = lint_clean("sre-runbook-author/scripts/runbook_lint.py", rbs)
    return ev


def assess(ev, th):
    fa = ev["facts"]
    def need(ok, msg):
        return (bool(ok), msg)
    pm_clean_pct = 100 * ev.get("postmortems", 0) / ev["postmortems_total"] if ev.get("postmortems_total") else 0
    checks = {
        "R1": [need(fa.get("plugin_packaging"), "kit packaged as a versioned plugin"),
               need(fa.get("hooks_verified"), "guardrail hooks verified on the target surface")],
        "R2": [need(ev.get("incidents", 0) >= th["r2_min_incidents"], f">= {th['r2_min_incidents']} incident records (have {ev.get('incidents', 0)})"),
               need(fa.get("telemetry_read_access"), "read-only telemetry access for agents")],
        "R3": [need(ev.get("clean_runbooks", 0) >= th["r3_min_clean_runbooks"], f">= {th['r3_min_clean_runbooks']} runbooks passing runbook_lint (have {ev.get('clean_runbooks', 0)})"),
               need(fa.get("hooks_verified"), "guardrail hooks verified"),
               need(ev.get("slos", 0) >= 1, "at least one SLO defined, to gate autonomy on error budget")],
        "R4": [need(fa.get("gates_pipeline_enabled"), "reliability gates pipeline enabled")],
        "R5": [need(ev.get("deployments", 0) >= th["r5_min_deployments"], f">= {th['r5_min_deployments']} production deployments (have {ev.get('deployments', 0)})"),
               need(ev.get("attribution_known"), "deployment-to-incident attribution recorded"),
               need(ev.get("change_failures", 0) >= th["r5_min_change_failures"], f">= {th['r5_min_change_failures']} attributed change failures as labels (have {ev.get('change_failures', 0)})")],
        "R6": [need(ev.get("telemetry_days", 0) >= th["r6_min_telemetry_days"], f">= {th['r6_min_telemetry_days']} days of telemetry (have {ev.get('telemetry_days', 0)})")],
        "R7": [need(ev.get("postmortems_total", 0) >= th["r7_min_postmortems"], f">= {th['r7_min_postmortems']} postmortems (have {ev.get('postmortems_total', 0)})"),
               need(pm_clean_pct >= th["r7_min_clean_pct"], f">= {th['r7_min_clean_pct']}% pass postmortem_lint (have {pm_clean_pct:.0f}%)")],
        "R8": [need(ev.get("alert_events", 0) >= th["r8_min_alert_events"], f">= {th['r8_min_alert_events']} alert events (have {ev.get('alert_events', 0)})"),
               need(fa.get("service_topology_available"), "service topology available")],
        "R9": [need(ev.get("slos", 0) >= 1, "at least one SLO defined"),
               need(ev.get("sli_days", 0) >= th["r9_min_sli_days"], f">= {th['r9_min_sli_days']} days of daily SLI data (have {ev.get('sli_days', 0)})")],
        "R10": [need(fa.get("tracing_coverage_pct", 0) >= th["r10_min_tracing_pct"], f">= {th['r10_min_tracing_pct']}% tracing coverage (have {fa.get('tracing_coverage_pct', 0)}%)")],
        "R11": [need(fa.get("agent_in_production"), "an operational agent in production to evaluate"),
                need(ev.get("postmortems_total", 0) >= th["r11_min_replay_incidents"], f">= {th['r11_min_replay_incidents']} documented incidents for replay (have {ev.get('postmortems_total', 0)})")],
        "R12": [need(fa.get("control_map_verified"), "control map verified by the compliance lead"),
                need(fa.get("audit_retention_days", 0) >= th["r12_min_audit_retention_days"], f"guardrail audit retention >= {th['r12_min_audit_retention_days']} days")],
    }
    unverified = []
    if ev.get("postmortems_total") and not ev.get("postmortem_lint_verified", True):
        unverified.append("postmortem_lint not present: R7 clean-rate unverified")
    if ev.get("runbooks_total") and not ev.get("runbook_lint_verified", True):
        unverified.append("runbook_lint not present: R3 runbook quality unverified")
    return checks, unverified


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config"); ap.add_argument("--root", default=".", help="base for relative file paths")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        cfg = yaml.safe_load(open(a.config, encoding="utf-8")) or {}
        meta = yaml.safe_load(open(ITEMS, encoding="utf-8"))
        ev = gather(cfg, a.root)
        checks, unverified = assess(ev, meta["thresholds"])
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError, json.JSONDecodeError) as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    rows = []
    for rid, info in meta["items"].items():
        c = checks[rid]; met = sum(ok for ok, _ in c)
        status = "Ready" if met == len(c) else ("Partial" if met else "Not ready")
        rows.append({"id": rid, "name": info["name"], "horizon": info["horizon"], "status": status,
                     "unmet": [m for ok, m in c if not ok]})
    out = {"client": cfg.get("client"), "items": rows, "unverified": unverified}
    if a.json:
        print(json.dumps(out, indent=2)); return
    print(f"Roadmap readiness for {out['client']}")
    for r in rows:
        print(f"  {r['id']:>3} H{r['horizon']} {r['status']:9} {r['name']}")
        for m in r["unmet"]:
            print(f"               needs: {m}")
    for u in unverified:
        print("  NOTE:", u)


if __name__ == "__main__":
    main()
