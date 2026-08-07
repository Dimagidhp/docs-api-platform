#!/usr/bin/env python3
"""Link + asset checker for wso2/docs-api-platform (migration-aware)."""
import os, re, sys, json, collections, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fm_lib import is_legacy_url  # noqa: E402

import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument("docs_root", nargs="?", default="en/docs")
_ap.add_argument("--json", dest="json_out", default=None,
                 help="Write full findings to this path. Omitted = summary only.")
_ap.add_argument("--gate", action="store_true", help="Exit 1 if any blocking finding.")
_ap.add_argument("--mkdocs-yml", dest="mkdocs_yml", default=None,
                 help="Where to read `toc_depth` from. Defaults to <docs_root>/../mkdocs.yml.")
_args = _ap.parse_args()
DOCS = _args.docs_root.rstrip("/")
SITE = "https://wso2.com/api-platform/docs"
VER = re.compile(r"^(\d+\.\d+(\.\d+)?|next|latest)$")

md_files, all_files = set(), set()
for root, _, fs in os.walk(DOCS):
    for f in fs:
        rel = os.path.relpath(os.path.join(root, f), DOCS)
        all_files.add(rel)
        if f.endswith(".md"):
            md_files.add(rel)

def slug(h):
    """Match python-markdown's toc slugify: strip non-word chars, then collapse
    runs of whitespace AND hyphens into a single hyphen."""
    h = re.sub(r"`|\*", "", h)   # backticks/emphasis markers; keep _ (it is a \w char)
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)   # link text only
    h = re.sub(r"<[^>]+>", "", h)
    h = re.sub(r"[^\w\s-]", "", h).strip().lower()
    return re.sub(r"[-\s]+", "-", h)

def toc_depth(mkdocs_yml):
    """The `toc_depth` configured for the python-markdown toc extension.

    This is load-bearing, not cosmetic. With `toc_depth: 3`, python-markdown
    assigns NO `id` to h4 and deeper — so `#some-h4-heading` links resolve to
    nothing in the built site even though the heading is right there in the
    Markdown. Neither this checker nor `mkdocs build` on 1.4.x flags that on its
    own, so a page can look clean and still have dead in-page links.
    """
    if not os.path.isfile(mkdocs_yml):
        return 6
    text = open(mkdocs_yml, encoding="utf-8", errors="replace").read()
    m = re.search(r"^\s*toc_depth:\s*['\"]?(\d)", text, re.M)
    return int(m.group(1)) if m else 6


MKDOCS_YML = _args.mkdocs_yml or os.path.join(os.path.dirname(DOCS) or ".", "mkdocs.yml")
TOC_DEPTH = toc_depth(MKDOCS_YML)

# harvest anchors per file (headings + explicit <a name>/{#id})
#
# `anchors` is what the build actually produces. `deep_anchors` holds the ids a
# heading WOULD have if toc_depth allowed it — kept separately so a link to one
# can be reported as its own cause rather than as a generic missing anchor.
#
# Do NOT suggest `{#id}` as the fix for a deep heading here, even though
# `attr_list` would honour it: the `markdownextradata` plugin runs every page
# through Jinja BEFORE Markdown, and `{#` opens a Jinja comment. An unterminated
# one fails the whole build with "Missing end of comment tag". The safe additive
# fix is `<a name="...">` immediately above the heading — inert HTML, already used
# in ~300 pages here, and it leaves the heading level and the TOC untouched.
anchors, deep_anchors = {}, {}
for p in md_files:
    txt = open(os.path.join(DOCS, p), encoding="utf-8", errors="replace").read()
    txt = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
    txt = re.sub(r"```.*?```", "", txt, flags=re.S)
    a, deep = set(), set()
    for m in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", txt, re.M):
        level, h = len(m.group(1)), m.group(2)
        exp = re.search(r"\{#([\w-]+)\}", h)
        if exp:
            a.add(exp.group(1))            # explicit id survives any toc_depth
            h = h[:exp.start()]
        (a if level <= TOC_DEPTH else deep).add(slug(h))
    for m in re.finditer(r'<a[^>]+(?:name|id)="([^"]+)"', txt): a.add(m.group(1))
    for m in re.finditer(r'\{#([\w-]+)\}', txt): a.add(m.group(1))
    anchors[p] = a
    deep_anchors[p] = deep - a

