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
- release ZIP is byte-reproducible and passes `ZipFile.testzip()`;
- SHA256SUMS is included;
- known limitations are present;
- Pages stable and immutable version routes both build;
- CI passes on the exact commit being released.
