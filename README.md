# sre-copilot-kit

The SRE practice's skills, packaged for **GitHub Copilot** in client **Azure DevOps** tenants.
18 Agent Skills, 5 custom agents, 8 slash-command prompts, path-specific instructions and ADO MCP config.

## What's inside

| Path | Copilot construct | Purpose |
| --- | --- | --- |
| `.github/copilot-instructions.md` | Repository instructions | Practice-wide rules: profile check, sanitize first, scripts for exact answers, no unconfirmed writes |
| `.github/instructions/*.instructions.md` | Path-specific instructions | Conventions for pipelines YAML, Bicep, Terraform, KQL, runbooks, postmortems |
| `.github/skills/` | Agent Skills (`SKILL.md`) | 18 SRE skills (including `sre-roadmap-readiness`) plus `client-overlay` and `client-overlay-ado` |
| `ROADMAP.md`, `roadmap/` | Roadmap | 12 advanced capabilities (R1-R12): status, drafts not loaded by Copilot, promotion process |
| `.github/agents/*.agent.md` | Custom agents | Role agents whose tool lists match each tenant profile |
| `.github/prompts/*.prompt.md` | Prompt files | `/incident-update`, `/postmortem`, `/slo-design`, `/pipeline-review`, `/change-risk`, `/dora`, `/governance-scan`, `/backlog-plan` |
| `.github/hooks/sre-guardrails.json` | Hooks (`preToolUse`) | Deterministic policy: blocks destructive shell commands, ADO writes outside the allowlist, raw-input reads and profile violations; asks before work item creation; logs denials to `out/.audit/` |
| `pipelines/sre-reliability-gates.yml` | Azure Pipelines template | Runs the lint and plan checks as a PR gate, no AI required |
| `.vscode/mcp.json` | MCP config | Remote ADO MCP server (Entra sign-in); `docs/mcp-local.json` is the local alternative |
| `tests/run_tests.sh` | — | Full suite: script regressions, 33 script behavior cases, 27 guardrail cases, `--help` on every script |
| `tests/evals/trigger-cases.json` | — | Prompts to verify each skill loads when it should (and not otherwise) |

## Agents

| Agent | Use for | ADO access |
| --- | --- | --- |
| `sre-incident-commander` | Live incidents, status updates, postmortems | Read |
| `sre-reviewer` | Pipeline, change, readiness and governance reviews | Read; no edit tool |
| `sre-reliability-engineer` | SLOs, KQL, alerts, runbooks, capacity, game days | None |
| `sre-backlog-manager` | Work items, backlog reports, DORA | Write, only after previewed confirmation |
| `sre-restricted` | Profile C engagements | None; edits only in `out/` |

## Setup per engagement

1. Copy this repo's contents into a client ops repository (Azure Repos is fine) or open it as a workspace next to the client repos.
2. Fill `.github/skills/client-overlay-ado/references/ado-overlay.json` (it ships as Profile C, read-only, until you change it) and `SKILL.md`: profile, org, project, work item conventions, production environments, protected branches.
3. Add client codenames to `.github/skills/client-overlay-ado/references/sanitizer-patterns.yaml` (`client_terms`).
4. Profiles A/B: start the `ado` MCP server from `.vscode/mcp.json` and sign in with Entra. Profile C: delete `.vscode/mcp.json` and use only `sre-restricted`.
5. Confirm the Copilot policies with the client's GitHub admin: approved models, data residency (Profile B), FedRAMP model restriction (Profile C, if approved), and that Agent Skills are enabled.
6. Run `python .github/skills/client-overlay/scripts/overlay_check.py` (must report OK), then `bash tests/run_tests.sh` (Python 3.10+ and PyYAML required).

## Where Copilot runs in an ADO tenant

- **VS Code agent mode and Copilot CLI:** full support for skills, agents and prompts against code in Azure Repos.
- **Copilot coding agent from Azure Boards:** only when the code is hosted on GitHub. Custom agents defined in the GitHub repo or org appear in Boards.
- **Copilot cloud agent on GitHub.com:** ignores `handoffs`; the agents still work without them.

