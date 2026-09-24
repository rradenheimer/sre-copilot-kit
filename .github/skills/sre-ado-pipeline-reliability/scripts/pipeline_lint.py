#!/usr/bin/env python3
"""Deterministic reliability checks for Azure Pipelines YAML. Rule catalog: references/rules.md.
Usage: pipeline_lint.py FILE [--prod-env NAME ...] [--require-extends] [--json]
Exit code 1 when any High finding exists (usable as a pipeline gate)."""
import argparse, json, re, sys
import yaml

PROD_RE = re.compile(r"(^|[-_.])(prod|prd|production|live)([-_.]|$)", re.I)
SECRET_RE = re.compile(r"(password|passwd|secret|token|apikey|api_key|connectionstring|accountkey)\w*\s*[:=]\s*['\"]?[A-Za-z0-9+/=_\-]{8,}", re.I)
DEPLOY_HINT = re.compile(r"(AzureWebApp|AzureRmWebAppDeployment|AzureFunctionApp|KubernetesManifest|HelmDeploy|AzureResourceManagerTemplateDeployment|kubectl apply|az deployment|terraform apply|helm upgrade)", re.I)


def env_name(env):
    return str(env.get("name", "")) if isinstance(env, dict) else str(env or "")


def walk_jobs(doc):
    def from_stages(stages):
        for st in stages or []:
            if isinstance(st, dict):
                for j in st.get("jobs", []) or []:
                    if isinstance(j, dict):
                        yield st.get("stage", "?"), st, j
    yield from from_stages(doc.get("stages"))
    for j in doc.get("jobs", []) or []:
        if isinstance(j, dict):
            yield "(root)", {}, j
    ext = doc.get("extends") or {}
    yield from from_stages((ext.get("parameters") or {}).get("stages"))


def lint(text, prod_names=(), require_extends=False):
    findings = []
    def add(rule, sev, loc, msg):
        findings.append({"rule": rule, "severity": sev, "location": loc, "message": msg})
    try:
        doc = yaml.safe_load(text) or {}
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        where = f"line {mark.line + 1}" if mark else "unknown location"
        return [{"rule": "PR000", "severity": "High", "location": where, "message": f"Invalid YAML: {getattr(e, 'problem', e)}"}]
    if not isinstance(doc, dict):
        return [{"rule": "PR000", "severity": "High", "location": "(root)", "message": "Pipeline YAML root must be a mapping."}]
    extra = {n.lower() for n in prod_names}
    is_prod = lambda n: bool(PROD_RE.search(n)) or n.lower() in extra
    saw_prod = False

    for stage, st, job in walk_jobs(doc):
        loc = f"stage {stage} / job {job.get('deployment') or job.get('job') or '?'}"
        if "deployment" in job:
            env = env_name(job.get("environment"))
            if not env:
                add("PR002", "High", loc, "Deployment job has no environment; checks and history are skipped.")
            strat = job.get("strategy") if isinstance(job.get("strategy"), dict) else {}
            kind = next(iter(strat), "runOnce")
            body = strat.get(kind) or {}
            if env and is_prod(env):
                saw_prod = True
                if kind == "runOnce":
                    add("PR003", "Medium", loc, f"Environment '{env}' uses runOnce; consider canary or rolling.")
                # PyYAML (YAML 1.1) parses the key `on` as boolean True
                hooks = body.get("on") or body.get(True) or {}
                if not hooks.get("failure"):
                    add("PR004", "High", loc, "No on.failure rollback hook for a production-like deployment.")
                if st and not st.get("condition"):
                    add("PR009", "Low", f"stage {stage}", "Production stage has no explicit condition such as succeeded().")
        elif DEPLOY_HINT.search(yaml.safe_dump(job.get("steps", []))):
            add("PR001", "High", loc, "Deploy-like steps run in a plain job; use a deployment job bound to an environment.")

    for repo in ((doc.get("resources") or {}).get("repositories") or []):
        if isinstance(repo, dict) and repo.get("repository") != "self" and not repo.get("ref"):
            add("PR005", "Medium", f"resources.repositories.{repo.get('repository')}", "Template repository not pinned to a tag or commit ref.")

    for m in re.finditer(r"task:\s*([A-Za-z0-9_.\-@]+)", text):
        if "@" not in m.group(1):
            add("PR006", "Low", f"line {text[:m.start()].count(chr(10)) + 1}", f"Task '{m.group(1)}' has no major version.")

    if require_extends and "extends" not in doc:
        add("PR007", "Medium", "(root)", "Pipeline does not extend the governed template required by the client overlay.")

    for i, line in enumerate(text.splitlines(), 1):
        if SECRET_RE.search(line) and "$(" not in line and "${{" not in line:
            add("PR008", "High", f"line {i}", "Possible secret literal; move it to a Key Vault-linked variable group.")

    trig = doc.get("trigger", "__absent__")
    all_branches = trig == "__absent__" or trig == "*" or (isinstance(trig, dict) and "*" in str((trig.get("branches") or {}).get("include", "")))
    if saw_prod and all_branches:
        add("PR010", "Medium", "trigger", "Production-deploying pipeline triggers on all branches.")
    if saw_prod:
        add("PR011", "Info", "environments", "Confirm approvals and checks on production environments in ADO; YAML cannot show them.")
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file")
    ap.add_argument("--prod-env", action="append", default=[])
    ap.add_argument("--require-extends", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.file, encoding="utf-8") as fh:
        text = fh.read()
    f = lint(text, a.prod_env, a.require_extends)
    if a.json:
        print(json.dumps(f, indent=2))
    else:
        print("No findings." if not f else "\n".join(f"[{x['severity']}] {x['rule']} {x['location']}: {x['message']}" for x in f))
    sys.exit(1 if any(x["severity"] == "High" for x in f) else 0)


if __name__ == "__main__":
    main()