LINK = re.compile(r'(!?)\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
# Tag name is captured so an `<a href>` is reported as a broken LINK and an
# `<img src>` as a missing IMAGE. Lumping them together mislabels every raw-HTML
# link as an image, which sends whoever reads the report looking for the wrong thing.
HTML_SRC = re.compile(r'<(img|a|source|iframe)[^>]+(?:src|href)="([^"]+)"')


def url_base(rel):
    """Directory the RENDERED page sits in, under `use_directory_urls: true`.

    `a/b/page.md` is served at `/a/b/page/` — one level deeper than the source —
    while `a/b/index.md` is served at `/a/b/`, the same level.

    mkdocs rewrites relative targets written in Markdown syntax, resolving them
    against the source file, but passes raw HTML through untouched, so the browser
    resolves an `<img src>` against the rendered URL instead. The identical string
    is therefore correct in one syntax and broken in the other. Resolving both the
    same way is how a working image gets "fixed" into a broken one.
    """
    d = os.path.dirname(rel)
    stem = os.path.basename(rel)[:-3] if rel.endswith(".md") else os.path.basename(rel)
    return d if stem in ("index", "README") else (f"{d}/{stem}" if d else stem)

findings = []
def add(f, sev, code, msg):
    findings.append({"file": f, "severity": sev, "code": code, "message": msg})

for p in sorted(md_files):
    full = os.path.join(DOCS, p)
    txt = open(full, encoding="utf-8", errors="replace").read()
    body = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    body = re.sub(r"`[^`\n]*`", "", body)
    d = os.path.dirname(p)

    targets = [(m.group(1) == "!", m.group(3), False) for m in LINK.finditer(body)]
    targets += [(m.group(1).lower() != "a", m.group(2), True) for m in HTML_SRC.finditer(body)]

    for is_img, t, is_html in targets:
        if t.startswith(("mailto:", "tel:", "#!")):
            continue
        # Build-time template variables (e.g. `{{base_path}}`) are not paths. They
        # cannot be resolved statically and are not broken in their own context, so
        # report them as informational rather than as broken links.
        if re.search(r"\{\{.*?\}\}", t):
            add(p, "polish", "LINK_TEMPLATED",
                f"Target contains a build-time variable, so it can't be checked statically: `{t}`")
            continue
        # stale pre-migration domain
        if is_legacy_url(t):
            add(p, "blocking", "STALE_LINK", f"Links to the pre-migration site: `{t}`")
            continue
        if re.match(r"^https?://", t):
            if t.startswith(SITE):
                # absolute self-link — should be relative, and must resolve
                add(p, "should-fix", "ABS_SELF_LINK",
                    f"Absolute link to our own site: `{t}` — use a relative path so it survives moves and works in previews.")
            continue
        if t.startswith("//"):
            continue
        if t.startswith("#"):
            frag = urllib.parse.unquote(t[1:])
            if frag and frag not in anchors.get(p, set()):
                if frag in deep_anchors.get(p, set()):
                    add(p, "blocking", "ANCHOR_TOO_DEEP",
                        f"`{t}` names a heading deeper than h{TOC_DEPTH}, and `toc_depth: {TOC_DEPTH}` "
                        f"means the build gives it no id — so the link goes nowhere. Add "
                        f"`<a name=\"{frag}\"></a>` just above the heading, or promote the heading "
                        f"to h{TOC_DEPTH}.")
                else:
                    add(p, "should-fix", "ANCHOR_MISSING", f"In-page anchor `{t}` has no matching heading.")
            continue

        path, _, frag = t.partition("#")
        path = urllib.parse.unquote(path)
        frag = urllib.parse.unquote(frag)
        if not path:
            continue
        # WHICH BASE APPLIES — verified against a real mkdocs build, not inferred.
        #
        # mkdocs rewrites a Markdown target only when the literal path names a file
        # that exists in docs_dir (`../c/target.md`, `../img.png`). Then, and only
        # then, is the target resolved against the SOURCE directory.
        #
        # Everything else is passed through verbatim and resolved by the browser
        # against the RENDERED URL, which sits one level deeper for a non-index page:
        #   * raw HTML (`<img src>`, `<a href>`)
        #   * directory-style Markdown links (`../c/target/`)
        #   * extensionless Markdown links (`../c/target`) — passed through even
        #     when `target.md` exists right there
        #
        # Judging a passed-through link source-relative is how a link that is broken
        # in the browser gets reported as clean.
        if path.startswith("/"):
            cand = path.lstrip("/")
            rewritten = False
        else:
            literal = os.path.normpath(os.path.join(d, path)).replace("\\", "/")
            rewritten = (not is_html) and literal in all_files
            rel_base = d if rewritten else url_base(p)
            cand = os.path.normpath(os.path.join(rel_base, path))
        if cand.startswith(".."):
            add(p, "blocking", "LINK_ESCAPES_ROOT", f"Link `{t}` resolves outside the docs root.")
            continue

        resolved = None
        for c in (cand, cand + ".md", os.path.join(cand, "index.md"), os.path.join(cand, "README.md")):
            if c in all_files:
                resolved = c; break
        if resolved is None:
            if os.path.isdir(os.path.join(DOCS, cand)):
                add(p, "should-fix", "LINK_DIR_NO_INDEX", f"Link `{t}` points at a directory with no index.md/README.md.")
            else:
                code = "IMG_MISSING" if is_img else "LINK_BROKEN"
                add(p, "blocking", code, f"{'Image' if is_img else 'Link'} target does not exist: `{t}`")
            continue
        if frag and resolved.endswith(".md"):
            if frag not in anchors.get(resolved, set()):
                if frag in deep_anchors.get(resolved, set()):
                    add(p, "blocking", "ANCHOR_TOO_DEEP",
                        f"`{t}` names a heading in `{resolved}` deeper than h{TOC_DEPTH}, which "
                        f"`toc_depth: {TOC_DEPTH}` leaves without an id, so the link goes nowhere.")
                else:
                    add(p, "should-fix", "ANCHOR_MISSING",
                        f"Anchor `#{frag}` not found in `{resolved}` (link was `{t}`).")

    # Alt text. The style guide is specific here and it is easy to get wrong:
    #   - alt="" is CORRECT for purely decorative images or screenshots that
    #     merely mirror the text steps. Do not flag it as missing.
    #   - informative images need meaningful alt text, max 155 characters.
    #   - "Image of" / "Photo of" prefixes are called out to avoid.
    for m in LINK.finditer(body):
        if m.group(1) != "!":
            continue
        alt, src = m.group(2), m.group(3)
        if not alt.strip():
            add(p, "polish", "IMG_ALT_EMPTY_VERIFY",
                f"Image has alt=\"\": `{src}`. Correct if the image is decorative or "
                f"mirrors the text steps; a defect if it carries information.")
        elif len(alt) > 155:
            add(p, "should-fix", "IMG_ALT_TOO_LONG",
                f"Alt text is {len(alt)} chars; the guide caps it at 155: `{src}`")
        if re.match(r"^\s*(image|photo|picture|screenshot)\s+of\b", alt, re.I):
            add(p, "should-fix", "IMG_ALT_PREFIX",
                f"Alt text starts with \"{alt.split()[0]} of\" — the guide calls this out to avoid: `{src}`")
        if re.search(r"\.gif$", src.split("#")[0], re.I):
            add(p, "should-fix", "IMG_ANIMATED_GIF",
                f"Animated GIF: `{src}`. The guide says use a resource-efficient format like MP4 instead.")

# orphan assets
used = set()
for p in md_files:
    txt = re.sub(r"<!--.*?-->", "", open(os.path.join(DOCS, p), encoding="utf-8", errors="replace").read(), flags=re.S)
    d = os.path.dirname(p)
    for m in list(LINK.finditer(txt)) + list(HTML_SRC.finditer(txt)):
        t = m.group(3) if m.lastindex and m.lastindex >= 3 else m.group(1)
        if re.match(r"^(https?:|mailto:|#)", t): continue
        t = urllib.parse.unquote(t.split("#")[0])
        if not t: continue
        used.add(os.path.normpath(os.path.join(d, t)) if not t.startswith("/") else t.lstrip("/"))
assets = {f for f in all_files if f.startswith("assets/") and re.search(r"\.(png|jpg|jpeg|gif|svg|webp|mp4)$", f, re.I)}
orphans = sorted(assets - used)

by = collections.Counter((f["code"], f["severity"]) for f in findings)
print("=" * 68); print("LINK & ASSET CHECK"); print("=" * 68)
print(f"md files scanned  : {len(md_files)}")
print(f"total findings    : {len(findings)}")
print(f"orphaned assets   : {len(orphans)} of {len(assets)} images never referenced")
print()
print(f"{'COUNT':>6}  {'SEV':<11} CODE"); print("-" * 68)
for (code, sev), n in by.most_common():
    print(f"{n:>6}  {sev:<11} {code}")
if _args.json_out:
    json.dump({"findings": findings, "orphans": orphans}, open(_args.json_out, "w"), indent=1)
    print(f"\n(full findings -> {_args.json_out})")
else:
    print("\n(re-run with --json <path> for the full findings list)")

if _args.gate and any(f["severity"] == "blocking" for f in findings):
    sys.exit(1)
