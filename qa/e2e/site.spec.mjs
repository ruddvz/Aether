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

    // V5.2 is an immutable real-time WebGL presentation. Retained traces show
    // that on shared Chromium runners the renderer can delay title reads,
    // page.evaluate(), accessibility snapshots and screenshots by many seconds
    // even after the static shell is already usable. Static QA separately owns
    // language/title/link/budget checks. Keep this browser gate deliberately
    // shell-scoped and use direct first-party IDs so it proves that the dock and
    // its primary controls actually attach without interrogating the hot render
    // loop. Explicitly close the target afterward so renderer load cannot stall
    // Playwright fixture teardown.
    if (route.id === 'vx4800-viewer') {
      await expect(page.locator('#dock')).toBeVisible();
      await expect(page.locator('#lightBtn')).toBeAttached();
      await expect(page.locator('#motionBtn')).toBeAttached();
      await page.waitForTimeout(250);
      expect(
        pageErrors,
        `${route.id} emitted uncaught browser errors: ${pageErrors.join(' | ')}`,
      ).toEqual([]);
      await page.close({ runBeforeUnload: false });
      return;
    }

    await expect(page.locator('html')).toHaveAttribute('lang', /\S+/);
    await expect(page).toHaveTitle(/\S+/);
    await expect(page.locator(route.selector).first()).toBeVisible();

    await page.waitForTimeout(800);
    const layout = await page.evaluate(() => ({
      viewportWidth: window.innerWidth,
      documentWidth: document.documentElement.scrollWidth,
      bodyWidth: document.body.scrollWidth,
    }));
    expect(
      Math.max(layout.documentWidth, layout.bodyWidth),
      `${route.id} should not create unintended horizontal page overflow`,
    ).toBeLessThanOrEqual(layout.viewportWidth + 3);

    if (route.id === 'vx4800-inspector') {
      await expect(page.getByRole('navigation', { name: 'Inspector tools' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Inspect', exact: true })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Measure' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Annotate' })).toBeVisible();
    }

    const screenshotDir = path.join('artifacts', 'screenshots', testInfo.project.name);
    fs.mkdirSync(screenshotDir, { recursive: true });
    await page.screenshot({ path: path.join(screenshotDir, `${route.id}.png`), fullPage: false });

    let unexpectedPageErrors = pageErrors;
    if (route.id === 'vx4800-inspector') {
      // The capability probe exists only to distinguish a headless runner that
      // cannot create any WebGL context from a genuine inspector exception.
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
