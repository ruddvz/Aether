# AETHERIA Fixture Platform Plan

Status: proposed architecture
Date: 2026-09-03

## Goal

Turn Aether from a repository containing individual product viewers into a reusable product platform for architectural sculptural lighting.

The platform must support:

- original fixture design.
- parametric geometry.
- photometric data.
- material and finish variants.
- suspension systems.
- static and kinetic products.
- installation and structural interface data.
- manufacturing/BOM documentation.
- web presentation.
- CAD/BIM exchange.
- professional lighting-control exchange when applicable.
- versioned validation and release packaging.

## Core principle

One internal source of truth, many derived formats.

Do not make HTML, STEP, GDTF, IFC, MVR, DXF or a spreadsheet the canonical product definition. They are views or exports of one AETHERIA fixture manifest.

## Proposed repository architecture

```text
Aether/
├── schemas/
│   ├── aether-fixture.schema.json
│   ├── aether-material.schema.json
│   ├── aether-photometry.schema.json
│   └── aether-release.schema.json
├── fixtures/
│   └── vx4800/
│       ├── fixture.json
│       ├── variants/
│       ├── geometry/
│       │   ├── cad/
│       │   ├── coordination/
│       │   └── web/
│       ├── photometry/
│       │   ├── ies/
│       │   ├── spectral/
│       │   └── reports/
│       ├── materials/
│       ├── bom/
│       ├── assembly/
│       ├── installation/
│       ├── compliance/
│       └── presentation/
├── tools/
│   ├── validate/
│   ├── cad/
│   ├── photometry/
│   ├── geometry/
│   ├── viewer/
│   └── exporters/
│       ├── gltf/
│       ├── dxf/
│       ├── ifc/
│       ├── gdtf/
│       └── mvr/
├── web/
│   ├── viewer/
│   ├── catalog/
│   └── components/
└── docs/
```

## Aether Fixture Package

Every product should eventually be releasable as an Aether Fixture Package, or AFP.

Conceptual contents:

```text
VX4800-BF-01.afp/
├── fixture.json
├── manifest.sha256
├── geometry/
│   ├── product.step
│   ├── coordination.glb
│   ├── installation.dxf
│   └── parts/
├── photometry/
│   ├── standard-3000k.ies
│   └── report.json
├── documents/
├── installation/
├── bom/
└── previews/
```

AFP does not need a custom binary container in Phase 1. A normal directory and ZIP with a versioned manifest is safer and easier to audit.

## Canonical fixture manifest

The initial schema should have these top-level domains.

### Identity

- schema version.
- fixture ID.
- product code.
- manufacturer/brand.
- collection.
- name.
- revision.
- lifecycle state: concept, prototype, RFQ, engineering, production, retired.
- authorship/provenance.

### Classification

- architectural pendant.
- sculptural suspension.
- static/kinetic.
- residential/hospitality/commercial/contract.
- indoor/outdoor/environment rating.

### Physical

- overall envelope.
- canopy envelope.
- maximum installed drop.
- measured/calculated mass with status.
- center of gravity when available.
- mounting/interface zones.
- maintenance/service envelope.

### Optical

- emitters.
- CCT options.
- CRI target/tested value.
- TM-30 metrics when measured SPD exists.
- lumen output.
- beam distributions.
- IES assets.
- dimming/control.
- glare-related notes.

### Materials and finishes

- material code.
- supplier/process.
- optical material class.
- finish.
- color specification.
- approved sample status.
- durability/testing data.

### Composition

For suspended sculptures:

- element count.
- element families.
- position IDs.
- suspension exits.
- cable lengths.
- yoke/attachment configuration.
- orientation.
- pose/fold parameters.
- spare quantities.

### Kinematics

Optional:

- fixed assembly.
- moving assembly.
- axis.
- speed range.
- acceleration profile.
- drive type.
- bearing interface.
- braking.
- secondary retention.
- dynamic-clearance status.

### Electrical/control

Optional:

- supply voltage/frequency.
- power.
- driver topology.
- dimming: TRIAC, 0-10V, DALI, DMX, etc.
- control channels/attributes.
- control profile revision.

### Geometry assets

Each asset should include:

- role: manufacturing, coordination, web, preview.
- file path.
- format.
- units.
- coordinate system.
- LOD.
- SHA-256.
- generated-from identifier.
- authority rank.

### BIM/interchange

- IFC class mapping.
- GDTF profile mapping if relevant.
- MVR identifiers.
- Revit/IFC property names.
- classification codes if later adopted.

### Manufacturing

- BOM reference.
- part register.
- assembly revision.
- supplier-return requirements.
- tolerances.
- finish samples.
- packaging.
- QC plan.

### Compliance and verification

- applicable standards.
- target markets.
- test status.
- certificate references.
- design verification checks.
- open engineering issues.

## Adapter architecture

Borrow the plugin philosophy from Open Fixture Library, not its internal fixture format.

```text
Canonical fixture.json
        |
        +--> web viewer model
        +--> product-page data
        +--> STEP/DXF build
        +--> glTF build
        +--> IES report
        +--> IFC exporter
        +--> GDTF exporter
        +--> MVR scene exporter
        +--> manufacturing package
```

Each exporter should declare:

- supported Aether schema versions.
- exporter version.
- required fields.
- fields that cannot be represented by the destination format.
- warnings/loss report.
- generated file hashes.

