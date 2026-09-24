---
name: sre-incident-similarity
description: Finds past incidents similar to a current one using embeddings over sanitized postmortems and incident records, and clusters contributing factors to reveal systemic weaknesses. Use when an engineer asks 'have we seen this before', wants known fixes, or asks for recurring themes across incidents.
metadata:
  status: draft
  roadmap_id: R7
---

# Incident similarity search (draft, R7)

This is a design draft, not an active skill. It lives in `roadmap/skills/` so Copilot does not load it.
Check prerequisites with `sre-roadmap-readiness` before starting work on it.

## Workflow (proposed)

1. Index sanitized postmortems (passing `postmortem_lint.py`) with an embedding model approved for the client's boundary.
2. At query time, embed the current symptoms and return the top five matches with their triggers, fixes and action item status.
3. Quarterly, cluster contributing factors and report recurring themes with the incidents behind each.

## Guardrails

- Only sanitized text is indexed; the token map is never indexed.
- Matches are presented as leads to check, not conclusions.

## Exit criteria to promote

On 10 held-out past incidents, a relevant match appears in the top five at least 7 times.

Promotion follows `roadmap/README.md`: tests, trigger evals, champion review, then move to `.github/skills/`.
