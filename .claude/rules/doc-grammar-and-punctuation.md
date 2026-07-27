# Rule: grammar and punctuation

Applies to Markdown documentation under `en/docs/`.

Spelling and punctuation follow **standard American English**. Capitalization follows
sentence case, per the Google developer documentation style guide.

## Contractions

- Use common two-word contractions: `you're`, `don't`, `there's`.
- Prefer negation contractions — `isn't`, `don't`, `can't`. A reader scanning quickly can
  miss the word "not", but rarely misreads "don't" as "do".
- Never invent nonstandard contractions (`guides're`) or use three-word contractions
  (`mightn't've`).

## Conditional clauses come first

State the circumstance before the instruction, so a reader it doesn't apply to can skip it.
Write "If the program runs slowly, try the `--perf` flag", not the reverse.

## Commas

- Use the Oxford comma before the final "and" or "or" in a list.
- Put a comma between a conditional clause and its consequence.
- Enclose parenthetical asides in a pair of commas.
- Never join two independent clauses with a comma. "Samantha is a wonderful coder, she
  writes abundant tests" is wrong — use a period.

## Semicolons

Use one only to join two grammatically complete, closely related sentences that would still
make sense if flipped. Put a comma immediately after a transition word that follows a
semicolon ("...; therefore, write unit tests"). Inside an embedded list use commas, not
semicolons — or better, convert it to bullets.

## Dashes and hyphens

- **Em dash (—):** no space before or after. Use in pairs to set off a digression:
  "Protocol Buffers—often nicknamed protobufs—encode structured data efficiently."
- **En dash (–):** never use one. Use a hyphen or the word "to".
- **Hyphens:** use inside compound terms (`self-attention`, `floating-point`, `on-prem`).

## Colons

Use a colon to introduce a formal list or table only when the list doesn't already read as
the sentence's own object. "Consider the following languages: Python, Java, and C++" takes a
colon; "My favorite languages are Python, Java, and C++" does not.

## Parentheses

Use sparingly, for minor or non-critical asides only. If the information is essential, don't
put it in parentheses. The period goes inside the closing parenthesis only when the whole
sentence sits inside the parentheses; otherwise it goes outside.

## Symbols

Spell out the text equivalent instead of using a symbol — symbols confuse readers and aren't
always read correctly by screen readers.

| Write this | Not this |
|---|---|
| Begin the line with a forward slash ( / ). | Begin the line with a forward slash, /. |
| It can take about 5 minutes for your host to appear. | It can take ~5 minutes for your host to appear. |

Spell out "and", "plus", "minus", and "about" rather than using `&`, `+`, `-`, or `~`.

**Symbols are fine as-is** in: grammatical punctuation; string literals, code, command
syntax, URLs, and file paths; keyboard shortcuts (`Ctrl+Alt+Del`); angle-bracket
placeholders (`host=<your_hostname>`); a percent sign after a number (`10%`); and
mathematical equations.
