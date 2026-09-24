---
name: sre-capacity-forecast
description: Forecasts capacity headroom, saturation dates and cloud cost from utilization and growth data. Use whenever a user mentions capacity planning, headroom, scaling, saturation, growth projections, peak season readiness, right-sizing, reserved capacity or cloud cost forecasts, or shares utilization metrics exports.
---

# Capacity & Cost Forecaster

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Capacity problems are predictable when someone does the math. This skill keeps the math in scripts and
uses Copilot to interpret results and write the recommendation leadership will read.

## Before starting

Use aggregated metrics (hourly or daily percentiles per resource pool). Run `sre-telemetry-sanitizer`
if exports include hostnames or account IDs.

## Workflow

1. Confirm the resources and constraints: CPU, memory, storage, connections, throughput, quotas and limits.
2. Confirm the growth driver (traffic, users, data volume) and any known events (launches, peak seasons).
3. Run `${SKILL_PATH}/scripts/forecast.py <data> --horizon <days> --threshold <pct>` for trend and seasonality, with
   confidence intervals and projected threshold-crossing dates.
4. Compare projected peak against safe utilization targets from `references/headroom-targets.md`.
5. Model options (scale up, scale out, reserved or committed capacity, right-sizing) with cost using
   `${SKILL_PATH}/scripts/cost_model.py` and the client's pricing inputs.
6. Recommend the option with timing (order-by and deploy-by dates).

## Deterministic checks

Use the scripts for anything exact; do not recompute their results by hand.

- `python ${SKILL_PATH}/scripts/forecast.py series.json --threshold <pct> --horizon 180` gives the crossing date and band.
- `python ${SKILL_PATH}/scripts/cost_model.py options.yaml --months 12` compares options; include pricing_source and pricing_date.

## Output format

Headline (what saturates first and when); forecast chart; options table (option, cost, risk, lead time);
recommendation; assumptions.

## Guardrails

- Always state the confidence interval and data range; never present a single date as certain.
- Label cost figures with pricing source and date.

## Resources

- [scripts/forecast.py](./scripts/forecast.py) — threshold crossing date with a 95% band (built)
- [scripts/cost_model.py](./scripts/cost_model.py) — option costs, headroom and commitment flags (built)
- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
- Planned (not yet built): `references/headroom-targets.md`
