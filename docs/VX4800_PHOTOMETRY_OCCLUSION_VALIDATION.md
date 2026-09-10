# VX4800 L2 photometry occlusion validation

## Purpose

This layer evaluates direct-path obstruction and attenuation between the 14 fixed VX4800 light heads and controlled photometric sensors.

It sits downstream of the L1 direct-light system validator in `scripts/validate_vx4800_photometry_system.py`.

L2 answers a narrower question than full optical simulation:

> For a reviewed obstruction model, which direct head-to-sensor rays intersect which obstruction objects, and what direct-light attenuation follows from the released object-level assumptions?

It does **not** model architectural interreflection, transparent-glass refraction, caustics, wavelength-dependent transmission, glare, or commissioning tolerance. Those remain separate evidence layers.

## Executable validator

`scripts/validate_vx4800_photometry_occlusion.py`:

- binds a specific L1 system scene by path and SHA-256;
- re-runs L1 rather than trusting a stale derived report;
- evaluates every one of the 14 head-to-sensor direct paths;
- represents obstruction geometry as named objects containing triangle meshes;
- uses open-segment Möller–Trumbore ray/triangle intersection;
- excludes intersections exactly at source or sensor endpoints;
- applies each intersected object's direct-transmission factor once per source-to-sensor path;
- records the obstruction identities hit by every head/sensor ray;
- records baseline and attenuated per-head contributions;
- reports baseline lux, occluded lux, lost lux, and loss fraction per sensor; and
- evaluates released per-sensor L2 criteria when controlled criteria exist.

## Object grouping

Triangles belong to an obstruction object.

This matters because a physical surface represented by two or more triangles is still one obstruction object. Its transmission factor is applied once when the ray intersects that object.

The implementation therefore does **not** multiply attenuation once per triangle. This avoids mesh tessellation changing the photometric result.

Example:

```json
{
  "objectId": "FIXED-CANOPY-01",
  "category": "canopy",
  "directTransmissionFactor": 0.0,
  "triangles": [
    [[0,0,0],[1,0,0],[1,1,0]],
    [[0,0,0],[1,1,0],[0,1,0]]
  ]
}
```

A ray crossing either or both triangles is blocked by `FIXED-CANOPY-01` once.

## Direct-transmission factor

`directTransmissionFactor` is bounded from 0 to 1.

- `0.0` means no direct flux from that source reaches the sensor through the object in this simplified L2 model.
- `1.0` means the object does not attenuate that direct path.
- intermediate values are permitted only when a controlled engineering/optical assumption supports them.

The factor is a scalar engineering simplification, not a glass shader.

It does not inherently model:

- refraction;
- Fresnel effects;
- multiple internal reflections;
- angular transmission;
- wavelength dependence;
- scattering;
- caustics; or
- polarization.

Transparent or faceted butterfly materials may therefore require a more complete optical treatment before their contribution can close the real L2 product gate.

## Geometry authority

A geometry file being convenient to load does not make it valid L2 evidence.

The following are **not automatically controlled obstruction geometry**:

- Blender visualization geometry;
- presentation geometry;
- coordination GLB;
- repository coordination STEP/DXF;
- simplified marketing meshes; or
- screenshots/renders.

A controlled L2 model requires reviewed obstruction geometry with traceable source references and SHA-256 identities.

The source may ultimately be a reviewed derivative of manufacturing geometry, but that promotion must be explicit.

## Synthetic CI model

`tests/fixtures/photometry/vx4800-occlusion-synthetic.json` is software-test-only.

It binds the synthetic L1 system scene and places one oversized opaque plane halfway between all heads and the 3×3 sensor grid.

Expected result:

- 14 heads × 9 sensors = 126 head-to-sensor paths;
- every path intersects the synthetic object;
- baseline direct illuminance is positive;
- attenuated direct illuminance is zero;
- loss fraction is 1.0 at every sensor;
- `pipelinePass = true`; but
- `controlledInputsReady = false`;
- `occlusionAssessmentCompleted = false`; and
- `productPhotometryApproved = false`.

This provides a strong deterministic software oracle without pretending the plane represents VORTEX.

## Controlled L2 promotion requirements

`occlusionAssessmentCompleted` may become true only when all required upstream and L2 controls are satisfied.

At minimum:

1. The bound L1 system scene must pass as a controlled `direct-layer-pass`.
2. Exact role-set/source evidence must already be controlled through the L1 chain.
3. Obstruction geometry must be released/reviewed for the stated L2 purpose.
4. Every controlled obstruction object must carry a traceable source reference and source SHA-256.
5. Direct-transmission assumptions must be controlled.
6. The obstruction model must explicitly state that coverage is complete for the L2 scope.
7. L2 acceptance criteria must be released before result evaluation.
8. Every released L2 criterion must pass.

Changing the model authority/status labels cannot bypass the L1 requirement.

## L2 acceptance criteria

The repository does not invent generic occlusion limits.

Controlled criteria may later include, where justified:

- maximum direct-light loss fraction at named sensors;
- minimum attenuated illuminance at named sensors;
- required clear optical paths;
- permissible shadowing on named target surfaces; and
- project-specific constraints on sculpture/canopy blockage.

Criteria must be released before they are used to claim pass/fail.

## Relationship to later validation layers

### L3 — reflectance/interreflection

L3 evaluates indirect light and requires controlled surface/material reflectance assumptions and a controlled scene.

L2 direct transmission is not an interreflection model.

### L4 — aim/setout tolerance sensitivity

L4 perturbs released construction and commissioning tolerances.

An ideal nominal L2 result does not demonstrate robustness to installation variation.

### Site commissioning

Where the released project plan requires field photometric checks, simulation remains predictive/engineering evidence and must be correlated with as-installed measurements.

## Product authority boundary

The L2 report always keeps these false in the current implementation:

```json
{
  "reflectanceAssessmentCompletedWhereRequired": false,
  "toleranceSensitivityValidated": false,
  "full14HeadPhotometricValidationCompleted": false,
  "applicationPerformanceValidated": false,
  "productPhotometryApproved": false
}
```

There is no CLI override for those flags.

## Commands

Synthetic L2 pipeline check:

```bash
python scripts/validate_vx4800_photometry_occlusion.py \
  tests/fixtures/photometry/vx4800-occlusion-synthetic.json \
  --output _radiance_validation/occlusion-validation.report.json
```

Future controlled study:

```bash
python scripts/validate_vx4800_photometry_occlusion.py \
  <controlled-occlusion-model.json> \
  --output <controlled-occlusion-report.json>
```

A zero exit code means the L2 software/input-integrity pipeline completed successfully. It does not by itself mean that product occlusion, application performance, or product photometry is approved.
