#!/usr/bin/env python3
"""Repair the *mechanical* parts of frontmatter, and scaffold what needs judgement.

Two things this script deliberately will NOT invent: `title` and `description`.
Those are the fields a reader and a search engine actually see, and a generated
one is worse than none. Everything derivable from the path, the H1 or git
history is filled in automatically; anything requiring judgement is emitted as a
worklist for the LLM to fill.

    # See what would change — always run this first.
    python3 scripts/fm_fix.py en/docs --dry-run

    # Fix mechanical fields in place on files that already have frontmatter.
    python3 scripts/fm_fix.py en/docs --apply

    # Add a frontmatter block to files that have none. title comes from the H1;
    # description/tags/content_type are left as TODO and listed in the worklist.
    python3 scripts/fm_fix.py en/docs --scaffold --apply --worklist work.json

    # Fill in the TODO fields the LLM decided on.
    python3 scripts/fm_fix.py en/docs --fill filled.json --apply

`filled.json` format:
    {"cloud/api-platform-gateway/analytics.md":
        {"description": "...", "tags": ["a","b"], "content_type": "reference",
         "title": "optional override"}}
"""
import os
import re
import sys
import json
import argparse
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fm_lib import (  # noqa: E402
    REQUIRED, AUTHOR, DESC_MAX, effective_allowed_ct, CT_ALIASES,
    discover_versions, site_paths, split_frontmatter, md_files,
    norm_date, git_last_modified, first_h1, render_frontmatter, load_frontmatter,
)

TODO = "TODO"


def sentence_case(s):
    """Lowercase a Title Case heading into sentence case.

    Preserved: the first word, acronyms, anything in `TITLE_PROPER`, and any
    multi-word product name in `PROPER_PHRASES` ("API Manager", "Developer
    Portal"). Those allowlists are shared with `check_style.py` — without them
    this function lowercases the very capitals that checker calls correct, and
    an H1 of "API Manager Configuration Catalog" becomes the wrong
    "API manager configuration catalog".
    """
    from fm_lib import TITLE_PROPER, PROPER_PHRASES

    # Mask phrases first: they cannot be decided one word at a time. Match on word
    # boundaries — a bare `in` test lets "Rate Limit" swallow "Rate Limiting" and
    # preserve a capital that belongs in lower case.
    # A trailing "s" is kept, so "Developer Portals" survives as a plural rather than
    # being restored as the singular the allowlist happens to spell.
    holes = {}
    for n, ph in enumerate(sorted(PROPER_PHRASES, key=len, reverse=True)):
        pat = r"\b" + re.escape(ph) + r"(s?)\b"

        def _hole(m, n=n):
            token = "\x00%d.%d\x00" % (n, len(holes))
            holes[token] = m.group(0)
            return token

        s = re.sub(pat, _hole, s)

    out = []
    for i, w in enumerate(s.split()):
        core = w.strip("()[],.:;\"'")
        if (i == 0 or core in TITLE_PROPER or core.upper() == core
                or not re.match(r"^[A-Z][a-z]+$", core)):
            out.append(w)
        else:
            out.append(w[0].lower() + w[1:])
    joined = " ".join(out)
    for token, ph in holes.items():
        joined = joined.replace(token, ph)
    return joined


