# RFQ-KIN-BRK-01 — VX4800 direct-carrier fail-safe holding and fault-stop brake enquiry

Status: **prepared-not-sent**  
Fixture: AETHERIA VORTEX VX4800-BF-01  
Engineering revision: 1.3.0

Primary route: RINGSPANN Corporation / RINGSPANN GmbH  
Alternate route: Chr. Mayr GmbH + Co. KG

## Enquiry purpose

We are developing a fixed-side, power-off mechanical brake acting directly on a passive rotating carrier ring/disc. The objective is to retain carrier holding/fault-stop capability even if the propulsion belt/gear transmission is disconnected or failed. This enquiry is for application-engineering input and does not contain a released brake torque or stopping-energy value.

## Controlled architecture

- vertical-axis rotating carrier
- carrier speed range: 0.08 to 0.65 rpm; nominal 0.36 rpm
- healthy normal stops are intended to use controlled drive deceleration
- fault/power-loss holding is being studied with a spring-applied/electrically released or equivalent fail-safe fixed-side brake
- the brake should act directly on a passive carrier ring/disc so the required holding path can bypass a failed drive transmission
- the brake is not the positive mechanical service lock
- technician access requires verified zero speed, isolation and an independent positive service lock
- manual release must not create uncontrolled freewheel

## Inputs intentionally not supplied as design values

- static holding torque
- dynamic fault-stop torque
- stopping energy
- stopping time/travel criterion
- brake effective radius
- disc/ring thickness
- thermal duty and application count
- final safety-function allocation or PL/SIL requirement

Please identify any assumptions and do not convert them into final ratings.

## Requested application-engineering response

Please advise:

1. Which fixed-caliper / direct-disc fail-safe brake families should be evaluated for this architecture.
2. The input data required to size static holding duty separately from dynamic fault/emergency stopping duty.
3. Brake force/torque calculation methodology and effective-radius requirements.
4. Permissible disc/ring thickness range, material/friction-surface requirements and surface-finish requirements.
5. Permissible axial/radial runout and alignment tolerances.
6. Apply/release times and the conditions under which they are valid.
7. Power-off state, release voltage/current and any release/control-module requirements.
8. Brake-state or wear/air-gap monitoring options and diagnostic limitations.
9. Thermal-energy and repeated-stop methodology, including required cooling/recovery assumptions.
10. Manual-release method and how uncontrolled carrier motion should be prevented during service.
11. Wear inspection, friction-lining replacement, air-gap adjustment and maintenance requirements.
12. Mounting/reaction-load requirements for the fixed caliper bracket.
13. Exact mating drawing and CAD for any proposed variant and disc/ring interface.
14. Relevant component certifications or safety data, clearly separated from any claim about complete-machine PL/SIL/category.
15. Which values are manufacturer-published, application-calculated or estimates.

## Required submittals for technical comparison

For any exact proposed brake variant, please provide where available:

- exact family/model/variant code
- current datasheet
- exact disc/ring mating drawing
- STEP/IGES or equivalent CAD
- static holding calculation
- dynamic stopping/energy calculation method or application calculation
- release/control and monitoring documentation
- installation/maintenance/manual-release instructions
- explicit assumptions and missing application inputs

## Engineering boundary

No brake model, torque, disc radius/thickness or safety integrity claim is selected by this enquiry. Static holding and dynamic stopping remain separate duties. Final selection requires controlled load/energy cases, released risk allocation, direct-carrier transmission-failure containment and physical stop/hold validation.
