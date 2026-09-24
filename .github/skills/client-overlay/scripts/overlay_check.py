#!/usr/bin/env python3
"""Pre-deployment check of the client overlays. Run from the repository root before first use.

  overlay_check.py [--root .github/skills] [--json]
Checks ado-overlay.json types and values, profile/write-access consistency, leftover TODO or placeholder
values in overlay files, and empty client_terms for the sanitizer. Exit 1 on errors, 2 if files are missing.
"""
import argparse, json, os, re, sys
import yaml

PLACEHOLDER = re.compile(r"\b(TODO|ORGNAME|PROJECTNAME|CLIENTCODE)\b")
REQUIRED = {"profile": str, "write_access": bool, "org_url": str, "project": str, "work_item_types": list,
            "area_paths": list, "production_environments": list, "protected_branches": list}


def check(root):
    errs, warns = [], []
    ovp = os.path.join(root, "client-overlay-ado", "references", "ado-overlay.json")
    with open(ovp, encoding="utf-8") as fh:
        ov = json.load(fh)
    for k, t in REQUIRED.items():
        if k not in ov:
            errs.append(f"ado-overlay.json: missing {k}")
        elif not isinstance(ov[k], t):
            errs.append(f"ado-overlay.json: {k} must be {t.__name__}")
    prof = str(ov.get("profile", "")).upper()
    if prof not in ("A", "B", "C"):
        errs.append("profile must be A, B or C")
    if prof == "C" and ov.get("write_access"):
        errs.append("Profile C cannot have write_access true")
    url = str(ov.get("org_url", ""))
    if not (re.match(r"^https://dev\.azure\.com/[A-Za-z0-9_-]+/?$", url) or re.match(r"^https://[\w.-]+(:\d+)?/(tfs/)?[\w-]+/?$", url)):
        errs.append(f"org_url '{url}' is not an ADO Services or Server collection URL")
    for k, v in ov.items():
        if PLACEHOLDER.search(json.dumps(v)):
            errs.append(f"ado-overlay.json: {k} still holds a placeholder")
    for k in ("production_environments", "protected_branches", "area_paths", "work_item_types"):
        if isinstance(ov.get(k), list) and not ov[k]:
            errs.append(f"ado-overlay.json: {k} is empty")
    if ov.get("write_access") and prof in ("A", "B"):
        warns.append("write_access is true: confirm written client approval is on file")
    for rel in ("client-overlay-ado/SKILL.md", "client-overlay/SKILL.md"):
        p = os.path.join(root, rel)
        if os.path.exists(p):
            n = len(PLACEHOLDER.findall(open(p, encoding="utf-8").read()))
            if n:
                (errs if rel.startswith("client-overlay-ado") else warns).append(f"{rel}: {n} TODO/placeholder values left")
    sp = os.path.join(root, "client-overlay-ado", "references", "sanitizer-patterns.yaml")
    if os.path.exists(sp) and not (yaml.safe_load(open(sp, encoding="utf-8")) or {}).get("client_terms"):
        warns.append("sanitizer client_terms is empty: add client codenames and product names")
    return {"profile": prof, "errors": errs, "warnings": warns, "ok": not errs}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".github/skills"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        r = check(a.root)
    except (OSError, ValueError) as e:
        print(f"Input error: {e}", file=sys.stderr); sys.exit(2)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"Profile {r['profile']}: {'OK' if r['ok'] else 'NOT READY'}")
        for e in r["errors"]:
            print("  ERROR:", e)
        for w in r["warnings"]:
            print("  WARN: ", w)
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
