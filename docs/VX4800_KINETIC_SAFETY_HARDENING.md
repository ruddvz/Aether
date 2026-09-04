# VX4800 kinetic safety hardening review

Date: 2026-09-04

Product: AETHERIA VORTEX  
Model: VX4800-BF-01  
Design revision: 1.3.0  
Hardening review: 1.0.0

Status: engineering-development input, not construction release.

This document records an adversarial review of the rotating-carrier architecture after the first machine-readable kinetic package was built. The purpose is to find the ways the first architecture could still fail despite looking internally coherent.

It does not replace physical testing, a released risk assessment, structural calculation, supplier application review or certification work.

## 1. What the first architecture got right

The first slice established several boundaries that remain correct:

- keep the 240-element engineering composition and cable-exit coordinates unchanged;
- keep the 14 accent heads fixed;
- keep powered kinetic equipment on the fixed side where practical;
- do not introduce a slip ring while the rotor has no electrical loads;
- separate primary structural load, drive torque, braking, service lock and secondary retention;
- require a positive mechanical service lock;
- require independent secondary retention;
- prohibit automatic restart after power restoration;
- do not select final bearing, motor, brake or torque ratings from assumed butterfly masses;
- make full physical pre-hang and dynamic testing mandatory.

Those decisions survive this review.

## 2. Critical correction: holding path must survive drive-transmission failure

The largest weakness in the first architecture was the braking path.

A brake on the motor or gearbox can be useful, but if the carrier is driven through a belt, toothed ring, pinion or coupling, the brake may depend on the same transmission that can fail. A broken belt or disconnected transmission could therefore remove both propulsion and the through-drive holding path.

The preferred architecture study is now:

1. motor/gearbox and drive transmission for controlled propulsion and normal deceleration;
2. fixed-side spring-applied brake acting directly on a passive brake ring/disc attached to the rotating carrier, or another demonstrably independent carrier holding architecture;
3. positive mechanical service lock for access.

These three functions must not be casually collapsed into one component.

The direct-carrier brake remains a study, not a selected product. Its diameter, torque, number of calipers, friction material, switching behaviour, wear, noise and thermal duty remain unknown until the real mechanical load cases exist.

Current manufacturer references show that this architecture is industrially credible without selecting a VX4800 part:

- mayr `ROBA-diskstop` is an electromagnetic safety caliper-brake family for brake discs and is presented by the manufacturer for applications including elevator and stage/event technology: https://www.mayr.com/en/products/safety-brakes/elevator-and-stage-brakes/roba-diskstop~486
- RINGSPANN publishes spring-activated, electromagnetically released industrial disc-brake calipers in its FEM families: https://www.ringspann.com/en/products/brakes/electrical-brake-calipers/spring-activated-electromagnetically-released/ev-024-fem

These pages prove only that relevant component families exist. They do not provide the VX4800 brake rating.

## 3. Secondary retention needs a common-cause analysis

A normally-clear annular catch is still the preferred broad concept because it allows continuous rotation without winding a fixed tether.

However, calling the catch “independent” is not enough.

If the rotating capture flange is attached only to the same local hub, bearing bolts or carrier feature that fails, the secondary path can disappear with the primary path.

The refined direction is:

- multiple fixed catch sectors;
- multiple distributed rotating capture attachments;
- attachment into carrier structural regions that bypass relevant primary-bearing rings/fasteners;
- explicit coverage of bearing internal failure, bearing-fastener failure and local hub failure;
- explicit list of structural failures that the secondary system cannot reasonably contain and must therefore be prevented by primary design.

A full-carrier fracture cannot be waved away by adding a cable near the bearing. The retention design must state its actual failure coverage.

## 4. Feedback needs common-mode thinking

A single perfect encoder does not exist.

If one feedback device is used for closed-loop speed control, stall detection and overspeed detection, a plausible frozen or corrupted signal can defeat all three functions together.

The architecture therefore requires evaluation of a sufficiently independent or diverse speed-plausibility channel where the final risk assessment requires it.

The no-slip-ring boundary remains intact. The preferred pattern is still powered fixed-side sensors reading passive rotating rings, targets or coded markers.

The exact sensor count, resolution and fault-detection latency must come from the released risk assessment and physical motion tests.

## 5. Brake failures must be separated

