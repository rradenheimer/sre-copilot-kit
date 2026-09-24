---
name: sre-change-risk-model
description: Trains and applies a per-client model that predicts which production changes will fail, from diff size, services touched, timing, service criticality and test signals, and uses the score to set canary duration and approval depth. Use when a team asks for change risk scores, predictive deployment gating, or which changes need extra review.
metadata:
  status: draft
  roadmap_id: R5
---

# Change risk prediction (draft, R5)

This is a design draft, not an active skill. It lives in `roadmap/skills/` so Copilot does not load it.
Check prerequisites with `sre-roadmap-readiness` before starting work on it.

## Workflow (proposed)

1. Build a feature table from pipeline runs and PRs: lines changed, files and services touched, hour and weekday, criticality tier, test pass rate, time since last deploy.
2. Labels come from DORA attribution (`caused_incident`); require the R5 readiness thresholds before training.
3. Start with an interpretable model (logistic regression or gradient-boosted trees with feature importance); evaluate with time-based splits, never random splits.
4. Output a calibrated probability and the top three contributing features; map score bands to canary duration and reviewers.

## Guardrails

- Train and host inside the client's boundary; never pool data across clients.
- The score adjusts review depth; it never blocks a change on its own and never ranks individual engineers.
- Retrain on a schedule and monitor calibration; disable the gate if calibration drifts beyond the agreed bound.

## Exit criteria to promote

Backtest over 6 months shows precision and recall agreed with the client, with calibration error under the agreed bound.

Promotion follows `roadmap/README.md`: tests, trigger evals, champion review, then move to `.github/skills/`.
