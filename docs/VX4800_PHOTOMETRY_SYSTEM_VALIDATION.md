# VX4800 14-head photometry system validation

## Purpose

This layer validates the complete fixed 14-head AETHERIA VORTEX lighting arrangement after exact narrow / spot / flood source evidence becomes controlled.

It sits downstream of:

1. controlled raw LM-63 ingestion;
2. independent per-source Radiance cross-check;
3. controlled SPD / colour-quality review;
4. exact angular + spectral configuration evidence packages; and
5. the three-role 4 / 6 / 4 role-set gate.

It does **not** replace those layers and does not make synthetic data product evidence.

## Current implementation scope

The first executable system layer is **L1 — direct-light distribution**.

`scripts/validate_vx4800_photometry_system.py`:

- verifies the controlled 14-head engineering XY setout by SHA-256 and coordinates;
- requires exactly 14 head identities `LED-01` through `LED-14`;
- requires the controlled role quantities:
  - 4 deep-tail narrow;
  - 6 mid-field spot;
  - 4 upper-field flood;
- binds exactly one LM-63 source to each role;
- verifies source SHA-256 values;
- supports LM-63 Type C sources only in this initial system layer;
- interpolates vertical and horizontal candela values;
- applies explicit per-head aim direction and C0-reference roll;
- evaluates each head independently at each sensor;
- applies inverse-square distance and sensor-plane incidence cosine;
- records all 14 contributions for every sensor;
- evaluates released per-sensor minimum / maximum lux criteria when they exist; and
- produces a machine-readable validation report.

The independent Radiance workflow remains upstream evidence that the AETHERIA parser's angular distribution agrees with a separate established photometric toolchain. The L1 system aggregation does not claim to be a second independent LM-63 parser.

## Coordinate convention

The scene uses:

- x/y: ceiling-plane coordinates in metres;
- z: positive downward;
- engineering LED XY positions: converted directly from `led-setout-engineering-v1.3.0.csv`;
- `aimDirection`: unit direction from the head into the scene;
- `rollDeg`: rotation of the source C0 reference plane about the aim axis;
- sensor `normal`: normal pointing toward the side of the sensor that receives light.

A head with:

```json
{
  "aimDirection": [0, 0, 1],
  "rollDeg": 0
}
```

points vertically downward.

A horizontal receiving plane below the fixture uses:

```json
{"normal": [0, 0, -1]}
```

## Direct illuminance calculation

For each head/sensor pair, the validator determines the source vertical/horizontal angles in the head's local Type-C frame, interpolates candela, and computes:

`E = I × outputScale × cos(incidence) / distance²`

where:

- `E` is direct illuminance in lux;
- `I` is interpolated source intensity in candela;
- `outputScale` is a 0…1 source-output multiplier;
- `cos(incidence)` is the receiving-plane incidence factor; and
- `distance` is head-to-sensor distance in metres.

This layer deliberately contains no interreflection term.

## Initial LM-63 limitations

The system validator intentionally fails rather than silently approximating unsupported source data.

Initial system review accepts:

- LM-63 Type C photometry;
- a single horizontal plane where the source is represented as rotational/single-plane for the required calculation;
- reviewed 0…90 quadrant coverage;
- reviewed 0…180 bilateral coverage; or
- reviewed full 0…360 coverage.

Other source conventions must be explicitly reviewed and implemented before use.

`TILT` handling remains governed by the core AETHERIA LM-63 parser; unsupported tilt data cannot be promoted by this system layer.

## Synthetic CI scene

`tests/fixtures/photometry/vx4800-system-synthetic.json` exists only to prove the software path.

It uses:

- the real controlled 14-head XY positions;
- a synthetic 4 / 6 / 4 role mapping;
- the existing synthetic narrow IES for all three role sources;
- synthetic straight-down aiming;
- a synthetic 3 × 3 sensor plane; and
- no released acceptance criteria.

Therefore a successful CI execution may report:

- `pipelinePass = true`

but must report:

- `controlledInputsReady = false`;
- `directDistributionValidated = false`;
- `full14HeadPhotometricValidationCompleted = false`;
- `applicationPerformanceValidated = false`; and
- `productPhotometryApproved = false`.

This is an intentional authority boundary, not an incomplete test.

## Controlled L1 promotion requirements

A controlled direct-distribution study may reach `direct-layer-pass` only when all of the following are true:

- the scene is explicitly a controlled system-review input;
- the exact eligible three-role evidence set is bound by path and SHA-256;
- each scene IES source matches the exact source hash in its evidence package;
- every source has supplier or laboratory provenance and is non-synthetic;
- the 14 engineering head positions match the controlled setout;
- the 4 / 6 / 4 role mapping is controlled;
- all 14 aim directions / roll values are controlled;
- sensor locations / normals are controlled;
- acceptance criteria are released; and
- all released L1 criteria pass.

Changing labels in a JSON file is insufficient. The role-set and exact evidence-package hash chain is checked.

## Layers not yet closed by L1

A direct-layer pass does **not** close full system validation.

The following remain separate evidence layers:

### L2 — fixture / sculpture occlusion

Include reviewed obstruction geometry for the canopy, relevant suspended field, and other fixed elements that can shadow or block the 14 sources.

Coordination or presentation geometry must not be silently treated as manufacturing truth.

### L3 — architectural reflectance / interreflection

Requires a controlled project or test scene and documented reflectance/material assumptions.

Blender shader parameters are not photometric reflectance evidence.

### L4 — aiming / construction tolerance sensitivity

Requires released commissioning and construction tolerances. The study must perturb controlled tolerances, not arbitrary values chosen to make a robustness plot.

### Application / occupied-space review

Project-specific glare, source visibility, spill, user viewpoints, dimming scenes, target surfaces and visual-comfort criteria require an explicit released method.

## Acceptance criteria

The repository intentionally does not invent generic lux targets for this sculptural product.

Project or controlled test-scene criteria must be released before a pass/fail claim is permitted. Criteria may later include, where appropriate:

- minimum / maximum / average illuminance on named surfaces;
- uniformity or contrast relationships;
- required beam coverage;
- spill limits;
- glare/source-visibility metrics;
- sculpture-light interaction;
- sensitivity to aim and installation tolerances; and
- correlation with site commissioning measurements.

The acceptance criteria must be traceable to the intended application rather than chosen after seeing the result.

## Product approval boundary

The system report schema hard-codes the following as false in this L1 implementation:

```json
{
  "occlusionAssessmentCompleted": false,
  "reflectanceAssessmentCompletedWhereRequired": false,
  "toleranceSensitivityValidated": false,
  "full14HeadPhotometricValidationCompleted": false,
  "applicationPerformanceValidated": false,
  "productPhotometryApproved": false
}
```

No CLI option can override those values.

Product photometry remains blocked until the complete controlled evidence chain is reviewed and explicitly released.

## Command

Synthetic pipeline check:

```bash
python scripts/validate_vx4800_photometry_system.py \
  tests/fixtures/photometry/vx4800-system-synthetic.json \
  --output _radiance_validation/system-validation.report.json
```

Future controlled study:

```bash
python scripts/validate_vx4800_photometry_system.py \
  <controlled-system-scene.json> \
  --output <controlled-system-report.json>
```

A command returning success means the software/input integrity checks passed. It does not by itself mean the product lighting is approved.
