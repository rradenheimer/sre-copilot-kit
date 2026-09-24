---
name: sre-maturity-assessment
description: Runs the firm's SRE maturity assessment — structured discovery interviews, scoring, findings and a phased roadmap — for a client engagement. Use whenever a user mentions an SRE assessment, reliability maturity, operational maturity, discovery workshop, current-state analysis, engagement kickoff, or asks for a reliability roadmap or findings report for a client.
---

# SRE Maturity Assessor

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Engagement quality should not depend on which consultant leads it. This skill runs the firm's assessment
method consistently and produces a branded, evidence-backed report and roadmap.

## Workflow

1. **Scope.** Confirm services, teams and business priorities in scope, and the stakeholders interviewed.
2. **Discovery.** Use `references/interview-guide.md`. Capture answers and evidence per dimension.
3. **Score** each dimension 1-5 using the rubric in `references/maturity-model.md`:
   incident management, observability, SLOs and error budgets, on-call health, toil and automation,
   change management, capacity, resilience and DR, and reliability culture and ownership.
4. **Evidence.** Every score cites the observation or artifact behind it. Mark self-reported vs. verified.
5. **Findings.** Group into strengths, risks and opportunities. Tie each risk to business impact.
6. **Roadmap.** Phase recommendations: 0-90 days (quick wins), 3-6 months (foundations), 6-12 months
   (scale). Link recommendations to firm offerings and other sre-* skills where relevant.

## Deterministic checks

Use the scripts for anything exact; do not recompute their results by hand.

- Record scores and evidence in `out/assessment.yaml`, then run `python ${SKILL_PATH}/scripts/maturity_score.py out/assessment.yaml`. Use its roadmap phases as the starting point; unverified scores are flagged.

## Output format

Use `assets/assessment-report-template.md`: executive summary, scorecard (dimension, score, target, evidence),
key findings, roadmap by phase, next steps.

## Guardrails

- Never inflate or soften scores to please stakeholders; explain low scores constructively.
- Do not benchmark against other named clients; use anonymized industry ranges only.

## Resources

- [scripts/maturity_score.py](./scripts/maturity_score.py) — scorecard, gaps and roadmap phases (built)
- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
- Planned (not yet built): `references/maturity-model.md` — firm rubric
- Planned (not yet built): `references/interview-guide.md` — questions per dimension and role
- Planned (not yet built): `assets/assessment-report-template.md` — firm-branded template
