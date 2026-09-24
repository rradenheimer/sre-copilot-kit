#!/usr/bin/env bash
# Regression checks for the kit's scripts. Run from the repo root: bash tests/run_tests.sh
set -u
PYTHON_BIN="${PYTHON:-${PYTHON_BIN:-$(command -v python3 || command -v python || printf '%s' python)}}"
S=.github/skills; F=tests/fixtures; T=$(mktemp -d); pass=0; fail=0
check(){ if eval "$2"; then echo "PASS $1"; pass=$((pass+1)); else echo "FAIL $1"; fail=$((fail+1)); fi; }

"$PYTHON_BIN" $S/sre-telemetry-sanitizer/scripts/sanitize.py $F/sample.log --patterns $S/client-overlay-ado/references/sanitizer-patterns.yaml --map-out $T/map.json > $T/san.txt
check "sanitizer removes secrets"      "! grep -qE 'Hunter2|eyJhbGci|9f8e7d6c' $T/san.txt"
check "sanitizer tokenizes stably"     "[ \$(grep -o '<IP_01>' $T/san.txt | wc -l) -eq 2 ]"
"$PYTHON_BIN" $S/sre-telemetry-sanitizer/scripts/sanitize.py $F/marked.txt --map-out $T/m2.json >/dev/null 2>&1; rc=$?
check "sanitizer stops on markings"    "[ $rc -eq 3 ]"

"$PYTHON_BIN" $S/sre-ado-pipeline-reliability/scripts/pipeline_lint.py $F/bad-pipeline.yml --json > $T/lint.json; rc=$?
check "lint flags bad pipeline"        "[ $rc -eq 1 ] && grep -q PR004 $T/lint.json && grep -q PR008 $T/lint.json"
"$PYTHON_BIN" $S/sre-ado-pipeline-reliability/scripts/pipeline_lint.py $S/sre-ado-pipeline-reliability/assets/safe-deploy-template.yml --require-extends >/dev/null; rc=$?
check "lint passes reference template" "[ $rc -eq 0 ]"

"$PYTHON_BIN" $S/sre-ado-reliability-backlog/scripts/work_items.py apply $F/items.json --overlay $F/overlay.json >/dev/null 2>&1; rc=$?
check "backlog refuses invalid apply"  "[ $rc -ne 0 ]"

"$PYTHON_BIN" $S/sre-ado-delivery-metrics/scripts/dora.py compute --deployments $F/deployments.json --incidents $F/incidents.json --days 90 --as-of 2026-09-20T00:00:00Z --json > $T/dora.json
check "dora separates CFR from failed runs" ""$PYTHON_BIN" -c \"import json;d=json.load(open('$T/dora.json'));assert d['change_failure_rate_pct']<d['failed_deployment_run_pct']\""

"$PYTHON_BIN" $S/sre-ado-org-governance/scripts/ado_governance.py evaluate $F/governance.snapshot.sample.json --protected main --json > $T/gov.json
check "governance finds WIF gap"       "grep -q GV006 $T/gov.json"

"$PYTHON_BIN" $S/sre-slo-designer/scripts/burn_rate.py --slo 99.9 --format json > $T/br.json
check "burn rate 14.4x at 99.9"        ""$PYTHON_BIN" -c \"import json;assert json.load(open('$T/br.json'))[0]['burn_rate']==14.4\""

"$PYTHON_BIN" $S/sre-change-risk-review/scripts/parse_plan.py $F/tfplan.json --json > $T/plan.json; rc=$?
check "plan parser flags stateful replace" "[ $rc -eq 1 ] && grep -q stateful $T/plan.json"

"$PYTHON_BIN" tests/test_guardrails.py > $T/g.txt; rc=$?
check "guardrail hook policy (27 cases)" "[ $rc -eq 0 ]"

"$PYTHON_BIN" tests/test_scripts.py > $T/s.txt; rc=$?
check "skill script behaviors (39 cases)" "[ $rc -eq 0 ]"
helpfail=0
for f in .github/skills/*/scripts/*.py; do timeout 20 "$PYTHON_BIN" $f --help </dev/null >/dev/null 2>&1 || { echo "  --help failed: $f"; helpfail=$((helpfail+1)); }; done
check "--help on every skill script" "[ $helpfail -eq 0 ]"

bad_draft=$(find .github/skills -name SKILL.md -exec grep -l "status: draft" {} + 2>/dev/null | wc -l)
check "no draft skills in .github/skills" "[ $bad_draft -eq 0 ]"

rm -rf $T; echo "$pass passed, $fail failed"; [ $fail -eq 0 ]
