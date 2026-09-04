# Roadmap

This roadmap describes repository capabilities, not promised commercial release dates.

## Foundation
- [x] Canonical AETHERIA fixture schema
- [x] Engineering and presentation authority separation
- [x] 240-element controlled VORTEX engineering schedule
- [x] Deterministic V5.2 viewer generation
- [x] Repository-native product artifact build and controlled hash validation
- [x] GitHub Pages catalog architecture
- [x] Public versioned JSON Schemas
- [x] Canonical fixture JSON public route
- [x] Coordination STEP/DXF generation and QA
- [x] Coordination GLB generation and QA
- [x] Product registry and immutable viewer routes
- [x] Automated regression validation

## Photometry
- [x] Separate conceptual-photometry domain
- [x] Exact luminaire/head research brief
- [x] Candidate schema and objective evaluator
- [x] LM-63 raw-file ingestion with SHA-256 provenance
- [x] Parsed IES report schema
- [x] Normalized polar SVG generation
- [x] Formal supplier-qualification shortlist
- [ ] Acquire exact supplier/lab IES files
- [ ] Independent parser/viewer cross-check
- [x] Browser measured-distribution adapter
- [ ] Radiance validation workflow
- [ ] SPD ingestion and Colour-based CRI/TM-30 report

## VORTEX product engineering
- [ ] Resolve actual installed mass and center of gravity
  - [x] Define controlled physical S/M/L suspended-assembly mass record
  - [ ] Build production-intent S/M/L samples and measure complete suspended-assembly masses
  - [ ] Establish production mass tolerance and balance inputs
- [ ] Select rated suspension cable/gripper/yoke system
  - [x] Formal 0.81-1.0 mm stainless cable/gripper supplier-qualification shortlist
  - [ ] Control final S/M/L butterfly and lower-yoke masses
  - [ ] Establish kinetic line design load and approved load factors
  - [ ] Engineer and proof-test the lower three-point anti-rotation bridle/yoke
  - [ ] Resolve independent secondary retention
  - [ ] Complete supplier sample pull/slip/fatigue qualification
- [ ] Resolve butterfly attachment detail and material tier
  - [x] Formal ARC / LUX / ART material and attachment qualification architecture
  - [ ] Select exact ARC material/process and validate attachment
  - [ ] Select exact LUX material/process and validate attachment
  - [ ] Select ART glassmaker/process and validate attachment
  - [ ] Freeze optical/cosmetic acceptance standards by tier
  - [ ] Pass production-equivalent attachment proof and fatigue tests
  - [ ] Resolve occupied-space failure/fragment retention strategy
- [ ] Engineer rotating carrier, bearing, drive, braking and secondary retention
  - [x] Define separate primary, drive, braking, service-lock and secondary-retention load paths
  - [x] Preserve fixed-side powered systems and the current no-slip-ring boundary
  - [x] Compare bearing, positive-drive and power-off brake architecture families without inventing ratings
  - [x] Define positive mechanical service lock and normally-clear annular secondary retention
  - [x] Define balance/trim, fixed-side feedback, abnormal-motion and no-auto-restart requirements
  - [x] Define calculation inputs and staged physical dynamics/clearance validation
  - [x] Complete adversarial fault-containment review and identify drive-transmission / holding-path common-cause risk
  - [x] Define direct-carrier brake-ring study without selecting a final brake rating
  - [x] Define distributed secondary-retention common-cause review requirements
  - [x] Define commissioning/service mechanical state model separating held, locked and safe-to-access states
  - [x] Define executable T1-T4 dynamic test plan and physical test-record schema
  - [x] Define kinetic hazard register without inventing PL/SIL/category values
  - [x] Define pre-prototype fixed/rotating interface-zone package for bearing, drive, direct brake, service lock, secondary retention, feedback, trim and service access
  - [x] Define six supplier RFQ packages with assumption disclosure and exact-variant evidence requirements
  - [x] Record current manufacturer evidence for bearing mounting, belt reactions, power-off brake families and fixed-readhead/passive-scale feedback without selecting components
  - [x] Define schedule-derived T1 single-suspension and T2 mixed-cluster test-rig architecture with instrumentation, data and build gates
  - [x] Define CAD-facing functional datums, independent mechanical interfaces, tolerance closures, failure-state models and fail-closed interface release gates
  - [x] Define thirteen traceable normal/fault/service load cases with explicit evidence classes and no unsupported numeric results
  - [x] Generate fail-safe P0 DXF coordination output from controlled setout while refusing unresolved mechanism footprints and any inferred physical rotation-axis XY datum
  - [ ] Issue kinetic RFQs and archive supplier application-engineering responses/CAD
  - [ ] Populate exact supplier mating data and close bearing/drive/brake/lock/retention/feedback tolerance loops
  - [ ] Replace P0 annotation-only mechanism callouts with supplier/evidence-backed parametric interface geometry and failure-state configurations without changing controlled setout
  - [ ] Control rotating mass, center of gravity, production variation and dynamic load cases
  - [ ] Release T1 rig structural/instrument design from controlled mass envelope and execute T1
  - [ ] Release schedule-derived T2 cluster rig and execute T2 after T1 findings are dispositioned
  - [ ] Select bearing and approve combined-load/mounting calculation
  - [ ] Resolve direct-carrier holding/fault-brake architecture and transmission-failure containment
  - [ ] Select drive and approve torque/stopping calculations
  - [ ] Validate service lock, distributed secondary retention, feedback and fault handling
  - [ ] Resolve independent/diverse overspeed monitoring need from released risk assessment
  - [ ] Release kinetic risk assessment and safety-related function allocation
  - [ ] Correlate suspended-field dynamics with drive/brake calculations
  - [ ] Control acoustic acceptance and endurance duty
  - [ ] Pass staged T1-T4 physical qualification and release maintenance plan
- [ ] Structural calculation and site interface reactions
- [ ] Full factory pre-hang and dynamic-clearance test
- [ ] Electrical architecture and service access
  - [x] Separate fixed-canopy lighting / kinetic / auxiliary electrical domains
  - [x] Preserve no-slip-ring architecture while rotating field has no electrical loads
  - [x] Define DALI-2 preferred lighting-control and commissioning architecture
  - [x] Define service access, component identification and replacement requirements
  - [ ] Select exact head and driver/control-gear topology
  - [ ] Resolve protective earthing/bonding and market supply variants
  - [ ] Complete wiring/voltage-drop and canopy thermal validation
  - [ ] Resolve kinetic electrical safety and lockout architecture
  - [ ] Pass first-article electrical/service tests
- [ ] Complete luminaire certification/test plan

## Viewer and review tooling
- [x] Refactor single-file development source into reusable Three.js modules
- [x] Keep generated standalone HTML as a deployable viewer artifact
- [x] Add optimized GLB pipeline with glTF-Transform
- [x] Add three-mesh-bvh inspection and proximity tools
- [x] Add measurement/annotation mode
- [ ] Visual QA across iPhone, Android, Safari, Chrome and desktop
- [ ] Performance budgets and Lighthouse checks
- [ ] Open Graph/share artwork

## Interchange
- [ ] IfcOpenShell IFC export
- [ ] pyGDTF export for controllable products
- [ ] pyMVR scene export
- [ ] Loss-reporting adapter framework

## Multi-product platform
- [x] Registry-driven AETHERIA catalog root
- [ ] Shared viewer UI package
- [ ] Shared material library
- [ ] Shared photometry library
- [ ] Fixture editor driven by JSON Schema
- [ ] Collection navigation for FLIGHT, OCEAN, BOTANICA, CELESTIAL and ABSTRACT MOTION
