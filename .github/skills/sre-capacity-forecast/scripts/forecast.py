#!/usr/bin/env python3
"""Forecast when a utilization series crosses a threshold (linear trend + weekly seasonality).

  forecast.py SERIES.json|csv [--threshold 80] [--horizon 180] [--json]
SERIES: [{"date": "2026-06-01", "value": 61.5}, ...] or CSV with header date,value. One point per day,
ideally the daily peak (p95/max). Uses least squares on the trend and day-of-week mean residuals, then reports
the projected crossing date with an approximate 95% band (+/- 1.96 x residual std). Needs >= 28 points for a
confident result. Exit 1 if the central estimate crosses within the horizon, 2 on input error.
"""
import argparse, csv, json, statistics, sys
from datetime import date, timedelta


def load(path):
    if path.lower().endswith(".csv"):
        with open(path, encoding="utf-8") as fh:
            rows = [{"date": r["date"], "value": float(r["value"])} for r in csv.DictReader(fh)]
    else:
        rows = json.load(open(path, encoding="utf-8"))
    pts = sorted((date.fromisoformat(r["date"][:10]), float(r["value"])) for r in rows)
    if len(pts) < 7:
        raise ValueError("need at least 7 daily points")
    return pts


def fit(pts):
    d0 = pts[0][0]
    xs = [(d - d0).days for d, _ in pts]; ys = [v for _, v in pts]
    slope, intercept = statistics.linear_regression(xs, ys)
    resid = [y - (slope * x + intercept) for x, y in zip(xs, ys)]
    dow = {}
    for (d, _), r in zip(pts, resid):
        dow.setdefault(d.weekday(), []).append(r)
    season = {k: statistics.mean(v) for k, v in dow.items()} if len(pts) >= 21 else {}
    adj = [r - season.get(d.weekday(), 0) for (d, _), r in zip(pts, resid)]
    sd = statistics.stdev(adj) if len(adj) > 2 else 0.0
    return d0, slope, intercept, season, sd


def crossing(d0, slope, intercept, season, offset, threshold, start, horizon):
    for i in range(horizon + 1):
        d = start + timedelta(days=i)
        x = (d - d0).days
        if slope * x + intercept + season.get(d.weekday(), 0) + offset >= threshold:
            return d
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("series"); ap.add_argument("--threshold", type=float, default=80.0)
    ap.add_argument("--horizon", type=int, default=180); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        pts = load(a.series)
    except (OSError, ValueError, KeyError) as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    d0, slope, intercept, season, sd = fit(pts)
    last = pts[-1][0]; start = last + timedelta(days=1)
    band = 1.96 * sd
    central = crossing(d0, slope, intercept, season, 0, a.threshold, start, a.horizon)
    early = crossing(d0, slope, intercept, season, band, a.threshold, start, a.horizon)
    late = crossing(d0, slope, intercept, season, -band, a.threshold, start, a.horizon)
    already = max(v for _, v in pts[-7:]) >= a.threshold
    r = {"points": len(pts), "from": str(pts[0][0]), "to": str(last), "threshold": a.threshold,
         "trend_per_week": round(slope * 7, 3), "residual_std": round(sd, 3), "weekly_seasonality": bool(season),
         "already_breached_last_7d": already,
         "crossing_central": str(central) if central else None,
         "crossing_earliest": str(early) if early else None,
         "crossing_latest": str(late) if late else None,
         "confidence": "low" if len(pts) < 28 else "normal"}
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"{r['points']} points {r['from']}..{r['to']}; trend {r['trend_per_week']:+}/week; confidence {r['confidence']}")
        if already:
            print(f"Threshold {a.threshold} already breached in the last 7 days.")
        if central:
            print(f"Projected to cross {a.threshold}: {central} (95% band {early or 'beyond'} .. {late or 'beyond horizon'})")
        else:
            print(f"No crossing within {a.horizon} days (earliest plausible: {early or 'none'}).")
    sys.exit(1 if central or already else 0)


if __name__ == "__main__":
    main()
