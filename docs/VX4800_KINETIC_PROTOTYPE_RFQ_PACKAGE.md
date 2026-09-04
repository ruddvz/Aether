# VX4800 rotating-carrier prototype and RFQ package

## Status

Engineering-development input only. Not released manufacturing geometry. Not a bearing, motor, brake, belt, encoder or structural selection.

Product: AETHERIA VORTEX VX4800-BF-01  
Controlled engineering revision: 1.3.0  
Prototype package revision: 1.0.0

The purpose of this package is to move the kinetic track from architecture into controlled pre-prototype work without inventing the physical inputs that Issues #7 and #9 still have to supply.

## What is now ready to do

The repository has enough authority to:

1. issue structured technical RFQs for bearing, drive, positive transmission, direct-carrier brake, feedback and prototype fabrication;
2. create coordination CAD for mechanical interface zones;
3. detail a prototype service lock and secondary-retention concept parametrically;
4. build a T1/T2 rig design once the real mass envelope and rig risk assessment are controlled;
5. collect manufacturer CAD, mounting requirements, maintenance instructions and application-engineering responses;
6. prepare load calculations with explicit blanks for measured data.

The repository does **not** have enough evidence to release final load-dependent sections, bolt patterns, brake radius, belt width/tension, trim capacity or retention rating.

## Controlled baseline that cannot be silently changed

- 240 engineering elements.
- S66 / M144 / L30.
- Controlled cable-exit coordinates in `composition/engineering-v1.3.0.csv`.
- 14 fixed architectural accent heads.
- 2400 x 1500 x 150 mm canopy envelope.
- Rotating-carrier coordination envelope approximately 2260 x 1330 mm with the current 24 mm coordination thickness parameter.
- Vertical rotation axis.
- 0.08 rpm minimum, 0.36 rpm nominal and 0.65 rpm maximum conceptual operating envelope.
- No planned rotating electrical loads.
- No slip ring under the current architecture.

The 24 mm carrier value is not a statement that the bearing, drive, brake, retention and sensing stack must fit inside 24 mm. It is a coordination parameter from the controlled geometry model.

## Prototype interface architecture

The next mechanical CAD should treat the following as distinct functional zones.

### KZ-PRIMARY-BEARING

The primary bearing transfers the complete normal structural load between a fixed bearing-support structure and the rotating hub/carrier.

The fixed side needs a supplier-compliant mounting face, a structurally stiff load path into the canopy frame and full fastener/inspection access. The rotating side needs a dedicated structural attachment to the hub/carrier.

Do not use the motor, gearbox, bearing seals, sensor brackets, decorative skin or false ceiling as part of this load path.

The final bearing interface stays parameterised until controlled mass, CG and combined axial/radial/moment load cases exist.

### KZ-POSITIVE-DRIVE

The preferred study remains a fixed drive acting on a positive rotating transmission interface, currently a synchronous toothed ring/belt architecture with ring gear/pinion retained as an alternative.

The drive should be mechanically separable from the primary vertical support. Adjustment/tensioning, guarding, removal and inspection need their own fixed service region.

Belt pretension, tooth engagement, tangential drive force and tensioner reaction must be included in bearing/support reactions. The transmission is not allowed to distort the bearing support ring.

### KZ-DIRECT-CARRIER-BRAKE

The hardened architecture adds a direct-carrier brake study because a brake acting only through the motor/reducer and the same belt/gear train can share the drive-transmission failure path.

Preferred study:

- fixed-side spring-applied, electrically released caliper or equivalent;
- passive annular brake ring/disc on the rotating carrier;
- power-off holding without rotating electrical power;
- motor/reducer brake treated as supplemental until failure analysis proves otherwise;
- positive service lock still mandatory for technician access.

The brake ring must be a dedicated engineered friction/structural interface. It must not be improvised from a precision encoder ring, secondary-retention face or decorative carrier surface.

No effective brake radius, disc thickness, clamping force, holding torque, stopping torque or energy value is released yet.

### KZ-SERVICE-LOCK

The service lock is a positive fixed-frame mechanical restraint.

Prototype detail should provide:

- fixed double-shear or equivalent lock support;
- captive positive lock device;
- dedicated rotating receiver ring or lugs;
- direct visual verification of full engagement;
- optional fixed-side state sensing only as a supplement;
- physical geometry that rejects or clearly exposes partial engagement;
- a load path into the fixed structural frame rather than through motor torque.

A stopped or brake-held carrier is not mechanically safe to access until the service-lock and released isolation procedure are satisfied.

### KZ-SECONDARY-RETENTION

The preferred study remains normally clear, non-load-sharing annular retention with multiple fixed catch sectors and multiple distributed rotating capture features.

The detailed prototype must answer a harder question than “is there a safety ring?” It must show which failures are contained.

At minimum review:

- primary bearing internal/race failure;
- primary bearing mounting-joint/fastener failure;
- local hub/carrier fracture;
- fixed support local fracture;
- capture fastener failure.

