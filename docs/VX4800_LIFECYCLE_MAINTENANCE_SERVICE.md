# VX4800 Lifecycle Maintenance and Service Framework

## Purpose

This document defines how an installed AETHERIA VORTEX VX4800-BF-01 should be inspected, serviced, repaired and returned to operation without losing the controlled as-installed baseline.

It is a qualification framework, not a released maintenance manual. Exact intervals, lubricants, replacement lives and component-specific service instructions remain unresolved until final hardware, qualification testing and commissioned duty-cycle evidence exist.

## 1. Service baseline

The handover/commissioning record becomes the historical service baseline. It should include the fixture serial/build configuration, installed controlled component identities, project/site identity, approved deviations, structural approval, lighting and kinetic commissioning records, motion limits, condition photographs and first inspection due date.

Later service records must update the as-maintained state without overwriting the original commissioned state or prior failures.

## 2. Periodic inspection domains

Periodic inspection should address at least:

- structural interfaces and secondary-retention termination;
- suspension cables, grippers, terminals, lower bridles/yokes and visible attachment condition;
- butterfly assemblies and material-tier-specific damage modes;
- bearing/drive/brake/service-lock/secondary-retention/feedback/balance items from the released kinetic architecture;
- electrical isolation, protection, bonding, wiring, control gear and the 14 fixed heads;
- finishes, service access and any new architectural interference.

Exact inspection intervals are not defined by this document.

## 3. How intervals are eventually released

Initial intervals should be based on:

1. exact selected component manufacturer maintenance requirements;
2. qualification and first-article test evidence;
3. the commissioned operating duty cycle and environment;
4. regulatory/certification obligations where applicable;
5. engineering judgment for the complete product architecture.

Field history may justify shortening an interval. Extending a released interval requires engineering review and controlled evidence.

Do not invent generic annual bearing lubrication, cable replacement or brake replacement requirements before the final components and evidence exist.

## 4. Event-triggered inspection

Inspection is also required after events capable of changing a verified condition, including:

- abnormal/fault/emergency stop or unexplained high-torque event;
- physical contact, snag or interference;
- building/support modification or significant structural event;
- water ingress/contamination;
- discovery of an unauthorized part, setting or field modification;
- major service to safety-critical structural, suspension, kinetic or electrical items.

The event record should identify what happened, affected evidence, inspection scope, disposition and return-to-service verification.

## 5. Safety-critical maintenance

Safety-critical work requires a released procedure and authorized personnel.

Where applicable:

- isolate the relevant electrical domain;
- engage and verify the mechanical service lock before work on or near the rotating field;
- maintain independent secondary-retention integrity;
- record removed and installed part identities;
- follow controlled fastening/locking requirements;
- use only released lubricant type/quantity and method for selected kinetic hardware;
- preserve fault/failure evidence before repair;
- record deviations and engineering approvals.

The motor brake or software stop alone is not a mechanical service lock.

## 6. Spares and replacements

A critical-spares list must eventually be released. Safety-critical spare parts require exact qualified identity unless an engineering change formally approves an alternative.

Part fit is not sufficient evidence of equivalence.

Specific replacement reviews include:

- butterfly replacement: material tier, dimensions, appearance and mass/balance effect;
- suspension replacement: exact cable/gripper/terminal/yoke configuration and qualification coverage;
- kinetic replacement: bearing/drive/brake/feedback/retention configuration and qualification impact;
- lighting replacement: electrical, thermal, photometric, CCT/CRI/optic and control compatibility;
- structural fastener/support replacement: project structural authority;
- obsolete components: formal engineering substitution and evidence-impact review.

Spare quantities are deliberately not frozen by this document. They should be set once production/service strategy, lead time, matching requirements and field risk are known.

## 7. Cleaning and cosmetic service

Cleaning instructions must be compatible with the released butterfly material tier and visible finishes.

Do not use uncontrolled chemicals, abrasives or polishing methods on optical glass/PMMA, PVD/coated finishes or other sensitive surfaces.

Cosmetic work must not obscure cracks, wear, corrosion, fastener movement or other inspection evidence.

## 8. Post-service verification

Before return to service, verify the domains affected by the work.

At minimum:

- configuration: part identities, revision/change records and deviations;
- mechanical: fastening, locking, suspension, retention, alignment and service lock;
- electrical: isolation/bonding/wiring/function/safety checks after electrical work;
- kinetic: affected feedback, low-speed motion, normal motion and stop behavior when motion can be affected;
- clearance: where mass, line length, geometry or alignment changed;
- lighting: exact head/control-gear identity, addressing/groups/scenes and function where changed;
- baseline: update the as-maintained configuration and history without erasing prior evidence.

Visual operation alone is not sufficient return-to-service evidence for safety-critical work.

## 9. Fault and service history

Maintain a persistent record of:

- inspection history;
- service work orders;
- fault/events and diagnostic findings;
- replacement-part identities;
- configuration changes;
- deviations/NCRs and re-test;
- recurring-fault trends;
- safety-related field issues and evidence-impact reviews.

Repeated faults should trigger engineering review rather than repeated reset/replacement without root-cause analysis.

## 10. Obsolescence

Long-life architectural products will outlive some electronic and mechanical components.

Obsolescence must be managed through controlled substitution, not informal procurement. The review should consider physical fit, structural/mechanical ratings, electrical/thermal behavior, photometry, control interoperability, mass/balance, service access, certification and existing qualification coverage as applicable.

## 11. Return-to-service gate

A serviced fixture may return to normal operation only when the affected verification is complete, deviations are controlled and no open safety-critical condition remains.

The final lifecycle/service release gate remains false until `fixtures/vx4800/service/lifecycle-plan-v1.json` is promoted with controlled intervals, procedures, spares, history systems and return-to-service requirements based on the final product configuration.

GitHub CI validates this framework only. It cannot prove that an inspection, repair or physical verification occurred.
