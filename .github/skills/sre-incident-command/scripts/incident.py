#!/usr/bin/env python3
"""Incident bookkeeping: timeline from chat/bridge notes, key durations, severity proposal.

  incident.py timeline NOTES.txt [--date 2026-09-23] [--json]
  incident.py severity FACTS.json --matrix MATRIX.json [--json]

timeline: extracts lines that start with a time ("14:02", "14:02:10", "2026-09-23T14:02Z", "[14:02]"),
sorts them in UTC, tags milestones (detected, declared, mitigated, resolved) by keyword, and computes
time to detect/declare/mitigate/resolve from the first event.
severity: picks the most severe level whose criteria the facts meet. Matrix format:
  {"levels": [{"name": "SEV1", "any": {"users_affected_pct": 25, "revenue_impact": true, "data_loss": true}}, ...]}
  Numeric criteria are thresholds (fact >= value); booleans must match true. Levels are listed most severe first.
Exit codes: 0 ok, 2 input error.
"""
import argparse, json, re, sys
from datetime import datetime, timedelta, timezone

TIME_RE = re.compile(r"^\s*\[?(?P<ts>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?|\d{1,2}:\d{2}(?::\d{2})?)\]?\s*(?:UTC|Z)?\s*[-–:|]?\s*(?P<text>.+)$")
MILESTONES = [
    ("resolved", r"\b(resolved|all clear|fully recovered|closing the incident)\b"),
    ("mitigated", r"\b(mitigat\w*|rolled back|rollback complete|failover complete|error rate (back|returned) to normal|recovering)\b"),
    ("declared", r"\b(declar\w*|sev ?[0-4] (opened|called)|incident (opened|started)|paging (ic|incident commander))\b"),
    ("detected", r"\b(alert(ed)?|paged|page fired|detected|customer report\w*|noticed)\b"),
]


def parse_ts(raw, day):
    raw = raw.replace(" ", "T") if re.match(r"\d{4}-", raw) else raw
    if re.match(r"\d{4}-", raw):
        raw = raw.replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    parts = [int(p) for p in raw.split(":")]
    h, m, s = parts[0], parts[1], parts[2] if len(parts) > 2 else 0
    return datetime(day.year, day.month, day.day, h, m, s, tzinfo=timezone.utc)


def timeline(text, day):
    events, prev = [], None
    for line in text.splitlines():
        m = TIME_RE.match(line)
        if not m:
            continue
        ts = parse_ts(m.group("ts"), day)
        if prev and ts < prev and not re.match(r"\d{4}-", m.group("ts")) and (prev - ts) > timedelta(hours=12):
            ts += timedelta(days=1)  # notes crossed midnight
        prev = ts
        body = m.group("text").strip()
        tag = next((name for name, pat in MILESTONES if re.search(pat, body, re.I)), "")
        events.append({"time_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"), "milestone": tag, "text": body})
    events.sort(key=lambda e: e["time_utc"])
    first = {}
    for e in events:
        if e["milestone"] and e["milestone"] not in first:
            first[e["milestone"]] = e["time_utc"]
    start = events[0]["time_utc"] if events else None
    def mins(a, b):
        if not a or not b:
            return None
        d = (datetime.fromisoformat(b.replace("Z", "+00:00")) - datetime.fromisoformat(a.replace("Z", "+00:00"))).total_seconds() / 60
        return round(d, 1)
    base = first.get("detected", start)
    durations = {
        "time_to_declare_min": mins(base, first.get("declared")),
        "time_to_mitigate_min": mins(base, first.get("mitigated")),
        "time_to_resolve_min": mins(base, first.get("resolved")),
    }
    missing = [m for m in ("detected", "declared", "mitigated", "resolved") if m not in first]
    return {"events": events, "milestones": first, "durations": durations, "missing_milestones": missing}


def severity(facts, matrix):
    for lvl in matrix.get("levels", []):
        hits = []
        for k, v in (lvl.get("any") or {}).items():
            f = facts.get(k)
            if isinstance(v, bool):
                if f is True and v:
                    hits.append(k)
            elif isinstance(v, (int, float)) and isinstance(f, (int, float)) and f >= v:
                hits.append(f"{k}>={v}")
        if hits:
            return {"proposed": lvl["name"], "criteria_met": hits, "status": "proposed - IC must confirm"}
    return {"proposed": (matrix.get("levels") or [{"name": "none"}])[-1]["name"], "criteria_met": [],
            "status": "no criteria met; lowest level proposed - IC must confirm"}


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("timeline"); t.add_argument("notes"); t.add_argument("--date"); t.add_argument("--json", action="store_true")
    s = sub.add_parser("severity"); s.add_argument("facts"); s.add_argument("--matrix", required=True); s.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        if a.cmd == "timeline":
            day = datetime.strptime(a.date, "%Y-%m-%d") if a.date else datetime.now(timezone.utc)
            out = timeline(open(a.notes, encoding="utf-8").read(), day)
        else:
            out = severity(load(a.facts), load(a.matrix))
    except (OSError, ValueError) as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    if a.json:
        print(json.dumps(out, indent=2)); return
    if a.cmd == "severity":
        print(f"{out['proposed']} ({out['status']}); criteria: {', '.join(out['criteria_met']) or 'none'}"); return
    for e in out["events"]:
        print(f"{e['time_utc']}  {e['milestone']:<9} {e['text']}")
    print("\n" + ", ".join(f"{k}={v}" for k, v in out["durations"].items()))
    if out["missing_milestones"]:
        print("Missing milestones: " + ", ".join(out["missing_milestones"]))


if __name__ == "__main__":
    main()
