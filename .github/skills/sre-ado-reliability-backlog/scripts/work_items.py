#!/usr/bin/env python3
"""Plan (dry-run) or apply Azure Boards work item creation from items.json.

  work_items.py plan  items.json --overlay overlay.json
  work_items.py apply items.json --overlay overlay.json --confirm

apply requires --confirm, overlay "write_access": true, and ADO_TOKEN in the environment
(Entra access token or PAT). Uses Azure DevOps REST API 7.1.
"""
import argparse, base64, html, json, os, sys, urllib.parse

API = "7.1"
BASE_TAG = "sre"


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def validate(item, ov):
    errs = []
    if not item.get("title"):
        errs.append("missing title")
    elif len(item["title"]) > 255:
        errs.append("title over 255 characters")
    types = ov.get("work_item_types") or []
    if types and item.get("type") not in types:
        errs.append(f"type '{item.get('type')}' not in overlay work_item_types {types}")
    areas = ov.get("area_paths") or []
    if item.get("area_path") and areas and not any(item["area_path"] == a or item["area_path"].startswith(a + "\\") for a in areas):
        errs.append(f"area_path '{item['area_path']}' not under overlay area_paths")
    p = item.get("priority")
    if p is not None and p not in (1, 2, 3, 4):
        errs.append("priority must be 1-4")
    for f in ov.get("required_fields") or []:
        if f not in (item.get("fields") or {}) and f not in ("System.Title",):
            errs.append(f"required field {f} missing")
    return errs


def to_html(text):
    return html.escape(text or "").replace("\n", "<br/>")


def patch_for(item, ov, source):
    ops = [{"op": "add", "path": "/fields/System.Title", "value": item["title"]}]
    add = lambda f, v: ops.append({"op": "add", "path": f"/fields/{f}", "value": v})
    desc = item.get("description", "")
    if source:
        desc = f"{desc}\n\nSource: {source}".strip()
    if desc:
        add("System.Description", to_html(desc))
    if item.get("acceptance_criteria"):
        add("Microsoft.VSTS.Common.AcceptanceCriteria", to_html(item["acceptance_criteria"]))
    if item.get("priority"):
        add("Microsoft.VSTS.Common.Priority", item["priority"])
    for key, field in (("area_path", "System.AreaPath"), ("iteration_path", "System.IterationPath")):
        if item.get(key):
            add(field, item[key])
    tags = [ov.get("base_tag", BASE_TAG)] + list(item.get("tags") or [])
    add("System.Tags", "; ".join(dict.fromkeys(tags)))
    for f, v in (item.get("fields") or {}).items():
        add(f, v)
    org = ov.get("org_url", "").rstrip("/")
    if item.get("parent_id"):
        ops.append({"op": "add", "path": "/relations/-", "value": {
            "rel": "System.LinkTypes.Hierarchy-Reverse", "url": f"{org}/_apis/wit/workItems/{item['parent_id']}"}})
    for l in item.get("links") or []:
        ops.append({"op": "add", "path": "/relations/-", "value": {
            "rel": l.get("rel", "System.LinkTypes.Related"), "url": f"{org}/_apis/wit/workItems/{l['id']}"}})
    return ops


def auth_header(token):
    if token.count(".") == 2:  # JWT -> Entra bearer token
        return f"Bearer {token}"
    return "Basic " + base64.b64encode(f":{token}".encode()).decode()


def create(ov, item, ops, token):
    import urllib.request
    url = f"{ov['org_url'].rstrip('/')}/{urllib.parse.quote(ov['project'])}/_apis/wit/workitems/${urllib.parse.quote(item['type'])}?api-version={API}"
    req = urllib.request.Request(url, data=json.dumps(ops).encode(), method="POST",
                                 headers={"Content-Type": "application/json-patch+json", "Authorization": auth_header(token)})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["plan", "apply"])
    ap.add_argument("items")
    ap.add_argument("--overlay", required=True)
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--payload-out", help="write payloads to this file (for Profile C manual import)")
    a = ap.parse_args()
    ov, data = load(a.overlay), load(a.items)
    items, source = data.get("items", []), data.get("source", "")

    plans, bad = [], 0
    print(f"{'#':<3} {'Type':<14} {'Area':<24} {'Pri':<4} Title / issues")
    for i, it in enumerate(items, 1):
        errs = validate(it, ov)
        bad += bool(errs)
        plans.append({"item": it, "ops": patch_for(it, ov, source) if not errs else None, "errors": errs})
        print(f"{i:<3} {str(it.get('type')):<14} {str(it.get('area_path', '-'))[:23]:<24} {str(it.get('priority', '-')):<4} {it.get('title')}")
        for e in errs:
            print(f"      ERROR: {e}")
    print(f"\n{len(items)} items, {bad} with errors.")

    if a.payload_out:
        with open(a.payload_out, "w", encoding="utf-8") as fh:
            json.dump([{"type": p["item"].get("type"), "patch": p["ops"]} for p in plans if p["ops"]], fh, indent=2)
        print(f"Payloads written to {a.payload_out}")

    if a.mode == "plan":
        print("Dry run only. No changes made.")
        return
    if bad:
        sys.exit("Refusing to apply: fix validation errors first.")
    if not a.confirm:
        sys.exit("Refusing to apply without --confirm (requires explicit human approval).")
    if ov.get("profile") == "C" or not ov.get("write_access"):
        sys.exit("Refusing to apply: overlay is read-only (Profile C or write_access false). Use --payload-out.")
    token = os.environ.get("ADO_TOKEN")
    if not token:
        sys.exit("ADO_TOKEN not set.")
    for p in plans:
        res = create(ov, p["item"], p["ops"], token)
        print(f"Created {res.get('id')}: {res.get('_links', {}).get('html', {}).get('href', '')}")


if __name__ == "__main__":
    main()
