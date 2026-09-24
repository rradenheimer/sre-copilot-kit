---
name: sre-ado-reliability-backlog
description: Creates, updates and reports on reliability work in Azure Boards — postmortem action items, alert hygiene fixes, toil automation, PRR gaps and SLO work — using the client's area paths, tags, work item types and fields. Use whenever a user wants action items, findings or recommendations turned into Azure DevOps work items, asks for a WIQL query, reliability backlog report, stale or unowned reliability work, or wants to link work items to incidents, PRs or pipeline runs.
---

# ADO Reliability Backlog Manager

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Reliability findings only matter when they land in the backlog teams actually work from. This skill turns
outputs of other sre-* skills into well-formed Azure Boards work items and keeps that backlog visible.

## Before starting

- Load the ADO client overlay: org, project, process template, work item types, area paths, required
  fields and the tag convention (default `sre`, plus source tags such as `sre-postmortem`).
- Check the tenant profile in the overlay. Profile C (restricted) is read-only: produce the payload file
  for a human to import, never call the API.

## Workflow: create work items

1. Collect items from the source skill (postmortem actions, alert hygiene rows, PRR gaps, toil list).
2. Write them to a JSON file following `references/item-schema.md` (title, type, description,
   acceptance criteria, priority, area path, tags, optional parent and links).
3. Run `python ${SKILL_PATH}/scripts/work_items.py plan items.json --overlay .github/skills/client-overlay-ado/references/ado-overlay.json`. It validates fields against the
   overlay and prints the exact JSON Patch payloads. This is the default and makes no API calls.
4. Show the user the plan summary table and ask for confirmation. Explain any validation errors.
5. Only after explicit confirmation, and only for Profile A or B with write access in the overlay, run
   `python ${SKILL_PATH}/scripts/work_items.py apply items.json --overlay .github/skills/client-overlay-ado/references/ado-overlay.json --confirm`. Credentials come from
   `ADO_TOKEN` (Entra access token or PAT) in the environment; never ask the user to paste a token in chat.
   If the local ADO MCP server is connected, its work item tools may be used instead, with the same confirmation step.
6. Report the created IDs and links.

## Workflow: report

Use `references/wiql-library.md` for reliability queries (open sre work by age, unowned items, overdue
postmortem actions, items by source). Summarize counts, oldest items and owners-by-area; flag items older
than the overlay's SLA for reliability work.

## Writing good work items

- Title: verb + object + outcome, under 80 characters ("Add burn-rate alert for checkout availability SLO").
- Acceptance criteria: observable and testable.
- Link back to the source (postmortem, incident work item, PR or pipeline run) so audits can trace it.

## Guardrails

- Never bulk-close, delete or reassign existing work items.
- Never create items without a preview and explicit confirmation.
- Do not put customer data, hostnames or log excerpts in work item text; reference the sanitized source.

## Resources

- [scripts/work_items.py](./scripts/work_items.py) — plan (dry-run) and apply via ADO REST 7.1 (built)
- [references/item-schema.md](./references/item-schema.md) — input format (built)
- [references/wiql-library.md](./references/wiql-library.md) — reliability WIQL queries (built)
