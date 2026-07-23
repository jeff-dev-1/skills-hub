---
name: wechat-editorial-layout
description: Create, review, repair, and safely update Chinese WeChat Official Account articles with Milos AI editorial structure, mobile-safe inline-CSS HTML, semantic process diagrams, official image upload handling, API read-back verification, and draft-only publication gates. Use for 微信公众号排版, 微信长文改稿, WeChat HTML conversion, cover/summary/process image layout, converting arrow-heavy workflow blocks into diagrams, producing LinkedIn visual variants of article diagrams, local image-path repair, desktop/mobile preview QA, official draft creation or update, and pre-draft validation.
---

# WeChat Editorial Layout

Turn a source-backed research package into a concise Chinese article that looks intentional on both desktop and mobile. Preserve facts, uncertainty, and the human review boundary; layout must clarify the argument rather than decorate it.

## Workflow

1. Read the source package, claims, evidence bindings, and review flags before editing prose.
2. Establish one thesis and three to five supporting judgments. Separate verified facts, vendor claims, and Milos AI inference.
3. Detect semantic visual candidates before writing HTML. A sequence with four or more stages (three or more transitions), a feedback loop, a branch/gate, a before/after comparison, or a layered control model is a diagram candidate, not a fenced code block. Keep actual code, configuration, commands, and logs as code.
4. Build the article in this reading order:
   - title and short digest;
   - one 16:9 executive-summary infographic;
   - thesis and why-now paragraph;
   - four judgment cards in a 2×2 table layout;
   - detailed company and technical signals;
   - four lifecycle or architecture layers, explicitly described as non-hierarchical;
   - implications, risks, and what to watch;
   - compact references.
5. Convert Markdown to WeChat-safe HTML using inline CSS and presentation tables where stable two-column layout is required.
6. Replace every semantic workflow block with a diagram asset. Use `scripts/render_process_diagram.py` for standard linear or feedback flows; use a custom SVG only when the process has branching, nested ownership, or topology that the standard renderer cannot express.
7. Build a local preview whose relative image paths resolve from the HTML file, then visually inspect every rendered image.
8. Upload every body image with the official WeChat image API and replace local or `asset://` placeholders before creating a draft.
9. Create a draft by default. When repairing an existing draft, update its stored `media_id`; do not create a duplicate.
10. Read the draft back through the official API and verify the remote artifact. Never infer public-publish approval from model output, feedback, or a successful draft write.
11. Render desktop and 390px mobile previews, inspect them visually, then run `scripts/validate_wechat_html.py` in the correct mode.

## Editorial Rules

- Write for technical managers, architects, founders, presales engineers, and senior practitioners.
- Lead with a specific judgment, not generic context or a meta reading guide.
- Do not include headings such as “这篇文章怎么看” unless the reading path itself is genuinely necessary.
- Use short paragraphs and concrete verbs. Avoid “值得注意的是”, “在当今时代”, repetitive summaries, and inflated AI prose.
- Do not present vendor positioning as an independently verified fact. Label vendor claims and analytical inference.
- Do not force ADC, gateway, or traffic implications into unrelated material.
- Keep important nuance in prose; the summary image is a map, not the entire report.
- Prefer four compact cards to long bullet walls. Prefer a lifecycle map to a pyramid when layers are not ranked.
- Do not place an editorial process with four or more stages inside `<pre>` merely because arrows make it easy to type. Convert it into numbered nodes with visible connectors and keep the detailed wording in prose.
- Use native Chinese punctuation and avoid literal translation from the LinkedIn version.

## Layout and Safety Rules

Read [references/layout-spec.md](references/layout-spec.md) before changing HTML, cover, or summary infographic generation.

Read [references/process-diagrams.md](references/process-diagrams.md) whenever the article contains `→`, `↓`, lifecycle stages, gates, feedback loops, before/after flows, or a LinkedIn diagram variant.

Read [references/draft-operations.md](references/draft-operations.md) before creating, updating, or reconciling a remote WeChat draft.

Hard requirements:

- no JavaScript, forms, iframe, local paths, data URLs, OAuth tokens, or secrets;
- no unreplaced `asset://` or `data-invalid-src` attributes in a remote draft;
- no overly wide tables; use `table-layout: fixed` for 2×2 cards;
- avoid native `ul`, `ol`, and `li` when WeChat rendering introduces stray markers; render list rows as paragraphs with explicit markers;
- all CSS must be inline for content sent to WeChat;
- body images must use hosted HTTPS URLs after upload;
- cover uses 2.35:1 and summary graphic uses 16:9;
- supporting diagrams may use another aspect ratio when their content needs it;
- keep text, arrows, captions, and card borders separated after WeChat downscaling;
- no arrow-dense semantic process may remain as a fenced code block in final HTML;
- public publishing remains a separate explicit action.

## Visual QA

Check the first screen first: the reader must understand the thesis from the title, digest, and summary graphic. Then inspect:

- no clipped or microscopic text in the summary graphic;
- no collision between card titles and bodies;
- no arrow touching a card border, no arrowhead hidden behind a card, and no caption overlapping a control row;
- equal-role cards use consistent widths and internal padding; the number/title row is centered as one group and every following line shares the card center guide;
- judgment grids use one outer presentation table only; each judgment is frameless with a single top accent strip and content-driven height, never a nested table inside a bordered card;
- card content is vertically centered as one text group; short copy must not cling to the top edge and leave a large empty lower half;
- cards stack or remain legible at 390px;
- headings have consistent spacing and alignment;
- references are visibly secondary but still readable;
- no unexplained blank area caused by a rejected local image URL.
- no workflow text squeezed into one long line; each process node has one short label, optional one-line detail, and a step number where sequence matters;
- every connector retains a visible shaft and a border gap after 640px downscaling; do not accept an arrow that only looks correct at SVG source size;
- every card uses a shared inner-padding box; number badges and titles align on one visual center line, the number/title row and every following line are centered horizontally, the full content group is centered vertically, and font size adapts to available width instead of filling the card aggressively;
- a WeChat process diagram remains legible at 390px and a LinkedIn variant uses its own 4:5 composition rather than a crop of the WeChat asset.

Do not accept a layout based only on HTML inspection. Render it and inspect the pixels. After a remote draft update, inspect the official read-back image or its CDN rendition as well; WeChat may resize images and normalize their URLs.

## Validation

Run:

```bash
uv run python skills/wechat-editorial-layout/scripts/validate_wechat_html.py \
  path/to/local-preview.html --mode local-preview

uv run python skills/wechat-editorial-layout/scripts/validate_wechat_html.py \
  path/to/remote-draft.html --mode remote-draft
```

Then run the repository lint and test suite before changing shared generation code.
