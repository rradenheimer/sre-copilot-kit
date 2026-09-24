---
description: Assess Azure DevOps organization and project governance posture
agent: sre-reviewer
argument-hint: project name and protected branch patterns
---
Using the `sre-ado-org-governance` skill, collect a read-only snapshot (or use the one provided in
`out/`), evaluate it with `ado_governance.py`, walk me through the manual checks, and report a posture
summary and findings table. Offer a hand-off of High findings to the backlog.
