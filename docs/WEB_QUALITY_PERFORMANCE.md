# AETHERIA web quality and performance validation

## Purpose

This QA layer protects the public repository Pages experience without changing product engineering authority. It covers the AETHERIA catalog, the stable VX4800 VORTEX viewer and the VX4800 technical inspector.

A passing web-quality workflow means the tested software routes built, served, passed the configured browser smoke matrix and stayed within the current repository performance budgets. It does **not** qualify physical product performance, manufacturing geometry, photometry, structure, kinetics, installation or certification.

## Quality layers

### 1. Deterministic published-tree QA

`scripts/qa_site.py` validates the built `_site` tree against `fixtures/platform/web-quality-v1.json`.

The blocking checks include:

- required public HTML routes exist;
- each route declares document language, viewport and title;
- direct first-party `href` / `src` references resolve inside the built Pages tree;
- published HTML does not contain local development URLs;
- external HTML hosts are restricted to the controlled allowlist;
- per-route HTML sizes stay within configured budgets;
- total Pages tree and largest-file budgets are enforced;
- ZIP packages are not allowed back into the active Pages product workflow.

This layer is deterministic and should not be relaxed merely because a browser audit is noisy.

### 2. Cross-browser smoke matrix

The browser QA toolchain pins `@playwright/test` 1.62.1 and currently exercises:

- Chromium desktop;
- Firefox desktop;
- WebKit desktop;
- iPhone 15 WebKit emulation;
- Pixel 7 Chromium emulation.

For the catalog, viewer and inspector the smoke suite verifies:

- the route returns without an HTTP error;
- the declared primary UI shell is visible;
- required control navigation is exposed where applicable;
- the page does not create unintended document-level horizontal overflow;
- no uncaught page error is emitted during the smoke interval.

The workflow captures a screenshot for every route/project pair. These screenshots are QA evidence and are not marketing renders.

Device emulation is useful regression coverage but is not a claim that every physical iPhone, Android handset, Safari build, Chrome build or GPU has been tested. Physical-device review remains a separate manual/release activity.

### 3. Lighthouse regression budgets

Lighthouse 13.4.1 is pinned and runs mobile and desktop audits against the locally served Pages tree. The repository checks the following categories:

- performance;
- accessibility;
- best practices;
- SEO.

Score floors live in the machine-readable quality budget rather than in workflow shell code. The first implementation intentionally uses different floors for the simple catalog and the much heavier interactive WebGL routes.

These floors are regression budgets, not public performance guarantees. A score change should be investigated before changing a floor. Lowering a floor solely to make CI green is not an acceptable fix.

## Immutable presentation boundary

The V5.2 viewer is an immutable presentation artifact. This QA track audits it as published and must not silently alter historical V5.2 presentation data or visual behavior simply to raise a Lighthouse score.

If a web-quality issue requires a user-visible viewer redesign, implement it as a new presentation/tooling revision with the normal authority separation rather than mutating V5.2 in place.

## Running locally

Build the product and site with the repository's normal Python/Node prerequisites:

```text
python scripts/build_site.py
python scripts/qa_site.py _site --report qa/artifacts/static-site-qa.report.json
```

The full browser workflow additionally requires Node 24 and the pinned packages in `qa/package.json`. GitHub Actions installs the three Playwright browser engines and runs the complete matrix.

## Artifacts

The workflow uploads `aetheria-web-quality`, containing as available:

- deterministic static-site QA report;
- Playwright HTML report;
- browser/device screenshots;
- traces and failure screenshots when applicable;
- raw Lighthouse JSON reports;
- consolidated Lighthouse budget summary;
- local HTTP-server log.

## Change control

Changes to any of the following should trigger web-quality review:

- catalog shell;
- viewer source/build path;
- technical inspector;
- public routing;
- public asset loading;
- WebGL/CDN dependencies;
- optimization pipeline;
- browser/toolchain version pins;
- quality budgets.

Budget changes require a reason. Toolchain updates should be explicit and pinned. New external runtime hosts require allowlist review rather than being accepted automatically.
