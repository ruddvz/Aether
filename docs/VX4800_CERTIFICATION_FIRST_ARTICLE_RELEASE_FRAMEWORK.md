# VX4800 Certification, First-Article and Release Framework

Product: AETHERIA VORTEX  
Model: VX4800-BF-01  
Design revision: 1.3.0  
Framework revision: 1.0.0  
Status: qualification plan, not certification or construction release

## 1. Purpose

This document defines how VX4800 progresses from a repository-valid prototype design to a physically qualified first article and, later, a project-specific construction release and repeatable production release.

It exists to prevent four different ideas from being collapsed into one word such as `validated`:

1. repository/package consistency;
2. supplier component evidence;
3. engineering calculations and risk decisions;
4. physical product tests and third-party conformity evidence.

The existing `fixtures/vx4800/documents/final-validation-v1.3.0.md` is retained as historical controlled package-validation evidence. It verifies digital/package conditions such as schedule counts and geometry intent. It explicitly does not certify the rotating mechanism, structure, drive or occupied-space installation.

A green GitHub Actions run is necessary repository evidence, but it is never a substitute for a load test, electrical safety test, thermal test, fatigue test, dynamic pre-hang or certification-body report.

## 2. Current product state

The product remains a prototype/RFQ design.

Known controlled design facts include:

- 240 engineering butterfly elements;
- S66 / M144 / L30 engineering allocation;
- 14 fixed accent-head locations;
- maximum controlled lower edge below the canopy: 4778 mm;
- fixed canopy envelope: 2400 x 1500 x 150 mm;
- repository-generated coordination geometry is not manufacturing BREP authority.

Major release inputs remain unresolved, including actual installed mass, rotating mass and centre of gravity, final material/attachment system, final suspension system, released kinetic mechanism, project structural reactions, exact luminaire/control gear, measured photometry and full first-article test evidence.

## 3. Standards target matrix

Standards listed here are targets for applicability review. Listing a standard does not mean the product complies with it.

### 3.1 IEC-oriented luminaire path

Current official IEC publications checked for this framework:

- `IEC 60598-1:2024`, Luminaires - Part 1: General requirements and tests, Edition 10.0, published 2024-11-06.
- `IEC 60598-2-1:2025`, Luminaires - Part 2-1: Particular requirements - Fixed general purpose luminaires, Edition 3.0, published 2025-12-02.
- `IECEE TRF 60598-2-1L:2026`, published 2026-02-27, applies IEC 60598-2-1:2025 in conjunction with IEC 60598-1:2024.

IEC 60598-1:2024 includes requirements relevant to marking, construction, conductor mechanical stress, earthing, serviceable components and photobiological safety, among many other luminaire safety topics.

The certification body must confirm the exact applicability of Part 2-1 to the released VX4800 configuration and identify any additional requirements created by the kinetic mechanism.

### 3.2 India

BIS sources checked for this framework currently list:

- `IS 10322 (Part 1):2026`, Luminaires Part 1 General Requirements and Tests;
- `IS 10322 (Part 5/Sec 1):2026`, Luminaires Part 5: Particular requirements Section 1: Fixed general purpose luminaires.

The BIS Compulsory Registration Scheme standard list currently includes IS 10322 (Part 5/Sec 1):2026 under Fixed General Purpose LED Luminaires.

This is not a declaration that VX4800 is automatically in scope or registered. Exact product classification, registration route, factory scope, marking and any kinetic-specific requirements must be confirmed with BIS/recognized laboratory/certification specialists for the intended release.

### 3.3 United States and Canada

The current North American target remains the harmonized luminaire family centred on:

- UL 1598, Luminaires, 5th edition;
- CSA C22.2 No. 250.0-21, Luminaires, harmonized trinational edition.

UL Solutions currently identifies UL 1598 5th edition in its lighting safety resources. The published CSA/UL harmonized standard metadata identifies the 2021 edition as the fifth CSA edition and fifth UL 1598 edition.

An NRTL/SCC certification body must confirm the final path, component standards, installation-code interfaces and how the kinetic mechanism is treated.

## 4. Evidence hierarchy

### 4.1 Repository evidence

Examples:

- controlled JSON/CSV schedules;
- schema validation;
- deterministic build fingerprints;
- STEP/DXF/GLB coordination QA;
- regression tests;
- version-controlled drawings/documents.

