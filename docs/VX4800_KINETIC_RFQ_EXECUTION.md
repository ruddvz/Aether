# VX4800 Kinetic RFQ Execution and Response Intake

Status: supplier-enquiry execution control, not component selection or manufacturing release.

Fixture: AETHERIA VORTEX VX4800-BF-01  
Controlled product engineering revision: 1.3.0

## Purpose

The existing RFQ requirements define what suppliers must answer. This execution layer controls what happens before dispatch, what proves an RFQ was actually issued, how a supplier response is normalized, and what evidence is required before a response can be compared technically.

Machine-readable controls:

- `fixtures/vx4800/kinetics/qualification/rfq-requirements-v1.json`
- `fixtures/vx4800/kinetics/qualification/rfq-dispatch-register-v1.json`
- `fixtures/vx4800/kinetics/qualification/rfq-response-template-v1.json`
- `schemas/aether-kinetic-rfq-dispatch.schema.json`
- `schemas/aether-kinetic-rfq-response.schema.json`

## Current dispatch truth

No kinetic RFQ is recorded as externally issued by the repository at this stage.

The dispatch register deliberately distinguishes:

1. `repository-evidence-target`: a manufacturer already has relevant source evidence in the repository.
2. `research-required`: a supplier/fabricator category or alternate requires contact/application-engineering qualification before issue.
3. `contact-qualified`: a real external application-engineering channel has been verified and is ready for dispatch.

A researched manufacturer name is not proof of contact. `dispatchStatus=issued` requires both an issue date and an external dispatch-channel reference.

## Controlled RFQ packages

The six packages remain:

- `RFQ-KIN-BRG-01`: primary bearing / slewing or crossed-roller architecture
- `RFQ-KIN-DRV-01`: fixed motor/reducer and positive carrier drive
- `RFQ-KIN-BELT-01`: synchronous belt / toothed carrier-ring transmission
- `RFQ-KIN-BRK-01`: direct-carrier power-off holding/fault brake
- `RFQ-KIN-FBK-01`: fixed-side position/speed feedback with passive rotating target
- `RFQ-KIN-FAB-01`: prototype structural hub/support, service-lock and secondary-retention fabrication

## Dispatch sequence

For each package:

1. Confirm the supplier target is technically relevant to the package.
2. Verify the current application-engineering contact or formal enquiry channel.
3. Send the controlled package without inventing the missing rotating mass, CG, bearing loads, drive torque, brake torque or dynamic amplification.
4. Record the issue date and external channel/thread reference.
5. Preserve the exact material sent so later supplier assumptions can be audited against it.
6. On response, create a supplier-specific response JSON from the controlled template.
7. Archive supplier evidence with revision/variant identity and hash where practical.
8. Complete the compliance matrix against the original requiredSupplierResponse entries.
9. Request clarification for missing assumptions, mixed variants, untied ratings, incomplete mating data or ambiguous duty conditions.
10. Only after technical review may the response become `technically-comparable` and at most `shortlisted-not-selected`.

## Supplier-response normalization

Every response record separates four things that supplier correspondence often mixes together:

### Exact variant identity

Family, model code and variant/configuration code must be explicit before shortlist candidacy. A generic family brochure does not identify the proposed product.

### Evidence

Supplier files are logged by type, title, revision, source reference and optional SHA-256. The reviewer records whether each item is actually bound to the exact proposed variant.

### Numeric ratings

Every rating is stored with:

- value
- unit
- operating/application condition
- evidence reference
- provenance state: supplier-published, supplier-calculated, supplier-estimate or not-provided

This prevents a catalog number, application estimate and engineering calculation from being treated as equivalent evidence.

### Assumptions and missing inputs

Supplier assumptions must be preserved explicitly. Missing VX4800 inputs remain missing rather than being replaced by supplier guesses. If a supplier needs a mass, moment, torque or stopping-energy input that has not yet been released, the correct response state is clarification/input pending, not final sizing.

## Selection firewall

The RFQ response schema intentionally has no `selected` state.

A response can be:

- not selected
- candidate for shortlist
- shortlisted but not selected
- rejected

Final component selection remains a separate controlled engineering action after the required physical mass/dynamic evidence, load/fault calculations, mating/tolerance review and risk-allocation gates are closed.

Commercial price or lead time never closes a technical gate.

## Immediate dispatch priorities

### Bearing

Repository evidence supports contacting Kaydon as a current bearing target. A crossed-roller application-engineering route remains to be qualified as an alternate study path. The first enquiry should focus on required design inputs, mounting-face/rigidity requirements, exact mating data and the supplier's combined-load/torque methodology rather than asking for a final bearing size from incomplete loads.

### Positive transmission

Repository evidence supports Gates as the current synchronous-transmission target. The enquiry should obtain the method for tooth-family/width/tension selection, large-ring fabrication tolerances, alignment/runout requirements and resulting bearing/support reactions after the controlled torque case becomes available.

### Direct-carrier brake

Repository evidence supports RINGSPANN as a current fail-safe caliper target; Mayr remains an alternate research target. The supplier must explicitly distinguish static holding capability from dynamic stopping/energy duty and provide exact disc/ring mating requirements for any proposed variant.

### Feedback

Repository evidence supports HEIDENHAIN as the current modular feedback target. The enquiry should focus on fixed readhead/passive rotating scale options, very-low-speed update behavior, index/reference recovery, runout/air-gap tolerance and a possible diverse channel without powered rotating electronics.

### Drive and fabrication

These packages are not yet attached to a qualified target. The next research step is application-engineering supplier qualification for a low-speed fixed-side gearmotor/reducer and precision prototype fabricators capable of large-ring machining, controlled distortion, measurement/NDT and proof-load work.

## Evidence dependencies that still block final sizing

The RFQ step does not remove the known physical blockers:

- Issue #9: controlled S/M/L suspended-assembly masses and production variation
- Issue #7: suspension/dynamic response, pendulum lag, transient angles and load evidence
- Issue #11: final kinetic electrical safety-chain, brake release/control and service implementation

Until these inputs are controlled, supplier responses are useful for architecture, mating, calculation-method and prototype planning, but not final product sizing.
