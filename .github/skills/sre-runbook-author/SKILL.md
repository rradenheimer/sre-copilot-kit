---
name: sre-runbook-author
description: Creates and validates operational runbooks and playbooks from interviews, wiki pages, shell history, tickets or existing docs. Use whenever a user mentions a runbook, playbook, SOP, on-call guide, troubleshooting steps, "how do we fix X", or asks to review, standardize or automate existing operational procedures.
---

# Runbook Author & Validator

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Runbooks fail when they are ambiguous, unverifiable or unsafe at 3 a.m. This skill turns tribal knowledge
into runbooks a new on-call engineer can follow, and flags steps that should become automation.

## Before starting

- Run `sre-telemetry-sanitizer` on shell history, tickets and logs.
- Use the client overlay runbook template if present; otherwise `assets/runbook-template.md`.

## Workflow

1. Identify the alert or symptom the runbook serves, and the service it covers.
2. Structure: Symptoms → Impact check → Diagnosis → Mitigation → Verification → Rollback → Escalation.
3. Write each step as one action with the exact command or console path and the expected result.
4. Validate every step against `references/runbook-checks.md`:
   - Ambiguity ("check the logs" with no where or what)
   - Missing verification after a change
   - Destructive commands (delete, drain, failover, restart all) without a safeguard or confirmation
   - Steps requiring privileged or break-glass access — mark them clearly with the approval required
   - Hard-coded values that should be parameters
5. Score automation potential per step (manual / scriptable / auto-remediable) for the toil backlog.

## Deterministic checks

Use the scripts for anything exact; do not recompute their results by hand.

- `python ${SKILL_PATH}/scripts/runbook_lint.py <runbook>.md` replaces the manual checklist pass in step 4. Its automation scores feed step 5.

## Output format

The runbook, then a validation report table: step, issue, severity, suggested fix.

## Guardrails

- Never remove a safety step from an existing runbook without flagging it.
- Do not invent commands for tools you cannot confirm the client uses; mark as TODO for the owner.

## Resources

- [scripts/runbook_lint.py](./scripts/runbook_lint.py) — safety and usability checks with automation scoring (built)
- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
- Planned (not yet built): `assets/runbook-template.md`
- Planned (not yet built): `references/runbook-checks.md` — validation checklist with examples
