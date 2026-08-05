# Frontmatter conventions

Reference for the conventions the scripts implement. The authoritative list of
*required fields* is `.claude/rules/doc-frontmatter-and-metadata.md` in this
repository; this file records the mechanics that rule leaves implicit — field
order, quoting, and how a file path maps to a URL.

If this file and the repository rule disagree, the rule wins.

## Field order and quoting

```yaml
---
title: "Moesif analytics"                        # double-quoted
description: "Configure Moesif to capture ..."   # double-quoted
canonical_url: https://wso2.com/...              # bare
md_url: https://wso2.com/...                     # bare
tags:                                            # block list, lowercase items
  - ai-gateway
  - analytics
author: WSO2 API Platform Documentation Team     # bare
last_updated: 2026-06-16                         # bare YYYY-MM-DD, never quoted
content_type: "how-to"                           # double-quoted
---
```

`fm_fix.py` reproduces this exactly, including the quoting. That matters for a
practical reason: if the serialiser quotes differently from the house style, every
page it touches shows a diff even where no value changed, and the real changes get
buried.

## URL derivation

`BASE` is `https://wso2.com/api-platform/docs`.

| Source file | `canonical_url` | `md_url` |
|---|---|---|
| `foo/bar.md` | `{BASE}/foo/bar/` | `{BASE}/foo/bar.md` |
| `foo/index.md` | `{BASE}/foo/` | `{BASE}/foo.md` |
| `foo/README.md` | `{BASE}/foo/` | `{BASE}/foo.md` |

`README.md` collapses to its directory the same way `index.md` does.

## Versions

Some products keep several versions on disk:

```
<product>/1.0.0/...
<product>/1.1.0/...
<product>/next/...
```

The published site serves the **current release at a version-less URL**, with the
`redirects` plugin in `mkdocs.yml` mapping that version-less path onto the current
release's file. Every other version — older releases, and `next` — is served at a
URL that includes its version segment.

So the rule the scripts implement, which `fm_lib.py:site_paths()` calls
`latest-only`:

> The current release gets the version-less URL. Every other version keeps its
> version segment in both `canonical_url` and `md_url`.

This is the only policy under which each file owns a unique `md_url`. Two
alternatives exist for comparison and are selectable with `--policy`:

| Policy | Behaviour |
|---|---|
| `latest-only` | Default. Current release version-less, others keep their segment. |
| `strip-all` | Every version claims the version-less URL. Produces collisions. |
| `keep-all` | Every version keeps its segment. No stable "latest" URL. |

Changing the policy rewrites URLs across every versioned page, so say so
explicitly when you do.

### A version segment is only a version at the top of the tree

`discover_versions()` treats a directory as a documentation version only at the
docs root (`next/...`) or directly under a single-segment product directory
(`<product>/4.7.0/...`). Anything deeper that merely looks like a version is
something else — most often a third-party connector's own release directory:

```
<product>/<version>/reference/connectors/<connector>/1.0.1/
```

Treating that as a documentation version would invent a phantom product and strip
the wrong segment out of a URL, so the depth limit in `MAX_VERSION_DEPTH` is
load-bearing rather than cosmetic.

## Redirects and `canonical_url` are one contract

Under `latest-only`, a current-release page's `canonical_url` is a version-less
path. That path is not a file — it resolves only because a redirect maps it onto
the release. A page can therefore have valid frontmatter *and* a valid redirect
map and still declare a canonical URL that resolves to nothing, because each half
looks correct on its own.

`check_redirects.py` is what catches that, as `CANONICAL_UNREACHABLE`. Run it
after changing the URL policy, and after adding a page to a versioned tree.

The practical consequence: **adding a page to a versioned tree is a two-part
change** — the page, and a `redirect_maps` entry for its version-less path. Miss
the second and the page still renders and still passes a link check; only its
declared canonical URL is dead.

## Links containing build-time variables

Pages migrated from the API Manager docs may contain link and image targets built
around a template variable:

```markdown
[Rate limiting]({{base_path}}/api-design-manage/design/rate-limiting/overview/)
<img src="{{base_path}}/assets/img/example.png" />
```

Both the Markdown and raw-HTML forms occur. The variable is substituted at build
time by machinery that is not present in this site, which is why migrated pages use
relative links instead.

The checkers treat these as **out of scope, not broken**: `check_links.py` reports
`LINK_TEMPLATED` at `polish` severity, and `report_links.py` quarantines them in a
section with no proposed fix. Nothing should rewrite them until the redirect
strategy is settled, because the right replacement depends on that decision.

Redirects themselves belong either in a `redirects.yml` file or in a `redirects`
block inside `mkdocs.yml`.

## Adding another source of documentation

Nothing in the scripts is tied to a particular product or version. Versions are
discovered from the directory tree, and each product's current release is resolved
independently, so a new product or a version bump needs no code change.

Two things are configuration rather than logic, both in `fm_lib.py`:

- **`LEGACY_DOMAINS`** — locations the documentation has migrated away from. A link
  or frontmatter URL still pointing at one is migration debt. When another set of
  docs is folded in, add its old domain here; the checkers pick it up.
- **`CT_ALIASES`** — near-miss `content_type` values seen in incoming pages, mapped
  onto the closest valid type. Extend it when a new source uses different names.

## `content_type`

One of `how-to`, `tutorial`, `reference`, `concept`, `explanation`,
`troubleshooting`, `faq`, `release-notes`, `changelog`, `quickstart` — based on
the Diátaxis framework.

Choose by what the page *is*: numbered task steps → `how-to`; an end-to-end
learning walkthrough → `tutorial`; parameter and field tables → `reference`;
explains an idea without steps → `concept`; diagnosing failures →
`troubleshooting`. A section landing page that is mostly a list of links is
`concept`.

`overview` is not a valid value. `CT_ALIASES` in `fm_lib.py` maps it, and a few
other near-misses, onto the closest valid type.

## Fields the scripts will not generate

`title` and `description` are what a reader and a search engine actually see. A
generated one looks finished, so nobody revisits it — which is worse than an
obviously missing one.

`fm_fix.py` derives `title` from an existing H1 when scaffolding, since that is an
editorial decision someone already made, and leaves `description` as `TODO` in the
worklist for a person or an LLM to write after reading the page.
