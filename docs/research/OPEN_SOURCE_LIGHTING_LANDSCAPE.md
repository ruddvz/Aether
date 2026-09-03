# Open-source lighting landscape for AETHERIA

Status: research baseline
Date: 2026-09-03
Scope: fixture data, photometry, CAD/BIM, 3D delivery, control, manufacturing documentation

## Executive conclusion

There is no single open-source repository that already solves the AETHERIA problem. The strongest approach is to build AETHERIA as a small canonical fixture platform and integrate narrowly selected libraries around it.

The recommended core is:

1. AETHERIA-owned fixture schema and package format.
2. Open Fixture Library patterns for schema governance, fixture metadata, validation, generated indexes and adapter architecture.
3. Three.js for presentation, with real IES support added through IESNA data and/or Three.js IES loaders as browser support allows.
4. CadQuery as the existing manufacturing CAD engine, with build123d monitored as a possible future modeling layer.
5. trimesh + Manifold for mesh QA and geometric checks.
6. glTF-Transform for web geometry optimization.
7. three-mesh-bvh for fast picking, clearance and spatial queries in the browser.
8. Colour for CCT, CRI, TM-30 and spectral/color quality analysis.
9. pyGDTF + pyMVR for future professional interchange without coupling AETHERIA to stage-lighting software.
10. IfcOpenShell for offline BIM export and optional web-ifc later if browser-side IFC becomes necessary.
11. Radiance as an offline validation target for serious photometric studies, not as runtime viewer code.

## License policy used in this audit

### Preferred for direct product integration

- MIT
- BSD-2-Clause / BSD-3-Clause
- Apache-2.0

### Acceptable with isolation and review

- MPL-2.0
- LGPL
- custom standards/SDK licenses with clear redistribution terms

### Study or external-tool only by default

- GPL
- AGPL

A repository can still be extremely valuable when its code is not copied. Architecture, workflows, data-model ideas, testing strategies and interoperability concepts can be studied independently.

## Scorecard

Scores are for AETHERIA relevance, not general repository quality.

| Repository | Area | License | Score | Recommendation | What AETHERIA should use |
| --- | --- | --- | ---: | --- | --- |
| OpenLightingProject/open-fixture-library | Fixture data platform | MIT | 10/10 | Integrate patterns now | JSON Schema governance, physical metadata, manufacturer/product registry, validation, plugin adapters, generated indexes, provenance fields |
| mrdoob/three.js | Browser 3D | MIT | 10/10 | Core runtime | Rendering, WebGL/WebGPU, IESLoader, glTF loading, instancing, materials, responsive viewer |
| richard-viney/iesna | Photometry | MIT | 9/10 | Integrate | LM-63 parser, browser-side photometric sampling, polar distribution rendering |
| donmccurdy/glTF-Transform | Web geometry pipeline | MIT | 9/10 | Integrate | Geometry optimization, texture resize/compression, deduplication, mesh/scene transforms |
| gkjohnson/three-mesh-bvh | Spatial QA / browser performance | MIT | 9/10 | Integrate | Accelerated picking, nearest-distance checks, clearance queries, collision inspection |
| CadQuery/cadquery | Parametric CAD | Apache-2.0 | 9/10 | Keep as primary CAD engine | Parametric STEP/DXF/STL generation, assemblies, manufacturing exports |
| mikedh/trimesh | Mesh QA | MIT | 9/10 | Integrate | Watertight checks, bounds, signed distance, nearest points, mesh statistics, scene conversions |
| mozman/ezdxf | DXF | MIT | 9/10 | Integrate | Controlled DXF authoring/reading/validation, set-out drawing automation |
| colour-science/colour | Color science | BSD-3-Clause | 9/10 | Integrate offline | CCT, CRI, CIE colorimetry, ANSI/IES TM-30-18 metrics, spectral analysis |
| open-stage/python-gdtf | Fixture interchange | MIT | 8.5/10 | Add adapter later | Read/write GDTF 1.2, geometry/control metadata export |
| open-stage/python-mvr | Scene interchange | MIT | 8.5/10 | Add adapter later | MVR import/export for CAD/previsualization scene exchange |
| mvrdevelopment/spec | Industry standard | Spec/reference | 8.5/10 | Track as specification | GDTF/MVR semantics, persistent IDs, packaged geometry, revision behavior |
| LBNL-ETA/Radiance | Validated simulation | Radiance distribution terms | 8.5/10 | External validation tool | Offline photometric/light simulation and benchmark renders |
| gumyr/build123d | Parametric CAD | Apache-2.0 | 8/10 | Benchmark/R&D | Modern typed CAD-as-code patterns, possible future modeling API |
| elalish/manifold | Robust geometry | Apache-2.0 | 8/10 | Integrate through Python/mesh tooling | Robust booleans and manifold geometry repair/checking |
| IfcOpenShell/IfcOpenShell | BIM | LGPL/GPL components | 8/10 | Offline adapter | IFC authoring, IfcLightFixture export, property sets, IDS validation |
| changyunhai/IESViewer360 | Photometric UX | MIT | 7.5/10 | Study + selectively reuse | Mobile IES visualization concepts, 2D/3D photometric plots, room-light simulator UX |
| google/model-viewer | Generic 3D viewer | Apache-2.0 | 7.5/10 | Study/fallback | Loading, camera interaction, accessibility, annotations, progressive delivery, AR patterns |
| gkjohnson/three-gpu-pathtracer | High-quality browser render | MIT | 7.5/10 | Optional R&D mode | Progressive path-traced product-review renders where hardware permits |
| ThatOpen/engine_web-ifc | Browser IFC | MPL-2.0 | 7/10 | Optional later | Browser-side IFC reading/writing when architects need web BIM inspection |
| open-stage/blender-dmx | Lighting previsualization | GPL-3.0 | 7/10 | Study/external tool | GDTF/MVR workflows, beam visualization, fixture hierarchy, Blender validation |
| mcallegari/qlcplus | Control | Apache-2.0 | 6.5/10 | Test harness later | DMX/Art-Net/sACN fixture control concepts, profiles, lab control/testing |
| OpenLightingProject/ola | Protocol abstraction | LGPL client / GPL daemon/plugins | 6.5/10 | External control service later | Protocol gateway for DMX, RDM, Art-Net, sACN when AETHERIA gets addressable/kinetic systems |
| mvrdevelopment/libMVRgdtf | GDTF/MVR SDK | Custom MVR SDK license | 6/10 | Reference / avoid unless needed | C++ reference implementation; prefer MIT Python libraries for AETHERIA tooling |
| GitBuilding/GitBuilding | Hardware documentation | GPL-3.0 | 6/10 | External docs tooling / study | BOM-linked assembly documentation, reusable parts libraries, variant build instructions |