def derive_tags(rel):
    """Path segments make honest default tags: they are what the page is filed under."""
    from fm_lib import VER_RE, INDEXY
    parts = [p for p in os.path.dirname(rel).split("/") if p and not VER_RE.match(p)]
    stem = os.path.basename(rel)[:-3]
    if stem in INDEXY:
        stem = None
    tags = [p.lower() for p in parts]
    if stem and stem.lower() not in tags:
        tags.append(stem.lower())
    seen, out = set(), []
    for t in tags[:4]:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out or ["docs"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docs_root", nargs="?", default="en/docs")
    ap.add_argument("--files", nargs="*", default=None)
    ap.add_argument("--policy", default="keep-all",
                    choices=["keep-all", "latest-only", "strip-all"])
    ap.add_argument("--apply", action="store_true", help="Write changes to disk.")
    ap.add_argument("--dry-run", action="store_true", help="Report only (default).")
    ap.add_argument("--scaffold", action="store_true",
                    help="Also add a block to files that have no frontmatter.")
    ap.add_argument("--fill", default=None, help="JSON of LLM-decided field values.")
    ap.add_argument("--worklist", default=None,
                    help="Write the list of files needing LLM judgement here.")
    ap.add_argument("--repo-root", default=".", help="For `git log` dates.")
    args = ap.parse_args()

    if not args.apply:
        args.dry_run = True
    root = args.docs_root.rstrip("/")
    versions = discover_versions(root)
    allowed_ct = effective_allowed_ct()
    filled = json.load(open(args.fill)) if args.fill else {}

    files = args.files or md_files(root)
    files = [f[len(root) + 1:] if f.startswith(root + "/") else f for f in files]

    changes = collections.Counter()
    worklist, edited = [], []

    for rel in sorted(files):
        full = os.path.join(root, rel)
        if not os.path.isfile(full):
            continue
        text = open(full, encoding="utf-8", errors="replace").read()
        raw, body = split_frontmatter(text)
        given = filled.get(rel, {})
        need = []

        if raw is None:
            if not args.scaffold:
                continue
            fm = {}
            h1 = first_h1(body)
            fm["title"] = given.get("title") or (sentence_case(h1) if h1 else TODO)
            if fm["title"] == TODO:
                need.append("title")
            fm["description"] = given.get("description", TODO)
            if fm["description"] == TODO:
                need.append("description")
            fm["tags"] = given.get("tags") or derive_tags(rel)
            fm["author"] = AUTHOR
            fm["last_updated"] = git_last_modified(os.path.join(root, rel), args.repo_root)
            ct = given.get("content_type", TODO)
            fm["content_type"] = ct
            if ct == TODO:
                need.append("content_type")
            fm["canonical_url"], fm["md_url"] = site_paths(rel, versions, args.policy)
            need = [n for n in need if not given.get(n)]
            new_text = render_frontmatter(fm, REQUIRED) + "\n\n" + body.lstrip("\n")
            changes["scaffolded"] += 1
        else:
            try:
                fm = load_frontmatter(raw)
            except Exception:
                print(f"  SKIP (unparseable YAML): {rel}")
                changes["skipped_yaml"] += 1
                continue
            if not isinstance(fm, dict):
                changes["skipped_yaml"] += 1
                continue
            orig = dict(fm)

            # --- mechanical, safe to automate -------------------------------
            canon, md = site_paths(rel, versions, args.policy)
            if str(fm.get("canonical_url", "")).strip() != canon:
                fm["canonical_url"] = canon
                changes["canonical_url"] += 1
            if str(fm.get("md_url", "")).strip() != md:
                fm["md_url"] = md
                changes["md_url"] += 1

            ct = str(fm.get("content_type", "")).strip().strip('"').lower()
            if ct and ct not in allowed_ct:
                if ct in CT_ALIASES:
                    fm["content_type"] = CT_ALIASES[ct]
                    changes["content_type_mapped"] += 1
                else:
                    need.append("content_type")
            elif not ct:
                need.append("content_type")

            # House rule: `author` is always the team string. A page with
            # multiple authors uses the plural `authors` list instead, and that
            # is left untouched.
            if "authors" not in fm and str(fm.get("author", "")).strip().strip('"') != AUTHOR:
                fm["author"] = AUTHOR
                changes["author"] += 1

            nd = norm_date(fm.get("last_updated"))
            if nd is None:
                fm["last_updated"] = git_last_modified(os.path.join(root, rel), args.repo_root)
                changes["last_updated"] += 1
            else:
                fm["last_updated"] = nd

            tg = fm.get("tags")
            if isinstance(tg, list):
                low = [str(t).lower() for t in tg]
                if low != tg:
                    fm["tags"] = low
                    changes["tags_lowercased"] += 1
                if len(low) < 2:
                    need.append("tags")
            elif tg in (None, "", []):
                fm["tags"] = derive_tags(rel)
                changes["tags_derived"] += 1
            else:
                fm["tags"] = [str(tg).lower()]
                changes["tags_listified"] += 1

            # --- needs judgement: never auto-written ------------------------
            if given.get("description"):
                fm["description"] = given["description"]
                changes["description_filled"] += 1
            d = fm.get("description")
            if not isinstance(d, str) or not d.strip():
                need.append("description")
            elif len(d) > DESC_MAX:
                need.append("description")   # rewrite, never truncate

            if given.get("title"):
                fm["title"] = given["title"]
                changes["title_filled"] += 1
            if given.get("content_type"):
                fm["content_type"] = given["content_type"]
                changes["content_type_filled"] += 1
            if given.get("tags"):
                fm["tags"] = [str(t).lower() for t in given["tags"]]
                changes["tags_filled"] += 1

            if not str(fm.get("title", "")).strip():
                need.append("title")

            # Anything the --fill payload supplied is no longer outstanding.
            need = [n for n in need if not given.get(n)]

            del orig
            # Compare the *rendered* result, not the parsed dict: YAML gives dates
            # back as date objects, so a dict compare reports a change on every
            # file even when the serialised output is byte-identical.
            new_text = render_frontmatter(fm, REQUIRED) + "\n\n" + body.lstrip("\n")
            if new_text == text:
                if need:
                    worklist.append({"file": rel, "needs": sorted(set(need)),
                                     "h1": first_h1(body),
                                     "current": {k: fm.get(k) for k in ("title", "description", "content_type", "tags")}})
                continue

        if need:
            worklist.append({"file": rel, "needs": sorted(set(need)),
                             "h1": first_h1(body),
                             "current": {k: fm.get(k) for k in ("title", "description", "content_type", "tags")}})
        edited.append(rel)
        if args.apply:
            open(full, "w", encoding="utf-8").write(new_text)

    print("=" * 70)
    print(f"FRONTMATTER FIX   ({'APPLIED' if args.apply else 'DRY RUN'}, policy: {args.policy})")
    print("=" * 70)
    print(f"files touched : {len(edited)}")
    if changes:
        print()
        for k, v in changes.most_common():
            print(f"  {v:5d}  {k}")
    print(f"\nfiles still needing LLM judgement: {len(worklist)}")
    if worklist:
        c = collections.Counter(n for w in worklist for n in w["needs"])
        for k, v in c.most_common():
            print(f"  {v:5d}  {k}")
    if args.worklist:
        json.dump(worklist, open(args.worklist, "w"), indent=1)
        print(f"\nworklist -> {args.worklist}")
    if not args.apply:
        print("\n(nothing written — re-run with --apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
