"""Behavior tests for the skill scripts added in v1.1 (run from repo root: python3 tests/test_scripts.py)."""
import json, shlex, subprocess, sys

S, F = ".github/skills", "tests/fixtures"
CASES = [  # (name, command, expected exit, substring expected in stdout or None)
    ("incident timeline durations", f"{S}/sre-incident-command/scripts/incident.py timeline {F}/incident-notes.txt --date 2026-09-23 --json", 0, '"time_to_mitigate_min": 19.0'),
    ("incident severity proposes SEV2", f"{S}/sre-incident-command/scripts/incident.py severity {F}/sev-facts.json --matrix {F}/sev-matrix.json", 0, "SEV2"),
    ("postmortem flags blame + ownerless action", f"{S}/sre-postmortem-author/scripts/postmortem_lint.py {F}/postmortem-bad.md", 1, "No owner"),
    ("postmortem good passes", f"{S}/sre-postmortem-author/scripts/postmortem_lint.py {F}/postmortem-good.md", 0, "No findings"),
    ("runbook flags unsafe delete", f"{S}/sre-runbook-author/scripts/runbook_lint.py {F}/runbook-bad.md", 1, "Destructive action"),
    ("runbook good passes", f"{S}/sre-runbook-author/scripts/runbook_lint.py {F}/runbook-good.md", 0, "No findings"),
    ("kql time filter after summarize", f"{S}/sre-query-translator/scripts/validate.py --lang kql {F}/query-bad.kql", 1, "after `summarize`"),
    ("kql good passes", f"{S}/sre-query-translator/scripts/validate.py --lang kql {F}/query-good.kql", 0, "No findings"),
    ("promql high cardinality", f"{S}/sre-query-translator/scripts/validate.py --lang promql --query 'sum by (user_id) (rate(x_total[5m]))'", 1, "high-cardinality"),
    ("spl missing index", f"{S}/sre-query-translator/scripts/validate.py --lang spl --query 'error | search status=500'", 1, "index="),
    ("alert stats classifies flapping", f"{S}/sre-alert-hygiene/scripts/alert_stats.py {F}/alert-events.json --rules {F}/alert-rules.json", 0, "flapping"),
    ("alert stats finds orphaned rule", f"{S}/sre-alert-hygiene/scripts/alert_stats.py {F}/alert-events.json --rules {F}/alert-rules.json", 0, "orphaned"),
    ("openslo emits v1", f"{S}/sre-slo-designer/scripts/emit_openslo.py {F}/slo-spec.yaml", 0, "apiVersion: openslo/v1"),
    ("openslo target as ratio", f"{S}/sre-slo-designer/scripts/emit_openslo.py {F}/slo-spec.yaml", 0, "target: 0.999"),
    ("prr untested backup blocks", f"{S}/sre-production-readiness/scripts/prr_score.py {F}/prr-evidence.yaml", 1, "Not ready"),
    ("prr ready", f"{S}/sre-production-readiness/scripts/prr_score.py {F}/prr-ready.yaml", 0, "billing: Ready"),
    ("maturity roadmap order", f"{S}/sre-maturity-assessment/scripts/maturity_score.py {F}/maturity.yaml", 0, "0-90 days: incident_management, change_management"),
    ("gameday not ready", f"{S}/sre-gameday-planner/scripts/gameday_check.py check {F}/gameday-plan.yaml", 1, "Rollback path not tested"),
    ("gameday ready", f"{S}/sre-gameday-planner/scripts/gameday_check.py check {F}/gameday-ready.yaml", 0, "READY"),
    ("gameday RTO measured", f"{S}/sre-gameday-planner/scripts/gameday_check.py measure {F}/gameday-events.yaml", 0, "RTO 12.5 min"),
    ("forecast crossing date", f"{S}/sre-capacity-forecast/scripts/forecast.py {F}/capacity-series.json --threshold 80", 1, "Projected to cross 80.0: 2026-12-01"),
    ("cost model units", f"{S}/sre-capacity-forecast/scripts/cost_model.py {F}/capacity-options.yaml", 0, "units 115"),
    ("control coverage partial with gap", f"{S}/sre-compliance-evidence/scripts/control_lookup.py coverage {F}/evidence-inventory.yaml --framework soc2 --as-of 2026-09-23", 1, "145 days old"),
    ("control lookup by artifact", f"{S}/sre-compliance-evidence/scripts/control_lookup.py controls --framework nist-800-53-r5 --artifact dr_test_report", 0, "CP-4"),
    ("overlay template not ready", f"{S}/client-overlay/scripts/overlay_check.py", 1, "NOT READY"),
    ("budget forecast exhaustion", f"{S}/sre-slo-designer/scripts/budget_forecast.py {F}/sli-daily.json --slo 99.9", 1, "runs out on 2026-09-24"),
    ("budget forecast healthy", f"{S}/sre-slo-designer/scripts/budget_forecast.py {F}/sli-daily-healthy.json --slo 99.9", 0, "lasts the full window"),
    ("readiness R9 ready", f"{S}/sre-roadmap-readiness/scripts/readiness.py {F}/readiness/readiness.yaml", 0, "R9 H2 Ready"),
    ("readiness R5 needs labels", f"{S}/sre-roadmap-readiness/scripts/readiness.py {F}/readiness/readiness.yaml", 0, "attributed change failures"),
    ("budget forecast bad slo", f"{S}/sre-slo-designer/scripts/budget_forecast.py {F}/sli-daily.json --slo 120", 2, None),
    ("readiness malformed", f"{S}/sre-roadmap-readiness/scripts/readiness.py {F}/malformed.yaml", 2, None),
    # malformed or missing input -> exit 2
    ("forecast too short", f"{S}/sre-capacity-forecast/scripts/forecast.py {F}/series-too-short.json", 2, None),
    ("prr malformed", f"{S}/sre-production-readiness/scripts/prr_score.py {F}/malformed.yaml", 2, None),
    ("maturity malformed", f"{S}/sre-maturity-assessment/scripts/maturity_score.py {F}/malformed.yaml", 2, None),
    ("gameday malformed", f"{S}/sre-gameday-planner/scripts/gameday_check.py check {F}/malformed.yaml", 2, None),
    ("cost malformed", f"{S}/sre-capacity-forecast/scripts/cost_model.py {F}/malformed.yaml", 2, None),
    ("openslo malformed", f"{S}/sre-slo-designer/scripts/emit_openslo.py {F}/malformed.yaml", 2, None),
    ("controls unknown framework", f"{S}/sre-compliance-evidence/scripts/control_lookup.py controls --framework nope", 2, None),
    ("validate without input", f"{S}/sre-query-translator/scripts/validate.py --lang kql", 2, None),
]
fails = 0
for name, cmd, exp, needle in CASES:
    r = subprocess.run([sys.executable, *shlex.split(cmd)], capture_output=True, text=True)
    ok = r.returncode == exp and (needle is None or needle in r.stdout)
    fails += not ok
    print(("PASS" if ok else f"FAIL (exit {r.returncode})"), name)
print(f"{len(CASES) - fails}/{len(CASES)} script cases passed")
sys.exit(1 if fails else 0)
