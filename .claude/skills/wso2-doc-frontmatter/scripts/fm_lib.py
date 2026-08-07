#!/usr/bin/env python3
"""Shared frontmatter logic for the WSO2 API Platform docs repo.

The one thing worth understanding before changing anything here: this repo keeps
several *versions* of the same page on disk (``<product>/1.0.0/x.md``,
``<product>/1.1.0/x.md``, ``<product>/next/x.md``), and every one of them is
published at a URL that includes its version segment — the latest release included.
A version-less URL redirects to the versioned page rather than serving content.

That makes the version segment the only genuinely tricky part of deriving a URL from
a path, so it is all funnelled through :func:`site_paths` below.
"""
import os
import re
import subprocess
import datetime

# ---------------------------------------------------------------------------
# YAML loading, with a dependency-free fallback.
#
# PyYAML is nicer, but requiring `pip install` is real friction — on macOS with
# Homebrew Python, a plain `pip install` is refused outright (PEP 668), and in CI
# it is one more step to get wrong. Frontmatter here is flat: scalars, block
# lists, and comments. That is a small enough grammar to parse directly, so the
# scripts run on a bare `python3` with nothing installed.
#
# The fallback is validated against PyYAML across every page in the repo; see
# `--selftest` in fm_audit.py.
# ---------------------------------------------------------------------------
try:
    import yaml as _yaml
except ImportError:
    _yaml = None


