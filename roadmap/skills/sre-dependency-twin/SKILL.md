---
name: sre-dependency-twin
description: Builds a dependency graph from traces and infrastructure state and simulates failures to predict blast radius and rank game day experiments by expected learning versus risk. Use when planning resilience tests, asking what breaks if a service or region fails, or prioritizing chaos experiments.
metadata:
  status: draft
  roadmap_id: R10
---

# Service dependency twin (draft, R10)

This is a design draft, not an active skill. It lives in `roadmap/skills/` so Copilot does not load it.
Check prerequisites with `sre-roadmap-readiness` before starting work on it.

## Workflow (proposed)

1. Derive edges from distributed traces (caller, callee, call volume, criticality) and from infrastructure state.
2. Simulate single-node and zone failures; propagate impact along edges with timeout and retry behavior where known.
3. Rank experiments for `sre-gameday-planner` by predicted impact uncertainty (most to learn) within the approved blast radius.

## Guardrails

- Simulation results are hypotheses for game days, never evidence of resilience on their own.
- Graph coverage is reported; edges from services without tracing are marked unknown.

## Exit criteria to promote

Predicted blast radius matches observed impact in two real game days.

Promotion follows `roadmap/README.md`: tests, trigger evals, champion review, then move to `.github/skills/`.
