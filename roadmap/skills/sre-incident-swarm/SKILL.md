---
name: sre-incident-swarm
description: Coordinates specialist sub-agents during a live incident — telemetry analysis, change correlation, dependency health and stakeholder comms — posting evidence to one shared board for the human incident commander. Use when an incident is declared and the engineer asks for a parallel investigation or a hypothesis board.
metadata:
  status: draft
  roadmap_id: R2
---

# Multi-agent incident response (draft, R2)

This is a design draft, not an active skill. It lives in `roadmap/skills/` so Copilot does not load it.
Check prerequisites with `sre-roadmap-readiness` before starting work on it.

## Workflow (proposed)

1. Incident commander agent starts four sub-agents with narrow tool sets: telemetry (KQL read), changes (ADO pipelines and PRs read), dependencies (health endpoints and topology read), comms (drafts only).
2. Each sub-agent posts findings as `{hypothesis, evidence, confidence, source}` to `out/incident-<id>/board.json`.
3. The commander ranks hypotheses by evidence, not confidence wording, and presents the top three to the human IC.
4. `incident.py timeline` keeps the timeline; `sre-postmortem-author` takes over at resolution.

## Guardrails

- Sub-agents are read-only; any action goes through the Backlog Manager or a human.
- Agents rank hypotheses; they never declare root cause.
- Every evidence item cites a query, run ID or file; unsupported claims are dropped from the board.

## Exit criteria to promote

Three replayed past incidents where the board's top hypothesis matched the documented trigger, with no unsupported claims.

Promotion follows `roadmap/README.md`: tests, trigger evals, champion review, then move to `.github/skills/`.
