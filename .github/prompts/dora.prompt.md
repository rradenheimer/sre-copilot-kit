---
description: Compute DORA metrics for an Azure DevOps project
agent: sre-backlog-manager
argument-hint: production environment name(s) and period in days (default 90)
---
Using the `sre-ado-delivery-metrics` skill, collect production environment deployment records and
incident work items read-only, normalize and compute with `dora.py`, and report the metrics table with
sample sizes, drivers and two or three recommendations. Save data and report under `out/dora/`.
