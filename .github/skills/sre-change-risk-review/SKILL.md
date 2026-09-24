---
name: sre-change-risk-review
description: Assesses risk and blast radius of infrastructure and platform changes — Terraform plans, Kubernetes manifests, Helm values, CloudFormation, Bicep and CI/CD pipeline changes. Use whenever a user shares an IaC diff, plan output, manifest or pull request, or asks whether a change is safe, what could break, or to prepare a CAB or change-request risk assessment.
---

# Infrastructure Change Risk Reviewer

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Most incidents follow a change. This skill gives reviewers a consistent, evidence-based risk read before a
change ships. It advises; it never approves, which preserves separation-of-duties requirements.

## Before starting

Run `sre-telemetry-sanitizer` on plans and manifests (they contain account IDs, ARNs and hostnames).

## Workflow

1. Summarize the change in plain language: what is created, modified, replaced and destroyed.
2. Run `python ${SKILL_PATH}/scripts/parse_plan.py plan.json` on Terraform plan JSON to list replacements and deletions exactly.
3. Check against `references/risk-checklist.md`:
   - Stateful resources replaced or destroyed (databases, volumes, queues, DNS, KMS keys)
   - IAM and network exposure changes (new privileges, wildcard actions, public ingress)
   - Kubernetes: missing resource requests/limits, liveness/readiness probes, PodDisruptionBudgets,
     single replicas, `latest` image tags, privileged containers
   - Rollout safety: canary or progressive delivery, rollback path, feature flags
   - Timing: change freeze windows and peak traffic from the client overlay
4. Check against the client's policy-as-code rules listed in the overlay (OPA/Rego, Sentinel, Kyverno).
5. Rate risk Low / Medium / High / Critical with the reasons.

## Output format

Risk rating and one-line reason; change summary; findings table (finding, evidence, severity, recommendation);
reviewer checklist; rollback plan assessment.

## Guardrails

- Never state that a change is approved or safe to deploy; state the assessed risk.
- Treat any destruction of stateful or cryptographic resources as at least High until a human confirms intent.

## Resources

- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
- [scripts/parse_plan.py](./scripts/parse_plan.py) — Terraform plan JSON → action summary and risk flags (built)
- Planned (not yet built): `references/risk-checklist.md`
- Planned (not yet built): `references/k8s-best-practices.md`
