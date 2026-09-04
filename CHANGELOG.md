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

- Added the Blender 5.2.1 LTS visualization master generated from controlled VX4800 repository data.
- Preserved all 240 engineering element identities and the controlled 66 S / 144 M / 30 L allocation inside linked Blender instances.
- Added Blender-native validation for controlled instance counts, suspension splines, fixed LED placeholders, conceptual fixture lights, cameras, materials and visualization authority.
- Added procedural faceted optical butterfly studies with linked S/M/L prototypes, physically plausible transmission/IOR lookdev and visualization-only sculptural spine refinement.
- Added premium dark-champagne, black-titanium, brushed-brass, satin-nickel and stainless visual material studies with micro-roughness.
- Separated the 14 fixture-integrated conceptual light studies from photographic product, macro and architectural lighting rigs.
- Added dark-studio hero, isolated butterfly macro and double-height residential architectural visualization modes.
- Added a visualization-only residential environment with flat mounting ceiling context, glazing, restrained furniture, material hierarchy and procedural surface variation.
- Added ten traceable product/detail/technical/architectural cameras and a named-shot catalogue covering every camera.
- Separated render quality tiers from landscape, vertical and square output profiles while retaining legacy preset compatibility.
- Expanded Blender CI from a single preview into a nine-image aspect-correct Cycles visual-QA suite plus Blender-native validation artifacts.
- Corrected the human build instructions so local complete-master builds use the same `build_entrypoint.py` path as GitHub Actions.
- Kept engineering revision 1.3.0, controlled coordinates, fixed head set-out and manufacturing authority unchanged throughout the visualization work.
