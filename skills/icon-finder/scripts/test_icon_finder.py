#!/usr/bin/env python3
"""Unit tests for icon_finder.py that do not require network access."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("icon_finder.py")
SPEC = importlib.util.spec_from_file_location("icon_finder", SCRIPT)
assert SPEC and SPEC.loader
icon_finder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(icon_finder)


class IconFinderTest(unittest.TestCase):
    def test_parse_icon_id(self) -> None:
        self.assertEqual(
            icon_finder._parse_icon_id("tabler:shield-check"),
            ("tabler", "shield-check"),
        )
        with self.assertRaises(icon_finder.IconFinderError):
            icon_finder._parse_icon_id("../unsafe")

    def test_rejects_script_and_external_reference(self) -> None:
        scripted = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            "<script>alert(1)</script></svg>"
        )
        with self.assertRaises(icon_finder.IconFinderError):
            icon_finder._validate_svg(scripted)

        external = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<use href="https://example.com/icon.svg#x"/></svg>'
        )
        with self.assertRaises(icon_finder.IconFinderError):
            icon_finder._validate_svg(external)

    def test_rejects_doctype(self) -> None:
        svg = (
            '<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"/>'
        )
        with self.assertRaises(icon_finder.IconFinderError):
            icon_finder._validate_svg(svg)

    def test_normalizes_to_transparent_square_canvas(self) -> None:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 24 12" fill="currentColor">'
            '<path d="M0 0h24v12H0z"/></svg>'
        )
        normalized, warnings = icon_finder._normalize_svg(
            svg, canvas=512, padding=0.1
        )
        root, post_warnings = icon_finder._validate_svg(normalized)
        self.assertEqual(root.attrib["viewBox"], "0 0 512 512")
        self.assertNotIn("<rect", normalized)
        self.assertIn("scale(", normalized)
        self.assertEqual(warnings, [])
        self.assertEqual(post_warnings, [])

    def test_warns_on_opaque_full_canvas_rect(self) -> None:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<rect width="24" height="24" fill="#fff"/></svg>'
        )
        _, warnings = icon_finder._validate_svg(svg)
        self.assertEqual(warnings, ["SVG contains an opaque full-canvas rectangle"])

    def test_manifest_preserves_multiple_icons(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "icon-manifest.json"
            icon_finder._update_manifest(path, "tabler:a", {"id": "tabler:a"})
            icon_finder._update_manifest(path, "tabler:b", {"id": "tabler:b"})
            manifest = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(sorted(manifest["icons"]), ["tabler:a", "tabler:b"])


if __name__ == "__main__":
    unittest.main()
