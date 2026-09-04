# AETHERIA

AETHERIA is a design and engineering platform for architectural sculptural lighting. VORTEX (`VX4800-BF-01`) is the first fixture implemented on the platform.

## Source-of-truth rule

`fixtures/<product>/fixture.json` plus controlled engineering assets are the product source of truth. HTML, glTF, IFC, GDTF, MVR, drawings and release packages are outputs/adapters, not product authority.

For VORTEX, engineering revision **1.3.0** remains authoritative. Presentation revision **5.2.0** is an interactive visual study and intentionally contains declared visual divergences.

## Public review surfaces

- Presentation viewer: `/products/vx4800/`
- Technical coordination inspector: `/products/vx4800/inspect/`

The technical inspector uses a derived Meshopt-compressed coordination GLB plus BVH-powered browser review tools. It does not change the V5.2 presentation release or manufacturing authority.

## Validate locally

Python 3.12 and Node.js 24 are the controlled CI targets for the current repository tooling.

```bash
pip install -r requirements-dev.txt -r requirements-geometry.txt
python scripts/validate_repository.py
python scripts/qa_geometry.py
python scripts/qa_web_geometry.py
python scripts/qa_optimized_web_geometry.py
pytest -q
python scripts/build_site.py
```

The optimized web-geometry step invokes pinned `@gltf-transform/cli@4.5.0` through `npx`.

## Repository domains

- `schemas/` versioned canonical data contracts.
- `fixtures/` product truth, controlled geometry, schedules, photometry status and presentation studies.
- `scripts/` validators and deterministic builders.
- `tests/` regression tests.
- `site/` public static shell and technical inspector source.
- `docs/` architecture, research and process documentation.

## Photometry

Current VORTEX browser illumination is explicitly **conceptual**. The platform is ready for controlled LM-63 IES and spectral assets, but no browser intensity value is represented as tested lux, lumens or candela.

## License

Third-party dependency policy and upstream research are documented under `docs/`. Product/design asset rights are separate from third-party software licenses.