The rotating capture attachments should bypass relevant primary-bearing fasteners and should not all depend on one local hub feature. Any structural failure that is not reasonably containable must be stated explicitly and controlled through primary structural design.

Normal running clearance and failed-support engagement are separate modeled states.

### KZ-FEEDBACK

Powered sensing should stay fixed-side.

The prototype layout should reserve:

- one fixed non-contact primary readhead;
- one passive rotating scale/ring/target system;
- a distinct passive reference/index feature if required;
- a second fixed/diverse plausibility sensor location if the released risk assessment requires independent overspeed plausibility;
- protected adjustment and service access.

Do not specify a single encoder resolution simply because a high-resolution catalogue model exists. The actual resolution/update requirements come from low-speed fault-detection latency, controlled stopping and commissioning needs.

### KZ-BALANCE-TRIM

Balance stations belong on the rotating structural assembly and must not move any cable exit.

Trim masses need captive locations, positive locked fasteners, secondary capture and a controlled station/mass record. Replacing one suspended assembly triggers a balance review.

Trim range remains unknown until Issue #9 produces production mass distributions.

### KZ-SERVICE-CORRIDOR

Component serviceability is now part of the engineering layout, not something to solve after detailed CAD.

The next model must include service envelopes for:

- bearing fasteners/inspection;
- motor/reducer removal;
- belt/gear inspection and tensioning;
- brake-pad/caliper inspection and replacement;
- lock engagement/inspection;
- retention inspection;
- sensor air-gap/reference adjustment;
- trim access;
- wiring/isolation coordination with Issue #11.

Removable panels, false ceilings and service doors are access features, not structural members.

## Drawing sequence

### P0: interface-zone coordination

Create one fixed-frame plan, one rotating-hub/carrier plan and at least one radial/axial stack section.

Show all bearing, drive, brake, lock, feedback, trim, retention and service zones as distinct components/layers. Load-dependent dimensions remain named parameters marked TBD.

### P1: candidate-specific mating package

After supplier responses identify credible exact candidates, add vendor mating dimensions without promoting the component to selected status.

Check:

- bearing support and bolt access;
- drive ring/sprocket/tensioning geometry;
- brake ring/caliper effective radius and extraction path;
- sensor readhead air-gap/runout compatibility;
- service-lock receiver and tolerance envelope;
- secondary-retention normal/failed states.

### P2: prototype-release drawing set

Only after measured masses and approved calculations are available, replace the required TBD fields with controlled values and release the prototype drawing set through the repository gates.

## Supplier RFQ strategy

RFQs are separated into six technical packages.

### RFQ-KIN-BRG-01: primary bearing

Ask for bearing-family/variant recommendations, combined-load method, starting/running torque, mounting flatness/rigidity, fastener/preload requirements, lubrication, corrosion protection, runout/play, service-life method, CAD and maintenance instructions.

Do not give a guessed mass or design load.

### RFQ-KIN-DRV-01: motor/reducer

Ask for stable very-low-speed behaviour, control strategy, torque-speed curves after final load data, backlash/compliance, output-load limits, thermal data, noise information, service movement, lubrication and CAD.

Gearbox self-locking is not the service restraint.

### RFQ-KIN-BELT-01: positive synchronous transmission

Ask for belt/tooth family, tooth engagement, belt-width selection method, installation-tension method, predicted static/separation loads once torque data exists, alignment/runout limits, tooth-jump protection, inspection and ring fabrication tolerances.

### RFQ-KIN-BRK-01: direct carrier brake

Ask for power-off spring-applied architecture, friction-ring requirements, clamping/tangential force, static holding versus dynamic-stop capability, energy/thermal method, release/apply time, manual release, wear monitoring, status switch, electrical release requirements, mounting stiffness and CAD.

Static holding data must not be silently treated as fault/emergency stop data.

### RFQ-KIN-FBK-01: feedback

Ask for fixed-readhead/passive-ring solutions, incremental/absolute options, index strategy, very-low-speed update behaviour, air-gap/runout tolerance, contamination limits, startup/reference behaviour, diagnostics and possible second-channel architecture.

### RFQ-KIN-FAB-01: structural/prototype fabrication

Ask for large-ring post-weld machining, inspection capability, material traceability, distortion control, fastener access, NDT options, modular replaceability and proof-test-fixture capability.

## Current manufacturer evidence used to shape the RFQs

These sources justify questions and architecture families only. They do not select components.

### Bearing mounting

Kaydon's slewing-bearing mounting guidance states that mounting-structure rigidity and flatness affect bearing behaviour, and that out-of-flat mounting can increase frictional torque and reduce life. Kaydon also publishes installation guidance requiring controlled mounting faces after welding/stress relief and notes that tighter tolerances may be needed where low rotational resistance or high precision is required.

Sources recorded in `qualification/vendor-evidence-v1.json`:

