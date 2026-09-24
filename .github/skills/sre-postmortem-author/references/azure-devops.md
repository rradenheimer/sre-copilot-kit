# Azure DevOps tenant notes

Read this file only when the active client overlay declares an Azure DevOps tenant.

- Build the change timeline from environment deployment records and pipeline run history (start/finish,
  run ID, commit) alongside the incident timeline.
- Link the postmortem to the incident work item and the deploying run/PR where a change contributed.
- Hand action items to `sre-ado-reliability-backlog` with tag `sre-postmortem` and the incident as related link.
- Publish the postmortem to the ADO Wiki page path the overlay names, if the client keeps postmortems there.
