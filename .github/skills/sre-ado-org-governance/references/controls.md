# Governance rules

| Rule | Severity | Check |
| --- | --- | --- |
| GV001 | High | Protected branch has no minimum-reviewer policy |
| GV002 | Medium | Minimum-reviewer policy allows the author to approve their own change |
| GV003 | Medium | Protected branch has no build validation policy |
| GV004 | Low | Protected branch does not require linked work items |
| GV005 | Medium | Protected branch policy is not blocking (isBlocking false) |
| GV006 | High | Azure service connection uses a service principal secret instead of workload identity federation |
| GV007 | High | Azure service connection scoped to a whole subscription or management group without a resource group |
| GV008 | Medium | Service connection is shared across projects |
| GV009 | Medium | Production-like environment has no approval or check configured |
| GV010 | Info | Self-hosted agent pool in use; confirm isolation and patching (manual check) |