Repository evidence can prove what configuration was intended and whether digital constraints are internally consistent. It cannot prove physical strength, electrical safety, thermal behavior, dynamic performance or certification.

### 4.2 Supplier evidence

Examples:

- exact datasheets;
- exact model/option declarations;
- cable/gripper ratings;
- bearing and drive data;
- control gear data;
- DALI certification records where applicable;
- exact IES files and photometric reports;
- material/process certificates;
- component conformity records.

Supplier evidence only applies to the exact selected configuration. Component certificates do not certify the complete VX4800 fixture.

### 4.3 Engineering evidence

Examples:

- structural calculation;
- suspension line-load calculation;
- bearing/drive/brake calculations;
- kinetic risk assessment;
- electrical protection and conductor calculations;
- thermal assessment;
- balance calculation;
- dynamic-clearance analysis;
- approved deviations.

Engineering calculations must use controlled physical inputs. Unknown mass, centre of gravity, torque, thermal or dynamic inputs may not be filled with presentation values merely to complete a calculation.

### 4.4 Physical evidence

Examples:

- measured mass;
- pull/slip/fatigue tests;
- attachment proof tests;
- bearing/drive trial;
- electrical tests;
- thermal soak/endurance;
- full 240-element pre-hang;
- dynamic-clearance measurements;
- fault-stop and power-loss trials;
- service replacement trials;
- first-article inspection.

A physical test record must identify the exact test article, configuration revision, test equipment, equipment status/calibration where relevant, procedure, acceptance criterion, measured result, photographs/data and disposition.

### 4.5 Third-party evidence

Where required by the market path, this includes accredited laboratory, certification body, inspection body or authority evidence.

The release package must retain the exact report/certificate identity and the exact product/configuration it covers.

## 5. Release stages

### Stage A - design review

Goal: digital baseline is coherent enough to support prototype/RFQ work.

This stage can be supported primarily by repository and engineering evidence.

It is not permission to install the product over occupied space.

### Stage B - prototype test

Goal: representative subsystems exist for engineering investigation.

Typical articles:

- representative S/M/L butterfly assemblies;
- lower bridle/yoke;
- cable/gripper samples;
- bearing/drive rig;
- service-lock prototype;
- electrical service-board/mock canopy zone;
- representative butterfly cluster.

Prototype evidence may change the design and therefore is not automatically production evidence.

### Stage C - first article

Goal: build one production-intent fixture representing the exact proposed release configuration.

The first article must be traceable to a frozen BOM/drawing/configuration set.

### Stage D - construction release

Goal: approve a named product/project configuration for manufacture and installation based on completed product evidence plus project-specific structural/site interfaces.

Construction release is not generic. A material, motor, bearing, control gear, suspension or structural change can invalidate relevant evidence.

### Stage E - production release

Goal: demonstrate the configuration and manufacturing/test process can be repeated with controlled production checks, traceability and change control.

## 6. Configuration freeze before first article

Before the first complete article is accepted for qualification, freeze at minimum:

- product code and revision;
- manufacturing drawing/BREP references;
- 240-element engineering schedule;
- exact material tier and process;
- exact S/M/L attachment revisions;
- exact suspension cable/gripper/terminal/yoke system;
- exact carrier/bearing/drive/brake/service-lock/secondary-retention configuration;
- exact accent head/optic/CCT configuration;
- exact PSU/control gear and control topology;
- exact wiring/connectors/protection components;
- canopy structural and service-zone configuration;
- finish/process specification;
- software/firmware/configuration identifiers where applicable;
- installation/interface drawing revision.

Every qualification record must point to this configuration identity.

## 7. First-article inspection sequence

### 7.1 Incoming and traceability

Verify:

- exact supplier and part identities;
- material batches/process records;
- safety-critical hardware certificates where required;
- cable/gripper/terminal lots;
- bearing/drive/brake IDs;
- head/control-gear IDs;
- fastener grades;
- finish sample/process identity;
- deviations already approved before build.

### 7.2 Dimensional/configuration inspection

Inspect the built article against controlled manufacturing drawings and schedules.

At minimum verify:

