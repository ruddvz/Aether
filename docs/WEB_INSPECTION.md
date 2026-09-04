# VX4800 web inspection architecture

## Purpose

The web inspection slice provides a browser-focused review tool without changing VORTEX engineering or manufacturing authority.

The public technical inspector is intended for:

- selecting coordination objects by name,
- checking the nearest coordination clearance between butterfly elements,
- taking point-to-point browser measurements,
- placing local review annotations,
- sharing a browser coordination model with architects, designers, engineers and internal reviewers.

It is not a structural, fabrication, electrical, photometric, certification or manufacturing release.

## Authority chain

1. `fixtures/vx4800/composition/engineering-v1.3.0.csv` remains controlled engineering schedule data.
2. `build/vx4800/web/vx4800-coordination-v1.3.0.glb` is the deterministic coordination GLB generated from controlled repository inputs.
3. `vx4800-coordination-v1.3.0.optimized.glb` is a derived web asset only.
4. The browser inspector is a review adapter only.

The optimized GLB may never replace the source coordination GLB in geometry QA or become manufacturing authority.

## Optimization pipeline

`scripts/optimize_web_geometry.py` runs the pinned glTF-Transform CLI package:

- package: `@gltf-transform/cli@4.5.0`
- command: `meshopt`
- level: `medium`

The output uses `EXT_meshopt_compression` and is decoded in the browser by the Three.js Meshopt decoder.

The source coordination GLB already shares only three butterfly meshes across 240 element nodes, so it is unusually compact before compression. For this fixture, Meshopt metadata may make the raw GLB container slightly larger. Raw file-size reduction is therefore not an acceptance criterion. The optimization gate instead verifies a valid Meshopt-encoded derivative, preserved node and mesh identity, bounded overhead, and an unchanged source coordination asset.

The optimization manifest records:

- source SHA-256,
- source byte length,
- optimized SHA-256,
- optimized byte length,
- raw byte ratio and delta,
- optimizer package/version,
- explicit authority constraints.

`scripts/qa_optimized_web_geometry.py` verifies that optimization preserves node identity, including all 240 element nodes, 240 cable nodes and 14 LED-head nodes.

## Browser spatial queries

The inspector pins:

- Three.js `0.185.1`,
- three-mesh-bvh `0.9.14`.

Every unique loaded mesh geometry receives a BVH. Three.js raycasting is replaced with the library's accelerated raycast implementation for surface picking.

For a selected butterfly element, the inspector:

1. computes a conservative surface-distance lower bound for every other element from their world-space bounding spheres,
2. sorts candidates from smallest to largest lower bound,
3. evaluates exact coordination-mesh distances with `MeshBVH.closestPointToGeometry`,
4. stops only when the next candidate's lower bound cannot beat the current exact best distance,
5. reports the resulting nearest surface-to-surface distance in millimetres,
6. visualizes the two closest points with a line.

There is deliberately no fixed candidate-count cap. The lower-bound stop condition makes the result the exact nearest surface pair for the loaded coordination meshes while avoiding unnecessary BVH comparisons.

This is still a coordination-model clearance measurement. It is not a final engineering clearance calculation because the coordination butterfly meshes are deliberately simplified.

## Measurement mode

Measurement mode records two surface hits and displays their straight-line 3D distance in millimetres.

Measurements exist only in the current browser review session. They do not modify fixture JSON, CAD, schedules, or release packages.

## Annotation mode

Annotation mode places a marker at a clicked surface point. Notes are stored in browser `localStorage` under a VX4800-specific key.

Annotations are intentionally local and non-authoritative. Clearing browser storage or using the Clear Review control removes them.

A future controlled review workflow may export annotations into a separate review-record schema, but that must remain distinct from product authority.

## V5.2 historical release authority

The verified historical V5.2 ZIP is guarded by `releases/vx4800/5.2.0/authority.json`.

During repository recovery, live `fixture.json` formatting was compacted without changing the parsed JSON object. The original V5.2 ZIP had serialized that same object with two-space indentation and one trailing newline. `scripts/build_release.py` reproduces that historical member serialization only inside the frozen V5.2 package, then verifies:

- exact archive SHA-256,
- exact archive byte length,
- member order,
- every member byte length,
- every member SHA-256.

Live fixture formatting remains non-authoritative. A semantic fixture change would alter the reconstructed member SHA and fail the release gate.

## Public routes

After the Pages build:

- presentation viewer: `/products/vx4800/`
- technical inspector: `/products/vx4800/inspect/`
- source coordination GLB: `/downloads/vx4800/1.3.0/vx4800-coordination-v1.3.0.glb`
- optimized coordination GLB: `/downloads/vx4800/1.3.0/vx4800-coordination-v1.3.0.optimized.glb`
- optimization manifest: `/downloads/vx4800/1.3.0/optimization-manifest.json`

## Validation gates

The feature must not merge unless:

- canonical fixture validation passes,
- engineering geometry QA passes,
- source web geometry QA passes,
- optimized web geometry QA passes,
- the complete pytest suite passes,
- V5.2 release SHA-256 remains `4cffd5a003a718d359811bf6f3b406d8ad197a92cc3632f9321c6859dca48f79`,
- Pages builds the technical inspector and both coordination GLBs.
