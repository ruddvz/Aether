# VX4800 Structural and Site-Interface Framework

Product: AETHERIA VORTEX  
Model: VX4800-BF-01  
Design revision: 1.3.0  
Framework revision: 1.0.0  
Status: qualification plan; no structural construction release

## 1. Purpose

This document defines the structural boundary between the VX4800 product and a real building project.

It does not calculate or publish anchor loads. Those loads are deliberately withheld until the fixture has controlled physical mass properties, the rotating-mechanism track releases kinetic reaction cases, the manufacturing interface geometry is available, and the actual site structure is known.

The machine-readable authority for this framework is:

`fixtures/vx4800/structural/interface-brief-v1.json`

## 2. Controlled product boundary

The current controlled fixture defines:

- canopy envelope: 2400 x 1500 x 150 mm;
- eight engineered structural interface zones;
- primary support: site structure via engineered interface zones;
- site structural design required;
- actual product mass: unknown;
- repository-generated geometry: coordination-only.

The eight interface zones are a design/interface count. They are not eight identical support reactions and they do not imply equal 1/8 load sharing.

Final interface coordinates and connection geometry must come from released manufacturing authority, not from lightweight coordination geometry.

## 3. Valid support path

The intended primary structural path is:

building structure / purpose-designed support steel
→ project-specific interface/anchors/connections
→ fixed VX4800 structural canopy frame
→ bearing/rotating-carrier load path
→ suspension system
→ butterfly field.

A valid fixed structural path must also exist for the released secondary-retention architecture.

The following are not accepted as structural support merely because they are physically nearby:

- false-ceiling grid or framing;
- decorative canopy skin;
- electrical conduit, cable tray or other MEP supports;
- access panels;
- architectural finishes.

If any such system is intentionally used structurally, it must itself be specifically engineered, documented and approved for the released load path. The default is that it is nonstructural.

## 4. Why reactions are currently not published

Several governing inputs are still unknown:

- complete installed mass;
- complete rotating mass;
- fixture and rotating-assembly centre of gravity;
- normal acceleration/deceleration reactions;
- controlled stopping reactions;
- fault/abnormal stopping reactions;
- approved residual imbalance;
- secondary-retention engagement load case;
- installation/service temporary loads.

These cannot be substituted with decorative-material density, Blender mass, bounding-box volume, nominal rpm or a generic dynamic factor.

The rotating-mechanism engineering track owns the motion/mechanical load architecture. The structural framework consumes its released reactions; it does not pre-empt that work.

## 5. Site inputs required

A project structural engineer cannot approve the interface without actual site information.

Required project inputs include:

- project location and governing structural/design criteria;
- actual supporting structural system and substrate;
- structural drawings;
- member/reinforcement geometry relevant to the support;
- material strengths/grades as required by the design method;
- as-built survey/verification where existing structure is involved;
- ceiling void, finishes and service obstructions for coordination;
- anchor edge distances, member boundaries and reinforcement/member details;
- installation access and tolerances.

Anchor selection is downstream of these inputs, not upstream.

## 6. Required structural load cases

The final project analysis must establish applicable combinations using the governing project design basis. The product-side structural brief identifies at least these product cases for engineering review:

- complete dead load;
- normal kinetic operation;
- controlled normal stop;
- structurally relevant fault/abnormal stop;
- released residual imbalance / production mass variation;
- secondary-retention engagement/failure scenario;
- service/maintenance condition;
- installation/hoisting/temporary restraint condition.

This list identifies cases that must be resolved. It does not prescribe code load factors or combinations. Those belong to the named project, jurisdiction and engineer-approved design basis.

## 7. Interface reaction schedule

When inputs are controlled, the structural analysis must publish a reaction schedule for every released interface zone and governing load combination.

The schedule should use an explicitly defined product/project coordinate system and provide, as applicable:

- Fx;
- Fy;
- Fz;
- Mx;
- My;
- Mz.

Units are N and N-m in the machine-readable structural interface model.

No numeric reaction in the repository should be treated as released unless it is linked to:

1. a controlled product configuration;
2. controlled mass/CoG data;
3. the released kinetic load-case input;
4. the actual structural model;
5. the named project/site condition;
6. engineer approval.

## 8. Load distribution among eight interfaces

