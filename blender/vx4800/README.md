# VX4800 Blender visualization master

This folder is the Blender visualization layer for AETHERIA VORTEX (`VX4800-BF-01`). It is intentionally downstream from the controlled fixture data.

## Authority boundary

The `.blend` scene is for photorealistic rendering, finish studies, camera work, architectural installation studies and motion review. It is not manufacturing CAD, structural analysis, certified photometry, kinetic safety analysis or construction authority.

Controlled inputs remain under `fixtures/vx4800/`. Visual geometry, material shaders, environment architecture, display cable diameters, photographic lights, finish overrides and animation references must not silently overwrite those inputs.

## Target Blender version

Blender 5.2.1 LTS.

## Build the complete master scene

From the repository root, use the same entrypoint as GitHub Actions:

```bash
blender --background --factory-startup \
  --python blender/vx4800/build_entrypoint.py -- \
  --repo-root . \
  --output blender/vx4800/VX4800_MASTER.blend
```

`build_scene.py` is the lower-level controlled-product scene generator. Calling it directly intentionally omits downstream lookdev, the refined optical layer, architectural environments and the derived motion reference, so it is not the normal command for rebuilding `VX4800_MASTER.blend`.

Validate the saved scene:

```bash
blender --background blender/vx4800/VX4800_MASTER.blend \
  --python blender/vx4800/validate_scene.py
```

The final 0.13 validator also exercises repeated master-refinement calls and sequential finish switching in one Blender session so local iterative work cannot silently compound the sculptural refinement or become stuck on the first finish override.

## Render by named shot

Named shots are the preferred human and automation interface because each shot records its intended camera, aspect ratio, environment and production defaults.

List the catalogue and visualization finish variants:

```bash
blender --background blender/vx4800/VX4800_MASTER.blend \
  --python blender/vx4800/render_shot.py -- \
  --repo-root . \
  --list-shots
```

Render a production hero:

```bash
blender --background blender/vx4800/VX4800_MASTER.blend \
  --python blender/vx4800/render_shot.py -- \
  --repo-root . \
  --shot product_hero \
  --output renders/vx4800/product_hero.png
```

Render a lookdev preview with a visualization-only satin-nickel finish study:

```bash
blender --background blender/vx4800/VX4800_MASTER.blend \
  --python blender/vx4800/render_shot.py -- \
  --repo-root . \
  --shot canopy_detail \
  --quality lookdev \
  --output-profile square_preview \
  --finish satin_nickel \
  --output renders/vx4800/canopy_satin_nickel_preview.png
```

Quality tiers are `draft`, `lookdev`, `production` and `hero`. Output profiles independently define landscape, vertical or square resolution. The shot catalogue rejects aspect/profile mismatches.

Visualization finish studies are `dark_champagne`, `black_titanium`, `brushed_brass` and `satin_nickel`. They are render-time presentation overrides. They do not select, qualify or approve a manufacturing finish.

The older `--camera` + `--preset` path remains available for advanced or legacy use.

## Named environments

Architectural shots automatically enable the correct visualization-only context and suppress the studio stage. The current library contains:

- double-height luxury residential;
- staircase void;
- hospitality lobby;
- gallery atrium.

The existing dark product stage is the premium studio context. The butterfly macro mode is an isolated optical-review context rather than an architectural environment.

Every architectural object and environment light is tagged visualization-only. Room dimensions, floor/ceiling datums, furniture, stairs and photographic lights are not site design, structural design or fixture output data.

## Scene structure

The generated scene contains:

- fixed canopy and 14 fixed-position LED-head placeholders;
- one conceptual rotating-field parent;
- 240 controlled-position linked butterfly instances, preserving 66 S / 144 M / 30 L;
- 240 main suspension splines and 720 visual yoke/lead splines;
- linked S/M/L optical visualization prototypes;
- separate fixture-integrated conceptual lights and photographic render lights;
- dark premium studio and isolated macro lookdev contexts;
- four visualization-only architectural environments;
- thirteen named product, detail, technical and architectural cameras;
- thirteen validated named shot definitions.

Every butterfly instance carries its engineering element ID and source schedule values as Blender custom properties.

## Optical and finish authority

The optical butterfly shader is a visualization study. Its transmission, IOR, roughness and pale edge absorption exist to produce a plausible render and do not specify glass composition, PMMA grade, coating, thickness or supplier process. The final 0.13 baseline retains the restrained absorption introduced in 0.11, recentres the macro review and keeps thin-film/fantasy dispersion disabled.

The four metal finish variants are appearance studies only. A convincing render does not approve PVD chemistry, plating stack, substrate, brushing process, colour tolerance, durability or supplier.

## Motion reference

`AETHERIA_ROTATING_FIELD` carries a constant-speed visualization reference derived from the controlled nominal RPM. The cycle length is calculated from nominal RPM and scene FPS instead of being hard-coded.

This reference explicitly excludes acceleration, braking, controlled stopping, jam behaviour, wind, cable dynamics, butterfly flapping and safety response. Those remain engineering responsibilities outside the Blender visualization layer.

## Lighting authority

The 14 `RENDER_LIGHT_*` objects represent conceptual fixture-integrated lighting studies at the controlled head positions. Their Blender energy values are not watts, lumens, candela or measured lux. They are not supplier IES/LDT data.

`RIG_*`, `MACRO_RIG_*`, `ENV_RES_*`, `ENV_STAIR_*`, `ENV_HOSP_*` and `ENV_ATRIUM_*` lights are photographic visualization lights and are not fixture output.

## Generated binary and CI

`VX4800_MASTER.blend` is generated from repository source data. The Blender GitHub workflow rebuilds it with Blender 5.2.1 LTS, validates it inside Blender, refreshes the generated binary when needed, distributes one validated master to independent parallel render jobs, and collects the targeted visual-QA outputs into one review artifact.

The final 0.13 baseline passed both the dedicated Blender workflow and the ordinary repository validation workflow before integration.
