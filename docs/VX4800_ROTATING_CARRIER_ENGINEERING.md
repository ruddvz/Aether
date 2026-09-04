# VX4800 rotating-carrier and kinetic mechanical engineering

Date: 2026-09-04

Status: engineering-development input, not construction release.

Product: AETHERIA VORTEX, VX4800-BF-01

Repository architecture record: `fixtures/vx4800/kinetics/architecture-v1.json`

Qualification shortlist: `fixtures/vx4800/kinetics/qualification/shortlist-v1.json`

This document defines the mechanical architecture and evidence gates for the VX4800 rotating carrier. It deliberately does not assign a final bearing model, motor torque, brake torque, dynamic amplification factor, structural reaction or secondary-retention rating while the required physical inputs remain unknown.

## Engineering objective

The rotating system is to be slow, quiet, predictable, serviceable, fail-safe and physically restrainable for service.

The 240 butterflies do not flap. Their 240 suspension lines and the carrier rotate together as one field about the vertical axis. The 14 architectural accent heads remain fixed. The rotating carrier has no planned electrical loads, so the current architecture keeps powered controls and sensing electronics on the fixed side and does not require a slip ring.

A future powered device on the rotating carrier is not a small component substitution. It is a controlled architecture change because it reopens rotary power/data transfer, service, failure and protective-bonding questions.

## Controlled baseline and authority boundary

The following product inputs remain controlled and are not changed by this work:

- 240 engineering elements;
- allocation S66, M144 and L30;
- controlled cable-exit coordinates in `composition/engineering-v1.3.0.csv`;
- 14 fixed LED positions;
- 2400 x 1500 x 150 mm canopy envelope;
- current rotating-carrier coordination parameters of approximately 2260 x 1330 mm and 24 mm thickness parameter;
- vertical rotation axis;
- current engineering speed envelope of 0.08 to 0.65 rpm, nominal 0.36 rpm;
- external controlled manufacturing geometry authority;
- repository geometry remains coordination-only;
- Blender remains visualization authority only.

This track does not qualify butterfly material, suspension hardware, lighting photometry, electrical lighting architecture or Blender rendering.

If later bearing, drive, catch or service-lock engineering cannot be packaged inside the controlled envelope without moving a cable exit, LED location, canopy boundary or manufacturing geometry, the correct action is a controlled design-change proposal. The baseline must not be silently edited.

## Evidence dependencies

### Issue #9: butterfly material and mass evidence

Issue #9 must eventually supply production-intent S, M and L complete suspended-assembly mass records, center-of-gravity data where relevant, and production mass variation. Those records use `schemas/aether-butterfly-mass-measurement.schema.json`.

The kinetic track must not replace those measurements with densities, CAD volumes, bounding boxes or decorative-glass assumptions.

### Issue #7: suspension and dynamic-load evidence

Issue #7 must eventually supply physical pendulum lag, transient cable angles, dynamic amplification/load cases, line design loads and fatigue duty. These results feed both the suspension system and the rotating mechanism.

### Issue #11: kinetic electrical implementation

This document defines mechanical motion behavior, sensing architecture boundaries and restart requirements. Issue #11 remains responsible for the final electrical isolation, safety-chain implementation, motor-drive/control service zones and wiring. The mechanical service lock remains mandatory even if the final controls have an interlock.

## Unknown physical inputs

The current architecture explicitly treats these as unknown:

- actual S complete suspended-assembly mass;
- actual M complete suspended-assembly mass;
- actual L complete suspended-assembly mass;
- total installed rotating mass;
- rotating assembly center of gravity;
- production mass variation;
- equivalent rotational inertia;
- dynamic amplification;
- pendulum lag;
- transient cable angles;
- bearing axial/radial/moment design load envelope;
- drive torque;
- braking torque and energy;
- imbalance;
- structural reactions.

These are not blanks to be filled with convenient assumptions. They are promotion gates.

## 1. Fixed and rotating load paths

The architecture separates five mechanical functions.

### Primary gravity and operating load path

Building structure
-> engineered site interface zones
-> fixed canopy structural frame
-> primary bearing support structure
-> primary bearing rings/rolling elements and controlled fasteners
-> rotating structural hub/carrier
-> 240 positively retained upper suspension exits
-> 240 main suspension lines
-> lower bridles/yokes and terminals
-> 240 butterfly suspended assemblies.

