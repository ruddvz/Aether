# VX4800 implementation recovery state

Date: 2026-09-03
Branch: `aetheria/vx4800-photometry-platform-20260903`

## Why this branch exists

The verified local AETHERIA/VORTEX platform implementation progressed beyond the current GitHub `main` branch while GitHub write access was unavailable. This branch records the recovery point before source expansion so nobody mistakes `main` for the current implementation authority.

Do not merge this branch as a complete platform implementation until the verified source snapshot has been expanded into normal repository files and CI has passed on GitHub.

## Verified local platform state

- Fixture: VX4800-BF-01
- Canonical engineering design revision: 1.3.0
- Presentation revision: 5.2.0
- Engineering elements: 240
- Engineering S/M/L allocation: 66 / 144 / 30
- Presentation S/M/L allocation: 54 / 132 / 54
- Maximum controlled lower edge: 4778 mm
- Fixed engineering LED-head positions: 14
- Repository CAD authority: coordination only
- Manufacturing geometry remains external controlled authority

## Deterministic outputs

Coordination GLB SHA-256:

`6b9b95ed29de42d366cc406d36b476d7402ee2508e31757a5a473e60f15f091d`

V5.2 controlled release SHA-256:

`4cffd5a003a718d359811bf6f3b406d8ad197a92cc3632f9321c6859dca48f79`

The release remained byte-identical after the supplier-research integration slice.

## Photometry/platform implementation already present locally

- controlled LM-63 `TILT=NONE` ingestion
- raw IES byte preservation and SHA-256 provenance
- parsed IES report schema
- peak-candela detection
- conservative FWHM/field-angle review estimate
- normalized polar SVG generation
- synthetic IES test fixtures isolated from product photometry
- VX4800 lighting-head selection brief
- strict machine-readable candidate schema and evaluator
- deterministic coordination GLB with 240 butterfly nodes, 240 cable nodes and 14 fixed LED-head nodes
- public schema, fixture and GLB route generation
- split V5.2 development source with generated single-file release

## Supplier research integration completed in continuation slice

Five real supplier records are now represented locally without fabricated unknown values:

1. Precision Lighting by Luminii, Evo 16
2. Reggiani, Yori Evo Ghostrack 1X - 43 mm
3. ERCO, Eclipse 48V XS
4. formalighting, Zero 40 Low Voltage
5. KIT Concept, A90D-5L

Unknown exact article, optic, CCT, CRI, driver or photometry fields are stored as `null` rather than placeholder values.

Strict evaluator result:

| Candidate | Decision | Blockers | Warnings | Passes |
| --- | --- | ---: | ---: | ---: |
| Precision Evo 16 | reject-for-now | 1 | 4 | 16 |
| ERCO Eclipse 48V XS | reject-for-now | 8 | 9 | 13 |
| formalighting Zero 40 LV | reject-for-now | 9 | 8 | 12 |
| KIT Concept A90D-5L | reject-for-now | 8 | 9 | 13 |
| Reggiani Yori Evo Ghostrack 43 | reject-for-now | 15 | 12 | 7 |

`reject-for-now` means controlled product photometry cannot be promoted yet. It does not mean the supplier family is commercially rejected.

Precision is currently closest to technical qualification. Official manufacturer IES links are known, but no raw IES file is marked downloaded, parsed or verified because exact configuration identity and raw bytes have not yet been controlled.

## Measured browser-distribution adapter

A renderer-neutral measured-distribution adapter is implemented locally and tested. It requires:

- candidate photometry status `parsed` or `verified`;
- candidate SHA-256 exactly matching the parsed LM-63 report;
- supplier or laboratory provenance for product use;
- `TILT=NONE`;
- a single horizontal plane for the first 1D adapter.

Multi-plane photometry is rejected instead of being silently reduced to one plane.

V5.2 is intentionally not wired to measured photometry yet. It remains a WebGL conceptual-lighting presentation. Moving to native Three.js IES lighting would be a separate renderer/viewer architecture decision.

## Verification after continuation slice

- repository validation: PASS
- engineering geometry QA: PASS
- web geometry QA: PASS
- pytest: 19 / 19 PASS
- viewer JavaScript syntax: PASS
- measured adapter JavaScript syntax: PASS
- V5.2 release rebuild: byte-identical to the prior controlled release

## Current blocker

The next authority promotion requires raw official supplier/laboratory photometry for exact 3000K configurations. Marketing beam angles and family-level files are not sufficient.

## Recovery rule

The verified local source snapshot remains the implementation handoff until its files are expanded onto this branch and GitHub CI reproduces the local validation results. Do not reconstruct missing source from this summary alone.