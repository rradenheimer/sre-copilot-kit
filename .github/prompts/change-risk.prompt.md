---
description: Assess risk and blast radius of an infrastructure change or pull request
agent: sre-reviewer
argument-hint: PR ID, or attach Bicep what-if / Terraform plan JSON / manifests
---
Using the `sre-change-risk-review` skill, sanitize the inputs, summarize what is created, modified,
replaced and destroyed, check the risk checklist and client policy-as-code, and give a risk rating with
reasons, findings table, reviewer checklist and rollback assessment.