The decorative canopy skin, false ceiling, motor gearbox, bearing seals, electrical conduits, lighting heads and service panels are excluded from this primary structural path.

### Drive torque path

Fixed motor/gearmotor reaction mount
-> drive output
-> positive transmission under qualification
-> dedicated rotating drive ring/interface
-> rotating structural hub/carrier.

The drive is not allowed to become the primary vertical carrier support.

### Braking path

Fixed-side brake
-> drive shaft/geartrain
-> positive transmission
-> dedicated rotating drive interface
-> carrier
-> fixed motor/brake reaction structure.

This path is separate in purpose from primary gravity support and from the service lock.

### Mechanical service-lock path

Rotating dedicated lock receiver
-> positive mechanical lock pin/bolt
-> fixed lock bracket
-> fixed canopy structural frame.

A technician must be able to establish this path without relying on motor torque or software.

### Secondary-retention path

Rotating retained hub/capture flange
-> normally-clear annular catch structure
-> fixed structural catch brackets
-> fixed canopy structural frame
-> engineered site interfaces
-> building structure.

The catch is not intended to carry normal operating load. It exists to prevent catastrophic carrier fall if the primary support separates.

## 2. Primary bearing architecture

No bearing is selected yet.

The current candidate families are:

| Family | Why it is credible | Key concerns before selection |
| --- | --- | --- |
| Large slewing-ring / turntable bearing | Purpose-built family for combined axial, radial and moment loading; supplier families exist for low-speed turntable duty | Suspended/tension load case, mounting-ring stiffness, bolt loading, starting/running torque, runout, lubrication, service replacement |
| Crossed-roller slewing/large bearing | High stiffness and combined-load capability can suit a precision low-speed rotating plate | Mounting accuracy, preload sensitivity, torque, support stiffness, cost, service access |
| Large thin-section bearing | Potentially attractive for canopy height | Must not be promoted merely because it is thin; combined load, moment stiffness, bolt/support design and secondary retention still need supplier proof |
| Custom multi-roller turntable | Can distribute support around a large footprint | Load sharing, alignment, wear, noise, debris, adjustment and redundant retention become more complex |

Kaydon currently publishes multiple slewing/turntable families. Its XR cross-roller family is described as providing high stiffness and low rotational torque within a minimal envelope, while its RK family is positioned for intermittent low-velocity turntable use. Its selector accepts static load and envelope inputs rather than treating a diameter alone as a selection basis.

Schaeffler's crossed-roller product information states that the X roller arrangement can support axial force in both directions, radial force, tilting moment and combinations in one bearing position, and describes the family as rigid with high running accuracy.

Those statements make the families credible research candidates. They do not establish a VX4800 bearing rating.

The final supplier return must include:

- exact manufacturer and part/configuration;
- combined-load calculation or selection confirmation using approved VX load cases;
- permitted mounting orientation including suspended/tension axial loading;
- ring support stiffness and mounting-flatness requirements;
- bolt size, class, preload and joint assumptions;
- starting and running torque data or test method;
- preload/clearance and runout;
- lubrication type and interval;
- sealing and corrosion guidance;
- life/duty methodology at the released motion profile;
- replacement and inspection method.

A bearing must be replaceable without destroying the decorative canopy or dismantling the entire 240-line field unless a deliberate service module proves otherwise.

## 3. Drive architecture

No motor or gearbox torque is selected.

### Preferred study: fixed gearmotor plus positive synchronous ring drive

The leading architecture study is a fixed-side gearmotor driving a concentric toothed/synchronous ring associated with the carrier. It keeps powered equipment fixed, separates motor mass from the rotating field, avoids relying on friction for position fidelity, and permits the bearing to remain a structural bearing rather than becoming a motor-supported spindle.

A synchronous belt system is attractive because current industrial families provide positive tooth engagement without chain lubrication. Gates currently describes Poly Chain GT Carbon as a polyurethane synchronous belt system using carbon tensile cords and matched sprockets, with no lubrication or retensioning requirement for the published system. That is a family-level reference only. Exact pitch, width, pulley, belt length, pretension and torque capacity remain unselected.

