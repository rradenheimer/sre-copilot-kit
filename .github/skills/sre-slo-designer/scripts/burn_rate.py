#!/usr/bin/env python3
"""Multiwindow, multi-burn-rate alert thresholds for an SLO.

  burn_rate.py --slo 99.9 [--window-days 30] [--format table|json|kql] [--table requests]

Default policy (budget consumed within the long window -> severity):
  2% in 1h  (short 5m)  -> page
  5% in 6h  (short 30m) -> page
  10% in 3d (short 6h)  -> ticket
burn rate = budget_fraction * window_hours / long_window_hours
error-rate threshold = burn rate * (1 - SLO)
"""
import argparse, json

POLICY = [  # (budget fraction, long window h, short window h, severity)
    (0.02, 1, 5 / 60, "page"),
    (0.05, 6, 0.5, "page"),
    (0.10, 72, 6, "ticket"),
]


def fmt_window(h):
    return f"{int(round(h * 60))}m" if h < 1 else (f"{int(h)}h" if h < 24 else f"{int(h / 24)}d")


def thresholds(slo_pct, window_days):
    budget = 1 - slo_pct / 100
    total_h = window_days * 24
    rows = []
    for frac, long_h, short_h, sev in POLICY:
        burn = frac * total_h / long_h
        rows.append({"severity": sev, "budget_consumed_pct": frac * 100, "long_window": fmt_window(long_h),
                     "short_window": fmt_window(short_h), "burn_rate": round(burn, 2),
                     "error_rate_threshold_pct": round(burn * budget * 100, 4)})
    return rows


def kql(rows, table):
    # Application Insights / Log Analytics availability SLI: failed requests / all requests
    out = []
    for r in rows:
        thr = r["error_rate_threshold_pct"] / 100
        out.append(f"""// {r['severity']}: {r['budget_consumed_pct']:g}% of budget in {r['long_window']} (burn {r['burn_rate']}x)
let errRate = (w: timespan) {{ {table} | where timestamp > ago(w)
    | summarize total = count(), failed = countif(success == false)
    | project rate = todouble(failed) / todouble(total) }};
let longRate = toscalar(errRate({r['long_window']}));
let shortRate = toscalar(errRate({r['short_window']}));
print longRate, shortRate, fire = longRate > {thr:.6f} and shortRate > {thr:.6f}""")
    return "\n\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slo", type=float, required=True, help="target, e.g. 99.9")
    ap.add_argument("--window-days", type=int, default=30)
    ap.add_argument("--format", choices=["table", "json", "kql"], default="table")
    ap.add_argument("--table", default="requests", help="KQL table (App Insights 'requests' or workspace 'AppRequests' with Success column)")
    a = ap.parse_args()
    if not 0 < a.slo < 100:
        raise SystemExit("--slo must be between 0 and 100 (exclusive)")
    rows = thresholds(a.slo, a.window_days)
    if a.format == "json":
        print(json.dumps(rows, indent=2))
    elif a.format == "kql":
        print(kql(rows, a.table))
    else:
        print(f"SLO {a.slo}% over {a.window_days}d (error budget {100 - a.slo:.4g}%)")
        print(f"{'severity':8} {'budget':>7} {'long':>5} {'short':>5} {'burn':>6} {'err-rate thr %':>15}")
        for r in rows:
            print(f"{r['severity']:8} {r['budget_consumed_pct']:>6g}% {r['long_window']:>5} {r['short_window']:>5} {r['burn_rate']:>6} {r['error_rate_threshold_pct']:>15}")


if __name__ == "__main__":
    main()
