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

## 2026-09-04 - VX4800 rotating-carrier engineering architecture

- Added a machine-readable kinetic architecture for primary load path, bearing/drive studies, braking, positive service locking, independent annular secondary retention, balance/trim, feedback, faults, power loss, dynamic clearance and maintenance.
- Added a manufacturer-scoped qualification shortlist without selecting final bearing, drive, brake or encoder ratings before measured mass/load evidence exists.
- Added calculation frameworks that consume controlled S/M/L mass records, production variation and physical dynamic-test evidence instead of decorative-material assumptions.
- Added staged T1 through T4 dynamic testing ending in a full 240-element factory pre-hang.
- Added JSON Schema and regression gates that prevent final kinetic approval while required mass, component-selection, safety, clearance, test and maintenance gates remain open.
- Preserved the 240-element engineering schedule, S66/M144/L30 allocation, 14 fixed LEDs, canopy envelope, manufacturing authority and fixed-side no-slip-ring electrical boundary.
