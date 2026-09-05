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
- [x] Radiance validation workflow
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
  - [x] Separate repository validation from physical/certification evidence
  - [x] Define IEC / India / North America standards target and applicability-review matrix
  - [x] Define first-article, construction-release and production-release evidence gates
  - [x] Define full 240-element pre-hang, serviceability and deviation/re-test framework
  - [ ] Confirm exact standards/applicability with selected certification body/laboratory
  - [ ] Freeze exact first-article configuration/BOM
  - [ ] Complete first-article inspection and physical qualification
  - [ ] Complete applicable third-party luminaire safety/conformity tests
  - [ ] Compile controlled technical construction/release evidence file
  - [ ] Approve project-specific construction release
  - [ ] Approve repeatable production release and factory routine controls

## Blender visualization and rendering
- [x] Pin Blender 5.2.1 LTS visualization baseline
- [x] Deterministic complete-master generator from controlled repository data
- [x] Preserve 240 traceable butterfly instances and 66 S / 144 M / 30 L allocation
- [x] Preserve 240 main suspension splines, 720 visual yoke/lead splines and 14 fixed head positions
- [x] Linked S/M/L optical visualization prototypes and isolated macro QA
- [x] Four reversible visualization finish studies: dark champagne, black titanium, brushed brass and satin nickel
- [x] Thirteen cameras and thirteen validated named shots
- [x] Dark premium studio plus residential, staircase, hospitality and atrium installed contexts
- [x] Independent draft/lookdev/production/hero quality tiers and landscape/vertical/square output profiles
- [x] Blender-native authority/count/environment/lookdev validation
- [x] Repeated-refinement idempotence and sequential finish-switch validation
- [x] Parallel Cycles visual-QA workflow from one validated master
- [x] Constant-speed nominal-RPM visualization reference derived from RPM and scene FPS
- [ ] Add measured supplier IES/LDT render mode after exact approved supplier/lab files are controlled
- [ ] Add physically authoritative dynamic animation only after kinetic engineering defines acceleration, braking, abnormal-state and cable-dynamics requirements

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
- [x] IfcOpenShell IFC coordination export
- [ ] pyGDTF export for controllable products
- [ ] pyMVR scene export
- [x] Loss-reporting adapter framework

## Multi-product platform
- [x] Registry-driven AETHERIA catalog root
- [ ] Shared viewer UI package
- [ ] Shared material library
- [ ] Shared photometry library
- [ ] Shared Blender material/render library
- [x] Fixture editor driven by JSON Schema
- [x] Collection navigation for FLIGHT, OCEAN, BOTANICA, CELESTIAL and ABSTRACT MOTION
