# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import bpy

VISUALIZATION_REVISION = "0.11.0"

FINISH_MATERIALS = {
    "dark_champagne": "MAT_PVD_DARK_CHAMPAGNE",
    "black_titanium": "MAT_PVD_BLACK_TITANIUM",
    "brushed_brass": "MAT_BRUSHED_BRASS",
    "satin_nickel": "MAT_SATIN_NICKEL",
}

_FINISH_SOURCE_MATERIALS = {
    "MAT_PVD_DARK_CHAMPAGNE",
    "MAT_BUTTERFLY_BODY_CHAMPAGNE",
    "MAT_LED_HEAD_TITANIUM",
}


def _iter_finish_objects():
    for obj in bpy.data.objects:
        if obj.name == "CANOPY_FIXED":
            yield obj
        elif obj.name == "SUSPENSION_YOKES_240":
            yield obj
        elif obj.name.startswith("CENTRAL_SPINE"):
            yield obj
        elif obj.name.startswith("LED_HEAD_") and not obj.name.endswith("_LENS"):
            yield obj


def apply_finish_variant(name: str) -> int:
    if name not in FINISH_MATERIALS:
        raise ValueError(f"Unknown visualization finish: {name}")
    target = bpy.data.materials.get(FINISH_MATERIALS[name])
    if target is None:
        raise RuntimeError(f"Finish material is missing: {FINISH_MATERIALS[name]}")

    replaced = 0
    for obj in _iter_finish_objects():
        if not getattr(obj, "data", None) or not hasattr(obj.data, "materials"):
            continue
        for index, material in enumerate(obj.data.materials):
            if material and material.name in _FINISH_SOURCE_MATERIALS:
                obj.data.materials[index] = target
                replaced += 1
        obj["aetheria_finish_override"] = name
        obj["aetheria_finish_override_authority"] = "visualization-only-not-manufacturing-finish"

    scene = bpy.context.scene
    scene["aetheria_active_finish_variant"] = name
    scene["aetheria_finish_override_status"] = "visualization-only"
    return replaced


def apply_master_refinements() -> None:
    scene = bpy.context.scene

    glass = bpy.data.materials.get("MAT_BUTTERFLY_OPTICAL_GLASS")
    if glass and glass.use_nodes and glass.node_tree:
        absorption = glass.node_tree.nodes.get("AETHERIA_EDGE_ABSORPTION")
        if absorption and absorption.inputs.get("Density"):
            absorption.inputs["Density"].default_value = 3.5
            glass["aetheria_absorption_density_visual_study"] = 3.5
            glass["aetheria_absorption_status"] = "visualization-lookdev-value-not-material-specification"

    refined_spines = 0
    for obj in bpy.data.objects:
        if not obj.name.startswith("CENTRAL_SPINE"):
            continue
        obj.scale.x *= 0.54
        obj.scale.y *= 0.62
        obj.scale.z *= 0.67
        obj["aetheria_spine_refinement"] = "0.11-smaller-sculptural-centre"
        obj["aetheria_geometry_status"] = "visualization-sculptural-abstraction"
        refined_spines += 1

    scene["aetheria_visualization_revision"] = VISUALIZATION_REVISION
    scene["aetheria_default_finish_variant"] = "dark_champagne"
    scene["aetheria_optical_absorption_status"] = "visualization-only"
    scene["aetheria_refined_spine_count"] = refined_spines
