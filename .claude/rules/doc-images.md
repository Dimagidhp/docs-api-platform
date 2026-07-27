# Rule: images, diagrams, and figures

Applies to Markdown documentation under `en/docs/` and image assets under
`en/docs/assets/img/`.

## When to use an image

- Only when it gives a visual explanation that's genuinely hard to express in words.
- Never use an image to show text, code samples, or terminal output — use real text.
- Everything an image conveys must also appear in the **body text**, not only in alt text.
  Alt text is not a substitute: not everyone processes images the same way, and non-visual
  tools generally can't use image-only information.

## File formats

- Prefer **SVG** so images stay sharp when zoomed. Use PNG only when SVG isn't available.
  Diagrams in particular should be SVG.
- Never use transparent backgrounds.
- No animated GIFs — use an efficient video format such as MP4.
- No image maps: they cause accessibility problems and scale poorly on mobile. List text
  references below the image instead.

## Screenshots and PII

- Crop tightly to the relevant UI. Keep visual consistency across a document set — same OS,
  same window decoration.
- Never include personally identifying information. Cover PII with a solid-color overlay at
  100% opacity — never a blur or mosaic, both of which can be reversed. Flatten layers on
  export.

## Text around images

- Introduce every image with a complete, standalone sentence. End it with a colon if the
  image follows immediately, or a period if a note paragraph separates them.
- **Alt text:** up to 155 characters, sentence case, no "Image of" or "Photo of" prefix.
  Use an empty `alt=""` for purely decorative images, or screenshots that only mirror the
  surrounding text steps.
- Captions are optional. If used, write a complete sentence with end punctuation, formatted
  "Figure 1. Description."
- Never refer to an image by position ("the image above"). Use its figure number, or repeat
  the relevant content.

## High-resolution images

Use `srcset` alongside the standard `src`. The 2x image must be exactly double the 1x's
width and height. Set `width` in CSS pixels and don't set an explicit `height`. Point `src`
at the 1x image for older browsers, and never upscale a 1x image to fake a 2x.

## Layout

Trust the system. Don't hand-adjust margins or alignment with inline `style` attributes.
Don't center images or shrink them unnecessarily, and don't let them exceed the width of the
main content column.
