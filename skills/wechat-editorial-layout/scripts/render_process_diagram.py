#!/usr/bin/env python3
"""Render a concise editorial workflow as channel-specific SVG."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
from itertools import pairwise
from math import ceil
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Profile:
    width: int
    height: int
    columns: int
    margin_x: int
    top: int
    card_height: int
    gap_x: int
    gap_y: int
    title_size: int
    subtitle_size: int
    label_size: int
    detail_size: int


PROFILES = {
    "wechat": Profile(1600, 0, 3, 96, 250, 180, 100, 96, 54, 28, 38, 26),
    "linkedin": Profile(1200, 1500, 2, 86, 270, 188, 96, 96, 52, 28, 36, 26),
}

CONNECTOR_LENGTH = 54
ARROW_HEAD_LENGTH = 18
ARROW_HEAD_HALF_HEIGHT = 11
MIN_CONNECTOR_CLEARANCE = 20

CARD_STYLES = (
    ("#0D3B4C", "#42D7E3", "#D2FAFC"),
    ("#163A5B", "#5BB7F3", "#DAF1FF"),
    ("#263566", "#7885FF", "#E4E7FF"),
    ("#3E2B61", "#B07DF4", "#F1E4FF"),
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
    fitted = int(available_width / units)
    return max(minimum, min(preferred, fitted))


def text_element(
    x: float,
    y: float,
    value: str,
    *,
    size: int,
    fill: str,
    weight: int = 500,
    anchor: str = "start",
) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'fill="{fill}" font-family="PingFang SC,Microsoft YaHei,Arial,sans-serif" '
        f'font-size="{size}" font-weight="{weight}">{escape(value)}</text>'
    )


def positions(step_count: int, profile: Profile) -> tuple[list[tuple[float, float]], float]:
    columns = min(profile.columns, step_count)
    card_width = (profile.width - 2 * profile.margin_x - (columns - 1) * profile.gap_x) / columns
    result: list[tuple[float, float]] = []
    for index in range(step_count):
        row = index // columns
        within = index % columns
        column = within if row % 2 == 0 else columns - 1 - within
        x = profile.margin_x + column * (card_width + profile.gap_x)
        y = profile.top + row * (profile.card_height + profile.gap_y)
        result.append((x, y))
    return result, card_width


def connector(
    first: tuple[float, float],
    second: tuple[float, float],
    card_width: float,
    card_height: float,
) -> str:
    x1, y1 = first
    x2, y2 = second
    mid_y1 = y1 + card_height / 2
    color = "#8EA6E5"
    if abs(y1 - y2) < 1:
        if x2 > x1:
            lane_start, lane_end = x1 + card_width, x2
            direction = 1
        else:
            lane_start, lane_end = x2 + card_width, x1
            direction = -1
        lane_width = lane_end - lane_start
        if lane_width < CONNECTOR_LENGTH + 2 * MIN_CONNECTOR_CLEARANCE:
            raise ValueError("horizontal connector lane is too short")
        center_x = (lane_start + lane_end) / 2
        tail_x = center_x - direction * CONNECTOR_LENGTH / 2
        tip_x = center_x + direction * CONNECTOR_LENGTH / 2
        base_x = tip_x - direction * ARROW_HEAD_LENGTH
        line = (
            f'<line x1="{tail_x:.1f}" y1="{mid_y1:.1f}" '
            f'x2="{base_x:.1f}" y2="{mid_y1:.1f}" stroke="{color}" '
            'stroke-width="6" stroke-linecap="round"/>'
        )
        points = (
            f"{base_x:.1f},{mid_y1 - ARROW_HEAD_HALF_HEIGHT:.1f} "
            f"{tip_x:.1f},{mid_y1:.1f} "
            f"{base_x:.1f},{mid_y1 + ARROW_HEAD_HALF_HEIGHT:.1f}"
        )
    else:
        center_x1 = x1 + card_width / 2
        center_x2 = x2 + card_width / 2
        if abs(center_x1 - center_x2) >= 1:
            raise ValueError("row transition must use one vertical connector lane")
        lane_start = y1 + card_height
        lane_end = y2
        lane_height = lane_end - lane_start
        if lane_height < CONNECTOR_LENGTH + 2 * MIN_CONNECTOR_CLEARANCE:
            raise ValueError("vertical connector lane is too short")
        center_y = (lane_start + lane_end) / 2
        tail_y = center_y - CONNECTOR_LENGTH / 2
        tip_y = center_y + CONNECTOR_LENGTH / 2
        base_y = tip_y - ARROW_HEAD_LENGTH
        line = (
            f'<line x1="{center_x1:.1f}" y1="{tail_y:.1f}" '
            f'x2="{center_x1:.1f}" y2="{base_y:.1f}" stroke="{color}" '
            'stroke-width="6" stroke-linecap="round"/>'
        )
        points = (
            f"{center_x1 - ARROW_HEAD_HALF_HEIGHT:.1f},{base_y:.1f} "
            f"{center_x1:.1f},{tip_y:.1f} "
            f"{center_x1 + ARROW_HEAD_HALF_HEIGHT:.1f},{base_y:.1f}"
        )
    return f'<g aria-hidden="true">{line}<polygon points="{points}" fill="{color}"/></g>'


def render(spec: dict, profile_name: str) -> str:
    profile = PROFILES[profile_name]
    title = str(spec.get("title") or "").strip()
    subtitle = str(spec.get("subtitle") or "").strip()
    steps = spec.get("steps")
    if not title or not isinstance(steps, list) or not 2 <= len(steps) <= 9:
        raise ValueError("title and 2–9 steps are required")
    if any(
        not isinstance(step, dict) or not str(step.get("label") or "").strip() for step in steps
    ):
        raise ValueError("every step requires a label")

    coords, card_width = positions(len(steps), profile)
    rows = ceil(len(steps) / min(profile.columns, len(steps)))
    grid_bottom = profile.top + rows * profile.card_height + (rows - 1) * profile.gap_y
    feedback = str(spec.get("feedback") or "").strip()
    footer = str(spec.get("footer") or "").strip()
    extra = (126 if feedback else 36) + (106 if footer else 30)
    computed_height = int(grid_bottom + extra + 58)
    height = max(profile.height, computed_height) if profile.height else computed_height

    canvas = max(profile.width, height)
    offset_x = (canvas - profile.width) / 2
    offset_y = (canvas - height) / 2
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas}" height="{canvas}" viewBox="0 0 {canvas} {canvas}" data-design-width="{profile.width}" data-design-height="{height}">',
        "<defs>",
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#07182D"/><stop offset="1" stop-color="#202657"/></linearGradient>',
        '<linearGradient id="flow" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#42D8E4"/><stop offset="1" stop-color="#B17CFA"/></linearGradient>',
        '<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#020814" flood-opacity="0.30"/></filter>',
        "</defs>",
        f'<g transform="translate({offset_x:.1f} {offset_y:.1f})">',
        f'<rect width="{profile.width}" height="{height}" rx="28" fill="url(#bg)"/>',
        f'<circle cx="{profile.width - 90}" cy="65" r="230" fill="#6554E8" opacity="0.12"/>',
        text_element(
            profile.margin_x, 92, title, size=profile.title_size, fill="#FFFFFF", weight=800
        ),
    ]
    if subtitle:
        parts.append(
            text_element(
                profile.margin_x,
                142,
                subtitle,
                size=profile.subtitle_size,
                fill="#B8C8DF",
                weight=500,
            )
        )

    for index, (step, (x, y)) in enumerate(zip(steps, coords, strict=True), 1):
        fill, stroke, detail_fill = CARD_STYLES[(index - 1) % len(CARD_STYLES)]
        parts.append(
            f'<g filter="url(#shadow)"><rect x="{x:.1f}" y="{y:.1f}" width="{card_width:.1f}" height="{profile.card_height}" rx="24" fill="{fill}" stroke="{stroke}" stroke-width="3"/></g>'
        )
        card_padding = 32
        badge_diameter = 48
        badge_gap = 14
        text_offset = badge_diameter + badge_gap
        group_capacity = card_width - 2 * card_padding
        text_capacity = group_capacity - text_offset
        label_value = str(step["label"])
        label_size = fit_font_size(label_value, text_capacity, profile.label_size, 30)
        label_lines = wrap_text(label_value, text_capacity / label_size, 2)
        label_line_height = label_size + 6
        label_block_height = len(label_lines) * label_line_height - 6
        detail = str(step.get("detail") or "").strip()
        detail_size = fit_font_size(detail, text_capacity, profile.detail_size, 22) if detail else 0
        detail_lines = wrap_text(detail, text_capacity / detail_size, 2) if detail else []
        detail_line_height = detail_size + 5
        detail_block_height = len(detail_lines) * detail_line_height - 5 if detail_lines else 0
        label_text_width = min(
            text_capacity,
            max(visual_units(line) * label_size for line in label_lines),
        )
        header_width = text_offset + label_text_width
        header_left = x + (card_width - header_width) / 2
        number_x = header_left + badge_diameter / 2
        label_center_x = header_left + text_offset + label_text_width / 2
        header_height = max(48, label_block_height)
        content_gap = (18 if len(detail_lines) > 1 else 24) if detail else 0
        content_height = header_height + content_gap + detail_block_height
        content_top = y + (profile.card_height - content_height) / 2
        header_center_y = content_top + header_height / 2
        label_top = header_center_y - label_block_height / 2
        parts.append(
            f'<circle cx="{number_x:.1f}" cy="{header_center_y:.1f}" r="24" fill="{stroke}"/>'
        )
        parts.append(
            text_element(
                number_x,
                header_center_y + 8,
                str(index),
                size=24,
                fill="#0B1D35",
                weight=800,
                anchor="middle",
            )
        )
        for line_index, line in enumerate(label_lines):
            parts.append(
                text_element(
                    label_center_x,
                    label_top + label_size * 0.84 + line_index * label_line_height,
                    line,
                    size=label_size,
                    fill="#FFFFFF",
                    weight=800,
                    anchor="middle",
                )
            )
        if detail:
            detail_top = content_top + header_height + content_gap
            for line_index, line in enumerate(detail_lines):
                parts.append(
                    text_element(
                        x + card_width / 2,
                        detail_top + detail_size * 0.84 + line_index * detail_line_height,
                        line,
                        size=detail_size,
                        fill=detail_fill,
                        weight=500,
                        anchor="middle",
                    )
                )

    # Draw connectors above card shadows. The paths remain inside the reserved
    # lanes, so raising their z-order reveals the shaft without crossing cards.
    for first, second in pairwise(coords):
        parts.append(connector(first, second, card_width, profile.card_height))

    next_y = grid_bottom + 44
    if feedback:
        parts.append(
            f'<rect x="{profile.margin_x}" y="{next_y}" width="{profile.width - 2 * profile.margin_x}" height="78" rx="24" fill="#10243F" stroke="#6681B3" stroke-width="2"/>'
        )
        parts.append(
            text_element(
                profile.width / 2,
                next_y + 50,
                "↺ " + feedback,
                size=32 if profile_name == "wechat" else 30,
                fill="#D7E3F5",
                weight=700,
                anchor="middle",
            )
        )
        next_y += 102
    if footer:
        footer_width = profile.width - 2 * profile.margin_x - 160
        parts.append(
            f'<rect x="{profile.margin_x + 80}" y="{next_y}" width="{footer_width}" height="70" rx="35" fill="url(#flow)" opacity="0.20"/>'
        )
        parts.append(
            text_element(
                profile.width / 2,
                next_y + 46,
                footer,
                size=30 if profile_name == "wechat" else 28,
                fill="#FFFFFF",
                weight=700,
                anchor="middle",
            )
        )
    parts.extend(("</g>", "</svg>"))
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--profile", choices=tuple(PROFILES), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    spec = yaml.safe_load(args.spec.read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        raise SystemExit("diagram spec must be a YAML mapping")
    output = render(spec, args.profile)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"wrote {args.output} ({args.profile}, {len(spec.get('steps') or [])} steps)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
