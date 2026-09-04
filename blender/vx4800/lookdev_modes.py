# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from mathutils import Vector
import bpy

from aether_blender_lib import create_area_light, ensure_collection, link_object

VISUALIZATION_REVISION = "0.5.0"
MACRO_TARGET_ID = "VX-001"
MACRO_CARD_NAME = "MACRO_NEUTRAL_CARD"
MACRO_LIGHT_PREFIX = "MACRO_RIG_"


def _set_socket(node: bpy.types.Node | None, name: str, value) -> None:
    if node is None:
        return
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def _tune_optical_glass() -> None:
    material = bpy.data.materials.get("MAT_BUTTERFLY_OPTICAL_GLASS")
    if material is None or not material.use_nodes:
        raise RuntimeError("MAT_BUTTERFLY_OPTICAL_GLASS is missing")
    nodes = material.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    _set_socket(bsdf, "Base Color", (0.965, 0.985, 1.0, 1.0))
    _set_socket(bsdf, "Metallic", 0.0)
    _set_socket(bsdf, "Transmission Weight", 1.0)
    _set_socket(bsdf, "IOR", 1.50)
    _set_socket(bsdf, "Coat Weight", 0.02)
    absorption = nodes.get("AETHERIA_EDGE_ABSORPTION")
    if absorption is not None:
        _set_socket(absorption, "Color", (0.82, 0.92, 0.95, 1.0))
        _set_socket(absorption, "Density", 1.6)
    ramp = nodes.get("AETHERIA_GLASS_ROUGHNESS_RANGE")
    if ramp is not None:
        ramp.color_ramp.elements[0].color = (0.010, 0.010, 0.010, 1.0)
        ramp.color_ramp.elements[1].color = (0.030, 0.030, 0.030, 1.0)
    material["aetheria_absorption_status"] = "visualization-lookdev-value-not-material-specification"
    material["aetheria_optical_revision"] = VISUALIZATION_REVISION


def _slim_butterfly_spines() -> int:
    count = 0
    for obj in bpy.data.objects:
        if obj.name == "CENTRAL_SPINE" or obj.name.startswith("CENTRAL_SPINE."):
            obj.scale.x *= 0.78
            obj.scale.y *= 0.70
            obj.scale.z *= 0.82
            obj["aetheria_geometry_status"] = "visualization-sculptural-abstraction-slimmed-0.5.0"
            count += 1
    if count != 3:
        raise RuntimeError(f"Expected 3 linked butterfly prototype spines, found {count}")
    return count


def _build_macro_stage() -> None:
    target_obj = bpy.data.objects.get(MACRO_TARGET_ID)
    camera = bpy.data.objects.get("CAM_BUTTERFLY_MACRO")
    root = bpy.data.collections.get("AETHERIA_VX4800")
    rig_collection = bpy.data.collections.get("70_LIGHT_RIGS")
    stage_collection = bpy.data.collections.get("80_RENDER_STAGE")
    if target_obj is None or camera is None or root is None or rig_collection is None or stage_collection is None:
        raise RuntimeError("Macro lookdev requires the built VX4800 scene and CAM_BUTTERFLY_MACRO")

    target = target_obj.matrix_world.translation.copy()
    view_dir = (target - camera.matrix_world.translation).normalized()
    card_center = target + view_dir * 0.48
    card_normal = -view_dir

    if bpy.data.objects.get(MACRO_CARD_NAME) is None:
        bpy.ops.mesh.primitive_plane_add(size=2.2, location=card_center)
        card = bpy.context.object
        card.name = MACRO_CARD_NAME
        link_object(card, stage_collection)
        card.rotation_euler = Vector((0.0, 0.0, 1.0)).rotation_difference(card_normal).to_euler()
        stage_material = bpy.data.materials.get("MAT_STAGE_IVORY")
        if stage_material is None:
            raise RuntimeError("MAT_STAGE_IVORY is missing")
        card.data.materials.append(stage_material)
        card.hide_render = True
        card["aetheria_stage_role"] = "optical-macro-neutral-reflection-card"
        card["aetheria_authority"] = "visualization-only"

    macro_lights = (
        ("MACRO_RIG_KEY", target + Vector((0.52, -0.48, 0.42)), 72.0, 0.46, (1.0, 0.92, 0.84)),
        ("MACRO_RIG_EDGE", target + Vector((-0.44, 0.34, 0.28)), 108.0, 0.34, (0.78, 0.88, 1.0)),
        ("MACRO_RIG_FILL", target + Vector((-0.34, -0.38, -0.16)), 34.0, 0.62, (1.0, 0.96, 0.90)),
    )
    for name, location, energy, size, color in macro_lights:
        if bpy.data.objects.get(name) is None:
            light = create_area_light(
                name,
                tuple(location),
                tuple(target),
                energy,
                size,
                color,
                rig_collection,
                shape="DISK",
                spread_deg=105,
            )
            light.hide_render = True
            light["aetheria_light_class"] = "photographic-optical-macro"
            light["aetheria_authority"] = "visualization-only"


