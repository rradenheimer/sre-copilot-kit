# Azure DevOps tenant notes

Read this file only when the active client overlay declares an Azure DevOps tenant.

Add these ADO checks to the scorecard:

- Deploys through a YAML pipeline using the required `extends` template.
- Production environment has approvals and an Azure Monitor or SLO gate.
- Rollback path exists and has been exercised (run ID as evidence).
- Protected branch policies meet `sre-ado-org-governance` baseline.
- Service connection uses workload identity federation and resource-group scope.
