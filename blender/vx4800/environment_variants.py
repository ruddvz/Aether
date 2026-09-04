# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import bpy

from aether_blender_lib import create_area_light, ensure_collection, link_object, set_socket

VARIANTS = {
    "staircase-void": {
        "collection": "86_ENV_STAIRCASE",
        "lightPrefix": "ENV_STAIR_",
        "cameras": {"CAM_ARCH_STAIRCASE_WIDE"},
        "exposure": -0.46,
        "world": (0.045, 0.050, 0.065, 1.0),
        "worldStrength": 0.12,
    },
    "hospitality-lobby": {
        "collection": "87_ENV_HOSPITALITY",
        "lightPrefix": "ENV_HOSP_",
        "cameras": {"CAM_ARCH_HOSPITALITY_WIDE"},
        "exposure": -0.42,
        "world": (0.060, 0.050, 0.045, 1.0),
        "worldStrength": 0.13,
    },
    "gallery-atrium": {
        "collection": "88_ENV_ATRIUM",
        "lightPrefix": "ENV_ATRIUM_",
        "cameras": {"CAM_ARCH_ATRIUM_WIDE"},
        "exposure": -0.50,
        "world": (0.045, 0.050, 0.060, 1.0),
        "worldStrength": 0.11,
    },
}


def _material(name: str) -> bpy.types.Material:
    material = bpy.data.materials.get(name)
    if material is None:
        raise RuntimeError(f"Required shared environment material is missing: {name}")
    return material


def _tag(obj: bpy.types.Object, environment_id: str, role: str) -> bpy.types.Object:
    obj["aetheria_authority"] = "visualization-only"
    obj["aetheria_environment_id"] = environment_id
    obj["aetheria_environment_role"] = role
    obj.hide_render = True
    return obj


