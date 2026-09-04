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
from lookdev_refinements import FINISH_MATERIALS, apply_finish_variant


def cli_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    p = argparse.ArgumentParser(description="Render an AETHERIA VX4800 Blender shot")
    p.add_argument("--shot", default=None, help="Named shot from shot_catalogue.json")
    p.add_argument("--camera", default=None, help="Advanced camera override / legacy camera path")
    p.add_argument("--preset", default=None, help="Legacy combined render preset")
    p.add_argument("--quality", default=None, help="Quality tier from render_quality.json")
    p.add_argument("--output-profile", default=None, help="Aspect/resolution profile from output_profiles.json")
    p.add_argument("--finish", default=None, help="Visualization finish override")
    p.add_argument("--output", default=None)
    p.add_argument("--repo-root", default=".")
    p.add_argument("--fixture-lights", choices=("preset", "on", "off"), default="preset")
    p.add_argument("--list-shots", action="store_true")
    return p.parse_args(argv)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def apply_legacy_preset(scene: bpy.types.Scene, preset: dict) -> None:
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


def apply_quality_and_output(scene: bpy.types.Scene, quality: dict, output_profile: dict) -> None:
    scene.render.engine = quality.get("engine", "CYCLES")
    scene.render.resolution_x, scene.render.resolution_y = output_profile["resolution"]
    scene.render.resolution_percentage = output_profile.get("percentage", 100)
    scene.render.film_transparent = output_profile.get("transparent", False)
    scene.render.image_settings.file_format = output_profile.get("fileFormat", "PNG")
    scene.render.image_settings.color_depth = quality.get("colorDepth", "16")
    if scene.render.engine == "CYCLES":
        scene.cycles.samples = quality.get("samples", 256)
        scene.cycles.use_denoising = bool(quality.get("denoising", True))
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = quality.get("adaptiveThreshold", 0.01)


def set_fixture_lights(enabled: bool) -> int:
    count = 0
    for obj in bpy.data.objects:
        if obj.type == "LIGHT" and obj.name.startswith("RENDER_LIGHT_"):
            obj.hide_render = not enabled
            count += 1
    return count


def _print_shots(catalogue: dict, manifest: dict) -> None:
    for name, shot in catalogue["shots"].items():
        print(
            f"{name}: camera={shot['camera']} aspect={shot['aspect']} "
            f"environment={shot['environment']} purpose={shot['purpose']}"
        )
    print("finish variants: " + ", ".join(manifest.get("finishVariants", [])))


def main() -> None:
    args = cli_args()
    repo_root = Path(args.repo_root).resolve()
    base = repo_root / "blender/vx4800"
    presets = _read_json(base / "render_presets.json")
    qualities = _read_json(base / "render_quality.json")
    output_profiles = _read_json(base / "output_profiles.json")
    catalogue = _read_json(base / "shot_catalogue.json")
    manifest = _read_json(base / "scene_manifest.json")

    if args.list_shots:
        _print_shots(catalogue, manifest)
        return
    if not args.output:
        raise SystemExit("--output is required unless --list-shots is used")

    shot = None
    if args.shot:
        shot = catalogue["shots"].get(args.shot)
        if shot is None:
            raise SystemExit(f"Unknown named shot: {args.shot}")
        if args.camera is not None:
            raise SystemExit("--camera cannot be combined with --shot; use a named shot or the advanced camera path")
        if args.preset is not None:
            raise SystemExit("--preset cannot be combined with --shot; use --quality/--output-profile overrides")
        camera_name = shot["camera"]
    else:
        camera_name = args.camera or "CAM_HERO_FRONT_3Q"

    camera = bpy.data.objects.get(camera_name)
    if not camera or camera.type != "CAMERA":
        raise SystemExit(f"Unknown camera: {camera_name}")

    scene = bpy.context.scene
    scene.camera = camera
    settings_label: str
    fixture_lights_enabled: bool

    if shot is not None:
        quality_name = args.quality or shot["defaultQuality"]
        output_profile_name = args.output_profile or shot["defaultOutputProfile"]
        if quality_name not in qualities or quality_name == "schemaVersion":
            raise SystemExit(f"Unknown quality tier: {quality_name}")
        if output_profile_name not in output_profiles or output_profile_name == "schemaVersion":
            raise SystemExit(f"Unknown output profile: {output_profile_name}")
        profile = output_profiles[output_profile_name]
        if profile.get("aspect") != shot["aspect"]:
            raise SystemExit(
                f"Output profile {output_profile_name} aspect {profile.get('aspect')} does not match "
                f"shot {args.shot} aspect {shot['aspect']}"
            )
        apply_quality_and_output(scene, qualities[quality_name], profile)
        fixture_lights_enabled = bool(shot.get("fixtureLights", False))
        settings_label = f"shot={args.shot} quality={quality_name} outputProfile={output_profile_name}"
    elif args.quality is not None or args.output_profile is not None:
        quality_name = args.quality or "production"
        output_profile_name = args.output_profile or "landscape_4k"
        if quality_name not in qualities or quality_name == "schemaVersion":
            raise SystemExit(f"Unknown quality tier: {quality_name}")
        if output_profile_name not in output_profiles or output_profile_name == "schemaVersion":
            raise SystemExit(f"Unknown output profile: {output_profile_name}")
        apply_quality_and_output(scene, qualities[quality_name], output_profiles[output_profile_name])
        fixture_lights_enabled = False
        settings_label = f"camera={camera_name} quality={quality_name} outputProfile={output_profile_name}"
    else:
        preset_name = args.preset or "hero"
        if preset_name not in presets or preset_name == "schemaVersion":
            raise SystemExit(f"Unknown render preset: {preset_name}")
        preset = presets[preset_name]
        apply_legacy_preset(scene, preset)
        fixture_lights_enabled = bool(preset.get("fixtureLights", True))
        settings_label = f"camera={camera_name} legacyPreset={preset_name}"

    render_mode = prepare_render_mode(camera_name)
    environment_mode = prepare_environment_render(camera_name)
    if environment_mode is not None:
        render_mode = environment_mode

    finish_name = args.finish or manifest.get("defaultFinish", "dark_champagne")
    if finish_name not in manifest.get("finishVariants", []) or finish_name not in FINISH_MATERIALS:
        raise SystemExit(f"Unknown visualization finish: {finish_name}")
    finish_replacements = apply_finish_variant(finish_name)

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
        f"Rendered {settings_label}: {output} | mode={render_mode} | finish={finish_name} "
        f"finishSlots={finish_replacements} | fixture conceptual lights={'on' if fixture_lights_enabled else 'off'}"
    )


if __name__ == "__main__":
    main()
