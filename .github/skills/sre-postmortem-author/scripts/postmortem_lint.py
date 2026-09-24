#!/usr/bin/env python3
"""Check a postmortem draft (Markdown) for structure, blameless language and action item quality.

  postmortem_lint.py POSTMORTEM.md [--sections "Summary,Impact,..."] [--json]
Checks: required sections present; blame-oriented phrases; action item table rows missing owner, due date
or done criterion; vague action verbs; timeline entries without UTC. Exit 1 on High findings, 2 on input error.
"""
import argparse, json, re, sys

DEFAULT_SECTIONS = ["Summary", "Impact", "Timeline", "Contributing factors", "What went well", "Action items"]
BLAME = [r"\b(\w+) (failed|forgot|neglected) to\b", r"\bhuman error\b", r"\b(careless|sloppy|negligen\w*)\b",
         r"\bshould have known\b", r"\b(his|her) mistake\b", r"\bdidn'?t bother\b", r"\bat fault\b"]
VAGUE = re.compile(r"^\s*(investigate|look into|consider|monitor|be more careful|improve|review)\b", re.I)
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def sections(md):
    return [m.group(2).strip() for m in re.finditer(r"(?m)^(#{1,3})\s+(.+)$", md)]


def action_rows(md):
    m = re.search(r"(?ims)^#{1,3}\s*action items\s*$(.*?)(?=^#{1,3}\s|\Z)", md)
    if not m:
        return None, []
    rows = [r for r in m.group(1).splitlines() if r.strip().startswith("|")]
    if len(rows) < 2:
        return None, []
    header = [c.strip().lower() for c in rows[0].strip("|").split("|")]
    body = [[c.strip() for c in r.strip("|").split("|")] for r in rows[2:]]
    return header, body


def lint(md, required):
    f = []
    add = lambda sev, where, msg: f.append({"severity": sev, "location": where, "message": msg})
    have = [s.lower() for s in sections(md)]
    for s in required:
        if not any(s.lower() in h for h in have):
            add("High", "structure", f"Missing section: {s}")
    for i, line in enumerate(md.splitlines(), 1):
        for pat in BLAME:
            if re.search(pat, line, re.I):
                add("Medium", f"line {i}", f"Blame-oriented language: '{line.strip()[:80]}'. Reframe around the system.")
                break
    header, rows = action_rows(md)
    if header is None:
        add("High", "action items", "No action item table found (columns: action, owner, priority, due, done criterion).")
    else:
        col = lambda *names: next((header.index(h) for h in header for n in names if n in h), None)
        c_act, c_own, c_due, c_done = col("action"), col("owner"), col("due", "date"), col("done", "criteri", "success")
        for n, r in enumerate(rows, 1):
            cell = lambda c: r[c] if c is not None and c < len(r) else ""
            if not cell(c_own) or cell(c_own).lower() in ("tbd", "?", "-"):
                add("High", f"action {n}", "No owner.")
            if not DATE.search(cell(c_due)):
                add("Medium", f"action {n}", "No due date (YYYY-MM-DD).")
            if not cell(c_done) or cell(c_done).lower() in ("tbd", "-"):
                add("Medium", f"action {n}", "No done criterion.")
            if VAGUE.search(cell(c_act)):
                add("Low", f"action {n}", f"Vague action '{cell(c_act)[:50]}'; state the concrete change.")
    tl = re.search(r"(?ims)^#{1,3}\s*timeline\s*$(.*?)(?=^#{1,3}\s|\Z)", md)
    if tl and re.search(r"\d{1,2}:\d{2}", tl.group(1)) and not re.search(r"\bUTC\b|Z\b", tl.group(1)):
        add("Low", "timeline", "Times have no timezone; use UTC.")
    return f


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file"); ap.add_argument("--sections"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        md = open(a.file, encoding="utf-8").read()
    except OSError as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    req = [s.strip() for s in a.sections.split(",")] if a.sections else DEFAULT_SECTIONS
    f = lint(md, req)
    if a.json:
        print(json.dumps(f, indent=2))
    else:
        print("No findings." if not f else "\n".join(f"[{x['severity']}] {x['location']}: {x['message']}" for x in f))
    sys.exit(1 if any(x["severity"] == "High" for x in f) else 0)


if __name__ == "__main__":
    main()
