# Release checklist

A product presentation release is ready only when:

- canonical manifest validates;
- all controlled asset hashes match;
- engineering and presentation revisions are explicitly separated;
- engineering schedule count/IDs/drop limits pass;
- STEP and DXF files open and pass geometry QA;
- conceptual versus tested photometry is explicit;
- viewer generation passes its regression fingerprint;
- viewer placeholders are fully resolved;
- `scripts/build_product.py` completes successfully for the exact source commit;
- generated coordination GLB and optimized GLB pass their respective QA and provenance checks;
- generated interchange loss reports preserve blocked/eligible states without promoting adapters to authority;
- known limitations are present;
- Pages stable and immutable version routes both build;
- CI passes on the exact commit being released.

The active product pipeline does not create a release ZIP or `SHA256SUMS`. Product and Pages artifacts remain generated outputs downstream of canonical fixture data and controlled engineering assets.