This avoids silent data loss.

## Implementation phases

### Phase 0: repository recovery and foundation

Current Aether `main` is still only partially bootstrapped. Finish the base repository structure before merging application code.

Deliverables:

- CI.
- Pages deployment.
- dependency/license policy.
- fixture schema directory.
- product registry.
- version rules.

### Phase 1: canonical fixture data

Build `aether-fixture.schema.json` and migrate VORTEX into `fixtures/vx4800/fixture.json`.

Validation requirements:

- JSON Schema.
- unique IDs.
- element counts.
- valid units.
- all referenced assets exist.
- all referenced assets have hashes.
- no duplicate part IDs.
- drop/envelope constraints.
- lifecycle-specific required fields.

Result: viewer data stops being buried inside HTML.

### Phase 2: geometry pipeline

Standardize:

CadQuery -> STEP/DXF/STL -> QA -> glTF/GLB -> optimization -> viewer.

Tools:

- CadQuery.
- ezdxf.
- trimesh.
- Manifold where needed.
- glTF-Transform.

Checks:

- STEP opens.
- DXF opens.
- mesh watertightness where expected.
- bounding dimensions.
- unit correctness.
- triangle budget.
- duplicate geometry.
- orientation/coordinate conventions.

### Phase 3: real photometry

Add `photometry/` as a controlled product domain.

Tools:

- IESNA for LM-63 parsing/sampling.
- Three.js IESLoader for texture generation.
- custom WebGL fallback while IESSpotLight remains WebGPU-only.
- Colour for spectral/color quality reports.
- Radiance for offline validation.

Viewer behavior:

- use real distributions if an IES asset exists.
- clearly label conceptual lighting if no tested IES exists.
- never convert arbitrary WebGL intensity settings into claimed lux/lumen figures.

### Phase 4: viewer architecture

Refactor single-file VORTEX into reusable modules while still supporting a generated standalone HTML release.

Recommended modules:

- scene/background calibration.
- product geometry loader.
- fixture composition.
- photometric lights.
- materials.
- kinematic controller.
- UI mode controller.
- performance profile.
- annotation/measurement.
- asset integrity loader.

Add three-mesh-bvh for selection and spatial review.

Keep generated single-file HTML as a release artifact, not the development source.

### Phase 5: product catalog/editor

Adopt the best OFL idea: edit structured fixture data through forms instead of editing JSON by hand.

AETHERIA editor panels:

- Identity.
- Geometry.
- Composition.
- Materials.
- Lighting.
- Controls.
- Installation.
- Manufacturing.
- Compliance.
- Release.

Every edit must validate against the schema.

### Phase 6: IFC/BIM

Use IfcOpenShell offline first.

Generate:

- IfcLightFixture.
- proxy/coordination geometry.
- product/revision information.
- electrical load.
- dimensional properties.
- installation classification.
- manufacturer documentation references.

Add web-ifc only if in-browser BIM review becomes a real requirement.

### Phase 7: GDTF/MVR interchange

Use pyGDTF and pyMVR.

Do this for products with meaningful controllable behavior.

Export only what is truthful:

- geometry hierarchy.
- emitter/control data.
- DMX attributes if present.
- persistent identifiers.
- scene placement.

Do not force a passive architectural sculpture into fake entertainment-lighting channel semantics.

### Phase 8: control lab

For addressable/kinetic prototypes:

- QLC+ for fixture/control testing.
- OLA as protocol abstraction/gateway.
- BlenderDMX as external previsualization.

Keep lab control separate from the public product viewer.

### Phase 9: manufacturing documentation

Build structured BOM and assembly data from the canonical manifest.

If documentation grows complex, run GitBuilding as an external documentation generator rather than copying its GPL implementation.

## Immediate implementation backlog

### P0

1. Finish Aether repository bootstrap.
2. Add `THIRD_PARTY_POLICY.md`.
3. Add `schemas/aether-fixture.schema.json` draft.
4. Add `fixtures/vx4800/fixture.json` draft.
5. Write validator.
6. Extract V5.2 embedded product data from HTML into canonical fixture data.
7. Generate HTML data bundle from manifest instead of duplicating hard-coded constants.

### P1

8. Add IES asset model and IESNA parser.
9. Add photometric preview page.
10. Add Colour report generator.
11. Add mesh QA with trimesh.
12. Add glTF optimization with glTF-Transform.
13. Add three-mesh-bvh to viewer inspection.
14. Generate asset manifest and hashes.

### P2

15. Add IFC exporter.
16. Add GDTF exporter.
17. Add MVR scene exporter.
18. Add CAD/BIM download panel to product page.
19. Add fixture editor.
20. Add control-lab prototype.

## Definition of done for a production-grade fixture entry

A fixture is not production-grade because the render looks good.

It should eventually have:

- valid canonical manifest.
- controlled geometry.
- measured mass.
- controlled BOM.
- verified light source data.
- IES file or explicit conceptual-lighting status.
- installation information.
- structural interface status.
- electrical status.
- compliance matrix.
- release hashes.
- change history.
- web viewer.
- downloadable coordination geometry.
- documented limitations.

## Decision

Build AETHERIA as a fixture platform inspired by OFL/GDTF interoperability principles, but designed around architectural sculptural lighting and manufacturing reality.