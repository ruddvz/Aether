# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy

from aether_blender_lib import (
    MM, add_beveled_rounded_box, add_poly_spline, build_materials, build_stage,
    clear_scene, configure_scene, create_area_light, create_camera, create_curve_object,
    create_led_head, create_spot_light, ensure_collection, make_butterfly_prototype, read_csv,
    read_json, sha256,
)

VISUALIZATION_REVISION = "0.3.0"
BLENDER_TARGET = "5.2.1 LTS"


def cli_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    p = argparse.ArgumentParser(description="Build AETHERIA VX4800 Blender visualization master")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--output", default="blender/vx4800/VX4800_MASTER.blend")
    p.add_argument("--render-preview", default=None)
    return p.parse_args(argv)


def build_scene(repo_root: Path, output: Path, render_preview: Path | None = None) -> Path:
    manifest_path = repo_root / "blender/vx4800/scene_manifest.json"
    preset_path = repo_root / "blender/vx4800/render_presets.json"
    manifest = read_json(manifest_path)
    _presets = read_json(preset_path)

    source_paths = {k: repo_root / v for k, v in manifest["sources"].items()}
    fixture = read_json(source_paths["fixture"])
    params = read_json(source_paths["geometryParameters"])
    schedule = read_csv(source_paths["composition"])
    leds = read_csv(source_paths["ledSetout"])
    lighting = read_json(source_paths["lightingStudy"])

    if len(schedule) != 240:
        raise RuntimeError(f"Expected 240 engineering elements, got {len(schedule)}")
    if len(leds) != 14:
        raise RuntimeError(f"Expected 14 fixed LED positions, got {len(leds)}")

    clear_scene()
    scene = bpy.context.scene
    configure_scene(scene)

    scene["aetheria_fixture_id"] = fixture["identity"]["fixtureId"]
    scene["aetheria_product_code"] = fixture["identity"]["productCode"]
    scene["aetheria_design_revision"] = fixture["identity"]["designRevision"]
    scene["aetheria_visualization_revision"] = VISUALIZATION_REVISION
    scene["aetheria_blender_target"] = BLENDER_TARGET
    scene["aetheria_authority"] = "visualization-only"
    scene["aetheria_optical_material_status"] = "visualization-study-not-commercially-locked"
    scene["aetheria_fixture_photometry_status"] = "conceptual-render-only-until-controlled-supplier-photometry"
    scene["aetheria_stage_lighting_status"] = "photographic-visualization-only"
    for key, path in source_paths.items():
        scene[f"source_sha256_{key}"] = sha256(path)

    root = bpy.data.collections.get("AETHERIA_VX4800") or ensure_collection("AETHERIA_VX4800")
    collections = {name: ensure_collection(name, root) for name in manifest["collections"]}
    mats = build_materials()

    canopy_params = params["canopy"]
    carrier_params = params["rotatingCarrier"]
    canopy = add_beveled_rounded_box(
        "CANOPY_FIXED",
        collections["10_CANOPY_FIXED"],
        canopy_params["widthMm"] * MM,
        canopy_params["depthMm"] * MM,
        canopy_params["heightMm"] * MM,
        canopy_params["cornerRadiusMm"] * MM,
        mats["champagne"],
        z=0.0,
        edge_bevel=0.007,
    )
    canopy["aetheria_authority"] = "visualization-derived-from-controlled-envelope"

    rotor_root = bpy.data.objects.new("AETHERIA_ROTATING_FIELD", None)
    collections["20_ROTATING_FIELD"].objects.link(rotor_root)
    rotor_root.empty_display_type = "CIRCLE"
    rotor_root.empty_display_size = 0.45
    rotor_root["motion_status"] = "conceptual"
    rotor_root["nominal_rpm"] = fixture["kinematics"]["speedRpm"]["nominal"]

    carrier = add_beveled_rounded_box(
        "ROTATING_CARRIER_VISUAL",
        collections["20_ROTATING_FIELD"],
        carrier_params["widthMm"] * MM,
        carrier_params["depthMm"] * MM,
        carrier_params["thicknessMm"] * MM,
        carrier_params["cornerRadiusMm"] * MM,
        mats["black_titanium"],
        z=-carrier_params["thicknessMm"] * MM,
        edge_bevel=0.004,
    )
    carrier.parent = rotor_root
    carrier["aetheria_authority"] = "visualization-derived-from-controlled-envelope"

    rotor_root.rotation_euler.z = 0.0
    rotor_root.keyframe_insert(data_path="rotation_euler", index=2, frame=1)
    rotor_root.rotation_euler.z = math.tau
    rotor_root.keyframe_insert(data_path="rotation_euler", index=2, frame=4001)
    if rotor_root.animation_data and rotor_root.animation_data.action:
        action = rotor_root.animation_data.action
        action.name = "PHYSICAL_NOMINAL_0_36RPM_REFERENCE"
        try:
            for fcurve in action.fcurves:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = "LINEAR"
        except Exception:
            pass
    rotor_root.rotation_euler.z = 0.0

    prototypes: dict[str, bpy.types.Collection] = {}
    for size, d in params["butterflies"].items():
        prototypes[size] = make_butterfly_prototype(
            size,
            d["spanMm"] * MM,
            d["lengthMm"] * MM,
            d["thicknessMm"] * MM,
            42.0,
            mats,
        )

    cables = create_curve_object(
        "SUSPENSION_MICROCABLES_240",
        collections["30_SUSPENSION"],
        mats["cable"],
        bevel_depth=0.00018,
    )
    cables.parent = rotor_root
    cables["aetheria_authority"] = "visualization-derived-from-controlled-schedule"
    cables["aetheria_curve_diameter_status"] = "visualization-only-not-rated-suspension-diameter"

    yokes = create_curve_object(
        "SUSPENSION_YOKES_240",
        collections["30_SUSPENSION"],
        mats["body"],
        bevel_depth=0.00028,
    )
    yokes.parent = rotor_root
    yokes["aetheria_authority"] = "visualization-yoke-detail"
    yokes["aetheria_curve_diameter_status"] = "visualization-only-not-rated-hardware-diameter"

    size_counts = {"S": 0, "M": 0, "L": 0}
    for row in schedule:
        element_id = row["element_id"]
        size = row["size"]
        size_counts[size] += 1
        x = float(row["ceiling_x_mm"]) * MM
        y = float(row["ceiling_y_mm"]) * MM
        drop = float(row["element_origin_drop_mm"]) * MM
        yoke_drop = float(row["yoke_drop_mm"]) * MM
        yaw = math.radians(float(row["target_yaw_deg"]))
        fold = float(row["wing_fold_deg"])

        inst = bpy.data.objects.new(element_id, None)
        inst.instance_type = "COLLECTION"
        inst.instance_collection = prototypes[size]
        collections["40_BUTTERFLIES"].objects.link(inst)
        inst.location = (x, y, -drop)
        inst.rotation_euler.z = yaw
        inst.parent = rotor_root
        inst["element_id"] = element_id
        inst["size"] = size
        inst["ceiling_x_mm"] = float(row["ceiling_x_mm"])
        inst["ceiling_y_mm"] = float(row["ceiling_y_mm"])
        inst["element_origin_drop_mm"] = float(row["element_origin_drop_mm"])
        inst["finished_main_cable_mm"] = float(row["finished_main_cable_mm"])
        inst["target_yaw_deg"] = float(row["target_yaw_deg"])
        inst["wing_fold_deg"] = fold
        inst["authority"] = "visualization-instance-from-controlled-schedule"

        add_poly_spline(cables, [(x, y, -0.024), (x, y, -yoke_drop)])

        ux, uy = math.cos(yaw), math.sin(yaw)
        half_bar = 0.015
        half_attach = 0.006
        yoke_left = (x - half_bar * ux, y - half_bar * uy, -yoke_drop)
        yoke_right = (x + half_bar * ux, y + half_bar * uy, -yoke_drop)
        attach_z = -drop + 0.012
        attach_left = (x - half_attach * ux, y - half_attach * uy, attach_z)
        attach_right = (x + half_attach * ux, y + half_attach * uy, attach_z)
        add_poly_spline(yokes, [yoke_left, yoke_right])
        add_poly_spline(yokes, [yoke_left, attach_left])
        add_poly_spline(yokes, [yoke_right, attach_right])

    expected_counts = {f["id"]: f["count"] for f in fixture["composition"]["families"]}
    if size_counts != expected_counts:
        raise RuntimeError(f"Butterfly size counts {size_counts} do not match fixture {expected_counts}")

    lighting_heads = lighting["heads"]
    for i, row in enumerate(leds):
        x = float(row["x_mm"]) * MM
        y = float(row["y_mm"]) * MM
        body = create_led_head(
            f"LED_HEAD_{i+1:02d}", x, y, mats["led_head"], mats["led_lens"],
            collections["50_LED_HEADS_FIXED"],
        )
        body["controlled_led_id"] = row["led_id"]
        body["supplier_status"] = "unselected"
        body["authority"] = "visual-placeholder-at-controlled-position"

        h = lighting_heads[i]
        target = (float(h["targetX"]), -float(h["targetZ"]), float(h["targetY"]))
        energy = {"narrow": 105.0, "spot": 78.0, "flood": 58.0}.get(h["kind"], 70.0)
        spot = create_spot_light(
            f"RENDER_LIGHT_{i+1:02d}_{h['kind'].upper()}",
            (x, y, -0.070), target, float(h["beam"]), energy,
            collections["70_LIGHT_RIGS"],
        )
        spot["controlled_led_id"] = row["led_id"]
        spot["visual_role"] = h["kind"]

    cameras = {}
    for name, spec in manifest["cameraShots"].items():
        cameras[name] = create_camera(
            name, spec["location"], spec["target"], spec["lensMm"], collections["60_CAMERAS"]
        )
    scene.camera = cameras["CAM_HERO_FRONT_3Q"]

    build_stage(mats, collections["80_RENDER_STAGE"])
    target = (0.0, 0.0, -2.35)
    create_area_light(
        "RIG_KEY", (4.8, -5.8, 2.2), target, 1180, 3.8, (1.0, 0.90, 0.79),
        collections["70_LIGHT_RIGS"], shape="DISK", spread_deg=110,
    )
    create_area_light(
        "RIG_FILL", (-5.5, -3.2, -0.9), target, 300, 4.8, (0.78, 0.86, 1.0),
        collections["70_LIGHT_RIGS"], shape="DISK", spread_deg=120,
    )
    create_area_light(
        "RIG_RIM_RIGHT", (5.1, 3.2, -0.4), target, 1320, 2.8, (1.0, 0.78, 0.58),
        collections["70_LIGHT_RIGS"], shape="RECTANGLE", size_y=0.55, spread_deg=88,
    )
    create_area_light(
        "RIG_RIM_LEFT", (-5.0, 3.0, -2.5), target, 1020, 2.6, (0.72, 0.82, 1.0),
        collections["70_LIGHT_RIGS"], shape="RECTANGLE", size_y=0.48, spread_deg=88,
    )
    create_area_light(
        "RIG_TOP", (0.0, -0.8, 5.0), (0.0, 0.0, -1.25), 540, 4.2, (1.0, 0.94, 0.86),
        collections["70_LIGHT_RIGS"], shape="DISK", spread_deg=100,
    )

    for proto in prototypes.values():
        proto["aetheria_role"] = "linked_butterfly_prototype"
        proto["authority"] = "visualization-only"

    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output))

    if render_preview is not None:
        render_preview.parent.mkdir(parents=True, exist_ok=True)
        scene.render.engine = "BLENDER_EEVEE_NEXT"
        scene.render.resolution_x = 1280
        scene.render.resolution_y = 720
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_depth = "8"
        scene.render.filepath = str(render_preview)
        scene.camera = cameras["CAM_HERO_FRONT_3Q"]
        bpy.ops.render.render(write_still=True)

    print(f"AETHERIA Blender master saved: {output}")
    return output


def main() -> None:
    args = cli_args()
    repo_root = Path(args.repo_root).resolve()
    output = (repo_root / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    preview = None
    if args.render_preview:
        preview = (repo_root / args.render_preview).resolve() if not Path(args.render_preview).is_absolute() else Path(args.render_preview)
    build_scene(repo_root, output, preview)


if __name__ == "__main__":
    main()
