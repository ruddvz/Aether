# AETHERIA web quality validation

## Purpose

This QA layer protects the public repository Pages experience without changing product engineering authority. It covers the AETHERIA catalog, the stable VX4800 VORTEX viewer and the VX4800 technical inspector.

A passing web-quality workflow means the tested software routes built, served, passed the configured browser smoke matrix and stayed within deterministic repository budgets. It does not qualify physical product performance, manufacturing geometry, photometry, structure, kinetics, installation or certification.

## Deterministic published-tree QA

`scripts/qa_site.py` validates the built `_site` tree against `fixtures/platform/web-quality-v1.json`.

Blocking checks include required routes, document language, viewport and title, resolvable first-party references, forbidden development URLs, controlled external runtime hosts, per-route HTML size, total published-tree size, largest-file size and the repository rule that ZIP packages are not part of the active Pages product workflow. Ordinary outbound navigation links are not treated as runtime dependencies.

## Cross-browser smoke matrix

The browser toolchain pins `@playwright/test` 1.62.1 and exercises Chromium desktop, Firefox desktop, WebKit desktop, iPhone 15 WebKit emulation and Pixel 7 Chromium emulation.

Catalog and inspector smoke coverage verifies an HTTP response, document metadata, the primary shell, expected control navigation, no unintended document-level horizontal overflow and no unexpected uncaught page error. Screenshots are captured for those non-realtime shells.

The immutable V5.2 viewer uses a narrower browser contract because it starts a continuous WebGL render loop. Static QA already owns its document language, title, local references, external-runtime hosts and size budgets. The browser matrix therefore proves that the viewer route responds and that the first-party `#dock`, `#lightBtn` and `#motionBtn` shell controls actually attach, checks for uncaught page errors during that shell window, and then explicitly closes the page target. It deliberately does not run layout evaluation, accessibility-tree snapshots or compositor screenshots against the hot renderer in the blocking shell gate.

Retained CI traces showed those renderer-adjacent operations taking many seconds on shared Chromium runners after the viewer shell was already present. In one failed run, title access took roughly 14 seconds, layout evaluation roughly 7 seconds, accessibility queries several seconds each and compositor capture roughly 16 seconds, pushing an otherwise successful shell test beyond its 60-second deadline. Viewer failures still retain Playwright traces and error-context snapshots.

Browser/device emulation is regression coverage. It is not proof for every physical handset, operating-system build, browser version or GPU.

## Lighthouse status

Lighthouse score enforcement is deliberately not an active blocking gate in this version. The earlier draft proved the static and five-browser layers but its Lighthouse audit-production step was not reliable on the shared GitHub Actions runner. Score floors must not be lowered merely to make CI green. Lighthouse can return as a blocking layer after the runner produces all configured reports reliably with route-specific diagnostics.

The immutable V5.2 presentation must not be changed merely to improve an audit score.

## Running locally

```text
python scripts/build_site.py
python scripts/qa_site.py _site --report qa/artifacts/static-site-qa.report.json
cd qa
npm install --no-audit --no-fund
npx playwright install chromium firefox webkit
AETHERIA_QA_BASE_URL=http://127.0.0.1:4173 npm run test:e2e
```

Serve `_site` on port 4173 before running the browser matrix.

## Artifacts

The workflow uploads deterministic static-site QA output, Playwright HTML output, catalog/inspector browser-device screenshots, traces and failure snapshots when applicable, and the local HTTP-server log.

## Change control

Catalog shell, viewer source/build path, inspector, public routing, public asset loading, WebGL/CDN dependencies, optimization pipeline, browser version pins and quality budgets all require web-quality review. New external runtime hosts require explicit allowlist review.
