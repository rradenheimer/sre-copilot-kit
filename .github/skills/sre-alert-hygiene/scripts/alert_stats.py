#!/usr/bin/env python3
"""Per-alert noise statistics and classification from a normalized alert export.

  alert_stats.py EVENTS.json [--rules RULES.json] [--days 28] [--json]
EVENTS.json: [{"alert": "name", "fired": ISO, "resolved": ISO|null, "acked": bool, "paged": bool,
               "incident_id": str|null, "action_taken": bool}]
RULES.json (optional): [{"alert": "name", "owner": str|null, "runbook": str|null, "enabled": bool}]
Classes: actionable, informational, flapping, orphaned, noisy. Thresholds are CLI flags and documented in
references/classification-rules.md. Exit 2 on input error.
"""
import argparse, json, statistics, sys
from collections import defaultdict
from datetime import datetime


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def analyze(events, rules, days, flap_min, auto_min, action_min):
    by = defaultdict(list)
    for e in events:
        by[e["alert"]].append(e)
    meta = {r["alert"]: r for r in rules}
    out = []
    for name in sorted(set(by) | set(meta)):
        ev = sorted(by.get(name, []), key=lambda e: e["fired"])
        n = len(ev)
        pages = sum(1 for e in ev if e.get("paged"))
        durations = [(ts(e["resolved"]) - ts(e["fired"])).total_seconds() / 60 for e in ev if e.get("resolved")]
        short = sum(1 for d in durations if d < flap_min)
        auto = sum(1 for e in ev if e.get("resolved") and not e.get("acked"))
        acted = sum(1 for e in ev if e.get("action_taken") or e.get("incident_id"))
        r = meta.get(name, {})
        stats = {
            "alert": name, "fires": n, "pages": pages, "pages_per_week": round(pages / (days / 7), 2),
            "median_open_min": round(statistics.median(durations), 1) if durations else None,
            "auto_resolve_pct": round(100 * auto / n, 1) if n else 0,
            "flap_pct": round(100 * short / len(durations), 1) if durations else 0,
            "action_pct": round(100 * acted / n, 1) if n else 0,
        }
        if r and (not r.get("owner") or not r.get("runbook")):
            cls, rec = "orphaned", "Assign an owner and runbook, or delete."
        elif n == 0:
            cls, rec = ("orphaned", "Never fired in the window; confirm it still monitors something real.") if r else ("unknown", "")
        elif stats["flap_pct"] >= 50:
            cls, rec = "flapping", f"Add a duration (for:) of at least {flap_min} min or hysteresis."
        elif stats["action_pct"] >= action_min:
            cls, rec = "actionable", "Keep; check it has a runbook link."
        elif pages and stats["auto_resolve_pct"] >= auto_min:
            cls, rec = "noisy", "Pages but resolves on its own; downgrade to ticket or replace with an SLO burn-rate alert."
        else:
            cls, rec = "informational", "Move to a dashboard or ticket; do not page."
        stats.update({"class": cls, "recommendation": rec,
                      "pages_saved_per_week": stats["pages_per_week"] if cls in ("noisy", "informational", "flapping") else 0})
        out.append(stats)
    out.sort(key=lambda s: -s["pages_per_week"])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("events"); ap.add_argument("--rules"); ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--flap-min", type=float, default=5, help="open time under this counts as a flap (minutes)")
    ap.add_argument("--auto-resolve-pct", type=float, default=80); ap.add_argument("--action-pct", type=float, default=30)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        events = json.load(open(a.events, encoding="utf-8"))
        rules = json.load(open(a.rules, encoding="utf-8")) if a.rules else []
        res = analyze(events, rules, a.days, a.flap_min, a.auto_resolve_pct, a.action_pct)
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    total = sum(r["pages_per_week"] for r in res); saved = sum(r["pages_saved_per_week"] for r in res)
    if a.json:
        print(json.dumps({"pages_per_week": round(total, 2), "projected_pages_per_week": round(total - saved, 2), "alerts": res}, indent=2)); return
    print(f"Pages/week now {total:.1f}; after recommendations {total - saved:.1f}")
    print(f"{'alert':30} {'class':13} {'pages/wk':>8} {'auto%':>6} {'flap%':>6} {'act%':>5}")
    for r in res:
        print(f"{r['alert'][:30]:30} {r['class']:13} {r['pages_per_week']:>8} {r['auto_resolve_pct']:>6} {r['flap_pct']:>6} {r['action_pct']:>5}")


if __name__ == "__main__":
    main()
