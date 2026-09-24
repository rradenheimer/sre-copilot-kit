---
name: sre-ai-governance-evidence
description: Produces evidence that AI in operations is controlled — mapping guardrail logs, agent permissions, evaluation results and approvals to NIST AI RMF and ISO/IEC 42001, alongside existing control frameworks. Use when a client's risk, audit or AI governance team asks how AI agents are governed, or when preparing an AI-related audit.
metadata:
  status: draft
  roadmap_id: R12
---

# AI governance evidence (draft, R12)

This is a design draft, not an active skill. It lives in `roadmap/skills/` so Copilot does not load it.
Check prerequisites with `sre-roadmap-readiness` before starting work on it.

## Workflow (proposed)

1. Extend `artifact-to-control-map.yaml` with AI artifact types: guardrail decision log, agent permission snapshot, replay evaluation report, autonomy ladder record.
2. Map them to NIST AI RMF functions and ISO/IEC 42001 controls once the compliance lead has verified the references.
3. Generate coverage with `control_lookup.py` and draft narratives for assessors.

## Guardrails

- Never claim conformance; report evidence coverage for the assessor to judge.
- AI framework mappings require the same compliance-lead verification as the existing map.

## Exit criteria to promote

One AI governance evidence package reviewed by a pilot client's risk team.

Promotion follows `roadmap/README.md`: tests, trigger evals, champion review, then move to `.github/skills/`.
