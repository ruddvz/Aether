# AETHERIA Blender visualization pipeline

Blender is AETHERIA's downstream rendering and visualization master for photorealistic product images, finish studies, camera composition, architectural installation imagery and motion review. It does not replace canonical fixture data, manufacturing CAD, structural calculations, supplier qualification, measured photometry or kinetic safety engineering.

The VX4800 pipeline targets Blender 5.2.1 LTS. The build workflow downloads the official Linux distribution and verifies it against Blender's published SHA-256 manifest before execution.

## Data flow

`controlled fixture data + controlled 240-element schedule + controlled 14-head set-out + controlled envelope parameters + conceptual lighting study -> build_scene.py -> lookdev + animation-reference + environment layers -> final refinements -> build_entrypoint.py -> VX4800_MASTER.blend -> Blender-native validation -> named-shot rendering`.

`build_scene.py` is deliberately the controlled-product scene core. `build_entrypoint.py` is the supported complete-master path. The downstream layers may improve presentation, but they may not change controlled IDs, transforms, size allocation or fixed head set-out.

The master records SHA-256 values for source inputs as scene custom properties. Every butterfly instance keeps its `VX-###` element ID and key controlled schedule fields.

## Coordinate and controlled-scene contract

Source X maps to Blender +X, source Y to Blender +Y, source drop-positive-down to Blender -Z, with the canopy underside at Z=0. Blender units are metres.

The controlled visualization mapping remains:

- 240 butterfly instances;
- 66 S / 144 M / 30 L;
- 240 main suspension splines;
- 720 visual yoke/lead splines;
- 14 fixed-position LED-head placeholders;
- one conceptual rotating-field root.

Lookdev, finish studies, environments and camera changes do not become upstream authority.

## Rendering model

Cycles is the production renderer. The current master includes linked faceted optical S/M/L butterfly studies, four metal finish directions, a dark premium studio stage, isolated butterfly macro mode, four architectural contexts and a constant-speed motion reference.

The 14 `RENDER_LIGHT_*` objects are fixture-integrated conceptual light studies at controlled positions. Their Blender energy values are not electrical watts, candela, lumens or lux and do not represent final measured photometry.

Photographic lighting is separate:

- `RIG_*` for clean product imagery;
- `MACRO_RIG_*` for isolated optical-detail QA;
- `ENV_RES_*` for residential photography;
- `ENV_STAIR_*` for staircase photography;
- `ENV_HOSP_*` for hospitality photography;
- `ENV_ATRIUM_*` for atrium photography.

Baseline named shots suppress conceptual fixture beams without deleting or moving their objects.

## Named shots and render UX

`shot_catalogue.json` is the preferred render/review interface. Each named shot binds one existing camera to its purpose, aspect, environment, default quality, high-resolution output profile, preview profile and conceptual fixture-light state.

The current catalogue covers all thirteen cameras exactly once. This prevents common review errors such as rendering a vertical composition through a landscape preset or accidentally using the wrong architectural context.

`render_shot.py --list-shots` prints semantic shot names and available finish variants. Named shots may be rendered at defaults or overridden with compatible quality/output settings. The legacy `--camera` + `--preset` route remains available for advanced use.

## Quality tiers and output profiles

Quality is independent from output size. `render_quality.json` defines `draft`, `lookdev`, `production` and `hero`. `output_profiles.json` separately defines landscape preview/4K, vertical preview/4K and square preview/detail resolutions.

A named shot rejects a profile whose declared aspect does not match the shot. `render_presets.json` remains supported for backwards compatibility rather than serving as the preferred interface.

## Cameras

The thirteen cameras cover:

- clean product hero;
- dramatic low hero;
- full elevation;
- canopy detail;
- isolated butterfly macro;
- lower-tail detail;
- top/set-out technical review;
- residential wide and residential medium;
- vertical installed marketing;
- staircase-void wide;
- hospitality-lobby wide;
- gallery-atrium wide.

Camera geometry is presentation-only. The technical top/set-out camera is a review visualization and does not turn the `.blend` into dimensional CAD.

## Architectural environment library

The environment library provides four visualization-only contexts around the unchanged fixture:

1. double-height luxury residential;
2. staircase void;
3. premium hospitality lobby;
4. gallery atrium.

The dark product stage remains the premium studio context and is not duplicated as a fake fifth architectural environment.

The residential reference establishes the shared quality rules: restrained architecture, believable human scale, clear contrast behind the vortex, no competing decorative hero object, and photographic lighting that supports transparent butterfly readability. The additional environments reuse those rules with different spatial cues.

Room dimensions, floor and ceiling datums, stairs, columns, furniture, plinths, glazing and environment lights are visualization-only. They do not define site interfaces, structural reactions, mounting requirements or customer construction details.

## Optical lookdev

The optical shader uses a physically plausible dielectric/transmission basis with IOR 1.50, low micro-roughness and restrained pale edge absorption. The 0.12 baseline reduces the earlier overly strong absorption so macro and installed views read as transparent decorative material rather than black mirrored leaves.

Thin-film/rainbow effects remain deliberately disabled because no controlled coating specification supports them. Optical lookdev does not approve glass composition, polymer grade, coating, supplier, thickness or optical qualification.

## Finish studies

The visualization finish variants are:

- `dark_champagne`;
- `black_titanium`;
- `brushed_brass`;
- `satin_nickel`.

`render_shot.py --finish ...` applies a presentation-only material override to appropriate visual metal surfaces without changing geometry or controlled engineering data. It does not select a PVD chemistry, substrate, brushing process, colour tolerance, durability specification or supplier.

## Motion reference

The rotating-field action is a constant-speed visualization reference. Its cycle length is derived from the controlled nominal RPM and scene FPS instead of a hard-coded frame count.

The motion reference explicitly excludes acceleration, braking, controlled stopping, power-loss behaviour, jam response, wind, cable dynamics and butterfly flapping. Those remain engineering responsibilities. A smooth Blender rotation is not proof of mechanical safety or dynamic performance.

## Validation and CI

Two independent paths protect the branch.

The ordinary repository workflow validates canonical product data, Blender source policy, controlled geometry, optimized web geometry, regression tests and product builds.

The dedicated Blender workflow:

1. obtains and checksum-verifies Blender 5.2.1 LTS;
2. builds the complete master through `build_entrypoint.py`;
3. opens and validates the generated `.blend` inside Blender;
4. checks controlled counts, visualization revision, cameras, environments, optics and motion-reference metadata;
5. refreshes the generated binary on the feature branch when source changes require it;
6. renders targeted Cycles visual QA for core framing, installed environments and finish variants;
7. uploads individual preview images plus `validation.json`.

The routine visual suite is intentionally targeted rather than rendering every historical camera on every source change. The complete named-shot catalogue remains available for deliberate full review.

## Measured photometry boundary

When exact approved supplier IES/LDT files are controlled, a measured-photometry render mode may be added without deleting or relabelling the conceptual rig. Measured data must retain source provenance and must never be inferred from visually pleasing Blender beams.

## Licensing boundary

Blender is GNU GPL software. Blender-Python scripts under `blender/` carry a GPL-3.0-or-later SPDX header because they use Blender's Python API. Generated artwork and renders are visualization deliverables and do not become engineering/manufacturing authority.
