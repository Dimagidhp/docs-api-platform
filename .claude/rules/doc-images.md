# Rule: images, diagrams, figures

Also covers image assets under `en/docs/assets/img/`.

## When to use one

- Only for a visual explanation that's genuinely hard to express in words.
- Never to show text, code samples, or terminal output — use real text.
- Everything an image conveys must also appear in the body text, not only in alt text. Non-visual tools generally can't use image-only information.

## Files

- SVG preferred, especially for diagrams; PNG only when SVG isn't available. No transparent backgrounds.
- No animated GIFs — use an efficient video format such as MP4. No image maps; list text references below the image.
- **Screenshots:** crop tightly to the relevant UI, and keep one OS and window decoration across a document set.
- **PII:** never include it. Cover it with a solid-color overlay at 100% opacity — never a blur or mosaic, both of which can be reversed. Flatten layers on export.

## Text around images

- Introduce every image with a complete, standalone sentence: colon if the image follows immediately, period if a note paragraph separates them.
- **Alt text:** up to 155 characters, sentence case, no "Image of" or "Photo of" prefix. Empty `alt=""` for decorative images and screenshots that only mirror the steps.
- Captions are optional; if used, write a complete sentence: "Figure 1. Description."
- Never refer to an image by position ("the image above") — use its figure number or repeat the relevant content.

## Layout

- **High-resolution:** use `srcset` alongside `src`. The 2x image must be exactly double the 1x width and height. Set `width` in CSS pixels with no explicit `height`. Point `src` at the 1x. Never upscale a 1x to fake a 2x.
- No inline `style` margin or alignment tweaks. Don't center or shrink images unnecessarily, and don't let them exceed the main content column width.
