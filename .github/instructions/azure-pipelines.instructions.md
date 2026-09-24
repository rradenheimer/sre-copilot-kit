---
applyTo: "**/azure-pipelines*.yml,**/azure-pipelines*.yaml,**/pipelines/**/*.yml,**/pipelines/**/*.yaml,**/.azuredevops/**/*.yml"
---
# Azure Pipelines YAML

- Before proposing changes, run `python .github/skills/sre-ado-pipeline-reliability/scripts/pipeline_lint.py <file> --prod-env <names from overlay>` and address High findings first.
- Deploy only in `deployment` jobs bound to an `environment`; production environments use `canary` or `rolling` with an `on: failure` rollback hook.
- Pin template repositories to a tag or commit `ref`, and tasks to a major version (`AzureCLI@2`).
- Keep the client's required `extends` template; never remove approvals, checks or template references.
- No secrets in YAML: use variable groups linked to Key Vault.
- Remember approvals and checks live on the ADO environment, not in YAML; ask before assuming they are missing.
