# AETHERIA public brand site

This folder contains the public editorial layer built into the repository's existing GitHub Pages artifact.

## Public routes

- `/` — brand homepage
- `/collections/` — five-family collection architecture
- `/collections/flight/`
- `/collections/ocean/`
- `/collections/botanica/`
- `/collections/celestial/`
- `/collections/abstract-motion/`
- `/vortex/` — VORTEX brand story and gateway to controlled product surfaces
- `/applications/` — architectural typology guidance
- `/studio/` — design method and authority model
- `/lookbook/` — digital concept archive
- `/concept.html?id=...` — reusable concept-study detail surface

The existing `/products/vx4800/` and `/products/vx4800/inspect/` routes remain the product viewer and technical inspector.

## Authority boundary

Concept pages, collection copy and generated imagery are presentation material. They do not modify fixture JSON, controlled geometry, photometry, material qualification, certification evidence or released engineering records.

`VORTEX` is the implemented fixture programme in the current registry. Other named studies on the public site remain explicitly marked as concept or exploratory work.

## Images

Web imagery is stored as text-safe base64 chunks under `assets-b64/`. `scripts/build_site.py` reconstructs normal WebP files into `_site/assets/` during the Pages build. This is an implementation detail of the repository workflow, not a product-data source.