The design must resolve:

- belt/ring geometry inside the shallow canopy;
- wrap angle and tooth engagement;
- pretension reactions on motor and carrier;
- tensioning/adjustment method;
- guarding;
- contamination and wear inspection;
- structure-borne noise;
- replacement without disturbing the 240 exits;
- any splice/join strategy if a continuous ring cannot be packaged;
- exact manufacturer calculation using the approved torque envelope.

### Alternate: ring gear and pinion

A geared ring can provide positive motion and compact torque transmission. It may be preferable if belt packaging, tooth engagement or long-term dimensional stability is weak. It introduces backlash, lubrication or wear-management questions, gear mesh noise and alignment requirements that must be compared in prototype testing.

### Non-preferred: friction wheel

A friction wheel remains a study only. It is not the baseline because slip, wear, contamination and normal-force variation complicate deterministic low-speed movement, jam diagnosis, holding and position feedback.

### Reserve study: central geared drive

A central drive is acceptable only if it gives materially better service access and torsional behavior without pushing the motor/gearbox into the primary gravity load path.

## 4. Calculation framework

The repository distinguishes:

- published manufacturer data;
- engineering calculation;
- prototype measurement;
- controlled production measurement;
- assumption;
- design target.

Every future calculation record should identify which class each input belongs to.

### Rotating mass and inertia

The controlled setout gives each element's XY position. Once real mass records exist, polar inertia about the vertical axis can be evaluated as:

`I_z = sum(m_i * r_i^2 + I_i,local) + I_carrier + I_rotating_drive_parts`

Outputs must include total rotating mass, center of gravity, polar inertia and a first-moment imbalance map.

The calculation must use production-intent carrier/hub/drive rotating masses as measured or controlled. Nominal S/M/L family counts are not enough for final balance if production variation is material.

### Bearing load cases

Bearing selection must use an approved load envelope containing, as applicable:

- gravity;
- center-of-gravity offsets;
- radial disturbances;
- dynamic amplification;
- drive and brake reactions;
- imbalance;
- support/mount geometry.

Outputs include axial load, radial load, overturning moment and mounting/bolt reactions. Supplier catalog maxima are not VX4800 design loads.

### Drive torque

The calculation framework is:

`T_required = reserve * ((I_eq * alpha) + T_bearing + T_drag + T_imbalance + T_other)`

It must be evaluated by signed load case using measured inputs. The reserve factor is an engineer-approved input, not an arbitrary multiplier added to make a motor look safe.

Outputs include steady torque, starting torque, acceleration torque, normal-stop braking demand, fault-stop demand and a candidate motor/gearbox/transmission envelope.

### Braking

Normal stop, fault stop, emergency stop and power-loss stop are separate cases. For each released case calculate or measure initial speed, equivalent inertia, stopping profile, braking torque envelope, stopping travel, energy per stop and thermal duty.

### Balance

First moments are tracked with:

`M_x = sum(m_i * x_i)`

`M_y = sum(m_i * y_i)`

The calculated trim solution is not accepted until verified by low-speed physical testing.

## 5. Motion profile

The motion profile is an engineering requirement, not a render animation.

### Normal run

- soft start is mandatory;
- acceleration is limited by physical pendulum testing;
- steady speed remains inside the released 0.08 to 0.65 rpm range;
- normal stop uses controlled deceleration while the drive is healthy;
- zero speed is verified before parking/holding state;
- abrupt command steps are prohibited.

### Direction reversal

Instantaneous reversing is prohibited.

Routine automatic reversing is not currently approved. If reversal is later required, the sequence is controlled stop, verify zero speed, wait a test-derived pendulum-settle interval, then command the opposite direction through the normal soft-start profile.

### Commissioning/jog mode

Jog is allowed only as a restricted commissioning/service function at a test-derived reduced speed/acceleration. The service lock must be disengaged before motion and re-engaged before mechanical access.

### Service mode

Mechanical access to the moving sweep or pinch zones is not permitted while motion is enabled.

## 6. Braking and holding

Four functions are kept distinct.

### Normal controlled deceleration

The motor drive/controller performs normal ramp-down while control and feedback remain healthy.

### Parking/holding

