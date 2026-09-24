---
name: sre-postmortem-author
description: Writes blameless postmortems and post-incident reviews from timelines, chat exports, alert history and notes. Use whenever a user mentions a postmortem, PIR, RCA, incident review, retrospective, after-action report or lessons learned, or shares incident artifacts after an event is resolved.
---

# Postmortem Author

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Postmortems create value only when they are published quickly and lead to completed actions. This skill
cuts drafting time from weeks to hours and keeps the review blameless and specific.

## Before starting

- Run `sre-telemetry-sanitizer` on all inputs.
- Use the client overlay's postmortem template if present; otherwise `assets/postmortem-template.md`.

## Workflow

1. Build a UTC timeline from the inputs. Mark gaps and inferred times explicitly.
2. Compute key durations: time to detect, acknowledge, mitigate and resolve.
3. Quantify impact: users or requests affected, duration, SLO/error budget consumed, business effect if given.
4. Separate the **trigger** from **contributing factors**. Use the taxonomy in `references/contributing-factors.md`
   (detection, change management, capacity, dependency, design, process, knowledge). There is rarely one root cause.
5. Record what went well — it reinforces practices worth keeping.
6. Propose action items. Each must be specific, have an owner role, a priority and a measurable done state.
   Prefer actions that prevent a class of failure over ones that patch this instance.
7. Run a blameless language check: rewrite phrases that assign fault to individuals ("X failed to...") into
   system framing ("the deploy process allowed...").
8. List open questions the review meeting must resolve.

## Deterministic checks

Use the scripts for anything exact; do not recompute their results by hand.

- `python ${SKILL_PATH}/scripts/postmortem_lint.py out/postmortem-<id>.md` before handing the draft over. Fix every High finding; pass the client template's section names with `--sections` if they differ.

## Output format

Follow the template sections: Summary, Impact, Timeline, Contributing factors, What went well,
Action items (table: action, owner role, priority, due, done criterion), Open questions.

## Guardrails

- Never invent facts to fill gaps; list them as open questions.
- Use roles, not personal names, unless the client template requires names.

## Resources

- [scripts/postmortem_lint.py](./scripts/postmortem_lint.py) — structure, blameless language and action item checks (built)
- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
- Planned (not yet built): `assets/postmortem-template.md` — firm standard template
- Planned (not yet built): `references/contributing-factors.md` — taxonomy with examples
- Planned (not yet built): `references/action-item-quality.md` — good vs. weak action examples
