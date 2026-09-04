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
    qualities = json.loads((BLENDER / "render_quality.json").read_text())
    output_profiles = json.loads((BLENDER / "output_profiles.json").read_text())
    shot_catalogue = json.loads((BLENDER / "shot_catalogue.json").read_text())

    if manifest.get("fixtureId") != "vx4800-bf-01": fail("Blender manifest fixtureId mismatch")
    if manifest.get("designRevision") != "1.3.0": fail("Blender manifest designRevision mismatch")
    if manifest.get("visualizationRevision") != "0.12.0": fail("Blender manifest visualizationRevision mismatch")
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
    if set(presets) - {"schemaVersion"} != required_presets: fail("Legacy Blender render preset set changed unexpectedly")
    required_qualities = {"draft", "lookdev", "production", "hero"}
    if set(qualities) - {"schemaVersion"} != required_qualities: fail("Blender quality tier set is incomplete")
    required_output_profiles = {"landscape_preview", "landscape_4k", "vertical_preview", "vertical_4k", "square_preview", "square_detail"}
    if set(output_profiles) - {"schemaVersion"} != required_output_profiles: fail("Blender output profile set is incomplete")

    required_cameras = {
        "CAM_HERO_FRONT_3Q", "CAM_HERO_LOW", "CAM_FULL_ELEVATION", "CAM_CANOPY_DETAIL",
        "CAM_BUTTERFLY_MACRO", "CAM_TAIL_DETAIL", "CAM_TOP_SET_OUT",
        "CAM_ARCH_RESIDENTIAL_WIDE", "CAM_ARCH_RESIDENTIAL_MEDIUM", "CAM_VERTICAL_MARKETING",
        "CAM_ARCH_STAIRCASE_WIDE", "CAM_ARCH_HOSPITALITY_WIDE", "CAM_ARCH_ATRIUM_WIDE",
    }
    if set(manifest.get("cameraShots", {})) != required_cameras: fail("Blender camera-shot manifest is incomplete")
    required_environment_collections = {"85_ENV_RESIDENTIAL", "86_ENV_STAIRCASE", "87_ENV_HOSPITALITY", "88_ENV_ATRIUM"}
    if not required_environment_collections.issubset(set(manifest.get("collections", []))):
        fail("Blender architectural environment collections are incomplete in manifest")

    finish_variants = manifest.get("finishVariants", [])
    if finish_variants != ["dark_champagne", "black_titanium", "brushed_brass", "satin_nickel"]:
        fail("Blender finish-variant set changed unexpectedly")

    shots = shot_catalogue.get("shots", {})
    if len(shots) != 13: fail(f"Expected 13 named Blender shots, found {len(shots)}")
    shot_cameras = {shot.get("camera") for shot in shots.values()}
    if shot_cameras != required_cameras: fail("Named shot catalogue must cover every manifest camera exactly once")
    for name, shot in shots.items():
        quality = shot.get("defaultQuality")
        default_profile = shot.get("defaultOutputProfile")
        preview_profile = shot.get("previewOutputProfile")
        aspect = shot.get("aspect")
        if quality not in required_qualities: fail(f"Shot {name} references invalid quality tier: {quality}")
        for profile_name in (default_profile, preview_profile):
            if profile_name not in required_output_profiles: fail(f"Shot {name} references invalid output profile: {profile_name}")
            if output_profiles[profile_name].get("aspect") != aspect:
                fail(f"Shot {name} aspect does not match output profile {profile_name}")
        if shot.get("fixtureLights") is not False:
            fail(f"Baseline named shot {name} must keep conceptual fixture beams suppressed")

    print("Blender source QA: PASS")
    print(f"- controlled butterflies: {len(rows)} ({counts})")
    print(f"- fixed LED positions: {len(led_rows)}")
    print(f"- cameras: {len(required_cameras)}")
    print(f"- named shots: {len(shots)}")
    print(f"- architectural environments: {len(required_environment_collections)}")
    print(f"- finish variants: {len(finish_variants)}")
    print(f"- quality tiers: {len(required_qualities)}")
    print(f"- output profiles: {len(required_output_profiles)}")
    print(f"- legacy render presets: {len(required_presets)}")


if __name__ == "__main__": main()
