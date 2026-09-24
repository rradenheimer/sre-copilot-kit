# Azure DevOps tenant notes

Read this file only when the active client overlay declares an Azure DevOps tenant.

KQL is the default language in ADO tenants. Cover:

- Application Insights (`requests`, `dependencies`, `exceptions`, `traces`) vs. workspace-based tables
  (`AppRequests`, `AppDependencies`, ...) and their column-name differences.
- Log Analytics resource tables (`AzureDiagnostics`, resource-specific tables, `ContainerLogV2` for AKS).
- Azure Resource Graph (`resources`, `resourcechanges`) for inventory and change questions.
- ADO audit events when streamed to a workspace (table name set by the client's streaming config).
- Cost patterns: filter on `TimeGenerated` first, project early, avoid `search *` over long ranges.