def _strip_comment(v):
    """Remove a trailing ` # comment`, but never inside quotes or a URL."""
    out, quote = [], None
    for i, ch in enumerate(v):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            continue
        if ch == "#" and (i == 0 or v[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).strip()


def _scalar(v):
    """Coerce a YAML scalar the way safe_load would, for the subset we use."""
    v = _strip_comment(v)
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        inner = v[1:-1]
        if v[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        return inner
    if v in ("", "~", "null"):
        return None
    if v in ("true", "True"):
        return True
    if v in ("false", "False"):
        return False
    if re.match(r"^\d{4}-\d{2}-\d{2}$", v):
        try:
            return datetime.date.fromisoformat(v)   # match PyYAML's date typing
        except ValueError:
            return v
    if re.match(r"^-?\d+$", v):
        return int(v)
    if re.match(r"^\[.*\]$", v):                    # inline flow list
        body = v[1:-1].strip()
        return [_scalar(x.strip()) for x in body.split(",")] if body else []
    return v


def parse_frontmatter_yaml(raw):
    """Parse the flat YAML subset used in frontmatter. Raises ValueError if the
    input uses something outside that subset, so callers can report it honestly
    rather than silently mis-reading a page."""
    data, key = {}, None
    for line in raw.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m_item = re.match(r"^\s+-\s*(.*)$", line)
        if m_item:
            if key is None:
                raise ValueError("list item before any key")
            data.setdefault(key, [])
            if not isinstance(data[key], list):
                raise ValueError(f"list item under non-list key {key!r}")
            data[key].append(_scalar(m_item.group(1)))
            continue
        m_kv = re.match(r"^([A-Za-z_][\w.-]*)\s*:\s*(.*)$", line)
        if not m_kv:
            raise ValueError(f"unsupported line: {line[:60]!r}")
        key, val = m_kv.group(1), m_kv.group(2)
        if val.strip() in ("|", ">", "|-", ">-"):
            raise ValueError(f"block scalar on {key!r} is outside the supported subset")
        data[key] = [] if val.strip() == "" else _scalar(val)
    return data


def load_frontmatter(raw, prefer_pyyaml=True):
    """Load frontmatter YAML, using PyYAML when available."""
    if prefer_pyyaml and _yaml is not None:
        out = _yaml.safe_load(raw)
        return out if out is not None else {}
    return parse_frontmatter_yaml(raw)


HAVE_PYYAML = _yaml is not None

BASE = "https://wso2.com/api-platform/docs"
DOCS_ROOT = "en/docs"

VER_RE = re.compile(r"^(\d+\.\d+(\.\d+)?|next|latest)$")
INDEXY = ("index", "README")

# A *documentation* version segment lives at the top of the tree: either at the
# docs root (`next/...`) or directly under a single-segment product directory
# (`api-manager/4.7.0/...`). Anything deeper that merely looks like a version is
# something else — most importantly a third-party connector's own release
# directory, e.g.
#     api-manager/4.2.0/reference/connectors/redis-connector/1.0.1/
# Treating that as a doc version invents a phantom product and can strip the
# wrong segment out of a URL, so the depth limit is load-bearing, not cosmetic.
MAX_VERSION_DEPTH = 1


def version_index(rel):
    """Index of the doc-version segment in `rel`, or None if there isn't one."""
    parts = rel.split("/")
    for i, p in enumerate(parts[:MAX_VERSION_DEPTH + 1]):
        if VER_RE.match(p):
            return i
    return None

REQUIRED = ["title", "description", "canonical_url", "md_url", "tags",
            "author", "last_updated", "content_type"]
AUTHOR = "WSO2 API Platform Documentation Team"
DESC_MAX = 158
DESC_MIN = 50
TITLE_MAX = 60

# The enum from .claude/rules/doc-frontmatter-and-metadata.md, verbatim.
ALLOWED_CT = {"how-to", "tutorial", "reference", "concept", "explanation",
              "troubleshooting", "faq", "release-notes", "changelog", "quickstart"}

# Near-miss values that appear in practice but are not in the rule's enum, mapped
# onto the closest valid type. `overview` is the common one; it folds into
# `concept`. Set ADD_OVERVIEW_TO_ENUM to treat it as valid in its own right.
ADD_OVERVIEW_TO_ENUM = False
CT_ALIASES = {
    "overview": "concept",
    "guide": "how-to",
    "howto": "how-to",
    "how to": "how-to",
    "quick-start": "quickstart",
    "quick start": "quickstart",
    "getting-started": "quickstart",
    "ref": "reference",
    "conceptual": "concept",
    "release notes": "release-notes",
}


# ---------------------------------------------------------------------------
# Capitalisation allowlists. Shared, because two scripts need the same answer:
# `check_style.py` decides whether a capital in a heading is a violation, and
# `fm_fix.py` decides whether to lowercase a word when it derives a `title` from
# an H1. If those disagree, one script lowercases what the other says is correct.
# ---------------------------------------------------------------------------

SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "into", "nor",
         "of", "on", "onto", "or", "over", "per", "the", "to", "up", "via", "with",
         "vs", "near", "off", "out"}

# Product/proper nouns and acronyms that legitimately stay capitalised mid-heading.
PROPER = {"WSO2", "API", "APIs", "AI", "LLM", "LLMs", "MCP", "REST", "gRPC", "GraphQL",
          "JSON", "YAML", "XML", "HTTP", "HTTPS", "OAuth", "OAuth2", "JWT", "SSO", "IdP",
          "OIDC", "SAML", "TLS", "mTLS", "SSL", "CORS", "URL", "URI", "URLs", "ID", "IDs",
          "UI", "CLI", "SDK", "IDE", "CI", "CD", "VM", "VMs", "K8s", "Kubernetes",
          "Docker", "Helm", "Istio", "Envoy", "Redis", "PostgreSQL", "MySQL", "Oracle",
          "Grafana", "Prometheus", "Jaeger", "Zipkin", "OpenTelemetry", "OpenSearch",
          "Elasticsearch", "Moesif", "Stripe", "AWS", "Azure", "GCP", "Bedrock", "OpenAI",
          "Anthropic", "Gemini", "Mistral", "Ollama", "Choreo", "Bijira", "Ballerina",
          "Git", "GitHub", "GitLab", "Linux", "Windows", "macOS", "Java", "Python", "Go",
          "Node", "npm", "Maven", "Gradle", "Swagger", "OpenAPI", "AsyncAPI", "Postman",
          "Portal", "Gateway", "Platform", "Manager", "Publisher", "Developer",
          "Control", "Plane",
          "Hub", "Workspace", "Analytics", "PII", "RBAC", "ACL", "SLA", "TPS", "QPS",
          "DNS", "IP", "TCP", "UDP", "gRPC-Web", "Kafka", "RabbitMQ", "NGINX", "Terraform",
          "Ansible", "Prometheus-compatible", "Bitbucket", "Vault", "Keycloak", "Okta",
          "Auth0", "Asgardeo", "I", "Step", "Table", "Contents", "Note", "Tip", "Warning",
          "Example", "Appendix", "FAQ", "README", "Enumerated", "Values"}

# Phrase-level allowlist: matched case-sensitively and masked out BEFORE per-word
# scanning, because multi-word product names cannot be expressed as single words.
PROPER_PHRASES = {
    # Third-party products / cloud services
    "Google Cloud Trace", "Google Cloud Monitoring", "Google Cloud",
    "Azure AI Content Safety", "Azure Content Safety Content Moderation",
    "Azure Content Safety Guardrail", "Azure Content Safety", "Azure OpenAI",
    "AWS Bedrock Guardrails", "AWS Bedrock Guardrail", "Docker Compose",
    "OpenSearch Dashboards", "VS Code", "Server-Sent Events",
    # Kubernetes API kinds / concepts
    "Horizontal Pod Autoscaler", "Pod Disruption Budget", "Custom Resource Definition",
    "Service Account", "ConfigMap", "StatefulSet", "DaemonSet", "HTTPRoute", "Gateway API",
    # Standards
    "JSON Schema Draft 7", "JSON Schema", "JSONPath",
    # WSO2 components (capitalised-dominant in the corpus)
    "Gateway Controller", "Developer Portal", "Control Plane", "Policy Hub",
    "Policy Engine", "Gateway Builder", "Event Gateway", "API Platform Console",
    "API Platform", "MCP Proxy", "API Proxy", "Publisher Portal", "Admin Portal",
    "API Gateway",
    "API Manager", "AI Gateway", "Universal Gateway", "Micro Integrator",
    "Service Catalog", "API Product", "API Products",
    # --- Policy Hub policy names -------------------------------------------------
    # Treated as proper nouns, matching the Policy Hub catalogue. Remove this block
    # if policy names should instead follow sentence case.
    "Model Weighted Round Robin", "Model Round Robin", "Sentence Count Guardrail",
    "Word Count Guardrail", "Content Length Guardrail", "JSON Schema Guardrail",
    "Regex Guardrail", "URL Guardrail", "Semantic Prompt Guard",
    "Semantic Tool Filtering", "PII Masking", "Analytics Header Filter",
    "Subscription Validation", "API Key Auth", "Basic Auth", "JWT Auth", "Rate Limit",
}

# Conventional release-stage / status labels never count as Title Case evidence.
STATUS_LABELS = {"beta", "alpha", "ga", "preview", "deprecated", "optional",
                 "experimental", "recommended", "required", "default", "new", "legacy"}

# Words in PROPER that are NOT product names on their own. Two kinds:
# document furniture ("Table of Contents", "Step 3"), and generic component words
# that are only capitalised inside a longer name — "Gateway" in "AI Gateway",
# "Portal" in "Developer Portal". `check_style.py` needs them in PROPER so it does
# not flag those longer names word by word, but a title derived from an H1 should
# lowercase them unless the full phrase is present in PROPER_PHRASES.
TITLE_GENERIC = {"Table", "Contents", "Note", "Tip", "Warning", "Example", "Appendix",
                 "Step", "Values", "Enumerated", "I",
                 "Gateway", "Portal", "Platform", "Manager", "Publisher", "Developer",
                 "Control", "Plane", "Hub", "Workspace", "Analytics"}

# What `fm_fix.py` protects when it sentence-cases an H1 into a `title`.
TITLE_PROPER = PROPER - TITLE_GENERIC


# Domains the documentation has migrated away from. A link or a frontmatter URL
# still pointing at one of these is migration debt regardless of which source repo
# it came from, so add to this list rather than editing the checkers when another
# set of docs is folded in.
LEGACY_DOMAINS = (
    "apim.docs.wso2.com",
    "/bijira/",
)


def is_legacy_url(value):
    """True if `value` points at a pre-migration location."""
    v = str(value)
    return any(d in v for d in LEGACY_DOMAINS)


def effective_allowed_ct():
    s = set(ALLOWED_CT)
    if ADD_OVERVIEW_TO_ENUM:
        s.add("overview")
    return s


def split_version(rel):
    """Return (version_or_None, path_with_version_removed)."""
    i = version_index(rel)
    if i is None:
        return None, rel
    parts = rel.split("/")
    return parts[i], "/".join(parts[:i] + parts[i + 1:])


def product_of(rel):
    """Top-level product directory for a versioned page, else None."""
    i = version_index(rel)
    if i is None:
        return None
    return "/".join(rel.split("/")[:i])


def discover_versions(docs_root=DOCS_ROOT):
    """Map product dir -> sorted list of on-disk version segments.

    ``next`` sorts last (it is unreleased); numeric versions sort naturally.
    """
    found = {}
    for root, dirs, _ in os.walk(docs_root):
        prod = os.path.relpath(root, docs_root).replace("\\", "/")
        if prod == ".":
            prod = ""
        # Depth of the version dir itself == number of segments in `prod`.
        if len(prod.split("/")) > MAX_VERSION_DEPTH if prod else False:
            continue
        for d in dirs:
            if VER_RE.match(d):
                found.setdefault(prod, set()).add(d)

    def key(v):
        if v in ("next", "latest"):
            return (1, [])
        return (0, [int(x) for x in v.split(".")])

    return {k: sorted(v, key=key) for k, v in found.items()}


def current_release(product, versions_map):
    """Newest *released* version for a product (ignores next/latest)."""
    vs = [v for v in versions_map.get(product, []) if v not in ("next", "latest")]
    return vs[-1] if vs else None


def site_paths(rel, versions_map=None, policy="keep-all"):
    """Derive (canonical_url, md_url) for a repo-relative Markdown path.

    policy:
      "keep-all"     DEFAULT, and what the site does. Every version keeps its
                     segment, latest release included.
      "latest-only"  Gives the latest release a version-less URL.
      "strip-all"    Every version claims one version-less URL. Collides.
    """
    versions_map = versions_map if versions_map is not None else {}
    ver, stripped = split_version(rel)
    prod = product_of(rel)

    if ver is None:
        url_rel = rel
    elif policy == "strip-all":
        url_rel = stripped
    elif policy == "keep-all":
        url_rel = rel
    else:  # latest-only
        url_rel = stripped if ver == current_release(prod, versions_map) else rel

    stem = url_rel[:-3] if url_rel.endswith(".md") else url_rel
    base = stem.rsplit("/", 1)[-1]

    if base in INDEXY:
        dir_part = stem[: -len(base)].rstrip("/")
        canonical = f"{BASE}/{dir_part}/" if dir_part else f"{BASE}/"
        md = f"{BASE}/{dir_part}.md" if dir_part else f"{BASE}/index.md"
    else:
        canonical = f"{BASE}/{stem}/"
        md = f"{BASE}/{stem}.md"
    return canonical, md


def git_last_modified(path, repo_root="."):
    """Author date of the last commit touching `path`, as YYYY-MM-DD."""
    try:
        out = subprocess.run(
            ["git", "-C", repo_root, "log", "-1", "--format=%ad", "--date=short", "--", path],
            capture_output=True, text=True, timeout=30,
        )
        d = out.stdout.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            return d
    except Exception:
        pass
    return datetime.date.today().isoformat()


def norm_date(v):
    """Coerce whatever YAML gave us into a YYYY-MM-DD string, or None."""
    if v is None:
        return None
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.date().isoformat() if isinstance(v, datetime.datetime) else v.isoformat()
    s = str(v).strip().strip('"').strip("'").split("T")[0]
    return s if re.match(r"^\d{4}-\d{2}-\d{2}$", s) else None


def split_frontmatter(text):
    """Return (raw_yaml_or_None, body). Tolerates a UTF-8 BOM."""
    t = text.lstrip("﻿")
    if not t.startswith("---"):
        return None, t
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?(.*)$", t, re.S)
    if not m:
        return None, t
    return m.group(1), m.group(2)


def first_h1(body):
    """First H1, with inline Markdown stripped.

    Legacy API Manager pages write headings as `# **Bold Heading**`, and the
    emphasis markers must not leak into `title` — they would be rendered
    literally in a browser tab and a search result.
    """
    m = re.search(r"^#\s+(.+?)\s*$", body, re.M)
    if not m:
        return None
    t = m.group(1).strip()
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)   # links -> link text
    t = re.sub(r"`([^`]*)`", r"\1", t)                   # code spans
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)            # bold
    t = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", t)      # underscore emphasis
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", t)   # single-asterisk italics
    t = re.sub(r"<[^>]+>", "", t)                        # stray inline HTML
    t = re.sub(r"\{#[\w-]+\}", "", t)                    # explicit anchor id
    return re.sub(r"\s+", " ", t).strip() or None


