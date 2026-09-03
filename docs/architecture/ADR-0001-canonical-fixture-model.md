# ADR-0001: AETHERIA owns the canonical fixture model

Status: proposed
Date: 2026-09-03

## Context

AETHERIA must interoperate with web viewers, manufacturing CAD, BIM, lighting-control formats and photometric tools. Relevant external formats include OFL fixture JSON, GDTF, MVR, IFC, STEP, DXF, glTF and IES.

No one external format represents the entire architectural sculptural-lighting product lifecycle. Making any one of them the source of truth would either lose AETHERIA-specific product information or force unrelated concepts into the product model.

## Decision

AETHERIA will maintain its own versioned canonical fixture schema.

External formats are generated or imported through adapters.

The canonical model must describe identity, physical properties, optical data, composition, kinematics, electrical/control data, materials, assets, manufacturing, compliance, interchange mappings and provenance.

## Consequences

Positive:

- one source of truth.
- no coupling to a third-party schema lifecycle.
- manufacturing and presentation data can coexist without confusing authority.
- adapters can report lossy conversions explicitly.
- future fixtures do not need to be DMX devices to exist in the catalog.

Costs:

- AETHERIA must maintain schema versions and migrations.
- exporters/importers need tests.
- the project must define authority rules between generated assets.

## External influences

- Open Fixture Library: schema governance, validation and plugin adapter architecture.
- GDTF/MVR: structured device and scene interchange.
- IFC: BIM product exchange.
- IES LM-63: measured photometric data.

## Rejected alternatives

### Use Open Fixture Library JSON directly

Rejected because its domain is entertainment-lighting fixtures and its internal format is not intended as a permanently stable third-party API.

### Use GDTF as the source of truth

Rejected because not every AETHERIA fixture is a DMX/GDTF device and GDTF does not represent the full manufacturing/compliance lifecycle.

### Use STEP/IFC as the source of truth

Rejected because geometry/BIM files are outputs, not complete product definitions.

### Keep HTML as the source of truth

Rejected because viewer code must never become the authoritative location for manufacturing dimensions, photometry or product revision data.