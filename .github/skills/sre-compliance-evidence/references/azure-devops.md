# Azure DevOps tenant notes

Read this file only when the active client overlay declares an Azure DevOps tenant.

ADO artifacts that commonly serve as change-management and access-control evidence:

- PR completion records: reviewers, approvals, build validation results, linked work items.
- Environment approval history and check results per production deployment.
- Pipeline run records linking commit, artifact and deployment.
- ADO audit log (streamed to Azure Monitor Logs or SIEM) for permission and policy changes.
- `sre-ado-org-governance` snapshot and findings as configuration evidence.
Map them to controls through `references/`; do not assert satisfaction.
