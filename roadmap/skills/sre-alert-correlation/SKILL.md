---
name: sre-alert-correlation
description: Groups related alerts into one incident thread using time windows and service topology, so on-call sees one problem instead of many pages. Use when on-call is flooded by related alerts during one event, or a team asks for alert grouping, deduplication or event correlation.
metadata:
  status: draft
  roadmap_id: R8
---

# Alert correlation (draft, R8)

This is a design draft, not an active skill. It lives in `roadmap/skills/` so Copilot does not load it.
Check prerequisites with `sre-roadmap-readiness` before starting work on it.

## Workflow (proposed)

1. Load alert events (EVENTS.json format from `alert_stats.py`) and the service dependency map.
2. Group alerts that fire within a window on services connected in the topology; name the group after the most upstream service.
3. Report compression (alerts per group) and check that each past incident maps to exactly one group.

## Guardrails

- Correlation groups notifications; it never suppresses the first page of a new group.
- Topology comes from an owned source of truth, not model inference.

## Exit criteria to promote

Replaying 28 days of events yields at least 3:1 compression with no incident split across groups or merged with another.

Promotion follows `roadmap/README.md`: tests, trigger evals, champion review, then move to `.github/skills/`.
