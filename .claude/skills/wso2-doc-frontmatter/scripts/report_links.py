#!/usr/bin/env python3
"""Turn raw broken-link findings into a fix plan a person or an agent can act on.

    python3 scripts/report_links.py en/docs --out BROKEN-LINKS.md
    python3 scripts/report_links.py en/docs --scope <product>/<version> --out BROKEN-LINKS-<version>.md

`check_links.py` answers "what is broken". This answers "what do I change", which
is a different question and the one that actually gets the work done. Every
finding is classified by *cause*, because the causes have completely different
fixes:

  * wrong relative depth  -> exact mechanical rewrite, no judgement at all
  * renamed / moved page  -> a target exists elsewhere; propose it, rank confidence
  * genuinely gone        -> needs a human decision, cannot be automated
  * pre-migration domain  -> map to the new site or drop the link
  * missing anchor        -> heading was reworded

The report ends with a prompt written for an AI coding agent, so the mechanical
tiers can be handed straight off.
"""
import os
import re
import sys
import json
import argparse
import collections
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fm_lib import split_version, is_legacy_url  # noqa: E402

LINK = re.compile(r'(!?)\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
# Quote character captured and back-referenced: HTML allows single or double
# quotes and these pages use both, so a double-quote-only pattern silently skips
# whatever is single-quoted.
HTML_SRC = re.compile(r"""<(img|a|source|iframe)[^>]+(?:src|href)=(["'])(.*?)\2""")


def url_base(rel):
    """Directory the RENDERED page sits in, under `use_directory_urls: true`.

    `a/b/page.md` is served at `/a/b/page/`, so it is one level DEEPER than the
    source file, while `a/b/index.md` is served at `/a/b/` — the same level.

    This matters because mkdocs rewrites relative targets in Markdown syntax
    (resolving them against the source file) but passes raw HTML through
    untouched, so an `<img src>` is resolved by the browser against the rendered
    URL instead. The same string is therefore correct in one syntax and broken in
    the other, and the two must not be checked the same way.
    """
    d = os.path.dirname(rel)
    stem = os.path.basename(rel)[:-3] if rel.endswith(".md") else os.path.basename(rel)
    return d if stem in ("index", "README") else (f"{d}/{stem}" if d else stem)


def version_root(rel):
    """`<product>/<version>/a/b.md` -> `<product>/<version>`, else ''."""
    ver, _ = split_version(rel)
    if not ver:
        return ""
    parts = rel.split("/")
    return "/".join(parts[: parts.index(ver) + 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docs_root", nargs="?", default="en/docs")
    ap.add_argument("--scope", default=None,
                    help="Only report files under this path prefix, e.g. <product>/<version>")
    ap.add_argument("--out", default="BROKEN-LINKS.md")
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--max-rows", type=int, default=40,
                    help="Rows per table in the Markdown before truncating (JSON is always complete).")
    args = ap.parse_args()

    root = args.docs_root.rstrip("/")

    all_files, md_list = set(), []
    for r, _, fs in os.walk(root):
        for f in fs:
            rel = os.path.relpath(os.path.join(r, f), root).replace("\\", "/")
            all_files.add(rel)
            if f.endswith(".md"):
                md_list.append(rel)
    md_list.sort()

    by_basename = collections.defaultdict(list)
    for f in all_files:
        by_basename[os.path.basename(f)].append(f)

    def resolves(cand):
        return any(c in all_files
                   for c in (cand, cand + ".md", cand + "/index.md", cand + "/README.md"))

    def slug(h):
        h = re.sub(r"`|\*", "", h)
        h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)
        h = re.sub(r"<[^>]+>", "", h)
        h = re.sub(r"[^\w\s-]", "", h).strip().lower()
        return re.sub(r"[-\s]+", "-", h)

    anchors = {}
    for p in md_list:
        txt = open(os.path.join(root, p), encoding="utf-8", errors="replace").read()
        txt = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
        txt = re.sub(r"```.*?```", "", txt, flags=re.S)
        a = set()
        for m in re.finditer(r"^#{1,6}\s+(.+?)\s*$", txt, re.M):
            h = m.group(1)
            exp = re.search(r"\{#([\w-]+)\}", h)
            if exp:
                a.add(exp.group(1))
                h = h[: exp.start()]
            a.add(slug(h))
        for m in re.finditer(r"""<a[^>]+(?:name|id)=(["'])(.*?)\1""", txt):
            a.add(m.group(2))
        anchors[p] = a

    tiers = {k: [] for k in ("templated_fixable", "templated", "malformed", "dir_style",
                             "depth", "renamed", "gone", "stale", "anchor")}

    targets = [p for p in md_list if not args.scope or p.startswith(args.scope)]
    for p in targets:
        txt = open(os.path.join(root, p), encoding="utf-8", errors="replace").read()
        body = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
        body = re.sub(r"```.*?```", "", body, flags=re.S)
        d = os.path.dirname(p)
        stem = os.path.basename(p)[:-3]
        vroot = version_root(p)

        # The third element records whether the target was written in raw HTML.
        # mkdocs rewrites Markdown targets and leaves HTML alone, so the two need
        # different bases — see url_base() above.
        raw = [(m.group(1) == "!", m.group(3), False) for m in LINK.finditer(body)]
        raw += [(m.group(1).lower() != "a", m.group(3), True) for m in HTML_SRC.finditer(body)]

        for is_img, t, is_html in raw:
            if t.startswith(("mailto:", "tel:", "//", "#!")):
                continue

            # Malformed syntax, caught before resolution so it isn't mis-filed as a
            # missing target. Both forms below occur in migrated pages and both
            # render as literal broken text, so the fix is exact.
            # `{{base_path}}` stands for the root of the version's site, so the
            # remainder is a path relative to that version's directory. Where the
            # resource actually exists there, the link can be rewritten as an
            # ordinary relative path and the variable dropped — that is a real fix,
            # not a guess. Where it does not exist, the target may be served by a
            # redirect, so leave it alone until the redirect strategy is settled.
            if re.search(r"\{\{.*?\}\}", t):
                m_bp = re.match(r"^\{\{\s*base_path\s*\}\}/?(.*)$", t)
                fixed = None
                if m_bp:
                    rest, _, bfrag = m_bp.group(1).partition("#")
                    rest = urllib.parse.unquote(rest).strip("/")
                    base_dir = vroot if vroot else ""
                    cand = f"{base_dir}/{rest}" if base_dir else rest
                    cand = os.path.normpath(cand).replace("\\", "/")
                    target = next((c for c in (cand, cand + ".md", cand + "/index.md",
                                               cand + "/README.md") if c in all_files), None)
                    if target:
                        fixed = os.path.relpath(target, d).replace("\\", "/")
                        if bfrag:
                            fixed += "#" + bfrag
                if fixed:
                    tiers["templated_fixable"].append({
                        "file": p, "link": t, "suggested": fixed,
                        "why": "resource exists, so the variable can be replaced with a relative path"})
                else:
                    tiers["templated"].append({"file": p, "link": t,
                                               "variable": ", ".join(sorted(set(
                                                   re.findall(r"\{\{.*?\}\}", t))))})
                continue

            raw_t = t
            cleaned = t.strip("`'\"")                       # [text](`https://…`)
            m_hash = re.match(r"^(#{2,})([\w-]+)$", cleaned)  # [text](###anchor)
            if m_hash:
                tiers["malformed"].append({
                    "file": p, "link": raw_t, "suggested": "#" + m_hash.group(2),
                    "why": f"{len(m_hash.group(1))} `#` characters; an anchor takes exactly one"})
                continue
            if cleaned != raw_t:
                tiers["malformed"].append({
                    "file": p, "link": raw_t, "suggested": cleaned,
                    "why": "target is wrapped in backticks or quotes, so it is not a valid URL"})
                continue
            if is_legacy_url(t):
                tiers["stale"].append({"file": p, "link": t})
                continue
            if re.match(r"^https?://", t):
                continue

            path, _, frag = t.partition("#")
            path = urllib.parse.unquote(path)
            frag = urllib.parse.unquote(frag)

            if not path:
                if frag and frag not in anchors.get(p, set()):
                    tiers["anchor"].append({"file": p, "link": t, "target_file": p, "anchor": frag})
                continue

            # WHICH BASE APPLIES — verified against a real mkdocs build.
            #
            # mkdocs rewrites a Markdown target only when the literal path names a
            # file that exists; then it is resolved against the SOURCE directory.
            # Everything else — raw HTML, directory-style links (`../foo/bar/`),
            # extensionless links (`../foo/bar`) — is passed through verbatim and
            # resolved by the browser against the RENDERED URL, one level deeper.
            if is_html:
                own_base, alt_base = url_base(p), d
                rewritten = False
            else:
                literal = os.path.normpath(os.path.join(d, path)).replace("\\", "/")
                rewritten = literal in all_files
                own_base, alt_base = (d, url_base(p)) if rewritten else (url_base(p), d)

            own_rel = os.path.normpath(os.path.join(own_base, path)).replace("\\", "/")
            if resolves(own_rel):
                if frag:
                    tf = next((c for c in (own_rel, own_rel + ".md", own_rel + "/index.md",
                                           own_rel + "/README.md") if c in all_files), None)
                    if tf and tf.endswith(".md") and frag not in anchors.get(tf, set()):
                        tiers["anchor"].append({"file": p, "link": t, "target_file": tf, "anchor": frag})
                continue

            # A Markdown link written in URL shape, whose `.md` file sits exactly
            # where the link already points. Adding the extension is the real fix,
            # not adding a `../`: mkdocs then owns the depth calculation and the link
            # keeps working when the page moves. Checked BEFORE the depth tier so the
            # brittle fix never wins.
            if not is_html and not rewritten:
                src_guess = os.path.normpath(os.path.join(d, path)).replace("\\", "/")
                md_target = next((c for c in (src_guess + ".md", src_guess + "/index.md",
                                              src_guess + "/README.md") if c in all_files), None)
                if md_target:
                    fixed = os.path.relpath(md_target, d).replace("\\", "/")
                    tiers["dir_style"].append({
                        "file": p, "link": t, "resolves_to": md_target,
                        "suggested": fixed + (("#" + frag) if frag else ""),
                        "why": "written as a URL, so mkdocs passes it through unresolved"})
                    continue

            # Resolves against the OTHER base — so the depth is wrong by exactly the
            # one level between a source file and its rendered directory.
            alt_rel = os.path.normpath(os.path.join(alt_base, path)).replace("\\", "/")
            if resolves(alt_rel):
                fixed = os.path.relpath(alt_rel, own_base).replace("\\", "/")
                if not is_html and alt_rel + ".md" in all_files:
                    fixed += ".md"
                tiers["depth"].append({"file": p, "link": t, "resolves_to": alt_rel,
                                       "is_html": is_html,
                                       "suggested": fixed + (("#" + frag) if frag else "")})
                continue

            # Nothing resolves. Look for a file of the same name elsewhere — the
            # restructure renamed directories without updating links, so the page
            # usually still exists somewhere under the same version root.
            base = os.path.basename(path.rstrip("/")) or stem
            cands = by_basename.get(base + ".md", []) + by_basename.get(base, [])
            if vroot:
                # STRICT. Previously this fell back to the unscoped candidate list
                # when nothing matched inside the version, which proposed targets in
                # *other* versions — sending a reader from a current page to an old
                # release. A missing page inside this version is `gone`, not a reason
                # to look in another version.
                cands = [c for c in cands if c.startswith(vroot + "/")]
            cands = [c for c in cands if c != p]

            if len(cands) == 1:
                sug = os.path.relpath(cands[0], d).replace("\\", "/")
                tiers["renamed"].append({"file": p, "link": t, "found_at": cands[0],
                                         "suggested": sug + (("#" + frag) if frag else ""),
                                         "confidence": "high"})
            elif 2 <= len(cands) <= 5:
                ranked = sorted(cands, key=lambda c: -len(os.path.commonprefix([c, p])))
                sug = os.path.relpath(ranked[0], d).replace("\\", "/")
                tiers["renamed"].append({"file": p, "link": t, "found_at": ranked[0],
                                         "suggested": sug + (("#" + frag) if frag else ""),
                                         "confidence": f"low ({len(cands)} candidates)",
                                         "alternatives": ranked[:5]})
            elif cands:
                # A generic basename like `overview.md` matches dozens of pages.
                # Guessing one would be worse than saying nothing: a guess reads as
                # an answer, and nobody re-checks an answer. List the field instead.
                ranked = sorted(cands, key=lambda c: -len(os.path.commonprefix([c, p])))
                tiers["gone"].append({"file": p, "link": t,
                                      "kind": "image" if is_img else "link",
                                      "note": f"{len(cands)} files share this name — too ambiguous to propose one",
                                      "candidates": ranked[:6]})
            else:
                tiers["gone"].append({"file": p, "link": t,
                                      "kind": "image" if is_img else "link",
                                      "note": "no file of this name exists anywhere under the docs root"})

    # ---------------- write the report ----------------
    n = {k: len(v) for k, v in tiers.items()}
    total = sum(n.values())
    scope_label = args.scope or f"all of {root}"
    auto = (n["templated_fixable"] + n["malformed"] + n["dir_style"] + n["depth"]
            + len([x for x in tiers["renamed"] if x["confidence"] == "high"]))

    L = []
    w = L.append
    w(f"# Broken links and images — `{scope_label}`")
    w("")
    w(f"**{total} findings** across {len(targets)} pages. "
      f"**{auto}** have an exact or high-confidence mechanical fix; "
      f"**{n['gone']}** need a human decision.")
    w("")
    # Groups are named, not numbered. The name is the value `fix_links.py --tier`
    # takes, so a row in this table is directly runnable. Numbering them invited
    # the obvious question of why two groups shared a number and one had none.
    w("### Fixable by script")
    w("")
    w("Run in this order. Each is a separate `fix_links.py --tier` run, and every "
      "rewrite is verified against the files on disk before it is written.")
    w("")
    w("| Order | Group | Cause | Count | Fix |")
    w("|---|---|---|---|---|")
    w(f"| 1 | `malformed` | Malformed link syntax | {n['malformed']} | Exact — no judgement |")
    w(f"| 2 | `dir_style` | Written as a URL, so mkdocs never resolves it | {n['dir_style']} | Add `.md` — mkdocs then owns the depth |")
    w(f"| 3 | `depth` | Wrong relative depth | {n['depth']} | Exact — no judgement |")
    w(f"| 4 | `renamed` | Renamed or moved target | {n['renamed']} | Proposed; `high` confidence applied by default |")
    w(f"| 5 | `templated_fixable` | `{{{{base_path}}}}` where the resource exists | {n['templated_fixable']} | Exact rewrite to a relative path |")
    w("")
    w("### Needs a person")
    w("")
    w("`fix_links.py` refuses these. The information needed is not in the repository, "
      "and a guess produces a confident link to the wrong page — worse than a visibly "
      "broken one, because nobody re-checks it.")
    w("")
    w("| Group | Cause | Count | Why it cannot be automated |")
    w("|---|---|---|---|")
    w(f"| `templated` | `{{{{base_path}}}}` where the resource does not exist | {n['templated']} | May be served by a redirect |")
    w(f"| `stale` | Pre-migration domain | {n['stale']} | Needs the equivalent page on the new site |")
    w(f"| `anchor` | Missing anchor | {n['anchor']} | The heading was reworded — which one now? |")
    w(f"| `gone` | No target anywhere | {n['gone']} | Was it dropped, missed, or merged? |")
    w("")

    def table(rows, cols, keys, limit):
        w("| " + " | ".join(cols) + " |")
        w("|" + "|".join(["---"] * len(cols)) + "|")
        for r in rows[:limit]:
            w("| " + " | ".join(f"`{r.get(k,'')}`" if k != "confidence" else str(r.get(k, ""))
                                for k in keys) + " |")
        if len(rows) > limit:
            w("")
            w(f"_…and {len(rows) - limit} more. Full list in the JSON sidecar._")
        w("")

    if n["templated_fixable"]:
        w("## `templated_fixable` — `{{base_path}}` where the resource exists")
        w("")
        w("`{{base_path}}` stands for the root of the version's site, so the rest of the "
          "target is a path within that version's directory. For these, the resource is "
          "there: the variable can be dropped and the link written as an ordinary relative "
          "path. The replacement below is exact.")
        w("")
        table(tiers["templated_fixable"], ["Page", "Currently", "Change to"],
              ["file", "link", "suggested"], args.max_rows)

    if n["templated"]:
        w("## Excluded — `{{base_path}}` where the resource does not exist")
        w("")
        w("Same variable, but the target is not present at that path in this version. It may "
          "be served by a redirect, or the page may not have been migrated. **Leave these "
          "alone** until the redirect strategy is settled — a rewrite here would be a guess.")
        w("")
        table(tiers["templated"], ["Page", "Link", "Variable"],
              ["file", "link", "variable"], args.max_rows)

    if n["malformed"]:
        w("## `malformed` — Malformed link syntax")
        w("")
        w("The link target is not a valid path or URL, so it renders as literal broken text "
          "regardless of whether the destination exists. Carried over from the old wiki. "
          "The replacement is exact.")
        w("")
        table(tiers["malformed"], ["Page", "Currently", "Change to", "Why"],
              ["file", "link", "suggested", "why"], args.max_rows)

    if n["dir_style"]:
        w("## `dir_style` — Written as a URL, so mkdocs never resolves it")
        w("")
        w("These point at the right page already. Because the target is written in URL "
          "shape rather than naming the `.md` file, mkdocs passes it through untouched and "
          "the browser resolves it against the rendered page URL — one directory deeper "
          "than the source file, so it lands one level short. Adding the extension hands "
          "the depth calculation back to mkdocs, permanently.")
        w("")
        table(tiers["dir_style"], ["Page", "Currently", "Change to"],
              ["file", "link", "suggested"], args.max_rows)
        w("")

    if n["depth"]:
        w("## `depth` — Wrong relative depth")
        w("")
        w("The target exists; the path has one `../` too many. These render correctly in a "
          "browser (the published URL sits one directory deeper than the source file), so they "
          "look fine on the site — but `mkdocs build` warns about every one, and anyone reading "
          "the raw Markdown through `md_url` gets a broken path. The replacement below is exact.")
        w("")
        table(tiers["depth"], ["Page", "Currently", "Change to"],
              ["file", "link", "suggested"], args.max_rows)

    if n["renamed"]:
        hi = [x for x in tiers["renamed"] if x["confidence"] == "high"]
        lo = [x for x in tiers["renamed"] if x["confidence"] != "high"]
        w("## `renamed` — Renamed or moved target")
        w("")
        w("The target does not exist at the path written, but a file of the same name exists "
          "elsewhere under the same version. This is the restructure: directories were renamed "
          "and the inbound links were never updated.")
        w("")
        if hi:
            w(f"### Exactly one candidate — high confidence ({len(hi)})")
            w("")
            table(hi, ["Page", "Currently", "Change to"], ["file", "link", "suggested"], args.max_rows)
        if lo:
            w(f"### Several candidates — verify before applying ({len(lo)})")
            w("")
            table(lo, ["Page", "Currently", "Best guess", "Confidence"],
                  ["file", "link", "suggested", "confidence"], args.max_rows)

    if n["stale"]:
        w("## `stale` — Links to the pre-migration site")
        w("")
        w("These point at a location the documentation has migrated away from. For each "
          "one: find the equivalent page on the new site and link to it relatively, or if the "
          "content wasn't migrated, remove the link and say so in the prose. Never leave a "
          "reader on the old site.")
        w("")
        table(tiers["stale"], ["Page", "Link"], ["file", "link"], args.max_rows)

    if n["anchor"]:
        w("## `anchor` — Missing anchor")
        w("")
        w("The page resolves but the `#fragment` matches no heading, so the reader lands at the "
          "top instead of the section. Usually the heading was reworded. Open the target, find "
          "the heading that was meant, and use its current slug.")
        w("")
        table(tiers["anchor"], ["Page", "Link", "Target file", "Missing anchor"],
              ["file", "link", "target_file", "anchor"], args.max_rows)

    if n["gone"]:
        w("## `gone` — No target anywhere")
        w("")
        w("No file of this name exists anywhere under the docs root, so there is nothing to "
          "point at. Each needs a decision: was the page meant to be migrated and missed, was it "
          "deliberately dropped (then the link and its sentence should go), or was it merged into "
          "another page (then link there)? **Do not guess these.**")
        w("")
        table(tiers["gone"], ["Page", "Broken target", "Note"],
              ["file", "link", "note"], args.max_rows)

    # ---- the agent prompt ----
    w("---")
    w("")
    w("## Prompt for an AI coding agent")
    w("")
    w("Paste the block below to an agent working in the repo root. It is deliberately scoped to "
      "the four groups with a defensible mechanical answer. `templated`, `stale`, `anchor` and "
      "`gone` need judgement and are left out on purpose.")
    w("")
    w("Alternatively, run `fix_links.py --tier <group>` yourself — same scope, one group at a "
      "time, and every rewrite verified against the files on disk before it is written.")
    w("")
    w("````text")
    w(f"You are fixing broken links in the WSO2 API Platform docs, scope: {scope_label}.")
    w("")
    w(f"Read the fix plan in `{args.out}`" +
      (f" and the machine-readable list in `{args.json_out}`." if args.json_out else "."))
    w("")
    w("Apply ONLY these groups:")
    w("  - `templated_fixable`: apply every row as given.")
    w("  - `malformed`: apply every row exactly as given.")
    w("  - `dir_style`: apply every row exactly as given (adds `.md`).")
    w("  - `depth`: apply every row exactly as given.")
    w("  - `renamed`, the high-confidence subsection only: apply every row as given.")
    w("")
    w("Rules:")
    w("  1. Replace only the link target inside the parentheses. Never change the link TEXT,")
    w("     the surrounding sentence, or anything else on the line.")
    w("  2. A target may appear more than once in a file — replace every occurrence of that")
    w("     exact target in that file.")
    w("  3. Preserve any `#fragment` already on the link unless the plan says otherwise.")
    w("  4. Do NOT touch `templated`, `stale`, `anchor` or `gone`. Do not invent a")
    w("     target that is not in the plan.")
    w("  5. Do not reformat, reflow, or reorder anything. Minimal diffs only.")
    w("")
    w("Verify when done, from the repo root:")
    w(f"  python3 .claude/skills/wso2-doc-frontmatter/scripts/check_links.py {root}" +
      (f" --json /tmp/after.json" if True else ""))
    w("")
    w("The blocking count must go DOWN and no new codes may appear. If any count rises, stop")
    w("and report what you changed rather than continuing.")
    w("")
    w("Then report: rows applied per group, files touched, and the before/after blocking counts.")
    w("````")
    w("")
    w("### Why `templated`, `stale`, `anchor` and `gone` are excluded")
    w("")
    w("Each needs information that isn't in the repo: which new page replaces an old-site link, "
      "which reworded heading was meant, whether a missing page was dropped on purpose. An agent "
      "asked to fix those will produce plausible links to the wrong places, which is worse than "
      "a visibly broken link because nobody re-checks it.")
    w("")
    w("Template-variable links are excluded for a different reason: they are not broken at all "
      "in their original context. They depend on a build-time substitution, and whether that "
      "survives migration is a redirect-strategy decision, not a link fix.")

    open(args.out, "w", encoding="utf-8").write("\n".join(L) + "\n")

    if args.json_out:
        json.dump({"scope": args.scope, "docs_root": root, "counts": n, "tiers": tiers},
                  open(args.json_out, "w"), indent=1)

    print(f"{total} findings across {len(targets)} pages "
          f"({auto} mechanically fixable, {n['gone']} need a human)")
    for k in ("templated_fixable", "templated", "malformed", "depth", "renamed",
              "stale", "anchor", "gone"):
        print(f"  {n[k]:5d}  {k}")
    print(f"\nreport -> {args.out}")
    if args.json_out:
        print(f"json   -> {args.json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
