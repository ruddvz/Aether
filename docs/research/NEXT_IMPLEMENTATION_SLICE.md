# Next implementation slice

Do this before adding more third-party dependencies.

## Objective

Make VORTEX the first fixture that validates against the AETHERIA canonical schema and can generate viewer data from that schema.

## Work items

1. Finish the repository bootstrap on `main` so CI, Pages and tooling exist.
2. Add `fixtures/vx4800/fixture.json` with only known/controlled values.
3. Mark unknown mass, final photometry, final motor/bearing and certification status explicitly rather than inventing values.
4. Keep the current engineering schedule and presentation-only V5 changes distinguishable.
5. Add a schema validator in CI.
6. Add asset-reference and SHA-256 validation.
7. Convert the VORTEX viewer build to consume generated fixture data.
8. Add a photometry asset model but leave the current light field marked `conceptual` until real supplier/test IES data exists.
9. Add a mesh QA report using trimesh.
10. Only after the above is stable, add IESNA and glTF-Transform as the first new runtime/build dependencies.

## Explicitly deferred

- IFC export.
- GDTF export.
- MVR export.
- DMX/Art-Net/sACN control.
- browser IFC.
- path-traced browser mode.

These are valuable, but implementing them before the canonical fixture model would create adapters with no stable source of truth.