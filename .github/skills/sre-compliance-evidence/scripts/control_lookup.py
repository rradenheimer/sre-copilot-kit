#!/usr/bin/env python3
"""Look up controls for SRE artifacts and compute evidence coverage.

  control_lookup.py controls --framework soc2 [--artifact dr_test_report] [--json]
  control_lookup.py coverage INVENTORY.yaml --framework nist-800-53-r5 [--as-of 2026-09-23] [--json]
INVENTORY: {"artifacts": [{"type": "dr_test_report", "id": "DR-2026-08", "date": "2026-08-14",
            "attributes": {"tested": true, "results_recorded": true}}]}
Coverage per control: Full (an artifact meets every requirement), Partial (artifacts exist, requirements
unmet; gaps listed), None (no mapped artifact). It never states a control is satisfied; the assessor decides.
Mapping: ../references/artifact-to-control-map.yaml. Exit 1 when any mapped control has None, 2 on input error.
"""
import argparse, json, os, sys
from datetime import date
import yaml

MAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "artifact-to-control-map.yaml")


def load_map():
    with open(MAP, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def controls(m, fw, artifact=None):
    out = {}
    for atype, spec in m["artifacts"].items():
        if artifact and atype != artifact:
            continue
        for cid, title in (spec["controls"].get(fw) or {}).items():
            out.setdefault(cid, {"control": cid, "title": title, "artifact_types": []})["artifact_types"].append(atype)
    return sorted(out.values(), key=lambda c: c["control"])


def gaps_for(item, req, as_of):
    g = []
    attrs = item.get("attributes") or {}
    for a in req.get("attributes", []):
        v = attrs.get(a)
        if a == "retention_days":
            if not isinstance(v, (int, float)) or v < req.get("min_retention_days", 0):
                g.append(f"retention_days {v} below {req.get('min_retention_days')}")
        elif not v:
            g.append(f"{a} missing or false")
    if req.get("max_age_days"):
        d = item.get("date")
        if not d:
            g.append("no date")
        else:
            age = (as_of - date.fromisoformat(str(d)[:10])).days
            if age > req["max_age_days"]:
                g.append(f"{age} days old (max {req['max_age_days']})")
    return g


def coverage(m, fw, inv, as_of):
    rows = []
    items = inv.get("artifacts") or []
    for c in controls(m, fw):
        evid, best = [], "None"
        for atype in c["artifact_types"]:
            req = m["artifacts"][atype]["requires"]
            for it in (i for i in items if i.get("type") == atype):
                g = gaps_for(it, req, as_of)
                evid.append({"id": it.get("id"), "type": atype, "gaps": g})
                if not g:
                    best = "Full"
                elif best == "None":
                    best = "Partial"
        rows.append({**c, "coverage": best, "evidence": evid})
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("controls"); c.add_argument("--framework", required=True); c.add_argument("--artifact"); c.add_argument("--json", action="store_true")
    v = sub.add_parser("coverage"); v.add_argument("inventory"); v.add_argument("--framework", required=True); v.add_argument("--as-of"); v.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        m = load_map()
        if a.framework not in m["frameworks"]:
            raise ValueError(f"unknown framework; choose from {', '.join(m['frameworks'])}")
        if a.cmd == "controls":
            res = controls(m, a.framework, a.artifact)
        else:
            inv = yaml.safe_load(open(a.inventory, encoding="utf-8")) or {}
            res = coverage(m, a.framework, inv, date.fromisoformat(a.as_of) if a.as_of else date.today())
    except (OSError, ValueError, yaml.YAMLError, KeyError) as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    if a.json:
        print(json.dumps({"framework": m["frameworks"][a.framework], "map_version": m["version"], "controls": res}, indent=2, default=str))
    else:
        print(f"{m['frameworks'][a.framework]} (map {m['version']}; verify IDs against the licensed catalog)")
        for r in res:
            line = f"  {r['control']:22} {r['title'][:40]:40}"
            if a.cmd == "coverage":
                gaps = "; ".join(g for e in r["evidence"] for g in e["gaps"])
                line += f" {r['coverage']:8} {gaps[:70]}"
            else:
                line += " " + ", ".join(r["artifact_types"])
            print(line)
    sys.exit(1 if a.cmd == "coverage" and any(r["coverage"] == "None" for r in res) else 0)


if __name__ == "__main__":
    main()
