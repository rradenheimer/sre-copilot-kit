# Checkout outage 2026-09-23
## Summary
Checkout returned errors for 28 minutes after release 2026.09.23.1.
## Impact
8% of checkout attempts failed; 19 minutes of error budget consumed.
## Timeline
14:02 UTC alert fired
14:21 UTC rollback completed
## Contributing factors
The pipeline allowed a schema migration to deploy before the application change that depended on it.
## What went well
Rollback completed in 12 minutes.
## Action items
| Action | Owner | Priority | Due | Done criterion |
| --- | --- | --- | --- | --- |
| Add pending-migration check to the deploy pipeline | Platform team | P1 | 2026-10-15 | Pipeline fails when a migration is pending |
