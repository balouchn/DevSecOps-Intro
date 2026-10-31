#!/usr/bin/env python3
"""Compare tools/versions.yaml against the latest upstream releases.

Usage:  python3 tools/check-versions.py [--json]

Exit code 1 when any pin has drifted, so CI can open an issue. Set GITHUB_TOKEN
to avoid the 60 requests/hour anonymous rate limit.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "tools", "versions.yaml")
API = "https://api.github.com/repos/%s/releases/latest"


def load_manifest():
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML is required: pip install pyyaml")
    with open(MANIFEST) as fh:
        return yaml.safe_load(fh)


def latest_release(repo):
    req = urllib.request.Request(API % repo, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        return None, "HTTP %s" % exc.code
    except Exception as exc:  # network, timeout, JSON
        return None, str(exc)
    return data.get("tag_name"), None


def normalise(version):
    """v1.2.3 / 1.2.3 / cosign-v1.2.3 -> (1, 2, 3); unparseable -> None."""
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", str(version))
    if not match:
        return None
    return tuple(int(part or 0) for part in match.groups())


def main():
    manifest = load_manifest()
    rows, drifted = [], 0
    for name, spec in sorted(manifest.get("tools", {}).items()):
        repo = spec.get("github")
        pin = str(spec.get("pin", ""))
        if not repo:
            rows.append((name, pin, "-", "no github repo in manifest", spec.get("labs", [])))
            continue
        upstream, err = latest_release(repo)
        if err:
            rows.append((name, pin, "?", "lookup failed: " + err, spec.get("labs", [])))
            continue
        pinned_v, upstream_v = normalise(pin), normalise(upstream)
        held = bool(spec.get("hold"))
        if pin == "latest":
            state = "unpinned"
        elif pinned_v and upstream_v and pinned_v == upstream_v:
            state = "current"
        elif pinned_v and upstream_v and pinned_v < upstream_v:
            # A documented hold is a decision, not drift: it must not page anyone.
            state = "held" if held else "DRIFTED"
            drifted += 0 if held else 1
        else:
            state = "check by hand"
        rows.append((name, pin, upstream, state, spec.get("labs", [])))

    if "--json" in sys.argv:
        print(json.dumps([dict(zip(("tool", "pin", "latest", "state", "labs"), r)) for r in rows], indent=2))
    else:
        print("%-12s %-12s %-12s %-14s %s" % ("TOOL", "PINNED", "LATEST", "STATE", "LABS"))
        for name, pin, upstream, state, labs in rows:
            print("%-12s %-12s %-12s %-14s %s" % (name, pin, upstream, state, ",".join(str(x) for x in labs)))
        held_names = [n for n, spec in manifest.get("tools", {}).items() if spec.get("hold")]
        print("\nchecked %s, %d drifted, %d held" % (manifest.get("checked", "?"), drifted, len(held_names)))
        if held_names:
            print("held on purpose (see the hold: note in versions.yaml): %s" % ", ".join(sorted(held_names)))
        if drifted:
            print("Re-pin before the next cohort; mid-semester only if a pin is broken.")
    return 1 if drifted else 0


if __name__ == "__main__":
    sys.exit(main())
