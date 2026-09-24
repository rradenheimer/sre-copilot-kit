---
name: sre-slo-designer
description: Designs SLIs, SLOs, error budget policies and burn-rate alerting from a description of a service and its users. Use whenever a user mentions SLOs, SLIs, SLAs, error budgets, reliability targets, burn-rate alerts, availability or latency goals, or asks "how reliable should this be" — even if they only describe a service and its users.
---

# SLO & Error Budget Designer

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Good SLOs measure what users experience and drive decisions. This skill encodes the firm's method for
getting from a service description to approved SLOs and alerting that pages only on real budget risk.

## Workflow

1. **Interview.** Establish: who the users are, the 2-4 critical user journeys, dependencies, current
   telemetry available, known pain, and any contractual SLA. Ask only what's missing.
2. **Choose SLIs** per journey from `references/sli-menu.md` (availability, latency, freshness, correctness,
   throughput). Define each as good events / valid events, with exact measurement point (load balancer, client, synthetic).
3. **Set targets.** Start from current measured performance when available; set the target where users
   would notice degradation, and keep SLOs tighter than any SLA. Explain the rationale for each number.
4. **Window.** Default 28- or 30-day rolling unless the client prefers calendar alignment.
5. **Error budget policy.** Define what happens at 50%, 75% and 100% budget consumed (e.g., release gating,
   reliability work prioritization) and who decides. Use `assets/error-budget-policy.md`.
6. **Alerting.** Run `${SKILL_PATH}/scripts/burn_rate.py --slo <target> --window-days <days>` to generate multiwindow,
   multi-burn-rate thresholds. Do the math in the script, never by hand.
7. **Emit artifacts.** Generate OpenSLO YAML and the client stack's rules (Prometheus recording/alerting
   rules, Datadog SLO monitors, etc.) per the overlay.

## Deterministic checks

Use the scripts for anything exact; do not recompute their results by hand.

- Preview (roadmap R9): once daily SLI counts exist, `python ${SKILL_PATH}/scripts/budget_forecast.py sli.json --slo <target>` reports budget consumed, recent burn rate and the projected exhaustion date. Include it in the error budget policy review and label it preview.
- `python ${SKILL_PATH}/scripts/emit_openslo.py slo-spec.yaml --out out/slo-<service>/` writes the OpenSLO files in step 7.

## Output format

1. SLO summary table: journey, SLI, target, window, rationale.
2. Error budget policy.
3. Alert rules and OpenSLO files as code blocks or files.
4. Open questions and data gaps.

## Guardrails

- Flag any target of 99.99% or higher and ask whether dependencies can support it.
- Flag SLIs that cannot yet be measured and propose the instrumentation needed.

## Resources

- [scripts/budget_forecast.py](./scripts/budget_forecast.py) — error budget status and exhaustion forecast (preview, R9)
- [scripts/emit_openslo.py](./scripts/emit_openslo.py) — OpenSLO v1 YAML from an SLO spec (built)
- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
- [scripts/burn_rate.py](./scripts/burn_rate.py) — thresholds per window pair; `--format kql` emits Azure Monitor queries (built)
- Planned (not yet built): `references/sli-menu.md`
- Planned (not yet built): `assets/error-budget-policy.md`
