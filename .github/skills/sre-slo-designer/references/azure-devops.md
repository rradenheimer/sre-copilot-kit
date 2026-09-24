# Azure DevOps tenant notes

Read this file only when the active client overlay declares an Azure DevOps tenant.

- Default SLI sources: Application Insights `requests` / `dependencies` (or workspace tables `AppRequests`,
  `AppDependencies`), Azure Monitor platform metrics, availability tests.
- `.github/skills/sre-slo-designer/scripts/burn_rate.py --format kql --table AppRequests` emits burn-rate queries; for workspace tables use
  the `Success` column instead of `success` and `TimeGenerated` instead of `timestamp`.
- Emit alerts as Bicep `Microsoft.Insights/scheduledQueryRules` resources so they ship through the client's
  pipelines, not portal clicks.
- For deployment gating, provide the same query for an Azure Monitor check on the production ADO environment
  (hand off to `sre-ado-pipeline-reliability`).
