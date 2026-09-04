# Photometry pipeline

Current VORTEX lighting is `conceptual`. The fourteen presentation heads and their WebGL intensities are composition tools, not photometric test data.

## Design rule

The raw supplier or laboratory photometry file is the controlled evidence. Parsed JSON, plots and browser textures are derived artifacts.

AETHERIA never generates a fake `.ies` file from Three.js lights, marketing beam angles, lumen claims or screenshots.

## Status ladder

1. `conceptual` - current V5.2 visual lighting only.
2. `supplier-data` - exact supplier configuration and untouched photometry received.
3. `simulated` - controlled photometry used in a documented simulation.
4. `tested` - physical test evidence linked to the exact fixture configuration.

A product does not move upward automatically. Promotion is an engineering/release decision.

## Candidate research

The controlled research brief is:

`fixtures/vx4800/photometry/selection-brief.json`

Candidate records use:

`schemas/aether-photometry-candidate.schema.json`

Do not record only a product family. Record the exact LED/CCT/optic configuration, driver and source URLs. Prefer one architectural head family offering narrow, spot and flood optics.

## Raw IES ingestion

The initial AETHERIA LM-63 ingestor is intentionally small and dependency-free. It:

- preserves the raw source file byte-for-byte.
- records SHA-256 and byte length.
- parses LM-63 numeric photometry with `TILT=NONE`.
- records vertical and horizontal angles.
- preserves candela arrays after the LM-63 multiplier.
- identifies peak candela and its angular position.
- generates a conservative FWHM/field-angle estimate from the first horizontal plane for review only.
- creates a normalized SVG polar diagram.
- refuses unsupported TILT data rather than silently misinterpreting it.

Example:

```bash
python scripts/ingest_ies.py vendor-head-3000k-5deg.ies \
  --out fixtures/vx4800/photometry/measured/vendor-head-5deg \
  --provenance supplier \
  --manufacturer "Manufacturer" \
  --model "Exact model and optic code" \
  --source-url "https://manufacturer.example/product" \
  --received-at "2026-09-03T18:00:00Z"
```

Outputs:

- untouched `.ies` source.
- `.report.json` validated against `aether-ies-report.schema.json`.
- `.polar.svg` review plot.

## Independent verification

The in-repo parser is not intended to become a substitute for professional photometric software. Before approving product photometry:

1. compare the parsed distribution against the manufacturer's own polar/photometric documentation.
2. cross-check the file using an independent parser/viewer such as the MIT `iesna` project or an established lighting application.
3. use the exact file in the selected lighting simulation workflow.
4. retain original supplier/lab provenance.

## Controlled progression

1. Select a real luminaire/head and driver.
2. Acquire supplier or laboratory LM-63 IES data for the exact configuration.
3. Store the untouched IES file as a controlled asset with SHA-256.
4. Parse and validate metadata/distribution.
5. Generate polar/summary reports.
6. Use the distribution in the browser where supported, with a documented fallback.
7. Validate critical room/application studies in an offline lighting engine such as Radiance.
8. Add SPD data where available and calculate color-quality metrics using Colour.

## What is intentionally not calculated yet

The first ingestor does not claim:

- room lux.
- UGR.
- total fixture lumens derived from integration.
- TM-30.
- CRI.
- spectral metrics.
- physical thermal performance.

Those require the right source data and separate validated calculations.

## Measured browser-distribution adapter

The next browser step is implemented as a deliberately dormant, renderer-neutral adapter:

`tools/web/measured-photometry-adapter.mjs`

It accepts only a candidate configuration already marked `parsed` or `verified` plus a parsed LM-63 report whose SHA-256 exactly matches the candidate record. Product use rejects synthetic/unknown provenance, unsupported TILT data and multi-plane distributions that the first 1D adapter cannot represent without approximation.

The first adapter produces a normalized angular lookup table from a single controlled horizontal plane. It does not calculate lux, replace Radiance/DIALux/Relux, or promote a candidate to approved status.

### Why V5.2 is not wired to it yet

V5.2 deliberately remains on `THREE.WebGLRenderer` and conceptual `THREE.SpotLight` cones. Current Three.js provides `IESLoader` and `IESSpotLight`, but `IESSpotLight` is documented for `WebGPURenderer`. Changing the renderer or silently approximating multi-plane IES data would be a material viewer architecture change.

Therefore this release does **not** change V5.2 output. The measured adapter is a controlled bridge for the next presentation revision after exact supplier/laboratory IES files are received and independently checked.

A future viewer integration must choose explicitly between:

1. a WebGPU/TSL path using native Three.js IES support, with browser fallback testing; or
2. a documented WebGL-compatible shader/texture path that consumes the same controlled lookup data without changing photometric authority.

Neither path may infer measured data from the current conceptual cone angles.
