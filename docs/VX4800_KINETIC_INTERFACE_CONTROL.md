# VX4800 Kinetic Mechanical Interface Control and Calculation Readiness

Status: engineering development input, not released for manufacture or installation.

Fixture: AETHERIA VORTEX VX4800-BF-01  
Controlled product engineering revision: 1.3.0

## Purpose

This document converts the rotating-carrier architecture into a CAD-facing mechanical interface and calculation framework. It deliberately stops short of inventing dimensions, loads or component ratings that depend on physical mass data, released risk cases or exact supplier variants.

The authoritative machine-readable companions are:

- `fixtures/vx4800/kinetics/interface-control-v1.json`
- `schemas/aether-kinetic-interface-control.schema.json`
- `fixtures/vx4800/kinetics/qualification/calculation-register-v1.json`
- `schemas/aether-kinetic-calculation-register.schema.json`

The controlled P0 coordination generator is:

- `scripts/generate_kinetic_p0.py`
- output: `build/vx4800/kinetics/vx4800-kinetic-p0-interface-v1.dxf`
- output manifest: `build/vx4800/kinetics/vx4800-kinetic-p0-interface-v1.manifest.json`

The P0 generator is intentionally fail-safe. It reproduces controlled canopy/carrier coordination outlines, the 240 controlled suspension exits and 14 fixed accent-head locations, but it does not draw load- or supplier-dependent bearing, drive, brake, service-lock, retention or sensor mating footprints while those parameters remain unresolved. Generated P0 output is coordination evidence only and is not manufacturing authority.

The pre-prototype/RFQ layer remains in:

- `fixtures/vx4800/kinetics/prototype-package-v1.json`
- `fixtures/vx4800/kinetics/qualification/rfq-requirements-v1.json`
- `fixtures/vx4800/kinetics/qualification/t1-t2-test-rig-v1.json`

## Controlled boundary

This work does not alter:

- 240 suspended elements
- S/M/L allocation of 66 / 144 / 30
- 2400 x 1500 x 150 mm canopy envelope
- approximately 2260 x 1330 mm rotating-carrier coordination envelope
- 24 mm rotating-carrier coordination thickness parameter
- vertical rotation axis
- 0.08 / 0.36 / 0.65 rpm minimum / nominal / maximum controlled speeds
- 14 fixed accent heads
- controlled cable-exit coordinates
- current fixed-side powered architecture
- current no-slip-ring boundary

The 24 mm carrier parameter is not permission to fit the bearing, brake, drive, lock, sensors and retention system inside a 24 mm axial stack. The real mechanism stack remains a controlled interface problem.

## Datum strategy

The interface package defines four functional references before manufacturing datums are frozen.

### KD-A fixed structure

The fixed kinetic structure is the future primary machining and reaction reference. Decorative skin, false ceiling, removable panels and electrical trays cannot become the datum or structural substitute.

### KD-B rotation axis

Only the vertical direction of the rotation axis is controlled at this stage. Its physical XY location and the physical feature that establishes it remain TBD until the bearing/support architecture and mechanical datum drawing are controlled. The composition/setout origin must not be silently promoted into a bearing, shaft, bore or bolt-circle datum. The P0 generator therefore labels KD-B textually and deliberately draws no axis crosshair or physical axis feature.

### KD-C index azimuth

A physical angular reference is required for service/index recovery. Reaching the index is not the same as engaging the mechanical service lock.

### KD-D carrier interface plane

A functional plane coordinates the axial mechanism stack. Its exact offset is TBD and must not be inferred from the existing 24 mm carrier coordination parameter.

## Mechanical interface modules

The CAD model should keep these as separate bodies, assemblies or clearly separable layers/components:

| Interface | Fixed side | Rotating side | Key boundary |
| --- | --- | --- | --- |
| Primary bearing | structural support and supplier-compliant mounting face | bearing ring and structural carrier/hub | only qualified primary support path |
| Positive drive | motor/reducer, sprocket/pinion, tensioning, guard | toothed belt ring or ring gear | not primary support, not service lock |
| Direct-carrier brake | spring-applied fixed-side caliper/equivalent and reaction bracket | passive annular brake ring/disc | holding/fault path must be able to bypass failed transmission where required |
| Service lock | positive fixed bracket and captive lock | dedicated receiver | access restraint independent of brake/motor/software |
| Secondary retention | multiple fixed catch sectors | distributed passive capture features | normally clear; relevant primary failures must not remove the same capture path |
| Primary feedback | fixed powered readhead | passive ring/scale/targets | measurement only, never structural restraint |
| Diverse feedback | fixed independent/diverse sensor if allocated | passive target set | only released risk assessment decides whether it is required |
| Balance/trim | inspection access | captive indexed trim stations | no cable-exit movement allowed |
| Service access | panels, guards, tools, extraction paths | no-contact swept/service envelope | normal service must not require uncontrolled carrier movement |

