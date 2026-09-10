# ADR 0002: Canonical fixture data with generated product outputs

Status: Accepted

Date: 2026-09-10

Supersedes: ADR 0001

## Decision

Use `fixtures/<product>/fixture.json` plus controlled engineering assets as product source authority, with `project.json` as the product registry. Deterministic builders write derived product artifacts under `build/`, and `scripts/build_site.py` assembles the public Pages tree under ignored `_site/`.

The former editable `products/<slug>/viewer/` source tree and immutable `releases/<product>/<version>/` package tree are retired. Public product routes are generated from `project.json` and `fixtures/` instead.

`scripts/build_product.py` produces ordinary build artifacts rather than an archive package. Generated HTML, STEP/DXF coordination files, GLB derivatives, interchange reports and public Pages files do not become product or manufacturing authority by being generated.

## Reason

A single canonical product model prevents source, release-package and public-site copies from drifting into competing definitions of the same fixture. Keeping build products derived also makes validation and authority boundaries explicit across presentation, engineering, interchange and public review surfaces.

## Consequences

- Contributors change canonical inputs rather than generated `build/` or `_site/` outputs.
- Product metadata changes are coordinated through `project.json` and the canonical fixture.
- Builders and validators must preserve the distinction between source authority and derived artifacts.
- Historical packaged-release assumptions remain historical only and must not be documented as the current contribution or inspection workflow.
