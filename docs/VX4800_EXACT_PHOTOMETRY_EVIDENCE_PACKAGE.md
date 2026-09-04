# VX4800 exact photometry evidence package

## Purpose

The VX4800 photometry toolchain now has two independent evidence tracks:

1. angular distribution evidence from exact IES/LDT source data, LM-63 parsing and Radiance cross-validation; and
2. spectral / colour-quality evidence from exact SPD data, independent colour calculations and current primary colour-rendering evidence.

Those tracks are useful only when they describe the **same exact product configuration**.

This document defines the bridge between them.

## Core rule

A matching family name, CCT or nominal beam angle is not sufficient to combine evidence.

Each evidence package is tied to one explicit configuration ID and one candidate configuration containing:

- manufacturer;
- family;
- exact model/order/article code;
- optic code;
- VX4800 optical role;
- CCT;
- controlled IES identity;
- exact angular report;
- exact spectral report.

The same `configurationId` must appear in both the Radiance and spectral reports.

## Why this matters

Several real-world mismatches can otherwise pass unnoticed:

- a 3000 K SPD measured on one optic paired with an IES from another optic;
- a family-level SPD paired with a configuration-specific IES;
- an old IES revision paired with a newer supplier order code;
- a medium optic marketed as 16 degrees paired with an unresolved `-15.IES` file;
- a laboratory SPD produced at a different drive current from the intended product configuration;
- a supplier TM-30 report for a nearby but different light engine.

The evidence package is designed to make those mismatches visible and machine-testable.

## Eligibility gates

A package can reach `eligible-for-further-review` only when all of the following are true:

1. the candidate's exact configuration has been confirmed;
2. the candidate configuration's `photometryStatus` is `verified`;
3. the candidate stores a controlled IES SHA-256;
4. that IES hash exactly matches the Radiance report source hash;
5. the Radiance source is supplier or laboratory evidence, not synthetic/unknown;
6. the Radiance source is bound to the same controlled `configurationId`;
7. the Radiance pipeline and numerical cross-check both pass;
8. the spectral source is supplier or laboratory evidence with a raw SPD SHA-256;
9. the spectral report is bound to the same controlled `configurationId`;
10. the spectral report itself is eligible according to its provenance/configuration gates;
11. current TM-30-24 primary evidence is controlled and referenced;
12. the angular and spectral configuration IDs match one another and the package.

If any one condition is false, package status is `incomplete`.

## Product approval boundary

`eligible-for-further-review` is **not** product approval.

The package schema and assembler always keep:

```json
"productPhotometryApproved": false
```

Final product photometry still requires a controlled design/release decision considering all three VX4800 optical roles, the 14-head setout, project/application performance, electrical configuration, thermal/configuration compatibility, and the global release framework.

## Current VX4800 optical roles

The controlled design currently uses 14 fixed architectural accent-head positions grouped conceptually as:

- 4 deep-tail narrow heads;
- 6 mid-field spot heads;
- 4 upper-field flood heads.

The grouping does not authorize a particular supplier configuration. Each selected role configuration needs its own exact evidence package.

## Assembler

Use:

```bash
python scripts/assemble_photometry_evidence.py \
  --candidate fixtures/vx4800/photometry/candidates/<candidate>.json \
  --role "mid-field spot" \
  --configuration-id <controlled-configuration-id> \
  --radiance-report <radiance-report.json> \
  --spectral-report <spectral-report.json> \
  --package-id <package-id> \
  --output <evidence-package.json>
```

Exit status:

- `0`: package is eligible for further review;
- `2`: package is structurally assembled but remains incomplete.

An incomplete package is useful: it records exactly which evidence boundary is still unresolved.

## Hash chain

The package records:

- IES SHA-256 from the Radiance report;
- Radiance report SHA-256;
- SPD SHA-256 from the spectral report;
- spectral report SHA-256;
- candidate IES SHA comparison result.

This gives a reproducible chain from raw evidence into the combined package without copying or rewriting the raw photometry.

## Precision Evo 16 current state

The current Precision Evo 16 candidate remains intentionally blocked:

- exact configuration confirmation is false;
- the three public IES links are only `linked`;
- no controlled IES SHA-256 is stored;
- the published 16-degree medium optic vs `-15.IES` filename mapping is unresolved.

The evidence package does not hide or work around those gaps.

## Supplier/laboratory acquisition

Issue #6 remains the acquisition gate.

When the supplier/lab evidence arrives, process each selected role through:

```text
exact configuration confirmation
    -> raw IES/LDT ingestion + SHA
    -> independent Radiance report
    -> raw SPD ingestion + SHA
    -> spectral cross-check report
    -> current TM-30-24 primary evidence
    -> exact configuration evidence package
    -> all-role product photometry release review
```

Do not combine evidence across variants merely to fill missing fields.

## Synthetic testing

Unit tests create in-memory/test-directory evidence objects to prove that the consistency logic works. Those objects are not stored as product evidence and cannot approve product photometry.
