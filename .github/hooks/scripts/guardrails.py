#!/usr/bin/env python3
"""preToolUse guardrail for the SRE Copilot kit. Enforces tenant-profile rules deterministically.

Reads the hook payload on stdin (Copilot CLI camelCase or VS Code-compatible snake_case), reads the tenant
profile from the ADO overlay, and prints one decision JSON:
  deny  -> {"permissionDecision":"deny","permissionDecisionReason":...}
  ask   -> {"permissionDecision":"ask", ...}    (human must approve in the client)
  allow -> no output (normal permission flow continues)
Any crash exits non-zero, which Copilot treats as deny (fail-closed). Keep this fast: timeouts fail open.
"""
import json, os, re, sys, time

OVERLAY = ".github/skills/client-overlay-ado/references/ado-overlay.json"
AUDIT = "out/.audit/guardrail-decisions.jsonl"
ADO_PREFIX = re.compile(r"^(mcp__)?ado([/_\-.:]|$)", re.I)
ADO_READ = re.compile(r"(^|[_\-/.])(get|list|search|query|read|show|batch_get|my_)", re.I)
ADO_ASK = re.compile(r"(wit_create_work_item|wit_add_work_item_comment|create_work_item|add_work_item_comment)", re.I)

SHELL_TOOLS = {"bash", "powershell", "shell", "runinterminal", "run_in_terminal", "runterminalcommand", "execute"}
READ_TOOLS = {"view", "read", "readfile", "read_file", "grep", "glob", "search", "filesearch", "textsearch"}
WRITE_TOOLS = {"create", "edit", "write", "str_replace_editor", "apply_patch", "createfile", "editfiles", "create_file", "replace_string_in_file", "insert_edit_into_file"}
WEB_TOOLS = {"web_fetch", "web_search", "fetch", "fetch_webpage", "websearch", "webfetch"}

DANGEROUS_SHELL = [
    (r"\bterraform\s+(apply|destroy|import|state\s+(rm|mv|push))\b", "Terraform state-changing command"),
    (r"\baz\s+[\w\s-]*\b(delete|purge|remove)\b", "Azure CLI delete/purge"),
    (r"\baz\s+deployment\s+[\w\s-]*\bcreate\b", "Azure deployment create (use what-if and a pipeline)"),
    (r"\baz\s+pipelines\s+(run|release\s+create|update|delete)\b", "Pipeline run or change"),
    (r"\baz\s+repos\s+(policy|pr\s+(update|set-vote))\b", "Repo policy or PR approval change"),
    (r"\baz\s+boards\s+work-item\s+(update|delete)\b", "Work item update/delete"),
    (r"\baz\s+devops\s+(security|service-endpoint|user)\b", "ADO security, service connection or user change"),
    (r"\bkubectl\s+(delete|apply|drain|cordon|scale|rollout\s+restart|patch|replace)\b", "Kubernetes state change"),
    (r"\bhelm\s+(install|upgrade|uninstall|rollback)\b", "Helm release change"),
    (r"\bgit\s+push\b", "git push (changes go through a reviewed PR)"),
    (r"\bgit\s+(add|commit)\b[^\n]*(\s|/)(out|\.sanitizer|inputs)(/|\s|$)", "Committing client-derived data"),
    (r"\bgit\s+add\s+(-f|--force)\b", "Force-adding ignored files"),
]


def load_profile():
    try:
        with open(OVERLAY, encoding="utf-8") as fh:
            ov = json.load(fh)
        return str(ov.get("profile", "C")).upper(), bool(ov.get("write_access", False))
    except (OSError, ValueError):
        return "C", False  # no overlay -> most restrictive


def norm(payload):
    name = payload.get("toolName") or payload.get("tool_name") or ""
    args = payload.get("toolArgs", payload.get("tool_input", {}))
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            args = {"raw": args}
    return str(name), args if isinstance(args, dict) else {"raw": args}


def arg_text(args):
    return json.dumps(args, ensure_ascii=False)


