# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from environment_library import prepare_environment_render
from lookdev_modes import prepare_render_mode


def cli_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    p = argparse.ArgumentParser(description="Render a named AETHERIA VX4800 Blender shot")
    p.add_argument("--camera", default="CAM_HERO_FRONT_3Q")
    p.add_argument("--preset", default="hero")
    p.add_argument("--output", required=True)
    p.add_argument("--repo-root", default=".")
    p.add_argument("--fixture-lights", choices=("preset", "on", "off"), default="preset")
    return p.parse_args(argv)


def apply_preset(scene: bpy.types.Scene, preset: dict) -> None:
    scene.render.engine = preset["engine"]
    scene.render.resolution_x, scene.render.resolution_y = preset["resolution"]
    scene.render.resolution_percentage = preset.get("percentage", 100)
    scene.render.film_transparent = preset.get("transparent", False)
    scene.render.image_settings.file_format = preset.get("fileFormat", "PNG")
    scene.render.image_settings.color_depth = preset.get("colorDepth", "16")
    if scene.render.engine == "CYCLES":
        scene.cycles.samples = preset.get("samples", 256)
        scene.cycles.use_denoising = True
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = preset.get("adaptiveThreshold", 0.01)


def set_fixture_lights(enabled: bool) -> int:
    count = 0
    for obj in bpy.data.objects:
        if obj.type == "LIGHT" and obj.name.startswith("RENDER_LIGHT_"):
            obj.hide_render = not enabled
            count += 1
    return count


def main() -> None:
    args = cli_args()
    repo_root = Path(args.repo_root).resolve()
    presets = json.loads((repo_root / "blender/vx4800/render_presets.json").read_text())
    if args.preset not in presets:
        raise SystemExit(f"Unknown render preset: {args.preset}")
    camera = bpy.data.objects.get(args.camera)
    if not camera or camera.type != "CAMERA":
        raise SystemExit(f"Unknown camera: {args.camera}")
    scene = bpy.context.scene
    preset = presets[args.preset]
    scene.camera = camera
    apply_preset(scene, preset)
    render_mode = prepare_render_mode(args.camera)
    environment_mode = prepare_environment_render(args.camera)
    if environment_mode is not None:
        render_mode = environment_mode
    fixture_lights_enabled = bool(preset.get("fixtureLights", True))
    if args.fixture_lights != "preset":
        fixture_lights_enabled = args.fixture_lights == "on"
    fixture_count = set_fixture_lights(fixture_lights_enabled)
    if fixture_count != 14:
        raise SystemExit(f"Expected 14 fixture-integrated conceptual render lights, found {fixture_count}")
    output = Path(args.output)
    if not output.is_absolute():
        output = repo_root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    print(
        f"Rendered {args.camera} / {args.preset}: {output} | "
        f"mode={render_mode} | fixture conceptual lights={'on' if fixture_lights_enabled else 'off'}"
    )


if __name__ == "__main__":
    main()
