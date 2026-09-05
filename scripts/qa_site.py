#!/usr/bin/env python3
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlparse, unquote

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "fixtures/platform/web-quality-v1.json"
DEFAULT_SCHEMA = ROOT / "schemas/aether-web-quality-budget.schema.json"


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.html_attrs: dict[str, str] = {}
        self.has_viewport = False
        self.title_text = ""
        self.importmap_errors: list[str] = []
        self._in_title = False
        self._in_importmap = False
        self._importmap_data: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: (value or "") for key, value in attrs}
        if tag == "html":
            self.html_attrs = values
        if tag == "meta" and values.get("name", "").lower() == "viewport" and values.get("content"):
            self.has_viewport = True
        if tag == "title":
            self._in_title = True
        if tag == "script" and values.get("type", "").lower() == "importmap":
            self._in_importmap = True
            self._importmap_data = []
        for key in ("href", "src"):
            value = values.get(key)
            if value:
                self.refs.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_importmap:
            raw = "".join(self._importmap_data).strip()
            try:
                payload = json.loads(raw)
                imports = payload.get("imports", {})
                if not isinstance(imports, dict):
                    raise ValueError("imports must be an object")
                self.refs.extend(value for value in imports.values() if isinstance(value, str))
            except (json.JSONDecodeError, ValueError) as exc:
                self.importmap_errors.append(str(exc))
            finally:
                self._in_importmap = False
                self._importmap_data = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_text += data
        if self._in_importmap:
            self._importmap_data.append(data)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def local_target(site_root: Path, html_file: Path, ref: str) -> Path | None:
    stripped = ref.strip()
    if not stripped or stripped.startswith(("#", "data:", "blob:", "mailto:", "tel:", "javascript:")):
        return None
    parsed = urlparse(stripped)
    if parsed.scheme or parsed.netloc:
        return None
    raw_path = unquote(parsed.path)
    if not raw_path:
        return None
    if raw_path.startswith("/"):
        target = site_root / raw_path.lstrip("/")
    else:
        target = html_file.parent / raw_path
    if target.is_dir():
        target = target / "index.html"
    return target


def external_hosts(refs: list[str]) -> set[str]:
    hosts: set[str] = set()
    for ref in refs:
        parsed = urlparse(ref.strip())
        if parsed.scheme in {"http", "https"} and parsed.hostname:
            hosts.add(parsed.hostname.lower())
    return hosts


def validate_site(site_root: Path, config_path: Path, schema_path: Path) -> dict:
    config = load_json(config_path)
    schema = load_json(schema_path)
    schema_errors = list(Draft202012Validator(schema).iter_errors(config))
    if schema_errors:
        raise RuntimeError("Invalid web-quality config: " + "; ".join(error.message for error in schema_errors))

    errors: list[str] = []
    measurements: dict[str, object] = {"routes": {}}
    global_cfg = config["global"]
    allowed_hosts = set(global_cfg["allowedExternalHosts"])

    all_files = [path for path in site_root.rglob("*") if path.is_file()]
    total_bytes = sum(path.stat().st_size for path in all_files)
    max_file = max((path.stat().st_size for path in all_files), default=0)
    measurements["publishedTreeBytes"] = total_bytes
    measurements["largestPublishedFileBytes"] = max_file
    measurements["publishedFileCount"] = len(all_files)

    if total_bytes > global_cfg["maxPublishedTreeBytes"]:
        errors.append(f"published tree is {total_bytes} bytes; budget is {global_cfg['maxPublishedTreeBytes']}")
    if max_file > global_cfg["maxSinglePublishedFileBytes"]:
        errors.append(f"largest published file is {max_file} bytes; budget is {global_cfg['maxSinglePublishedFileBytes']}")
    if not global_cfg["zipFilesPermitted"]:
        zip_paths = [path.relative_to(site_root).as_posix() for path in all_files if path.suffix.lower() == ".zip"]
        if zip_paths:
            errors.append("ZIP files are not permitted in the Pages tree: " + ", ".join(zip_paths))

    for route in config["routes"]:
        route_id = route["id"]
        html_path = site_root / route["htmlFile"]
        route_result: dict[str, object] = {"htmlFile": route["htmlFile"]}
        measurements["routes"][route_id] = route_result
        if not html_path.is_file():
            errors.append(f"{route_id}: missing {route['htmlFile']}")
            continue

        html_bytes = html_path.stat().st_size
        route_result["htmlBytes"] = html_bytes
        if html_bytes > route["maxHtmlBytes"]:
            errors.append(f"{route_id}: HTML is {html_bytes} bytes; budget is {route['maxHtmlBytes']}")

        text = html_path.read_text(encoding="utf-8")
        parser = SiteParser()
        parser.feed(text)
        if not parser.html_attrs.get("lang", "").strip():
            errors.append(f"{route_id}: <html> must declare lang")
        if not parser.has_viewport:
            errors.append(f"{route_id}: viewport meta tag is required")
        if not parser.title_text.strip():
            errors.append(f"{route_id}: non-empty <title> is required")
        if parser.importmap_errors:
            errors.append(f"{route_id}: invalid import map: {'; '.join(parser.importmap_errors)}")

        for forbidden in global_cfg["forbiddenUrlFragments"]:
            matching = [ref for ref in parser.refs if forbidden in ref]
            if matching:
                errors.append(f"{route_id}: runtime references contain forbidden fragment {forbidden!r}: {matching}")

        hosts = external_hosts(parser.refs)
        route_result["externalHosts"] = sorted(hosts)
        unexpected = sorted(hosts - allowed_hosts)
        if unexpected:
            errors.append(f"{route_id}: external runtime hosts not allowlisted: {', '.join(unexpected)}")

        missing_refs: list[str] = []
        local_refs: list[str] = []
        for ref in parser.refs:
            target = local_target(site_root, html_path, ref)
            if target is None:
                continue
            local_refs.append(ref)
            if not target.exists():
                missing_refs.append(ref)
        route_result["localReferenceCount"] = len(local_refs)
        route_result["missingLocalReferences"] = missing_refs
        if missing_refs:
            errors.append(f"{route_id}: missing local references: {', '.join(missing_refs)}")

    return {
        "schemaVersion": "1.0.0",
        "status": "pass" if not errors else "fail",
        "authority": "repository-software-qa",
        "siteRoot": str(site_root),
        "config": str(config_path),
        "measurements": measurements,
        "errors": errors,
        "notes": [
            "This report validates published software artifacts only.",
            "It does not qualify VX4800 engineering, manufacturing, photometry, installation or certification."
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the built AETHERIA Pages tree against repository web-quality budgets")
    parser.add_argument("site_root", type=Path)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    report = validate_site(args.site_root.resolve(), args.config.resolve(), args.schema.resolve())
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
