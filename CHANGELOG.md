# Changelog

All notable repository and product presentation changes are recorded here.

## [Repository bootstrap] - 2026-09-03

### Added
- Initial AETHERIA repository architecture.
- VORTEX VX4800 viewer v5.2.0 as the first product.
- Product registry in `project.json`.
- GitHub Pages build and deployment workflow.
- Repository validation workflow.
- Versioning, Pages, repository structure and product pipeline documentation.
- Pull request, issue and ownership conventions.
- Historical ZIP snapshots were used only as handoff bundles before the repository became the active source of truth.

## [VORTEX viewer 5.2.0]

- Unified bottom control island.
- Scene, Vortex and Detail review modes.
- Warm ivory product-review cyclorama.
- Dedicated high-detail butterfly study.
- Stable 240-cable suspension logic.
- Mobile touch-target and performance refinements.

## 2026-09-03 - GitHub source recovery

- Restored the verified local AETHERIA platform source tree onto the recovery branch after GitHub write access returned.
- Preserved controlled product data and the coordination GLB hash during recovery.
- Corrected roadmap state for the completed split viewer source and measured-distribution adapter.
- Kept the recovery pull request in draft until GitHub CI reproduced local validation.

## 2026-09-03 - supplier photometry integration slice

- Added five real supplier research candidate records for VX4800.
- Changed candidate schema so unknown exact fields can be represented as `null` instead of fabricated placeholders.
- Strengthened candidate evaluator checks for missing exact model code, optic code, CCT, CRI, lumen output and driver model.
- Added generated JSON and Markdown evaluator reviews for all five research candidates.
- Added a renderer-neutral measured-distribution browser adapter gated by controlled SHA-256 and provenance.
- Added explicit rejection of unsupported multi-plane distributions in the first browser adapter.
- Kept V5.2 presentation output unchanged until exact supplier/laboratory files are controlled.

## 2026-09-04 - VX4800 technical inspection slice

- Added a derived Meshopt web-geometry pipeline using pinned glTF-Transform CLI 4.5.0.
- Added an optimization manifest and QA that preserve all 240 element nodes, 240 suspension-cable nodes and 14 fixed LED-head nodes.
- Added the dedicated `/products/vx4800/inspect/` browser inspector with pinned Three.js 0.185.1 and three-mesh-bvh 0.9.14.
- Added BVH-accelerated picking, exact nearest coordination-mesh surface clearance, point-to-point measurement and browser-local review annotations.
- Replaced the early fixed 18-candidate proximity shortcut with lower-bound branch-and-bound traversal so nearest-clearance review is exact for the loaded coordination meshes.
- Added Pages publication for the technical inspector, source coordination GLB, derived Meshopt GLB and optimization manifest.
- Replaced archive-oriented build steps with `scripts/build_product.py`, which builds repository product artifacts directly without generating ZIP packages.
- Removed ZIP-specific CI gates and download publication from the active repository workflow.
- Kept engineering revision 1.3.0 and presentation revision 5.2.0 unchanged; the new web tooling remains review-only and cannot become manufacturing authority.

## 2026-09-04 - VX4800 Blender visualization and photoreal pipeline

- Added a Blender 5.2.1 LTS visualization master generated from controlled VX4800 repository data.
- Preserved all 240 engineering element identities, the controlled 66 S / 144 M / 30 L allocation, 240 main suspension splines, 720 visual yoke/lead splines and 14 fixed head positions.
- Added Blender-native validation for controlled counts, source provenance, cameras, environments, optical lookdev, motion-reference metadata, repeated-refinement idempotence and sequential finish switching.
- Added linked faceted S/M/L optical butterfly studies with physically plausible transmission/IOR lookdev, restrained visualization-only absorption and a reduced sculptural centre.
- Added dark-champagne, black-titanium, brushed-brass and satin-nickel render-time finish studies without promoting any finish to manufacturing authority.
- Separated the 14 fixture-integrated conceptual light studies from product, macro and architectural photographic rigs.
- Added dark premium studio product photography plus isolated butterfly macro review.
- Added four visualization-only installed contexts: double-height residential, staircase void, hospitality lobby and gallery atrium.
- Added thirteen traceable product/detail/technical/architectural cameras and thirteen validated named shots.
- Added independent `draft`, `lookdev`, `production` and `hero` quality tiers plus landscape, vertical and square output profiles while retaining legacy preset compatibility.
- Added a constant-speed rotating-field visualization action whose cycle length is derived from controlled nominal RPM and scene FPS; acceleration, braking, jam response and dynamic safety remain outside Blender authority.
- Reworked CI into one checksum-pinned authoritative Blender build/validation job, parallel independent Cycles QA renders, and one combined validation/render artifact.
- Closed the final 0.13 visual QA with approved product hero, full elevation, optical macro, residential wide/medium, vertical marketing, staircase, hospitality, atrium and alternate-finish previews.
- Corrected headless environment activation for saved `.blend` reloads and made final refinement/finish operations safe for repeated interactive use.
- Corrected human documentation so local complete-master builds use the same `build_entrypoint.py` path and authority model as GitHub Actions.
- Kept engineering revision 1.3.0, presentation revision 5.2.0, controlled coordinates, fixed head set-out and all unresolved physical qualification gates unchanged throughout the visualization work.

## 2026-09-04 - VX4800 interchange loss-reporting framework

- Added a machine-readable interchange loss-report schema and VX4800 target policy for IFC, GDTF and MVR.
- Bound interchange review to canonical fixture SHA-256 plus the controlled 240-element, 66 S / 144 M / 30 L, 240-suspension and 14-head invariants.
- Added deterministic target reports that classify mappings as preserved, approximated, external-reference or omitted and separate warnings from blocking losses.
- Allowed IFC only at coordination-only authority while explicitly preserving manufacturing, structural, photometry, kinetic-safety and construction-release boundaries.
- Kept GDTF blocked until exact head/optic and applicable control-personality data are released.
- Kept lighting-authoritative MVR blocked until the GDTF dependency and controlled final head aiming are released.
- Added regression tests that reject controlled-count drift and any interchange profile that attempts to claim engineering or release authority.
