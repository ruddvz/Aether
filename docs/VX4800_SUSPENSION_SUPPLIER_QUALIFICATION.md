# VX4800 suspension supplier qualification

Date: 2026-09-04

Status: RFQ / engineering qualification input, not construction release.

This document converts the current visual microcable concept into a controlled hardware-qualification workflow. It does not select the final suspension system and it does not establish the final kinetic design load.

## Controlled starting point

The current VX4800 engineering fixture defines:

- 240 suspended elements;
- 240 main suspension lines;
- current visual cable target: 0.8 to 1.0 mm nominal diameter;
- AISI 316 stainless microcable as the preferred material direction;
- shortest controlled line: 318.676 mm;
- longest controlled line: 4705.401 mm;
- actual installed element mass: unknown;
- final kinetic design load: unknown;
- independent secondary retention: required but unresolved.

The 0.8 to 1.0 mm diameter is therefore a design target, not a released engineering specification.

## Preferred system architecture

The current preferred architecture is deliberately split into three functions.

### 1. Upper carrier interface

Use a supplier-rated adjustable gripper positively retained to the rotating carrier. The exact thread, fork, clevis or captive detail must be selected together with the carrier design.

Requirements include:

- compatible with the selected cable diameter and construction;
- no unprotected release plunger that can be operated accidentally in service;
- suitable for the actual cable exit angle;
- individually serviceable from the canopy;
- compatible with production adjustment and factory pre-hang;
- traceable manufacturer part number and working-load documentation.

### 2. Main suspension line

Use the cable construction explicitly approved by the selected gripper manufacturer, preferably stainless 7x7 in the current 0.81 to 1.0 mm visual range if the calculated design load allows it.

Do not substitute cable from another source merely because nominal diameter matches. Gripper performance depends on cable construction, material and tensile class.

### 3. Lower anti-rotation bridle / yoke

The lower attachment is product-specific and remains custom engineering.

The current visual concept uses one main line transitioning to three fine leads per butterfly. This can provide orientation control and a cleaner attachment than a single point, but it is not yet an engineered detail.

The final lower assembly must resolve:

- attachment locations in the final butterfly geometry;
- local glass/crystal stress concentration;
- junction/yoke geometry;
- lead material and diameter;
- terminal/crimp/sleeve design;
- bend radius;
- proof load;
- fatigue;
- replaceability;
- anti-rotation effectiveness;
- interaction with kinetic motion.

Blender's three lead splines are visualization reference only.

## Supplier finalist A: Reutlinger Type 12

Role: compact-system reference finalist.

Current manufacturer data for Cable Holder Type 12 publishes compatibility with 0.63, 0.81, 1.0 and 1.2 mm cable. For stainless steel 7x7 cable at 1570 N/mm2, published working loads are 3 kg, 6 kg, 8 kg and 12 kg respectively. Reutlinger's Type 12 technical information states an operating coefficient / safety factor of 5 for the specified cable/holder combinations.

Potential attachment variants include:

- Type 12 M4x7 with release, serial 193.000.133;
- Type 12 M4x7 without release, serial 193.000.134;
- Type 12 M8x1 A9, serial 193.000.139;
- Type 12 M8x1 A9 with fork coupling, serial 193.000.141.

Why it is interesting:

- 0.81 mm and 1.0 mm stainless options remain visually compatible with the product intent;
- manufacturer publishes exact stainless working-load data;
- compact threaded and fork variants are available;
- factory certificates based on special tests are available on request.

Why it is not approved:

- actual S/M/L butterfly masses are not controlled;
- lower-yoke mass is not controlled;
- kinetic dynamic amplification is not established;
- exact upper fitting is not selected;
- complete VX4800 line assembly has not been tested.

Manufacturer references:

- https://reutlinger.de/en/cable-holder/type-12
- https://reutlinger.de/de/arbeitslast-edelstahl-drahtseilhalter

## Supplier finalist B: Griplock Premium Type 12 / 1.0 mm stainless

Role: lighting-industry suspension-system reference finalist.

Griplock's current working-load guidance publishes 20 lb working load for a Premium Type 12 gripper with 1.0 mm stainless cable. The company states that its working-load limits are 20 percent of the minimum break strength of the gripper/cable combination. Griplock's matching 1.0 mm Extra-Fine stainless cable page publishes a 17 lb working load.

The compact `12Z-M4-Q1.6` side-exit gripper is relevant to carrier-detail exploration because it uses an M4 x 0.70 thread and supports 1.0 mm cable.

Why it is interesting:

- 1.0 mm cable stays inside the current visual target;
- the manufacturer specializes in lighting suspension systems;
- compact threaded and side-exit gripper configurations are available;
- matching 1.0 mm cable is a standard product.

Why it is not approved:

- the complete candidate assembly must be confirmed by Griplock as an exact matched system;
- actual element mass and dynamic design load are unknown;
- lower three-point bridle is unresolved;
- kinetic fatigue suitability has not been established.

Manufacturer references:

- https://griplocksystems.com/technical-legal/weight-load-guidelines
- https://griplocksystems.com/product/extra-fine-cable
- https://griplocksystems.com/product/12z-m4-q1-6

## Engineering promotion gates

No candidate may be promoted to final suspension authority until all of the following are complete:

1. Final S, M and L butterfly masses are measured and controlled.
2. Complete lower bridle/yoke/terminal mass is controlled.
3. Dynamic line design load is established from the released motion architecture and physical test evidence.
4. Structural/mechanical engineer approves the load factors and required design load per line.
5. Exact cable, gripper and terminal part numbers are fixed.
6. Manufacturer confirms the published rating applies to that exact combination and installation orientation.
7. Production-equivalent pull/slip testing passes.
8. Lower three-point bridle and butterfly attachment are proof-loaded as a complete assembly.
9. Fatigue and repeated-adjustment testing passes.
10. Independent secondary retention is resolved.
11. Full 240-line factory pre-hang and dynamic-clearance testing passes before construction release.

## Testing plan for samples

The first supplier sample round should be used to establish process capability, not merely visual approval.

At minimum test:

- dimensional inspection of cable and gripper;
- cable cut quality and fraying behavior;
- adjustment repeatability;
- release-lock behavior;
- pull/slip behavior at multiple cable lengths;
- off-axis/cable-exit behavior within manufacturer limits;
- visible marking and surface damage after repeated adjustment;
- production assembly time;
- finish compatibility with canopy and butterfly hardware;
- lower-yoke proof load once prototype detail exists;
- cyclic/fatigue behavior once the kinetic duty case is defined.

## Spares and serviceability

RFQ quantities should distinguish installed hardware from project spares. The existing commercial service strategy calls for 5 percent spare grippers/terminal hardware. Exact spare quantities can be finalized only after a supplier system is selected and the replaceable assembly boundary is frozen.

## Explicit non-claims

This qualification does not claim:

- that 0.81 mm or 1.0 mm cable is structurally adequate for the final product;
- that the published static working loads are valid for the final kinetic duty cycle;
- that either supplier has approved VX4800;
- that the three-point Blender yoke is an engineered detail;
- that site anchors or the rotating carrier are resolved;
- that the product is ready for occupied-space installation.