The preferred study is a fixed-side normally-engaged mechanical brake. Current SEW-EURODRIVE BR/BY/BZ planning information describes spring-loaded brakes that open electrically and apply by spring force when power is interrupted. This is an architecture reference for power-off behavior, not a selected brake.

### Fault stop

Where drive and feedback remain trustworthy, a fault-specific controlled stop may reduce excitation of the 240 pendulums. Where control is no longer trustworthy, propulsion is removed and the qualified mechanical brake acts according to the final risk assessment.

### Emergency stop

Final stop behavior, category and safety performance remain subject to the released risk assessment and electrical safety design. This document makes no SIL, PL or safety-category claim.

The motor brake is never the sole service restraint. Gearbox self-locking is also not accepted as the service lock.

## 7. Positive mechanical service lock

The proposed architecture uses a fixed-frame lock pin or bolt engaging a dedicated receiver ring/bracket on the rotating structural assembly at defined service index positions.

Required behavior:

- carrier is first at verified zero speed;
- lock receiver is aligned to a service index;
- captive lock fully engages;
- engaged/disengaged state is directly visible;
- lock is mechanically retained against accidental withdrawal;
- lock is compatible with site lockout/tagout;
- service disturbance loads transfer into the fixed structural frame;
- the lock does not load encoder scales, bearing rolling elements or delicate drive teeth;
- a fixed sensor may report engagement, but the technician still verifies it mechanically;
- normal motion is interlocked against an engaged lock in the final electrical design.

Validation includes tolerance/runout engagement, static proof in both rotational directions once loads are established, partial/mis-engagement tests and repeated service-cycle wear testing.

## 8. Independent secondary retention

A loose fixed-to-rotating tether is not an acceptable default because a continuously rotating carrier would wind it up or force a rotary interface.

The preferred concept is an annular capture/catch system.

### Normal state

A rotating structural capture flange or retained hub feature runs with controlled clearance inside or below multiple fixed structural catch sectors. There is no routine load sharing and no routine rubbing.

### Failure state

If the primary bearing/support permits abnormal axial or radial separation, the rotating capture feature contacts the fixed catch sectors. Multiple circumferential sectors transfer the abnormal load into the fixed canopy frame and site support path, limiting downward loss and overturning.

The catch design must be independent of the relevant primary-bearing failure modes to the extent practicable. Simply bolting both the bearing and the catch to the same weak removable plate would not provide meaningful independence.

### Qualification

Normal clearance is not yet numeric. It must be derived from bearing runout, carrier deflection, mounting tolerances, thermal effects, drive/sensor clearances and measured dynamic motion.

The abnormal load rating is unknown until the failure load case is approved.

The representative rig must undergo proof testing and a controlled simulated catch engagement. Any real catch event removes the fixture from service until bearing, carrier, catch surfaces, fasteners and fixed structure are inspected and dispositioned.

## 9. Balance and trim

Perfect geometric symmetry does not guarantee mass balance.

The carrier therefore needs indexed trim-mass stations that do not move controlled suspension-exit coordinates. Trim stations should sit on the structural carrier/hub in accessible locations outside cable, bearing, drive, encoder and service clearances.

Requirements:

- consume controlled production mass records from Issue #9;
- record actual installed mass by element ID where available;
- use dedicated captive trim locations;
- positively lock trim fasteners and secondarily capture trim masses against release;
- record trim station, mass and fastener state;
- replacement of a butterfly triggers a balance review;
- field service can re-trim without changing controlled geometry.

A production trim range is not defined until actual mass variation is known.

Factory procedure: establish mechanical axis/runout, build the production-intent field, record the installed mass map, calculate first moments, trim only approved stations, run low-speed balance/load checks, lock and witness-mark hardware, then archive the final trim map.

## 10. Position and speed feedback

The architecture keeps powered sensing electronics fixed-side. Passive features may rotate.

Candidate families are:

- fixed optical readhead with passive steel rotary scale ring;
- fixed magnetic readhead with passive magnetised ring;
- two fixed proximity/magnetic sensors reading a passive multi-target speed ring plus a separate index target.

Renishaw's current rotary optical encoder architecture separates a scale ring/disc from a readhead, which fits the passive-rotor principle. RLS currently describes AksIM-4 as a non-contact off-axis absolute magnetic encoder consisting of an axially magnetised ring and readhead.

