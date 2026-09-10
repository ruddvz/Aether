# ADR 0001: Separate source, release and deployed site

Status: Superseded by ADR 0005

Date: 2026-09-03

## Historical decision

Keep editable product viewers under `products/`, immutable packaged artifacts under `releases/`, and build the public Pages artifact into ignored `_site/`.

## Reason at the time

AETHERIA was expected to grow beyond a single product. Mixing documentation, source files and public deployment at repository root made versioning and future products fragile.

## Supersession

The repository no longer uses `products/` or `releases/` as source directories. ADR 0005 records the current canonical-fixture and generated-output layout.
