# RFQ-KIN-DRV-01 — VX4800 very-low-speed kinetic carrier drive application enquiry

Status: **prepared-not-sent**  
Fixture: AETHERIA VORTEX VX4800-BF-01  
Engineering revision: 1.3.0

Primary route: SEW-EURODRIVE Company of Canada Ltd.

## Enquiry purpose

We are developing a fixed-side motor/reducer drive for an architectural kinetic-lighting carrier. We are requesting application-engineering guidance for stable, quiet, continuous very-low-speed operation. This is a pre-prototype enquiry and does not contain a released torque value.

## Controlled product information

- vertical-axis carrier rotation
- carrier speed range: 0.08 to 0.65 rpm; nominal 0.36 rpm
- normal direction reversal is not yet approved
- preferred control development uses jerk-limited or equivalently smooth start/stop profiles
- carrier uses 240 long suspended assemblies whose transient lag will be physically measured
- powered kinetic equipment remains fixed-side where practical
- motor/reducer is propulsion only and is not the primary vertical support
- motor/reducer brake, if present, is not credited as the sole service lock or sole carrier holding path
- positive transmission to the carrier is being studied separately

## Inputs intentionally not supplied as design values

The following remain controlled TBDs:

- required drive torque
- equivalent transient rotational inertia
- approved acceleration and jerk limits
- final stopping profile
- final transmission ratio and ring diameter
- belt/gear reactions
- structural mount reactions
- exact duty spectrum and endurance interval

Please identify any preliminary assumptions rather than silently filling these gaps.

## Requested application-engineering response

Please advise:

1. Which motor/reducer/control architecture you would study for a carrier output range of 0.08 to 0.65 rpm after the final transmission ratio is established.
2. The minimum application inputs required before you can size an exact motor/reducer variant.
3. Stable continuous low-speed control method, including any minimum motor/reducer speed or cooling limitation.
4. Torque-speed, thermal and service-factor methodology for the proposed architecture.
5. Backlash, torsional compliance and low-speed ripple considerations that could excite a suspended field.
6. Recommended drive/control strategy for smooth jerk-limited start/stop and zero-speed verification.
7. Any restrictions on prolonged holding, repeated starts/stops or commissioning jog duty.
8. Output-shaft radial/axial load limits and how belt/gear reactions must be applied to the selection.
9. Mounting orientation, alignment, lubrication and maintenance requirements.
10. Noise/vibration considerations for an architectural interior application.
11. Manual/service movement provisions and any hazards associated with gearbox or brake release.
12. Exact mating drawing and CAD for any proposed motor/reducer variant.
13. Which values are manufacturer-published, supplier-calculated or supplier estimates.

## Required submittals for technical comparison

For any proposed exact variant, please provide where available:

- exact motor/reducer/control family and model codes
- current technical datasheets
- torque-speed and thermal/application calculation
- exact output-shaft and mounting data
- STEP/IGES or equivalent CAD
- installation/maintenance manual
- brake data if a brake is included, clearly separated from the independent carrier brake function
- declared assumptions and missing inputs

## Engineering boundary

No drive variant can be selected from this enquiry alone. Final sizing remains blocked until rotating mass/CG, transient dynamic evidence, drive torque, transmission reactions, motion profile and structural mounting calculations are controlled.
