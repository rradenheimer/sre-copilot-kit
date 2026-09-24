# Azure DevOps tenant notes

Read this file only when the active client overlay declares an Azure DevOps tenant.

- Review ADO pull requests: the diff, linked work items, build validation results and reviewer policy.
- For Bicep/ARM, request `az deployment group what-if` output; treat `Delete` and `Modify` on stateful
  resources (SQL, Storage, Cosmos DB, Key Vault, managed disks) as High until confirmed.
- Check against Azure Policy assignments in scope and the client's required pipeline templates.
- Post the assessment as a PR comment only with confirmation and write access; otherwise return it as text.
