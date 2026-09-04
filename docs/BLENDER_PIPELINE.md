# AETHERIA Blender visualization pipeline

Blender is AETHERIA's rendering and visualization master for photorealistic product images, finish studies, camera composition, marketing animation and design-review imagery. It does not replace canonical fixture data, manufacturing CAD, structural calculations or measured photometry.

The VX4800 pipeline targets Blender 5.2.1 LTS. The build workflow downloads the official Linux distribution and verifies it against Blender's published SHA-256 manifest before execution.

## Data flow

`fixture.json + controlled 240-element schedule + controlled 14-head set-out + controlled envelope parameters + conceptual lighting study -> build_scene.py -> VX4800_MASTER.blend -> validation -> rendering`.

The script records SHA-256 values for all source inputs as scene custom properties. Every butterfly instance keeps its `VX-###` element ID and key controlled schedule fields.

## Coordinate system

Source X maps to Blender +X, source Y to Blender +Y, source drop-positive-down to Blender -Z, with the canopy underside at Z=0. Blender units are metres.

## Scene hierarchy

The master contains fixed canopy, one rotating field, suspension, butterfly instances, fixed head placeholders, cameras, render lights and a neutral studio stage. The rotating field owns the carrier, 240 main cable splines, 720 yoke/lead splines and 240 butterfly instances. The 14 LED head positions stay fixed.

## Rendering model

The first Blender master provides procedural S/M/L optical butterfly prototypes, linked instances, optical glass and metal material studies, six named cameras and four render presets. Cycles is the default master renderer. The conceptual 14-light Blender rig is photographic only: its energy values are not electrical watts, candela, lumens or lux.

When exact supplier IES/LDT files are controlled, add a measured-photometry mode without deleting the conceptual render rig.

## Licensing boundary

Blender is GNU GPL software. Blender-Python scripts under `blender/` carry a GPL-3.0-or-later SPDX header because they use Blender's Python API. Generated artwork and renders are visualization deliverables and do not become engineering/manufacturing authority.
