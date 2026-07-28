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
- SVG `<text>` does not wrap automatically. In a custom SVG, split every variable-length card label or detail into explicit lines, and give each line a `data-max-width` equal to the card's usable inner width plus a `data-font-size` matching its rendered size.
- Represent a feedback loop with one clearly separated return path. Do not cross the forward path or route the arrow through text.
- Generate a dedicated LinkedIn 4:5 variant; do not crop a wide WeChat diagram into a portrait asset.

See [process-diagrams.md](process-diagrams.md) for diagram selection, channel profiles, and the standard renderer.

## Diagram collision safety

- Give every card a shared 28–32px inner-padding box. Title and detail text must remain inside that box on all four sides.
- Keep connector arrows visibly outside card borders; reserve at least 20px clear space at each end.
- Reject a connector whose full line-and-head geometry is longer than its visible lane. A technically correct path can still look clipped when any part extends behind a card.
- Draw connectors after card shadows in SVG document order. Keep paths inside their reserved lanes so raising the connector layer reveals the shaft without crossing card content.
- Reject a card whose title, number badge, or detail line breaks the common inner-padding box.
- Run `validate_svg_text_fit.py --require-contract` for custom SVGs. A clean outer canvas is insufficient when text crosses an internal card border.
- Reject a card whose title and following lines use inconsistent horizontal alignment modes.
- For comparison cards, use one card center guide for headings, short labels, explanations, and metric values. A checklist may keep left-aligned rows, but compute its widest row and center the checklist group inside the card instead of assigning an arbitrary left inset.
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

## Assessment matrices

- Do not send Markdown pipe tables through the generic CommonMark converter.
- A factual table may remain a table only when it has at most two concise columns and four short rows.
- When either column contains sentence-length assessments, render each entry as one full-width stacked row with label, explicit maturity/status badge, and one or two short sentences.
- Keep the label and status on the first line. Do not squeeze a long English dimension name into a narrow left column; use Chinese as the primary label and optional English as secondary text.
- Keep assessment text as HTML, not a screenshot, so it remains selectable and accessible.
- Group more than six rows under two to four meaningful subheadings instead of producing one long undifferentiated wall.

## Capability grids

- Treat `Harness + Identity + Isolation + Evaluation + Audit + Secure Execution` as composition, not sequence.
- Use an unnumbered 2×2 or 2×3 presentation grid for four to six equal-role capabilities.
- Give each card one short capability name and one short responsibility line.
- Do not use arrows, step badges, or ranking colors unless the evidence defines an order, transition, or priority.
- Convert four or more additive `+ item` Markdown lines before the generic list normalizer turns them into bullet rows.

## Diagnostic rankings

- Convert two or more root-cause candidates with probabilities into full-width stacked diagnostic cards.
- Keep the candidate label and probability in one header row. Do not present probability as model confidence unless the source explicitly defines it that way.
- Preserve evidence polarity with separate supporting, opposing, and missing-evidence rows. Do not merge them into one undifferentiated list.
- Order candidates by the supplied probability or score, but do not invent missing probability mass or imply that the candidates are exhaustive.
- Mark example probabilities as illustrative. Production probabilities require calibration, time scope, model version, and traceable evidence.
- Keep evidence as selectable HTML; use an image only when the ranking itself is part of a larger architecture visual.

## Layered reasoning architectures

- Use a vertical stack for five to eight ordered, text-rich layers such as global prior → local calibration → incident evidence → prediction → investigation → governed action.
- Give each stage one title and at most two compact detail lines. Put long source inventories and caveats back into prose.
- Place transition labels in the connector lane, never inside a source or destination card.
- Use `render_layered_architecture.py` for this grammar. Reserve the standard serpentine renderer for shorter labels and more spatial flows.
- Do not use a vertical stack when the layers are additive peers; use a capability grid instead.

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
