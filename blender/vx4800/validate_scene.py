# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import argparse
import json
from pathlib import Path

import bpy


def cli_args() -> argparse.Namespace:
    argv = __import__("sys").argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--report", default=None)
    return p.parse_args(argv)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> None:
    args = cli_args()
    errors: list[str] = []
    scene = bpy.context.scene

    if tuple(bpy.app.version) < (5, 2, 0):
        fail(errors, f"Blender {bpy.app.version_string} is older than the 5.2 pipeline target")
    if scene.get("aetheria_fixture_id") != "vx4800-bf-01": fail(errors, "scene fixture id is missing or incorrect")
    if scene.get("aetheria_design_revision") != "1.3.0": fail(errors, "scene design revision is missing or incorrect")
    if scene.get("aetheria_visualization_revision") != "0.11.0": fail(errors, "scene visualization revision must be 0.11.0")
    if scene.get("aetheria_authority") != "visualization-only": fail(errors, "scene authority must remain visualization-only")

    instances = [o for o in bpy.data.objects if o.instance_type == "COLLECTION" and o.instance_collection and o.name.startswith("VX-")]
    if len(instances) != 240: fail(errors, f"expected 240 butterfly instances, found {len(instances)}")
    ids = [o.get("element_id") for o in instances]
    if len(set(ids)) != 240 or any(not x for x in ids): fail(errors, "butterfly element IDs are missing or duplicated")
    counts = {"S": 0, "M": 0, "L": 0}
    for o in instances:
        size = o.get("size")
        if size in counts: counts[size] += 1
        else: fail(errors, f"invalid butterfly size on {o.name}: {size}")
    if counts != {"S": 66, "M": 144, "L": 30}: fail(errors, f"engineering size allocation mismatch: {counts}")

    cables = bpy.data.objects.get("SUSPENSION_MICROCABLES_240")
    if not cables or cables.type != "CURVE": fail(errors, "combined suspension curve is missing")
    elif len(cables.data.splines) != 240: fail(errors, f"expected 240 suspension splines, found {len(cables.data.splines)}")
    yokes = bpy.data.objects.get("SUSPENSION_YOKES_240")
    if not yokes or yokes.type != "CURVE": fail(errors, "combined suspension yoke curve is missing")
    elif len(yokes.data.splines) != 720: fail(errors, f"expected 720 yoke/lead splines, found {len(yokes.data.splines)}")

    led_heads = [o for o in bpy.data.objects if o.name.startswith("LED_HEAD_") and not o.name.endswith("_LENS")]
    if len(led_heads) != 14: fail(errors, f"expected 14 LED head bodies, found {len(led_heads)}")
    render_lights = [o for o in bpy.data.objects if o.name.startswith("RENDER_LIGHT_")]
    if len(render_lights) != 14: fail(errors, f"expected 14 conceptual render lights, found {len(render_lights)}")
    for light in render_lights:
        if light.get("aetheria_photometry_status") != "conceptual-render-only": fail(errors, f"{light.name} is missing conceptual photometry status")

    camera_names = {
        "CAM_HERO_FRONT_3Q", "CAM_HERO_LOW", "CAM_FULL_ELEVATION", "CAM_CANOPY_DETAIL",
        "CAM_BUTTERFLY_MACRO", "CAM_TAIL_DETAIL", "CAM_TOP_SET_OUT",
        "CAM_ARCH_RESIDENTIAL_WIDE", "CAM_ARCH_RESIDENTIAL_MEDIUM", "CAM_VERTICAL_MARKETING",
    }
    missing_cameras = sorted(camera_names - set(bpy.data.objects.keys()))
    if missing_cameras: fail(errors, f"missing cameras: {missing_cameras}")

    material_names = {
        "MAT_BUTTERFLY_OPTICAL_GLASS", "MAT_PVD_DARK_CHAMPAGNE", "MAT_PVD_BLACK_TITANIUM",
        "MAT_BRUSHED_BRASS", "MAT_SATIN_NICKEL", "MAT_CABLE_STAINLESS",
        "MAT_BUTTERFLY_BODY_CHAMPAGNE", "MAT_LED_HEAD_TITANIUM", "MAT_LED_LENS_3000K", "MAT_STAGE_IVORY",
    }
    missing_materials = sorted(material_names - set(bpy.data.materials.keys()))
    if missing_materials: fail(errors, f"missing materials: {missing_materials}")

    glass = bpy.data.materials.get("MAT_BUTTERFLY_OPTICAL_GLASS")
    absorption_density = None
    if glass and glass.use_nodes and glass.node_tree:
        absorption = glass.node_tree.nodes.get("AETHERIA_EDGE_ABSORPTION")
        if absorption and absorption.inputs.get("Density"):
            absorption_density = float(absorption.inputs["Density"].default_value)
    if absorption_density is None or abs(absorption_density - 3.5) > 1e-6:
        fail(errors, f"expected visualization glass absorption density 3.5, found {absorption_density}")

    spines = [o for o in bpy.data.objects if o.name.startswith("CENTRAL_SPINE")]
    if len(spines) != 3: fail(errors, f"expected 3 linked prototype spine objects, found {len(spines)}")
    for spine in spines:
        if spine.get("aetheria_spine_refinement") != "0.11-smaller-sculptural-centre":
            fail(errors, f"{spine.name} is missing 0.11 spine refinement metadata")

    env = bpy.data.collections.get("85_ENV_RESIDENTIAL")
    env_objects = list(env.all_objects) if env else []
    if not env: fail(errors, "residential visualization environment collection is missing")
    elif len(env_objects) < 20: fail(errors, f"residential environment is unexpectedly sparse: {len(env_objects)} objects")
    for obj in env_objects:
        if obj.get("aetheria_authority") != "visualization-only":
            fail(errors, f"residential environment object lacks visualization-only authority: {obj.name}")
    env_lights = [o for o in env_objects if o.type == "LIGHT" and o.name.startswith("ENV_RES_")]
    if len(env_lights) != 4: fail(errors, f"expected 4 residential photographic environment lights, found {len(env_lights)}")

    rotor = bpy.data.objects.get("AETHERIA_ROTATING_FIELD")
    animation_action = rotor.animation_data.action if rotor and rotor.animation_data else None
    if rotor is None: fail(errors, "rotating field root is missing")
    elif rotor.get("motion_status") != "conceptual-reference-only": fail(errors, "rotating field motion must remain conceptual-reference-only")
    if not animation_action or animation_action.name != "PHYSICAL_NOMINAL_RPM_REFERENCE":
        fail(errors, "derived nominal-RPM animation reference action is missing")
    if scene.get("aetheria_animation_reference_status") != "visualization-only-constant-speed-reference":
        fail(errors, "animation reference authority/status is missing")
    if int(scene.get("aetheria_animation_reference_cycle_frames", 0)) <= 0:
        fail(errors, "animation reference cycle frame count is missing")

    source_sha_keys = [k for k in scene.keys() if str(k).startswith("source_sha256_")]
    if len(source_sha_keys) < 5: fail(errors, "source SHA-256 provenance is incomplete")

    report = {
        "status": "fail" if errors else "pass",
        "blenderVersion": bpy.app.version_string,
        "fixtureId": scene.get("aetheria_fixture_id"),
        "designRevision": scene.get("aetheria_design_revision"),
        "visualizationRevision": scene.get("aetheria_visualization_revision"),
        "authority": scene.get("aetheria_authority"),
        "butterflyInstances": len(instances),
        "sizeCounts": counts,
        "suspensionSplines": len(cables.data.splines) if cables and cables.type == "CURVE" else 0,
        "yokeLeadSplines": len(yokes.data.splines) if yokes and yokes.type == "CURVE" else 0,
        "ledHeads": len(led_heads),
        "renderLights": len(render_lights),
        "cameras": len([o for o in bpy.data.objects if o.type == "CAMERA"]),
        "materials": len(bpy.data.materials),
        "glassAbsorptionDensity": absorption_density,
        "refinedSpines": len(spines),
        "animationAction": animation_action.name if animation_action else None,
        "animationCycleFrames": scene.get("aetheria_animation_reference_cycle_frames"),
        "residentialEnvironmentObjects": len(env_objects),
        "residentialEnvironmentLights": len(env_lights),
        "errors": errors,
    }
    if args.report:
        path = Path(args.report).resolve(); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if errors: raise SystemExit(1)


if __name__ == "__main__":
    main()