No encoder is selected. A high-resolution absolute encoder may be unnecessary if a simpler passive multi-target ring can prove motion, speed and service index reliably.

Feedback must support actual rotation detection, speed measurement, failure-to-move detection, overspeed detection, controlled stop/reference support, service index/home if needed and commissioning.

The number of passive targets or required encoder resolution must be derived from acceptable fault-detection latency at the slowest 0.08 rpm case. It must not be an arbitrary CAD detail.

## 11. Jam and abnormal-motion detection

The final controls should combine multiple signals rather than trust one sensor.

Candidate signals include drive current/torque estimate, measured speed, position change over time, command versus actual response, brake state where instrumented, temperatures where justified, and independent index/reference events.

Fault patterns to validate include bearing seizure, foreign-object interference, cable/element snag, excess drag, drive fault, overspeed, feedback disagreement and failed restart.

Thresholds are set from commissioning and dynamic-test evidence plus manufacturer data. Software monitoring never substitutes for the independent mechanical catch.

Fault logs should preserve command state, feedback, drive-load estimate and stop outcome where available.

## 12. Power-loss behavior and safe restart

Automatic restart after power restoration is prohibited.

On power loss:

1. remove propulsion command;
2. the qualified power-off brake/holding function acts according to the released design;
3. when controls return, verify zero speed and system state before new motion.

If testing shows that immediate brake application at the maximum approved speed excites unacceptable pendulum motion, the response is not to weaken the holding requirement. A controlled energy reserve or ride-through strategy may be evaluated through formal change control to produce controlled deceleration before mechanical hold.

Restart permissives include controller self-check complete, valid feedback, verified zero speed, service lock disengaged before motion enable, no active jam/overspeed/drive fault, brake/drive readiness valid where instrumented, and a deliberate reset after a fault or power interruption.

The previous run command is not automatically resumed. A reference or reduced-risk verification move may be required after certain faults before normal soft start.

## 13. Cable dynamics

A 4.8 m suspended field cannot be released from animation.

Physical testing must investigate pendulum lag, transient cable angle, steady-state angular offset, torsional oscillation, start/stop wave propagation, S/M/L mass differences, production mass variation, neighboring-element interaction, fault/emergency-stop response, imbalance, air drag and shortest-versus-longest suspension lines.

Tests must include acceleration and deceleration, not only steady-state rpm. Production-intent suspended assemblies are required as soon as the material track can provide them. Record repeatability and the worst credible observed transient, not only a visually attractive nominal run.

## 14. Clearance validation

The controlled 240-position engineering schedule remains the geometry authority for locations.

Seven clearance categories are mandatory:

1. butterfly-to-butterfly;
2. cable-to-cable;
3. butterfly-to-cable;
4. field-to-fixed-head;
5. field-to-canopy;
6. carrier-to-fixed-canopy;
7. bearing/drive-to-service-components.

The existing Three.js/three-mesh-bvh inspector is useful for static screening. It is not dynamic clearance authority.

Final clearance evidence must include physical swept-motion results under acceleration, deceleration, stopping, fault cases, production mass variation, imbalance and representative longest/shortest suspension lines. Acceptance margins remain TBD until physical motion and manufacturing tolerance data exist.

## 15. Staged dynamic test programme

Do not progress directly from CAD to occupied-space installation.

### T1: single suspension assembly

Characterise a real line/bridle/butterfly pendulum, lag, orientation, drag and stop response without neighbour interaction.

### T2: representative small mixed cluster

Use mixed S/M/L sizes and representative short/medium/long drops to study neighbouring interaction, aerodynamic effects, local dynamic clearance and start/stop wave behaviour.

### T3: representative quadrant or subfield

Exercise realistic carrier stiffness/load distribution, imbalance sensitivity, drive/brake demand, bearing behaviour, feedback/fault thresholds and meaningful-scale clearance.

### T4: full 240-element factory pre-hang

This is the product-level pre-installation gate.

Measure or record:

