#!/usr/bin/env python3
"""Render a text-rich ordered architecture as a mobile-safe vertical stack."""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path

import yaml

WIDTH = 1600
MARGIN_X = 92
TOP = 250
CARD_HEIGHT = 164
GAP_Y = 100
CARD_WIDTH = WIDTH - 2 * MARGIN_X
CARD_STYLES = (
    ("#0D3B4C", "#42D7E3"),
    ("#163A5B", "#5BB7F3"),
    ("#263566", "#7885FF"),
    ("#3E2B61", "#B07DF4"),
    ("#164B4A", "#42CFA5"),
    ("#40304D", "#E08ACD"),
)


def visual_units(text: str) -> float:
    return sum(0.56 if ord(char) < 128 else 1.0 for char in text)


def wrap_text(text: str, max_units: float, max_lines: int = 2) -> list[str]:
    value = " ".join(str(text).split())
    if visual_units(value) <= max_units:
        return [value]
    lines: list[str] = []
    remaining = value
    for _ in range(max_lines):
        if visual_units(remaining) <= max_units:
            lines.append(remaining)
            remaining = ""
            break
        units = 0.0
        split_at = 0
        preferred = 0
        for index, char in enumerate(remaining, 1):
            units += 0.56 if ord(char) < 128 else 1.0
            if char in " /·、，,:：-—":
                preferred = index
            if units > max_units:
                split_at = preferred if preferred >= max(1, index // 2) else index - 1
                break
        split_at = max(1, split_at)
        lines.append(remaining[:split_at].strip(" /·、，,:：-—"))
        remaining = remaining[split_at:].strip()
    if remaining:
        last = lines[-1]
        while last and visual_units(last + "…") > max_units:
            last = last[:-1]
        lines[-1] = last.rstrip() + "…"
    return lines


def fit_font_size(text: str, available_width: float, preferred: int, minimum: int) -> int:
    units = max(visual_units(text), 1.0)
    return max(minimum, min(preferred, int(available_width / units)))


def text_element(
    x: float,
    y: float,
    value: str,
    *,
    size: int,
    fill: str,
    max_width: float,
    weight: int = 500,
    anchor: str = "start",
) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'fill="{fill}" font-family="PingFang SC,Microsoft YaHei,Arial,sans-serif" '
        f'font-size="{size}" font-weight="{weight}" '
        f'data-max-width="{max_width:.1f}" data-font-size="{size}">'
        f"{escape(value)}</text>"
    )


def _detail_text(stage: dict) -> str:
    raw = stage.get("detail") or ""
    if isinstance(raw, list):
        return " · ".join(str(value).strip() for value in raw if str(value).strip())
    return str(raw).strip()


