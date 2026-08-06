#!/usr/bin/env python3
"""Validate the mkdocs `redirects` plugin map, and cross-check it against frontmatter.

    python3 scripts/check_redirects.py en/mkdocs.yml en/docs
    python3 scripts/check_redirects.py en/mkdocs.yml en/docs --gate

Checks that every redirect target exists, that no source is shadowed by a real
file, that there are no chains (the plugin does not follow them), and that no map
was left pointing at a superseded version after a version bump.

`CANONICAL_UNREACHABLE` only applies under `--policy latest-only`, and is skipped
otherwise: under the default `keep-all` a canonical is a versioned path, which is a
real file, so it cannot depend on a redirect existing.
"""
import os
import re
import sys
import json
import argparse
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fm_lib import (  # noqa: E402
    discover_versions, current_release, split_version, product_of, md_files,
)


def parse_redirect_maps(mkdocs_path):
    """Pull `redirect_maps` out of mkdocs.yml without a full YAML load.

    mkdocs.yml here contains custom tags and a very large nav, and a strict YAML
    parse is both slow and prone to choking on them. The block is flat
    `source: target` pairs, so a scoped regex is more robust than a full parse.
    """
    text = open(mkdocs_path, encoding="utf-8", errors="replace").read()
    m = re.search(r"^\s*redirect_maps:\s*\n(.*?)(?=\n\s{0,4}\S|\Z)", text, re.S | re.M)
    if not m:
        return {}
    pairs = re.findall(r"^\s+(\S+\.md):\s*(\S+\.md)\s*$", m.group(1), re.M)
    return dict(pairs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mkdocs_yml", nargs="?", default="en/mkdocs.yml")
    ap.add_argument("docs_root", nargs="?", default="en/docs")
    ap.add_argument("--policy", default="keep-all",
                    choices=["keep-all", "latest-only", "strip-all"])
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--gate", action="store_true")
    args = ap.parse_args()

    root = args.docs_root.rstrip("/")
    redirects = parse_redirect_maps(args.mkdocs_yml)
    versions = discover_versions(root)
    on_disk = set(md_files(root))

    findings = []

    def add(sev, code, msg, where=None):
        findings.append({"severity": sev, "code": code, "message": msg, "where": where})

    # 1. Every redirect target must exist.
    for src, tgt in sorted(redirects.items()):
        if tgt not in on_disk:
            add("blocking", "REDIRECT_TARGET_MISSING",
                f"`{src}` redirects to `{tgt}`, which is not a file in {root}.", src)

    # 2. A redirect whose source is also a real file never fires.
    for src, tgt in sorted(redirects.items()):
        if src in on_disk:
            add("should-fix", "REDIRECT_SHADOWED",
                f"`{src}` exists as a real page, so its redirect to `{tgt}` never fires. "
                f"Delete the redirect or the file.", src)

    # 3. Redirect chains: the plugin does not follow them.
    for src, tgt in sorted(redirects.items()):
        if tgt in redirects:
            add("blocking", "REDIRECT_CHAIN",
                f"`{src}` -> `{tgt}`, but `{tgt}` is itself redirected to "
                f"`{redirects[tgt]}`. The plugin does not follow chains, so this "
                f"lands on a redirect stub.", src)

    # 4. Only under latest-only: a version-less canonical needs a redirect to resolve.
    if args.policy == "latest-only":
        for rel in sorted(on_disk):
            ver, stripped = split_version(rel)
            if ver is None:
                continue
            if ver != current_release(product_of(rel), versions):
                continue
            if stripped in redirects or stripped in on_disk:
                continue
            add("blocking", "CANONICAL_UNREACHABLE",
                f"`{rel}` is the current release, so its canonical_url is the "
                f"version-less `{stripped}` — but nothing resolves there. Add "
                f"`{stripped}: {rel}` to redirect_maps, or that canonical URL 404s.", rel)

    # 5. Redirects that skip the current release (a stale map after a version bump).
    for src, tgt in sorted(redirects.items()):
        tv = split_version(tgt)[0]
        if not tv:
            continue
        cur = current_release(product_of(tgt), versions)
        if cur and tv != cur and tv not in ("next", "latest"):
            add("should-fix", "REDIRECT_STALE_VERSION",
                f"`{src}` redirects to `{tgt}` (version {tv}) while the current "
                f"release is {cur}. Likely a map that wasn't updated on the version bump.", src)

    sev = collections.Counter(f["severity"] for f in findings)
    codes = collections.Counter((f["code"], f["severity"]) for f in findings)

    print("=" * 70)
    print("REDIRECT CHECK")
    print("=" * 70)
    print(f"redirect_maps entries : {len(redirects)}")
    print(f"pages on disk         : {len(on_disk)}")
    print(f"total findings        : {len(findings)}"
          f"   (blocking={sev['blocking']}, should-fix={sev['should-fix']})")
    if codes:
        print()
        print(f"{'COUNT':>6}  {'SEVERITY':<11} CODE")
        print("-" * 70)
        for (c, s), n in codes.most_common():
            print(f"{n:>6}  {s:<11} {c}")
        print()
        for f in findings:
            print(f"  [{f['severity']}] {f['code']}: {f['message']}")
    else:
        print("\nNo redirect problems found.")

    if args.json_out:
        json.dump(findings, open(args.json_out, "w"), indent=1)
        print(f"\nJSON -> {args.json_out}")

    return 1 if (args.gate and sev["blocking"]) else 0


if __name__ == "__main__":
    sys.exit(main())
