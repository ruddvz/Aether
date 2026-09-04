# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import bpy

from aether_blender_lib import (
    create_area_light,
    ensure_collection,
    link_object,
    make_emission_material,
    principled_material,
    set_socket,
)

VISUALIZATION_REVISION = "0.9.0"
ENVIRONMENT_ID = "residential-double-height"
ENV_COLLECTION = "85_ENV_RESIDENTIAL"
ENV_LIGHT_PREFIX = "ENV_RES_"
ARCH_CAMERAS = {
    "CAM_ARCH_RESIDENTIAL_WIDE",
    "CAM_ARCH_RESIDENTIAL_MEDIUM",
    "CAM_VERTICAL_MARKETING",
}


def _mark_material(material: bpy.types.Material, role: str) -> bpy.types.Material:
    material["aetheria_authority"] = "visualization-only"
    material["aetheria_environment_id"] = ENVIRONMENT_ID
    material["aetheria_environment_material_role"] = role
    material.use_fake_user = True
    return material


def _environment_materials() -> dict[str, bpy.types.Material]:
    plaster = _mark_material(
        principled_material("MAT_ENV_RES_PLASTER", "#A79E93", 0.0, 0.82),
        "warm-mineral-plaster",
    )
    limestone = _mark_material(
        principled_material("MAT_ENV_RES_LIMESTONE", "#4C4945", 0.0, 0.38),
        "honed-dark-limestone-floor",
    )
    feature_stone = _mark_material(
        principled_material("MAT_ENV_RES_FEATURE_STONE", "#302D2B", 0.0, 0.50),
        "charcoal-warm-stone-feature-wall",
    )
    walnut = _mark_material(
        principled_material("MAT_ENV_RES_WALNUT", "#2A1B14", 0.0, 0.30, coat=0.035),
        "dark-walnut-joinery",
    )
    textile = _mark_material(
        principled_material("MAT_ENV_RES_TEXTILE", "#55504A", 0.0, 0.80),
        "warm-grey-upholstery-textile",
    )
    rug = _mark_material(
        principled_material("MAT_ENV_RES_RUG", "#777067", 0.0, 0.90),
        "woven-rug",
    )
    glass = _mark_material(
        principled_material(
            "MAT_ENV_RES_WINDOW_GLASS",
            "#DDE9EE",
            0.0,
            0.10,
            transmission=1.0,
            ior=1.45,
        ),
        "architectural-glazing-visual-study",
    )
    sky = _mark_material(
        make_emission_material("MAT_ENV_RES_SKY_CARD", "#7898B3", 0.28),
        "daylight-view-card",
    )
    return {
        "plaster": plaster,
        "limestone": limestone,
        "feature_stone": feature_stone,
        "walnut": walnut,
        "textile": textile,
        "rug": rug,
        "glass": glass,
        "sky": sky,
    }


def _tag_object(obj: bpy.types.Object, role: str) -> bpy.types.Object:
    obj["aetheria_authority"] = "visualization-only"
    obj["aetheria_environment_id"] = ENVIRONMENT_ID
    obj["aetheria_environment_role"] = role
    obj.hide_render = True
    return obj


