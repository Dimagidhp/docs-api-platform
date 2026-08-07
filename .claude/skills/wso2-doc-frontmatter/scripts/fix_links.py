#!/usr/bin/env python3
"""Apply the link fixes proposed in a `report_links.py` plan, one tier at a time.

    # look, change nothing (the default)
    python3 scripts/fix_links.py en/docs --plan BROKEN-LINKS-4.6.0.json --tier malformed
    # apply that tier
    python3 scripts/fix_links.py en/docs --plan BROKEN-LINKS-4.6.0.json --tier malformed --apply

The split from `report_links.py` is deliberate. The reporter reads and proposes;
this script is the only thing that writes. So a plan can be reviewed, committed,
and handed to someone else, and applying it later is a separate, auditable act.

Tiers are applied ONE AT A TIME on purpose. Each tier has a different failure
mode, so each deserves its own look and its own commit — a bad `renamed`
proposal is a link to a real page about the wrong thing, which no build catches.

Only tiers whose entries carry a `suggested` value can be applied at all:

    malformed   link syntax. Exact.
    dir_style   written in URL shape; add `.md` so mkdocs resolves it. Exact.
    depth       wrong number of `../`. Exact.
    renamed     target moved. Proposed, with a confidence — high only by default.
    templated_fixable   `{{base_path}}` where the resource exists. Exact.

`templated`, `stale`, `anchor` and `gone` are refused. They need information that
is not in the repo, and a guess there produces a confident link to the wrong page.

Every rewrite is verified against the disk BEFORE it is written, and the exact
link text must still be present in the file — so a plan that has gone stale
skips rather than corrupts.
"""
import os
import re
import sys
import json
import argparse
import collections

APPLICABLE = {
    "malformed": "link syntax, exact",
    "dir_style": "written as a URL; adding `.md` lets mkdocs resolve it",
    "depth": "wrong relative depth, exact",
    "templated_fixable": "build-time variable where the resource exists, exact",
    "renamed": "target moved, proposed with a confidence",
}
REFUSED = {
    "templated": "the resource does not exist at that path — may be served by a redirect",
    "stale": "points at a pre-migration domain — needs the new equivalent page",
    "anchor": "the heading was reworded — needs someone to pick the new one",
    "gone": "no target anywhere — was it dropped, missed, or merged?",
}


def slug(h):
    """python-markdown's toc slugify: strip non-word chars, then collapse runs of
    whitespace AND hyphens into one hyphen. Kept identical to check_links.py."""
    h = re.sub(r"`|\*", "", h)
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = re.sub(r"[^\w\s-]", "", h).strip().lower()
    return re.sub(r"[-\s]+", "-", h)


