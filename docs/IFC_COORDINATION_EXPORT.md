# VX4800 IFC4 coordination export

The VX4800 IFC adapter produces a **coordination-only** IFC4 model from the canonical AETHERIA fixture record. It is intentionally smaller and less authoritative than manufacturing CAD or project structural documentation.

## Toolchain

The exporter targets IfcOpenShell 0.8.5 through `requirements-interchange.txt` and is validated in a dedicated GitHub Actions workflow. The normal repository validation remains independent from the heavier IFC dependency.

## Output

The exporter creates:

- one `IfcProject`;
- one `IfcSite`;
- one `IfcBuilding`;
- one `IfcBuildingStorey` representing the mounting datum context;
- one `IfcLightFixture` occurrence for `VX4800-BF-01`;
- one simple body representation of the controlled overall coordination envelope;
- AETHERIA property sets for controlled identity/count metadata, explicit authority boundaries and released limitations;
- the companion IFC loss report generated from the interchange policy.

The IFC model is not a 240-object fabrication assembly. The authoritative 240-row engineering schedule remains in the controlled repository source and is not silently flattened into a collection of BIM objects in this baseline.

## Coordinate mapping

The canonical product schedule uses ceiling XY and drop-positive-down coordinates.

The IFC coordination model uses a conventional +Z-up coordinate system:

- canopy underside datum: `Z = 0`;
- controlled overall envelope centred in X/Y;
- fixture drop extends in negative Z;
- current coordination envelope: 2500 × 1650 × 4800 mm.

This mapping is a BIM coordination convention only. It does not redefine controlled manufacturing coordinates.

## Geometry authority

The body representation is a bounding coordination proxy generated from `physical.envelopeMm`.

It is useful for:

- gross spatial coordination;
- ceiling-zone planning;
- clash-screening context;
- product identification in BIM review;
- communicating the maximum product envelope.

It is not suitable for:

- fabrication;
- hole or attachment layout;
- bearing/carrier design;
- cable termination detail;
- butterfly fabrication;
- structural load derivation;
- clearance certification based on individual moving elements.

The model property `GeometryAuthority` remains `coordination-only`.

## Property sets

`AETHERIA_Coordination` carries released or explicitly bounded metadata including:

- fixture/product identity;
- design and presentation revisions;
- lifecycle state;
- export and geometry authority;
- 240 controlled elements;
- 66 S / 144 M / 30 L family counts;
- 240 suspension lines;
- 14 fixed lighting heads;
- 4800 mm maximum drop;
- unresolved mass status;
- conceptual motion and optical status.

`AETHERIA_AuthorityBoundary` hard-codes false values for:

- manufacturing authority;
- structural authority;
- photometry authority;
- kinetic-safety authority;
- construction-release authority.

It also binds the IFC to the SHA-256 of the canonical fixture used to generate the companion loss report.

`AETHERIA_Limitations` carries the controlled product limitations into the BIM file so downstream users do not need to infer unresolved status from missing geometry alone.

## Deliberately omitted information

The exporter does not invent or infer:

- installed mass or centre of gravity;
- site reactions or anchor loads;
- bearing or drive ratings;
- braking torque or stopping energy;
- dynamic amplification or cable motion;
- final secondary retention;
- exact selected lighting-head models;
- approved IES/LDT or spectral evidence;
- final per-head aiming;
- fabrication geometry.

Those values remain in their own engineering/qualification domains and should enter IFC only after controlled release.

## Build command

Install the pinned interchange dependency and export:

```bash
python -m pip install -r requirements-dev.txt -r requirements-interchange.txt
python scripts/export_vx4800_ifc.py
```

Default outputs:

```text
build/vx4800/interchange/VX4800-BF-01.ifc
build/vx4800/interchange/ifc-loss-report.json
```

## Validation

`.github/workflows/ifc.yml` provides an independent IFC gate. It:

1. installs the pinned IfcOpenShell version;
2. runs the IFC and loss-report regression tests;
3. generates the IFC4 file;
4. reopens the file with IfcOpenShell;
5. verifies fixture identity, controlled counts, source SHA binding and authority flags;
6. uploads the IFC and companion loss report as validation artifacts.

The test suite also verifies the 2500 × 1650 × 4800 mm proxy extents and stable primary entity/property-set GUIDs across rebuilds.

A successful IFC workflow means the coordination adapter is internally consistent and parseable. It does not constitute construction, manufacturing, structural, photometric or kinetic approval.
