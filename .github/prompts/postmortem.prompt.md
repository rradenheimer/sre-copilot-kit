---
description: Draft a blameless postmortem from incident artifacts and pipeline history
agent: sre-incident-commander
argument-hint: incident work item ID and/or attached timeline, chat export, alerts
---
Using the `sre-postmortem-author` skill, sanitize the inputs, build the UTC timeline including pipeline
runs to production, separate the trigger from contributing factors, and propose specific action items.
Use the client's template if the overlay names one. Save to `out/postmortem-<incident>.md`.
