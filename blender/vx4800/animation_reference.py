# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import bpy


def apply_nominal_rotation_reference() -> None:
    """Create a visualization-only constant-speed reference from controlled nominal RPM.

    This is not a drive, braking, acceleration, wind, cable-dynamics or safety simulation.
    """
    scene = bpy.context.scene
    rotor = bpy.data.objects.get("AETHERIA_ROTATING_FIELD")
    if rotor is None:
        raise RuntimeError("AETHERIA_ROTATING_FIELD is missing")

    nominal_rpm = float(rotor.get("nominal_rpm", 0.0))
    if nominal_rpm <= 0.0:
        raise RuntimeError("Controlled nominal RPM is missing or non-positive")

    scene.render.fps = 24
    scene.render.fps_base = 1.0
    frames_per_revolution = int(round((60.0 / nominal_rpm) * scene.render.fps))
    start_frame = 1
    end_frame = start_frame + frames_per_revolution

    rotor.animation_data_clear()
    rotor.rotation_mode = "XYZ"
    rotor.rotation_euler.z = 0.0
    rotor.keyframe_insert(data_path="rotation_euler", index=2, frame=start_frame)
    rotor.rotation_euler.z = math.tau
    rotor.keyframe_insert(data_path="rotation_euler", index=2, frame=end_frame)

    action = rotor.animation_data.action if rotor.animation_data else None
    if action is None:
        raise RuntimeError("Failed to create nominal rotation reference action")
    action.name = "PHYSICAL_NOMINAL_RPM_REFERENCE"
    try:
        for fcurve in action.fcurves:
            for point in fcurve.keyframe_points:
                point.interpolation = "LINEAR"
    except Exception:
        pass

    rotor["motion_status"] = "conceptual-reference-only"
    rotor["animation_authority"] = "visualization-only"
    rotor["animation_source"] = "controlled-nominal-rpm"
    scene.frame_start = start_frame
    scene.frame_end = end_frame
    scene.frame_set(start_frame)
    scene["aetheria_animation_reference_status"] = "visualization-only-constant-speed-reference"
    scene["aetheria_animation_reference_rpm"] = nominal_rpm
    scene["aetheria_animation_reference_fps"] = scene.render.fps
    scene["aetheria_animation_reference_cycle_frames"] = frames_per_revolution
    scene["aetheria_animation_exclusions"] = "no-acceleration-no-braking-no-wind-no-cable-dynamics-no-butterfly-flapping"
