# Reliability WIQL library

Replace `@project` scope and the tag if the overlay uses another convention. Run with
`az boards query --wiql "<query>"`, the ADO MCP server's query tool, or REST `POST _apis/wit/wiql`.

## Open reliability work, oldest first
```sql
SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], [System.CreatedDate]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.Tags] CONTAINS 'sre'
  AND [System.State] NOT IN ('Closed', 'Done', 'Removed', 'Resolved')
ORDER BY [System.CreatedDate] ASC
```

## Unowned reliability work
```sql
SELECT [System.Id], [System.Title], [System.AreaPath]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.Tags] CONTAINS 'sre'
  AND [System.AssignedTo] = ''
  AND [System.State] NOT IN ('Closed', 'Done', 'Removed')
```

## Postmortem actions older than 30 days
```sql
SELECT [System.Id], [System.Title], [System.AssignedTo], [System.CreatedDate]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.Tags] CONTAINS 'sre-postmortem'
  AND [System.State] NOT IN ('Closed', 'Done', 'Removed')
  AND [System.CreatedDate] < @Today - 30
```

## Incidents in the last 90 days (for DORA time to restore)
```sql
SELECT [System.Id], [System.Title], [System.CreatedDate], [Microsoft.VSTS.Common.ClosedDate]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.WorkItemType] = 'Bug'
  AND [System.Tags] CONTAINS 'incident'
  AND [System.CreatedDate] >= @Today - 90
```
The incident work item type and tag vary by client; take them from the overlay.

## Reliability work by source
```sql
SELECT [System.Id], [System.Title], [System.Tags], [System.State]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND ([System.Tags] CONTAINS 'sre-postmortem'
    OR [System.Tags] CONTAINS 'sre-alert-hygiene'
    OR [System.Tags] CONTAINS 'sre-prr'
    OR [System.Tags] CONTAINS 'sre-toil')
```
