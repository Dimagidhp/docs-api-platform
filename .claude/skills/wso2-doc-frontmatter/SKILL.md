---
name: wso2-doc-frontmatter
description: Adds, repairs, and validates YAML frontmatter on WSO2 API Platform documentation pages, and checks the same pages for broken links and mechanical style-guide violations. Use this when migrating docs into wso2/docs-api-platform, when a page is missing frontmatter or has a wrong canonical_url/md_url/content_type/description, when checking a docs PR before merge, or when asked things like "add frontmatter to these pages", "why is this page's canonical URL wrong", "check this PR for broken links", "validate the metadata on all versions", or "audit the migrated docs". Handles the repo's multi-version layout (product/1.0.0/, product/1.1.0/, product/next/), where every version is published at a URL that includes its version segment. Also runs non-interactively as a CI gate, so keep output structured.
---

# WSO2 API Platform doc frontmatter and validation

Most of the work in validating these docs is mechanical, and mechanical work belongs in a script. The scripts here handle everything with one correct answer; your job is the part that needs reading the page and making a judgement — `description`, `content_type`, and `title`.

Do not hand-edit frontmatter field by field across many files. Run the scripts, then fill in only what they hand back to you.

## Requirements

Python 3.8+ and nothing else. The scripts parse frontmatter with a built-in
parser for the flat YAML subset used here, so they run on a bare `python3` with
no `pip install` — which matters on macOS, where Homebrew Python refuses
`pip install` under PEP 668. PyYAML is used automatically when present;
`fm_audit.py --selftest` proves the built-in parser agrees with it across every
page in the repo.

## The rules this enforces

The authoritative frontmatter spec is `.claude/rules/doc-frontmatter-and-metadata.md` **in the target repo**, not in this skill. Read it at the start of every run — it changes. `references/conventions.md` here records the mechanics that rule leaves implicit — version-to-URL mapping, quoting style, field order. Read that too.

If the repo rule and `references/conventions.md` disagree, the repo rule wins, and say so in your report.

## Workflow

### 1. Audit first, always

```bash
python3 scripts/fm_audit.py en/docs --json /tmp/fm.json
```

Read the output before changing anything. It reports per-code counts and detects the repo's versioned products automatically. Add `--files a.md b.md` to scope it to a PR's changed files, and `--gate` to make it exit non-zero on blocking issues.

The `--policy` flag decides how the version segment maps to a URL. `keep-all` (the default) keeps it for every version, latest release included, which is what the site does. The other two do not match the site. Never change the policy without saying so explicitly in your report; it rewrites URLs across hundreds of files.

### 2. Let the script fix what's mechanical

```bash
python3 scripts/fm_fix.py en/docs --dry-run                 # inspect first
python3 scripts/fm_fix.py en/docs --scaffold --apply \
    --worklist /tmp/work.json
```

