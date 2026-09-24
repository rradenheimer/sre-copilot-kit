---
name: sre-ado-org-governance
description: Assesses an Azure DevOps organization or project's reliability and security posture — branch policies on protected branches, service connection scope and workload identity federation, agent pool isolation, environment approvals and checks, pipeline permissions, PAT policy and audit streaming. Use whenever a user asks for an Azure DevOps security review, governance or posture assessment, audit readiness of ADO, branch policy or service connection review, or evidence of change-management controls in ADO.
---

# ADO Org Governance Reviewer

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

In ADO tenants, the organization's configuration is itself a production control: it decides who can change
production and how. This skill collects that configuration read-only, evaluates it deterministically,
and turns gaps into control evidence and remediation work.

## Workflow

1. **Collect (read-only).** With a least-privilege identity (Project Collection Valid Users plus read on
   the projects in scope), run
   `python ${SKILL_PATH}/scripts/ado_governance.py collect --org <org_url> --project <name> --out snapshot.json`
   with `ADO_TOKEN` set in the environment. In Profile C tenants, a client admin runs it inside the
   boundary and shares the sanitized snapshot. The org-level settings the REST API does not expose
   (PAT policies, audit streaming, OAuth/SSH policies) are captured with `references/manual-checks.md`.
2. **Evaluate.** `python ${SKILL_PATH}/scripts/ado_governance.py evaluate snapshot.json --protected main --protected release/*`.
   Findings use rule IDs from `references/controls.md`. Trust the script's results.
3. **Interpret.** Explain each High finding's real-world risk (e.g., a subscription-scoped service
   connection lets any pipeline in the project change any resource).
4. **Hand off.** Map findings to controls with `sre-compliance-evidence` (change management, least
   privilege, audit logging) and to work items with `sre-ado-reliability-backlog`.

## Output format

Posture summary (counts by severity), findings table (rule, object, evidence, severity, fix),
manual-check results, and control mapping hand-off.

## Guardrails

- Collection is GET-only. Never change policies, permissions or connections, even when asked; propose changes.
- Never output token values, service connection secrets or full principal lists; summarize.

## Resources

- [scripts/ado_governance.py](./scripts/ado_governance.py) — collect (REST GET) and evaluate (offline) (built)
- [references/controls.md](./references/controls.md) — rule catalog (built)
- [references/manual-checks.md](./references/manual-checks.md) — org settings to verify in the portal (built)
