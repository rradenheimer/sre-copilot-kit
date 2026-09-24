---
name: sre-gameday-planner
description: Plans disaster recovery tests, failover exercises, game days and chaos engineering experiments with safety controls. Use whenever a user mentions a game day, DR test, failover test, chaos experiment, fault injection, resilience testing, tabletop exercise, or wants to prove RTO/RPO or validate recovery.
---

# Resilience Game Day Planner

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Untested recovery is assumed recovery. This skill designs exercises that produce real evidence while keeping
customer risk controlled. Human approval gates are mandatory.

## Workflow

1. **Objective.** State what the exercise proves (e.g., region failover meets RTO 30 min / RPO 5 min).
2. **Hypothesis.** "When <fault>, <system> will <expected behavior>, and <SLI> stays within <bound>."
3. **Steady state.** Define the SLIs and dashboards that show normal behavior before, during and after.
4. **Blast radius.** Start in non-production or with the smallest scope; state affected services, traffic
   share and customer impact ceiling.
5. **Abort criteria.** Specific thresholds that trigger immediate rollback, and who calls it.
6. **Runbook.** Step-by-step execution, rollback steps and verification, with timings.
7. **Roles and comms.** Exercise lead, observers, approvers, stakeholder notice template.
8. **Approvals.** List required approvals (service owner, change board, client security) before execution.
9. **Evidence capture.** What to record for `sre-compliance-evidence` (timestamps, measured RTO/RPO, issues).
10. **Readout.** Template for findings and actions after the exercise.

## Deterministic checks

Use the scripts for anything exact; do not recompute their results by hand.

- `python ${SKILL_PATH}/scripts/gameday_check.py check plan.yaml` must report READY before the exercise is scheduled.
- After the exercise, `python ${SKILL_PATH}/scripts/gameday_check.py measure events.yaml` gives measured RTO and RPO for the readout and for compliance evidence.

## Output format

Exercise plan document following the steps above, then an approval checklist.

## Guardrails

- Never generate fault-injection commands targeting production without the approvals in step 8 recorded.
- Always include a tested rollback path before any fault is injected.
- Default to tabletop or non-production for a first exercise with any client.

## Resources

- [scripts/gameday_check.py](./scripts/gameday_check.py) — plan readiness gate and RTO/RPO measurement (built)
- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
- Planned (not yet built): `assets/gameday-plan-template.md`
- Planned (not yet built): `references/fault-catalog.md` — common faults by layer with safe starting scopes
- Planned (not yet built): `assets/readout-template.md`
