---
applyTo: "**/*.kql,**/*.csl,**/queries/**"
---
# KQL

- Filter on `TimeGenerated` (workspace tables) or `timestamp` (classic Application Insights) first, then project early.
- Workspace tables use `AppRequests`/`Success`; classic Application Insights uses `requests`/`success`.
- Avoid `search *` and unbounded time ranges. State the time range explicitly in every query.
- For SLO burn-rate queries, use `python .github/skills/sre-slo-designer/scripts/burn_rate.py --slo <target> --format kql`.