## Detailed notes

### 1. OpenLightingProject/open-fixture-library

This is the most important architecture reference.

What is directly relevant:

- JSON Schema for fixture definitions.
- A separate physical section for dimensions, weight, power, light source and lens data.
- fixture metadata with authors, create date, modify date and source links.
- manufacturer registry.
- strict validation and tests.
- plugin-based import/export rather than allowing external software to depend on unstable internal storage.
- generated search/index files.
- fixture editor concepts.
- schema semantic versioning.

What should not be copied literally:

- entertainment-light categories as our main taxonomy.
- DMX channels as a required field for every architectural fixture.
- OFL internal JSON as our canonical schema. OFL itself warns external applications to use adapters because its internal format can make breaking changes.

AETHERIA improvement:

Create an AETHERIA-owned canonical schema designed for architectural sculptural fixtures. Control data becomes optional. Geometry, photometry, materials, suspension, installation, manufacturing, compliance and BIM become first-class data.

### 2. GDTF / MVR ecosystem

Repositories:

- mvrdevelopment/spec
- open-stage/python-gdtf
- open-stage/python-mvr
- mvrdevelopment/libMVRgdtf
- open-stage/blender-dmx

Why it matters:

GDTF treats a device as more than a DMX profile. It can package physical geometry, emitters, attributes and device structure. MVR adds scene placement and persistent object IDs for exchange between CAD and previsualization tools.

AETHERIA should not become GDTF internally. Instead, the AETHERIA package should be richer for architectural/manufacturing use and export a GDTF/MVR subset when appropriate.

Preferred libraries:

- pyGDTF and pyMVR are MIT and Python-native.
- libMVRgdtf has a custom SDK license and more licensing obligations, so it is not the first choice.
- BlenderDMX is GPL and should be used as an external test/reference application, not copied into the AETHERIA viewer.

### 3. IES and photometry

Repositories/tools:

- richard-viney/iesna
- changyunhai/IESViewer360
- Three.js IESLoader / IESSpotLight
- LBNL-ETA/Radiance

AETHERIA needs a real photometric path because fixture presentation cannot remain arbitrary spot-light intensity values forever.

Recommended model:

