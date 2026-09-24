---
applyTo: "**/*.bicep,**/*.bicepparam,**/azuredeploy*.json"
---
# Bicep and ARM

- For changes to existing infrastructure, ask for `az deployment group what-if` output and apply the `sre-change-risk-review` skill.
- Treat `Delete` or replacing `Modify` on SQL, Storage, Cosmos DB, Key Vault, managed disks and DNS as High risk until the owner confirms intent.
- Azure Monitor alerts are `Microsoft.Insights/scheduledQueryRules`; generate burn-rate thresholds with the `sre-slo-designer` skill script.
- Use managed identities and resource-group scope; never embed keys or connection strings.
