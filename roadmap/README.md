# Roadmap drafts

Drafts here are **not** loaded by Copilot (only `.github/skills/` is). Each draft has a proposed workflow,
guardrails and exit criteria.

## Promotion from draft to active skill

1. **Ready client.** `sre-roadmap-readiness` reports the item Ready for a pilot client.
2. **Scripts first.** Anything exact (scores, thresholds, graph math, model evaluation) is a script with
   `--help`, `--json`, exit codes 0/1/2, a known-bad and a known-good fixture, and cases in `tests/test_scripts.py`.
3. **Guardrails in the hook.** Any new tool or action path gets allow/ask/deny rules and cases in `tests/test_guardrails.py`.
4. **Trigger evals.** Add two positive and one negative case to `tests/evals/trigger-cases.json`.
5. **Exit criteria met** on the pilot client, recorded in the release notes.
6. **Champion review** (two approvals if the hook changes), then move the folder to `.github/skills/`,
   remove `metadata.status: draft`, update `ROADMAP.md` status, and release as a minor version.
