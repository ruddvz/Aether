# Contributing

## Core rule

Keep `main` deployable. Treat canonical fixture data and controlled engineering assets as source authority; generated build and Pages outputs are derivatives.

## Branch names

Use short scoped names such as:

- `viewer/vx4800-lighting-refinement`
- `design/vx4800-canopy-study`
- `docs/repository-structure`
- `fix/mobile-safari-layout`

## Product changes

For a VORTEX product or viewer change:

1. Edit the authoritative source under `fixtures/vx4800/` and, where registry metadata changes, `project.json`.
2. Version controlled product or presentation data deliberately; do not edit generated `build/` or `_site/` files as source.
3. Update `CHANGELOG.md` when the change is user-, product-, or engineering-visible.
4. Run `python scripts/validate_repository.py`.
5. Run the affected geometry, web-geometry, interchange, photometry or other domain QA required by the change.
6. Run `pytest -q`.
7. Run `python scripts/build_product.py` for product-artifact changes.
8. Run `python scripts/build_site.py` and inspect `_site` locally for public-surface changes.
9. Open a pull request and require the relevant CI gates to pass before merge.

The retired `products/<slug>/viewer/` and `releases/<product>/<version>/` source layouts are not part of the current workflow. Public product routes are generated from `project.json` and `fixtures/`, and `scripts/build_product.py` emits ordinary build artifacts without an archive package.

## Design data

Presentation code must not silently change controlled design quantities. If element counts, product dimensions, canopy architecture, part geometry, or placement schedules change, record the design decision and version the data.

## Engineering claims

Do not describe browser visuals as structural calculations, photometric simulations, certifications, or fabrication approvals.
