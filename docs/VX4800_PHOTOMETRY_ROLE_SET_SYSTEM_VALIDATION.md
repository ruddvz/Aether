# VX4800 photometry role set and system-validation gate

## Purpose

The exact-configuration evidence package validates one specific lighting-head configuration at a time.

VX4800 uses three optical roles across 14 fixed head positions, so product-level lighting review must also verify that the complete selected role set maps correctly to the engineering design before any full-system simulation or application-performance assessment begins.

This layer performs that binding.

## Controlled product mapping

The current controlled photometry selection brief defines:

| Role | Quantity | Target beam | Current acceptable research range |
| --- | ---: | ---: | ---: |
| deep-tail narrow | 4 | 5° | 3–7° |
| mid-field spot | 6 | 15° | 10–20° |
| upper-field flood | 4 | 30° | 24–36° |

Total: **14 fixed heads**.

The first controlled photometry package remains **3000 K**.

These values are bound to:

- `fixtures/vx4800/photometry/selection-brief.json`; and
- the controlled engineering LED setout referenced by `led-setout-engineering-1.3.0` in `fixture.json`.

## Required input packages

The role-set assembler requires exactly one eligible exact-configuration evidence package for each role:

1. deep-tail narrow;
2. mid-field spot;
3. upper-field flood.

Each package must already have passed the angular + spectral consistency gates described in `VX4800_EXACT_PHOTOMETRY_EVIDENCE_PACKAGE.md`.

## System-input checks

The role set can become `eligible-for-system-validation` only when:

- all three required roles are present exactly once;
- quantities remain exactly 4 / 6 / 4;
- total quantity remains exactly 14;
- all three exact packages are eligible for further review;
- each package role matches the slot in which it is used;
- all packages match the controlled 3000 K first-package target;
- the three exact configuration IDs are distinct;
- the controlled selection brief and engineering LED-setout identities are recorded.

A failed check makes the role set `incomplete`.

## Manufacturer-family preference

The selection brief says to **prefer** one manufacturer family providing sibling narrow/spot/flood optics.

That preference helps:

- visual consistency;
- driver/control compatibility;
- finish consistency;
- spare-part simplification;
- supplier coordination.

It is not currently a mandatory engineering requirement.

The role-set output therefore records `singleManufacturerFamily`, but does not fail solely because the three controlled configurations come from more than one family. If AETHERIA later decides that one-family architecture is mandatory, that requirement must be released explicitly rather than inferred from the word “prefer.”

## What this layer does not validate

An eligible role set does **not** demonstrate that the installed 14-head lighting design performs acceptably.

It does not yet validate:

- illuminance on project surfaces;
- peak/minimum/average ratios;
- overlap between the 14 beams;
- spill light;
- glare or source visibility;
- interaction with the butterfly field;
- shadowing/occlusion from the sculpture;
- scene materials/reflectances;
- aiming tolerances;
- project ceiling height and target geometry;
- final dimming/scene levels;
- thermal/electrical compatibility of the three selected configurations;
- occupied-space visual comfort.

Those belong to the next **full 14-head photometric system-validation** stage.

## Approval boundary

The role-set schema intentionally hard-codes:

```json
{
  "full14HeadPhotometricValidationCompleted": false,
  "applicationPerformanceValidated": false,
  "productPhotometryApproved": false
}
```

There is no command-line switch to override those values.

`eligible-for-system-validation` means only that the evidence inputs are coherent enough to build the next controlled study.

## Command

Once all three exact evidence packages exist:

```bash
python scripts/assemble_vx4800_photometry_role_set.py \
  --narrow <deep-tail-narrow-package.json> \
  --spot <mid-field-spot-package.json> \
  --flood <upper-field-flood-package.json> \
  --output <vx4800-role-set.json>
```

Exit status:

- `0`: coherent role set eligible for full-system validation;
- `2`: incomplete role set.

## Next system-validation stage

The subsequent stage should consume:

- the role-set manifest;
- the controlled 14-head XY setout;
- exact IES/LDT distributions already referenced by the three packages;
- controlled aiming definitions;
- a controlled architectural test scene or project geometry;
- controlled surface reflectances/material assumptions;
- explicitly released acceptance criteria.

Radiance is appropriate for the independent numerical workflow, but a simulation is only as authoritative as its source photometry, geometry, aiming, material assumptions and acceptance criteria.

No synthetic IES, presentation-light positions or Blender-only lighting rig may close the product photometry gate.

## Current status

No real role set is yet eligible because Issue #6 still lacks the exact supplier/laboratory source evidence required to create the three exact configuration packages.
