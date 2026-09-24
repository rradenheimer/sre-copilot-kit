#!/usr/bin/env python3
"""Score a production readiness review from an evidence file.

  prr_score.py EVIDENCE.yaml|json [--extra-checks OVERLAY_CHECKS.yaml] [--json]
EVIDENCE: {"service": "billing", "domains": {"observability": {"status": "met", "evidence": "dashboard link",
           "blocking": true}, ...}}
status: met | partial | not_met | not_tested | n/a. Domains listed in DOMAINS must all appear.
Rules: backup_restore and dr with status not_tested count as not_met; any blocking domain not met -> Not ready;
any partial or non-blocking not_met -> Ready with conditions; else Ready. Missing evidence text on a "met"
domain downgrades it to partial. Exit 1 when Not ready, 2 on input error.
"""
import argparse, json, sys
import yaml

DOMAINS = {  # domain: blocking by default
    "observability": True, "slos_and_alerting": True, "on_call": True, "runbooks": True,
    "capacity_and_load": False, "dependency_failure_modes": False, "backup_restore": True, "dr": True,
    "security_review": True, "change_and_rollback": True, "documentation_and_ownership": False,
}
TESTED = {"backup_restore", "dr"}
VALID = {"met", "partial", "not_met", "not_tested", "n/a"}


def score(ev, extra):
    domains = dict(DOMAINS); domains.update({k: bool(v) for k, v in (extra or {}).items()})
    got = ev.get("domains") or {}
    rows, errors = [], []
    for d, blocking_default in domains.items():
        item = got.get(d)
        if item is None:
            rows.append({"domain": d, "status": "not_met", "blocking": blocking_default, "note": "no evidence provided"}); continue
        st = str(item.get("status", "")).lower()
        if st not in VALID:
            errors.append(f"{d}: status '{st}' not in {sorted(VALID)}"); continue
        note = ""
        if st == "not_tested":
            st, note = ("not_met", "untested counts as not met") if d in TESTED else ("partial", "not tested")
        if st == "met" and not str(item.get("evidence", "")).strip():
            st, note = "partial", "met claimed without evidence"
        rows.append({"domain": d, "status": st, "blocking": bool(item.get("blocking", blocking_default)),
                     "evidence": item.get("evidence", ""), "owner": item.get("owner", ""), "note": note})
    for d in set(got) - set(domains):
        rows.append({"domain": d, "status": str(got[d].get("status")), "blocking": bool(got[d].get("blocking", False)),
                     "evidence": got[d].get("evidence", ""), "note": "extra domain"})
    blockers = [r for r in rows if r["blocking"] and r["status"] == "not_met"]
    conds = [r for r in rows if r not in blockers and r["status"] in ("partial", "not_met")]
    rec = "Not ready" if blockers else ("Ready with conditions" if conds else "Ready")
    return {"service": ev.get("service"), "recommendation": rec, "blocking_gaps": [r["domain"] for r in blockers],
            "conditions": [r["domain"] for r in conds], "domains": rows, "errors": errors}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("evidence"); ap.add_argument("--extra-checks"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        ev = yaml.safe_load(open(a.evidence, encoding="utf-8")) or {}
        extra = yaml.safe_load(open(a.extra_checks, encoding="utf-8")) if a.extra_checks else {}
    except (OSError, yaml.YAMLError) as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    r = score(ev, extra)
    if r["errors"]:
        print("Input error:\n- " + "\n- ".join(r["errors"]), file=sys.stderr); sys.exit(2)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"{r['service']}: {r['recommendation']}")
        for row in r["domains"]:
            flag = "BLOCKING" if row["blocking"] and row["status"] == "not_met" else ""
            print(f"  {row['domain']:28} {row['status']:9} {flag:8} {row.get('note', '')}")
    sys.exit(1 if r["recommendation"] == "Not ready" else 0)


if __name__ == "__main__":
    main()
