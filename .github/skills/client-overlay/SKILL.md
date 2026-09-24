---
name: client-overlay
description: Client-specific context for engagement CLIENTCODE. Use alongside any sre-* skill whenever work concerns CLIENTCODE systems, incidents, SLOs, runbooks, alerts, changes or compliance evidence. Supplies the client's severity matrix, observability stack, templates, terminology, escalation paths, sanitization patterns and data-handling rules.
---

# Client Overlay — CLIENTCODE

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Use this overlay to adapt firm core skills to this client. Where this file conflicts with a core skill's
defaults, this file wins, except for data-handling guardrails, where the stricter rule wins.

## Engagement facts (fill in)

- Engagement code: TODO (never the client's legal name in restricted engagements)
- Data classification ceiling: TODO (e.g., Public / Internal / CUI / ITAR — stop if exceeded)
- Approved AI surface: TODO (Copilot plan, residency region, allowed models, VS Code or Copilot CLI in client VDI)
- Compliance frameworks in scope: TODO (FedRAMP Moderate, SOC 2, PCI DSS, HIPAA...)
- Observability stack: TODO (Splunk / Datadog / Prometheus+Grafana / Azure Monitor / CloudWatch...)
- Ticketing / change system: TODO
- Incident comms channels and cadence: TODO

## Deterministic checks

Use the scripts for anything exact; do not recompute their results by hand.

- `python ${SKILL_PATH}/scripts/overlay_check.py` (run from the repository root) must report OK before first use on an engagement.

## Resources

- [scripts/overlay_check.py](./scripts/overlay_check.py) — pre-deployment check of both client overlays (built)
- Planned (not yet built): `references/severity-matrix.md` — client SEV definitions and paging rules
- Planned (not yet built): `references/terminology.md` — internal names, service catalog aliases
- Planned (not yet built): `references/escalation.md` — roles, not personal contact details
- Planned (not yet built): `references/sanitizer-patterns.yaml` — codenames, hostname and account patterns for the sanitizer
- Planned (not yet built): `assets/postmortem-template.md`, `assets/runbook-template.md`, `assets/status-update-templates.md`
- Planned (not yet built): `references/policy-as-code.md` — OPA/Sentinel/Kyverno rules the change reviewer checks against
- Planned (not yet built): `references/prr-mandatory-checks.md`

## Rules

- Never copy content from this overlay into firm core repositories or other client overlays.
- If a task would send data above the classification ceiling to the model, stop and tell the user.
