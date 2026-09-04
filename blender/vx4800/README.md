# VX4800 Blender visualization master

This folder is the Blender visualization layer for AETHERIA VORTEX (`VX4800-BF-01`). It is intentionally downstream from the controlled fixture data.

## Authority boundary

The `.blend` scene is for photorealistic rendering, material studies, camera work, architectural installation studies and animation review. It is not manufacturing CAD, structural analysis, certified photometry or construction authority.

Controlled inputs remain under `fixtures/vx4800/`. Visual geometry, material shaders, environment architecture, display cable diameters and photographic lights must not silently overwrite those inputs.

## Target Blender version

Blender 5.2.1 LTS.

## Build the complete master scene

From the repository root, use the entrypoint used by GitHub Actions:

```bash
blender --background --factory-startup \
  --python blender/vx4800/build_entrypoint.py -- \
  --repo-root . \
  --output blender/vx4800/VX4800_MASTER.blend
```

`build_scene.py` is the lower-level controlled-product scene generator. Calling it directly intentionally omits the downstream lookdev and architectural environment layers, so it is not the normal command for rebuilding `VX4800_MASTER.blend`.

Validate the saved scene:

```bash
blender --background blender/vx4800/VX4800_MASTER.blend \
  --python blender/vx4800/validate_scene.py
```

Render a named camera shot:

```bash
blender --background blender/vx4800/VX4800_MASTER.blend \
  --python blender/vx4800/render_shot.py -- \
  --repo-root . \
  --camera CAM_HERO_FRONT_3Q \
  --preset hero \
  --output renders/vx4800/hero_front_3q.png
```

Architectural cameras automatically enable their visualization-only environment and disable the dark product stage. The butterfly macro camera automatically isolates the controlled target instance for optical QA without changing that instance's controlled transform.

## Scene structure

The generated scene contains:

- fixed canopy and fixed LED-head placeholders;
- one conceptual rotating-field parent;
- 240 controlled-position linked butterfly instances;
- 240 main suspension splines and 720 visual yoke/lead splines;
- linked S/M/L optical visualization prototypes;
- separate fixture-integrated conceptual lights and photographic render lights;
- studio product-render stage;
- visualization-only residential architectural environment;
- ten named product, detail, technical and architectural cameras.

Every butterfly instance carries its engineering element ID and source schedule values as Blender custom properties.

## Render authority

The 14 `RENDER_LIGHT_*` objects represent conceptual fixture-integrated lighting studies at the controlled head positions. They are not measured supplier photometry. `RIG_*`, `MACRO_RIG_*` and `ENV_RES_*` lights are photographic visualization lights and are not fixture output.

The optical butterfly shader remains a visualization material study until a commercial material/process is controlled. A convincing render does not approve glass composition, PMMA grade, material thickness, attachment geometry, finished mass, proof strength or fatigue life.

## Generated binary

`VX4800_MASTER.blend` is generated from repository source data. The Blender GitHub workflow rebuilds it with Blender 5.2.1 LTS, validates it in Blender, refreshes the binary when needed and renders visual-QA previews.