- commanded and measured rotation speed;
- acceleration and deceleration;
- stopping time and angular travel;
- motor/drive current and torque estimate, or instrumented torque where practical;
- bearing temperature;
- motor/gearbox/brake temperatures as applicable;
- airborne noise;
- structure-borne vibration;
- carrier runout;
- cable angles and pendulum lag;
- butterfly yaw/roll/orientation;
- minimum observed clearances;
- imbalance and final trim;
- service-lock operation;
- secondary-retention proof/controlled engagement;
- fault behaviour;
- restart behaviour.

Fault cases include commanded stall/resisted motion, feedback loss, power interruption, drive fault, safely simulated overspeed, snag/drag increase, brake application at the approved worst-case speed and failed restart.

Findings from each stage must close before progressing to the next risk level.

## 16. Maintenance architecture

The canopy is designed around replaceable mechanical modules, not hidden lifetime components.

The maintenance plan must eventually cover bearing mounting bolts, support condition, runout/play, lubrication, belt/ring or gear mesh, tension/alignment/backlash, motor mount, brake wear/function, service lock, secondary-retention clearance/contact witness, trim masses, carrier/gripper fasteners, sensing air gaps/index alignment and fault trends.

Intervals remain supplier/test-derived. This architecture does not invent annual, hourly or revolution-based replacement intervals before exact components and endurance evidence exist.

Any unexplained catch contact or actual secondary-retention engagement requires immediate out-of-service inspection.

## 17. Qualification shortlist and current manufacturer references

The shortlist records manufacturer statements separately from VX4800 engineering decisions.

Current family-level references reviewed 2026-09-04:

- Kaydon turntable/slewing family overview: https://www.kaydonbearings.com/turntables.htm
- Kaydon XR cross-roller family: https://www.kaydonbearings.com/XR_turntable_bearings.htm
- Kaydon selector: https://www.kaydonbearings.com/slewing_ring_bearing_selector.htm
- Schaeffler crossed-roller product information: https://www.schaeffler.de/en/products-and-solutions/industrial/product-portfolio/rolling_and_plain_bearings/crossed_roller_bearings/
- Gates Poly Chain GT Carbon: https://www.gates.com/us/en/power-transmission/synchronous-belts/poly-chain-synchronous-belts.p.9268-000000-000045.html
- SEW-EURODRIVE BR/BY/BZ brake planning reference, 2026 edition: https://download.sew-eurodrive.com/download/html/31989101/en-EN/3323363303533236088971.html
- Renishaw rotary optical encoders: https://www.renishaw.com/en/rotary-optical-encoders--48559
- RLS AksIM-4 off-axis absolute magnetic encoder: https://www.rls.si/eng/aksim-4-rotary-absolute-magnetic-encoder

The shortlist does not approve an exact part number. Exact component selection requires the controlled physical input set, manufacturer application review and prototype evidence.

## 18. Promotion gates

Final system approval is impossible while any required gate remains false:

- `actualRotatingMassControlled`
- `centerOfGravityControlled`
- `productionMassVariationControlled`
- `bearingSelected`
- `bearingLoadCalculationApproved`
- `driveSelected`
- `driveTorqueCalculationApproved`
- `brakingArchitectureResolved`
- `serviceLockValidated`
- `secondaryRetentionValidated`
- `feedbackArchitectureValidated`
- `faultHandlingValidated`
- `dynamicClearanceValidated`
- `fullPreHangDynamicTestPassed`
- `maintenancePlanReleased`

All gates are false in architecture revision 1.0.0.

The JSON Schema enforces that `finalSystemApproved: true` is only valid when status is `approved`, authority is `controlled` and every required gate is true.

## Explicit non-claims

This engineering package does not claim:

- actual S/M/L butterfly mass;
- final rotating mass or center of gravity;
- final production mass tolerance;
- final dynamic amplification;
- final pendulum angle;
- final bearing manufacturer, model or rating;
- final motor/gearmotor model or torque;
- final belt/gear size;
- final brake model, torque, stopping time or safety category;
- final secondary-retention rating or catch clearance;
- final trim capacity;
- final encoder;
- final jam thresholds;
- final dynamic clearances;
- final structural reactions;
- certification;
- construction release.

The release path is measured mass -> approved load/inertia cases -> component selection/calculation -> prototype dynamics/fault validation -> full 240-element pre-hang -> controlled maintenance/release evidence.
