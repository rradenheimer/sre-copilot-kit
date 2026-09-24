---
name: sre-agent-reliability
description: Applies SRE practice to operational AI agents — SLOs for investigation accuracy and action precision, replay evaluations on past incidents before each release, adversarial testing through logs and tickets, and kill switches. Use when a client runs Azure SRE Agent, Copilot agents or other operational agents and asks how to trust, measure, test or govern them.
metadata:
  status: draft
  roadmap_id: R11
---

# SRE for AI agents (draft, R11)

This is a design draft, not an active skill. It lives in `roadmap/skills/` so Copilot does not load it.
Check prerequisites with `sre-roadmap-readiness` before starting work on it.

## Workflow (proposed)

1. Define agent SLIs: correct top hypothesis rate on replayed incidents, precision of proposed actions, time to first useful answer, guardrail denial rate.
2. Build a replay set from documented incidents (sanitized) and run it on every agent or skill release.
3. Test prompt injection by planting instructions in logs, tickets and wiki pages; the agent must not act on them.
4. Document the kill switch: how to revoke the agent identity and tool permissions within minutes.

## Guardrails

- Replay and adversarial tests run in non-production copies only.
- A release that lowers replay accuracy or raises unsafe-action attempts does not ship.

## Exit criteria to promote

Replay suite of at least 10 incidents runs in CI for one client's agent, with SLOs agreed and a kill-switch drill completed.

Promotion follows `roadmap/README.md`: tests, trigger evals, champion review, then move to `.github/skills/`.
