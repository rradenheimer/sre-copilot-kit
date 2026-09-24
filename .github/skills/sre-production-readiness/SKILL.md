---
name: sre-production-readiness
description: Runs a production readiness review (PRR) or launch readiness assessment for a new or significantly changed service. Use whenever a user mentions go-live, launch, PRR, ORR, operational readiness, cutover, migration to production, or asks "are we ready to launch" or what is missing before production.
---

# Production Readiness Reviewer

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

A consistent go-live gate prevents launching services that cannot be observed, operated or recovered.
This skill scores readiness and turns gaps into owned actions.

## Workflow

1. Gather evidence: architecture summary, dashboards, SLOs, runbooks, on-call schedule, load test and DR
   test results, security review status. Ask for what's missing; don't assume.
2. Score each domain from `references/prr-checklist.md` as Met / Partial / Not met / N/A, citing the evidence:
   - Observability (golden signals, logs, traces, dashboards)
   - SLOs and alerting (link to `sre-slo-designer` if missing)
   - On-call and escalation
   - Runbooks for top failure modes
   - Capacity and load testing
   - Dependency failure modes, timeouts, retries, circuit breaking
   - Backup, restore and DR — tested, with recorded results
   - Security and access review
   - Change and rollback process
   - Documentation and ownership
3. Add the client overlay's mandatory checks.
4. Give an overall recommendation: Ready / Ready with conditions / Not ready.

## Deterministic checks

Use the scripts for anything exact; do not recompute their results by hand.

- Record evidence per domain in `out/prr-<service>.yaml`, then run `python ${SKILL_PATH}/scripts/prr_score.py out/prr-<service>.yaml` (add `--extra-checks` for the overlay's mandatory checks). Its recommendation is the one you report.

## Output format

Recommendation and reason; domain scorecard table; blocking gaps with owner role and due date;
non-blocking improvements.

## Guardrails

- "Not tested" means Not met for backup, restore and DR, regardless of design quality.
- The recommendation is advisory; the client's launch authority decides.

## Resources

- [scripts/prr_score.py](./scripts/prr_score.py) — readiness scorecard and recommendation (built)
- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
- Planned (not yet built): `references/prr-checklist.md` — domains, criteria, evidence examples
- Planned (not yet built): `assets/prr-report-template.md`
