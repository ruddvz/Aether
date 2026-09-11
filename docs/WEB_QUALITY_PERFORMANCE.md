# AETHERIA web quality validation

## Purpose

This QA layer protects the public repository Pages experience without changing product engineering authority. It covers the AETHERIA catalog, the stable VX4800 VORTEX viewer and the VX4800 technical inspector.

A passing web-quality workflow means the tested software routes built, served, passed the configured browser smoke matrix, produced the complete Lighthouse audit set and stayed within deterministic repository and Lighthouse regression budgets. It does not qualify physical product performance, manufacturing geometry, photometry, structure, kinetics, installation or certification.

## Deterministic published-tree QA

`scripts/qa_site.py` validates the built `_site` tree against `fixtures/platform/web-quality-v1.json`.

Blocking checks include required routes, document language, viewport and title, resolvable first-party references, forbidden development URLs, controlled external runtime hosts, per-route HTML size, total published-tree size, largest-file size and the repository rule that ZIP packages are not part of the active Pages product workflow. Ordinary outbound navigation links are not treated as runtime dependencies.

## Cross-browser smoke matrix

The browser toolchain pins `@playwright/test` 1.62.1 and exercises Chromium desktop, Firefox desktop, WebKit desktop, iPhone 15 WebKit emulation and Pixel 7 Chromium emulation.

Catalog and inspector smoke coverage verifies an HTTP response, document metadata, the primary shell, expected control navigation, no unintended document-level horizontal overflow and no unexpected uncaught page error. Screenshots are captured for those non-realtime shells.

The immutable V5.2 viewer uses a narrower browser contract because it starts a continuous WebGL render loop. Static QA already owns its document language, title, local references, external-runtime hosts and size budgets. The browser matrix therefore proves that the viewer route responds and that the first-party `#dock`, `#lightBtn` and `#motionBtn` shell controls actually attach, checks for uncaught page errors during that shell window, and then explicitly closes the page target. It deliberately does not run layout evaluation, accessibility-tree snapshots or compositor screenshots against the hot renderer in the blocking shell gate.

Retained CI traces showed those renderer-adjacent operations taking many seconds on shared Chromium runners after the viewer shell was already present. In one failed run, title access took roughly 14 seconds, layout evaluation roughly 7 seconds, accessibility queries several seconds each and compositor capture roughly 16 seconds, pushing an otherwise successful shell test beyond its 60-second deadline. Viewer failures still retain Playwright traces and error-context snapshots.

Browser/device emulation is regression coverage. It is not proof for every physical handset, operating-system build, browser version or GPU.

## Lighthouse audit production and score enforcement

Lighthouse is pinned to 13.4.1. The workflow audits all three configured routes in mobile and desktop modes, producing six raw JSON reports.

Audit production and score enforcement are intentionally separate phases. `scripts/run_lighthouse.py` launches the pinned Playwright Chromium executable, runs each route/mode audit sequentially, retries report-production failures once, and writes route-specific attempt logs plus `lighthouse-production-summary.json`. Browser launch, DevTools transport, timeout, missing-report, malformed-report and version-mismatch failures are classified as audit-production failures. They are not reported as score regressions.

Only after all six reports are present and structurally valid does `scripts/enforce_lighthouse.py` evaluate category scores. Existing floors are preserved:

- catalog: performance 0.90, accessibility 0.90, best practices 0.90, SEO 0.90;
- VX4800 viewer: performance 0.55, accessibility 0.75, best practices 0.75, SEO 0.70;
- VX4800 inspector: performance 0.55, accessibility 0.80, best practices 0.75, SEO 0.70.

Score floors are regression budgets, not marketing or physical-product claims. They must not be lowered merely to make CI green. The immutable V5.2 presentation must not be changed merely to improve an audit score.

## Running locally

```text
python scripts/build_site.py
python scripts/qa_site.py _site --report qa/artifacts/static-site-qa.report.json
cd qa
npm install --no-audit --no-fund
npx playwright install chromium firefox webkit
AETHERIA_QA_BASE_URL=http://127.0.0.1:4173 npm run test:e2e
```

Serve `_site` on port 4173 before running the browser matrix or Lighthouse. For Lighthouse, set `CHROME_PATH` to the pinned Playwright Chromium executable, then run:

```text
python scripts/run_lighthouse.py --report-dir qa/artifacts/lighthouse
python scripts/enforce_lighthouse.py qa/artifacts/lighthouse --output qa/artifacts/lighthouse-budget-summary.json
```

## Artifacts

The workflow uploads deterministic static-site QA output, Playwright HTML output, catalog/inspector browser-device screenshots, traces and failure snapshots, the local HTTP-server log, all six raw Lighthouse reports, per-attempt Lighthouse logs, the Lighthouse production summary and the score-budget summary.

## Change control

Catalog shell, viewer source/build path, inspector, public routing, public asset loading, WebGL/CDN dependencies, optimization pipeline, browser/Lighthouse version pins and quality budgets all require web-quality review. New external runtime hosts require explicit allowlist review.
