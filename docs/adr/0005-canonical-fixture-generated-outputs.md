# ADR 0005: Canonical fixture sources and generated public outputs

Status: Accepted

Date: 2026-09-10

Supersedes: ADR 0001

## Decision

Use `fixtures/<product>/` as the canonical product-source boundary, with `project.json` as the product registry and versioned schemas under `schemas/` defining repository contracts.

Repository builders generate derived artefacts into `build/` and the deployable Pages tree into `_site/`. Those generated directories are outputs, not source authority.

The current pipeline does not maintain editable product sources under `products/` and does not create repository release ZIP packages under `releases/`.

## Public product delivery

`scripts/build_product.py` generates the presentation viewer and product derivatives from controlled repository inputs. `scripts/build_site.py` assembles the Pages tree, including stable and versioned presentation routes, canonical fixture data, inspector routes, coordination downloads and their manifests.

Public coordination downloads are keyed by the controlled design revision. Presentation routes are separately keyed by the presentation revision.

## Authority boundary

Generated HTML, GLB, optimized GLB, IFC and browser-inspection artefacts remain derived outputs. They do not replace the canonical fixture, controlled schedules, external manufacturing geometry, approved photometry, structural evidence or other explicitly controlled engineering authority.

## Consequences

- contributors change canonical inputs rather than hand-editing generated output;
- prior controlled revisions remain traceable in their versioned fixture/presentation sources;
- CI can rebuild public artefacts from the exact Git commit;
- product growth does not require a parallel hand-maintained `products/` or `releases/` hierarchy;
- historical documentation that refers to the bootstrap release-ZIP layout must be treated as superseded.
