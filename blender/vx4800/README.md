# VX4800 Blender visualization master

This folder is the Blender visualization layer for AETHERIA VORTEX (`VX4800-BF-01`). It is intentionally downstream from the controlled fixture data.

## Authority boundary

The `.blend` scene is for photorealistic rendering, material studies, camera work and animation review. It is not manufacturing CAD, structural analysis, certified photometry or construction authority.

Controlled inputs remain under `fixtures/vx4800/`.

## Target Blender version

Blender 5.2.1 LTS.

## Build the master scene

From the repository root:

```bash
blender --background --factory-startup \
  --python blender/vx4800/build_scene.py -- \
  --repo-root . \
  --output blender/vx4800/VX4800_MASTER.blend
```

Validate the saved scene:

```bash
blender --background blender/vx4800/VX4800_MASTER.blend \
  --python blender/vx4800/validate_scene.py
```

Render a named camera shot:

```bash
blender --background blender/vx4800/VX4800_MASTER.blend \
  --python blender/vx4800/render_shot.py -- \
  --camera CAM_HERO_FRONT_3Q \
  --preset hero \
  --output renders/vx4800/hero_front_3q.png
```

## Scene structure

The generated scene contains fixed canopy geometry, one rotating-field root, one combined 240-line suspension curve, a 720-spline yoke/lead system, three linked butterfly prototypes, 240 traceable collection instances, 14 fixed visual LED heads, camera presets, a neutral cyclorama and photographic light rigs.

Every butterfly instance carries its engineering element ID and source schedule values as Blender custom properties.

## Generated binary

`VX4800_MASTER.blend` is generated from repository source data. The Blender GitHub workflow validates and refreshes it when the Blender source pipeline changes.
