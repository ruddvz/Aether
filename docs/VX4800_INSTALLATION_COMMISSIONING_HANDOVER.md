# VX4800 Installation, Commissioning and Handover Framework

## Purpose

This document defines the site process required to move AETHERIA VORTEX VX4800-BF-01 from a factory-released build to an accepted installed fixture.

It is a qualification and commissioning framework. It is not evidence that any named installation has passed.

Factory acceptance, repository validation, coordination CAD, Blender visualization and a successful pre-hang do not constitute site acceptance.

## Authority boundary

The installation team must work from the released manufacturing, structural, electrical, kinetic and project-specific installation authorities.

Repository-generated STEP/DXF/GLB remain coordination-only. Blender remains visualization-only. False-ceiling framing and decorative canopy skin are not primary support.

Any site condition that conflicts with released authority must be recorded and dispositioned through engineering change control. Field improvisation does not become authority merely because the fixture can be made to fit.

## 1. Site receipt

Before installation begins:

- verify project, fixture serial and build configuration identity;
- verify package count and dispatch documentation;
- inspect transport restraints and packaging condition;
- inspect visible finishes, butterfly assemblies and safety-critical hardware;
- inspect microcables for kink, abrasion or uncontrolled tangling;
- quarantine damaged or unidentified parts;
- create an NCR for any condition that can affect released requirements.

Receipt acceptance only confirms the delivered condition. It does not accept structural, electrical or kinetic installation.

## 2. Site readiness and exclusion control

Before lifting or permanent load transfer:

- confirm the approved project structural design and interface information are available;
- confirm the actual supporting building structure is identifiable and consistent with the approved basis;
- confirm access, lifting equipment, temporary works and exclusion zones;
- identify nearby services, ceiling systems and architectural obstructions;
- confirm the installation method and temporary restraint sequence;
- confirm that no false-ceiling grid or decorative panel is being treated as structural support.

If the as-built structure differs materially from the approved basis, stop permanent installation until the structural engineer dispositions the difference.

## 3. Structural installation

Permanent support must follow the named-project structural release.

Record, where applicable:

- support/anchor/connection identity;
- installed location and interface zone;
- substrate/as-built verification;
- installation values such as torque, tightening sequence, embedment, weld inspection or other controlled characteristics when specified by the structural design;
- leveling/shimming configuration and limits;
- secondary-retention structural termination;
- inspection sign-off before inaccessible work is closed.

Do not assume equal reaction sharing among the eight interface zones. Do not substitute anchors or support steel using catalog similarity alone.

## 4. Fixture assembly

Maintain the production build identity through unpacking and assembly.

Verify:

- exact 240-element identity and S66/M144/L30 allocation;
- each controlled suspension line identity and released length/termination;
- butterfly attachment/orientation and required lower-yoke arrangement;
- canopy fixed/rotating separation;
- 14 fixed accent-head positions;
- safety-critical fasteners, locking features and secondary retention;
- no shipping restraint remains in an operating path;
- inaccessible inspections are completed before decorative closure.

Any field drilling, cutting, grinding, rewiring or reworking of a safety-critical part requires engineering approval before execution.

## 5. Electrical and lighting commissioning

Before energization:

- verify project/market supply configuration;
- verify isolation and protection;
- verify protective earthing/bonding against the released architecture;
- verify wiring, connectors and control gear identities;
- verify all 14 fixed heads and exact released optic/CCT configuration;
- verify segregation from the rotating field.

Commission the released control architecture and record:

- control-gear identities;
- DALI addresses or equivalent released addressing;
- groups/scenes and commissioning configuration;
- head operation and dimming behavior;
- required post-install electrical safety checks;
- any approved deviations.

The conceptual optical roles must not be converted into uncontrolled hardwired substitutions. A different head, optic, driver or control gear requires evidence-impact review.

## 6. Kinetic commissioning

Kinetic commissioning must use the released kinetic engineering package from the dedicated rotating-carrier track.

Before first powered motion:

- verify mechanical service lock and its clear locked/unlocked indication;
- verify brake/holding system;
- verify independent secondary retention;
- verify position/speed feedback and passive targets where applicable;
- verify the motion path is free of temporary works, packaging, people and obstructions;
- establish an exclusion zone.

Commission progressively:

1. service/jog condition;
2. released low-speed condition;
3. released nominal condition;
4. other released operating conditions only after preceding checks pass.

Verify, as applicable:

- direction;
- minimum/nominal/maximum released speed limits;
- soft start and controlled acceleration;
- normal controlled stop;
- fault stop;
- power-loss behavior;
- safe restart behavior;
- abnormal torque/jam detection response;
- actual feedback agreement;
- unacceptable noise or vibration;
- cable and butterfly behavior.

Do not widen a software speed, position or clearance limit to make a physical interference disappear. A physical interference is an engineering nonconformance.

## 7. Site dynamic clearance

The factory pre-hang is necessary but not sufficient because the real architecture and services exist only on site.

Site trials must confirm no unacceptable contact between:

- butterfly and butterfly;
- butterfly and cable;
- cable and cable;
- rotating field and fixed heads;
- rotating field and canopy;
- rotating hardware and fixed services;
- fixture and surrounding architecture.

Commissioning records must identify the conditions under which clearance was checked. Blender animation and static geometry review cannot close this physical requirement.

## 8. Deviations and failed tests

Maintain a site deviation/NCR register.

For any failed or out-of-tolerance commissioning result:

1. preserve the original failure record;
2. identify affected requirements and evidence;
3. obtain the required engineering disposition;
4. perform approved rework/repair/change only;
5. re-test the affected condition;
6. close the deviation only after the acceptance evidence is controlled.

No undocumented site fix is acceptable for a controlled structural, suspension, kinetic, electrical or safety requirement.

## 9. Handover baseline

The final handover package should establish the as-installed service baseline, including:

- fixture serial and build configuration;
- project/site identity;
- final structural approval reference;
- installed controlled component identities;
- approved site deviations;
- final inspection record;
- lighting commissioning record;
- kinetic commissioning record;
- motion configuration/limits and baseline observations;
- photographic condition record;
- installation and operation instructions;
- service, inspection and replacement instructions;
- spare-part identities;
- isolation/lockout and mechanical service-lock procedure;
- emergency/fault response instructions appropriate to the released system;
- responsible owner/operator/service contacts;
- first planned inspection date.

Changes made after handover must be assessed against this baseline rather than treated as an untracked maintenance choice.

## 10. Service demonstration

Before handover, authorized service personnel should be shown how to:

- isolate lighting and kinetic electrical domains independently where released;
- engage and verify the mechanical service lock;
- access serviceable heads/control gear;
- inspect suspension and visible safety-critical retention;
- identify fault/deviation conditions that require engineering escalation;
- restore the product to its released configuration after service.

This demonstration is not a substitute for the written service package.

## 11. Site acceptance gate

Installation/commissioning release remains false until every required promotion gate in `fixtures/vx4800/installation/commissioning-plan-v1.json` is supported by controlled evidence.

A green GitHub workflow proves only that the digital rules remain internally consistent. It does not prove a site installation has passed.
