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
- source and optimized coordination GLBs pass their respective QA gates;
- optimization metadata records source/optimized hashes, byte lengths and tool version;
- required interchange adapters and loss reports build without promoting derived formats to canonical authority;
- known limitations are present;
- Pages stable and immutable presentation routes both build;
- Pages coordination downloads are generated under the controlled design revision;
- CI passes on the exact commit being released.

The current repository pipeline does not create a release ZIP or `SHA256SUMS`. Reproducibility is enforced on the generated presentation and coordination outputs by their controlled fingerprints, manifests and CI checks.
