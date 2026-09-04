# VX4800 Radiance Photometry Validation

## Purpose

This workflow provides an independent numerical cross-check of LM-63 photometry using the Radiance lighting engine.

It does not create photometry, certify a luminaire or convert synthetic/test data into product evidence.

The raw supplier or laboratory IES remains the controlled photometric source. The AETHERIA parser and Radiance outputs are derived validation artifacts.

## Pinned toolchain

The repository pins the stable official Radiance release recorded in:

`fixtures/vx4800/photometry/radiance/toolchain-v1.json`

Current pin:

- Radiance 6.0.2
- tag `rad6R0P2`
- official Linux release archive `Radiance_c1700d56_Linux.zip`
- SHA-256 `04ee53cafbb64b943a53616b3d0ee379dd7ef80379c83aa7a145e547d9809c28`

CI verifies the archive digest before executing it.

## Independence from the AETHERIA parser

AETHERIA already parses the LM-63 numeric block in `tools/photometry/ies_lm63.py`.

The Radiance cross-check intentionally uses a separate implementation path:

1. AETHERIA reads the raw LM-63 data and candela values.
2. Radiance `ies2rad` independently converts the same raw IES into Radiance source/data files.
3. `oconv` compiles the converted source into a Radiance octree.
4. `rtrace -I` numerically samples irradiance below the source.
5. The sampled angular falloff is compared with the AETHERIA parser's source candela distribution using geometric normalization.

Agreement therefore cross-checks two separate interpretation/execution paths rather than comparing a parser with itself.

## Coordinate convention

Radiance documentation states that `ies2rad` places the generated luminaire at the origin, aimed in the negative Z direction, with the IES 0-degree plane along the X axis.

The initial VX4800 cross-check samples the first IES horizontal plane on a horizontal sensor plane below the luminaire.

For a sensor at constant vertical offset `d` and photometric angle `theta`:

- `x = d * tan(theta)`
- `y = 0`
- `z = -d`
- sensor normal = `+Z`
- source-to-sensor distance = `d / cos(theta)`
- incidence cosine on the horizontal sensor = `cos(theta)`

Therefore the expected relative irradiance is:

`E(theta) / E(0) = [I(theta) / I(0)] * cos(theta)^3`

where `I(theta)` is candela from the raw LM-63 distribution.

The comparison uses relative values, so the fixed Radiance RGB lamp weighting cancels for samples from the same converted source.

## Synthetic CI fixture

`tests/fixtures/photometry/synthetic-narrow.ies` exists only to prove that the software pipeline works.

It is explicitly labeled:

- `Synthetic AETHERIA parser fixture. NOT PRODUCT PHOTOMETRY.`
- `AETHERIA TEST ONLY`

The validator refuses synthetic provenance unless `--allow-synthetic-test` is supplied.

Even after a successful Radiance run:

- `productPhotometryEligibleForFurtherReview` remains false;
- `productPhotometryApproved` is always false;
- the report warns that the input is test-only.

The report schema structurally constrains `productPhotometryApproved` to `false` because this cross-check is only one evidence layer.

## Product photometry workflow

A real VX4800 optic can reach further review only when all of the following are true:

1. the raw IES bytes are obtained directly from the supplier or laboratory;
2. the raw file SHA-256 is controlled;
3. the exact manufacturer/model/article/optic/CCT/CRI/wattage configuration is identified;
4. the exact head/optic configuration is marked controlled;
5. the AETHERIA LM-63 parser accepts and reports the file without unresolved semantic warnings;
6. the independent Radiance cross-check passes;
7. configuration identity is independently checked against supplier documentation and, where necessary, a second photometric viewer/parser;
8. the selected physical head remains acceptable for thermal, electrical, mechanical and architectural requirements.

A Radiance pass alone does not approve the luminaire or close Issue #6.

## Command

After Radiance is installed and available on `PATH` with its library in `RAYPATH`:

```bash
python scripts/validate_radiance_photometry.py path/to/exact.ies \
  --out build/radiance-validation \
  --provenance supplier \
  --configuration-id "EXACT-MANUFACTURER-ARTICLE-OPTIC" \
  --configuration-controlled
```

For the repository synthetic test only:

```bash
python scripts/validate_radiance_photometry.py \
  tests/fixtures/photometry/synthetic-narrow.ies \
  --out _radiance_validation \
  --provenance synthetic-test \
  --allow-synthetic-test
```

## Outputs

The validator preserves useful derived artifacts in its output directory:

- copied raw IES input;
- `crosscheck.rad` from `ies2rad`;
- `crosscheck.dat` from `ies2rad`;
- `crosscheck.oct` from `oconv`;
- `radiance-validation.report.json`.

The JSON report contains:

- raw IES SHA-256 and byte length;
- provenance/configuration-control status;
- pinned and runtime Radiance identity;
- sample coordinates and normals;
- source candela values;
- expected relative irradiance;
- Radiance RGB/scalar irradiance;
- observed relative irradiance;
- per-angle and maximum relative error;
- product-authority warnings and eligibility state.

## Limitations of the initial cross-check

The initial method intentionally stays small and auditable.

It currently:

- uses the first horizontal photometric plane;
- assumes the IES source has a positive 0-degree reference candela;
- samples the default angles defined in the pinned toolchain;
- validates angular distribution rather than complete architectural illuminance;
- does not replace a second independent IES viewer/parser;
- does not validate SPD, CRI or TM-30;
- does not prove final aiming, room surfaces, butterfly optical interactions or project illuminance.

Future extensions should be added only with explicit validation and regression coverage.

## VX4800 status

The Radiance workflow is infrastructure only until exact supplier/laboratory files are controlled.

The current Precision Lighting Evo 16 and Reggiani Yori Evo Ghostrack candidates remain qualification candidates. No candidate becomes final because this workflow exists.
