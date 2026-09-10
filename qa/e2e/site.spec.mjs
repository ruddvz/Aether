import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const routes = [
  { id: 'catalog', path: '/', selector: 'main' },
  { id: 'vx4800-viewer', path: '/products/vx4800/', selector: '#dock' },
  { id: 'vx4800-inspector', path: '/products/vx4800/inspect/', selector: '.toolbar' },
];

function isExpectedCapabilityError(routeId, message, webglAvailable) {
  return (
    routeId === 'vx4800-inspector' &&
    !webglAvailable &&
    message.includes('THREE.WebGLRenderer: Error creating WebGL context')
  );
}

for (const route of routes) {
  test(`${route.id} shell is usable`, async ({ page }, testInfo) => {
    const pageErrors = [];
    page.on('pageerror', error => pageErrors.push(error.message));

    // These are shell smoke tests. Waiting for DOMContentLoaded makes the
    // assertion depend on third-party module latency because ES modules defer
    // DOMContentLoaded until their dependency graph resolves. Commit proves the
    // first-party route responded while the selectors below prove the published
    // shell itself parsed and rendered.
    const response = await page.goto(route.path, { waitUntil: 'commit', timeout: 45_000 });
    expect(response, `${route.id} must return an HTTP response`).not.toBeNull();
    expect(response.status(), `${route.id} must not return an HTTP error`).toBeLessThan(400);

    await expect(page.locator('html')).toHaveAttribute('lang', /\S+/);
    await expect(page).toHaveTitle(/\S+/);
    await expect(page.locator(route.selector).first()).toBeVisible();

    // Non-realtime pages get a short settle interval before layout measurement.
    // The immutable V5.2 viewer runs a continuous WebGL render loop; on shared
    // Chromium CI runners even an 800 ms timer can be delayed by several seconds.
    if (route.id !== 'vx4800-viewer') {
      await page.waitForTimeout(800);
    }
    const layout = await page.evaluate(() => ({
      viewportWidth: window.innerWidth,
      documentWidth: document.documentElement.scrollWidth,
      bodyWidth: document.body.scrollWidth,
    }));
    expect(
      Math.max(layout.documentWidth, layout.bodyWidth),
      `${route.id} should not create unintended horizontal page overflow`,
    ).toBeLessThanOrEqual(layout.viewportWidth + 3);

    if (route.id === 'vx4800-viewer') {
      await expect(page.getByRole('navigation', { name: 'Vortex controls' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Lighting' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Motion' })).toBeVisible();
    }
    if (route.id === 'vx4800-inspector') {
      await expect(page.getByRole('navigation', { name: 'Inspector tools' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Inspect', exact: true })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Measure' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Annotate' })).toBeVisible();
    }

    // A full-page compositor capture is useful evidence for ordinary shells, but
    // the V5.2 viewer is continuously rendering WebGL. Retained traces show that
    // Chromium and Android Chromium can spend ~20 s in page.screenshot() after
    // every functional assertion has already passed, exhausting the test-wide
    // timeout. Keep screenshot capture out of this blocking shell gate for that
    // one realtime route; failure traces and error-context snapshots remain.
    if (route.id !== 'vx4800-viewer') {
      const screenshotDir = path.join('artifacts', 'screenshots', testInfo.project.name);
      fs.mkdirSync(screenshotDir, { recursive: true });
      await page.screenshot({ path: path.join(screenshotDir, `${route.id}.png`), fullPage: false });
    }

    let unexpectedPageErrors = pageErrors;
    if (route.id === 'vx4800-inspector') {
      // The capability probe exists only to distinguish a headless runner that
      // cannot create any WebGL context from a genuine inspector exception.
      // Do not run it on the real-time V5.2 viewer: asking its busy main thread
      // for an extra WebGL context can itself turn a shell smoke test into a
      // renderer-load timeout on shared CI runners.
      const webglAvailable = await page.evaluate(() => {
        const canvas = document.createElement('canvas');
        return Boolean(canvas.getContext('webgl2') || canvas.getContext('webgl'));
      });
      unexpectedPageErrors = pageErrors.filter(
        message => !isExpectedCapabilityError(route.id, message, webglAvailable),
      );
    }

    expect(
      unexpectedPageErrors,
      `${route.id} emitted uncaught browser errors: ${unexpectedPageErrors.join(' | ')}`,
    ).toEqual([]);
  });
}