def _cube(
    name: str,
    collection: bpy.types.Collection,
    dimensions: tuple[float, float, float],
    location: tuple[float, float, float],
    material: bpy.types.Material,
    environment_id: str,
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
        modifier = obj.modifiers.new("AETHERIA_ENV_EDGE", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        modifier.limit_method = "ANGLE"
    return _tag(obj, environment_id, role)


def _add_light(
    collection: bpy.types.Collection,
    environment_id: str,
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    energy: float,
    size: float,
    color: tuple[float, float, float],
    *,
    size_y: float = 1.0,
    specular_factor: float = 0.18,
) -> None:
    light = create_area_light(
        name,
        location,
        target,
        energy,
        size,
        color,
        collection,
        shape="RECTANGLE",
        size_y=size_y,
        spread_deg=105,
    )
    if hasattr(light.data, "specular_factor"):
        light.data.specular_factor = specular_factor
    light.hide_render = True
    light["aetheria_light_class"] = "architectural-environment-photographic"
    light["aetheria_environment_id"] = environment_id
    light["aetheria_authority"] = "visualization-only"


def _build_staircase(collection: bpy.types.Collection) -> None:
    env = "staircase-void"
    plaster = _material("MAT_ENV_RES_PLASTER")
    stone = _material("MAT_ENV_RES_FEATURE_STONE")
    floor = _material("MAT_ENV_RES_LIMESTONE")
    walnut = _material("MAT_ENV_RES_WALNUT")

    _cube("ENV_STAIR_FLOOR", collection, (11.0, 16.0, 0.16), (0.0, 0.2, -6.08), floor, env, "floor", 0.012)
    _cube("ENV_STAIR_CEILING", collection, (11.0, 12.4, 0.22), (0.0, 0.0, 0.26), plaster, env, "flat-mounting-ceiling", 0.010)
    _cube("ENV_STAIR_BACK_WALL", collection, (11.0, 0.20, 6.15), (0.0, 5.75, -2.925), plaster, env, "back-wall", 0.012)
    _cube("ENV_STAIR_CONTRAST", collection, (5.6, 0.075, 5.30), (-1.35, 5.64, -3.02), stone, env, "vortex-contrast-stone", 0.010)
    _cube("ENV_STAIR_RIGHT_WALL", collection, (0.18, 8.0, 6.15), (5.45, 1.9, -2.925), plaster, env, "stair-side-wall", 0.010)

    for index in range(12):
        y = -0.8 + index * 0.46
        z = -5.80 + index * 0.235
        _cube(
            f"ENV_STAIR_TREAD_{index + 1:02d}",
            collection,
            (2.55, 0.52, 0.12),
            (3.55, y, z),
            walnut,
            env,
            "floating-stair-tread",
            0.018,
        )
    _cube("ENV_STAIR_LANDING", collection, (2.75, 1.70, 0.16), (3.55, 4.80, -3.05), walnut, env, "upper-landing", 0.020)
    _cube("ENV_STAIR_STRINGER", collection, (0.18, 5.75, 2.95), (4.78, 1.65, -4.38), stone, env, "stair-stringer-mass", 0.015)

    _add_light(collection, env, "ENV_STAIR_KEY", (-4.8, -1.2, -2.2), (0.0, 0.2, -2.7), 560.0, 4.4, (0.72, 0.84, 1.0), size_y=4.6, specular_factor=0.04)
    _add_light(collection, env, "ENV_STAIR_WARM_RIM", (4.2, 4.7, -1.4), (0.0, 0.0, -2.7), 420.0, 2.8, (1.0, 0.80, 0.62), size_y=0.8, specular_factor=0.18)
    _add_light(collection, env, "ENV_STAIR_TOP_FILL", (0.0, -0.4, 4.2), (0.0, 0.0, -2.2), 280.0, 3.8, (1.0, 0.92, 0.82), size_y=2.2, specular_factor=0.10)


def _build_hospitality(collection: bpy.types.Collection) -> None:
    env = "hospitality-lobby"
    plaster = _material("MAT_ENV_RES_PLASTER")
    stone = _material("MAT_ENV_RES_FEATURE_STONE")
    floor = _material("MAT_ENV_RES_LIMESTONE")
    walnut = _material("MAT_ENV_RES_WALNUT")
    textile = _material("MAT_ENV_RES_TEXTILE")
    rug = _material("MAT_ENV_RES_RUG")

    _cube("ENV_HOSP_FLOOR", collection, (13.0, 18.0, 0.16), (0.0, 0.4, -6.08), floor, env, "lobby-floor", 0.012)
    _cube("ENV_HOSP_CEILING", collection, (13.0, 13.0, 0.22), (0.0, 0.0, 0.26), plaster, env, "flat-mounting-ceiling", 0.010)
    _cube("ENV_HOSP_BACK_WALL", collection, (13.0, 0.20, 6.15), (0.0, 6.1, -2.925), plaster, env, "back-wall", 0.012)
    _cube("ENV_HOSP_PORTAL", collection, (5.8, 0.085, 5.35), (-0.9, 5.99, -3.02), stone, env, "dark-stone-vortex-backdrop", 0.010)
    for x in (-5.35, 5.35):
        _cube("ENV_HOSP_COLUMN_L" if x < 0 else "ENV_HOSP_COLUMN_R", collection, (0.72, 0.72, 6.15), (x, 3.65, -2.925), plaster, env, "lobby-column", 0.03)

    for side, x in (("L", -4.2), ("R", 3.7)):
        _cube(f"ENV_HOSP_RUG_{side}", collection, (3.0, 2.3, 0.025), (x, 1.9, -5.975), rug, env, "lounge-rug", 0.008)
        _cube(f"ENV_HOSP_BENCH_{side}", collection, (2.65, 0.90, 0.48), (x, 3.15, -5.70), textile, env, "lounge-bench", 0.13)
        _cube(f"ENV_HOSP_BACK_{side}", collection, (2.65, 0.22, 0.80), (x, 3.47, -5.38), textile, env, "lounge-back", 0.12)
        _cube(f"ENV_HOSP_TABLE_{side}", collection, (1.10, 0.65, 0.08), (x, 1.65, -5.55), walnut, env, "lounge-table", 0.035)

    _add_light(collection, env, "ENV_HOSP_KEY", (-5.4, -1.8, -1.7), (0.0, 0.4, -2.6), 620.0, 5.0, (0.76, 0.86, 1.0), size_y=4.8, specular_factor=0.05)
    _add_light(collection, env, "ENV_HOSP_WARM_KEY", (4.8, -2.4, -1.6), (0.0, 0.5, -2.8), 360.0, 3.4, (1.0, 0.79, 0.60), size_y=1.2, specular_factor=0.16)
    _add_light(collection, env, "ENV_HOSP_BACK_RIM", (0.8, 5.5, -1.0), (0.0, 0.0, -2.7), 500.0, 3.0, (1.0, 0.86, 0.68), size_y=0.9, specular_factor=0.20)


def _build_atrium(collection: bpy.types.Collection) -> None:
    env = "gallery-atrium"
    plaster = _material("MAT_ENV_RES_PLASTER")
    stone = _material("MAT_ENV_RES_FEATURE_STONE")
    floor = _material("MAT_ENV_RES_LIMESTONE")
    walnut = _material("MAT_ENV_RES_WALNUT")

    _cube("ENV_ATRIUM_FLOOR", collection, (14.0, 20.0, 0.16), (0.0, 0.6, -6.08), floor, env, "gallery-floor", 0.012)
    _cube("ENV_ATRIUM_CEILING", collection, (14.0, 14.0, 0.22), (0.0, 0.0, 0.26), plaster, env, "flat-mounting-ceiling", 0.010)
    _cube("ENV_ATRIUM_BACK", collection, (14.0, 0.20, 6.15), (0.0, 6.4, -2.925), plaster, env, "gallery-back-wall", 0.012)
    _cube("ENV_ATRIUM_CENTRE_PANEL", collection, (6.1, 0.07, 5.40), (0.0, 6.29, -3.00), stone, env, "gallery-contrast-panel", 0.010)

    for index, x in enumerate((-5.6, -4.3, -3.0, 3.0, 4.3, 5.6), start=1):
        _cube(f"ENV_ATRIUM_PILASTER_{index:02d}", collection, (0.34, 0.80, 6.15), (x, 5.95, -2.925), plaster, env, "gallery-pilaster", 0.018)
    for index, x in enumerate((-4.8, 4.8), start=1):
        _cube(f"ENV_ATRIUM_PLINTH_{index:02d}", collection, (1.25, 1.25, 0.72), (x, 2.9, -5.64), stone, env, "gallery-plinth", 0.035)
        _cube(f"ENV_ATRIUM_BENCH_{index:02d}", collection, (2.1, 0.62, 0.42), (x, 0.3, -5.78), walnut, env, "gallery-bench", 0.045)

    _add_light(collection, env, "ENV_ATRIUM_LEFT", (-5.8, -1.0, -1.7), (0.0, 0.6, -2.7), 540.0, 4.8, (0.72, 0.84, 1.0), size_y=4.6, specular_factor=0.04)
    _add_light(collection, env, "ENV_ATRIUM_RIGHT", (5.8, -0.4, -1.6), (0.0, 0.6, -2.7), 420.0, 4.0, (1.0, 0.84, 0.68), size_y=3.2, specular_factor=0.10)
    _add_light(collection, env, "ENV_ATRIUM_BACK", (0.0, 5.7, -0.8), (0.0, 0.0, -2.8), 520.0, 3.2, (1.0, 0.91, 0.78), size_y=1.0, specular_factor=0.18)


def build_additional_environments() -> None:
    root = bpy.data.collections.get("AETHERIA_VX4800")
    if root is None:
        raise RuntimeError("AETHERIA_VX4800 root collection is missing")

    builders = {
        "staircase-void": _build_staircase,
        "hospitality-lobby": _build_hospitality,
        "gallery-atrium": _build_atrium,
    }
    for environment_id, config in VARIANTS.items():
        collection = bpy.data.collections.get(config["collection"]) or ensure_collection(config["collection"], root)
        builders[environment_id](collection)
        collection.hide_render = True
        collection["aetheria_authority"] = "visualization-only"
        collection["aetheria_environment_id"] = environment_id
        collection["aetheria_environment_status"] = "architectural-scale-visualization-not-site-design"

    scene = bpy.context.scene
    scene["aetheria_additional_environment_count"] = len(VARIANTS)
    scene["aetheria_additional_environment_status"] = "visualization-only"


def _set_world(scene: bpy.types.Scene, color: tuple[float, float, float, float], strength: float) -> None:
    world = scene.world
    if world is None:
        return
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        set_socket(background, ("Color",), color)
        set_socket(background, ("Strength",), strength)


def _hide_all() -> None:
    for config in VARIANTS.values():
        collection = bpy.data.collections.get(config["collection"])
        if collection is not None:
            collection.hide_render = True
        prefix = config["lightPrefix"]
        for obj in bpy.data.objects:
            if obj.type == "LIGHT" and obj.name.startswith(prefix):
                obj.hide_render = True


def prepare_additional_environment_render(camera_name: str) -> str | None:
    _hide_all()
    scene = bpy.context.scene
    selected_id = None
    selected_config = None
    for environment_id, config in VARIANTS.items():
        if camera_name in config["cameras"]:
            selected_id = environment_id
            selected_config = config
            break
    if selected_id is None or selected_config is None:
        return None

    collection = bpy.data.collections.get(selected_config["collection"])
    if collection is None:
        raise RuntimeError(f"Environment collection is missing: {selected_config['collection']}")
    collection.hide_render = False
    # Variant environments are intentionally flat collections. Iterate direct
    # members rather than all_objects, which can expose a transient null weak
    # reference after a saved .blend is reloaded headlessly.
    for obj in collection.objects:
        if obj is not None:
            obj.hide_render = False

    backdrop = bpy.data.objects.get("STAGE_BACKDROP")
    if backdrop is not None:
        backdrop.hide_render = True
    for obj in bpy.data.objects:
        if obj.type == "LIGHT" and (obj.name.startswith("RIG_") or obj.name.startswith("MACRO_RIG_")):
            obj.hide_render = True

    scene.view_settings.exposure = selected_config["exposure"]
    _set_world(scene, selected_config["world"], selected_config["worldStrength"])
    scene["aetheria_active_environment"] = selected_id
    scene["aetheria_active_render_mode"] = f"architectural-{selected_id}"
    return f"architectural-{selected_id}"