def anchors_of(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    txt = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
    txt = re.sub(r"```.*?```", "", txt, flags=re.S)
    out = set()
    for m in re.finditer(r"^#{1,6}\s+(.+?)\s*$", txt, re.M):
        h = m.group(1)
        exp = re.search(r"\{#([\w-]+)\}", h)
        if exp:
            out.add(exp.group(1))
            h = h[:exp.start()]
        out.add(slug(h))
    for m in re.finditer(r'<a[^>]+(?:name|id)="([^"]+)"', txt):
        out.add(m.group(1))
    for m in re.finditer(r"\{#([\w-]+)\}", txt):
        out.add(m.group(1))
    return out


def page_id(p):
    """Collapse the ways one page can be spelled into a single identity, so
    `foo/bar`, `foo/bar.md` and `foo/bar/index.md` compare equal."""
    p = (p or "").rstrip("/")
    for suffix in ("/index.md", "/README.md"):
        if p.endswith(suffix):
            return p[: -len(suffix)]
    return p[:-3] if p.endswith(".md") else p


def resolve(root, src_rel, target):
    """Where does `target`, written in the page `src_rel`, land on disk?

    Returns a repo-relative path that exists, or None. Directory URLs mean a
    bare path may be a file, the same file with `.md`, or a directory's index.
    """
    target = target.split("#")[0].split("?")[0]
    if not target:
        return src_rel
    base = os.path.dirname(src_rel)
    cand = os.path.normpath(os.path.join(base, target)).replace("\\", "/")
    for c in (cand, cand + ".md", cand + "/index.md", cand + "/README.md"):
        if os.path.isfile(os.path.join(root, c)):
            return c
    return None


def verify(root, entry):
    """Can this entry's `suggested` value be trusted? Returns (ok, reason)."""
    src = entry["file"]
    suggested = entry.get("suggested")
    if not suggested:
        return False, "no suggested value in the plan"
    if not os.path.isfile(os.path.join(root, src)):
        return False, "source page no longer exists"

    # An absolute URL or mail link has no on-disk target to check. That is not a
    # reason to skip: these appear in `malformed`, where the fix is purely
    # syntactic (unwrapping backticks, removing a stray quote) and the address
    # itself is untouched.
    if re.match(r"^(?:[a-z][a-z0-9+.-]*:)?//|^mailto:", suggested, re.I):
        return True, "external address, syntax-only fix"

    frag = suggested.partition("#")[2]
    if suggested.startswith("#"):
        landed = src                      # same-page anchor
    else:
        landed = resolve(root, src, suggested)
        if landed is None:
            return False, f"suggested target does not resolve: {suggested}"

    # Where the plan already recorded the on-disk target, the two must agree — on
    # the *page*, not the spelling. The reporter records some targets in their
    # directory-URL form (`foo/bar`) and others as the file (`foo/bar.md`), and
    # those name the same page.
    recorded = entry.get("resolves_to") or entry.get("found_at")
    if recorded and page_id(landed) != page_id(recorded):
        return False, f"resolves to {landed}, but the plan recorded {recorded}"

    if frag and landed.endswith(".md"):
        if frag not in anchors_of(os.path.join(root, landed)):
            return False, f"anchor #{frag} not found in {landed}"
    return True, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docs_root", nargs="?", default="en/docs")
    ap.add_argument("--plan", required=True, help="The JSON written by report_links.py.")
    ap.add_argument("--tier", required=True,
                    help="One tier name. Run --list to see what a plan holds.")
    ap.add_argument("--apply", action="store_true", help="Write changes. Default is a dry run.")
    ap.add_argument("--sample", type=int, default=5,
                    help="How many before/after examples to print (dry run only).")
    ap.add_argument("--min-confidence", default="high", choices=["high", "medium", "low"],
                    help="For `renamed`: the lowest confidence to act on. Default high.")
    ap.add_argument("--files", nargs="*", default=None,
                    help="Limit to these pages (paths as they appear in the plan, or "
                         "prefixed with the docs root). Use this to try a tier on one "
                         "page before running it across the scope.")
    ap.add_argument("--journal", default=None,
                    help="Write what changed to this JSON, for review or reverting.")
    args = ap.parse_args()

    root = args.docs_root.rstrip("/")
    plan = json.load(open(args.plan, encoding="utf-8"))
    tiers = plan.get("tiers", {})

    if args.tier not in tiers:
        print(f"No tier {args.tier!r} in {args.plan}. This plan holds:")
        for t, items in tiers.items():
            print(f"    {t:<20} {len(items):>5}")
        return 2

    if args.tier in REFUSED:
        print(f"Refusing to apply `{args.tier}`: {REFUSED[args.tier]}.")
        print("These need a person. Work them from the report by hand.")
        return 2
    if args.tier not in APPLICABLE:
        print(f"`{args.tier}` has no proposed replacements, so there is nothing to apply.")
        return 2

    entries = tiers[args.tier]

    if args.files:
        # Accept either form: `en/docs/a/b.md` or the plan's `a/b.md`.
        wanted = {f[len(root):].lstrip("/") if f.startswith(root) else f for f in args.files}
        before = len(entries)
        entries = [e for e in entries if e.get("file") in wanted]
        unmatched = wanted - {e.get("file") for e in entries}
        print(f"--files: {len(entries)} of {before} entries in this tier match "
              f"{len(wanted)} path(s).")
        if unmatched:
            print("  no entries in this tier for: " + ", ".join(sorted(unmatched)))
        if not entries:
            return 0

    rank = {"high": 3, "medium": 2, "low": 1}
    if args.tier == "renamed":
        floor = rank[args.min_confidence]
        held = [e for e in entries if rank.get(e.get("confidence", "low"), 1) < floor]
        entries = [e for e in entries if rank.get(e.get("confidence", "low"), 1) >= floor]
    else:
        held = []

    # Verify everything first. Nothing is written until the whole tier is checked.
    ready, skipped = [], []
    for e in entries:
        ok, why = verify(root, e)
        (ready if ok else skipped).append(e if ok else (e, why))

    print("=" * 70)
    print(f"LINK FIX   tier: {args.tier}   ({APPLICABLE[args.tier]})")
    print("=" * 70)
    print(f"scope in plan     : {plan.get('scope', '?')}")
    print(f"entries in tier   : {len(entries) if args.files else len(tiers[args.tier])}")
    if held:
        print(f"below confidence  : {len(held)}   (raise with --min-confidence)")
    print(f"verified fixable  : {len(ready)}")
    print(f"skipped           : {len(skipped)}")

    if skipped:
        print("\nSkipped, with reasons:")
        for e, why in skipped[:10]:
            print(f"  {e['file']}\n      {e.get('link')}  ->  {why}")
        if len(skipped) > 10:
            print(f"  ... and {len(skipped) - 10} more")

    if not args.apply:
        n = min(args.sample, len(ready))
        if n:
            print(f"\nSample of {n} of {len(ready)} fixes (nothing written):\n")
            for e in ready[:n]:
                print(f"  {e['file']}")
                print(f"    -  {e['link']}")
                print(f"    +  {e['suggested']}")
                if e.get("confidence"):
                    print(f"       confidence: {e['confidence']}")
                print()
        print(f"To apply these {len(ready)}, re-run with --apply.")
        return 0

    # Group by file so each file is read and written once.
    by_file = collections.defaultdict(list)
    for e in ready:
        by_file[e["file"]].append(e)

    changed_files = 0
    rewrites = 0
    missing, already = [], 0
    journal = []
    for rel, es in sorted(by_file.items()):
        path = os.path.join(root, rel)
        txt = open(path, encoding="utf-8", errors="replace").read()
        orig = txt
        done = set()
        for e in es:
            if e["link"] in done:
                # The plan lists one entry per occurrence, and the first rewrite
                # replaced every copy of that exact string. Not a problem.
                already += 1
                continue
            if e["link"] not in txt:
                missing.append((rel, e["link"]))
                continue
            n = txt.count(e["link"])
            txt = txt.replace(e["link"], e["suggested"])
            done.add(e["link"])
            rewrites += n
            journal.append({"file": rel, "from": e["link"],
                            "to": e["suggested"], "occurrences": n})
        if txt != orig:
            open(path, "w", encoding="utf-8").write(txt)
            changed_files += 1

    print(f"\nAPPLIED   files changed: {changed_files}   link occurrences rewritten: {rewrites}")
    if already:
        print(f"          {already} further entries were duplicates of a link already "
              f"rewritten in the same file")
    if missing:
        print(f"\nNot found in the file, so left alone ({len(missing)}) — the plan is "
              f"older than the page:")
        for rel, link in missing[:10]:
            print(f"  {rel}: {link}")

    if args.journal:
        json.dump(journal, open(args.journal, "w"), indent=1, ensure_ascii=False)
        print(f"\njournal -> {args.journal}")

    print("\nReview with `git diff --stat`, then regenerate the plan before the next "
          "tier — fixing one tier changes what the others resolve to.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
