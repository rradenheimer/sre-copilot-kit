---
applyTo: "**/runbooks/**/*.md,**/playbooks/**/*.md"
---
# Runbooks

Follow the `sre-runbook-author` skill: Symptoms → Impact check → Diagnosis → Mitigation → Verification →
Rollback → Escalation. One action per step with the exact command and expected result. Mark privileged or
break-glass steps. Use `az` with explicit `--subscription` and `--resource-group`.
