# Contributing

## Core rule

Keep `main` deployable. Do not overwrite an immutable released viewer in place.

## Branch names

Use short scoped names such as:

- `viewer/vx4800-lighting-refinement`
- `design/vx4800-canopy-study`
- `docs/repository-structure`
- `fix/mobile-safari-layout`

## Product changes

For a VORTEX viewer change:

1. Create a new version folder under `products/vx4800/viewer/`.
2. Keep prior released folders unchanged.
3. Update `project.json` only when the new version becomes current.
4. Add or replace the matching immutable release artifact in `releases/vx4800/<version>/`.
5. Update `CHANGELOG.md`.
6. Run `python scripts/validate_repository.py`.
7. Run `python scripts/build_site.py` and inspect `_site` locally.
8. Open a pull request.

## Design data

Presentation code must not silently change controlled design quantities. If element counts, product dimensions, canopy architecture, part geometry, or placement schedules change, record the design decision and version the data.

## Engineering claims

Do not describe browser visuals as structural calculations, photometric simulations, certifications, or fabrication approvals.
