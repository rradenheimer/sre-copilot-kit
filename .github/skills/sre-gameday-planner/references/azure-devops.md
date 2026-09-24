# Azure DevOps tenant notes

Read this file only when the active client overlay declares an Azure DevOps tenant.

- Prefer Azure Chaos Studio experiments for Azure resources; run them from a manual-trigger pipeline bound to
  an environment with approvals, so every fault injection has an approver and audit trail.
- Abort criteria use the same KQL burn-rate queries as the SLO alerts.
- Record measured RTO/RPO and the pipeline run ID as evidence for `sre-compliance-evidence`.
