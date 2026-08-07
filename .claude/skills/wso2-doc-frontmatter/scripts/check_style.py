#!/usr/bin/env python3
"""Deterministic subset of the WSO2 style guide — the mechanical rules only.
Judgement-heavy rules (tone, anthropomorphism, plain language) are left to the LLM skill."""
import os, re, sys, json, collections

import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument("docs_root", nargs="?", default="en/docs")
_ap.add_argument("--files", nargs="*", default=None, help="Limit to these paths.")
_ap.add_argument("--json", dest="json_out", default=None,
                 help="Write full findings to this path. Omitted = summary only.")
_ap.add_argument("--gate", action="store_true", help="Exit 1 if any blocking finding.")
_args = _ap.parse_args()
DOCS = _args.docs_root.rstrip("/")
TARGETS = _args.files or None

SMALL = {"a","an","and","as","at","but","by","for","from","in","into","nor","of","on","onto","or",
         "over","per","the","to","up","via","with","vs","near","off","out"}
# PROPER, PROPER_PHRASES and STATUS_LABELS live in fm_lib.py so that this checker
# and fm_fix.py's sentence_case() cannot disagree about which capitals are correct.
# Add new product names there, not here.
from fm_lib import PROPER, PROPER_PHRASES, STATUS_LABELS  # noqa: E402

_PHRASES = sorted(PROPER_PHRASES, key=len, reverse=True)

RULES = [
    # (code, severity, regex, message, section, quoted rule)
    ("QUALITATIVE", "should-fix",
     r"\b(simply|simple|easy|easily|just\s+(?:click|run|add|set|use)|quick|quickly|straightforward|effortless|trivial|obviously|of\s+course)\b",
     "Qualitative/minimising language — it tells the reader how hard the task should feel.",
     "Voice, tone, and audience", "No qualitative language."),
    ("PLEASE", "should-fix", r"\bplease\b",
     "Drop \"please\" from instructions — documentation instructions are imperative, not requests.",
     "Voice, tone, and audience", "Explicitly called out to avoid:"),
    ("TIMELESS", "should-fix",
     r"\b(currently|at\s+the\s+moment|for\s+now|at\s+present|presently|as\s+of\s+(?:now|today|this\s+release)|recently|soon|in\s+the\s+near\s+future|upcoming|newly|brand[-\s]new|latest\s+version|new\s+feature|will\s+be\s+(?:released|available|supported)|coming\s+soon|not\s+yet\s+supported|future\s+release)\b",
     "Time-bound wording — it dates the page and goes stale without anyone editing it.",
     "Timeless documentation", "Avoid these words/phrases when describing product or feature capabilities:"),
    ("EN_DASH", "blocking", r"–",
     "En dash used. The guide bans en dashes outright.",
     "Grammar and punctuation", "En dashes: don't use them. Use a hyphen or the word \"to\" instead."),
    ("EM_DASH_SPACED", "polish", r"\s—|—\s",
     "Em dash with surrounding spaces. Common enough across the docs to be a house convention rather than a slip — raise it once as a convention question, not as hundreds of findings.",
     "Grammar and punctuation", "Em dash (—): no space before or after"),
    ("CLICK_HERE", "blocking", r"\[\s*(?:click\s+here|here|this\s+link|read\s+more|more|link)\s*\]\(",
     "Non-descriptive link text.",
     "Formatting and typography", "Link text: short, unique, descriptive phrases that give context for the destination"),
    ("BARE_URL_LINK", "should-fix", r"\[\s*https?://[^\]]+\]\(",
     "Bare URL used as the link text.",
     "Formatting and typography", "(Never \"click here\" or a bare URL.)"),
    ("FUTURE_TENSE", "polish", r"\b(?:will|shall)\s+(?:be\s+)?(?:see|need|want|have|get|find|notice|receive|return|display|show|create|appear)\b",
     "Future tense where present tense reads better.",
     "Voice, tone, and audience", "Active voice, present tense, indicative/imperative mood."),
    ("THE_USER", "should-fix", r"\bthe\s+user(?:'s)?\b(?!\s+(?:name|id|ID|attribute|claim|pool|store|directory|token|credential|context|identity))",
     "Refers to \"the user\" instead of addressing the reader as \"you\".",
     "Voice, tone, and audience", "Second person for the reader."),
    ("WE_US", "should-fix", r"\b(?:we|us|our)\b(?!\s*[-—])",
     "First person plural for product behaviour.",
     "Voice, tone, and audience", "Third person for WSO2 actions and features."),
]

def in_code_or_url(text):
    """Return a set of char indices inside fenced code, inline code, links' URL part, or HTML."""
    mask = bytearray(len(text))
    for m in re.finditer(r"```.*?```|~~~.*?~~~", text, re.S): mask[m.start():m.end()] = b"\x01"*(m.end()-m.start())
    for m in re.finditer(r"`[^`\n]*`", text): mask[m.start():m.end()] = b"\x01"*(m.end()-m.start())
    for m in re.finditer(r"<!--.*?-->", text, re.S): mask[m.start():m.end()] = b"\x01"*(m.end()-m.start())
    for m in re.finditer(r"<[^>]+>", text): mask[m.start():m.end()] = b"\x01"*(m.end()-m.start())
    for m in re.finditer(r"\]\([^)]*\)", text): mask[m.start():m.end()] = b"\x01"*(m.end()-m.start())
    for m in re.finditer(r"^(?: {4}|\t).*$", text, re.M): mask[m.start():m.end()] = b"\x01"*(m.end()-m.start())
    for m in re.finditer(r"https?://\S+", text): mask[m.start():m.end()] = b"\x01"*(m.end()-m.start())
    for m in re.finditer(r"^---\n.*?\n---", text, re.S): mask[m.start():m.end()] = b"\x01"*(m.end()-m.start())
    return mask