def apply_master_lookdev() -> None:
    scene = bpy.context.scene
    _tune_optical_glass()
    spine_count = _slim_butterfly_spines()
    _build_macro_stage()
    scene["aetheria_visualization_revision"] = VISUALIZATION_REVISION
    scene["aetheria_macro_target_id"] = MACRO_TARGET_ID
    scene["aetheria_macro_mode_status"] = "render-only-isolation-does-not-change-controlled-transform"
    scene["aetheria_optical_lookdev_status"] = "visualization-study-not-commercially-locked"
    scene["aetheria_linked_prototype_spine_count"] = spine_count


def _set_product_visibility() -> None:
    for obj in bpy.data.objects:
        if obj.name.startswith("VX-") and obj.instance_type == "COLLECTION":
            obj.hide_render = False
    for name in (
        "SUSPENSION_MICROCABLES_240",
        "SUSPENSION_YOKES_240",
        "CANOPY_FIXED",
        "ROTATING_CARRIER_VISUAL",
        "STAGE_BACKDROP",
    ):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            obj.hide_render = False
    for obj in bpy.data.objects:
        if obj.name.startswith("LED_HEAD_"):
            obj.hide_render = False
        if obj.type == "LIGHT" and obj.name.startswith("RIG_"):
            obj.hide_render = False
        if obj.type == "LIGHT" and obj.name.startswith(MACRO_LIGHT_PREFIX):
            obj.hide_render = True
    card = bpy.data.objects.get(MACRO_CARD_NAME)
    if card is not None:
        card.hide_render = True


def _set_macro_visibility() -> None:
    for obj in bpy.data.objects:
        if obj.name.startswith("VX-") and obj.instance_type == "COLLECTION":
            obj.hide_render = obj.name != MACRO_TARGET_ID
    for name in (
        "SUSPENSION_MICROCABLES_240",
        "SUSPENSION_YOKES_240",
        "CANOPY_FIXED",
        "ROTATING_CARRIER_VISUAL",
        "STAGE_BACKDROP",
    ):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            obj.hide_render = True
    for obj in bpy.data.objects:
        if obj.name.startswith("LED_HEAD_"):
            obj.hide_render = True
        if obj.type == "LIGHT" and obj.name.startswith("RIG_"):
            obj.hide_render = True
        if obj.type == "LIGHT" and obj.name.startswith(MACRO_LIGHT_PREFIX):
            obj.hide_render = False
    card = bpy.data.objects.get(MACRO_CARD_NAME)
    if card is None:
        raise RuntimeError("Macro neutral card is missing")
    card.hide_render = False


def prepare_render_mode(camera_name: str) -> str:
    scene = bpy.context.scene
    _set_product_visibility()
    if camera_name == "CAM_BUTTERFLY_MACRO":
        _set_macro_visibility()
        scene.view_settings.exposure = -0.10
        scene["aetheria_active_render_mode"] = "optical-macro-isolated"
        return "optical-macro-isolated"
    scene.view_settings.exposure = -0.45
    scene["aetheria_active_render_mode"] = "clean-product"
    return "clean-product"