- canopy envelope and critical interfaces;
- carrier geometry/interfaces;
- all 240 cable-exit identities;
- 14 fixed head positions;
- suspension lengths/setout identity;
- service clearances;
- drive/bearing/service-lock interfaces;
- secondary-retention interfaces;
- structural interface zones;
- electrical segregation and access zones.

Repository coordination geometry may be used as a review aid but is not the acceptance manufacturing geometry authority.

### 7.3 Mass and balance

Physically measure:

- complete installed mass;
- fixed canopy/service mass as needed by structural calculation;
- complete rotating mass;
- S/M/L suspended-assembly masses from production-intent samples/lots;
- centre of gravity or equivalent balance data required by the mechanical engineer;
- production variation sufficient to set balance/trim acceptance criteria.

Update structural, bearing, drive and suspension calculations after measured inputs are controlled.

## 8. Mechanical and suspension qualification

The release package must close the open evidence from the suspension/material/kinetic tracks.

Required evidence includes, as applicable:

- exact cable/gripper/terminal WLL/rating basis;
- complete lower-yoke/bridle design;
- line-load calculation using controlled mass and dynamic factors;
- pull/slip tests;
- fatigue/cyclic tests;
- local butterfly attachment proof/fatigue tests;
- failure/fragment-retention strategy;
- primary bearing/load path;
- independent secondary retention;
- service lock;
- balance/trim process;
- fastener retention;
- inspection/access procedure.

A supplier static WLL is not the VX4800 design load.

## 9. Structural release

The project structural calculation must use the released product and actual site structure.

It must address at minimum:

- dead load;
- rotating assembly load;
- eccentricity/centre of gravity;
- kinetic/dynamic load cases approved by the mechanical engineer;
- start/stop/fault load cases where relevant;
- primary and secondary load paths;
- interface reactions;
- anchor/interface design;
- local canopy/frame stresses and deflection;
- relevant installation tolerances;
- service/load-test conditions if required.

The false ceiling is never a structural support unless it is itself an explicitly engineered structural system for the released loads.

## 10. Kinetic first-article tests

The rotating-mechanism track owns the detailed procedure. The certification/release framework requires evidence for at least:

- minimum/nominal/maximum released speed;
- controlled acceleration/deceleration;
- normal stop;
- fault stop;
- power-loss behavior;
- safe restart behavior;
- overspeed/feedback disagreement response;
- abnormal torque/jam behavior;
- service-lock operation;
- secondary-retention proof/inspection;
- bearing temperature;
- drive temperature/load;
- vibration;
- audible behavior against the released acceptance criterion;
- balance and trim;
- repeated cycling/endurance requirement;
- maintenance access.

Software fault detection never substitutes for mechanical secondary retention.

## 11. Full 240-element factory pre-hang

A complete production-intent field must be assembled before construction release.

The pre-hang must record at minimum:

- exact 240-element identity/schedule;
- actual line lengths/setout;
- visual alignment against the controlled design;
- balance/trim state;
- speed and motion profile;
- cable angles and pendulum lag under defined transients;
- torsional/oscillatory behavior;
- butterfly-to-butterfly clearance;
- cable-to-cable clearance;
- butterfly-to-cable clearance;
- field-to-fixed-head clearance;
- field-to-canopy clearance;
- start/stop propagation through the suspended field;
- fault/emergency stopping behavior required by the released risk assessment;
- noise/vibration;
- fastener/gripper/terminal inspection after test;
- any damage, slip, rotation, loosening or permanent deformation.

Blender or Three.js clearance views may guide test planning; they cannot close this physical gate.

## 12. Electrical and luminaire safety qualification

The final test plan must be agreed against the applicable standard/certification route for the selected market.

The released product will require evidence covering applicable topics such as:

- construction;
- marking/instructions;
- creepage/clearance where applicable;
- provision for earthing/bonding where applicable;
- terminals;
- internal/external wiring;
- strain/mechanical stress on conductors;
- protection against electric shock;
- insulation/electric strength;
- touch/protective-conductor current where applicable;
- endurance/thermal tests;
- resistance to heat/fire/tracking where applicable;
- photobiological safety where applicable;
- ingress/dust/moisture classification if claimed;
- serviceable component requirements;
- selected control gear/component conditions of acceptability.

