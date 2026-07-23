---
name: icon-finder
description: Find, download, normalize, inspect, and attribute style-consistent vector icons for PowerPoint, documents, and visual artifacts. Use when a slide or document needs replaceable SVG icons, when screenshot crops are blurry or have opaque backgrounds, when repeated icons need consistent visual scale, or when icon source and license metadata must be recorded.
---

# Icon Finder

Find icons through the official Iconify API, save a normalized transparent SVG, optionally render a PNG fallback, and record provenance and icon-set license metadata.

Read [references/acknowledgements.md](references/acknowledgements.md) before publishing this skill, changing icon sources, or preparing commercial or externally distributed material.

## Workflow

1. Search in English first and keep repeated icons in one collection:

   ```bash
   python scripts/icon_finder.py search "shield" \
     --prefixes tabler,lucide --limit 20
   ```

2. Select an exact `prefix:name` result and save it:

   ```bash
   python scripts/icon_finder.py save tabler:shield-check \
     --color "#E60012" --out-dir assets/icons --padding 0.10
   ```

3. Generate a PNG only when the target application cannot use SVG:

   ```bash
   uv run --with cairosvg \
     python scripts/icon_finder.py save tabler:shield-check \
     --color "#E60012" --out-dir assets/icons --png --size 512
   ```

4. Inspect an existing SVG before inserting it:

   ```bash
   python scripts/icon_finder.py inspect assets/icons/tabler-shield-check.svg
   ```

5. Review `assets/icons/icon-manifest.json`. Confirm the collection license is compatible with the intended distribution and satisfy any attribution requirement.

## Selection Rules

- Prefer one Iconify collection for a repeated visual group.
- Do not mix outline, filled, duotone, and illustrated icons in one peer set.
- Prefer SVG as the editable source. Use PNG only as a compatibility fallback.
- Choose icons by semantic clarity at presentation size, not by decorative detail.
- Keep icon color, stroke character, apparent scale, and safe-zone padding consistent.
- Do not use screenshot crops when a matching vector icon exists.
- Do not use iconfont.cn assets in this workflow; their per-icon authorization is not reliably machine-verifiable.
- Do not assume that all Iconify collections share one license. License metadata is per collection.

## PowerPoint Integration

When used with `pptx-high-fidelity-reconstruction`:

- replace blurry or opaque screenshot icons with normalized SVG assets;
- use one shared badge diameter and one glyph safe zone for every repeated icon set;
- preserve the SVG aspect ratio when placing it;
- center by visible glyph weight, then verify optical alignment in the rendered slide;
- retain `icon-manifest.json` with the presentation source and assets.

The normalized SVG uses a transparent square canvas. It does not add a white tile or visible background rectangle.

## API And Offline Use

The default service is the official Iconify API with its documented backup hosts. Set `ICONIFY_API_BASE` or pass `--api-base` to use an approved self-hosted Iconify API.

Only HTTPS API bases are accepted by default. Use `--allow-http` only for a trusted local or internal self-hosted service.

## QA Gate

Reject an icon asset if any of these are present:

- script, event handler, external image, external link, or remote paint reference in the SVG;
- missing or invalid `viewBox`;
- opaque full-canvas background;
- stretched or clipped glyph;
- inconsistent collection or style within a repeated icon group;
- missing collection license metadata;
- PNG generated without a corresponding SVG source;
- asset source absent from `icon-manifest.json`.
