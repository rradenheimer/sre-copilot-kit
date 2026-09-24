# Alert classification rules (alert_stats.py)

Evaluated in order; the first match wins. Thresholds are CLI flags; defaults shown.

| Order | Class | Rule | Default | Recommendation |
| --- | --- | --- | --- | --- |
| 1 | orphaned | Rule has no owner or no runbook, or never fired in the window | — | Assign owner and runbook, or delete |
| 2 | flapping | At least 50% of firings open for less than `--flap-min` minutes | 5 min | Add a `for:` duration or hysteresis |
| 3 | actionable | At least `--action-pct` of firings led to action or an incident | 30% | Keep |
| 4 | noisy | Pages, and at least `--auto-resolve-pct` resolve without acknowledgement | 80% | Downgrade to ticket, or replace with an SLO burn-rate alert |
| 5 | informational | Everything else | — | Dashboard or ticket, not a page |

Normalize exports (PagerDuty, Opsgenie, Azure Monitor fired alerts from Resource Graph) to the EVENTS.json
format in the script header before running. Never delete an alert tied to a compliance control without
flagging the control.
