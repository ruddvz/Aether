# ADR 0001: Separate source, release and deployed site

Status: Accepted

Date: 2026-09-03

## Decision

Keep editable product viewers under `products/`, immutable packaged artifacts under `releases/`, and build the public Pages artifact into ignored `_site/`.

## Reason

AETHERIA is expected to grow beyond a single product. Mixing documentation, source files and public deployment at repository root makes versioning and future products fragile.
