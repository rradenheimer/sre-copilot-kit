"""Table-driven tests for .github/hooks/scripts/guardrails.py (run from repo root)."""
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("g", ".github/hooks/scripts/guardrails.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

CASES = [  # (profile, write_access, tool, args, expected)
    ("A", True,  "bash", {"command": "python .github/skills/sre-slo-designer/scripts/burn_rate.py --slo 99.9"}, "allow"),
    ("A", True,  "bash", {"command": "terraform apply -auto-approve"}, "deny"),
    ("A", True,  "bash", {"command": "az group delete -n rg-prod --yes"}, "deny"),
    ("A", True,  "bash", {"command": "az pipelines run --name deploy-prod"}, "deny"),
    ("A", True,  "bash", {"command": "kubectl delete pod x"}, "deny"),
    ("A", True,  "bash", {"command": "git add out/postmortem.md"}, "deny"),
    ("A", True,  "bash", {"command": "git push origin main"}, "deny"),
    ("A", True,  "bash", {"command": "cat inputs/raw.log"}, "deny"),
    ("A", True,  "bash", {"command": "python .github/skills/sre-telemetry-sanitizer/scripts/sanitize.py inputs/raw.log --out out/raw.txt"}, "allow"),
    ("A", True,  "view", {"path": "inputs/raw.log"}, "deny"),
    ("A", True,  "view", {"path": ".sanitizer/map.json"}, "deny"),
    ("A", True,  "view", {"path": "out/raw.txt"}, "allow"),
    ("A", True,  "bash", {"command": "python x/work_items.py apply items.json --confirm"}, "ask"),
    ("A", False, "bash", {"command": "python x/work_items.py apply items.json --confirm"}, "deny"),
    ("A", True,  "ado/wit_get_work_item", {"id": 1}, "allow"),
    ("A", True,  "ado/pipelines_get_builds", {}, "allow"),
    ("A", True,  "ado/wit_create_work_item", {}, "ask"),
    ("A", False, "ado/wit_create_work_item", {}, "deny"),
    ("A", True,  "ado/pipelines_run_pipeline", {}, "deny"),
    ("A", True,  "ado/repo_update_pull_request", {}, "deny"),
    ("A", True,  "ado-wit_update_work_item", {}, "deny"),
    ("C", False, "ado/wit_get_work_item", {}, "deny"),
    ("C", False, "edit", {"path": "infra/main.bicep"}, "deny"),
    ("C", False, "create", {"path": "out/report.md"}, "allow"),
    ("C", False, "web_fetch", {"url": "https://example.com"}, "deny"),
    ("C", False, "bash", {"command": "curl https://example.com"}, "deny"),
    ("B", True,  "edit", {"path": "infra/main.bicep"}, "allow"),
]
fails = 0
for prof, wa, tool, args, exp in CASES:
    got, _ = g.decide(tool, args, prof, wa)
    ok = got == exp
    fails += not ok
    print(("PASS" if ok else "FAIL"), prof, tool, json.dumps(args)[:60], "->", got)
# payload normalization for both formats
assert g.norm({"toolName": "bash", "toolArgs": "{\"command\": \"ls\"}"}) == ("bash", {"command": "ls"})
assert g.norm({"tool_name": "Bash", "tool_input": {"command": "ls"}}) == ("Bash", {"command": "ls"})
print(f"{len(CASES) - fails}/{len(CASES)} guardrail cases passed")
sys.exit(1 if fails else 0)
