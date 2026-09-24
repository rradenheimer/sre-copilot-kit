#!/usr/bin/env python3
"""Compare capacity options by cost, headroom and lead time.

  cost_model.py OPTIONS.yaml|json [--months 12] [--json]
OPTIONS: {"required_capacity": 640, "target_utilization_pct": 70, "pricing_source": "Azure price sheet",
          "pricing_date": "2026-09-01",
          "options": [{"name": "Scale out D8s_v5", "capacity_per_unit": 8, "unit_price_month": 280.0,
                       "one_time": 0, "lead_time_days": 1, "commitment_months": 0}, ...]}
Units needed = ceil(required / (capacity_per_unit x target utilization)). Reports monthly and total cost over
the horizon, cost per capacity unit, resulting headroom, and flags commitments longer than the horizon.
Exit 2 on input error.
"""
import argparse, json, math, sys
import yaml


def model(o, months):
    req = float(o["required_capacity"]); tu = float(o.get("target_utilization_pct", 70)) / 100
    out, warn = [], []
    if not o.get("pricing_source") or not o.get("pricing_date"):
        warn.append("pricing_source and pricing_date are missing; label every figure as unverified.")
    for opt in o["options"]:
        cap = float(opt["capacity_per_unit"])
        units = opt.get("units") or math.ceil(req / (cap * tu))
        monthly = units * float(opt["unit_price_month"])
        total = monthly * months + float(opt.get("one_time", 0))
        commit = int(opt.get("commitment_months", 0))
        headroom = round(100 * (1 - req / (units * cap)), 1)
        out.append({"name": opt["name"], "units": units, "monthly_cost": round(monthly, 2),
                    "total_cost": round(total, 2), "cost_per_capacity_unit_month": round(monthly / (units * cap), 4),
                    "headroom_pct": headroom, "lead_time_days": opt.get("lead_time_days"),
                    "commitment_months": commit,
                    "note": f"commits {commit} months, beyond the {months}-month horizon" if commit > months else ""})
    out.sort(key=lambda r: r["total_cost"])
    return {"required_capacity": req, "months": months, "pricing_source": o.get("pricing_source"),
            "pricing_date": o.get("pricing_date"), "warnings": warn, "options": out}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("options"); ap.add_argument("--months", type=int, default=12); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        r = model(yaml.safe_load(open(a.options, encoding="utf-8")), a.months)
    except (OSError, yaml.YAMLError, KeyError, TypeError, ValueError) as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    if a.json:
        print(json.dumps(r, indent=2)); return
    for w in r["warnings"]:
        print("WARNING:", w)
    print(f"Pricing: {r['pricing_source']} ({r['pricing_date']}); horizon {a.months} months")
    for o in r["options"]:
        print(f"  {o['name'][:32]:32} units {o['units']:>3}  ${o['monthly_cost']:>10,.2f}/mo  ${o['total_cost']:>11,.2f} total  headroom {o['headroom_pct']}%  {o['note']}")


if __name__ == "__main__":
    main()
