#!/usr/bin/env python3
"""Read-only Azure DevOps governance snapshot and offline evaluation.

  ado_governance.py collect  --org https://dev.azure.com/ORG --project NAME --out snapshot.json   (needs ADO_TOKEN)
  ado_governance.py evaluate snapshot.json [--protected main --protected 'release/*'] [--json]
Collection only issues GET requests.
"""
import argparse, base64, fnmatch, json, os, re, sys, urllib.parse, urllib.request

API = "7.1"
PROD_RE = re.compile(r"(^|[-_.])(prod|prd|production|live)([-_.]|$)", re.I)
MIN_REVIEWERS = "fa4e907d-c16b-4a4c-9dfa-4906e5d171dd"
BUILD_VALIDATION = "0609b952-1397-4640-95ec-e00a01b2c241"
WORK_ITEM_LINKING = "40e92b44-2fe1-4dd6-b3d8-74a9c21d0c6e"


def get(url, token):
    auth = f"Bearer {token}" if token.count(".") == 2 else "Basic " + base64.b64encode(f":{token}".encode()).decode()
    req = urllib.request.Request(url, method="GET", headers={"Authorization": auth, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect(org, project, token):
    org = org.rstrip("/")
    p = urllib.parse.quote(project)
    snap = {"org": org, "project": project}
    for key, path in {
        "policies": f"{p}/_apis/policy/configurations",
        "service_connections": f"{p}/_apis/serviceendpoint/endpoints",
        "environments": f"{p}/_apis/distributedtask/environments",
        "agent_queues": f"{p}/_apis/distributedtask/queues",
    }.items():
        snap[key] = get(f"{org}/{path}?api-version={API}", token).get("value", [])
    for e in snap["environments"]:
        try:
            e["checks"] = get(f"{org}/{p}/_apis/pipelines/checks/configurations?resourceType=environment&resourceId={e['id']}&api-version={API}-preview.1", token).get("value", [])
        except Exception as ex:  # record, don't fail the whole snapshot
            e["checks_error"] = str(ex)
    for s in snap["service_connections"]:  # drop anything secret-like before saving
        auth = s.get("authorization") or {}
        s["authorization"] = {"scheme": auth.get("scheme"), "parameters": {k: v for k, v in (auth.get("parameters") or {}).items() if k.lower() in ("scope", "serviceprincipalid", "tenantid")}}
    return snap


def refname_matches(ref, patterns):
    name = (ref or "").replace("refs/heads/", "")
    return any(fnmatch.fnmatch(name, pat) for pat in patterns)


def evaluate(snap, protected):
    out = []
    add = lambda rule, sev, obj, msg: out.append({"rule": rule, "severity": sev, "object": obj, "message": msg})
    by_branch = {}
    for pol in snap.get("policies", []):
        if not pol.get("isEnabled", True):
            continue
        for sc in (pol.get("settings") or {}).get("scope", []) or [{}]:
            ref = sc.get("refName")
            if ref and refname_matches(ref, protected):
                by_branch.setdefault(ref, []).append(pol)
    seen = set(by_branch)
    for pat in protected:
        if not any(refname_matches(r, [pat]) for r in seen):
            add("GV001", "High", pat, "No branch policies found for protected branch pattern.")
    for ref, pols in by_branch.items():
        types = {(p.get("type") or {}).get("id"): p for p in pols}
        mr = types.get(MIN_REVIEWERS)
        if not mr:
            add("GV001", "High", ref, "No minimum-reviewer policy.")
        elif (mr.get("settings") or {}).get("creatorVoteCounts"):
            add("GV002", "Medium", ref, "Author's own approval counts toward required reviewers.")
        if BUILD_VALIDATION not in types:
            add("GV003", "Medium", ref, "No build validation policy.")
        if WORK_ITEM_LINKING not in types:
            add("GV004", "Low", ref, "Linked work items not required.")
        for p in pols:
            if not p.get("isBlocking", True):
                add("GV005", "Medium", ref, f"Policy '{(p.get('type') or {}).get('displayName', 'unknown')}' is not blocking.")
    for s in snap.get("service_connections", []):
        name = s.get("name", "?")
        if (s.get("type") or "").lower() != "azurerm":
            continue
        scheme = ((s.get("authorization") or {}).get("scheme") or "")
        if scheme.lower() == "serviceprincipal":
            add("GV006", "High", name, "Uses a service principal secret; migrate to workload identity federation.")
        data = s.get("data") or {}
        scope = ((s.get("authorization") or {}).get("parameters") or {}).get("scope", "")
        if data.get("scopeLevel") in ("Subscription", "ManagementGroup") and "resourcegroups" not in scope.lower():
            add("GV007", "High", name, f"Scoped at {data.get('scopeLevel')} level; narrow to resource groups.")
        if len(s.get("serviceEndpointProjectReferences") or []) > 1:
            add("GV008", "Medium", name, "Shared across multiple projects.")
    for e in snap.get("environments", []):
        if PROD_RE.search(e.get("name", "")) and not e.get("checks") and "checks_error" not in e:
            add("GV009", "Medium", e.get("name"), "Production-like environment has no approvals or checks.")
    for q in snap.get("agent_queues", []):
        pool = q.get("pool") or {}
        if not pool.get("isHosted", False):
            add("GV010", "Info", q.get("name", "?"), "Self-hosted pool; confirm isolation and patching.")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect"); c.add_argument("--org", required=True); c.add_argument("--project", required=True); c.add_argument("--out", required=True)
    e = sub.add_parser("evaluate"); e.add_argument("snapshot"); e.add_argument("--protected", action="append", default=[]); e.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.cmd == "collect":
        token = os.environ.get("ADO_TOKEN") or sys.exit("ADO_TOKEN not set.")
        json.dump(collect(a.org, a.project, token), open(a.out, "w"), indent=2)
        print(f"Snapshot written to {a.out}"); return
    f = evaluate(json.load(open(a.snapshot)), a.protected or ["main"])
    if a.json:
        print(json.dumps(f, indent=2)); return
    sev = {}
    for x in f:
        sev[x["severity"]] = sev.get(x["severity"], 0) + 1
    print("Summary:", ", ".join(f"{k} {v}" for k, v in sev.items()) or "no findings")
    for x in f:
        print(f"[{x['severity']}] {x['rule']} {x['object']}: {x['message']}")


if __name__ == "__main__":
    main()
