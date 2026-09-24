---
name: sre-incident-command
description: Live incident command support — severity classification, running timeline, stakeholder status updates, action and owner tracking, and missed-step prompts. Use whenever a user says there is an incident, outage, degradation, SEV, P1/P2, war room or bridge, pastes live chat or bridge notes, or asks for a status update, exec summary or customer notice during an event.
---

# Incident Command Copilot

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Incident commanders lose time to bookkeeping and comms. This skill takes that load so the IC can make
decisions. It supports the IC; it does not make remediation decisions.

## Before starting

- Run `sre-telemetry-sanitizer` on any pasted logs or chat.
- Load the client overlay's severity matrix, comms templates and cadence. If absent, use `references/default-severity.md`.

## Workflow

1. **Classify.** Propose a severity with the matrix criteria it meets. Mark it "proposed" until the IC confirms.
2. **Roles.** Confirm IC, comms lead, ops/tech lead and scribe are named. Prompt if any is missing.
3. **Timeline.** Maintain a UTC timeline: detection, declaration, key findings, actions, mitigations, resolution.
   Extract entries from pasted chat; mark inferred times as "approx".
4. **Status updates.** At the overlay cadence, draft updates for the audiences requested:
   - Executive: impact, customer effect, current action, next update time. No jargon.
   - Technical: hypotheses, what's ruled out, active workstreams, owners.
   - Customer-facing: plain impact statement and next update time; no cause speculation.
5. **Track.** Keep open questions, actions and owners in a short table.
6. **Prompt for missed steps** when relevant: rollback decision point, change freeze, customer support briefed,
   regulatory or contractual notification clocks (e.g., breach-notification windows in the overlay), evidence preservation.
7. **Close.** On resolution, produce the final timeline and hand off to `sre-postmortem-author`.

## Deterministic checks

Use the scripts for anything exact; do not recompute their results by hand.

- `python ${SKILL_PATH}/scripts/incident.py timeline out/<notes>.sanitized.txt --date <YYYY-MM-DD>` builds the UTC timeline and time to declare, mitigate and resolve; it lists missing milestones.
- `python ${SKILL_PATH}/scripts/incident.py severity facts.json --matrix <overlay severity matrix JSON>` proposes a severity with the criteria met. The IC confirms it.

## Output format

Lead each response with a one-line state: `SEV<n> | <status> | Next update <time UTC>`. Then only what changed.

## Guardrails

- Never state root cause as fact during the incident; label hypotheses.
- Never send communications; draft them for human approval.
- Flag security-incident indicators (unauthorized access, data exfiltration) and recommend engaging the client's security IR process.

## Resources

- [scripts/incident.py](./scripts/incident.py) — timeline from notes, key durations, severity proposal (built)
- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
- Planned (not yet built): `references/default-severity.md`
- Planned (not yet built): `assets/status-update-templates.md` (exec, technical, customer)
- Planned (not yet built): `references/notification-clocks.md` — common regulatory windows, verified by compliance team