def render(spec: dict) -> str:
    title = str(spec.get("title") or "").strip()
    subtitle = str(spec.get("subtitle") or "").strip()
    stages = spec.get("stages")
    footer = str(spec.get("footer") or "").strip()
    if not title or not isinstance(stages, list) or not 3 <= len(stages) <= 8:
        raise ValueError("title and 3–8 stages are required")
    if any(
        not isinstance(stage, dict) or not str(stage.get("label") or "").strip() for stage in stages
    ):
        raise ValueError("every stage requires a label")

    stack_bottom = TOP + len(stages) * CARD_HEIGHT + (len(stages) - 1) * GAP_Y
    footer_extra = 150 if footer else 65
    height = stack_bottom + footer_extra
    canvas = max(WIDTH, height)
    offset_x = (canvas - WIDTH) / 2
    offset_y = (canvas - height) / 2

    title_size = fit_font_size(title, WIDTH - 2 * MARGIN_X, 54, 40)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas}" height="{canvas}" '
        f'viewBox="0 0 {canvas} {canvas}" data-design-width="{WIDTH}" '
        f'data-design-height="{height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(subtitle or "Ordered layered architecture")}</desc>',
        "<defs>",
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#07182D"/>'
        '<stop offset="1" stop-color="#202657"/></linearGradient>',
        '<linearGradient id="flow" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#42D8E4"/>'
        '<stop offset="1" stop-color="#B17CFA"/></linearGradient>',
        '<filter id="shadow" x="-20%" y="-20%" width="140%" height="150%">'
        '<feDropShadow dx="0" dy="10" stdDeviation="12" '
        'flood-color="#020814" flood-opacity="0.30"/></filter>',
        "</defs>",
        f'<g transform="translate({offset_x:.1f} {offset_y:.1f})">',
        f'<rect width="{WIDTH}" height="{height}" rx="28" fill="url(#bg)"/>',
        f'<circle cx="{WIDTH - 70}" cy="40" r="250" fill="#6554E8" opacity="0.12"/>',
        '<rect x="92" y="62" width="420" height="6" rx="3" fill="url(#flow)"/>',
        text_element(
            MARGIN_X,
            130,
            title,
            size=title_size,
            fill="#FFFFFF",
            max_width=WIDTH - 2 * MARGIN_X,
            weight=850,
        ),
    ]
    if subtitle:
        subtitle_size = fit_font_size(subtitle, WIDTH - 2 * MARGIN_X, 30, 26)
        parts.append(
            text_element(
                MARGIN_X,
                180,
                subtitle,
                size=subtitle_size,
                fill="#B8C8DF",
                max_width=WIDTH - 2 * MARGIN_X,
                weight=500,
            )
        )

    for index, stage in enumerate(stages, 1):
        y = TOP + (index - 1) * (CARD_HEIGHT + GAP_Y)
        fill, stroke = CARD_STYLES[(index - 1) % len(CARD_STYLES)]
        parts.extend(
            (
                f'<g filter="url(#shadow)"><rect x="{MARGIN_X}" y="{y}" '
                f'width="{CARD_WIDTH}" height="{CARD_HEIGHT}" rx="24" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="3"/></g>',
                f'<rect x="{MARGIN_X}" y="{y}" width="10" height="{CARD_HEIGHT}" '
                f'rx="5" fill="{stroke}"/>',
                f'<circle cx="154" cy="{y + CARD_HEIGHT / 2:.1f}" r="26" fill="{stroke}"/>',
                text_element(
                    154,
                    y + CARD_HEIGHT / 2 + 8,
                    str(index),
                    size=24,
                    fill="#0B1D35",
                    max_width=40,
                    weight=850,
                    anchor="middle",
                ),
            )
        )

        label = str(stage["label"]).strip()
        label_size = fit_font_size(label, 350, 40, 34)
        label_lines = wrap_text(label, 350 / label_size, 2)
        label_line_height = label_size + 6
        label_top = y + CARD_HEIGHT / 2 - (len(label_lines) * label_line_height - 6) / 2
        for line_index, line in enumerate(label_lines):
            parts.append(
                text_element(
                    205,
                    label_top + label_size * 0.84 + line_index * label_line_height,
                    line,
                    size=label_size,
                    fill="#FFFFFF",
                    max_width=350,
                    weight=800,
                )
            )

        detail = _detail_text(stage)
        if detail:
            detail_size = 30
            detail_lines = wrap_text(detail, 840 / detail_size, 2)
            detail_line_height = detail_size + 8
            detail_top = y + CARD_HEIGHT / 2 - (len(detail_lines) * detail_line_height - 8) / 2
            for line_index, line in enumerate(detail_lines):
                parts.append(
                    text_element(
                        590,
                        detail_top + detail_size * 0.84 + line_index * detail_line_height,
                        line,
                        size=detail_size,
                        fill="#D9E6F5",
                        max_width=840,
                        weight=550,
                    )
                )

        if index < len(stages):
            next_y = y + CARD_HEIGHT + GAP_Y
            tip_y = next_y - 20
            base_y = tip_y - 18
            line_start = y + CARD_HEIGHT + 18
            parts.extend(
                (
                    f'<line x1="800" y1="{line_start}" x2="800" y2="{base_y}" '
                    'stroke="#93A8DF" stroke-width="6" stroke-linecap="round"/>',
                    f'<polygon points="788,{base_y} 800,{tip_y} 812,{base_y}" fill="#93A8DF"/>',
                )
            )
            transition = str(stage.get("transition") or "").strip()
            if transition:
                transition_size = fit_font_size(transition, 460, 27, 23)
                parts.append(
                    text_element(
                        835,
                        (line_start + tip_y) / 2 + 8,
                        transition,
                        size=transition_size,
                        fill="#C7D4EA",
                        max_width=460,
                        weight=700,
                    )
                )

    if footer:
        footer_y = stack_bottom + 45
        parts.extend(
            (
                f'<rect x="210" y="{footer_y}" width="1180" height="72" rx="36" '
                'fill="url(#flow)" opacity="0.20"/>',
                text_element(
                    WIDTH / 2,
                    footer_y + 47,
                    footer,
                    size=31,
                    fill="#FFFFFF",
                    max_width=1080,
                    weight=750,
                    anchor="middle",
                ),
            )
        )
    parts.extend(("</g>", "</svg>"))
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    spec = yaml.safe_load(args.spec.read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        raise SystemExit("architecture spec must be a YAML mapping")
    output = render(spec)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"wrote {args.output} ({len(spec.get('stages') or [])} stages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
