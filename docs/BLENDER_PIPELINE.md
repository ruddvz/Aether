# AETHERIA Blender visualization pipeline

Blender is AETHERIA's rendering and visualization master for photorealistic product images, finish studies, camera composition, architectural installation imagery, marketing animation and design-review imagery. It does not replace canonical fixture data, manufacturing CAD, structural calculations, supplier qualification or measured photometry.

The VX4800 pipeline targets Blender 5.2.1 LTS. The build workflow downloads the official Linux distribution and verifies it against Blender's published SHA-256 manifest before execution.

## Data flow

`controlled fixture data + controlled 240-element schedule + controlled 14-head set-out + controlled envelope parameters + conceptual lighting study -> build_scene.py -> lookdev/environment layers -> build_entrypoint.py -> VX4800_MASTER.blend -> Blender-native validation -> rendering`.

`build_scene.py` is deliberately the controlled-product scene core. `build_entrypoint.py` is the supported complete-master build path because it applies the downstream visualization-only lookdev and environment libraries before saving the final `.blend`.

The script records SHA-256 values for source inputs as scene custom properties. Every butterfly instance keeps its `VX-###` element ID and key controlled schedule fields.

## Coordinate system

Source X maps to Blender +X, source Y to Blender +Y, source drop-positive-down to Blender -Z, with the canopy underside at Z=0. Blender units are metres.

## Scene hierarchy

The master separates fixed canopy, conceptual rotating field, suspension, butterfly instances, fixed head placeholders, cameras, fixture-integrated conceptual lights, photographic render lights, studio stage and visualization-only architectural environments.

The rotating field owns the carrier, 240 main cable splines, 720 yoke/lead splines and 240 butterfly instances. The 14 LED head positions stay fixed. Artistic lookdev must not change the controlled element IDs, schedule transforms or 66 S / 144 M / 30 L allocation.

## Rendering model

Cycles is the production renderer. The current master includes linked faceted optical S/M/L butterfly studies, premium metal finish directions, a dark studio product stage, an isolated butterfly macro mode and a double-height residential visualization environment.

The 14 `RENDER_LIGHT_*` objects are fixture-integrated conceptual light studies at controlled positions. Their Blender energy values are not electrical watts, candela, lumens or lux and do not represent final measured photometry.

Photographic lighting is separate:

- `RIG_*` for clean product imagery;
- `MACRO_RIG_*` for isolated optical-detail QA;
- `ENV_RES_*` for architectural environment photography.

Baseline named shots suppress the conceptual fixture beams without deleting or moving their objects.

## Named shots and render UX

`shot_catalogue.json` is the preferred render/review interface. Each named shot binds:

- one existing camera;
- intended visual purpose;
- expected aspect ratio;
- studio, macro or architectural environment role;
- default production quality tier;
- default high-resolution output profile;
- lightweight preview output profile;
- conceptual fixture-light state.

The current catalogue covers all ten cameras exactly once. This prevents a common review error where a valid camera is accidentally rendered through the wrong aspect preset.

`render_shot.py --list-shots` prints the available semantic shot names. A named shot can be rendered at its defaults or overridden with a compatible quality tier/output profile. The legacy `--camera` + `--preset` route remains available for advanced use.

## Quality tiers

Quality is independent from output size:

- `draft`: very low samples for layout checks;
- `lookdev`: moderate preview quality for materials, lights and camera iteration;
- `production`: higher-quality final working renders with 16-bit output;
- `hero`: high-sample final hero/detail rendering with tighter adaptive sampling.

The quality definitions live in `render_quality.json`. They intentionally avoid blindly maximizing sample count.

## Output profiles

Resolution/aspect lives separately in `output_profiles.json`:

- landscape preview and 4K;
- vertical preview and 2160 x 3840 marketing output;
- square preview and 4096 x 4096 detail output.

A named shot rejects an output profile whose declared aspect does not match the shot.

The older `render_presets.json` remains temporarily supported for backwards compatibility with existing commands and integrations.

## Cameras and render modes

The master currently carries ten named cameras spanning product hero, dramatic low hero, full elevation, canopy detail, butterfly macro, lower-tail detail, top/set-out review, residential wide, residential medium and vertical marketing composition.

`render_shot.py` prepares the correct visualization mode for the selected camera. Architectural cameras enable their environment and hide the studio stage. The macro camera hides unrelated field objects only for rendering and does not modify the controlled target element.

## Architectural environments

Architectural geometry is visualization-only and exists to establish believable scale, mounting context, materials and photographic composition. The current residential scene uses a flat mounting ceiling zone around the unchanged canopy and a visual floor datum. Those room dimensions are not site-interface or structural design values.

The residential reference environment now uses a dark warm-stone contrast zone, walnut joinery, floor-to-ceiling glazing, restrained furniture and procedural surface variation. The goal is photographic context and scale, not an interior-design claim.

Future staircase, hospitality and atrium environments should reuse the same rule: architecture supports the chandelier, remains realistically scaled and never becomes upstream product authority.

## Optical and finish studies

The current optical shader uses a physically plausible dielectric/transmission basis and deliberately avoids unsupported fantasy dispersion. It remains a lookdev study rather than a commercial material specification.

Metal finish variants and their micro-roughness/brushing are also visualization studies. They support finish comparison renders but do not freeze a supplier process or manufacturing finish specification.

## Validation and CI

The dedicated Blender workflow:

1. obtains and checksum-verifies Blender 5.2.1 LTS;
2. builds the complete master through `build_entrypoint.py`;
3. opens and validates the generated `.blend` inside Blender;
4. refreshes the generated binary on the feature branch;
5. renders a nine-image Cycles visual-QA suite using named shots and aspect-correct preview profiles;
6. uploads the validation report and individual preview images as workflow artifacts.

The ordinary repository workflow separately validates canonical product data, Blender source policy, controlled geometry, web geometry, regression tests and repository artifacts.

## Measured photometry boundary

When exact approved supplier IES/LDT files are controlled, add a measured-photometry render mode without deleting or relabelling the conceptual rig. Measured data must retain source provenance and must not be inferred from visually pleasing Blender beams.

## Licensing boundary

Blender is GNU GPL software. Blender-Python scripts under `blender/` carry a GPL-3.0-or-later SPDX header because they use Blender's Python API. Generated artwork and renders are visualization deliverables and do not become engineering/manufacturing authority.
