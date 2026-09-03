# Open-source implementation priority

Date: 2026-09-03

This file converts the landscape audit into an execution order for AETHERIA.

## Tier A: implement first

1. Open Fixture Library architecture patterns
   - schema-governed fixture metadata
   - provenance
   - physical data
   - generated registries
   - validation
   - import/export adapters

2. CadQuery + ezdxf + trimesh + Manifold
   - one controlled geometry pipeline
   - STEP/DXF/STL generation
   - mesh QA and bounds
   - robust geometry operations

3. Three.js + glTF-Transform + three-mesh-bvh
   - reusable web viewer
   - optimized GLB assets
   - fast selection and spatial inspection

4. IESNA + Colour
   - real LM-63 data parsing
   - polar/photometric plots
   - CCT, CRI and TM-30 reports when measured data exists

## Tier B: implement after canonical fixture schema is stable

5. IfcOpenShell
   - offline IFC export
   - IfcLightFixture mapping
   - BIM properties and coordination geometry

6. pyGDTF + pyMVR
   - professional entertainment/previsualization interoperability
   - only for products where the mappings are meaningful

7. Radiance
   - offline lighting simulation and benchmark validation

## Tier C: keep external or experimental

8. BlenderDMX
   - external GDTF/MVR and DMX previsualization

9. QLC+ and OLA
   - future control-lab and kinetic/addressable-light testing

10. model-viewer and three-gpu-pathtracer
    - UX and rendering experiments, not canonical runtime

11. web-ifc
    - only if browser BIM becomes a proven requirement

12. GitBuilding
    - study BOM-linked hardware documentation or run externally if needed

## First implementation milestone

The first milestone is complete when:

- `schemas/aether-fixture.schema.json` validates VORTEX.
- VORTEX has a standalone canonical `fixture.json`.
- viewer configuration is generated from that manifest instead of being the only source of truth.
- geometry assets have role, units, authority and SHA-256 metadata.
- CI rejects invalid fixture records and broken asset references.
- conceptual photometry is clearly distinguished from tested IES data.

Do not add IFC, GDTF, MVR or DMX code before this milestone. Those integrations depend on having a stable AETHERIA source model first.