1. Store manufacturer/test-lab LM-63 `.ies` files as controlled assets.
2. Parse them in build tooling and optionally in browser using IESNA.
3. Generate polar plots and summary metadata.
4. Feed distributions to the web viewer.
5. For WebGPU-capable browsers, evaluate Three.js IESSpotLight.
6. Keep a WebGL-compatible fallback because Three.js currently documents IESSpotLight as WebGPU-only.
7. Validate important fixture configurations offline with Radiance.

Do not generate fake IES files from the visual viewer and present them as tested photometry.

### 4. CAD and geometry

Primary stack:

- CadQuery for exact BREP/STEP/DXF generation.
- trimesh for mesh-level QA and conversion.
- Manifold for robust booleans/repair where useful.
- ezdxf for DXF generation and round-trip validation.
- glTF-Transform for web delivery.

build123d is excellent and should be monitored, but running two canonical CAD kernels/APIs in production would create needless maintenance. The existing AETHERIA work already uses CadQuery, so CadQuery remains primary until there is a measured reason to migrate.

### 5. Browser spatial intelligence

three-mesh-bvh is especially relevant to future AETHERIA tools.

Use cases:

- fast element picking.
- cable-to-element clearance checks.
- element-to-element proximity.
- installation collision checks against imported room geometry.
- measuring nearest fixture surface.
- high-performance raycasts for annotations.

This can move the viewer from a presentation page toward a genuine design-review tool without turning it into full CAD.

### 6. Color and spectral quality

Colour can provide calculated values from measured spectral power distributions:

- CCT and Duv.
- CRI.
- CIE colorimetry.
- ANSI/IES TM-30-18 fidelity/gamut data.
- spectral plots and conversions.

This belongs in offline tooling and generated product data, not heavy browser runtime code.

### 7. BIM

IfcOpenShell is the preferred offline IFC authoring route. It is mature and supports IFC manipulation and geometry. AETHERIA should create an IFC export adapter once the canonical fixture manifest is stable.

Potential output:

- IfcLightFixture product object.
- bounding geometry / coordination geometry.
- dimensions.
- electrical load.
- manufacturer / model / revision.
- maintenance clearances.
- installation height and mounting classification.
- linked photometric/document asset references where appropriate.

web-ifc should only be added when we have a clear browser-side IFC use case. It is MPL-2.0 and would add WASM weight to the public viewer.

### 8. Lighting control

OLA and QLC+ become relevant when AETHERIA moves beyond static fixtures into:

- DMX-controlled lighting scenes.
- addressable LED heads.
- Art-Net/sACN.
- RDM.
- kinetic motor control test rigs.

Do not add these protocols to the public viewer now. Define clean control interfaces in the fixture schema, then use OLA/QLC+ as test/lab infrastructure later.

### 9. Product documentation

GitBuilding is useful as an idea and potentially an external documentation build tool because it connects assembly steps, component metadata and BOM quantities.

AETHERIA should first implement a lighter native structure:

- `bom/`
- `assembly/`
- `installation/`
- `service/`
- `qc/`

If this becomes hard to maintain, evaluate running GitBuilding as a separate documentation job. Do not copy GPL code into the proprietary-facing viewer.

## Repositories intentionally not chosen as core

### Blender itself

Excellent rendering/manufacturing support tool, but GPL and far too broad to become an AETHERIA application dependency. Use Blender as a workstation/toolchain component.

### FreeCAD/OpenSCAD

Useful tools, but AETHERIA already has a Python BREP path through CadQuery. Adding another canonical CAD authoring system would create duplicate truth.

### Full QLC+/OLA stack now

Useful later, premature for a static architectural fixture platform.

### Web IFC now

Useful later, but the public site should not pay the WASM/performance cost until architects actually need in-browser IFC.

## Final shortlist

### Integrate in the first platform phase

- Open Fixture Library patterns
- Three.js
- IESNA
- CadQuery
- trimesh
- Manifold
- ezdxf
- glTF-Transform
- three-mesh-bvh
- Colour

### Build adapters in the second phase

- pyGDTF
- pyMVR
- IfcOpenShell
- Radiance validation

### Keep as external/reference tools

- BlenderDMX
- QLC+
- OLA
- GitBuilding
- three-gpu-pathtracer
- model-viewer
- web-ifc
- libMVRgdtf

## Non-negotiable architecture rule

AETHERIA owns the canonical fixture data model. External formats are adapters. No third-party fixture format, rendering library, BIM schema or DMX application becomes the source of truth for product design.