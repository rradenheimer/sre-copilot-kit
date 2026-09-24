#!/usr/bin/env python3
"""Error budget status and exhaustion forecast for one SLO (roadmap R9, preview).

  budget_forecast.py SLI.json --slo 99.9 [--window-days 28] [--trend-days 7] [--as-of YYYY-MM-DD] [--json]
SLI.json: [{"date": "2026-09-01", "good": 998012, "total": 999100}, ...] one row per day (UTC).
Reports budget consumed in the current rolling window, burn rate over the last --trend-days, and the date the
budget runs out if that burn continues (accounting for old days leaving the window). Exit 1 when the budget is
exhausted or projected to run out within the window, 2 on input error.
"""
import argparse, json, sys
from datetime import date, timedelta


def load(path):
    rows = json.load(open(path, encoding="utf-8"))
    out = {}
    for r in rows:
        d = date.fromisoformat(r["date"][:10]); g, t = float(r["good"]), float(r["total"])
        if t < 0 or g < 0 or g > t:
            raise ValueError(f"{d}: need 0 <= good <= total")
        out[d] = (g, t)
    if not out:
        raise ValueError("no rows")
    return out


def forecast(days, slo, window, trend, as_of):
    budget_frac = 1 - slo / 100
    start = as_of - timedelta(days=window - 1)
    win = {d: v for d, v in days.items() if start <= d <= as_of}
    bad = sum(t - g for g, t in win.values()); tot = sum(t for _, t in win.values())
    if tot == 0:
        raise ValueError("no traffic in the window")
    allowed = budget_frac * tot
    consumed = bad / allowed if allowed else float("inf")
    rec = [days[d] for d in sorted(days) if as_of - timedelta(days=trend - 1) <= d <= as_of]
    rbad = sum(t - g for g, t in rec); rtot = sum(t for _, t in rec)
    burn = (rbad / rtot) / budget_frac if rtot else 0.0
    daily_bad = rbad / len(rec) if rec else 0.0
    daily_tot = rtot / len(rec) if rec else 0.0
    exhaust = None
    if consumed < 1 and daily_bad > 0:
        wdays = dict(win)
        for i in range(1, window + 1):
            d = as_of + timedelta(days=i)
            wdays[d] = (daily_tot - daily_bad, daily_tot)
            wdays.pop(d - timedelta(days=window), None)
            b = sum(t - g for g, t in wdays.values()); tt = sum(t for _, t in wdays.values())
            if b >= budget_frac * tt:
                exhaust = d
                break
    return {"slo": slo, "window_days": window, "as_of": str(as_of), "days_in_window": len(win),
            "budget_consumed_pct": round(100 * consumed, 1),
            "budget_remaining_pct": round(max(0.0, 100 * (1 - consumed)), 1),
            "burn_rate_recent": round(burn, 2), "trend_days": trend,
            "exhausted": consumed >= 1,
            "projected_exhaustion": str(exhaust) if exhaust else None,
            "low_confidence": len(win) < window}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sli"); ap.add_argument("--slo", type=float, required=True)
    ap.add_argument("--window-days", type=int, default=28); ap.add_argument("--trend-days", type=int, default=7)
    ap.add_argument("--as-of"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        if not 0 < a.slo < 100:
            raise ValueError("--slo must be between 0 and 100")
        days = load(a.sli)
        as_of = date.fromisoformat(a.as_of) if a.as_of else max(days)
        r = forecast(days, a.slo, a.window_days, a.trend_days, as_of)
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        state = "EXHAUSTED" if r["exhausted"] else f"{r['budget_remaining_pct']}% remaining"
        print(f"SLO {a.slo}% / {a.window_days}d as of {r['as_of']}: {r['budget_consumed_pct']}% consumed ({state})")
        print(f"Burn rate over last {a.trend_days}d: {r['burn_rate_recent']}x")
        if r["projected_exhaustion"]:
            print(f"At this burn the budget runs out on {r['projected_exhaustion']}.")
        elif not r["exhausted"]:
            print("At this burn the budget lasts the full window.")
        if r["low_confidence"]:
            print(f"Low confidence: only {r['days_in_window']} of {a.window_days} days of data.")
    sys.exit(1 if r["exhausted"] or r["projected_exhaustion"] else 0)


if __name__ == "__main__":
    main()
