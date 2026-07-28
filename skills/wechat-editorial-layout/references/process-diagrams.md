# Editorial Process Diagrams

## Selection rule

Convert prose or a fenced block into a diagram when it contains any of these:

- four or more ordered stages;
- a return path or learning loop;
- a decision, policy gate, approval, or pass/fail branch;
- a before/after architecture change;
- three or more layers with named responsibilities;
- one source or control affecting three or more downstream stages.

Keep the block as code only when readers need executable syntax, exact configuration, a command, a log excerpt, or spacing-sensitive data. Arrows used as editorial prose are not code.

## Diagram grammar

Choose the smallest grammar that preserves the relationship:

| Relationship | Visual form |
| --- | --- |
| 2–3 simple steps | compact row or inline numbered cards |
| 4–9 ordered steps | numbered serpentine rows or vertical stage stack |
| feedback / learning | forward stages plus one isolated return path |
| gate / approval | decision node with explicit pass and stop/rework paths |
| before / after | two balanced panels with the changed hot path highlighted |
| layered system | stacked bands; state whether layers are hierarchy or lifecycle |
| text-rich ordered architecture | vertical stage stack with labeled connector lanes |
| repeated mapping | table or aligned cards instead of arrows |
| additive capabilities | unnumbered 2×2 or 2×3 capability grid |
| ranked hypotheses | stacked diagnostic cards with probability and evidence polarity |

Do not use a pyramid unless the evidence supports ranking. Do not place every noun in a separate box; a node should represent a decision, state, or stage.
Lines beginning with `+` are Markdown list syntax, not a reliable visual grammar. When four or more such lines describe equal-role capabilities, convert them to a capability grid before HTML normalization.

## Text budget

- Give each node one label of at most 8 Chinese characters or 3 English words when possible.
- Add at most one short detail line. Put evidence and caveats in article prose.
- Number nodes when order matters. Omit numbers for equal-role layers.
- Use verbs for transitions only when the transition itself matters.
- Use one caption outside the flow, never on top of the final node or return arrow.

## WeChat profile

- Use 1600px width and a content-driven height, normally 1000–1400px for a process.
- Use at most three columns. A 7–9 step flow normally uses three serpentine rows.
- Keep a 90–100px connector lane between cards. Use a compact fixed arrowhead, at least 20px clearance from each card, and a visible shaft inside that lane. At 1600px design width, an 18–22px head length or height is normally sufficient.
- Primary node labels: normally 36–40px at design size. Fit to the card width before considering a two-line wrap.
- Secondary text: normally 24–28px. Remove or shorten it if it approaches the shared 28–32px card padding.
- Custom SVG card text must use explicit line breaks because SVG `<text>` does not auto-wrap. Set `data-max-width` to the usable inner width and `data-font-size` to the rendered font size on every variable-length line.
- Vertically center the title/detail content group inside each card and keep top and bottom optical whitespace balanced.
- Center the badge/title row as one unit, then center every detail or wrapped line independently on the card center guide. Validate optical left/right whitespace from the card border to each visible row, not merely CSS padding values.
- In comparison panels, center short labels and metrics on the card guide. Keep checklist rows left-aligned for scanning, but center the widest-row bounding box as one group.
- Validate at 390px. If labels are not readable without zoom, use a taller diagram.
- Upload the final PNG through the official API and inspect the CDN rendition.

## LinkedIn profile

- Generate a separate 1200×1500 or 1080×1350 4:5 composition.
- Use one or two columns, 80–96px safe margins, and at least 40px label text.
- Put the thesis in the top 20% and the process in the middle 65%; reserve the bottom for one conclusion, not references.
- Use the same semantic colors as the WeChat diagram, but recompute positions and wrapping. Do not crop the WeChat output.
- For a carousel, give one stage or one decision per slide when the flow would exceed eight nodes.

## Standard renderer

Use the bundled renderer for a linear or feedback workflow:

```bash
uv run python skills/wechat-editorial-layout/scripts/render_process_diagram.py \
  path/to/flow.yaml --profile wechat --output path/to/flow-wechat.svg

uv run python skills/wechat-editorial-layout/scripts/render_process_diagram.py \
  path/to/flow.yaml --profile linkedin --output path/to/flow-linkedin.svg
```

Use the layered renderer for five to eight ordered, text-rich architecture stages:

```bash
uv run python skills/wechat-editorial-layout/scripts/render_layered_architecture.py \
  path/to/architecture.yaml --output path/to/architecture-wechat.svg
```

Each stage accepts `label`, `detail`, and an optional `transition` that labels the
connector to the next stage. Keep `detail` to one string or a short YAML list.

Input format:

```yaml
title: Agent Delivery Control Plane
subtitle: Every change passes through evidence and policy
steps:
  - label: Versioned change
    detail: Agent · Prompt · Skill · MCP
  - label: Build
    detail: CI and artifact
  - label: Evaluate
    detail: Quality and security gates
  - label: Deploy
    detail: Canary and approval
  - label: Observe
    detail: Trace and outcome
  - label: Learn
    detail: Failure to regression set
feedback: Failed cases return to evaluation
footer: Evidence → bounded action → verified outcome
```

The renderer is a baseline, not a license to skip visual QA. Render the SVG to PNG, inspect the pixels, and replace it with a custom diagram when the process contains real branching or nested topology.

The generated SVG uses a square preview-safe outer canvas and records the intended crop in `data-design-width` and `data-design-height`. Render the square SVG, then center-crop the PNG to those design dimensions. This avoids the aspect-ratio clipping produced by macOS Quick Look thumbnails.

Before rasterizing a custom SVG, validate its declared text boxes:

```bash
uv run python skills/wechat-editorial-layout/scripts/validate_svg_text_fit.py \
  path/to/custom-diagram.svg --require-contract
```

## Reject conditions

Reject or redesign the visual when any of these is true:

- a node contains a sentence or paragraph;
- more than three cards sit in one WeChat row;
- an arrow touches a border or runs through text;
- an arrowhead is partially hidden by a card, appears to grow out of a border, or has no visible shaft;
- a connector is rendered below card shadows, causing its shaft to disappear after rasterization;
- a connector shaft continues under or beyond its arrowhead instead of ending at the arrowhead base;
- the number badge and title do not share a visual center line;
- the title row and subsequent detail or wrapped lines use inconsistent center guides;
- any visible content row is left-heavy or right-heavy despite nominally equal padding;
- a checklist is left-aligned to an arbitrary inset instead of being centered as a group;
- a card uses unequal padding or oversized text to fill empty space;
- any text line exceeds its declared usable width, even when it remains inside the outer SVG canvas;
- a short title/detail group is top-heavy instead of vertically balanced;
- an SVG marker scales with stroke width instead of using fixed user-space dimensions;
- the return path crosses the forward path;
- the sequence relies only on color and has no labels or numbering;
- a LinkedIn asset is merely a crop of the WeChat diagram;
- text-rich architecture stages are compressed into a wide row or preserved as ASCII boxes;
- a transition label is placed inside a stage card instead of its connector lane;
- the final HTML still contains an arrow-heavy semantic `<pre>` block.