def title_case_violation(h):
    """Judge a heading against 'sentence case, always'.

    Returns (n_offenders, offenders). The caller decides severity: >=2 offenders is
    a confident Title Case verdict; exactly 1 is reported at lower severity, because
    a single stray capital is often a product name the allowlist doesn't know yet.
    """
    core = re.sub(r"\{#[\w-]+\}", "", h)
    core = re.sub(r"`[^`]*`", " ", core)                       # code spans are literals
    core = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", core)     # keep link text only
    core = re.sub(r"<[^>]+>", " ", core)

    # Mask known multi-word proper names so their constituent words aren't scanned.
    for ph in _PHRASES:
        core = core.replace(ph, " \x00 ")

    # Label-prefix rule: a heading may be split by MORE THAN ONE ':' / ';' / spaced
    # dash. Each segment gets its own exempt first word, so split on every boundary.
    segments = [sg for sg in re.split(r"[:;]|\s[-\u2013\u2014]\s", core) if sg.strip()]

    offenders = []
    total_words = 0
    for seg in segments:
        words = re.findall(r"[A-Za-z][A-Za-z0-9'\u2019\-\.]*", seg)
        total_words += len(words)
        for w in words[1:]:                                    # first word of each segment is exempt
            bare = w.rstrip(".").strip("'\u2019")
            if bare in PROPER or bare.upper() == bare:          # acronym or known proper noun
                continue
            if bare.lower() in STATUS_LABELS:                   # (Beta), (Optional), ...
                continue
            if re.match(r"^[A-Z][a-z]", bare):
                offenders.append(w)
    if total_words < 3:
        return 0, []
    return len(offenders), offenders

findings = []
files = []
if TARGETS:
    files = [os.path.relpath(t, DOCS) if t.startswith(DOCS) else t for t in TARGETS]
else:
    for root, _, fs in os.walk(DOCS):
        for f in sorted(fs):
            if f.endswith(".md"): files.append(os.path.relpath(os.path.join(root, f), DOCS))
files.sort()

for rel in files:
    full = os.path.join(DOCS, rel)
    if not os.path.exists(full): continue
    txt = open(full, encoding="utf-8", errors="replace").read()
    mask = in_code_or_url(txt)
    lines = txt.split("\n")
    # line start offsets
    offs, acc = [], 0
    for ln in lines: offs.append(acc); acc += len(ln) + 1

    for code, sev, pat, msg, section, rule in RULES:
        for m in re.finditer(pat, txt, re.I):
            if mask[m.start()] == 1: continue
            ln = max(i for i, o in enumerate(offs) if o <= m.start()) + 1
            findings.append({"file": rel, "line": ln, "severity": sev, "code": code,
                             "match": m.group(0).strip(), "message": msg,
                             "section": section, "rule": rule})

    in_fence = False
    for i, ln in enumerate(lines, 1):
        if re.match(r"^\s*(```|~~~)", ln): in_fence = not in_fence; continue
        if in_fence: continue
        hm = re.match(r"^(#{1,6})\s+(.+?)\s*$", ln)
        if hm:
            n, offenders = title_case_violation(hm.group(2))
            if n >= 2:
                findings.append({"file": rel, "line": i, "severity": "blocking", "code": "HEADING_TITLE_CASE",
                                 "match": hm.group(2), "message": f"Heading is in Title Case (capitalised: {', '.join(offenders)}).",
                                 "section": "Formatting and typography",
                                 "rule": "Headings and titles: sentence case, always."})
            elif n == 1:
                findings.append({"file": rel, "line": i, "severity": "should-fix", "code": "HEADING_CASE_SINGLE_WORD",
                                 "match": hm.group(2), "message": f"Heading has one unexpected capital: {offenders[0]}. Lowercase it, or add it to the proper-noun allowlist if it is a product name.",
                                 "section": "Formatting and typography",
                                 "rule": "Headings and titles: sentence case, always."})

by = collections.Counter((f["code"], f["severity"]) for f in findings)
print("=" * 68); print("STYLE CHECK (deterministic rules only)"); print("=" * 68)
print(f"files scanned  : {len(files)}")
print(f"total findings : {len(findings)}")
print()
print(f"{'COUNT':>6}  {'SEV':<11} CODE"); print("-" * 68)
for (c, s), n in by.most_common(): print(f"{n:>6}  {s:<11} {c}")
if _args.json_out:
    json.dump(findings, open(_args.json_out, "w"), indent=1)
    print(f"\n(full findings -> {_args.json_out})")
else:
    print("\n(re-run with --json <path> for the full findings list)")

if _args.gate and any(f["severity"] == "blocking" for f in findings):
    sys.exit(1)
