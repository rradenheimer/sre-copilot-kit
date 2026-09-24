---
name: sre-roadmap-readiness
description: Assesses which advanced reliability capabilities a client is ready for — agentic incident response, closed-loop remediation, change risk prediction, anomaly detection, incident similarity search, alert correlation, error budget forecasting, dependency simulation, SRE for AI agents and AI governance evidence. Use whenever a user asks about AIOps, ML, autonomous remediation, agentic operations, the roadmap, "what's next" for a client, or whether a client's data is good enough for machine learning.
---

# Roadmap Readiness

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Advanced capabilities fail when they start before their data and controls exist. This skill checks each
roadmap item (R1-R12 in `ROADMAP.md` at the repository root) against the client's actual evidence and
recommends the next item that is genuinely ready.

## Workflow

1. Collect evidence into `out/readiness/`: normalized deployments and incidents (from `sre-ado-delivery-metrics`),
   a telemetry series (from `sre-capacity-forecast`), daily SLI counts and the SLO spec (from `sre-slo-designer`),
   alert events (from `sre-alert-hygiene`), and folders of postmortems and runbooks. Sanitize client data first.
2. Confirm the people-verified facts with the engineer: hooks verified, plugin packaging, telemetry read access,
   gates pipeline, service topology, tracing coverage, agent in production, control map verified, audit retention.
   Never assume a fact is true; leave it false until confirmed.
3. Write `out/readiness/readiness.yaml` (format in the script's `--help`) and run
   `python ${SKILL_PATH}/scripts/readiness.py out/readiness/readiness.yaml`.
4. Report by horizon. Recommend the lowest-horizon item that is Ready, and for Partial items list the
   cheapest unmet prerequisite to close next.

## Deterministic checks

- `python ${SKILL_PATH}/scripts/readiness.py <config> [--json]` computes every status. Do not override a status by judgment.

## Output format

Table: item, horizon, status, unmet prerequisites. Then one recommended next item and the two prerequisites
most worth closing.

## Guardrails

- Readiness is advice, not approval: starting any roadmap item still needs the client's agreement and, for
  autonomous actions, the approvals in `ROADMAP.md`.
- Never recommend training models across clients; each client's data stays in its own boundary.

## Resources

- [scripts/readiness.py](./scripts/readiness.py) — prerequisite checks for R1-R12 (built)
- [references/roadmap-items.yaml](./references/roadmap-items.yaml) — items and thresholds (built)
