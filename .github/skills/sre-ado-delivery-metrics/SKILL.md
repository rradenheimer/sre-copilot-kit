---
name: sre-ado-delivery-metrics
description: Computes and interprets DORA delivery metrics — deployment frequency, lead time for changes, change failure rate and time to restore — from Azure DevOps pipeline runs, environment deployment records, commits and incident work items. Use whenever a user asks about DORA metrics, deployment frequency, lead time, change failure rate, MTTR, delivery performance or engineering velocity for an Azure DevOps project, or needs delivery data for a maturity assessment.
---

# ADO Delivery Metrics Analyst

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

DORA metrics show whether reliability and delivery speed are improving together. In ADO tenants the data
already exists in Pipelines and Boards; this skill computes the metrics exactly and explains what drives them.

## Data collection (read-only)

1. Production deployments: ADO environment deployment records for the production environment(s) named
   in the overlay (REST `_apis/distributedtask/environments/{id}/environmentdeploymentrecords`), or the
   pipeline runs that deploy to production (`az pipelines runs list`). Save as JSON.
2. Lead time (optional but recommended): for each deployment, the timestamp of the oldest commit it
   shipped. Add it as `first_commit_time` in the normalized file.
3. Incidents: incident work items for the same period (WIQL in `sre-ado-reliability-backlog`), with created
   and resolved/closed dates, and, where known, the deployment that caused them.
4. Run `sre-telemetry-sanitizer` on exports before sharing them outside the client boundary.

## Workflow

1. Normalize ADO environment records: `python ${SKILL_PATH}/scripts/dora.py normalize records.json > deployments.json`.
2. Compute: `python ${SKILL_PATH}/scripts/dora.py compute --deployments deployments.json --incidents incidents.json --days 90`.
   All numbers come from the script; do not estimate by reading the data.
3. Interpret: identify drivers (batch size, manual approvals wait time, flaky tests, failed deploys by
   service) and compare to the prior period if data allows.
4. Map to performance bands only using `references/bands.md`, and name the DORA report version used.
5. Recommend 2-3 improvements, each tied to a skill (Pipeline Reliability Reviewer for failure rate,
   SLO Designer for detection, Runbook Author for restore time).

## Output format

Metrics table (metric, value, period, sample size), trend notes, drivers, recommendations, data caveats.

## Definitions

- **Change failure rate** counts successful production deployments that caused an incident or needed remediation
  (rollback, hotfix). It needs attribution: `caused_incident` on deployments or `deployment_id` on incidents.
  If `change_failure_attribution_known` is false, report the metric as unavailable, not zero.
- **Failed deployment run rate** counts pipeline deployment runs that failed. It is a delivery-health signal,
  not a DORA metric; report it separately.

## Guardrails

- State sample sizes; flag any metric computed from fewer than 10 deployments or 3 incidents as low confidence.
- Use metrics to improve systems, never to rank individuals or teams against each other.

## Resources

- [scripts/dora.py](./scripts/dora.py) — normalize and compute (built)
- [references/data-schema.md](./references/data-schema.md) — normalized input formats (built)
- [references/bands.md](./references/bands.md) — performance bands, set by the practice (built, needs owner sign-off)
