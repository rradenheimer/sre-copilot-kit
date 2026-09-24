---
name: sre-continuous-agents
description: Runs scheduled reliability work without a human prompt — nightly governance and drift scans, weekly DORA and error budget reports, backlog grooming, and pull requests for low-risk linter fixes. Use when a team wants recurring reliability reports or automated hygiene PRs.
metadata:
  status: draft
  roadmap_id: R4
---

# Continuous reliability agents (draft, R4)

This is a design draft, not an active skill. It lives in `roadmap/skills/` so Copilot does not load it.
Check prerequisites with `sre-roadmap-readiness` before starting work on it.

## Workflow (proposed)

1. Schedule jobs in the client's pipeline (or Copilot CLI in programmatic mode) that call the kit's scripts: `ado_governance.py`, `dora.py`, `budget_forecast.py`, `alert_stats.py`.
2. Publish a digest to `out/digests/<date>.md` and, with approval, to the ADO Wiki.
3. For linter findings with a mechanical fix (PR005 pin a template ref, PR006 task version), open a PR on a branch; never merge.

## Guardrails

- Scheduled runs use a dedicated least-privilege identity, never an engineer's token.
- Automated PRs are limited to an allowlist of mechanical fixes and always require human review.
- Digests contain sanitized data only.

## Exit criteria to promote

Four consecutive weekly digests accepted by a pilot team; at least five automated PRs merged after review with no reverts.

Promotion follows `roadmap/README.md`: tests, trigger evals, champion review, then move to `.github/skills/`.