Two faults need different behaviour:

### Brake fails to release

Expected evidence may include:

- brake-state feedback where the selected product supports it;
- drive load rises but carrier does not move;
- time-to-move expires;
- start is aborted without indefinitely increasing drive torque.

### Brake fails to apply or loses holding force

The system must not infer safety from an “apply brake” command.

Required principles:

- verify actual zero speed;
- do not permit mechanical access;
- engage the mechanical service lock only after zero speed is independently established;
- treat manual recovery as a stored-motion hazard.

## 6. Manual release must never create freewheel

A manual brake release, gearbox release or disengaged transmission can allow motion from imbalance, suspended-field restoring forces or external disturbance.

The required sequence principle is:

1. verify zero speed;
2. engage and directly verify the positive service lock;
3. apply kinetic lockout/tagout;
4. only then use a controlled manual release if a released recovery procedure requires it;
5. restore the normal holding path before removing the service lock.

If a failed system cannot reach a service-lock index under controlled powered motion, the project needs an engineered recovery method. A technician must not improvise by pulling or forcing the 240-element carrier.

## 7. Motion profile should control jerk, not only acceleration

“Soft start” is too vague for a field of long pendulums.

A low peak acceleration can still create unnecessary excitation if acceleration changes abruptly.

The preferred control study is therefore a jerk-limited S-curve or a physically equivalent smooth motion profile.

The repository intentionally does not define numeric acceleration, jerk or settling dwell yet. T1 through T4 tests must produce that evidence.

Reversal remains unapproved. If later allowed, it must use verified zero speed plus test-derived settling before motion in the opposite direction.

## 8. Rigid-body inertia is not the whole suspended-field model

The existing mass-map equation is useful:

`I_z = sum(m_i * r_i^2 + I_i,local) + I_carrier + I_rotating_drive_parts`

But the 240 butterflies are not rigidly attached masses during transients. They lag the carrier on long suspension lines.

The rigid-body result must therefore be treated as a screening/calculation input, not final proof of start or braking torque.

The selected drive and brake calculations must be correlated against physical carrier torque/load, cable-angle and lag measurements.

## 9. Bearing installation is part of bearing engineering

A good catalog bearing can perform badly on a distorted support ring.

Current manufacturer guidance reinforces this. Kaydon notes that slewing-bearing performance depends strongly on mounting-surface flatness, structural rigidity, fastener preload and mounting distortion. Out-of-flat mounting can increase frictional torque and reduce life. See: https://www.kaydonbearings.com/white_papers_11.htm

The bearing qualification therefore now needs explicit evidence for:

- support-ring rigidity and flatness against the exact supplier requirement;
- circumferential support requirements;
- bolt quantity/grade only from the exact bearing application;
- controlled preload/installation method;
- post-install running torque;
- runout;
- lubrication and containment;
- service access;
- drive-belt/gear reactions included in structural/bearing loads.

Do not copy generic bolt grades or flatness numbers from a white paper into the product release.

## 10. Drive tension is a structural load

A synchronous belt may remain the preferred propulsion study, but belt pretension is not free.

The design calculation must include:

- belt pretension;
- tangential drive force;
- tensioner/idler reaction;
- local motor/tensioner mount stiffness;
- potential bearing-support distortion;
- belt loss/tooth-skip failure cases;
- guarding and service access.

A belt can reduce open-gear lubrication/noise concerns, but only if the complete installed transmission behaves well at ultra-low carrier speed.

## 11. Service and commissioning UX is mechanical safety engineering

The repository now separates these states:

- `SERVICE_LOCKED`;
- `ISOLATED_UNLOCKED`;
- `ENERGISED_HELD`;
- `RUN_READY`;
- `RUNNING`;
- `STOPPING`;
- `JOG_READY`;
- `JOGGING`;
- `FAULT_STOPPING`;
- `FAULT_HELD`;
- `RETENTION_ENGAGED`;
- `MANUAL_RECOVERY_LOCKED`.

The important UX rule is simple:

**Stopped is not the same as mechanically locked.**

Future control/service UI must not show a software-held zero-speed state as “safe to access”. Mechanical access is tied to a positively engaged service lock plus the released LOTO procedure.

Other requirements include:

