# AETHERIA / Aether

Aether is the design, visualization, release, and presentation repository for **AETHERIA sculptural lighting**. The first product in the repository is **VORTEX / VX4800-BF-01**, a 240-piece suspended butterfly composition with an interactive Three.js presentation viewer.

## Live site

The GitHub Pages deployment is designed to publish at:

**https://ruddvz.github.io/Aether/**

The root site opens the current VORTEX viewer. Versioned product viewers remain available through immutable source folders and release ZIPs.

> GitHub Pages requires a one-time repository setting to use GitHub Actions as the publishing source. The deployment workflow is already included. See `docs/GITHUB_PAGES.md`.

## Repository layout

```text
Aether/
├── .github/                 GitHub Actions, issue templates, CODEOWNERS
├── docs/                    Architecture, versioning, decisions and setup
├── products/                Editable product source and versioned viewers
│   └── vx4800/
│       ├── data/
│       └── viewer/5.2.0/
├── releases/                Immutable release ZIPs
├── scripts/                 Build and validation tooling
├── site/static/             Small static files used by GitHub Pages
├── project.json             Product registry and current-version pointers
├── CHANGELOG.md
└── ROADMAP.md
```

## Current product

| Field | Value |
| --- | --- |
| Brand | AETHERIA |
| Collection | VORTEX |
| Product | VX4800-BF-01 |
| Viewer | v5.2.0 |
| Suspended elements | 240 |
| Live route | `/products/vx4800/` |

## Development model

`main` is always expected to be deployable. Product work should normally happen on a feature branch and merge through a pull request. A product release must update its versioned viewer, immutable ZIP, `project.json`, validation rules, and changelog together.

The public GitHub Pages site is assembled by `scripts/build_site.py`. The deploy job never treats the entire repository as the website. This prevents internal documentation, tooling, and future manufacturing files from accidentally becoming site navigation.

## Local validation

```bash
python scripts/validate_repository.py
python scripts/build_site.py
python -m http.server 8000 --directory _site
```

Then open `http://localhost:8000/`.

## Important status

The VORTEX viewer is a design and presentation artifact. It is not a structural, electrical, photometric, fabrication, or certification release. Engineering-controlled deliverables should remain explicitly separated from presentation assets.

## Licensing

No open-source license is granted by this repository unless a license file is added explicitly in the future. All rights are reserved by default.
