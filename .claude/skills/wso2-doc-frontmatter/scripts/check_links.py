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

# harvest anchors per file (headings + explicit <a name>/{#id})
anchors = {}
for p in md_files:
    txt = open(os.path.join(DOCS, p), encoding="utf-8", errors="replace").read()
    txt = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
    txt = re.sub(r"```.*?```", "", txt, flags=re.S)
    a = set()
    for m in re.finditer(r"^#{1,6}\s+(.+?)\s*$", txt, re.M):
        h = m.group(1)
        exp = re.search(r"\{#([\w-]+)\}", h)
        if exp: a.add(exp.group(1)); h = h[:exp.start()]
        a.add(slug(h))
    for m in re.finditer(r'<a[^>]+(?:name|id)="([^"]+)"', txt): a.add(m.group(1))
    for m in re.finditer(r'\{#([\w-]+)\}', txt): a.add(m.group(1))
    anchors[p] = a

LINK = re.compile(r'(!?)\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
HTML_SRC = re.compile(r'<img[^>]+src="([^"]+)"')

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

    targets = [(m.group(1) == "!", m.group(3)) for m in LINK.finditer(body)]
    targets += [(True, m.group(1)) for m in HTML_SRC.finditer(body)]

    for is_img, t in targets:
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
                add(p, "should-fix", "ANCHOR_MISSING", f"In-page anchor `{t}` has no matching heading.")
            continue

        path, _, frag = t.partition("#")
        path = urllib.parse.unquote(path)
        frag = urllib.parse.unquote(frag)
        if not path:
            continue
        cand = os.path.normpath(os.path.join(d, path)) if not path.startswith("/") else path.lstrip("/")
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
