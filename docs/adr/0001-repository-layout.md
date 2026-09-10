# ADR 0001: Separate source, release and deployed site

Status: Superseded by ADR 0002

Date: 2026-09-03

## Decision

Keep editable product viewers under `products/`, immutable packaged artifacts under `releases/`, and build the public Pages artifact into ignored `_site/`.

## Reason

AETHERIA is expected to grow beyond a single product. Mixing documentation, source files and public deployment at repository root makes versioning and future products fragile.

## Supersession

The repository later moved product authority into canonical `fixtures/<product>/` data plus `project.json`, with ordinary generated artifacts under `build/` and public Pages output under `_site/`. See ADR 0002 for the current layout decision.