def paths_in(args):
    keys = ("path", "filePath", "file_path", "paths", "filePaths", "files", "includePattern", "pattern", "target_file", "dirPath")
    out = []
    for k in keys:
        v = args.get(k)
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, list):
            out += [x for x in v if isinstance(x, str)]
    return out


def rel(p):
    p = p.replace("\\", "/")
    cwd = os.getcwd().replace("\\", "/").rstrip("/") + "/"
    return p[len(cwd):] if p.startswith(cwd) else p.lstrip("./")


def decide(name, args, profile, write_access):
    low = name.lower()
    base = re.split(r"[/:]", low)[-1]
    text = arg_text(args)
    paths = [rel(p) for p in paths_in(args)]

    # 1. Sanitizer map and raw inputs are never read directly by the model.
    if ".sanitizer" in text and base not in SHELL_TOOLS:
        return "deny", "The sanitizer token map is off-limits."
    if base in READ_TOOLS and any(p.startswith("inputs/") for p in paths):
        return "deny", "Raw inputs must be sanitized first: run the sre-telemetry-sanitizer script and read the copy in out/."

    # 2. Shell commands.
    if base in SHELL_TOOLS:
        cmd = str(args.get("command") or args.get("cmd") or args.get("raw") or text)
        if ".sanitizer" in cmd and "sanitize.py" not in cmd:
            return "deny", "The sanitizer token map is off-limits."
        if re.search(r"\b(cat|type|less|more|head|tail|Get-Content|gc)\b[^|;&]*\binputs/", cmd, re.I):
            return "deny", "Raw inputs must go through sanitize.py, not be printed."
        for pat, why in DANGEROUS_SHELL:
            if re.search(pat, cmd, re.I):
                return "deny", f"Blocked by SRE guardrail: {why}. Propose it for a human to run through the approved process."
        if "work_items.py" in cmd and re.search(r"\bapply\b", cmd):
            if profile == "C" or not write_access:
                return "deny", "Work item writes are disabled for this tenant profile. Use plan with --payload-out."
            return "ask", "Creating Azure Boards work items. Confirm the previewed plan."
        if profile == "C" and re.search(r"\b(curl|wget|Invoke-WebRequest|iwr|az\s+rest|ssh|scp)\b", cmd, re.I):
            return "deny", "Network commands are disabled in Profile C."
        return "allow", ""

    # 3. ADO MCP tools.
    if ADO_PREFIX.search(low) or low.startswith("ado"):
        if profile == "C":
            return "deny", "ADO tools are disabled in Profile C."
        if ADO_ASK.search(low):
            if not write_access:
                return "deny", "ADO writes are disabled (write_access false in the overlay)."
            return "ask", "Writing to Azure Boards. Confirm this matches the previewed plan."
        if ADO_READ.search(base):
            return "allow", ""
        return "deny", f"ADO tool '{name}' can change the tenant and is not on the kit's allowlist."

    # 4. Profile C: no web, edits only under out/.
    if profile == "C":
        if base in WEB_TOOLS:
            return "deny", "Web access is disabled in Profile C."
        if base in WRITE_TOOLS and any(not p.startswith("out/") for p in paths):
            return "deny", "Profile C: create and edit files only under out/."
    return "allow", ""


def audit(name, decision, reason, profile):
    try:
        os.makedirs(os.path.dirname(AUDIT), exist_ok=True)
        with open(AUDIT, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "tool": name,
                                 "decision": decision, "reason": reason, "profile": profile}) + "\n")
    except OSError:
        pass  # auditing must never block work


def main():
    payload = json.load(sys.stdin)
    name, args = norm(payload)
    profile, write_access = load_profile()
    decision, reason = decide(name, args, profile, write_access)
    if decision != "allow":
        audit(name, decision, reason, profile)
        print(json.dumps({"permissionDecision": decision, "permissionDecisionReason": reason}))


if __name__ == "__main__":
    main()
