# VX4800 photometry candidate integration status

Date: 2026-09-03

This document records the first supplier-research integration into the AETHERIA candidate evaluator. It is not a luminaire approval.

## Evaluator state

| Candidate | Research status | Evaluator decision | Blockers | Warnings | Passes | Main unresolved item |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Precision Lighting Evo 16 | shortlisted | reject-for-now | 1 | 4 | 16 | exact configuration and raw IES identity must be confirmed |
| ERCO Eclipse 48V XS | shortlisted | reject-for-now | 8 | 9 | 13 | exact XS article numbers and configuration-specific photometry |
| formalighting Zero 40 LV | shortlisted | reject-for-now | 9 | 8 | 12 | exact DALI article codes and exact 32 degree fixed-CCT engine |
| KIT Concept A90D-5L | research-only | reject-for-now | 8 | 9 | 13 | manufacturer IES/LDT not yet published and optic codes absent |
| Reggiani Yori Evo Ghostrack 43 | shortlisted | reject-for-now | 15 | 12 | 7 | exact current 43 mm article/optic/CRI/wattage mapping and files |

`reject-for-now` means the candidate cannot enter controlled product photometry yet. It does not mean the supplier family is commercially rejected.

## Precision position

Precision is currently closest to technical qualification. The official current product documentation publishes the 6, 16 and 30 degree optics, 3000K, CRI 92 at 3000K, 9 W input, DALI-2 remote power supply option, product dimensions and direct manufacturer IES links.

The candidate remains blocked because:

- the order codes are assembled from the manufacturer ordering matrix rather than a factory quotation/order acknowledgement;
- the public IES filenames do not identify CCT in the filename;
- the medium optic is published as 16 degrees while the official IES filename is `G2490.334.314-15.IES`;
- the raw IES bytes have not yet been stored, hashed and independently checked in this repository.

No Precision IES file is marked `downloaded`, `parsed` or `verified` in this release.

## Browser measured distribution

`tools/web/measured-photometry-adapter.mjs` is implemented and tested but is not connected to V5.2.

The adapter requires:

- candidate `photometryStatus` of `parsed` or `verified`;
- an exact candidate IES SHA-256 matching the parsed report;
- supplier or laboratory provenance in normal product use;
- `TILT=NONE`;
- a single horizontal plane for this first 1D implementation.

It explicitly rejects multi-plane data instead of reducing it to the first plane silently.

Current V5.2 remains conceptual and continues to use its existing WebGL spotlight presentation. A future measured-light viewer revision must explicitly choose a WebGPU/TSL path or a documented WebGL-compatible measured texture/shader path.
