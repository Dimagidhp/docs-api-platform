# Rule: plain language and clarity

Applies to Markdown documentation under `en/docs/`.

## Words

- Avoid obscure words and company- or profession-specific jargon.
- If you must use WSO2-specific terminology: link to the term at first use if it exists in a
  root-level glossary. If no glossary exists, add a "Glossary" section to the document and
  link to it from first use.
- Define every acronym and initialism at first use. Repeat the definition later if it helps.
- Avoid ambiguous pronoun references — make it obvious what "it" or "this" refers to.
- Use the same term for the same thing across topics. Don't alternate between synonyms.

## Sentences

- Use simple, complete sentences. The same point usually fits in 20 words instead of 50.
- Aim for fewer than 26 words per sentence. Avoid complex-compound sentences.
- Put the paragraph's key information in the first sentence.
- Aim for no more than 5 sentences per paragraph. Break up walls of text with paragraphs,
  headings, and lists.
- Use parallel structure across similar list items.

## Use indicating nouns

Name the element or object explicitly rather than leaning on a bare verb or identifier.

| Write this | Not this |
|---|---|
| Submit a `GET` request. | Do a `GET`. |
| Use the `get()` function to extract nested values from the `attributes` field. | `get()` extracts nested values from `attributes`. |
| The auth header is included by default, unless the `noAuth` flag is set. | Auth header is included by default, unless `noAuth` is set. |

## Tables

- Introduce every table with meaningful text before it — not all screen readers announce
  tables.
- Apply header formatting to the first row and first column only.
- Avoid tables in the middle of a numbered procedure.
- Don't use a table unless it is genuinely the best format; tables are hard for screen
  readers.
- Never convey new information through an image or symbol alone inside a table. Always pair
  it with a descriptive alt attribute.
