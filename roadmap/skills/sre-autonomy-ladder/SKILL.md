---
name: sre-autonomy-ladder
description: Promotes proven runbook steps through autonomy levels — suggest, execute with approval, execute automatically when reversible — and demotes them when the error budget is low or the blast radius grows. Use when a team wants to automate remediation, auto-heal, or reduce toil from repeated runbook steps.
metadata:
  status: draft
  roadmap_id: R3
---

# Closed-loop remediation with graduated autonomy (draft, R3)

This is a design draft, not an active skill. It lives in `roadmap/skills/` so Copilot does not load it.
Check prerequisites with `sre-roadmap-readiness` before starting work on it.

## Workflow (proposed)

1. Inventory candidate steps from `runbook_lint.py` output (automation: scriptable).
2. Each step gets a record in `out/autonomy/ladder.yaml`: level (0 suggest, 1 approve, 2 auto-reversible), verification command, rollback command, blast radius, success history.
3. Promotion needs N successful approved runs (default 10) with verified outcomes and a tested rollback; demotion is automatic after one failed verification.
4. The guardrail hook reads `ladder.yaml`: level 2 steps are allowed only when `budget_forecast.py` shows budget remaining above the policy floor.

## Guardrails

- Only reversible, verifiable actions can reach level 2; destructive actions stay at level 1 forever.
- Autonomy never exceeds the client's written policy; the hook, not the model, enforces the level.
- Every automatic action is logged with its verification result for audit.

## Exit criteria to promote

Hook extension implemented and tested; one runbook step run at level 1 ten times with verified outcomes on a pilot client.

Promotion follows `roadmap/README.md`: tests, trigger evals, champion review, then move to `.github/skills/`.
