# AETHERIA web quality validation

## Purpose

This QA layer protects the public repository Pages experience without changing product engineering authority. It covers the AETHERIA catalog, the stable VX4800 VORTEX viewer and the VX4800 technical inspector.

A passing web-quality workflow means the tested software routes built, served, passed the configured browser smoke matrix, stayed within deterministic repository budgets and produced the configured Lighthouse reports. It does not qualify physical product performance, manufacturing geometry, photometry, structure, kinetics, installation or certification.

## Deterministic published-tree QA

`scripts/qa_site.py` validates the built `_site` tree against `fixtures/platform/web-quality-v1.json`.

Blocking checks include required routes, document language, viewport and title, resolvable first-party references, forbidden development URLs, controlled external runtime hosts, per-route HTML size, total published-tree size, largest-file size and the repository rule that ZIP packages are not part of the active Pages product workflow. Ordinary outbound navigation links are not treated as runtime dependencies.

## Cross-browser smoke matrix

The browser toolchain pins `@playwright/test` 1.62.1 and exercises Chromium desktop, Firefox desktop, WebKit desktop, iPhone 15 WebKit emulation and Pixel 7 Chromium emulation.

Catalog and inspector smoke coverage verifies an HTTP response, document metadata, the primary shell, expected control navigation, no unintended document-level horizontal overflow and no unexpected uncaught page error. Screenshots are captured for those non-realtime shells.

The immutable V5.2 viewer uses a narrower browser contract because it starts a continuous WebGL render loop. Static QA already owns its document language, title, local references, external-runtime hosts and size budgets. The browser matrix therefore proves that the viewer route responds and that the first-party `#dock`, `#lightBtn` and `#motionBtn` shell controls actually attach, checks for uncaught page errors during that shell window, and then explicitly closes the page target. It deliberately does not run layout evaluation, accessibility-tree snapshots or compositor screenshots against the hot renderer in the blocking shell gate.

Retained CI traces showed those renderer-adjacent operations taking many seconds on shared Chromium runners after the viewer shell was already present. In one failed run, title access took roughly 14 seconds, layout evaluation roughly 7 seconds, accessibility queries several seconds each and compositor capture roughly 16 seconds, pushing an otherwise successful shell test beyond its 60-second deadline. Viewer failures still retain Playwright traces and error-context snapshots.

Browser/device emulation is regression coverage. It is not proof for every physical handset, operating-system build, browser version or GPU.

## Lighthouse report production

Lighthouse is pinned separately from the Playwright smoke matrix so audit-production failures cannot be confused with browser-smoke failures. The repository currently pins Lighthouse 13.4.1 and `chrome-launcher` 1.2.1. Lighthouse launches the exact Chromium executable installed for the pinned Playwright toolchain rather than relying on an arbitrary system Chrome version.

The report-production job audits the catalog, V5.2 viewer and inspector in both mobile and desktop modes across Performance, Accessibility, Best Practices and SEO. Each route/form-factor pair may retry once if browser launch or report production fails. The job writes raw JSON and HTML reports, a compact score summary for each successful audit, a combined summary and phase-specific failure records.

Browser startup failures are recorded as `browser-launch`. Failures after Chrome is available but before Lighthouse returns a valid report are recorded as `audit-production`. Browser shutdown failures are recorded separately as `browser-cleanup`. This makes runner/transport instability distinguishable from genuine audit findings.

### Continuous-render viewer profile

The first pinned production run proved that catalog mobile and desktop audits complete normally, but the V5.2 viewer does not satisfy Lighthouse's default CPU-idle assumption because its WebGL render loop is intentionally continuous. A generic outer Promise timeout was also the wrong control because terminating Chrome while Lighthouse was still gathering could leave protocol work in flight.

The viewer therefore uses a declared Lighthouse load profile instead of modifying the V5.2 page. It retains normal first-contentful-paint, load-event and network-completion requirements, but sets the post-load FCP, load, network-quiet and CPU-quiet windows to zero and disables the full-page Lighthouse screenshot. In Lighthouse itself, a zero CPU-quiet interval bypasses the page-side CPU-idle probe, which is the protocol path that failed under the hot renderer. Catalog and inspector continue to use Lighthouse's normal load profile.

This is a route-specific measurement contract for an always-rendering application, not a hidden waiver. Every generated route summary records the actual load profile and Lighthouse load settings used for that audit. The Chrome launch no longer forces `--disable-gpu`, so the viewer is not deliberately pushed into a slower software-only rendering path by this QA harness.

Report production is blocking in this phase. Score enforcement is not. The force-pushed pre-salvage history no longer exposes the canonical score floors on current `main`, so this repository does not invent replacements. Issue #110 remains open until the historical floors are recovered or a deliberate score-budget review approves replacements and the resulting score gate is proven reliable. Score floors must not be lowered merely to make CI green.

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

For Lighthouse report production, serve `_site` locally, install Chromium through the pinned Playwright package, resolve that executable into `CHROME_PATH`, and run:

```text
cd qa
CHROME_PATH="$(node -e "const {chromium}=require('@playwright/test'); process.stdout.write(chromium.executablePath())")" \
AETHERIA_QA_BASE_URL=http://127.0.0.1:4174 \
npm run audit:lighthouse
```

## Artifacts

The workflow uploads deterministic static-site QA output, Playwright HTML output, catalog/inspector browser-device screenshots, traces and failure snapshots when applicable, the local browser-smoke HTTP-server log, Lighthouse JSON/HTML reports, Lighthouse route summaries, phase-specific Lighthouse failure records and the Lighthouse HTTP-server log.

## Change control

Catalog shell, viewer source/build path, inspector, public routing, public asset loading, WebGL/CDN dependencies, optimization pipeline, browser version pins, Lighthouse version pins, Lighthouse route load profiles and quality budgets all require web-quality review. New external runtime hosts require explicit allowlist review.
