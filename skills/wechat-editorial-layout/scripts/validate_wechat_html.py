#!/usr/bin/env python3
"""Validate the deterministic safety properties of WeChat article HTML."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


class ArticleInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: set[str] = set()
        self.images: list[dict[str, str]] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = tag.lower()
        self.tags.add(normalized)
        if normalized == "img":
            self.images.append({key.lower(): value or "" for key, value in attrs})

    def handle_data(self, data: str) -> None:
        self.text.append(data)


def validate(path: Path, *, mode: str = "remote-draft") -> list[str]:
    html = path.read_text(encoding="utf-8")
    inspector = ArticleInspector()
    inspector.feed(html)
    errors: list[str] = []
    for banned in ("script", "iframe", "form"):
        if banned in inspector.tags:
            errors.append(f"banned <{banned}> element")
    if inspector.tags.intersection({"ul", "ol", "li"}):
        errors.append("native list element may render stray markers in WeChat")
    for image in inspector.images:
        src = image.get("src", "")
        invalid = image.get("data-invalid-src", "")
        if invalid:
            errors.append(f"unreplaced image placeholder: {invalid}")
        if not src:
            errors.append("image has empty src")
            continue
        parsed = urlparse(src)
        if mode == "remote-draft":
            if parsed.scheme != "https":
                errors.append(f"image is not hosted HTTPS: {src}")
        elif parsed.scheme in {"http", "https"}:
            continue
        elif parsed.scheme:
            errors.append(f"unsupported local-preview image scheme: {src}")
        elif Path(unquote(parsed.path)).is_absolute():
            errors.append(f"local-preview image must use a relative path: {src}")
        elif not (path.parent / unquote(parsed.path)).resolve().is_file():
            errors.append(f"local-preview image does not exist: {src}")
    for marker in ("file://", "localhost", "127.0.0.1", "asset://"):
        if marker in html:
            errors.append(f"forbidden local marker: {marker}")
    if "这篇文章怎么看" in " ".join(inspector.text):
        errors.append("meta reading guide should be removed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("article", type=Path)
    parser.add_argument(
        "--mode",
        choices=("local-preview", "remote-draft"),
        default="remote-draft",
    )
    args = parser.parse_args()
    errors = validate(args.article, mode=args.mode)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.article} ({args.mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
