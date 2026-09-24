#!/usr/bin/env python3
"""DORA metrics from normalized ADO data. See references/data-schema.md.

  dora.py normalize environment_records.json > deployments.json
  dora.py compute --deployments deployments.json [--incidents incidents.json] [--days 90] [--json]
"""
import argparse, json, statistics, sys
from datetime import datetime, timedelta, timezone


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def normalize(records):
    if isinstance(records, dict):
        records = records.get("value", [])
    out = []
    for r in records:
        res = str(r.get("result", "")).lower()
        out.append({"id": str(r.get("id") or (r.get("owner") or {}).get("id")),
                    "finished": r.get("finishTime"),
                    "result": "succeeded" if res == "succeeded" else ("canceled" if res in ("canceled", "skipped") else "failed")})
    return out


def pct(values, p):
    if not values:
        return None
    v = sorted(values)
    k = (len(v) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def compute(deps, incs, days, now=None):
    now = now or datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    deps = [d for d in deps if d.get("finished") and start <= ts(d["finished"]) <= now and d.get("result") != "canceled"]
    incs = [i for i in incs if i.get("created") and start <= ts(i["created"]) <= now]
    ok = [d for d in deps if d["result"] == "succeeded"]
    caused = {str(i["deployment_id"]) for i in incs if i.get("deployment_id")}
    # DORA change failure rate: successful production deployments that caused a failure needing remediation.
    changes_failed = [d for d in ok if d.get("caused_incident") or str(d["id"]) in caused]
    failed_runs = [d for d in deps if d["result"] == "failed"]
    lead = [(ts(d["finished"]) - ts(d["first_commit_time"])).total_seconds() / 3600 for d in ok if d.get("first_commit_time")]
    restore = [(ts(i["resolved"]) - ts(i["created"])).total_seconds() / 3600 for i in incs if i.get("resolved")]
    deploy_days = len({ts(d["finished"]).date() for d in ok})
    m = {
        "period_days": days, "deployments_total": len(deps), "deployments_succeeded": len(ok),
        "deployment_frequency_per_week": round(len(ok) / (days / 7), 2),
        "days_with_a_deployment_pct": round(100 * deploy_days / days, 1),
        "lead_time_hours_median": round(statistics.median(lead), 2) if lead else None,
        "lead_time_hours_p90": round(pct(lead, 0.9), 2) if lead else None,
        "lead_time_sample": len(lead),
        "change_failure_rate_pct": round(100 * len(changes_failed) / len(ok), 1) if ok else None,
        "change_failure_attribution_known": any("caused_incident" in d for d in deps) or bool(caused),
        "failed_deployment_run_pct": round(100 * len(failed_runs) / len(deps), 1) if deps else None,
        "incidents": len(incs),
        "time_to_restore_hours_median": round(statistics.median(restore), 2) if restore else None,
        "time_to_restore_sample": len(restore),
    }
    m["low_confidence"] = [k for k, n in (("deployment metrics", len(deps)), ("time to restore", len(restore))) if n < (10 if k.startswith("dep") else 3)]
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("normalize"); n.add_argument("records")
    c = sub.add_parser("compute")
    c.add_argument("--deployments", required=True); c.add_argument("--incidents")
    c.add_argument("--days", type=int, default=90); c.add_argument("--as-of"); c.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.cmd == "normalize":
        json.dump(normalize(json.load(open(a.records))), sys.stdout, indent=2); return
    deps = json.load(open(a.deployments))
    incs = json.load(open(a.incidents)) if a.incidents else []
    m = compute(deps, incs, a.days, ts(a.as_of) if a.as_of else None)
    if a.json:
        print(json.dumps(m, indent=2))
    else:
        for k, v in m.items():
            print(f"{k:34} {v}")


if __name__ == "__main__":
    main()
