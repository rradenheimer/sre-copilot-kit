# Manual organization checks

Verify in Organization settings and record Yes / No / N/A with a screenshot reference for evidence.

1. Organization connected to Microsoft Entra ID; conditional access enforced.
2. Policies: third-party OAuth application access disabled unless approved.
3. Policies: SSH authentication and public projects disabled unless approved.
4. PAT lifecycle policy: maximum lifetime set and full-scoped PATs restricted.
5. Audit log enabled and streamed to Azure Monitor Logs or the client SIEM, with retention meeting policy.
6. Pipeline settings: limit job authorization scope to current project; protect access to repositories in YAML pipelines.
7. Pipeline settings: disable creation of classic build and release pipelines where the client has standardized on YAML.
8. Self-hosted agents: ephemeral or rebuilt regularly; no production credentials stored on agents.
9. Project Collection Administrators membership reviewed within the last 90 days.
