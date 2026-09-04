# ADR 0004: Deduplicate the embedded architectural background

Status: Accepted

Date: 2026-09-03

## Decision

Keep the viewer self-contained but embed the WebP architectural background only once as a CSS variable.

## Reason

The original standalone V5.2 HTML embedded the same PNG payload twice and was approximately 5.2 MB. The repository version converts that background to a high-quality WebP and references one embedded copy from both background layers. This keeps the viewer portable while making the source substantially smaller and faster to review and deploy.
