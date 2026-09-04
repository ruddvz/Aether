# ADR 0003: Immutable versioned viewers plus stable current route

Status: Accepted

Date: 2026-09-03

## Decision

Publish each released viewer at an immutable version route and publish the version selected by `project.json` at a stable product route.

## Reason

A shared link such as `/products/vx4800/` should always show the current approved presentation, while archived versions must remain reproducible for comparison and review.