## Parameter ledger

Every load-, datum- or selection-dependent mechanical dimension remains explicitly unresolved. Examples include:

- physical rotation-axis XY datum/location
- bearing mounting diameter
- bearing support flatness
- bearing bolt circle and preload
- drive-ring pitch diameter
- belt/gear width
- belt pretension
- brake effective radius
- brake-ring thickness
- brake-caliper offset
- service-lock pin diameter
- service-lock engagement travel
- secondary-retention normal clearance
- secondary-retention abnormal engagement travel
- primary feedback air gap
- diverse feedback air gap
- trim-station capacity
- component extraction envelope

The machine-readable package stores each current value as `null`, status `tbd`, and names the evidence needed to close it. This prevents a coordination placeholder, centered visual origin or supplier suggestion from quietly becoming a fabrication dimension.

## Tolerance closures that must be solved

A final mechanism drawing cannot be released by dimensioning parts independently. At minimum, these closed loops must be calculated and physically verified:

1. Bearing mounting face: structure fabrication/machining + fastening distortion + bearing mounting requirement.
2. Drive alignment: bearing axis/runout + carrier ring fabrication + fixed drive position + tensioner adjustment.
3. Brake runout: bearing runout + carrier/brake-ring fabrication + brake bracket position.
4. Service-lock engagement: angular/index accuracy + receiver position + fixed bracket position + carrier runout/deflection + engagement travel.
5. Secondary-retention normal gap: bearing play/runout + carrier/fixed-catch fabrication + normal deflection + thermal effects.
6. Feedback air gap: bearing runout + target-ring concentricity + readhead bracket + carrier deflection.
7. Component extraction: frame + adjacent modules + guarding + tools + removal trajectory.

No numeric tolerance is assigned until the exact component requirements, structural model and prototype inspection evidence exist.

## Failure-state CAD models

Normal assembled geometry alone is insufficient. The design model must include explicit configurations or derived studies for:

- normal running condition
- drive transmission disconnected with direct-carrier holding path available
- brake applied
- service lock fully engaged and representative partial/misaligned engagement
- relevant primary-support separation
- secondary-retention engaged
- manual recovery with positive restraint and isolation
- feedback fault / alternate channel study where allocated

These are engineering states, not photoreal animation states. Their purpose is to expose interference, missing reaction paths, common-cause failures and inaccessible recovery operations before hardware is ordered.

## Calculation register

The calculation register contains thirteen controlled case families. All are currently blocked by missing evidence rather than populated with assumed values.

| ID | Case | Primary purpose |
| --- | --- | --- |
| KLC-001 | Static gravity / bearing load | bearing and fixed-support axial/radial/moment reactions |
| KLC-002 | Jerk-limited start | start torque and suspended-field transient correlation |
| KLC-003 | Nominal steady operation | continuous drive, thermal and field-offset baseline |
| KLC-004 | Maximum approved speed | maximum-speed load, thermal and dynamic-clearance evidence |
| KLC-005 | Controlled normal stop | stop torque, travel and settling/restart criteria |
| KLC-006 | Power-loss/fault stop | direct-carrier brake torque/energy and field excitation |
| KLC-007 | Safe overspeed validation | risk-controlled test point, detection and stop envelope |
| KLC-008 | Snag/abnormal drag | jam signature and detection timing |
| KLC-009 | Imbalance/trim | Mx/My and controlled trim strategy |
| KLC-010 | Transmission disconnect | proof of holding-path independence from belt/gear transmission |
| KLC-011 | Service-lock proof | positive access-restraint load and proof validation |
| KLC-012 | Primary-support failure / retention | abnormal catch load, travel and fixed-frame reactions |
| KLC-013 | Manual recovery | restrained manual-release/recovery reactions and sequence |

## Calculation methodology

### Mass and screening inertia

Once controlled masses exist, the rigid-body screening inertia about the vertical axis is:

`I_z = Σ(m_i r_i² + I_i,local) + I_carrier + I_rotating_drive_parts`

This is not the complete transient model. The suspended elements lag, oscillate and can exchange energy with the carrier during acceleration and braking. T1/T2 measurements are therefore required before final drive/brake transient demand is released, followed by later T3/T4 correlation.

### Static first moments / balance

`M_x = Σ(m_i x_i)`  
`M_y = Σ(m_i y_i)`

The correction strategy must use dedicated captive trim stations. Controlled cable exits are not balance-adjustment points.

### Drive torque framework

A future released drive calculation should resolve the terms in:

`T_required = reserve × (I_eq α + T_bearing + T_drag + T_imbalance + T_transmission/loss + T_other-approved)`

