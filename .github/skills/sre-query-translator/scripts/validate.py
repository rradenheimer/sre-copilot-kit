#!/usr/bin/env python3
"""Static checks for observability queries: KQL, Splunk SPL, PromQL.

  validate.py --lang kql|spl|promql (FILE | --query "...") [--json]
Not a full parser. Catches the mistakes that make queries wrong or expensive: unbalanced brackets and
quotes, missing time bounds, full-scan patterns, late filtering, and high-cardinality labels.
Exit 1 on High findings, 2 on input error.
"""
import argparse, json, re, sys

HIGH_CARD = re.compile(r"\b(user_?id|request_?id|trace_?id|session_?id|ip|client_?ip|email|url|path)\b", re.I)


def balance(q):
    out, stack, pairs = [], [], {")": "(", "]": "[", "}": "{"}
    in_str = None
    for i, ch in enumerate(q):
        if in_str:
            if ch == in_str and q[i - 1] != "\\":
                in_str = None
            continue
        if ch in "\"'":
            in_str = ch
        elif ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack.pop() != pairs[ch]:
                out.append(("High", f"Unbalanced '{ch}' at position {i}."))
    if in_str:
        out.append(("High", "Unterminated string literal."))
    if stack:
        out.append(("High", f"Unclosed '{stack[-1]}'."))
    return out


def kql(q):
    f = []
    stages = [s.strip() for s in q.split("|")]
    if re.match(r"(?i)^\s*search\s", q) or re.search(r"(?i)\bsearch\s+\*", q):
        f.append(("High", "`search` scans every table; query a specific table."))
    if not re.search(r"(?i)\b(TimeGenerated|timestamp)\b\s*(>|>=|between)|\bago\(", q):
        f.append(("High", "No time filter on TimeGenerated/timestamp; the query scans the full retention."))
    else:
        idx = next((i for i, s in enumerate(stages) if re.search(r"(?i)(TimeGenerated|timestamp|ago\()", s)), 0)
        if any(re.match(r"(?i)summarize\b", s) for s in stages[:idx]):
            f.append(("High", "Time filter comes after `summarize`; it filters aggregated rows (or fails if the column is gone). Filter on time before aggregating."))
        elif idx > 1:
            f.append(("Medium", "Time filter is not the first operator after the table; filter on time first."))
    if re.search(r"(?i)\bcontains\b", q) and not re.search(r"(?i)\bhas\b", q):
        f.append(("Low", "`contains` is slower than `has` for whole terms."))
    if re.search(r"(?i)\bjoin\b", q) and not re.search(r"(?i)kind\s*=", q):
        f.append(("Medium", "`join` without `kind=`; the default innerunique can drop rows."))
    if re.search(r"(?i)^\s*(requests|dependencies|exceptions|traces)\b", q) and re.search(r"\bTimeGenerated\b", q):
        f.append(("Medium", "Classic Application Insights tables use `timestamp`, not `TimeGenerated`."))
    if re.search(r"(?i)^\s*App(Requests|Dependencies|Exceptions|Traces)\b", q) and re.search(r"\btimestamp\b", q):
        f.append(("Medium", "Workspace App* tables use `TimeGenerated`, not `timestamp`."))
    return f


def spl(q):
    f = []
    if not re.search(r"(?i)\bindex\s*=", q):
        f.append(("High", "No `index=`; the search runs across all default indexes."))
    if not re.search(r"(?i)\b(earliest|latest)\s*=", q):
        f.append(("Medium", "No earliest/latest; time range depends on the UI picker."))
    if re.search(r"(?i)^\s*\*|\bindex\s*=\s*\*", q):
        f.append(("High", "Wildcard index or leading `*` scans everything."))
    first_pipe = q.find("|")
    if first_pipe > 0 and re.search(r"(?i)\|\s*(search|where)\b", q) and len(q[:first_pipe].split()) <= 2:
        f.append(("Medium", "Filtering after the first pipe; move filters into the base search."))
    if re.search(r"(?i)\|\s*transaction\b", q):
        f.append(("Low", "`transaction` is expensive; prefer `stats` by a correlation field."))
    return f


def promql(q):
    f = []
    if re.search(r"\brate\(\s*[a-zA-Z_:][\w:]*(\{[^}]*\})?\s*\)", q):
        f.append(("High", "`rate()` needs a range vector, e.g. rate(metric[5m])."))
    if re.search(r"\b(rate|increase|irate)\(\s*[a-zA-Z_:][\w:]*_(bytes|seconds|ratio)\b(?!_(total|count|sum|bucket))", q):
        f.append(("Medium", "rate()/increase() on what looks like a gauge; use it only on counters (_total, _count, _sum, _bucket)."))
    for lbls in re.findall(r"by\s*\(([^)]*)\)", q):
        if HIGH_CARD.search(lbls):
            f.append(("High", f"Aggregating by a high-cardinality label ({lbls.strip()})."))
    if re.search(r"histogram_quantile\(", q) and not re.search(r"\ble\b", q):
        f.append(("High", "histogram_quantile must keep the `le` label in its `by` clause."))
    if re.search(r'=~"\.\*', q):
        f.append(("Low", 'Leading `.*` regex matcher is slow.'))
    return f


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?"); ap.add_argument("--query"); ap.add_argument("--lang", required=True, choices=["kql", "spl", "promql"])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        q = a.query if a.query is not None else open(a.file, encoding="utf-8").read()
    except (OSError, TypeError) as e:
        print(f"Input error: provide FILE or --query ({e})", file=sys.stderr); sys.exit(2)
    q = "\n".join(l for l in q.splitlines() if not l.strip().startswith(("//", "#", "``")))
    found = balance(q) + {"kql": kql, "spl": spl, "promql": promql}[a.lang](q)
    res = [{"severity": s, "message": m} for s, m in found]
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        print("No findings." if not res else "\n".join(f"[{r['severity']}] {r['message']}" for r in res))
    sys.exit(1 if any(r["severity"] == "High" for r in res) else 0)


if __name__ == "__main__":
    main()
