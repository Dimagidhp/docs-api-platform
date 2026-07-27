# Rule: timeless language

Applies to Markdown documentation under `en/docs/`.

Document how the product works **right now**. Don't anchor text to a moment in time, and
don't assume the reader knows earlier or later versions.

## Banned words when describing product or feature capability

`as of this writing`, `currently`, `does not yet`, `eventually`, `existing`,
`future`, `in the future`, `latest`, `new`, `newer`, `now`, `old`, `older`,
`presently`, `at present`, `soon`.

| Write this | Not this |
|---|---|
| These subcommands let you interact with HTTP load balancing. | These **new** subcommands let you interact with HTTP load balancing. |
| The following command-line options aren't supported: | The following command-line options aren't **currently** supported: |
| The emulator supports the following filters: | The emulator **now** supports the following filters: |

## Related rules

- If you must use a word like "new", anchor it to a date or version number — for example,
  "The January 14, 2021 release includes a new resource panel."
- Never document future or unreleased features, even in passing. "We're currently
  considering adding MongoDB support" is exactly what to avoid.

## Exception

Inherently dated content — release notes, blog posts, press releases — may use these words
normally. This rule governs product and reference documentation.
