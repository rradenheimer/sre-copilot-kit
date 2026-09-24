#!/usr/bin/env python3
"""Summarize a Terraform plan JSON (terraform show -json plan.out > plan.json) for risk review.

  parse_plan.py plan.json [--json]
Flags destroy/replace on stateful resource types, IAM/role changes and public exposure.
Exit 1 when any High finding exists, 2 on input error.
"""
import argparse, json, re, sys

STATEFUL = re.compile(r"(sql|database|db_|cosmos|storage_account|storage_container|key_vault|kms|disk|volume|"
                      r"redis|dns_zone|dns_record|eventhub|servicebus|s3_bucket|dynamodb|rds|backup)", re.I)
IAM = re.compile(r"(role_assignment|role_definition|iam|policy_attachment|access_policy|federated_identity|"
                 r"user_assigned_identity|service_principal|application_password)", re.I)
EXPOSURE_KEYS = re.compile(r"(public_network_access_enabled|allow_blob_public_access|source_address_prefix|"
                           r"cidr_blocks|ip_rules|public_ip)", re.I)


def action_of(actions):
    a = set(actions or [])
    if a == {"delete", "create"}:
        return "replace"
    if "delete" in a:
        return "delete"
    if "create" in a:
        return "create"
    if "update" in a:
        return "update"
    return "no-op" if a <= {"no-op", "read"} else ",".join(sorted(a))


def analyze(plan):
    counts, findings = {}, []
    for rc in plan.get("resource_changes", []):
        ch = rc.get("change") or {}
        act = action_of(ch.get("actions"))
        counts[act] = counts.get(act, 0) + 1
        if act == "no-op":
            continue
        addr, rtype = rc.get("address", "?"), rc.get("type", "")
        if act in ("delete", "replace") and STATEFUL.search(rtype):
            findings.append(("High", addr, f"{act} of stateful resource ({rtype}); data loss possible"))
        elif act in ("delete", "replace"):
            findings.append(("Medium", addr, f"{act} of {rtype}"))
        if IAM.search(rtype):
            findings.append(("High" if act in ("create", "update") else "Medium", addr, f"identity/permission change ({act})"))
        after = ch.get("after") if isinstance(ch.get("after"), dict) else {}
        before = ch.get("before") if isinstance(ch.get("before"), dict) else {}
        for k, v in after.items():
            if EXPOSURE_KEYS.search(k) and v != before.get(k):
                if v is True or (isinstance(v, (str, list)) and ("0.0.0.0/0" in str(v) or v == "*" or "Internet" in str(v))):
                    findings.append(("High", addr, f"public exposure: {k} -> {v}"))
        if ch.get("replace_paths") and act == "replace":
            paths = [".".join(map(str, p)) for p in ch["replace_paths"]][:3]
            findings.append(("Info", addr, f"replacement forced by: {', '.join(paths)}"))
    order = {"High": 0, "Medium": 1, "Info": 2}
    findings.sort(key=lambda f: order[f[0]])
    return counts, findings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        with open(a.plan, encoding="utf-8") as fh:
            plan = json.load(fh)
    except (OSError, ValueError) as e:
        print(f"Input error: cannot read plan JSON: {e}. Create it with: terraform show -json plan.out > plan.json", file=sys.stderr)
        sys.exit(2)
    counts, findings = analyze(plan)
    if a.json:
        print(json.dumps({"counts": counts, "findings": [dict(zip(("severity", "address", "message"), f)) for f in findings]}, indent=2))
    else:
        print("Changes: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
        for s, addr, msg in findings:
            print(f"[{s}] {addr}: {msg}")
    sys.exit(1 if any(f[0] == "High" for f in findings) else 0)


if __name__ == "__main__":
    main()
