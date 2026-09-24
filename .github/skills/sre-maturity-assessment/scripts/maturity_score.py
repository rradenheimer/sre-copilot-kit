#!/usr/bin/env python3
"""Score an SRE maturity assessment and draft the phased roadmap order.

  maturity_score.py ASSESSMENT.yaml|json [--json]
ASSESSMENT: {"client": "code", "target": 3, "dimensions": {"incident_management": {"score": 2, "target": 4,
             "verified": true, "evidence": "...", "weight": 1.0}, ...}}
score and target are 1-5. Unverified (self-reported) scores are capped at 3 for roadmap priority and flagged.
Priority = weight x gap, with a bonus for foundational dimensions. Phases: gap >= 2 on a foundational
dimension -> 0-90 days; other gap >= 2 -> 3-6 months; gap 1 -> 6-12 months. Exit 2 on input error.
"""
import argparse, json, sys
import yaml

DIMENSIONS = ["incident_management", "observability", "slos_and_error_budgets", "on_call_health",
              "toil_and_automation", "change_management", "capacity", "resilience_and_dr", "reliability_culture"]
FOUNDATIONAL = {"incident_management", "observability", "change_management"}


def run(a):
    dims, errs = a.get("dimensions") or {}, []
    default_target = a.get("target", 3)
    rows = []
    for d in DIMENSIONS:
        x = dims.get(d)
        if x is None:
            errs.append(f"missing dimension: {d}"); continue
        s, t = x.get("score"), x.get("target", default_target)
        if not all(isinstance(v, (int, float)) and 1 <= v <= 5 for v in (s, t)):
            errs.append(f"{d}: score and target must be 1-5"); continue
        verified = bool(x.get("verified", False))
        eff = s if verified else min(s, 3)
        gap = max(0, t - eff)
        pr = round(float(x.get("weight", 1.0)) * gap * (1.5 if d in FOUNDATIONAL else 1.0), 2)
        phase = "0-90 days" if gap >= 2 and d in FOUNDATIONAL else ("3-6 months" if gap >= 2 else ("6-12 months" if gap >= 1 else "sustain"))
        rows.append({"dimension": d, "score": s, "target": t, "verified": verified, "gap": gap,
                     "priority": pr, "phase": phase, "evidence": x.get("evidence", ""),
                     "note": "" if verified else "self-reported; verify before quoting"})
    if errs:
        return None, errs
    rows.sort(key=lambda r: -r["priority"])
    overall = round(sum(r["score"] for r in rows) / len(rows), 2)
    return {"client": a.get("client"), "overall_mean": overall,
            "unverified": [r["dimension"] for r in rows if not r["verified"]],
            "roadmap": {p: [r["dimension"] for r in rows if r["phase"] == p] for p in ("0-90 days", "3-6 months", "6-12 months")},
            "dimensions": rows}, []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("assessment"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        data = yaml.safe_load(open(a.assessment, encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    r, errs = run(data)
    if errs:
        print("Input error:\n- " + "\n- ".join(errs), file=sys.stderr); sys.exit(2)
    if a.json:
        print(json.dumps(r, indent=2)); return
    print(f"Overall mean {r['overall_mean']} / 5")
    for row in r["dimensions"]:
        print(f"  {row['dimension']:24} {row['score']} -> {row['target']}  gap {row['gap']}  {row['phase']:11} {row['note']}")
    for p, ds in r["roadmap"].items():
        print(f"{p}: {', '.join(ds) or '-'}")


if __name__ == "__main__":
    main()