def _cube(
    name: str,
    collection: bpy.types.Collection,
    dimensions: tuple[float, float, float],
    location: tuple[float, float, float],
    material: bpy.types.Material,
    role: str,
    bevel: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    link_object(obj, collection)
    obj.dimensions = dimensions
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel > 0.0:
        mod = obj.modifiers.new("AETHERIA_ENV_EDGE", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
    return _tag_object(obj, role)


def _build_room_shell(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> None:
    # Visualization-only installation volume. The controlled fixture remains at its
    # canonical coordinates. Floor/ceiling positions exist only to establish scale.
    _cube("ENV_RES_FLOOR", collection, (11.4, 18.0, 0.16), (0.0, 0.2, -6.08), mats["limestone"], "floor", 0.012)
    _cube("ENV_RES_CEILING", collection, (11.4, 12.6, 0.22), (0.0, 0.1, 0.26), mats["plaster"], "flat-mounting-ceiling", 0.010)
    _cube("ENV_RES_BACK_WALL", collection, (11.4, 0.20, 6.15), (0.0, 5.8, -2.925), mats["plaster"], "back-wall", 0.012)

    # The darker central stone zone is positioned behind the controlled vortex so
    # transparent edges remain legible without changing any fixture coordinates.
    _cube("ENV_RES_FEATURE_WALL", collection, (4.85, 0.075, 5.35), (0.15, 5.67, -3.02), mats["feature_stone"], "vortex-contrast-stone-zone", 0.010)
    for index, x in enumerate((3.05, 3.38, 3.71, 4.04, 4.37, 4.70, 5.03), start=1):
        _cube(
            f"ENV_RES_WALNUT_SLAT_{index:02d}",
            collection,
            (0.24, 0.085, 4.85),
            (x, 5.655, -3.14),
            mats["walnut"],
            "vertical-walnut-joinery",
            0.012,
        )
    _cube("ENV_RES_RIGHT_WALL", collection, (0.20, 4.6, 6.15), (5.6, 3.5, -2.925), mats["plaster"], "partial-side-wall", 0.012)

    _cube("ENV_RES_LEFT_FRONT_PIER", collection, (0.22, 1.45, 6.15), (-5.6, -4.75, -2.925), mats["plaster"], "window-pier", 0.010)
    _cube("ENV_RES_LEFT_REAR_PIER", collection, (0.22, 1.45, 6.15), (-5.6, 5.05, -2.925), mats["plaster"], "window-pier", 0.010)
    _cube("ENV_RES_LEFT_HEAD", collection, (0.22, 8.4, 0.52), (-5.6, 0.15, -0.11), mats["plaster"], "window-head", 0.010)
    _cube("ENV_RES_WINDOW_GLASS", collection, (0.035, 8.0, 5.20), (-5.47, 0.15, -3.10), mats["glass"], "floor-to-ceiling-glazing", 0.002)
    _cube("ENV_RES_SKY_CARD", collection, (0.025, 8.4, 5.55), (-5.72, 0.15, -3.05), mats["sky"], "exterior-daylight-card")

    metal = bpy.data.materials.get("MAT_PVD_DARK_CHAMPAGNE")
    if metal is None:
        raise RuntimeError("MAT_PVD_DARK_CHAMPAGNE is missing")
    for index, y in enumerate((-2.50, 0.15, 2.80), start=1):
        _cube(
            f"ENV_RES_WINDOW_MULLION_{index:02d}",
            collection,
            (0.055, 0.055, 5.20),
            (-5.43, y, -3.10),
            metal,
            "window-mullion",
            0.006,
        )


def _build_furniture(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> None:
    # Furniture stays outside the central chandelier footprint and exists only for
    # architectural scale/photographic composition.
    _cube("ENV_RES_RUG", collection, (3.8, 2.7, 0.025), (-3.25, 1.35, -5.975), mats["rug"], "rug", 0.008)
    _cube("ENV_RES_SOFA_BASE", collection, (3.15, 0.96, 0.32), (-3.45, 3.05, -5.82), mats["textile"], "sofa-base", 0.12)
    _cube("ENV_RES_SOFA_BACK", collection, (3.15, 0.23, 0.90), (-3.45, 3.42, -5.48), mats["textile"], "sofa-back", 0.12)
    _cube("ENV_RES_SOFA_ARM_L", collection, (0.22, 0.96, 0.58), (-4.91, 3.05, -5.68), mats["textile"], "sofa-arm", 0.09)
    _cube("ENV_RES_SOFA_ARM_R", collection, (0.22, 0.96, 0.58), (-1.99, 3.05, -5.68), mats["textile"], "sofa-arm", 0.09)
    for index, x in enumerate((-4.35, -3.45, -2.55), start=1):
        _cube(
            f"ENV_RES_SOFA_SEAT_{index:02d}",
            collection,
            (0.82, 0.78, 0.11),
            (x, 2.96, -5.58),
            mats["textile"],
            "sofa-seat-cushion",
            0.07,
        )
        _cube(
            f"ENV_RES_SOFA_CUSHION_{index:02d}",
            collection,
            (0.78, 0.18, 0.66),
            (x, 3.27, -5.25),
            mats["textile"],
            "sofa-back-cushion",
            0.08,
        )

    _cube("ENV_RES_COFFEE_TOP", collection, (1.55, 0.82, 0.075), (-2.95, 1.08, -5.55), mats["walnut"], "coffee-table-top", 0.035)
    for index, x in enumerate((-3.52, -2.38), start=1):
        _cube(
            f"ENV_RES_COFFEE_LEG_{index:02d}",
            collection,
            (0.09, 0.56, 0.38),
            (x, 1.08, -5.78),
            mats["walnut"],
            "coffee-table-leg",
            0.018,
        )

    _cube("ENV_RES_CONSOLE", collection, (2.15, 0.42, 0.095), (3.55, 5.18, -5.23), mats["walnut"], "floating-console", 0.025)


def _build_environment_lights(collection: bpy.types.Collection) -> None:
    specs = (
        # Broad daylight establishes room exposure but contributes no visible rectangular specular hotspot.
        ("ENV_RES_WINDOW_LIGHT", (-5.20, 0.10, -2.90), (0.0, 0.0, -2.65), 520.0, 4.8, (0.70, 0.82, 1.0), "RECTANGLE", 5.3, 0.0),
        # Warm front key provides gentle metal response without flattening the transparent field.
        ("ENV_RES_WARM_KEY", (4.5, -3.0, -1.80), (0.0, 0.15, -2.75), 320.0, 3.2, (1.0, 0.82, 0.64), "RECTANGLE", 1.0, 0.18),
        # Narrower rear sources create the glass edge structure visible in the studio baseline.
        ("ENV_RES_BACK_RIM", (2.6, 5.05, -1.35), (0.0, 0.0, -2.75), 450.0, 2.6, (1.0, 0.87, 0.70), "RECTANGLE", 0.65, 0.28),
        ("ENV_RES_EDGE_LEFT", (-2.8, 4.8, -2.05), (0.0, 0.0, -2.85), 260.0, 3.6, (0.72, 0.84, 1.0), "RECTANGLE", 0.38, 0.22),
    )
    for name, location, target, energy, size, color, shape, size_y, specular_factor in specs:
        light = create_area_light(
            name,
            location,
            target,
            energy,
            size,
            color,
            collection,
            shape=shape,
            size_y=size_y,
            spread_deg=115 if name == "ENV_RES_WINDOW_LIGHT" else 96,
        )
        if hasattr(light.data, "specular_factor"):
            light.data.specular_factor = specular_factor
        light.hide_render = True
        light["aetheria_light_class"] = "architectural-environment-photographic"
        light["aetheria_environment_id"] = ENVIRONMENT_ID
        light["aetheria_authority"] = "visualization-only"


def build_environment_library() -> None:
    scene = bpy.context.scene
    root = bpy.data.collections.get("AETHERIA_VX4800")
    if root is None:
        raise RuntimeError("AETHERIA_VX4800 root collection is missing")
    collection = bpy.data.collections.get(ENV_COLLECTION) or ensure_collection(ENV_COLLECTION, root)
    mats = _environment_materials()
    _build_room_shell(collection, mats)
    _build_furniture(collection, mats)
    _build_environment_lights(collection)
    collection.hide_render = True
    collection["aetheria_authority"] = "visualization-only"
    collection["aetheria_environment_id"] = ENVIRONMENT_ID
    collection["aetheria_environment_status"] = "architectural-scale-visualization-not-site-design"
    scene["aetheria_visualization_revision"] = VISUALIZATION_REVISION
    scene["aetheria_environment_library_status"] = "visualization-only"
    scene["aetheria_residential_environment_id"] = ENVIRONMENT_ID
    scene["aetheria_residential_floor_top_z_m"] = -6.0
    scene["aetheria_residential_ceiling_underside_z_m"] = 0.15
    scene["aetheria_residential_lookdev_status"] = "premium-contrast-study-visualization-only"


def _set_world(scene: bpy.types.Scene, color: tuple[float, float, float, float], strength: float) -> None:
    world = scene.world
    if world is None:
        return
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        set_socket(background, ("Color",), color)
        set_socket(background, ("Strength",), strength)


def _hide_environment() -> None:
    collection = bpy.data.collections.get(ENV_COLLECTION)
    if collection is not None:
        collection.hide_render = True
    for obj in bpy.data.objects:
        if obj.name.startswith(ENV_LIGHT_PREFIX):
            obj.hide_render = True


def _show_residential(scene: bpy.types.Scene) -> None:
    collection = bpy.data.collections.get(ENV_COLLECTION)
    if collection is None:
        raise RuntimeError("Residential environment collection is missing")
    collection.hide_render = False
    for obj in collection.all_objects:
        obj.hide_render = False
    backdrop = bpy.data.objects.get("STAGE_BACKDROP")
    if backdrop is not None:
        backdrop.hide_render = True
    for obj in bpy.data.objects:
        if obj.type == "LIGHT" and obj.name.startswith("RIG_"):
            obj.hide_render = True
        if obj.type == "LIGHT" and obj.name.startswith("MACRO_RIG_"):
            obj.hide_render = True
    scene.view_settings.exposure = -0.72
    _set_world(scene, (0.035, 0.045, 0.065, 1.0), 0.085)
    scene["aetheria_active_environment"] = ENVIRONMENT_ID


def prepare_environment_render(camera_name: str) -> str | None:
    scene = bpy.context.scene
    _hide_environment()
    if camera_name in ARCH_CAMERAS:
        _show_residential(scene)
        scene["aetheria_active_render_mode"] = "architectural-residential"
        return "architectural-residential"
    scene["aetheria_active_environment"] = "none"
    return None
