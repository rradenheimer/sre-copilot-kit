---
name: client-overlay-ado
description: Azure DevOps context for engagement CLIENTCODE. Use alongside any sre-* skill whenever work concerns CLIENTCODE's Azure DevOps organization, pipelines, boards, repos, environments, service connections, or Azure Monitor and Log Analytics. Supplies the tenant profile, ADO org and project, process template, work item conventions, production environments, required pipeline templates, KQL workspaces and data-handling rules.
---

# ADO Client Overlay — CLIENTCODE

This overlay extends the base client overlay (`client-overlay`) for Azure DevOps tenants.
Where it conflicts with a core skill's defaults, it wins, except for data-handling guardrails, where the
stricter rule wins.

## Tenant profile

Set in `references/ado-overlay.json` (machine-readable; scripts read it). Summary:

| Setting | Value |
| --- | --- |
| Profile | TODO: A (commercial) / B (regulated) / C (restricted) |
| ADO flavor | TODO: Azure DevOps Services / Azure DevOps Server (version) |
| Cloud | TODO: Azure commercial / Azure Government / on-premises |
| Copilot plan and policy | TODO: Business / Enterprise; data residency region; FedRAMP model restriction (yes/no); approved models |
| ADO access path | TODO: remote ADO MCP server / local ADO MCP server / exports only (Profile C) |
| Write access | TODO: true only for Profile A/B with signed client approval |

## Profile rules

- **A (commercial):** Copilot Business or Enterprise with the client's approved-model policy. Remote ADO MCP
  server. Writes only through `sre-backlog-manager` after preview and explicit confirmation.
- **B (regulated):** As A, plus Copilot data residency (US or EU) enforced on the client's GitHub Enterprise
  Cloud, work only inside the client VDI, and every export passes the sanitizer.
- **C (restricted):** Use only the `sre-restricted` agent. No MCP servers, no ADO writes, edits only under
  `out/`. Use Copilot only if the client's authorizing official has accepted the FedRAMP Moderate model
  restriction for this data; otherwise do not use AI on this engagement.

Tool lists in `.github/agents/` are guardrails, not security boundaries. Enforce the profile with the
engineer's ADO permissions (Readers for Profile C, no Contributor on pipelines or policies for any profile).

## Conventions (fill in)

- Process template: TODO (Agile / Scrum / CMMI / inherited custom)
- Incident work item type and tag: TODO (e.g., Bug + tag `incident`)
- Reliability tag convention: `sre`, plus `sre-postmortem`, `sre-alert-hygiene`, `sre-prr`, `sre-toil`
- Area paths in scope: TODO
- Production environments: TODO (names used by pipeline linter `--prod-env`)
- Protected branches: TODO (e.g., `main`, `release/*`)
- Required `extends` template: TODO (repo, path, pinned tag)
- Log Analytics workspaces and App Insights resources: TODO (names, not keys)
- Change management system of record: TODO (ADO approvals only, or ServiceNow linked)

## Readiness check

Before first use, run `python .github/skills/client-overlay/scripts/overlay_check.py` from the repository root.
It must report OK: no placeholders, a valid profile, and no write access in Profile C.

## Resources

- [references/ado-overlay.json](./references/ado-overlay.json) — machine-readable settings for scripts (template provided)
- [references/sanitizer-patterns.yaml](./references/sanitizer-patterns.yaml) — ADO/Azure identifiers to redact (template provided)
