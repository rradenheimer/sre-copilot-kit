---
name: sre-telemetry-sanitizer
description: Redacts and tokenizes sensitive data in logs, traces, metrics exports, chat transcripts, tickets and config files before any analysis. Use this skill FIRST whenever a user pastes or uploads client operational data — logs, stack traces, Slack or Teams exports, bridge notes, alert dumps, Terraform or Kubernetes files — even if they don't ask for redaction, and before any other sre-* skill analyzes that data.
---

# Telemetry Sanitizer

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Restricted and regulated clients cannot allow raw identifiers, credentials or personal data to reach a model
endpoint outside their approval. This skill makes client input safe to analyze while keeping it useful, by
replacing sensitive values with stable tokens so relationships (same host, same user) survive redaction.

## When to stop instead of sanitizing

Stop, do not process the content, and tell the user when you see any of:
- Classification or control markings: CUI, ITAR, EAR/export-controlled, FOUO, SECRET, or client-specific banners
  listed in the active client overlay.
- Data classified above the ceiling declared in the client overlay.
- Bulk regulated records (full PHI records, cardholder data dumps) rather than incidental fields.

Explain what was detected in general terms, and ask the user to use the client-approved environment or a
pre-sanitized extract. Never repeat the sensitive values in your reply.

## Workflow

1. Load the client overlay's `sanitizer-patterns.yaml` if present.
2. Run `python ${SKILL_PATH}/scripts/sanitize.py <input> --patterns .github/skills/client-overlay-ado/references/sanitizer-patterns.yaml --out out/<name>.sanitized.txt --report`.
   Exit code 3 means a classification marking was found: stop and tell the user. The token map is written to
   `.sanitizer/map.json`, which is git-ignored and must never be opened, quoted or committed.
3. Review the output for anything the detectors missed (free-text names, ticket bodies, customer names in URLs).
   Redact those manually using the same token scheme.
4. Report a summary: counts per category redacted, and anything suspicious that could not be classified.
5. Hand the sanitized text to the downstream skill. Keep the token map local; never include it in outputs.

## Token scheme

Use stable, typed tokens so analysis still works: `<HOST_01>`, `<IP_03>`, `<USER_07>`, `<ACCT_02>`,
`<EMAIL_01>`, `<SECRET_REDACTED>`, `<CLIENT_TERM_04>`. The same value always maps to the same token
within one session. Secrets are never tokenized reversibly — they are dropped.

## Detection categories

Credentials and secrets (API keys, tokens, private keys, connection strings, high-entropy strings);
network identifiers (IPv4/IPv6, internal FQDNs, MAC addresses); cloud identifiers (account and subscription IDs,
ARNs, resource IDs); personal data (names, emails, phone numbers, government IDs); client identifiers
(codenames and product names from the overlay).

## Resources

- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
- [scripts/sanitize.py](./scripts/sanitize.py) — regex + entropy detectors, stable tokenization, local map file (built)
- `tests/run_tests.sh` at the repo root — regression checks (built)
- [references/default-patterns.yaml](./references/default-patterns.yaml) — firm baseline patterns and stop markings (built)

## Guardrails

- Prefer over-redaction; a false positive costs little, a leak ends an engagement.
- Never print the token map, original values, or secrets in chat, files or downstream prompts.
