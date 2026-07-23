#!/usr/bin/env python3
"""Search, save, normalize, inspect, and attribute Iconify SVG icons."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_API_BASES = (
    "https://api.iconify.design",
    "https://api.simplesvg.com",
    "https://api.unisvg.com",
)
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
FORBIDDEN_TAGS = {
    "script",
    "foreignObject",
    "iframe",
    "object",
    "embed",
    "image",
    "audio",
    "video",
}
PRESENTATION_ATTRIBUTES = {
    "color",
    "fill",
    "fill-opacity",
    "fill-rule",
    "stroke",
    "stroke-dasharray",
    "stroke-dashoffset",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-miterlimit",
    "stroke-opacity",
    "stroke-width",
    "clip-rule",
    "opacity",
}
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$")
ICON_ID = re.compile(r"^(?P<prefix>[a-z0-9-]+):(?P<name>[a-z0-9-]+)$")
NUMBER = re.compile(r"^-?(?:\d+(?:\.\d*)?|\.\d+)$")

ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)


class IconFinderError(RuntimeError):
    """Expected command failure with a user-facing message."""


def _local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1]


def _api_bases(explicit: str | None, allow_http: bool) -> list[str]:
    configured = explicit or os.environ.get("ICONIFY_API_BASE")
    bases = [configured] if configured else list(DEFAULT_API_BASES)
    normalized: list[str] = []
    for value in bases:
        if not value:
            continue
        parsed = urllib.parse.urlparse(value)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc:
            raise IconFinderError(f"Invalid Iconify API base: {value}")
        if parsed.scheme == "http" and not allow_http:
            raise IconFinderError(
                f"Refusing insecure API base {value}; pass --allow-http only for a trusted service"
            )
        normalized.append(value.rstrip("/"))
    return normalized


def _request(
    path: str,
    *,
    params: dict[str, Any] | None,
    api_base: str | None,
    allow_http: bool,
    timeout: float,
) -> tuple[bytes, str]:
    query = urllib.parse.urlencode(params or {})
    suffix = f"?{query}" if query else ""
    errors: list[str] = []
    context = _ssl_context()
    for base in _api_bases(api_base, allow_http):
        url = f"{base}{path}{suffix}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json, image/svg+xml;q=0.9, */*;q=0.1",
                "User-Agent": "milos-icon-finder/1.0",
            },
        )
        try:
            with urllib.request.urlopen(
                request, timeout=timeout, context=context
            ) as response:
                return response.read(), url
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            errors.append(f"{base}: {exc}")
    raise IconFinderError("Iconify request failed: " + " | ".join(errors))


def _ssl_context() -> ssl.SSLContext:
    configured = os.environ.get("SSL_CERT_FILE")
    if configured:
        return ssl.create_default_context(cafile=configured)
    try:
        import certifi  # type: ignore[import-not-found]
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def _request_json(
    path: str,
    *,
    params: dict[str, Any] | None,
    api_base: str | None,
    allow_http: bool,
    timeout: float,
) -> tuple[dict[str, Any], str]:
    body, url = _request(
        path,
        params=params,
        api_base=api_base,
        allow_http=allow_http,
        timeout=timeout,
    )
    try:
        value = json.loads(body)
    except json.JSONDecodeError as exc:
        raise IconFinderError(f"Invalid JSON from {url}: {exc}") from exc
    if not isinstance(value, dict):
        raise IconFinderError(f"Unexpected JSON response from {url}")
    return value, url


def _parse_icon_id(value: str) -> tuple[str, str]:
    match = ICON_ID.fullmatch(value.strip())
    if not match:
        raise IconFinderError(
            f"Invalid icon id {value!r}; expected lowercase prefix:name"
        )
    return match.group("prefix"), match.group("name")


def _parse_view_box(root: ET.Element) -> tuple[float, float, float, float]:
    raw = root.attrib.get("viewBox", "").replace(",", " ").split()
    if len(raw) != 4 or any(not NUMBER.fullmatch(item) for item in raw):
        raise IconFinderError("SVG must have a numeric four-value viewBox")
    x, y, width, height = (float(item) for item in raw)
    if width <= 0 or height <= 0:
        raise IconFinderError("SVG viewBox width and height must be positive")
    return x, y, width, height


def _validate_svg(svg: str) -> tuple[ET.Element, list[str]]:
    lowered = svg.lower()
    if "<!doctype" in lowered or "<!entity" in lowered:
        raise IconFinderError("SVG document types and entities are not allowed")
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as exc:
        raise IconFinderError(f"Invalid SVG XML: {exc}") from exc
    if _local_name(root.tag) != "svg":
        raise IconFinderError("Root element must be <svg>")
    x, y, width, height = _parse_view_box(root)
    warnings: list[str] = []
    for element in root.iter():
        tag = _local_name(element.tag)
        if tag in FORBIDDEN_TAGS:
            raise IconFinderError(f"Forbidden SVG element: {tag}")
        for attr_name, attr_value in element.attrib.items():
            local_attr = _local_name(attr_name)
            value = attr_value.strip()
            if local_attr.lower().startswith("on"):
                raise IconFinderError(f"Event handler attribute is not allowed: {local_attr}")
            if local_attr == "href" and value and not value.startswith("#"):
                raise IconFinderError(f"External SVG reference is not allowed: {value}")
            if "url(" in value.lower() and "url(#" not in value.lower():
                raise IconFinderError(f"External SVG paint reference is not allowed: {value}")
        if tag == "rect" and _covers_view_box(element, x, y, width, height):
            fill = element.attrib.get("fill", root.attrib.get("fill", "black")).lower()
            opacity = element.attrib.get(
                "fill-opacity", element.attrib.get("opacity", "1")
            )
            if fill not in {"none", "transparent"} and opacity not in {"0", "0.0"}:
                warnings.append("SVG contains an opaque full-canvas rectangle")
    return root, warnings


def _float_attr(element: ET.Element, name: str, default: float) -> float:
    raw = element.attrib.get(name)
    if raw is None or not NUMBER.fullmatch(raw):
        return default
    return float(raw)


def _covers_view_box(
    element: ET.Element, x: float, y: float, width: float, height: float
) -> bool:
    rect_x = _float_attr(element, "x", 0)
    rect_y = _float_attr(element, "y", 0)
    rect_width = _float_attr(element, "width", 0)
    rect_height = _float_attr(element, "height", 0)
    tolerance = max(width, height) * 0.001
    return (
        rect_x <= x + tolerance
        and rect_y <= y + tolerance
        and rect_x + rect_width >= x + width - tolerance
        and rect_y + rect_height >= y + height - tolerance
    )


def _normalize_svg(svg: str, *, canvas: int, padding: float) -> tuple[str, list[str]]:
    if canvas <= 0:
        raise IconFinderError("--canvas must be positive")
    if not 0 <= padding < 0.45:
        raise IconFinderError("--padding must be between 0 and 0.45")
    root, warnings = _validate_svg(svg)
    x, y, width, height = _parse_view_box(root)
    available = canvas * (1 - 2 * padding)
    scale = min(available / width, available / height)
    left = (canvas - width * scale) / 2
    top = (canvas - height * scale) / 2

    normalized = ET.Element(
        f"{{{SVG_NS}}}svg",
        {
            "viewBox": f"0 0 {canvas} {canvas}",
            "width": str(canvas),
            "height": str(canvas),
            "role": "img",
        },
    )
    group_attributes = {
        key: value
        for key, value in root.attrib.items()
        if _local_name(key) in PRESENTATION_ATTRIBUTES
    }
    group_attributes["transform"] = (
        f"translate({_fmt(left)} {_fmt(top)}) "
        f"scale({_fmt(scale)}) translate({_fmt(-x)} {_fmt(-y)})"
    )
    group = ET.SubElement(normalized, f"{{{SVG_NS}}}g", group_attributes)
    for child in list(root):
        root.remove(child)
        group.append(child)

    rendered = ET.tostring(normalized, encoding="unicode")
    _validate_svg(rendered)
    return rendered + "\n", warnings


def _fmt(value: float) -> str:
    return f"{value:.8f}".rstrip("0").rstrip(".") or "0"


def _slug(value: str) -> str:
    result = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()
    if not result:
        raise IconFinderError("Output name does not contain a safe filename")
    return result


def _collection_info(
    prefix: str,
    *,
    api_base: str | None,
    allow_http: bool,
    timeout: float,
) -> tuple[dict[str, Any], str]:
    data, url = _request_json(
        "/collections",
        params={"prefix": prefix},
        api_base=api_base,
        allow_http=allow_http,
        timeout=timeout,
    )
    info = data.get(prefix)
    if not isinstance(info, dict):
        raise IconFinderError(f"No collection metadata returned for {prefix}")
    if not isinstance(info.get("license"), dict):
        raise IconFinderError(f"Collection {prefix} has no license metadata")
    return info, url


def _render_png(svg: str, path: Path, size: int) -> None:
    if size <= 0:
        raise IconFinderError("--size must be positive")
    try:
        import cairosvg  # type: ignore[import-not-found]
    except ImportError as exc:
        raise IconFinderError(
            "PNG rendering requires CairoSVG; use SVG or run with "
            "`uv run --with cairosvg ... --png`"
        ) from exc
    cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        write_to=str(path),
        output_width=size,
        output_height=size,
    )


def _update_manifest(path: Path, icon_id: str, entry: dict[str, Any]) -> None:
    if path.exists():
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise IconFinderError(f"Cannot read existing manifest {path}: {exc}") from exc
    else:
        manifest = {"schema_version": 1, "icons": {}}
    if manifest.get("schema_version") != 1 or not isinstance(
        manifest.get("icons"), dict
    ):
        raise IconFinderError(f"Unsupported manifest structure in {path}")
    manifest["icons"][icon_id] = entry
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _license_summary(info: dict[str, Any]) -> str:
    license_info = info.get("license")
    if not isinstance(license_info, dict):
        return "unknown"
    return str(
        license_info.get("spdx")
        or license_info.get("title")
        or license_info.get("url")
        or "unknown"
    )


def command_search(args: argparse.Namespace) -> int:
    requested_limit = max(1, min(args.limit, 999))
    params: dict[str, Any] = {
        "query": args.query,
        "limit": max(32, requested_limit),
    }
    if args.prefixes:
        params["prefixes"] = args.prefixes
    data, request_url = _request_json(
        "/search",
        params=params,
        api_base=args.api_base,
        allow_http=args.allow_http,
        timeout=args.timeout,
    )
    icons = data.get("icons")
    if not isinstance(icons, list):
        raise IconFinderError("Iconify search response did not include an icons list")
    collections = data.get("collections")
    if not isinstance(collections, dict):
        collections = {}
    results: list[dict[str, Any]] = []
    for icon_id in icons[:requested_limit]:
        if not isinstance(icon_id, str) or ":" not in icon_id:
            continue
        prefix, _ = icon_id.split(":", 1)
        info = collections.get(prefix)
        info = info if isinstance(info, dict) else {}
        results.append(
            {
                "id": icon_id,
                "collection": info.get("name", prefix),
                "license": _license_summary(info),
                "author": info.get("author"),
            }
        )
    output = {
        "query": args.query,
        "request_url": request_url,
        "total": data.get("total", len(results)),
        "results": results,
    }
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"Query: {args.query}  Results: {len(results)}")
        for index, item in enumerate(results):
            print(
                f"[{index:02d}] {item['id']:<40} "
                f"collection={item['collection']} license={item['license']}"
            )
    return 0


def command_save(args: argparse.Namespace) -> int:
    prefix, name = _parse_icon_id(args.icon_id)
    if args.color and not HEX_COLOR.fullmatch(args.color):
        raise IconFinderError("--color must be #RGB or #RRGGBB")
    collection, collection_url = _collection_info(
        prefix,
        api_base=args.api_base,
        allow_http=args.allow_http,
        timeout=args.timeout,
    )
    params = {"color": args.color} if args.color else None
    encoded_prefix = urllib.parse.quote(prefix, safe="")
    encoded_name = urllib.parse.quote(name, safe="")
    raw, download_url = _request(
        f"/{encoded_prefix}/{encoded_name}.svg",
        params=params,
        api_base=args.api_base,
        allow_http=args.allow_http,
        timeout=args.timeout,
    )
    try:
        svg = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IconFinderError("Iconify returned a non-UTF-8 SVG") from exc
    normalized, warnings = _normalize_svg(
        svg, canvas=args.canvas, padding=args.padding
    )
    if warnings and not args.allow_opaque_background:
        raise IconFinderError("; ".join(warnings))

    output_dir = Path(args.out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    base = _slug(args.out_name or f"{prefix}-{name}")
    svg_path = output_dir / f"{base}.svg"
    svg_path.write_text(normalized, encoding="utf-8")

    png_path: Path | None = None
    if args.png:
        png_path = output_dir / f"{base}.png"
        _render_png(normalized, png_path, args.size)

    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    manifest_path = output_dir / "icon-manifest.json"
    entry = {
        "id": args.icon_id,
        "source": "iconify",
        "collection_prefix": prefix,
        "collection_name": collection.get("name", prefix),
        "author": collection.get("author"),
        "license": collection.get("license"),
        "collection_metadata_url": collection_url,
        "download_url": download_url,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "color": args.color,
        "canvas": args.canvas,
        "padding": args.padding,
        "svg_path": str(svg_path),
        "svg_sha256": digest,
        "png_path": str(png_path) if png_path else None,
    }
    _update_manifest(manifest_path, args.icon_id, entry)

    print(f"SVG: {svg_path}")
    if png_path:
        print(f"PNG: {png_path}")
    print(f"Manifest: {manifest_path}")
    print(f"Collection license: {_license_summary(collection)}")
    return 0


def command_inspect(args: argparse.Namespace) -> int:
    path = Path(args.path)
    try:
        svg = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise IconFinderError(f"Cannot read {path}: {exc}") from exc
    root, warnings = _validate_svg(svg)
    x, y, width, height = _parse_view_box(root)
    result = {
        "path": str(path),
        "viewBox": [x, y, width, height],
        "square_canvas": abs(width - height) < 1e-9,
        "sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest(),
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Path: {path}")
        print(f"viewBox: {x:g} {y:g} {width:g} {height:g}")
        print(f"Square canvas: {result['square_canvas']}")
        print(f"SHA-256: {result['sha256']}")
        for warning in warnings:
            print(f"Warning: {warning}")
    return 2 if warnings else 0


def _add_api_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--allow-http", action="store_true")
    parser.add_argument("--timeout", type=float, default=15.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find and prepare attributable Iconify SVG icons"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Search Iconify collections")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=20)
    search.add_argument(
        "--prefixes",
        default=None,
        help="Comma-separated collection prefixes, such as tabler,lucide",
    )
    search.add_argument("--json", action="store_true")
    _add_api_arguments(search)
    search.set_defaults(func=command_search)

    save = subparsers.add_parser("save", help="Download and normalize one icon")
    save.add_argument("icon_id", help="Exact Iconify id in prefix:name form")
    save.add_argument("--out-dir", default="icons")
    save.add_argument("--out-name", default=None)
    save.add_argument("--color", default=None)
    save.add_argument("--canvas", type=int, default=512)
    save.add_argument("--padding", type=float, default=0.10)
    save.add_argument("--png", action="store_true")
    save.add_argument("--size", type=int, default=512)
    save.add_argument("--allow-opaque-background", action="store_true")
    _add_api_arguments(save)
    save.set_defaults(func=command_save)

    inspect = subparsers.add_parser("inspect", help="Inspect a local SVG")
    inspect.add_argument("path")
    inspect.add_argument("--json", action="store_true")
    inspect.set_defaults(func=command_inspect)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except IconFinderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
