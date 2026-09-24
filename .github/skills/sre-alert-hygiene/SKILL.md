---
name: sre-alert-hygiene
description: Reviews alert definitions and firing history to reduce pager noise and alert fatigue. Use whenever a user mentions noisy alerts, alert fatigue, too many pages, on-call burnout, alert review, or shares an export of alerts, monitors, notification history or PagerDuty/Opsgenie incidents.
---

# Alert Hygiene Reviewer

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Noisy paging erodes trust in alerts and hides real incidents. This skill gives teams evidence to delete,
merge or rework alerts, which is usually what overcomes resistance to removing them.

## Before starting

Run `sre-telemetry-sanitizer`. Work on alert metadata and firing history only; raw payloads are not needed.

## Workflow

1. Run `${SKILL_PATH}/scripts/alert_stats.py <export>` to compute per alert: fire count, pages per week, auto-resolve rate,
   median time open, acknowledgement rate, linked-incident rate, and flapping score.
2. Classify each alert:
   - Actionable: pages and led to human action
   - Informational: should be a ticket or dashboard, not a page
   - Duplicate: fires with another alert for the same cause
   - Flapping: frequent open/close within short windows
   - Orphaned: no owner, no runbook, or monitors a retired resource
3. Recommend per alert: keep, tune threshold, add duration, merge, downgrade to ticket, delete, or replace with
   an SLO burn-rate alert (hand off to `sre-slo-designer`).
4. Estimate pages saved per week if recommendations are adopted.

## Deterministic checks

Use the scripts for anything exact; do not recompute their results by hand.

- Normalize the export to the EVENTS.json format in the script header, then run `python ${SKILL_PATH}/scripts/alert_stats.py events.json --rules rules.json --days 28`. Use its classes and pages-saved figures; adjust thresholds only with the engineer's agreement.

## Output format

Summary (current pages/week, projected pages/week), then a prioritized table: alert, class, evidence,
recommendation, pages saved. Highest noise first.

## Guardrails

- Never recommend deleting an alert tied to a compliance control without flagging the control.
- Keep at least one alert covering each critical user journey.

## Resources

- [scripts/alert_stats.py](./scripts/alert_stats.py) — per-alert noise statistics and classification (built)
- [references/classification-rules.md](./references/classification-rules.md) — thresholds and rules for alert_stats.py (built)
- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
