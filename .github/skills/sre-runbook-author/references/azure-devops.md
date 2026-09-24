# Azure DevOps tenant notes

Read this file only when the active client overlay declares an Azure DevOps tenant.

- Publish runbooks to the ADO Wiki path in the overlay; keep one page per alert, linked from the alert's
  description.
- Steps scored "scriptable" become candidate pipeline jobs (manual-trigger pipelines with environment
  approvals), which gives audit history for every remediation.
- Commands use `az` CLI with explicit `--subscription` and resource group; never rely on default context.
