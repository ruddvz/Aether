from __future__ import annotations

import ast
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLENDER = ROOT / "blender/vx4800"
SPDX_GPL_RE = re.compile(r"^\s*#\s*SPDX-License-Identifier:\s*GPL-3\.0-or-later\s*$")


def fail(message: str) -> None:
    raise SystemExit(message)


def has_gpl_spdx_header(source: str) -> bool:
    return any(SPDX_GPL_RE.match(line) for line in source.splitlines()[:3])


def main() -> None:
    manifest = json.loads((BLENDER / "scene_manifest.json").read_text())
    presets = json.loads((BLENDER / "render_presets.json").read_text())
    if manifest.get("fixtureId") != "vx4800-bf-01": fail("Blender manifest fixtureId mismatch")
    if manifest.get("designRevision") != "1.3.0": fail("Blender manifest designRevision mismatch")
    if manifest.get("authority") != "visualization-only": fail("Blender manifest authority must be visualization-only")
    if manifest.get("blenderTarget") != "5.2.1 LTS": fail("Blender target must remain pinned to 5.2.1 LTS")
    for key, rel in manifest.get("sources", {}).items():
        if not (ROOT / rel).is_file(): fail(f"Blender source {key} does not exist: {rel}")
    for path in BLENDER.glob("*.py"):
        source = path.read_text(); ast.parse(source, filename=str(path))
        if not has_gpl_spdx_header(source): fail(f"Blender API script lacks GPL-compatible SPDX header: {path}")
    with (ROOT / manifest["sources"]["composition"]).open(newline="") as f: rows = list(csv.DictReader(f))
    if len(rows) != 240: fail(f"Blender pipeline expected 240 controlled composition rows, got {len(rows)}")
    counts = {"S": 0, "M": 0, "L": 0}
    for row in rows:
        if row["size"] not in counts: fail(f"Unexpected size in controlled schedule: {row['size']}")
        counts[row["size"]] += 1
    if counts != {"S": 66, "M": 144, "L": 30}: fail(f"Controlled Blender source size counts mismatch: {counts}")
    with (ROOT / manifest["sources"]["ledSetout"]).open(newline="") as f: led_rows = list(csv.DictReader(f))
    if len(led_rows) != 14: fail(f"Blender pipeline expected 14 fixed LED positions, got {len(led_rows)}")
    required_presets = {"preview", "hero", "social_vertical", "detail_square"}
    if set(presets) - {"schemaVersion"} != required_presets: fail("Blender render preset set changed unexpectedly")
    required_cameras = {
        "CAM_HERO_FRONT_3Q", "CAM_HERO_LOW", "CAM_FULL_ELEVATION", "CAM_CANOPY_DETAIL",
        "CAM_BUTTERFLY_MACRO", "CAM_TAIL_DETAIL", "CAM_TOP_SET_OUT",
        "CAM_ARCH_RESIDENTIAL_WIDE", "CAM_ARCH_RESIDENTIAL_MEDIUM", "CAM_VERTICAL_MARKETING",
    }
    if set(manifest.get("cameraShots", {})) != required_cameras: fail("Blender camera-shot manifest is incomplete")
    if "85_ENV_RESIDENTIAL" not in manifest.get("collections", []): fail("Residential Blender environment collection is missing from manifest")
    print("Blender source QA: PASS")
    print(f"- controlled butterflies: {len(rows)} ({counts})")
    print(f"- fixed LED positions: {len(led_rows)}")
    print(f"- cameras: {len(required_cameras)}")
    print(f"- render presets: {len(required_presets)}")


if __name__ == "__main__": main()
