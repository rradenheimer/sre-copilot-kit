# Azure DevOps tenant notes

Read this file only when the active client overlay declares an Azure DevOps tenant.

Load `client-overlay-ado/references/sanitizer-patterns.yaml` in addition to the base patterns.

- Redact ADO org URLs (`dev.azure.com/<org>`, `<org>.visualstudio.com`) and Azure DevOps Server collection URLs.
- Redact Azure subscription, tenant and object GUIDs and full resource IDs (`/subscriptions/...`).
- Drop, never tokenize: PATs, bearer tokens, service connection secrets, storage account keys, SAS tokens.
- Pipeline logs often echo variables; check for `##vso[task.setvariable` lines and redact their values.
- Work item exports can include customer names in titles and discussion; review free text manually.
