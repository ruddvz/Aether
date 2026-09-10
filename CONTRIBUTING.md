# Contributing

## Core rule

Keep `main` deployable. Do not overwrite a released presentation source or controlled product record in place.

## Branch names

Use short scoped names such as:

- `viewer/vx4800-lighting-refinement`
- `design/vx4800-canopy-study`
- `docs/repository-structure`
- `fix/mobile-safari-layout`

## Product changes

For a VORTEX viewer or presentation change:

1. Make source changes under `fixtures/vx4800/`, including a new presentation version directory when the presentation revision changes.
2. Keep prior controlled presentation sources and revisions unchanged unless a documented correction explicitly requires otherwise.
3. Update `fixtures/vx4800/fixture.json` and `project.json` only when their controlled identities, revisions, assets or current-public pointers must change.
4. Regenerate product artefacts with `python scripts/build_product.py`; do not hand-edit generated `build/` output as source authority.
5. Update `CHANGELOG.md` and any affected authority/process documentation.
6. Run `python scripts/validate_repository.py`.
7. Run `python scripts/build_site.py` and inspect `_site` locally.
8. Open a pull request and require CI to pass on the exact head being merged.

The retired `products/<slug>/viewer/` and `releases/<slug>/` source layout is not part of the current pipeline. Public product routes and downloadable coordination artefacts are generated from `project.json`, `fixtures/` and the deterministic builders.

## Design data

Presentation code must not silently change controlled design quantities. If element counts, product dimensions, canopy architecture, part geometry, or placement schedules change, record the design decision and version the data.

## Engineering claims

Do not describe browser visuals as structural calculations, photometric simulations, certifications, or fabrication approvals.
