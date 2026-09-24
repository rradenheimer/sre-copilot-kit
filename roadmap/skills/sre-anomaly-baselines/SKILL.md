---
name: sre-anomaly-baselines
description: Replaces static alert thresholds with seasonal baselines and anomaly scores, and upgrades capacity forecasting to backtested seasonal models. Use when alerts fire on normal daily or weekly patterns, when a team asks for dynamic thresholds or anomaly detection, or when linear capacity forecasts miss seasonality.
metadata:
  status: draft
  roadmap_id: R6
---

# Anomaly detection and dynamic baselines (draft, R6)

This is a design draft, not an active skill. It lives in `roadmap/skills/` so Copilot does not load it.
Check prerequisites with `sre-roadmap-readiness` before starting work on it.

## Workflow (proposed)

1. Decompose each metric into trend, daily and weekly seasonality and residual; score anomalies on the residual.
2. Backtest candidate baselines against past incidents: an anomaly model must catch known incidents without raising pages on normal days.
3. Where Azure Monitor dynamic thresholds fit, configure them instead of building a model; build only where they fall short.
4. Feed anomaly-backed alerts into `alert_stats.py` to confirm the noisy and flapping classes shrink.

## Guardrails

- A baseline never replaces an SLO burn-rate page; it supplements detection.
- Every model ships with its backtest results and a documented false-positive rate.

## Exit criteria to promote

Two services moved to dynamic baselines with pages per week reduced and no missed incidents over 30 days.

Promotion follows `roadmap/README.md`: tests, trigger evals, champion review, then move to `.github/skills/`.
