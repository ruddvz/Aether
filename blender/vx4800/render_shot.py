# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


def cli_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    p = argparse.ArgumentParser(description="Render a named AETHERIA VX4800 Blender shot")
    p.add_argument("--camera", default="CAM_HERO_FRONT_3Q")
    p.add_argument("--preset", default="hero")
    p.add_argument("--output", required=True)
    p.add_argument("--repo-root", default=".")
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
    scene.camera = camera
    apply_preset(scene, presets[args.preset])
    output = Path(args.output)
    if not output.is_absolute():
        output = repo_root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {args.camera} / {args.preset}: {output}")


if __name__ == "__main__":
    main()