Do not copy clause acceptance values into project files from memory. The laboratory/certification body must work from licensed/current standards and the exact released configuration.

## 13. Thermal/endurance

Worst-case testing must reflect the released canopy arrangement and operating duty, including the fixed accent heads/control gear and kinetic electrical equipment.

Record critical temperatures at, as relevant:

- control gear/PSUs;
- wiring/terminals/connectors;
- motor/drive/controller;
- brake;
- nearby polymers/insulation;
- canopy surfaces;
- service compartments.

Acceptance limits must come from the applicable product standard, component ratings and released engineering requirements.

## 14. Photometry/optical release

Before construction release:

- select the exact head family/configuration;
- obtain exact supplier/lab IES bytes with SHA-256 provenance;
- resolve naming/configuration ambiguity;
- independently parse/viewer-cross-check;
- validate optical intent in the intended installation geometry;
- record exact optic/CCT/CRI/control-gear combination;
- retain SPD/TM-30/CRI evidence where required by the project specification.

Conceptual browser cones are not photometric evidence.

## 15. Serviceability qualification

On the production-intent article, demonstrate safe access/replacement for representative service items.

At minimum include:

- accent head;
- PSU/control gear;
- control component;
- kinetic service item identified by the mechanical design;
- suspension cable/gripper/terminal where designed to be field-serviceable;
- butterfly assembly;
- relevant sensor/feedback device.

Verify:

- electrical isolation;
- mechanical service lock;
- no need to energize motion during routine lighting service;
- no destructive access;
- correct reassembly/torque/locking requirements;
- post-service functional checks;
- identification/traceability restored.

## 16. Deviations and failures

A failed test is not converted to a pass by explanatory text.

For every failure/deviation record:

1. identify the exact article/configuration;
2. record the failure or non-conformance;
3. identify root cause to the level appropriate to the risk;
4. define disposition/design change;
5. identify affected prior evidence;
6. update controlled drawings/BOM/software if required;
7. repeat the affected test(s);
8. obtain approval before closing the gate.

A design change after first-article testing must trigger an impact review. Safety-critical changes normally require re-test of the affected evidence chain.

## 17. Technical construction / release file

Before construction release, compile a versioned evidence package containing at minimum:

- released configuration/BOM;
- manufacturing drawing/BREP manifest;
- controlled engineering schedules;
- supplier evidence index;
- physical mass records;
- structural calculation;
- suspension qualification;
- material/attachment qualification;
- kinetic architecture/calculations/tests;
- electrical architecture/calculations/tests;
- thermal/endurance records;
- photometry evidence;
- full pre-hang report;
- first-article inspection report;
- serviceability report;
- risk/deviation register;
- installation instructions;
- service/inspection instructions;
- product markings/rating data;
- market conformity reports/certificates where required;
- project-specific structural/interface approval.

The package must identify every file by revision/hash or another controlled immutable reference.

## 18. Production release and factory controls

Production release comes after successful first article and approved construction configuration.

Define production controls for safety/quality-critical characteristics such as:

- incoming component identity;
- butterfly material/process/batch;
- suspension hardware identity;
- safety-critical fasteners/locking;
- cable length/setout identity;
- electrical wiring/termination;
- bonding/earth continuity where applicable;
- functional lighting test;
- kinetic functional/fault checks;
- balance/trim;
- final inspection;
- serialization/build record;
- packaging/transport restraints;
- site installation and commissioning record.

The exact routine test set must be aligned with the applicable certification route and production risk analysis.

## 19. Change control after release

Changes to any of the following require evidence-impact review before substitution:

- butterfly material/process/thickness;
- butterfly attachment;
- suspension cable/gripper/terminal/yoke;
- bearing;
- drive/motor/gearbox/belt/brake;
- service lock/secondary retention;
- carrier structural geometry;
- head/optic/CCT;
- PSU/control gear;
- wiring/protection/connector;
- canopy structural interface;
- safety-related software/configuration;
- installation envelope/duty.

A commercial `equivalent` is not automatically an engineering equivalent.

## 20. Current release decision

As of framework creation, VX4800 is not approved for construction release or production release.

The machine-readable authority is:

`fixtures/vx4800/compliance/release-gate-v1.json`

All construction and production promotion gates remain false until controlled evidence closes them.