- direct physical lock indication;
- no colour-only safety meaning;
- fault reset never causes motion;
- jog mode clearly identified as restricted commissioning motion;
- reaching a service index does not mean the lock is engaged;
- secondary-retention contact creates an out-of-service state that ordinary reset cannot clear;
- power restoration never resumes the previous motion command.

The state model is in:

`fixtures/vx4800/kinetics/commissioning-state-model-v1.json`

## 12. Test evidence now has a contract

The previous T1-T4 programme was directionally correct but too easy to interpret as a checklist.

The repository now defines individual test cases and a physical test-record schema.

Key new cases include:

- single-element pendulum period/damping and jerk response;
- representative air-drag/HVAC sensitivity;
- mixed cluster local clearance;
- controlled snag/abnormal-drag response;
- bearing mounting/runout/running-torque validation;
- transmission-disconnect test proving the carrier holding path survives transmission loss;
- primary feedback loss/frozen/plausibility fault tests;
- service-lock partial-engagement and proof tests;
- representative secondary-retention engagement;
- manual recovery with representative imbalance;
- full 240-element minimum/nominal/maximum operation;
- full-field power-loss and fault-stop cases;
- all seven dynamic-clearance categories;
- full-field balance and replacement-element re-trim;
- acoustic/vibration/thermal baseline;
- endurance duty plus teardown inspection;
- complete service-index/LOTO/lock/replacement/recommission workflow.

The physical evidence schema does not allow a test record to claim `passed` while acceptance criteria remain uncontrolled.

Files:

- `fixtures/vx4800/kinetics/qualification/dynamic-test-plan-v1.json`
- `schemas/aether-kinetic-test-plan.schema.json`
- `schemas/aether-kinetic-test-record.schema.json`

## 13. Acoustic acceptance remains open

“Quiet” is a product objective, not an engineering acceptance criterion.

Before release, define:

- measurement positions;
- room/background conditions;
- operating states;
- frequency/spectral information if useful for gear/belt/bearing tones;
- acceptable product/project limit.

No dB(A) value is being invented at this stage.

## 14. Endurance needs a duty spectrum

Slow rotational speed does not automatically mean low wear.

Different components accumulate different duty:

- bearing revolutions;
- motor/reducer operating hours;
- belt tooth cycles;
- starts/stops;
- fault/parking brake applications;
- service-lock cycles;
- jog cycles;
- sensor drift/contamination exposure;
- fastener and trim inspection intervals.

The endurance programme must define these from intended use and follow with teardown/inspection. Maintenance intervals then come from exact manufacturer requirements plus test evidence.

## 15. Integration with the broader release framework

The current `main` branch now includes the VX4800 certification/first-article release framework. It already has open evidence items for kinetic mechanism qualification, dynamic clearance and full pre-hang.

This hardening slice makes those broad release items more executable. It does not close them.

Issue dependencies remain:

- Issue #7: dynamic suspension/load evidence;
- Issue #9: physical S/M/L assembly masses and production variation;
- Issue #11: kinetic electrical safety-chain, isolation and implementation evidence.

## 16. Promotion gates added by the hardening review

The following remain false:

- `faultContainmentMatrixApproved`;
- `directCarrierHoldingPathResolved`;
- `transmissionFailureContainmentValidated`;
- `independentOverspeedMonitoringResolved`;
- `brakeStateMonitoringResolved`;
- `manualReleaseRecoveryValidated`;
- `serviceStateModelValidated`;
- `restartSettlingLogicValidated`;
- `suspendedFieldDynamicModelCorrelated`;
- `bearingMountingJointValidated`;
- `acousticAcceptanceControlled`;
- `enduranceDutyControlled`;
- `configurationChangeImpactMatrixReleased`.

Repository tests additionally prevent a future `finalSystemApproved` state from being treated as sufficient while the hardening package, service state model or staged physical-test gates remain open.

## 17. Explicit non-claims

This review does not claim:

- a final brake architecture or part number;
- a final bearing;
- a final drive;
- a final stop category, SIL or PL;
- a final number of sensors;
- a final emergency-stop distance/time;
- a final acoustic limit;
- a final endurance cycle count;
- a final secondary-retention rating;
- certification;
- occupied-space construction release.

The goal of this slice is stronger failure independence, clearer technician interaction and testable evidence, not more machinery for its own sake.
