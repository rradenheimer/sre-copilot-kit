# Azure DevOps tenant notes

Read this file only when the active client overlay declares an Azure DevOps tenant.

- Draft the incident record as a work item of the overlay's incident type and tag; hand creation to
  `sre-ado-reliability-backlog` (preview + confirmation).
- Pull recent changes for the affected service: last pipeline runs to its production environments
  (environment deployment history) and PRs merged to protected branches in the last 24 hours. Recent
  deployments are the first hypothesis to rule in or out.
- If rollback is chosen, point to the pipeline's rollback stage or redeploy of the last known good run.
- Status updates reference work item IDs, not internal URLs, when sent outside the client.
