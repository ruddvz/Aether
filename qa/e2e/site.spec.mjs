import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const routes = [
  { id: 'catalog', path: '/', selector: 'main' },
  { id: 'vx4800-viewer', path: '/products/vx4800/', selector: '#dock' },
  { id: 'vx4800-inspector', path: '/products/vx4800/inspect/', selector: '.toolbar' },
];

for (const route of routes) {
  test(`${route.id} shell is usable`, async ({ page }, testInfo) => {
    const pageErrors = [];
    page.on('pageerror', error => pageErrors.push(error.message));

    const response = await page.goto(route.path, { waitUntil: 'domcontentloaded', timeout: 45_000 });
    expect(response, `${route.id} must return an HTTP response`).not.toBeNull();
    expect(response.status(), `${route.id} must not return an HTTP error`).toBeLessThan(400);

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

    if (route.id === 'vx4800-viewer') {
      await expect(page.getByRole('navigation', { name: 'Vortex controls' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Lighting' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Motion' })).toBeVisible();
    }
    if (route.id === 'vx4800-inspector') {
      await expect(page.getByRole('navigation', { name: 'Inspector tools' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Inspect' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Measure' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Annotate' })).toBeVisible();
    }

    const screenshotDir = path.join('artifacts', 'screenshots', testInfo.project.name);
    fs.mkdirSync(screenshotDir, { recursive: true });
    await page.screenshot({ path: path.join(screenshotDir, `${route.id}.png`), fullPage: false });

    expect(pageErrors, `${route.id} emitted uncaught browser errors: ${pageErrors.join(' | ')}`).toEqual([]);
  });
}
