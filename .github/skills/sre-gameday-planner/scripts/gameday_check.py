#!/usr/bin/env python3
"""Readiness gate for a game day / DR test plan, and RTO/RPO measurement after it runs.

  gameday_check.py check PLAN.yaml [--json]
  gameday_check.py measure EVENTS.yaml [--json]
PLAN: {"name", "environment": "prod|nonprod", "hypothesis", "steady_state": [{"sli", "threshold"}],
       "blast_radius": {"services": [...], "traffic_pct": 5}, "abort_criteria": [{"sli", "threshold"}],
       "rollback": {"steps": [...], "tested": true}, "approvals": [{"role", "name", "date"}],
       "required_approvals": ["service owner", "change board"], "comms": {...}, "targets": {"rto_min", "rpo_min"}}
EVENTS: {"fault_injected": ISO, "service_restored": ISO, "last_good_data": ISO, "targets": {"rto_min", "rpo_min"}}
check exits 1 when not ready; measure exits 1 when RTO or RPO is missed; 2 on input error.
"""
import argparse, json, sys
from datetime import datetime
import yaml


def ts(s):
    return datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def check(p):
    f = []
    add = lambda sev, msg: f.append({"severity": sev, "message": msg})
    prod = str(p.get("environment", "")).lower() in ("prod", "production")
    h = str(p.get("hypothesis", ""))
    if not h or not all(w in h.lower() for w in ("when", "will")):
        add("High", "Hypothesis must follow 'When <fault>, <system> will <behavior>'.")
    if not p.get("steady_state"):
        add("High", "No steady-state SLIs defined.")
    ab = p.get("abort_criteria") or []
    if not ab:
        add("High", "No abort criteria.")
    elif any(not isinstance(a.get("threshold"), (int, float)) for a in ab):
        add("High", "Every abort criterion needs a numeric threshold.")
    br = p.get("blast_radius") or {}
    if not br.get("services"):
        add("High", "Blast radius does not name affected services.")
    pct = br.get("traffic_pct")
    if prod and (not isinstance(pct, (int, float)) or pct > 25):
        add("High", "Production exercise must cap traffic exposure at 25% or less.")
    rb = p.get("rollback") or {}
    if not rb.get("steps"):
        add("High", "No rollback steps.")
    if not rb.get("tested"):
        add("High" if prod else "Medium", "Rollback path not tested.")
    have = {str(a.get("role", "")).lower() for a in (p.get("approvals") or []) if a.get("name") and a.get("date")}
    need = [r.lower() for r in (p.get("required_approvals") or (["service owner", "change board"] if prod else ["service owner"]))]
    for r in need:
        if r not in have:
            add("High", f"Missing recorded approval: {r} (name and date).")
    if not p.get("comms"):
        add("Medium", "No communication plan.")
    if not (p.get("targets") or {}).get("rto_min"):
        add("Medium", "No RTO target to measure against.")
    ready = not any(x["severity"] == "High" for x in f)
    return {"name": p.get("name"), "ready": ready, "findings": f}


def measure(e):
    t = e.get("targets") or {}
    rto = (ts(e["service_restored"]) - ts(e["fault_injected"])).total_seconds() / 60
    rpo = (ts(e["fault_injected"]) - ts(e["last_good_data"])).total_seconds() / 60 if e.get("last_good_data") else None
    res = {"rto_min": round(rto, 1), "rpo_min": round(rpo, 1) if rpo is not None else None,
           "rto_target_min": t.get("rto_min"), "rpo_target_min": t.get("rpo_min")}
    res["rto_met"] = t.get("rto_min") is None or rto <= t["rto_min"]
    res["rpo_met"] = rpo is None or t.get("rpo_min") is None or rpo <= t["rpo_min"]
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("check", "measure"):
        s = sub.add_parser(c); s.add_argument("file"); s.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        data = yaml.safe_load(open(a.file, encoding="utf-8")) or {}
        r = check(data) if a.cmd == "check" else measure(data)
    except (OSError, yaml.YAMLError, KeyError, ValueError) as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    if a.json:
        print(json.dumps(r, indent=2))
    elif a.cmd == "check":
        print(f"{r['name']}: {'READY' if r['ready'] else 'NOT READY'}")
        for x in r["findings"]:
            print(f"  [{x['severity']}] {x['message']}")
    else:
        print(f"RTO {r['rto_min']} min (target {r['rto_target_min']}) {'met' if r['rto_met'] else 'MISSED'}; "
              f"RPO {r['rpo_min']} min (target {r['rpo_target_min']}) {'met' if r['rpo_met'] else 'MISSED'}")
    ok = r["ready"] if a.cmd == "check" else (r["rto_met"] and r["rpo_met"])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
