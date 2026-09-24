#!/usr/bin/env python3
"""Redact and tokenize sensitive values in text before AI analysis.

  sanitize.py INPUT [--patterns overlay.yaml ...] [--map-out .sanitizer/map.json] [--out OUTPUT] [--report]

- Secrets are dropped (not reversible). Identifiers get stable typed tokens: <HOST_01>, <IP_03>, ...
- The same value maps to the same token across runs when the same --map-out file is reused.
- If a classification/control marking is found, prints nothing from the input and exits 3.
Exit codes: 0 ok, 3 stop marking found, 2 usage error.
"""
import argparse, json, math, os, re, sys
from collections import Counter
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "..", "references", "default-patterns.yaml")


def load_config(paths):
    cfg = {"stop_markings": [], "patterns": [], "client_terms": [], "entropy": {}}
    for p in [DEFAULT] + list(paths or []):
        with open(p, encoding="utf-8") as fh:
            d = yaml.safe_load(fh) or {}
        cfg["stop_markings"] += d.get("stop_markings") or []
        cfg["patterns"] += d.get("patterns") or []
        cfg["client_terms"] += d.get("client_terms") or []
        cfg["entropy"].update(d.get("entropy") or {})
    return cfg


def entropy(s):
    c = Counter(s)
    return -sum(n / len(s) * math.log2(n / len(s)) for n in c.values())


class Tokenizer:
    def __init__(self, mapping):
        self.map = mapping  # value -> token
        self.counts = Counter(t.strip("<>").rsplit("_", 1)[0] for t in mapping.values())

    def token(self, kind, value):
        if value in self.map:
            return self.map[value]
        self.counts[kind] += 1
        tok = f"<{kind}_{self.counts[kind]:02d}>"
        self.map[value] = tok
        return tok


def sanitize(text, cfg, tok):
    for m in cfg["stop_markings"]:
        if re.search(m, text):
            return None, {"stopped": True}
    stats = Counter()
    for term in sorted(set(cfg["client_terms"]), key=len, reverse=True):
        rx = re.compile(re.escape(term), re.I)
        text, n = rx.subn(lambda m: tok.token("CLIENT_TERM", m.group(0).lower()), text)
        stats["client_term"] += n
    for p in cfg["patterns"]:
        rx = re.compile(p["regex"])
        if p.get("reversible", True) is False:
            if p["name"] == "kv_secret":  # keep the key name for context
                text, n = rx.subn(lambda m: f"{m.group(1)}{m.group(2)}<SECRET_REDACTED>", text)
            else:
                text, n = rx.subn("<SECRET_REDACTED>", text)
        else:
            text, n = rx.subn(lambda m: m.group(0) if m.group(0).startswith("<") else tok.token(p["token"], m.group(0)), text)
        stats[p["name"]] += n
    e = cfg["entropy"]
    if e:
        ml, mb = int(e.get("min_length", 32)), float(e.get("min_bits_per_char", 4.0))
        def ent(m):
            s = m.group(0)
            if entropy(s) >= mb:
                stats["high_entropy"] += 1
                return "<SECRET_REDACTED>"
            return s
        text = re.sub(r"(?<![<\w])[A-Za-z0-9+/=_\-]{%d,}(?![>\w])" % ml, ent, text)
    return text, dict(stats)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--patterns", action="append", default=[])
    ap.add_argument("--map-out", default=".sanitizer/map.json")
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print redaction counts to stderr")
    a = ap.parse_args()
    cfg = load_config(a.patterns)
    mapping = {}
    if os.path.exists(a.map_out):
        with open(a.map_out, encoding="utf-8") as fh:
            mapping = json.load(fh)
    tok = Tokenizer(mapping)
    with open(a.input, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    out, stats = sanitize(text, cfg, tok)
    if out is None:
        print("STOP: classification or control marking detected. Input not processed. "
              "Use the client-approved environment or a pre-sanitized extract.", file=sys.stderr)
        sys.exit(3)
    os.makedirs(os.path.dirname(os.path.abspath(a.map_out)), exist_ok=True)
    fd = os.open(a.map_out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(tok.map, fh, indent=1)
    os.chmod(a.map_out, 0o600)  # the map holds original values; owner-only
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(out)
    else:
        sys.stdout.write(out)
    if a.report:
        print("Redactions: " + (", ".join(f"{k}={v}" for k, v in sorted(stats.items()) if v) or "none"), file=sys.stderr)


if __name__ == "__main__":
    main()
