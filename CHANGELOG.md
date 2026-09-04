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

## 2026-09-04 - VX4800 kinetic safety hardening

- Performed an adversarial common-cause review of the first rotating-carrier architecture instead of treating the first green CI run as engineering completion.
- Identified the through-drive brake weakness and added a direct-carrier passive brake-ring/caliper architecture study so transmission failure cannot casually remove the only holding path.
- Strengthened secondary retention with distributed capture/common-cause analysis requirements rather than a single local hub catch feature.
- Added independent/diverse overspeed plausibility, separate brake-fails-to-release/apply handling, no-freewheel manual recovery and jerk-limited motion-profile studies.
- Promoted bearing mounting flatness, support rigidity, fastener preload, post-mount torque/runout and transmission reactions to first-class qualification inputs.
- Added a commissioning/service state model that distinguishes stopped, held, mechanically locked, fault-held and retention-engaged conditions.
- Added a detailed T1-T4 dynamic test plan plus a physical-test record schema that forbids a `passed` result before controlled acceptance criteria exist.
- Added a kinetic hazard/risk-assessment input register covering normal operation, service, fault, recovery and interface hazards without assigning unsupported PL, SIL or category values.
- Added regression gates so future final kinetic release logic must also consume the hardening package, state model, physical-test gates and released risk assessment.
- Preserved the fixed-side powered-system/no-slip-ring boundary and all controlled geometry/composition authority.

## 2026-09-04 - VX4800 kinetic pre-prototype / RFQ engineering

- Added a machine-readable prototype interface package that separates primary bearing, positive drive, direct-carrier brake, service lock, secondary retention, feedback, trim and service-access zones without changing controlled setout.
- Marked bearing section, support-ring stiffness, bolt/preload detail, drive-ring diameter, transmission width/tension, brake radius/ring section, lock section, retention gap/section, feedback air gap and trim capacity as explicit load- or selection-dependent TBDs.
- Added six supplier RFQ packages for bearing, motor/reducer, synchronous transmission, direct-carrier brake, fixed-side feedback and prototype fabrication, with mandatory assumption disclosure and exact-variant documentation.
- Recorded current manufacturer evidence from Kaydon, Gates, RINGSPANN and HEIDENHAIN as architecture/RFQ evidence only, not component selection.
- Added a schedule-derived T1 single-suspension rig and T2 mixed-cluster rig architecture with controlled instrumentation, raw-data traceability, guarding and pre-build risk/structural gates.
- Added schemas and regression tests that block prototype release while measured mass inputs, interface reviews, T1/T2 build releases and prototype drawings remain open.
- Added a prototype/RFQ engineering document with P0/P1/P2 drawing progression and the recommended execution order from RFQ through T1/T2 evidence to later T3/T4 qualification.

## 2026-09-04 - VX4800 kinetic interface control and calculation readiness

- Added a CAD-facing functional datum framework for fixed structure, rotation axis, service/index azimuth and carrier interface plane without converting coordination references into fabrication dimensions.
- Split bearing, positive drive, direct-carrier brake, service lock, distributed secondary retention, primary/diverse feedback, balance/trim and service access into explicit mechanical interfaces with reaction paths and common-cause prohibitions.
- Added a parameter ledger where all selection/load-dependent dimensions remain `null`/`tbd` and each field names the evidence permitted to close it.
- Added closed-loop tolerance requirements for bearing mounting, drive alignment, brake runout, service-lock engagement, retention normal clearance, feedback air gap and component extraction.
- Added explicit CAD failure-state configurations for transmission disconnect, brake application, service locking, primary-support separation, retention engagement, manual recovery and feedback faults.
- Added thirteen traceable normal, fault and service calculation/load cases covering static bearing load, start, steady operation, maximum speed, normal stop, power-loss stop, safe overspeed validation, snag/drag, imbalance, transmission disconnect, service lock, retention engagement and manual recovery.
- Kept all unresolved calculation outputs `null` and required physical T1/T2/T3/T4 correlation for suspended-field transients rather than treating rigid-body inertia as final transient truth.
- Hardened schemas so final interface release requires released non-null parameters and closed tolerance loops, while final calculation release requires every case and output to be verified plus all evidence gates closed.
- Added a deterministic fail-safe P0 DXF generator that reproduces only controlled canopy/carrier coordination, all 240 suspension exits and all 14 fixed accent-head locations while leaving unresolved mechanism footprints as annotation-only TBD callouts.
- Explicitly separated vertical rotation-axis direction from its still-unresolved physical XY datum; the P0 drawing no longer infers the composition origin as the bearing/shaft axis.
- Added regression coverage for authority boundaries, no-slip-ring/fixed-side sensing, common-cause separation, failure-state geometry, traceable TBDs, physical rotation-axis datum gating, P0 drawing behavior and fail-closed release behavior.
