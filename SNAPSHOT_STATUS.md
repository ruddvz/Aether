# AETHERIA local implementation snapshot

Date: 2026-09-03

This is a working source snapshot prepared while GitHub write access in the active session was unavailable.

## Current verified state

- Canonical VORTEX design revision: 1.3.0
- Presentation revision: 5.2.0
- Engineering element count: 240
- Engineering family allocation: 66 S / 144 M / 30 L
- Presentation family allocation: 54 S / 132 M / 54 L
- Maximum controlled lower edge: 4778 mm
- Fixed engineering LED positions: 14
- Repository CAD authority: coordination only
- Manufacturing geometry remains external controlled authority

## Implemented platform capabilities

- canonical fixture schema and validation
- engineering/presentation authority separation
- deterministic viewer generation
- deterministic release ZIP and checksums
- coordination STEP/DXF generation and QA
- deterministic coordination GLB with 240 elements + 240 cables + 14 heads
- public schema/fixture/GLB Pages build paths
- conceptual photometry domain
- exact photometry-selection brief
- photometry candidate schema and objective evaluator
- dependency-free LM-63 `TILT=NONE` ingestion
- raw IES SHA-256 provenance
- parsed IES report schema
- normalized polar SVG generation
- split viewer source: shell + CSS + module JS, while release remains one HTML file
- five real supplier candidate research records plus machine-readable evaluator reviews
- honest-null candidate schema for unverified exact fields
- dormant measured-distribution browser adapter with SHA/provenance gating

## Verification

- repository validation: PASS
- engineering geometry QA: PASS
- web geometry QA: PASS
- pytest: 19 tests PASS
- generated viewer JavaScript syntax: PASS
- deterministic product release: byte-identical across rebuilds
- current deterministic product release SHA-256: `4cffd5a003a718d359811bf6f3b406d8ad197a92cc3632f9321c6859dca48f79`

## Important limitations

- Current lighting remains conceptual until exact supplier/laboratory IES data is approved.
- Precision official IES URLs are registered as linked evidence only; raw bytes are not yet controlled or parsed.
- No shortlisted family currently passes the strict evaluator. Precision is closest with one blocker; other families require exact article-level data.
- Synthetic IES files under `tests/fixtures/` are parser tests only and must never be used as product photometry.
- Kinetic bearing, drive, braking, dynamic clearance and structural calculations remain unresolved engineering tasks.
- The current standalone HTML requires internet access for pinned Three.js modules.
