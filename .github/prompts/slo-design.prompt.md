---
description: Design SLIs, SLOs, error budget policy and Azure Monitor burn-rate alerts for a service
agent: sre-reliability-engineer
argument-hint: service name, users, critical journeys, current telemetry
---
Using the `sre-slo-designer` skill, interview me only for what is missing, then produce the SLO table,
error budget policy, burn-rate thresholds from `burn_rate.py`, KQL queries and Bicep
`scheduledQueryRules` resources. Write files under `out/slo-<service>/`.