This derives `canonical_url` and `md_url` from the path, normalises `last_updated` (from `git log` when it's missing or malformed), maps out-of-enum `content_type` values, lowercases `tags`, sets the standard `author`, and — with `--scaffold` — adds a whole frontmatter block to pages that have none, taking `title` from the H1.

The *script* never invents a `description` or `title` — but **you do, in step 3.** That split is the whole design: a regex guessing a description would produce something plausible and wrong that looks finished, so nobody revisits it. Reading the page and writing a real one is your job, and it is not optional. A page left with `description: "TODO"` is not done.

### 3. Fill in the judgement calls

`--worklist` writes the files still needing you, with the page's H1 and current values for context. For each one, **read the actual page** — headings and opening section at minimum — then decide:

- **`description`** — 90 to 155 characters, hard limit 158. Say what the reader can do or learn on this specific page, naming the actual feature or task. Present tense. No "This page describes…", no marketing adjectives, and none of the qualitative words the style guide bans ("easy", "simple", "quick"). Match the voice of existing good examples in the repo rather than inventing one.
  - When a description is merely too long, **rewrite it — never truncate it.** A sentence cut at 158 characters reads as broken.
- **`content_type`** — exactly one of `how-to`, `tutorial`, `reference`, `concept`, `explanation`, `troubleshooting`, `faq`, `release-notes`, `changelog`, `quickstart`. Pick by what the page *is*: numbered task steps → `how-to`; end-to-end learning walkthrough → `tutorial`; parameter and field tables → `reference`; explains an idea without steps → `concept`; diagnosing failures → `troubleshooting`. Section landing pages that are mostly link lists are `concept` — this is the settled default for this repo, so apply it without asking. `overview` is not a valid value; `CT_ALIASES` in `fm_lib.py` maps it to the closest valid type.
- **`title`** — sentence case, under 60 characters. Only the first word plus genuine proper nouns and acronyms are capitalised: "AI Gateway", "API Platform", "Developer Portal", "Gateway Controller" stay capitalised; "Analytics", "Configuration", "Policy" do not, unless part of a product name.

Write your decisions as a JSON map and hand them back to the script — don't edit files by hand:

```bash
cat > /tmp/filled.json <<'EOF'
{"cloud/api-platform-gateway/troubleshooting.md": {
   "title": "Troubleshoot the Self-Hosted Gateway",
   "description": "Diagnose and resolve connection, registration, startup, TLS, policy, and routing failures on the API Platform Self-Hosted Gateway.",
   "content_type": "troubleshooting"}}
EOF
python3 scripts/fm_fix.py en/docs --fill /tmp/filled.json --apply
```

Batch these — one `filled.json` for all outstanding files, not one run per file.

### 4. Write the broken-link fix plan to its own file

Link breakage is a *separate deliverable* from frontmatter. Never fold it into the
chat reply or into the frontmatter report — it is a work queue someone else will
pick up, so it belongs in a file that can be committed, reviewed, and assigned.

```bash
python3 scripts/report_links.py en/docs --scope <scope> \
    --out BROKEN-LINKS-<scope>.md --json BROKEN-LINKS-<scope>.json
```

Always pass `--scope` when working one version, product, or section, and name the
output after that scope. A single repo-wide report goes stale immediately and nobody
can tell which parts are theirs.

The report classifies every finding by **cause**, because the causes have
completely different fixes and completely different risk:

| Tier name | Cause | Fix | Applied by `fix_links.py`? |
|---|---|---|---|
| `templated_fixable` | `{{base_path}}` and the resource exists | Exact rewrite to a relative path | Yes |
| `malformed` | Malformed link syntax | Exact rewrite. No judgement. | Yes |
| `depth` | Wrong relative depth | Exact rewrite. No judgement. | Yes |
| `renamed` | Renamed or moved target | A file of that name exists elsewhere; proposed, with confidence | Yes, `high` confidence only by default |
| `templated` | `{{base_path}}` and it does not exist | **Leave alone.** May be served by a redirect | No — refused |
| `stale` | Pre-migration domain | Needs the new equivalent page | No — refused |
| `anchor` | Missing anchor | Heading was reworded | No — refused |
| `gone` | No target anywhere | Was it dropped, missed, or merged? | No — refused |

The report also ends with a **ready-to-paste prompt for an AI coding agent**, for
when someone wants to hand the work off rather than run step 5 here.

Two rules the reporter enforces, and you must not work around:

- **`{{base_path}}` is version-root-relative.** Where the resource exists at that
  path, convert the link to a relative path and drop the variable — that is an exact
  fix. Where it does not exist, leave it: it may be served by a redirect.
- **Never propose a target in a different version.** If a page under one version
  links to something missing, the replacement must live under that same version. A
  cross-version link silently sends a reader to a different release.
`stale`, `anchor` and `gone` need information that is not in the repo, and an agent
asked to fix them produces confident links to the wrong pages — worse than a
visibly broken link, because a plausible wrong link never gets re-checked.

When you report back, give the tier counts and say plainly how many need a human. A
raw total is alarming and useless on its own; "N have an exact fix, M need a
decision" is what someone can act on.

### 5. Fix the links one tier at a time, and ask before each tier

The report is a plan, not a change. `scripts/fix_links.py` is the only thing that
applies it, and it takes **one tier per run**:

```bash
# show what this tier would do — nothing is written
python3 scripts/fix_links.py en/docs --plan BROKEN-LINKS-<scope>.json --tier malformed
# apply it, and record what changed
python3 scripts/fix_links.py en/docs --plan BROKEN-LINKS-<scope>.json --tier malformed \
    --apply --journal /tmp/fixed-malformed.json
```

Work the tiers in this order, easiest and safest first:

1. `malformed` — link syntax
2. `depth` — wrong number of `../`
3. `renamed` — target moved (`high` confidence only; `--min-confidence` widens it)
4. `templated_fixable` — if the scope has any

**The rule for each tier: dry-run it, show the person a sample, tell them how many
would change and how many the verifier refused, and wait for an explicit yes before
`--apply`.** Never chain tiers in one go, and never apply a tier the person has not
seen. Their answer for one tier is not their answer for the next — `depth` is
arithmetic, but `renamed` is a proposal, and someone may want every one of those
eyeballed.

After each applied tier, report what actually changed and stop:

```
tier `depth`: 667 verified, 3 refused, 132 files changed, 667 links rewritten.
Refused: 3 where the anchor no longer exists. Next tier is `renamed` (448, 406
verified). Apply it?
```

**Regenerate the plan between tiers.** Fixing one tier changes what the others
resolve to, so a plan written before the last tier was applied is stale — and
`fix_links.py` will skip entries whose link text it can no longer find rather than
guess.

Two things the script does that you should not work around:

- **It verifies every rewrite against the disk before writing anything.** A
  proposal whose target does not resolve, or whose anchor does not exist on the new
  page, is refused rather than applied. Those refusals are the useful output — they
  are the cases where the report was optimistic.
- **It refuses `templated`, `stale`, `anchor` and `gone` outright.** Those need
  information that is not in the repo. Do not hand-apply them in bulk to save
  time; a plausible wrong link is worse than a visibly broken one, because nobody
  re-checks it.

Finish by re-running the link checker and quoting the before/after, since that —
not the number of files touched — is what says the fix worked.

### 6. Re-audit, and verify against a real build

```bash
python3 scripts/fm_audit.py en/docs --gate
python3 scripts/check_redirects.py en/mkdocs.yml en/docs --gate
python3 scripts/check_links.py en/docs
python3 scripts/check_style.py en/docs
```

Re-auditing is not optional: it's the only thing that proves the fix worked rather than moved the problem.

Where the repo can be built, `mkdocs build` is the authoritative check on links — the link checker is calibrated against it and finds a superset of what it reports. If you have the dependencies, run it and reconcile any difference rather than assuming the script is right.

## The other scripts

`scripts/fix_links.py` applies one tier of a `report_links.py` plan. Dry run by
default; `--apply` writes; `--journal` records every rewrite so a tier can be
reviewed or undone. It is the only script here that edits link text.

`scripts/check_redirects.py` validates `redirect_maps` in `mkdocs.yml` — targets exist, no source shadowed by a real file, no chains (the plugin doesn't follow them), no map left pointing at a superseded version after a version bump.

`CANONICAL_UNREACHABLE` only fires under `--policy latest-only`. Under the default `keep-all` a canonical is a versioned path, so it cannot depend on a redirect existing.

`scripts/check_links.py` resolves every relative link, image, and anchor against what's on disk, and flags links still pointing at a pre-migration location (the list is `LEGACY_DOMAINS` in `fm_lib.py`). It catches everything `mkdocs build` warns about plus two classes mkdocs stays silent on: bare directory links to a directory with no `index.md`/`README.md`, and directory links to a path that doesn't exist at all.

Note what `check_links.py` does **not** do: it only resolves links whose target is inside the repo. It cannot tell you whether a page is reachable at its own published URL — that is `check_redirects.py`'s job. "No broken links" and "every canonical URL resolves" are two different claims, and passing the first says nothing about the second.

`scripts/check_style.py` covers only the *mechanically decidable* part of the style guide — heading case, banned qualitative and time-bound words, en dashes, non-descriptive link text. It is not a replacement for reading the prose. Two things to know before you trust its output:

- **Heading case depends on its allowlist.** `PROPER` and `PROPER_PHRASES` in the script hold the product names that legitimately stay capitalised, and essentially every false positive traces to a name the list doesn't know yet. When you hit one, **add the name to `PROPER_PHRASES` rather than suppressing the finding** — that is how the checker improves. Headings with exactly one unexpected capital are reported separately as `HEADING_CASE_SINGLE_WORD` at lower severity, because a lone capital is usually an unknown product name.
- **Banned-word rules need your judgement on scope.** The style guide bans "new" and "latest" *"when describing product or feature capabilities."* "Generate a **new** token" is fine; "these **new** subcommands" is a violation. The script cannot tell these apart and will flag both. Read the surrounding sentence before reporting a `TIMELESS` or `QUALITATIVE` hit.

Some findings are established house conventions rather than slips. When a single pattern recurs across hundreds of pages, report it **once** as a convention question rather than as hundreds of findings. The style guide says outright that it "contains guidelines, not draconian rules", and a checker that ignores that stops being used.

## Reporting

Lead with the counts and what you changed. Then group findings by code, not by file — a hundred identical `canonical_url` corrections are one line of report, not a hundred. Show one representative diff per group.

Separate three things clearly, because they need different responses:

1. **Fixed automatically** — what the scripts changed, by code and count.
2. **Needs a human decision** — genuine ambiguity or repo-wide convention questions. State the options and your recommendation; don't silently pick one.
3. **Still outstanding** — what neither the scripts nor you could resolve, and why.

Never report a count without saying whether it counts occurrences or affected files. Those differ by an order of magnitude, and conflating them makes the report useless.

When running in CI, end with a single machine-readable line so a build step can grep it:

```
<!-- wso2-doc-frontmatter: STATUS=FAIL files=<N> blocking=<N> should_fix=<N> -->
```

`STATUS=FAIL` only when there is at least one blocking issue. Because blocking counts drive a merge gate, do not inflate severity — a should-fix reported as blocking is how a gate loses its credibility.