Equal division by eight is forbidden unless a structural model demonstrates that behavior for the governing case.

Real reaction distribution can change due to:

- structural-frame stiffness;
- support stiffness;
- connection slip/clearance;
- interface tolerances;
- eccentric centre of gravity;
- torsional kinetic reactions;
- local leveling/shimming;
- secondary-retention geometry;
- installation sequence.

The final design must use the actual stiffness/load-path model appropriate to the released construction.

## 9. Fixed canopy structural frame

The fixed canopy structural system must be checked independently of the decorative skin.

The final calculation should address, where applicable:

- strength of structural members;
- local bearing/connection stresses;
- frame torsion;
- global and local deflection;
- bearing-support stiffness/alignment;
- drive/alignment sensitivity;
- service-panel/interface clearances affected by deformation;
- fastener/connection behavior;
- fatigue or repeated-load effects identified by the kinetic risk/load analysis;
- secondary-retention attachment loads.

Deflection acceptance criteria should be tied to actual functional and architectural requirements rather than an arbitrary generic span ratio.

## 10. Building structure and support system

The project structural engineer must verify the actual supporting structure.

The calculation may need to address:

- local concrete/reinforcement behavior;
- steel member strength/stability/local effects;
- purpose-designed support framing;
- timber/other substrate if relevant;
- connection group behavior;
- edge distances and member boundaries;
- eccentricity/prying where relevant;
- welds/bolts/anchors/support plates;
- existing-condition capacity and uncertainty;
- load transfer beyond the immediate support to the building structure.

No universal anchor model is selected by this repository because the actual substrate and reactions are not yet controlled.

## 11. Primary versus secondary retention

Primary support and secondary retention must be represented as distinct load paths when the released kinetic architecture requires independent retention.

The structural package must show:

- normal non-engaged/engaged condition as applicable;
- fixed structural termination;
- credible engagement/failure load case;
- local attachment verification;
- load transfer into the site structure;
- inspection/access;
- effect on surrounding structure;
- proof-test/qualification evidence required by the released retention design.

A secondary tether connected back into the failed primary component does not constitute an independent structural path.

## 12. Installation and service conditions

Installation can create loads different from normal operation.

The released installation method must identify, where applicable:

- hoisting/lifting points;
- temporary supports;
- carrier restraint;
- service lock usage;
- temporary eccentric conditions before the full 240-element field is installed;
- leveling/shimming sequence;
- required tightening/torque sequence;
- prohibition on loading the false ceiling;
- verification of final alignment and interface engagement.

The structural engineer must review temporary conditions that are significant compared with the permanent design cases.

## 13. Tolerances and alignment

The project structural/interface drawing must define enough tolerance information to avoid unintended load redistribution or mechanical misalignment.

Coordinate with the kinetic engineering requirements for:

- bearing alignment;
- carrier clearance;
- drive alignment;
- service lock engagement;
- secondary retention clearance;
- canopy level;
- interface flatness;
- anchor/support positional tolerance.

Do not solve an alignment problem in the field by uncontrolled shimming or forcing the canopy into position.

## 14. Evidence chain

Structural approval must be traceable through the certification/first-article evidence framework.

Expected evidence includes:

- physical product mass records;
- rotating mass/CoG record;
- kinetic reaction/load-case input record;
- released manufacturing interface geometry;
- site structural drawings/survey;
- design-criteria record;
- structural calculation/model report;
- reaction schedule;
- anchor/support calculation;
- secondary-retention structural verification;
- installation/detail drawing;
- project structural approval.

The release evidence index introduced by the compliance framework should be used to register controlled evidence as it becomes available.

## 15. Change control

Structural impact review is required when a change affects, or may affect:

- total installed mass;
- rotating mass/CoG;
- butterfly material tier or count/allocation;
- suspension system;
- carrier/bearing/drive/braking behavior;
- secondary retention;
- structural canopy frame;
- interface geometry/count;
- site structure/support steel;
- anchor/connection system;
- operating/fault load cases;
- installation method.

A structural release for one building/project is not automatically transferable to another building.

## 16. Current decision

No interface reactions, anchors, support steel or project structural approval are currently released.

All structural promotion gates in `fixtures/vx4800/structural/interface-brief-v1.json` remain false.

That is the correct state until the physical and project-specific inputs exist.
