# R1: Kit as Azure SRE Agent plugins (draft)

**Goal.** Deliver the same skills, scripts and guardrail policy inside Azure SRE Agent for live operations,
while engineering work stays in Copilot.

**Why.** Azure SRE Agent (generally available March 2026) supports skills, subagents, Python tools, agent
hooks, MCP connectors, per-tool allow/ask/deny rules and a private plugin marketplace for publishing
approved skills and workflows to every agent in a tenant.

**Design.**
- One plugin per skill group: incident (sanitizer, incident command, postmortem), reliability (SLO, alerts,
  capacity, game day), change (pipeline, change risk, readiness), ADO (backlog, DORA, governance).
- Scripts ship unchanged as Python tools; the `${SKILL_PATH}` convention maps to the plugin's install path.
- Translate `guardrails.py` rules to SRE Agent allow/ask/deny tool permissions; keep the script as the test
  oracle so both surfaces enforce the same policy.
- Client overlays stay per tenant and are never published to the marketplace.

**Open questions.** Plugin manifest format and versioning; whether SRE Agent hooks accept the same payload
fields; how per-tenant overlays are injected.

**Exit criteria.** One plugin group installed from a private marketplace in a pilot tenant, with the
guardrail test cases passing against the translated permissions.
