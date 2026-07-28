#!/usr/bin/env python3
"""Validate declared text-width contracts in custom editorial SVGs."""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def visual_units(text: str) -> float:
    """Estimate rendered width in font-size units for mixed CJK/Latin text."""

    return sum(0.56 if ord(char) < 128 else 1.0 for char in text)


def text_lines(element: ET.Element) -> list[str]:
    tspans = [child for child in element if child.tag.rsplit("}", 1)[-1] == "tspan"]
    if tspans:
        return ["".join(child.itertext()).strip() for child in tspans]
    return ["".join(element.itertext()).strip()]


def validate_svg_text_fit(
    path: Path,
    *,
    require_contract: bool = False,
) -> list[str]:
    root = ET.parse(path).getroot()
    errors: list[str] = []
    contracted = 0

    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "text":
            continue
        max_width_raw = element.get("data-max-width")
        if max_width_raw is None:
            continue
        contracted += 1
        font_size_raw = element.get("data-font-size") or element.get("font-size")
        if font_size_raw is None:
            errors.append("contracted text is missing data-font-size or font-size")
            continue
        try:
            max_width = float(max_width_raw)
            font_size = float(font_size_raw.removesuffix("px"))
        except ValueError:
            errors.append("text width contract contains a non-numeric value")
            continue
        if max_width <= 0 or font_size <= 0:
            errors.append("text width contract values must be positive")
            continue

        for line in text_lines(element):
            if not line:
                continue
            estimated_width = visual_units(line) * font_size
            if estimated_width > max_width:
                errors.append(
                    f"text exceeds declared width: {line!r} "
                    f"({estimated_width:.1f}px > {max_width:.1f}px)"
                )

    if require_contract and contracted == 0:
        errors.append("custom SVG has no data-max-width text contracts")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("svg", type=Path)
    parser.add_argument(
        "--require-contract",
        action="store_true",
        help="fail when the SVG has no declared text-width contract",
    )
    args = parser.parse_args()

    errors = validate_svg_text_fit(args.svg, require_contract=args.require_contract)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"OK: {args.svg}")


if __name__ == "__main__":
    main()