def md_files(docs_root=DOCS_ROOT):
    out = []
    for root, _, fs in os.walk(docs_root):
        for f in fs:
            if f.endswith(".md"):
                out.append(os.path.relpath(os.path.join(root, f), docs_root).replace("\\", "/"))
    return sorted(out)


def yaml_str(s):
    """Quote a scalar for YAML only when it needs it."""
    s = str(s)
    if re.search(r'^[\s>|@`%&*!\[\]{}#-]|[:#]\s|["\']|\n|:$', s) or s.strip() != s:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


# The repo's house style: these scalars are double-quoted, everything else is bare.
# Matching it exactly keeps a fix run's diff limited to fields that genuinely
# changed, instead of showing a change on every page it touches.
ALWAYS_QUOTE = {"title", "description", "content_type"}
NEVER_QUOTE = {"canonical_url", "md_url", "last_updated", "author"}


def render_frontmatter(fm, order=None):
    """Serialise a frontmatter dict in the repo's conventional field order and quoting."""
    order = order or REQUIRED
    keys = [k for k in order if k in fm] + [k for k in fm if k not in order]
    lines = ["---"]
    for k in keys:
        v = fm[k]
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {yaml_str(item)}")
        elif k in NEVER_QUOTE:
            lines.append(f"{k}: {v}")
        elif k in ALWAYS_QUOTE:
            esc = str(v).replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{k}: "{esc}"')
        else:
            lines.append(f"{k}: {yaml_str(v)}")
    lines.append("---")
    return "\n".join(lines)
