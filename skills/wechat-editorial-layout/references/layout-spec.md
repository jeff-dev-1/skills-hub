# Milos AI WeChat Layout Specification

## Brand and hierarchy

- Primary dark navy: `#172B6B` or the established Milos navy.
- Violet accent: `#5B2DCC`.
- Cyan accent: `#42D5E8`.
- Teal accent: `#138178`.
- Body text: near-black navy; secondary text: muted slate.
- Use color to distinguish roles or stages, not to imply unsupported ranking.

## Article canvas

- Maximum reading width: approximately 677px in local preview.
- Desktop keeps a centered narrow reading column.
- Mobile must remain readable at 390px without horizontal scrolling.
- Main body line height: 1.75–1.9.
- Short paragraph rhythm: 8–14px bottom margin.
- Section heading: strong left alignment with a small cyan rule or accent, not multiple decorative banners.

## Summary infographic

- Canvas: 1600×900 PNG (16:9).
- Use one sentence thesis and at most four sections.
- Recommended structure: priority signals, control/architecture chain, lifecycle map, four judgments.
- Do not use dense citations, tiny vendor logos, or long paragraphs.
- Every factual signal in the graphic must be supported in the article body.
- Add an accessible `alt` description in the article.

Supporting diagrams do not have to be 16:9. Choose the shortest canvas that preserves a readable system model without compressing text.

## Diagram collision safety

- Give card body text at least 20px internal horizontal padding at the SVG design size.
- Keep connector arrows visibly outside card borders; reserve at least 12px clear space at each end.
- Use consistent widths for cards that have the same semantic role.
- Keep one caption in one location. Do not place a panel caption over the last control or data row.
- Render the final PNG and inspect it after downscaling. Source-coordinate correctness does not prove pixel-level readability.
- After a draft write, inspect the official CDN rendition because WeChat can resize or recompress the upload.

## Judgment cards

- Four cards in a 2×2 presentation table.
- Each card: one short title and one sentence.
- Fixed table layout, 50% cells, 6px spacing.
- Do not use the cards to repeat the thesis verbatim.

## Lifecycle map

- Use four stages: design, build, control, runtime when the report supports them.
- State explicitly that the stages are an engineering lifecycle, not a value ranking.
- Use compact cards rather than a pyramid unless evidence supports hierarchy.

## References

- Place at the end.
- Use smaller font and tighter line height than body copy, but keep tap targets usable.
- Prefer numbered source title + publisher + URL.
- Do not paste full copyrighted article text.

## Image handling

Local preview and remote draft are distinct artifacts:

1. Production HTML may contain an `asset://...` placeholder that sanitization moves to `data-invalid-src`.
2. Local preview may replace that placeholder with a local SVG solely for visual QA.
3. Before draft creation, upload PNG through the official API and replace the placeholder with the returned HTTPS URL.
4. Reject the draft if any local path, `asset://`, or `data-invalid-src` remains.

For ordinary relative paths, resolve from the HTML file's directory. A path such as `content/assets/...` is incorrect when the preview file already lives below `content/drafts/...`; use the actual relative traversal and validate that the target exists.

## Publication boundary

- Default output is review draft.
- Successful validation does not equal approval.
- Successful draft creation does not authorize public publication.
- Read back the draft through the official API and verify title, digest, body image URLs, absence of local paths, and expected content blocks.
