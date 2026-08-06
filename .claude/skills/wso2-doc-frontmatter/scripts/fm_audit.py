#!/usr/bin/env python3
"""Validate frontmatter across the WSO2 API Platform docs. Read-only.

    python3 scripts/fm_audit.py en/docs                     # human summary
    python3 scripts/fm_audit.py en/docs --json out.json     # machine-readable
    python3 scripts/fm_audit.py en/docs --policy strip-all   # audit as-is today
    python3 scripts/fm_audit.py en/docs --files a.md b.md    # just these files
    python3 scripts/fm_audit.py en/docs --gate               # exit 1 on blocking

Exit codes: 0 clean (or no blocking issues), 1 blocking issues found with --gate.
"""
import os
import sys
import json
import argparse
import collections
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fm_lib import (  # noqa: E402
    BASE, REQUIRED, AUTHOR, DESC_MAX, DESC_MIN, TITLE_MAX,
    effective_allowed_ct, CT_ALIASES, discover_versions, site_paths,
    split_frontmatter, md_files, norm_date, split_version,
    load_frontmatter, parse_frontmatter_yaml, HAVE_PYYAML, is_legacy_url,
)


def selftest(root):
    """Prove the dependency-free parser agrees with PyYAML on every real page.

    Only meaningful where PyYAML is installed — that is the point: run it once
    somewhere it is available, and you can trust the fallback everywhere it isn't.
    """
    if not HAVE_PYYAML:
        print("PyYAML is not installed here, so there is nothing to compare against.")
        print("Run --selftest on a machine that has it; the fallback is what runs otherwise.")
        return 0
    import yaml
    checked = mismatched = 0
    for rel in md_files(root):
        raw, _ = split_frontmatter(open(os.path.join(root, rel), encoding="utf-8",
                                       errors="replace").read())
        if raw is None:
            continue
        try:
            ref = yaml.safe_load(raw) or {}
        except Exception:
            continue
        try:
            got = parse_frontmatter_yaml(raw)
        except ValueError as e:
            print(f"  FALLBACK REFUSED {rel}: {e}")
            mismatched += 1
            continue
        checked += 1
        if got != ref:
            mismatched += 1
            print(f"  MISMATCH {rel}")
            for k in sorted(set(ref) | set(got)):
                if ref.get(k) != got.get(k):
                    print(f"     {k}: pyyaml={ref.get(k)!r}  fallback={got.get(k)!r}")
    print(f"\nself-test: {checked} pages compared, {mismatched} mismatch(es).")
    return 1 if mismatched else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docs_root", nargs="?", default="en/docs")
    ap.add_argument("--files", nargs="*", default=None,
                    help="Limit to these paths (relative to docs_root or to cwd).")
    ap.add_argument("--policy", default="keep-all",
                    choices=["keep-all", "latest-only", "strip-all"])
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--gate", action="store_true", help="Exit 1 if any blocking issue.")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="Verify the built-in YAML parser against PyYAML on every page.")
    args = ap.parse_args()

    if args.selftest:
        return selftest(args.docs_root.rstrip("/"))

    root = args.docs_root.rstrip("/")
    versions = discover_versions(root)
    allowed_ct = effective_allowed_ct()

    if args.files:
        files = []
        for f in args.files:
            f = f.replace("\\", "/")
            files.append(f[len(root) + 1:] if f.startswith(root + "/") else f)
    else:
        files = md_files(root)

    findings = []

    def add(rel, sev, code, msg, fix=None):
        f = {"file": rel, "severity": sev, "code": code, "message": msg}
        if fix:
            f["suggested"] = fix
        findings.append(f)

    canon_map, mdurl_map = collections.defaultdict(list), collections.defaultdict(list)
    stats = collections.Counter()

    for rel in files:
        full = os.path.join(root, rel)
        if not os.path.isfile(full):
            continue
        stats["scanned"] += 1
        text = open(full, encoding="utf-8", errors="replace").read()
        raw, body = split_frontmatter(text)

        if raw is None:
            add(rel, "blocking", "FM_MISSING",
                "No frontmatter block. Every page under en/docs/ needs one.")
            stats["no_fm"] += 1
            continue
        try:
            fm = load_frontmatter(raw)
        except Exception as e:
            add(rel, "blocking", "FM_YAML_INVALID", f"Frontmatter is not valid YAML: {str(e)[:150]}")
            stats["yaml_err"] += 1
            continue
        if not isinstance(fm, dict):
            add(rel, "blocking", "FM_NOT_MAPPING", "Frontmatter is not a YAML mapping.")
            continue

        before = len(findings)

        for k in REQUIRED:
            if k == "author" and "authors" in fm:
                continue
            if k not in fm or fm[k] in (None, "", []):
                add(rel, "blocking", "FM_FIELD_MISSING", f"Required field `{k}` is missing or empty.")

        ct = fm.get("content_type")
        if ct is not None:
            cts = str(ct).strip().strip('"').lower()
            if cts not in allowed_ct:
                mapped = CT_ALIASES.get(cts)
                add(rel, "blocking", "CT_INVALID",
                    f"content_type `{ct}` is not in the allowed set "
                    f"({', '.join(sorted(allowed_ct))}).",
                    fix=f"content_type: {mapped}" if mapped else None)

        d = fm.get("description")
        if isinstance(d, str):
            if len(d) > DESC_MAX:
                add(rel, "blocking", "DESC_TOO_LONG",
                    f"description is {len(d)} chars; the rule caps it at {DESC_MAX}. "
                    f"Needs a human/LLM rewrite, not a truncation.")
            elif len(d) < DESC_MIN:
                add(rel, "should-fix", "DESC_TOO_SHORT",
                    f"description is only {len(d)} chars — too thin to be useful for search or agents.")

        t = fm.get("title")
        if isinstance(t, str) and len(t) > TITLE_MAX:
            add(rel, "should-fix", "TITLE_TOO_LONG",
                f"title is {len(t)} chars — likely to truncate on narrow devices.")

        exp_canon, exp_md = site_paths(rel, versions, args.policy)
        cu = str(fm.get("canonical_url", "")).strip()
        mu = str(fm.get("md_url", "")).strip()
        if cu and cu.rstrip("/") + "/" != exp_canon.rstrip("/") + "/":
            add(rel, "blocking", "CANON_MISMATCH",
                f"canonical_url does not match the file path under the `{args.policy}` policy.",
                fix=f"canonical_url: {exp_canon}")
        if mu and mu != exp_md:
            add(rel, "blocking", "MDURL_MISMATCH",
                f"md_url does not match the file path under the `{args.policy}` policy.",
                fix=f"md_url: {exp_md}")
        for k in ("canonical_url", "md_url"):
            v = str(fm.get(k, ""))
            if is_legacy_url(v):
                add(rel, "blocking", "STALE_DOMAIN",
                    f"{k} still points at a pre-migration domain: `{v}`")

        tg = fm.get("tags")
        if tg is not None and not isinstance(tg, list):
            add(rel, "blocking", "TAGS_NOT_LIST", "tags must be a YAML list, so agents can parse it.")
        elif isinstance(tg, list):
            if len(tg) < 2:
                add(rel, "should-fix", "TAGS_TOO_FEW",
                    f"only {len(tg)} tag(s). 2-5 lets agents relate this page to neighbours.")
            bad = [x for x in tg if not isinstance(x, str) or x != x.lower()]
            if bad:
                add(rel, "should-fix", "TAGS_CASE", f"tags should be lowercase: {bad}")

        # House rule: `author` is always the team string. The style guide's own
        # note says "We currently just use 'WSO2 API Platform Documentation
        # Team'"; its named-individual example is illustrative only. Multiple
        # authors still use the plural `authors` list, which is left alone.
        a = fm.get("author")
        if a is not None:
            if not str(a).strip():
                add(rel, "blocking", "AUTHOR_EMPTY",
                    f"author is empty. Use `{AUTHOR}`.", fix=f"author: {AUTHOR}")
            elif str(a).strip().strip('"') != AUTHOR:
                add(rel, "should-fix", "AUTHOR_NONSTANDARD",
                    f"author is `{a}`, expected `{AUTHOR}`.", fix=f"author: {AUTHOR}")

        lu = fm.get("last_updated")
        if lu is not None:
            s = norm_date(lu)
            if s is None:
                add(rel, "blocking", "DATE_FORMAT", f"last_updated `{lu}` is not YYYY-MM-DD.")
            else:
                try:
                    if datetime.date.fromisoformat(s) > datetime.date.today():
                        add(rel, "should-fix", "DATE_FUTURE", f"last_updated `{s}` is in the future.")
                except ValueError:
                    add(rel, "blocking", "DATE_INVALID", f"last_updated `{lu}` is not a real date.")

        if cu:
            canon_map[cu].append(rel)
        if mu:
            mdurl_map[mu].append(rel)
        if len(findings) == before:
            stats["clean"] += 1

    # Cross-file: only one file can be served at a given .md path.
    for mu, owners in sorted(mdurl_map.items()):
        if len(owners) > 1:
            vers = [split_version(o)[0] or "-" for o in owners]
            for o in owners:
                add(o, "blocking", "MDURL_COLLISION",
                    f"md_url `{mu}` is claimed by {len(owners)} files (versions: {', '.join(vers)}). "
                    f"Only one can be served there, so the rest are unreachable as Markdown.")
    for cu, owners in sorted(canon_map.items()):
        if len(owners) > 1:
            for o in owners:
                add(o, "should-fix", "CANON_SHARED",
                    f"canonical_url `{cu}` is shared by {len(owners)} files: {', '.join(owners)}. "
                    f"Search engines will treat only one as the real page.")

    sev = collections.Counter(f["severity"] for f in findings)
    codes = collections.Counter((f["code"], f["severity"]) for f in findings)

    if not args.quiet:
        print("=" * 70)
        print(f"FRONTMATTER AUDIT   (url policy: {args.policy})")
        print("=" * 70)
        print(f"files scanned    : {stats['scanned']}")
        print(f"fully clean      : {stats['clean']}")
        print(f"no frontmatter   : {stats['no_fm']}")
        print(f"unparseable YAML : {stats['yaml_err']}")
        print(f"total findings   : {len(findings)}"
              f"   (blocking={sev['blocking']}, should-fix={sev['should-fix']}, polish={sev['polish']})")
        if codes:
            print()
            print(f"{'COUNT':>6}  {'SEVERITY':<11} CODE")
            print("-" * 70)
            for (c, s), n in codes.most_common():
                print(f"{n:>6}  {s:<11} {c}")
        if versions:
            print()
            print("versioned products detected:")
            for p, vs in sorted(versions.items()):
                print(f"  {p or '<root>'}: {', '.join(vs)}")

    if args.json_out:
        json.dump({"policy": args.policy, "stats": dict(stats), "findings": findings},
                  open(args.json_out, "w"), indent=1)
        if not args.quiet:
            print(f"\nJSON -> {args.json_out}")

    if args.gate and sev["blocking"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
