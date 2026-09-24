---
name: sre-query-translator
description: Writes, explains, optimizes and translates observability queries across Splunk SPL, Azure KQL, PromQL, Datadog, Elastic/ES|QL and CloudWatch Logs Insights. Use whenever a user asks for a query, search, dashboard panel or alert expression, pastes a query to fix or explain, or asks how to do in one tool what they know in another.
---

# Observability Query Translator

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Consultants move between client stacks constantly. This skill produces correct, efficient queries in the
client's language and explains them so engineers learn the stack as they go.

## Workflow

1. Identify the target language from the client overlay, or the user's message. If unknown, ask once.
2. Read only the matching reference: `references/<language>.md`.
3. Clarify intent in one sentence: what is being measured, over what time range, grouped by what.
4. Write the query. Apply the reference's cost-aware patterns (bounded time ranges, early filtering,
   index/source scoping, avoiding high-cardinality labels in PromQL).
5. Explain it line by line in a few sentences.
6. When translating, note semantic differences (e.g., `rate()` vs. per-bucket counts, sampling in APM tools,
   timezone and bucket alignment).
7. If `${SKILL_PATH}/scripts/validate.py <language>` supports the language, run a syntax check.

## Deterministic checks

Use the scripts for anything exact; do not recompute their results by hand.

- `python ${SKILL_PATH}/scripts/validate.py --lang kql|spl|promql --query "..."` on every query before presenting it. Fix High findings; mention Medium ones as caveats.

## Output format

Query in a code block with the language named, then a short explanation, then caveats.

## Guardrails

- Never include real hostnames, account IDs or index names from other clients in examples.
- Warn when a query could be expensive (full-index scans, unbounded regex, very long ranges).

## Resources

- [scripts/validate.py](./scripts/validate.py) — static checks for KQL, SPL and PromQL (built)
- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
- Planned (not yet built): `references/splunk-spl.md`, `references/kql.md`, `references/promql.md`, `references/datadog.md`,
  `references/elastic.md`, `references/cloudwatch-insights.md` — syntax, idioms, pitfalls, cost patterns
- Planned (not yet built): `references/translation-matrix.md` — equivalent operations across languages
