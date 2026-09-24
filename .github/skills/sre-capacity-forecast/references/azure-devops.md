# Azure DevOps tenant notes

Read this file only when the active client overlay declares an Azure DevOps tenant.

- Pull utilization from Azure Monitor metrics (e.g., App Service plan CPU/memory, AKS node pools, SQL DTU/vCore)
  at hourly aggregation for at least 90 days.
- Include Azure Advisor right-sizing recommendations and reservation or savings plan coverage as options.
- Check subscription and regional quotas as hard limits, not just utilization.
