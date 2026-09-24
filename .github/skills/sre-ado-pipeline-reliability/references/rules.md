# Pipeline reliability rules

| Rule | Severity | Check | Why it matters |
| --- | --- | --- | --- |
| PR000 | High | File is not valid YAML or not a mapping | Nothing else can be checked until it parses |
| PR001 | High | Deploy step runs in a plain `job`, not a `deployment` job | Only deployment jobs bind to environments, so approvals, checks and deployment history do not apply |
| PR002 | High | `deployment` job has no `environment` | Environment checks and audit history are skipped |
| PR003 | Medium | Deployment strategy is `runOnce` for a production-like environment | No progressive exposure; a bad release reaches all users at once |
| PR004 | High | No `on: failure` rollback hook for a production-like deployment | Recovery depends on manual improvisation |
| PR005 | Medium | Template repository referenced without a pinned `ref` | Upstream template changes alter production behavior silently |
| PR006 | Low | Task referenced without a major version (e.g., `AzureCLI` not `AzureCLI@2`) | Task behavior can change unexpectedly |
| PR007 | Medium | Pipeline does not `extends` a governed template when the overlay requires one | Bypasses org-wide security and compliance steps |
| PR008 | High | Possible secret literal in YAML (key, password, token, connection string) | Credential exposure |
| PR009 | Low | Production stage lacks an explicit `condition` | Deploys can proceed after failures |
| PR010 | Medium | Production-deploying pipeline triggers on all branches | Unreviewed branches can deploy |
| PR011 | Info | Production-like environment detected | Approvals and checks live on the ADO environment, not in YAML; confirm them |

Production-like environment names match `prod`, `prd`, `production` or `live` as a name segment
(case-insensitive), plus names listed in the ADO overlay (`--prod-env`).