No numeric reserve factor, equivalent transient inertia, acceleration, drag torque or other term is assigned by this package.

The bearing/support calculation must separately consume belt pretension, tangential drive force, tensioner/idler reactions, brake reactions and any local mount stiffness/distortion effects. Those reactions do not disappear because the carrier rotates slowly.

### Braking

Static holding and dynamic stopping are separate duties. The selected brake application must provide exact manufacturer data for the proposed disc/ring interface, force/torque conversion, thermal energy, apply/release behavior, runout/alignment and manual release. A motor or gearbox brake is not credited as the only carrier holding path across a transmission-disconnect case unless an approved analysis explicitly demonstrates equivalent fault containment.

### Secondary retention

There is intentionally no generic drop factor in this package. The retention load case must begin from a released, physically meaningful failure mode and a defined engagement geometry. The calculation must identify what remains connected, the available engagement travel, distributed contact/reactions and the structural path into the fixed frame. Any failure mode not actually contained must remain disclosed.

## Evidence hierarchy and traceability

Every numeric input belongs to one of these explicit evidence classes:

- published manufacturer data
- engineering calculation
- prototype measurement
- controlled production measurement
- assumption
- design target

An assumption may be useful for sensitivity analysis, but its label must survive into the result. It cannot become a released product value merely because a calculation converges.

Issue dependencies remain unchanged:

- Issue #9 is expected to supply production S/M/L and replacement-variation mass evidence.
- Issue #7 is expected to supply suspension and dynamic-load evidence used by T1/T2 correlation.
- Issue #11 retains authority for the electrical/service safety-chain implementation and the final brake/control interfaces.

## CAD maturity progression

### P0: interface coordination

Implemented now:

- deterministic DXF generation from controlled repository sources
- controlled fixed-canopy and rotating-carrier coordination outlines
- all 240 controlled suspension-exit markers
- all 14 controlled fixed accent-head markers
- annotation-only mechanical interface callouts
- explicit TBD parameter/dependency callouts
- explicit warning that generated output is not manufacturing authority
- fail-closed rejection if a partially frozen interface parameter is mixed into the P0 workflow
- no inferred physical XY rotation-axis datum

The P0 DXF does **not** claim that physical mechanism geometry exists yet.

Permitted in the next richer P0/P1 CAD model once evidence exists:

- fixed and rotating assembly separation
- controlled physical datums
- dedicated conceptual bearing/drive/brake/lock/retention/sensor/trim zones
- service access and removal volumes
- normal and failure-state configurations
- parameter names with controlled supplier/evidence-backed values

Not permitted:

- fabricated bolt circles based on guesses
- arbitrary brake-ring radius/thickness
- arbitrary retention gap
- arbitrary sensor air gap
- an assumed bearing axis at the composition origin
- a visual service lock presented as structurally released

### P1: supplier-coordinated prototype model

Requires exact candidate mating CAD/drawings and controlled application data for bearing, transmission, brake and feedback, plus a preliminary structural concept. Tolerance stacks can then be calculated, but the package remains prototype-only.

### P2: build-release prototype drawing set

Requires the relevant interface/tolerance gates, structural calculations, released test-rig safety documents and prototype drawing review to close. It is still not serial-production release.

### Production release

Requires measured mass/CG and production variation, physical dynamics correlation, supplier calculations, released risk/safety-function allocation, T1-T4 evidence, endurance/acoustic evidence where required, service validation and independent calculation review.

## Release logic

The schemas are intentionally fail-closed:

- `finalInterfaceControlReleased=true` requires released datums, released non-null interface parameters, released tolerance closures and every interface release gate true.
- `finalCalculationPackageReleased=true` requires every load case to be `verified`, every output to have a non-null verified value, and every calculation release gate true.

Changing only a top-level release flag cannot convert an unfinished package into released engineering.

## Immediate execution sequence

1. Keep supplier RFQs moving without allowing a supplier recommendation to become a selection.
2. Obtain controlled S/M/L assembly mass and variation evidence from Issues #7/#9.
3. Populate exact candidate mating requirements for bearing, positive drive, brake and fixed-side feedback.
4. Resolve the physical rotation-axis datum, then replace P0 annotation-only mechanism callouts with supplier/evidence-backed parametric interface geometry without changing the controlled setout.
5. Complete T1 rig structural/test-risk release after its measured mass envelope is known.
6. Run T1 and use measured lag/damping/start-stop data to constrain motion profiles.
7. Build/run the schedule-derived T2 cluster and establish interaction, snag and dynamic-clearance evidence.
8. Use those results to calculate and package the full-carrier P1/P2 mechanism for T3/T4 qualification.

No final bearing, drive, brake, sensor, structural section, fastener, torque, safety integrity level, performance level, acoustic criterion or maintenance interval is selected by this document.