- https://www.kaydonbearings.com/white_papers_11.htm
- https://www.kaydonbearings.com/downloads/catalog390/Kaydon_390_InstallMaintenance.pdf

### Synchronous belt reactions

Gates' PowerGrip GT3 design manual notes that synchronous-belt installation tension has to be designed for the load/geometry, that excessive tension increases bearing and shaft loading, and that severe undertension can produce ratcheting and large transient shaft-separation forces.

Source:

- https://www.gates.com/content/dam/documents-library/catalogs/powergrip-gt3-drive-design-manual-en.pdf

This is why belt pretension is explicitly part of the VX4800 bearing/support calculation.

### Power-off brake family

RINGSPANN publishes spring-activated, electromagnetically released caliper brake families. That supports the feasibility of studying a fixed-side, power-off caliper acting on a passive carrier ring.

Source:

- https://www.ringspann.com/en/service/downloads/installation-instructions/brakes/electromagnetic-brake-calipers

No RINGSPANN model or brake force is selected.

### Fixed readhead / passive rotating scale

HEIDENHAIN's modular angle-encoder architecture uses separate circular scales/scale drums and scanning heads, and current product pages include scale drums without integral bearings. This supports the architectural concept of a passive rotating scale with powered scanning electronics fixed to the canopy structure.

Sources:

- https://www.heidenhain.com/products/encoders/angle-encoders/modular
- https://www.heidenhain.com/product-details/modular-angle-encoders/1143118-01

No HEIDENHAIN model, accuracy, speed or functional-safety capability is selected for VX4800.

## T1 test rig

T1 should be a dedicated single-suspension dynamics rig, not a miniature final product.

Concept:

- rigid fixed frame;
- guarded rotary arm/table or equivalent motion stage;
- adjustable suspension-exit radius;
- actual controlled line length from the engineering schedule;
- production-intent gripper/cable/lower bridle/butterfly when available;
- independent actual position/speed measurement;
- controlled command profile;
- synchronized load and optical/video data.

The rig drive can be intentionally over-capable for test development, but its rating cannot be copied into the product motor calculation.

## T2 test rig

T2 reproduces a real schedule-derived cluster.

The selected element IDs, relative X/Y coordinates, S/M/L classes and controlled line lengths must be archived with the test record. A visually convenient cluster is not acceptable.

T2 measures local interaction and the three local clearance categories before full-field testing:

- butterfly-to-butterfly;
- butterfly-to-cable;
- cable-to-cable.

It can also introduce a controlled/sacrificial added-drag condition to develop snag detection. T2 cannot close full-field dynamic-clearance approval.

## Instrumentation requirements

The rig specification currently requires functions rather than invented ranges:

- independent actual angular position/speed;
- drive load/torque proxy or transducer;
- cable tension for selected cases;
- calibrated/synchronised optical motion measurement;
- dynamic-clearance measurement;
- common time synchronisation;
- airflow measurement where drag studies are run;
- optional development acoustics.

Actual ranges and sample rates are selected only after the fastest approved transient and measured mass/load envelope are known.

## Test-rig safety boundary

T1/T2 are engineering test equipment. They are not occupied-space installations and they do not establish the final product safety category.

Before construction:

- measured mass envelope must be controlled;
- rig structural calculation must be approved;
- instrument ranges must be selected;
- guarding/test risk assessment must be released;
- test procedure must be released.

Powered testing requires guarding, a test-rig emergency stop and personnel exclusion from the swept/fragment zone.

## Promotion gates

The pre-prototype package deliberately remains unreleased.

The following are currently false:

- controlledMassInputsAvailable
- carrierStructuralConceptReviewed
- bearingInterfaceConceptReviewed
- driveInterfaceConceptReviewed
- directCarrierBrakeConceptReviewed
- serviceLockDetailReviewed
- secondaryRetentionDetailReviewed
- feedbackTargetLayoutReviewed
- t1RigReleasedForBuild
- t2RigReleasedForBuild
- prototypeDrawingSetReleased

A schema prevents `finalPrototypePackageReleased: true` until all of those gates are true.

## Recommended execution order

1. Send the six technical RFQ packages with all unknown load fields clearly marked pending.
2. Receive supplier application-engineering responses and exact CAD/mating documents.
3. Build P0 interface-zone coordination CAD without changing controlled setout.
4. Complete Issue #9 S/M/L mass measurements and production variation.
5. Freeze the T1 rig structural/instrument envelope from real masses, then build T1.
6. Use T1 data to constrain acceleration/jerk, settling and preliminary dynamic load response.
7. Select a schedule-derived T2 cluster and release T2 after its own rig calculation/risk review.
8. Use T1/T2 evidence plus supplier data to prepare candidate-specific P1 mechanical package.
9. Only then select bearing/drive/brake/feedback candidates and calculate load-dependent geometry.
10. Continue to T3/T4 and full pre-hang before any occupied-space release.

The aim is to make every later numeric decision traceable to manufacturer data, engineering calculation or physical measurement rather than to an animation or catalogue maximum.
