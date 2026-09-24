# SRE Copilot Kit: one-page overview

## What this repo is

This repository packages a set of SRE operating capabilities for GitHub Copilot in a client Azure DevOps tenancy. It is designed to help a reliability engineering team work safely and consistently across incidents, rollout reviews, audit evidence, and roadmap planning.

## Core building blocks

- Agents: role-based operating personas such as the incident commander, reviewer, reliability engineer, backlog manager, and restricted profile agent.
- Skills: domain expertise for incident handling, postmortems, SLO design, validation, runbooks, alert hygiene, capacity forecasting, change-risk assessment, compliance evidence, and roadmap readiness.
- Hooks: pre-tool-use guardrails that enforce safety rules before destructive commands, raw-data reads, or unapproved ADO writes occur.
- Prompts: quick-start interaction patterns for incident updates, postmortems, SLO design, governance reviews, and backlog planning.
- Scripts: deterministic tooling that turns operational judgment into testable outputs and evidence.
- Overlay config: client-specific profiles for tenant, security posture, data-handling rules, and environment conventions.

## Why it exists

The kit reduces operational drift by standardizing the following:

- how incidents are triaged and communicated,
- how reliability work is measured and prioritized,
- how changes are reviewed before production,
- how evidence is mapped to compliance expectations,
- how advanced capabilities are evaluated against readiness thresholds.

## Safety model

The repo is intentionally designed to fail closed:

- raw client data is kept in inputs and sanitized before use,
- the guardrail hook blocks destructive shell commands and sensitive reads,
- ADO writes are allowed only under the correct profile and explicit review flow,
- profile C restrictions keep data handling to read-only or out-only workflows.

## Typical usage

### Incident response

- sanitize raw logs,
- classify severity and timeline,
- draft updates and postmortem findings,
- track actions without bypassing guardrails.

### Production readiness and launch

- validate overlay configuration,
- score readiness with the production-readiness script,
- review deployment safety and change risk,
- confirm that the service is ready before go-live.

### Audit and governance

- map artifacts to controls,
- assess branch-policy and pipeline posture,
- document evidence gaps and remediation work,
- keep recommendations tied to measured findings rather than assumptions.

### Roadmap and maturity

- score the client’s current maturity,
- identify readiness for advanced capabilities,
- prioritize backlog items and reliability investment,
- align delivery metrics with engineering improvements.

## Repository map

- [.github/copilot-instructions.md](../.github/copilot-instructions.md): practice-wide rules and guardrails
- [.github/skills](../.github/skills): skill library and client overlays
- [.github/agents](../.github/agents): custom agent definitions
- [.github/prompts](../.github/prompts): slash-command workflows
- [.github/hooks](../.github/hooks): enforcement layer for safe tool use
- [ROADMAP.md](../ROADMAP.md): strategic roadmap and adoption path
- [tests](../tests): regression and behavior validation
- [pipelines](../pipelines): reliability gate checks for Azure Pipelines

## In one sentence

This repo turns operational SRE judgment into a repeatable, policy-enforced, evidence-driven system for client-ready reliability work.
