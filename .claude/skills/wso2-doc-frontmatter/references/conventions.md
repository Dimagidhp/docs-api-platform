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

`README.md` is handled the same way as `index.md`. Note that most `README.md` files
under `en/docs/` are housekeeping notes rather than documentation pages, and none are
currently in the mkdocs nav.

## Versions

Some products keep several versions on disk:

```
<product>/1.0.0/...
<product>/1.1.0/...
<product>/next/...
```

**Every version, including the latest, is published at a URL that includes its
version segment.** So `canonical_url` and `md_url` both keep it.

A version-less URL redirects to the versioned page rather than serving content, so it
is never the canonical.

`fm_lib.py:site_paths()` calls this `keep-all`, and it is the default. Two other
policies are selectable with `--policy`; neither matches the site:

| Policy | Behaviour |
|---|---|
| `keep-all` | Default. Every version keeps its segment. |
| `latest-only` | Latest release gets a version-less URL. |
| `strip-all` | All versions share one version-less URL. Produces collisions. |

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

## Redirects

`check_redirects.py` validates `redirect_maps` in `mkdocs.yml`: every target exists,
no source is shadowed by a real file, no chains (the plugin does not follow them),
and no map is left pointing at a superseded version after a version bump.

`CANONICAL_UNREACHABLE` only applies under `--policy latest-only`. Under `keep-all` a
canonical is a versioned path, which is a real file, so it cannot depend on a
redirect existing.

## Links containing build-time variables

Pages migrated from the API Manager docs may contain link and image targets built
around a template variable:

```markdown
[Rate limiting]({{base_path}}/api-design-manage/design/rate-limiting/overview/)
<img src="{{base_path}}/assets/img/example.png" />
```

Both the Markdown and raw-HTML forms occur. The variable is not available in this
site, so these links need converting to relative paths.

`{{base_path}}` stands for the root of that version's site, so the rest of the target
is a path within the version's directory. That makes most of them mechanically
fixable, and `report_links.py` splits them accordingly:

- **The resource exists at that path** — drop the variable and write an ordinary
  relative path. The replacement is exact, and this is the large majority.
- **It does not exist there** — leave the link alone. It may be served by a redirect,
  or the page may not have been migrated. Rewriting it would be a guess.

Redirects themselves belong either in a `redirects.yml` file or in a `redirects`
block inside `mkdocs.yml`.

## Applying a link plan

`report_links.py` proposes; `fix_links.py` is the only script that rewrites link
text. It applies one tier per run, verifies each rewrite against the disk first,
and refuses the tiers that need a person (`templated`, `stale`, `anchor`, `gone`).

Regenerate the plan between tiers: fixing one tier changes what the others resolve
to. Entries whose link text can no longer be found are skipped rather than guessed.

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