## Data flow

Client data goes into `inputs/` (git-ignored). The sanitizer writes the redacted copy to `out/`; the hook blocks
the agent from reading `inputs/` or `.sanitizer/` directly. Pasting raw data into chat bypasses this, so train
engineers to save files to `inputs/` instead, and ask the client's GitHub admin to add `inputs/**` and
`.sanitizer/**` to Copilot content exclusion as an extra layer.

## Security notes

- Hooks are the enforcement layer; agent tool lists and instructions are guidance. Hooks are documented for
  Copilot CLI and the cloud agent. VS Code agent mode reads the PascalCase `PreToolUse` entry; verify it fires in the
  client's VS Code version before relying on it there (the table-driven tests cover the policy itself).
- `preToolUse` hooks fail closed on errors but fail open on timeout; the script is designed to finish well under 10 s.
- For regulated clients, the client can deploy the same script as a machine-wide policy hook
  (`/etc/github-copilot/policy.d/` or `C:\ProgramData\GitHub\Copilot\policy.d\`) so users cannot disable it.
- For scripts, prefer a short-lived Entra token over a PAT:
  `export ADO_TOKEN=$(az account get-access-token --resource 499b84ac-1321-427f-aa17-267ca6975798 --query accessToken -o tsv)`.

- Agent tool lists are guardrails, not security boundaries. Enforce profiles with ADO permissions.
- `.sanitizer/` (token maps) and `out/` (client-derived outputs) are git-ignored. Keep it that way.
- Scripts read ADO credentials only from `ADO_TOKEN`; Copilot's ADO access uses the engineer's Entra sign-in.

## Scripts

Every skill that needs an exact answer has a tested script (22 in total), run as `${SKILL_PATH}/scripts/<name>.py`.
All are standard library plus PyYAML, support `--help` and `--json`, and exit 0 (OK), 1 (High findings or not
ready) or 2 (bad input).

| Skill | Scripts |
| --- | --- |
| sre-telemetry-sanitizer | sanitize.py |
| sre-incident-command | incident.py (timeline, severity) |
| sre-postmortem-author | postmortem_lint.py |
| sre-slo-designer | burn_rate.py, emit_openslo.py, budget_forecast.py (preview, R9) |
| sre-query-translator | validate.py (KQL, SPL, PromQL) |
| sre-runbook-author | runbook_lint.py |
| sre-alert-hygiene | alert_stats.py |
| sre-change-risk-review | parse_plan.py |
| sre-production-readiness | prr_score.py |
| sre-compliance-evidence | control_lookup.py (+ artifact-to-control-map.yaml) |
| sre-capacity-forecast | forecast.py, cost_model.py |
| sre-maturity-assessment | maturity_score.py |
| sre-gameday-planner | gameday_check.py (check, measure) |
| sre-ado-pipeline-reliability | pipeline_lint.py |
| sre-ado-reliability-backlog | work_items.py |
| sre-ado-delivery-metrics | dora.py |
| sre-ado-org-governance | ado_governance.py |
| sre-roadmap-readiness | readiness.py (R1-R12 prerequisites) |
| client-overlay | overlay_check.py (pre-deployment gate) |

The control map's IDs must be verified by the compliance lead against licensed catalogs before client use.


## Conventions

Skills reference their own files with relative links (`./scripts/x.py`) and tell Copilot to run scripts as
`${SKILL_PATH}/scripts/x.py`. `${SKILL_PATH}` is an instruction-level placeholder for the skill's folder, not a
shell variable; it prevents failed calls because Copilot's terminal starts at the workspace root.

## Verify before production use

- ADO REST endpoints and branch-policy type IDs against the client's ADO version.
- The local MCP package name and domain flags in `docs/mcp-local.json` against the current azure-devops-mcp README.
- Agent tool names against the client's VS Code version (unknown tool names are ignored silently).
- DORA bands in `.github/skills/sre-ado-delivery-metrics/references/bands.md` (owner sign-off required).
