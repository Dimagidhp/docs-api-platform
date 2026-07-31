# Rule: formatting and typography

## Headings

- **Sentence case, always:** only the first word plus proper nouns and acronyms. "Configure rate limiting", not "Configure Rate Limiting".
- Descriptive and unique, so a reader can navigate by heading alone.
- Maintain logical order and never skip a heading level — an H3 belongs only under an H2.
- **After a colon, semicolon, or hyphen:** capitalize only the first word, then continue lowercase — `Example 1: Basic object validation`, `Optional - Second HTTPRoute`. Don't re-capitalize every word after the mark, and don't lowercase the word right after it.

## Code font (backticks)

- Inline code, user input, code samples and blocks.
- Filenames, class names, method names, HTTP status codes, console output, placeholders.
- *Italic code font* for a placeholder the reader must replace in a syntax or command example.
- Never change capitalization inside code font to satisfy a prose rule — `RestApi`, `APIGateway`, and `HTTPRoute` are case-sensitive literals.

## Emphasis and lists

- **Bold:** every UI element name a reader interacts with — panes, buttons, menu items, fields — plus run-in headings and the lead-in word of a notice. An unbolded UI element name is an error. Not for emphasis in body text.
- *Italics:* two uses only — first mention of a term you define immediately after (not bold, not quotation marks), and words-as-words ("Use the word *and* instead").
- Numbered lists when order matters, bulleted otherwise, description lists for pairs of related data.

## Other

- **Keyboard input:** the `<kbd>` element — "Press <kbd>Control+C</kbd>."
- **Dates:** months and days spelled out in full with a four-digit year. If a numeric format is unavoidable, `YYYY-MM-DD`.
- **Link text:** short, unique, descriptive, giving context for the destination. Rework the sentence to fit it. Never "click here", never a bare URL.
