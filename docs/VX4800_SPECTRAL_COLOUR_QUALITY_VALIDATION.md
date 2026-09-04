# VX4800 spectral colour-quality validation

## Purpose

This workflow controls spectral-power-distribution (SPD) evidence for AETHERIA VORTEX VX4800-BF-01 and provides reproducible independent calculations for colour-quality review.

It does **not** approve the final accent-head family, replace supplier/laboratory evidence, or turn an open-source calculation into certification.

## Current product targets

The current product fixture retains a 3000 K target and CRI Ra target of at least 92. No TM-30 or Duv acceptance threshold is released yet.

Do not invent missing thresholds to make a candidate pass.

## Standards boundary

The current reference set used by this qualification plan is:

- CIE 013.3-1995 for the legacy General Colour Rendering Index (Ra) during the current transition period.
- ANSI/IES TM-30-24 as the current IES colour-rendition method target.
- ANSI/IES TM-40-24 as the current IES CCT / distance-from-Planckian-locus target reference.
- ANSI/IES LP-30-26 as current colour-rendition specification guidance.

CIE has stated that CIE 013.3-1995 remains current during transition and encourages parallel reporting of the legacy CIE General Colour Rendering Index and the newer CIE General Colour Fidelity Index.

## Independent software toolchain

`requirements-spectral.txt` pins:

```text
colour-science==0.4.7
```

The repository uses it for independent calculation of:

- CIE 1995 CRI Ra;
- special CRI R9;
- CIE 2017 colour fidelity index Rf;
- Ohno 2013 CCT/Duv as an independent cross-check;
- ANSI/IES TM-30-18 Rf/Rg as a compatibility cross-check.

### Critical limitation

`colour-science` 0.4.7 exposes ANSI/IES TM-30-18 calculations. The current IES authority is ANSI/IES TM-30-24.

Therefore the repository must never label values from the open-source TM-30-18 implementation as TM-30-24 results.

For a released VX4800 configuration, current TM-30-24 primary evidence must come from a controlled supplier/laboratory report or other controlled implementation demonstrated to use the current method. The repository calculation remains an independent check.

Likewise, the current script's Ohno 2013 CCT/Duv calculation is explicitly labelled an independent check and is not represented as ANSI/IES TM-40-24 output.

## Product SPD input requirements

Product-eligible SPD input must:

1. originate from the exact supplier or laboratory configuration under review;
2. be preserved as exact raw bytes;
3. have a controlled SHA-256;
4. identify the exact head / optic / CCT / operating configuration;
5. cover at least 380-780 nm;
6. use a maximum wavelength step of 5 nm for this repository precondition;
7. retain measurement/report provenance.

These are AETHERIA evidence preconditions. They do not replace any stricter sampling, interpolation, measurement or uncertainty requirements imposed by the applicable current standard or laboratory method.

## Synthetic software test

The GitHub workflow generates a 3000 K Planckian radiator with `colour-science` and runs the full calculation path.

That report must always contain:

```json
{
  "sourceClass": "synthetic-test-only",
  "spectralEvidenceEligible": false,
  "productPhotometryApproved": false
}
```

The synthetic run exists only to prove that the code, library and report schema work together.

It is not luminaire evidence.

## Running a supplier/lab SPD

Expected CSV format:

```csv
wavelength_nm,power
380,0.0123
385,0.0148
...
780,0.0007
```

Run:

```bash
python scripts/analyze_vx4800_spectrum.py \
  --spd-csv path/to/exact-source.csv \
  --source-class laboratory \
  --expected-sha256 <64-character-sha256> \
  --configuration-id <controlled-configuration-id> \
  --configuration-controlled \
  --tm30-24-primary-ref <controlled-report-reference> \
  --output validation-output/vx4800-spectral-report.json
```

A SHA mismatch fails immediately.

Even when the source, hash and configuration are controlled, the script deliberately leaves `productPhotometryApproved` false. Product approval remains a separate controlled release decision that must also consume angular photometry, supplier configuration evidence and the qualification gates already in the repository.

## Required promotion sequence

```text
exact supplier/lab configuration
    -> raw SPD bytes
    -> SHA-256 provenance
    -> source/configuration control
    -> CIE CRI independent cross-check
    -> CIE 2017 Rf independent cross-check
    -> CCT/Duv independent cross-check
    -> TM-30-18 compatibility cross-check
    -> current TM-30-24 primary evidence
    -> released colour-quality criteria
    -> spectral evidence approval
    -> combined photometry release review
```

No earlier step may silently promote a later one.

## Relationship to angular photometry

Spectral evidence does not replace the LM-63 / Radiance work.

The final selected head must have both:

- controlled angular distribution evidence (IES/LDT and independent geometry/photometry cross-checks); and
- controlled spectral evidence for the exact released light-engine/configuration.

A beam can have correct geometry and poor colour quality, or excellent colour quality and the wrong distribution. Both evidence sets are required.

## Current status

All spectral promotion gates remain false. The current product CRI/CCT values remain targets/claims to be verified against exact selected configuration evidence.

Issue #6 remains the supplier evidence acquisition gate and should collect the exact SPD and current TM-30 report alongside the raw IES/LDT return.
