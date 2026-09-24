# Normalized inputs for dora.py

deployments.json
```json
[{"id": "4711", "finished": "2026-09-01T14:03:00Z", "result": "succeeded",
  "first_commit_time": "2026-08-31T09:12:00Z", "caused_incident": false}]
```
- `result`: succeeded | failed | canceled (canceled deployments are excluded)
- `first_commit_time`: optional; needed for lead time
- `caused_incident`: optional; true when an incident was attributed to this deployment

incidents.json
```json
[{"id": 12001, "created": "2026-09-02T10:00:00Z", "resolved": "2026-09-02T11:30:00Z", "deployment_id": "4711"}]
```
- `deployment_id`: optional; also counts that deployment as a change failure
