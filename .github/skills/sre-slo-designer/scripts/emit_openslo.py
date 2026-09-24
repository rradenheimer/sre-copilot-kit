#!/usr/bin/env python3
"""Emit OpenSLO v1 YAML from a compact SLO spec.

  emit_openslo.py SPEC.yaml|SPEC.json [--out DIR]
SPEC: {"service": "checkout", "slos": [{"name": "checkout-availability", "description": "...",
       "target": 99.9, "window_days": 28, "good": "<query>", "total": "<query>",
       "source": "azure-monitor"}]}
Writes one OpenSLO document per SLO (kind: SLO with an inline ratio indicator). Exit 2 on invalid spec.
"""
import argparse, json, os, re, sys
import yaml

NAME = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")


def validate(spec):
    errs = []
    if not spec.get("service"):
        errs.append("service is required")
    for i, s in enumerate(spec.get("slos") or []):
        w = f"slos[{i}]"
        if not NAME.match(str(s.get("name", ""))):
            errs.append(f"{w}.name must be lowercase DNS-style (a-z, 0-9, -)")
        t = s.get("target")
        if not isinstance(t, (int, float)) or not 0 < t < 100:
            errs.append(f"{w}.target must be a percentage between 0 and 100, e.g. 99.9")
        for k in ("good", "total"):
            if not s.get(k):
                errs.append(f"{w}.{k} query is required")
    if not spec.get("slos"):
        errs.append("slos must contain at least one SLO")
    return errs


def doc(service, s):
    src = s.get("source", "azure-monitor")
    return {
        "apiVersion": "openslo/v1",
        "kind": "SLO",
        "metadata": {"name": s["name"], "displayName": s.get("display_name", s["name"])},
        "spec": {
            "description": s.get("description", ""),
            "service": service,
            "indicator": {
                "metadata": {"name": f"{s['name']}-sli"},
                "spec": {"ratioMetric": {
                    "counter": True,
                    "good": {"metricSource": {"type": src, "spec": {"query": s["good"]}}},
                    "total": {"metricSource": {"type": src, "spec": {"query": s["total"]}}},
                }},
            },
            "timeWindow": [{"duration": f"{int(s.get('window_days', 28))}d", "isRolling": True}],
            "budgetingMethod": "Occurrences",
            "objectives": [{"displayName": s.get("objective_name", "target"), "target": round(s["target"] / 100, 6)}],
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec"); ap.add_argument("--out", help="directory for one YAML file per SLO; default stdout")
    a = ap.parse_args()
    try:
        with open(a.spec, encoding="utf-8") as fh:
            spec = yaml.safe_load(fh)  # YAML is a superset of JSON
    except (OSError, yaml.YAMLError) as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    errs = validate(spec or {})
    if errs:
        print("Invalid spec:\n- " + "\n- ".join(errs), file=sys.stderr); sys.exit(2)
    docs = [doc(spec["service"], s) for s in spec["slos"]]
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        for d in docs:
            p = os.path.join(a.out, f"{d['metadata']['name']}.openslo.yaml")
            with open(p, "w", encoding="utf-8") as fh:
                yaml.safe_dump(d, fh, sort_keys=False)
            print(p)
    else:
        print(yaml.safe_dump_all(docs, sort_keys=False), end="")


if __name__ == "__main__":
    main()
