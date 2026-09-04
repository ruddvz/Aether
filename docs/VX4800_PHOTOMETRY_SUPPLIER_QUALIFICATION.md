# VX4800 photometry supplier qualification

Date: 2026-09-04

This document turns the existing luminaire research into a controlled supplier-qualification step. It does not approve a final head.

## Current shortlist

Two finalists are retained for different reasons.

### Precision Lighting by Luminii - Evo 16

Role: photometric-data reference finalist.

Strengths:

- current manufacturer product data publishes 3000K and CRI 90+;
- required optical roles are covered by published 6 degree, 16 degree and 30 degree options;
- DALI is published;
- premium brass and dark finishes are available;
- official IES download links are published for the relevant beam families.

Constraint:

- 65.8 mm aperture exceeds the preferred 45 mm compact-head target.

Supplier return required before promotion:

1. Confirm exact current order codes for the 3000K narrow, medium and flood configurations.
2. Confirm that the manufacturer IES files `G2490.334.314-06.IES`, `G2490.334.314-15.IES` and `G2490.334.314-30.IES` map to those exact current configurations.
3. Resolve the published 16 degree medium optic versus `-15` IES filename discrepancy.
4. Provide the three raw LM-63 files directly or through a stable manufacturer source.
5. Confirm exact DALI/DALI-2 power-supply architecture, driver model and allowable head count for a 14-head installation.
6. Confirm current dimensions for the selected snoot/configuration.

### Reggiani - Yori Evo Ghostrack 43 mm

Role: physical-fit finalist.

Strengths:

- 43 mm head size fits the preferred compact visual target;
- current family information publishes 3000K and DALI;
- current family information publishes high-CRI options including >95 and >98;
- special finishes are available;
- manufacturer family pages expose photometry resources.

Supplier return required before promotion:

1. Provide exact current 43 mm article numbers for the closest fixed narrow, approximately 15 degree and approximately 30 degree optics at 3000K.
2. Confirm exact CRI, wattage, delivered lumens and driver/control configuration for each article.
3. Confirm whether a 3 to 7 degree current fixed optic exists in the 43 mm family. If not, provide the narrowest current fixed optic.
4. Provide exact configuration-matched IES or LDT files for all three roles.
5. Confirm dark bronze, antiqued bronze, brushed brass or similar finish availability for the exact articles.

## Required evidence chain

A candidate may not enter controlled product photometry until all of the following are true:

1. exact manufacturer configuration is identified;
2. exact LED/CCT/CRI/optic/driver combination is identified;
3. raw supplier or laboratory photometry is obtained;
4. raw file bytes are stored unchanged;
5. SHA-256 provenance is recorded;
6. LM-63 data passes the repository ingestor;
7. distribution is cross-checked independently;
8. candidate evaluator blockers are cleared;
9. browser measured-distribution work consumes the exact controlled file;
10. offline application validation is completed before photometric performance claims are made.

## Current file-access limitation

The manufacturer product page exposes the Precision IES links, but the current automated retrieval environment cannot control the raw `application/octet-stream` bytes reliably. The files therefore remain `linked`, not `downloaded`, `parsed` or `verified`.

This limitation must never be worked around by copying photometric values from a plot or generating synthetic IES data.

## Decision rule

The final product head is deliberately not selected yet.

Precision currently has the stronger public technical and photometric evidence. Reggiani currently has the stronger physical-size fit. Supplier returns decide whether one family clears both evidence and design requirements.

If neither finalist can supply exact configuration-matched photometry, reopen the alternate shortlist rather than weakening the evidence standard.

## Repository references

- `fixtures/vx4800/photometry/selection-brief.json`
- `fixtures/vx4800/photometry/qualification/shortlist-v1.json`
- `fixtures/vx4800/photometry/candidates/precision-evo16.json`
- `fixtures/vx4800/photometry/candidates/reggiani-yori-evo-ghostrack-43.json`
- `tools/photometry/candidate_review.py`
- `scripts/ingest_ies.py`
- `tools/web/measured-photometry-adapter.mjs`

## Explicit non-claims

This qualification package does not claim:

- final luminaire selection;
- construction-release electrical design;
- tested lux levels;
- final UGR performance;
- final thermal performance;
- final certification;
- final canopy driver layout.
