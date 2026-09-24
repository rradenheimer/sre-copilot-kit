# Azure DevOps tenant notes

Read this file only when the active client overlay declares an Azure DevOps tenant.

- Inputs: Azure Monitor alert rule exports (`az monitor scheduled-query list`, `az monitor metrics alert list`),
  action groups, and fired-alert history from Azure Resource Graph (`alertsmanagementresources`).
- Check action group routing: pages to on-call vs. email-only; rules with no action group are orphaned.
- Findings become work items tagged `sre-alert-hygiene` via `sre-ado-reliability-backlog`.
