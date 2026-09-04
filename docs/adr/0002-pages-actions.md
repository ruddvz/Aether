# ADR 0002: Deploy GitHub Pages with Actions

Status: Accepted

Date: 2026-09-03

## Decision

Use the official GitHub Pages Actions workflow rather than a committed `gh-pages` build branch.

## Reason

The source of truth remains on `main`, the deploy artifact is reproducible, and generated `_site/` output does not pollute version control.
