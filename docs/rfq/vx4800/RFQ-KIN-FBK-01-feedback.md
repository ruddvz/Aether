# RFQ-KIN-FBK-01 — VX4800 fixed-readhead passive-scale very-low-speed feedback enquiry

Status: **prepared-not-sent**  
Fixture: AETHERIA VORTEX VX4800-BF-01  
Engineering revision: 1.3.0

Primary route: HEIDENHAIN

## Enquiry purpose

We are developing position/speed/reference feedback for a continuously rotating architectural kinetic carrier. Powered electronics should remain fixed-side while only passive scale/target features rotate. We are requesting application-engineering guidance for modular angle-encoder or equivalent architecture at very low rotational speed.

## Controlled architecture

- vertical-axis rotating carrier
- speed range: 0.08 to 0.65 rpm; nominal 0.36 rpm
- powered readhead/electronics fixed-side
- passive scale, drum, ring or targets may rotate
- no slip ring required by the current architecture
- required functions include motion detection, speed, stall/overspeed plausibility, reference/index support and commissioning
- reaching a reference/index position is not proof that the mechanical service lock is engaged
- an independent/diverse speed plausibility channel may later be required by the released risk assessment

## Inputs intentionally not supplied as design values

- final position resolution
- update-rate/fault-detection latency requirement
- exact scale/ring diameter
- readhead air gap
- allowable carrier runout/concentricity
- safety-related control performance allocation

Please state assumptions explicitly.

## Requested application-engineering response

Please advise:

1. Which modular angle-encoder families or fixed-readhead/passive-scale architectures should be evaluated for continuous operation at 0.08 to 0.65 rpm.
2. The data required to select exact scale/drum/ring and readhead variants.
3. Behavior at the minimum 0.08 rpm speed, including update/edge/interpolation behavior relevant to reliable motion and stall detection.
4. Available absolute/incremental/reference/index architectures and power-restoration reference recovery options.
5. Scale/readhead diameter, mounting and segmentation constraints for a large carrier.
6. Permissible readhead air-gap range and sensitivity to radial/axial runout, eccentricity and mounting distortion.
7. Environmental/contamination limits and recommended protection for an architectural interior canopy.
8. Alignment/commissioning tools and verification procedures.
9. Diagnostic capabilities for loss, implausible signal, air-gap/alignment degradation or reference faults.
10. Options for a sufficiently diverse second speed/overspeed plausibility channel if later required, while keeping powered electronics fixed-side.
11. Exact mating drawings and CAD for proposed readhead/scale components.
12. Cabling, interface electronics, electrical environment and control-interface requirements for the fixed side.
13. Which performance values are manufacturer-published and which depend on application configuration.

## Required submittals for technical comparison

For any exact proposed configuration, please provide where available:

- exact readhead and passive scale/ring/drum model codes
- current technical datasheets
- dimensional/mating drawings
- STEP/IGES or equivalent CAD where available
- mounting/alignment/air-gap documentation
- interface/protocol documentation
- environmental/maintenance documentation
- explicit assumptions and missing application inputs

## Engineering boundary

No encoder family, scale diameter, air gap, resolution, update rate or safety performance level is selected by this enquiry. Final feedback architecture requires the released fault-detection/risk allocation, selected bearing/runout stack and physical full-rotation verification.
