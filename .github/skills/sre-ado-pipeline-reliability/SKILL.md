---
name: sre-ado-pipeline-reliability
description: Reviews and authors Azure Pipelines YAML for safe, reliable delivery — environments, approvals and checks, Azure Monitor gates, canary and rolling strategies, rollback stages, pinned templates and tasks, and extends-template governance. Use whenever a user shares an azure-pipelines.yml or pipeline template, asks to add deployment gates, approvals, canary, rollback or SLO checks to a pipeline, or asks whether an Azure DevOps pipeline is safe for production.
---

# ADO Pipeline Reliability Reviewer

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Most production incidents follow a deployment, and in ADO tenants the pipeline is where deployment safety
is enforced. This skill finds the gaps deterministically, then explains and fixes them.

## Before starting

- Run `sre-telemetry-sanitizer` if the YAML contains subscription IDs, service connection names or hostnames.
- Load the ADO client overlay (`client-overlay-ado`) for required templates, environments and gates.

## Workflow

1. Run `python ${SKILL_PATH}/scripts/pipeline_lint.py <file.yml> [--json]`. It reports findings with rule IDs from
   `references/rules.md`. Trust the script for what is present or missing; do not re-derive it by reading.
2. Note what YAML cannot show. Approvals and checks (approvals, business hours, Azure Monitor gates,
   required templates) are configured on the **environment** in ADO, not in YAML. Ask for, or fetch via the
   ADO MCP server / `az devops`, the environment's checks before concluding a gate is missing.
3. Rate each finding using the severity in `references/rules.md`, adjusted for context (a dev-only pipeline
   does not need production gates).
4. Propose fixes as YAML diffs. Use `assets/safe-deploy-template.yml` as the reference pattern:
   stages Build → Deploy canary → Verify (SLO gate) → Deploy remaining → with an explicit rollback path.
5. For SLO-based gates, hand off to `sre-slo-designer` for the KQL burn-rate query the Azure Monitor check runs.

## Output format

Summary line (production-ready / ready with fixes / not ready), findings table
(rule, location, severity, why it matters, fix), then YAML diffs.

## Guardrails

- Never remove existing approvals, checks or `extends` templates in proposed YAML.
- Never write secrets into YAML; use variable groups linked to Key Vault or secure files.
- Changes to pipelines go through a pull request; never suggest editing the default branch directly.

## Resources

- [scripts/pipeline_lint.py](./scripts/pipeline_lint.py) — deterministic YAML checks (built)
- [references/rules.md](./references/rules.md) — rule catalog with severities (built)
- [assets/safe-deploy-template.yml](./assets/safe-deploy-template.yml) — reference multi-stage pattern (built)
