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

## Process diagrams

- Treat four or more semantic stages, any feedback loop, or any policy branch as a visual relationship, not as code typography.
- Never ship an arrow-heavy editorial workflow inside `<pre>` when the arrows express meaning rather than executable syntax.
- Use no more than three process columns in a WeChat body image. Wrap longer flows into numbered serpentine rows or a vertical sequence.
- At the 1600px SVG design width, start primary node labels at 36–40px and secondary text at 24–28px. Treat these as readable defaults, not targets to maximize; fit downward when a label would crowd its card.
- Limit each node to two label lines and one short detail line. Move explanations back into prose.
- Use 72–96px outside margins and 24–36px card padding. Reserve a 90–100px connector lane between card borders when the lane contains an arrowhead and card shadows.
- Prefer an explicit connector group—one short line ending at the base of a separate arrowhead polygon—over an SVG Marker. Do not draw the shaft underneath or beyond the arrowhead.
- Center the entire connector inside its lane. At the 1600px design size, keep the connector at least 20px from both card borders. After 640px downscaling, both ends must retain a visible gap.
- Give cards 28–32px padding on all sides. Align the number badge and primary label to the same visual center line.
- Center the number badge and title as one header row. Center every detail or wrapped line on the same card center guide; do not merely reuse the title's left coordinate.
- Compute the actual width of the number/title row before centering it. Equal fixed padding alone is insufficient when short copy leaves much more visible whitespace on one side.
- Treat the number/title row and detail row as one content group. Center that group vertically inside the shared padding box instead of pinning one row to the top and one to the bottom.
- Start primary labels at 36–40px rather than maximizing their size. Shrink to fit the available width before wrapping; never let text approach the right border. Keep detail text at 24–28px.
- Represent a feedback loop with one clearly separated return path. Do not cross the forward path or route the arrow through text.
- Generate a dedicated LinkedIn 4:5 variant; do not crop a wide WeChat diagram into a portrait asset.

See [process-diagrams.md](process-diagrams.md) for diagram selection, channel profiles, and the standard renderer.

## Diagram collision safety

- Give every card a shared 28–32px inner-padding box. Title and detail text must remain inside that box on all four sides.
- Keep connector arrows visibly outside card borders; reserve at least 20px clear space at each end.
- Reject a connector whose full line-and-head geometry is longer than its visible lane. A technically correct path can still look clipped when any part extends behind a card.
- Draw connectors after card shadows in SVG document order. Keep paths inside their reserved lanes so raising the connector layer reveals the shaft without crossing card content.
- Reject a card whose title, number badge, or detail line breaks the common inner-padding box.
- Reject a card whose title and following lines use inconsistent horizontal alignment modes.
- Reject a card when the visible whitespace before and after any centered text row is materially unequal.
- Reject a card whose short content clings to the top edge and leaves a visibly empty lower half.
- Use consistent widths for cards that have the same semantic role.
- Keep one caption in one location. Do not place a panel caption over the last control or data row.
- Render the final PNG and inspect it after downscaling. Source-coordinate correctness does not prove pixel-level readability.
- After a draft write, inspect the official CDN rendition because WeChat can resize or recompress the upload.

## Judgment cards

- Four cards in a 2×2 presentation table.
- Each card: one short title and one sentence.
- Fixed table layout, 50% cells, 6px spacing.
- Use a single top color strip as the only card boundary. Remove side/bottom borders, inner frames, and nested layout tables.
- Let card height follow its content. Do not add a fixed-height box merely to make four short judgments visually equal.
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
