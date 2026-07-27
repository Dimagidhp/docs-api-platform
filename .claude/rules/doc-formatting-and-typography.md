# Rule: formatting and typography

Applies to Markdown documentation under `en/docs/`.

## Headings and titles

- **Sentence case, always.** Capitalize only the first word plus proper nouns and acronyms.
  Write "Configure rate limiting", not "Configure Rate Limiting".
- Make headings descriptive and unique, so a reader can navigate by heading alone.
- **Headings split by a colon, semicolon, or hyphen/dash:** capitalize only the first word
  after the punctuation mark, then continue in lowercase — as if starting a new clause.
  `Example 1: Basic object validation` and `Optional - Second HTTPRoute` are both correct.
  Don't re-capitalize every word after the mark, and don't lowercase the word right after it.

## Code font

- Use code font for inline code, user input, and code samples or blocks.
- Also use it for filenames, class names, method names, HTTP status codes, console output,
  and placeholders.
- Use *italic code font* to mark a placeholder the reader must replace inside a syntax or
  command example.
- In Markdown, use backticks.
- Never change the capitalization of anything inside code font to satisfy a prose rule —
  identifiers like `RestApi`, `APIGateway`, and `HTTPRoute` are case-sensitive literals.

## Bold and italics

- **Bold:** only for UI element names and run-in headings, including the lead-in word of a
  notice or callout. Not for emphasis in body text.
- *Italics:* use sparingly, for exactly two things — the first mention of a term you define
  immediately afterwards (don't use bold or quotation marks for this), and words-as-words
  ("Use the word *and* instead").

## Lists

- Numbered lists for sequences where order matters.
- Bulleted lists for everything else.
- Description lists for pairs of related data.

## Other

- **Keyboard input:** use the `<kbd>` element — "Press <kbd>Control+C</kbd>."
- **Dates and times:** spell out months and days in full, give the full four-digit year. If
  a numeric format is unavoidable, use `YYYY-MM-DD` with hyphens.
- **Link text:** short, unique, descriptive phrases that give context for the destination.
  Rework the sentence if needed to fit good link text in. Never "click here" and never a
  bare URL.
