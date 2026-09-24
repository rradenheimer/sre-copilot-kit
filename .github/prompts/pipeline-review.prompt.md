---
description: Review an Azure Pipelines YAML file for deployment safety
agent: sre-reviewer
argument-hint: path to azure-pipelines.yml
---
Using the `sre-ado-pipeline-reliability` skill, run `pipeline_lint.py` on the file with the overlay's
production environment names, read the production environments' approvals and checks from ADO, and
report findings with YAML diffs for fixes. Summary line first.
