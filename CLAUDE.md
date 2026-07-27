# WSO2 API Platform documentation — project instructions

This repository contains the WSO2 API Platform documentation (MkDocs, sources under `en/docs/`).

When you write, edit, or review any Markdown file under `en/docs/`, follow the documentation
style rules imported below. They are a condensed, checkable form of WSO2's official
"WSO2 API Platform documentation style guide."

## Documentation style rules

@.claude/rules/doc-voice-and-tone.md
@.claude/rules/doc-timeless-language.md
@.claude/rules/doc-plain-language.md
@.claude/rules/doc-grammar-and-punctuation.md
@.claude/rules/doc-formatting-and-typography.md
@.claude/rules/doc-images.md

## How to apply these rules

Two things govern how strictly to enforce them, and both come from the source guide itself:

1. The guide states: *"This guide contains guidelines, not draconian rules. There might be
   scenarios where it makes sense to depart from our guidelines to make the documentation
   better. When you depart from this guide, be consistent throughout your document."* So a
   deliberate, internally consistent departure that improves clarity is acceptable. Raise it
   as a low-severity note, and only push back firmly when the departure is inconsistent
   within the same document or genuinely hurts clarity.

2. The guide states: *"This style guide isn't comprehensive."* If something looks wrong but
   is not covered by a rule below, say so plainly — "not covered by the WSO2 guide" — rather
   than inventing a WSO2-specific rule. The guide's own stated fallback is the
   [Google developer documentation style guide](https://developers.google.com/style). Never
   present a Google-only convention as if it were an official WSO2 rule.

The "Writing for AI" guidance is marked work-in-progress in the source document, so treat
those points as directional suggestions rather than firm rules.

## Related

For a full structured review with severity levels, rule citations, and a per-issue report
format, use the `wso2-doc-style-checker` skill if it is installed. These rules and that
skill read from the same source guide, so they should never disagree — if they do, the
source PDF is the tiebreaker.
