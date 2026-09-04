# VX4800 Kinetic RFQ Execution and Response Intake

Status: supplier-enquiry execution control, not component selection or manufacturing release.

Fixture: AETHERIA VORTEX VX4800-BF-01  
Controlled product engineering revision: 1.3.0

## Purpose

The RFQ requirements define what suppliers must answer. This execution layer controls contact qualification, actual dispatch evidence, response normalization, clarification, technical comparison and the firewall between supplier advice and final engineering selection.

Machine-readable controls:

- `fixtures/vx4800/kinetics/qualification/rfq-requirements-v1.json`
- `fixtures/vx4800/kinetics/qualification/rfq-contact-evidence-v1.json`
- `fixtures/vx4800/kinetics/qualification/rfq-dispatch-register-v1.json`
- `fixtures/vx4800/kinetics/qualification/rfq-response-template-v1.json`
- `schemas/aether-kinetic-rfq-contact-evidence.schema.json`
- `schemas/aether-kinetic-rfq-dispatch.schema.json`
- `schemas/aether-kinetic-rfq-response.schema.json`

## Current dispatch truth

No kinetic RFQ is recorded as externally issued by the repository at this stage.

Five packages now have a verified current public supplier route and are therefore `ready-to-issue`:

- bearing: Kaydon Bearings
- drive: SEW-EURODRIVE Company of Canada Ltd.
- synchronous transmission: Gates Corporation
- direct-carrier brake: RINGSPANN Corporation / RINGSPANN GmbH
- feedback: HEIDENHAIN

The prototype-fabrication package remains `not-issued` because a precision fabricator has not yet been contact-qualified. Schaeffler and Mayr remain alternate research targets, not contact-qualified targets.

The dispatch model deliberately distinguishes:

1. `repository-evidence-target`: relevant technical evidence exists, but a current external contact route is not yet qualified.
2. `research-required`: supplier/fabricator research or contact qualification is still required.
3. `contact-qualified`: a current official public application-engineering, technical-support, sales or service route is evidenced and may support dispatch.

`contact-qualified` is not proof of contact and `ready-to-issue` is not proof of dispatch. `dispatchStatus=issued` requires both an actual issue date and an external channel/thread reference.

## Controlled RFQ packages

- `RFQ-KIN-BRG-01`: primary bearing / slewing or crossed-roller architecture
- `RFQ-KIN-DRV-01`: fixed motor/reducer and positive carrier drive
- `RFQ-KIN-BELT-01`: synchronous belt / toothed carrier-ring transmission
- `RFQ-KIN-BRK-01`: direct-carrier power-off holding/fault brake
- `RFQ-KIN-FBK-01`: fixed-side position/speed feedback with passive rotating target
- `RFQ-KIN-FAB-01`: prototype structural hub/support, service-lock and secondary-retention fabrication

## Dispatch sequence

For each package:

1. Confirm the supplier target is technically relevant.
2. Verify and archive a current public application-engineering/support contact route.
3. Send the controlled RFQ without inventing rotating mass, CG, bearing loads, drive torque, brake torque, stopping energy or dynamic amplification.
4. Record the actual issue date and external channel/thread reference.
5. Preserve the exact enquiry material sent.
6. On response, create a supplier-specific response JSON from the controlled template.
7. Archive supplier evidence with revision, exact-variant identity and hash where practical.
8. Complete the compliance matrix against the controlled RFQ requirements.
9. Request clarification for missing assumptions, mixed variants, untied ratings, incomplete mating data or ambiguous duty conditions.
10. Only after technical review may a response become `technically-comparable` and at most `shortlisted-not-selected`.

## Supplier-response normalization

### Exact variant identity

Family, model code and variant/configuration code must be explicit before shortlist candidacy. A generic family brochure is not an exact candidate.

### Evidence

Supplier files are logged by type, title, revision, source reference and optional SHA-256. Each item records whether it is actually bound to the exact proposed variant.

### Numeric ratings

Every rating carries:

- value
- unit
- operating/application condition
- evidence reference where the supplier claims published or calculated authority
- provenance state: supplier-published, supplier-calculated, supplier-estimate or not-provided

Published and calculated values cannot be recorded without a bound evidence reference. Estimates require an explicit operating/application condition. This prevents a catalog rating, application estimate and engineering calculation from being treated as equivalent evidence.

### Assumptions and missing inputs

Supplier assumptions remain explicit. Missing VX4800 inputs remain missing rather than being replaced with supplier guesses. If a supplier needs mass, moment, torque or stopping-energy inputs that have not been released, the correct state is clarification/input pending, not final sizing.

## Selection firewall

The response schema intentionally has no `selected` state. A response can only be:

- not selected
- candidate for shortlist
- shortlisted but not selected
- rejected

`technically-comparable` requires exact variant identity, assumptions disclosure, required submittals, variant-bound numeric ratings where applicable, completed technical review and a comparison-ready gate. `shortlisted-not-selected` additionally requires the technically-comparable state.

Final component selection remains a separate controlled engineering action after physical mass/dynamic evidence, load/fault calculations, mating/tolerance review and risk-allocation gates close. Commercial price or lead time cannot close a technical gate.

## Immediate dispatch priorities

### Bearing: ready to issue

Kaydon is contact-qualified from its current official engineering-support route. The enquiry should request required axial/radial/moment inputs, mounting-face and support-rigidity requirements, exact mating data, fastening/preload procedure, running-torque method and combined-load/life methodology. It must not ask Kaydon to infer final VX4800 loads.

Schaeffler remains an alternate crossed-roller research path until its application-engineering route is separately qualified.

### Drive: ready to issue

SEW-EURODRIVE Canada is contact-qualified from its current official Canadian support route. The enquiry should focus on candidate motor/reducer architecture for stable continuous very-low-speed operation, speed-control method, thermal behavior, output-load limits, backlash/compliance, mounting, service/manual movement and the data required for later torque-speed sizing. No exact SEW variant is selected.

### Positive transmission: ready to issue

Gates is contact-qualified from its current official Industrial Technical & Engineering Support route. The enquiry should obtain the tooth-family/width/tension selection method, minimum engagement, large-ring fabrication tolerances, alignment/runout limits, tooth-jump avoidance and resulting bearing/support reactions after a controlled torque case becomes available.

### Direct-carrier brake: ready to issue

RINGSPANN is contact-qualified from its current official North American route. The enquiry must distinguish static holding capability from dynamic stopping/energy duty and obtain exact disc/ring thickness, friction compatibility, runout/alignment, apply/release, manual-release, wear-state and mating requirements for any proposed variant.

Mayr remains an alternate research target until its current application-engineering route is separately qualified.

### Feedback: ready to issue

HEIDENHAIN is contact-qualified from its current official international-sales/application-advice route. The enquiry should focus on fixed readhead plus passive rotating scale/target architecture, very-low-speed update behavior, reference/index recovery, runout/air-gap tolerance, contamination/environment limits and options for a sufficiently diverse second channel if later required by risk assessment.

### Prototype fabrication: research still required

A fabricator must demonstrate large-ring machining, post-weld distortion control, material traceability, inspection/NDT, controlled fastener access and representative proof-load capability before this package moves to `ready-to-issue`.

## Evidence dependencies that still block final sizing

The RFQ step does not remove the known physical blockers:

- Issue #9: controlled S/M/L suspended-assembly masses and production variation
- Issue #7: suspension/dynamic response, pendulum lag, transient angles and load evidence
- Issue #11: final kinetic electrical safety-chain, brake release/control and service implementation

Until these inputs are controlled, supplier responses are useful for architecture, mating, calculation method and prototype planning, but not final product sizing.
