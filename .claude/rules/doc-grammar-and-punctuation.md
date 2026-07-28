# Rule: grammar and punctuation

Standard American English. Sentence case capitalization.

- **Contractions:** use common two-word ones (`you're`, `don't`, `there's`), and prefer negation contractions, since a reader scanning quickly can miss "not". Never nonstandard (`guides're`) or three-word (`mightn't've`).
- **Conditional clause first:** "If the program runs slowly, try the `--perf` flag" — not the reverse, so readers can skip the sentence when the condition doesn't apply to them.
- **Commas:** Oxford comma before the final "and" or "or"; comma between a conditional clause and its consequence; parenthetical asides in a pair of commas. Never join two independent clauses with a comma — use a period.
- **Semicolons:** only to join two complete, closely related sentences that would still make sense flipped. Comma after a transition word following one ("...; therefore, write unit tests"). In an embedded list use commas, or convert to bullets.
- **Em dash (—):** no space either side; use pairs to set off a digression. **En dash (–):** never — use a hyphen or "to". **Hyphens:** inside compound terms (`floating-point`, `on-prem`).
- **Colons:** introduce a formal list or table only when the list isn't already the sentence's own object. "Consider the following languages: Python, Java, and C++" takes one; "My favorite languages are Python, Java, and C++" doesn't.
- **Parentheses:** sparingly, for minor asides. Essential information doesn't belong in them. Period inside only when the whole sentence is parenthesized.

## Symbols

Spell out the text equivalent — "and", "plus", "minus", "about" — instead of `&`, `+`, `-`, `~`. Screen readers don't always read symbols correctly.

- "Begin the line with a forward slash ( / )." — not "Begin the line with a forward slash, /."
- "It can take about 5 minutes." — not "It can take ~5 minutes."

**Fine as-is:** grammatical punctuation; code, string literals, command syntax, URLs, file paths; keyboard shortcuts (`Ctrl+Alt+Del`); angle-bracket placeholders (`host=<your_hostname>`); a percent sign after a number (`10%`); mathematical equations.
