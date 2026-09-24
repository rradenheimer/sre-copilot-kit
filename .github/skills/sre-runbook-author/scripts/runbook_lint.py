#!/usr/bin/env python3
"""Validate a runbook (Markdown) for safety and usability at 3 a.m.

  runbook_lint.py RUNBOOK.md [--json]
Checks: required sections; steps without a command or expected result; destructive commands without a
confirmation/safeguard note; privileged steps not marked; az commands without --subscription;
hard-coded GUIDs/IPs that should be parameters; mitigation without verification.
Also scores each numbered step's automation potential (manual / scriptable).
Exit 1 on High findings, 2 on input error.
"""
import argparse, json, re, sys

REQUIRED = ["Symptoms", "Impact", "Diagnosis", "Mitigation", "Verification", "Rollback", "Escalation"]
DESTRUCTIVE = re.compile(r"\b(delete|drop|truncate|rm\s+-rf|purge|drain|failover|restart\s+(all|--all)|scale\s+.*--replicas[= ]0|destroy|reset)\b", re.I)
SAFEGUARD = re.compile(r"(confirm|approval|approve|double-check|dry[- ]run|what-if|--dry-run|backup|snapshot|safeguard)", re.I)
PRIV = re.compile(r"\b(sudo|break[- ]glass|owner role|global admin|pim|elevat\w*|--admin)\b", re.I)
PRIV_MARK = re.compile(r"(privileged|break-glass|requires approval|⚠)", re.I)
GUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)
IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
CMD = re.compile(r"`[^`]+`|^\s{4,}\S|^```", re.M)


def split_sections(md):
    parts = re.split(r"(?m)^#{1,3}\s+(.+)$", md)
    return {parts[i].strip().lower(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def steps(body):
    out, cur = [], None
    for line in body.splitlines():
        m = re.match(r"^\s*(\d+)[.)]\s+(.*)", line)
        if m:
            cur = [line]; out.append(cur)
        elif cur is not None:
            cur.append(line)
    return ["\n".join(s) for s in out]


def lint(md):
    f, auto = [], []
    add = lambda sev, where, msg: f.append({"severity": sev, "location": where, "message": msg})
    secs = split_sections(md)
    for r in REQUIRED:
        if not any(r.lower() in k for k in secs):
            add("High" if r in ("Mitigation", "Verification", "Rollback", "Escalation") else "Medium", "structure", f"Missing section: {r}")
    for name, body in secs.items():
        for n, st in enumerate(steps(body), 1):
            where = f"{name} step {n}"
            has_cmd = bool(CMD.search(st))
            if has_cmd and not re.search(r"(expect|should (see|return|show)|output|result)", st, re.I):
                add("Medium", where, "Command without an expected result.")
            if not has_cmd and re.search(r"\b(check|look at|see)\b", st, re.I) and not re.search(r"(expect|should|re-?run|repeat) ", st, re.I):
                add("Medium", where, "Ambiguous step: says what to check but not where or how.")
            if DESTRUCTIVE.search(st) and not SAFEGUARD.search(st):
                add("High", where, "Destructive action without a confirmation, dry run or backup note.")
            if PRIV.search(st) and not PRIV_MARK.search(st):
                add("Medium", where, "Privileged step not marked (state the approval or break-glass process).")
            for azl in re.findall(r"\baz\s+[^\n`]+", st):
                if "--subscription" not in azl and not re.search(r"\baz\s+(login|account)\b", azl):
                    add("Low", where, "az command without --subscription; context may point at the wrong subscription.")
            if GUID.search(st) or IP.search(st):
                add("Low", where, "Hard-coded ID or IP; make it a parameter.")
            auto.append({"step": where, "automation": "scriptable" if has_cmd and not PRIV.search(st) else "manual"})
    mit = next((b for k, b in secs.items() if "mitigation" in k), "")
    if mit and not any("verification" in k for k in secs) and not re.search(r"verif", mit, re.I):
        add("High", "mitigation", "Mitigation has no verification.")
    return f, auto


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        md = open(a.file, encoding="utf-8").read()
    except OSError as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    f, auto = lint(md)
    if a.json:
        print(json.dumps({"findings": f, "automation": auto}, indent=2))
    else:
        print("No findings." if not f else "\n".join(f"[{x['severity']}] {x['location']}: {x['message']}" for x in f))
        s = sum(1 for x in auto if x["automation"] == "scriptable")
        print(f"Automation potential: {s} of {len(auto)} steps scriptable.")
    sys.exit(1 if any(x["severity"] == "High" for x in f) else 0)


if __name__ == "__main__":
    main()
