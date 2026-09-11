import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

import * as chromeLauncher from 'chrome-launcher';
import lighthouse from 'lighthouse';
import desktopConfig from 'lighthouse/core/config/desktop-config.js';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const CONFIG_PATH = path.join(ROOT, 'fixtures', 'platform', 'web-quality-v1.json');
const ARTIFACT_ROOT = path.join(HERE, 'artifacts', 'lighthouse');

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function safeId(value) {
  return value.replace(/[^a-zA-Z0-9._-]+/g, '-');
}

function errorMessage(error) {
  if (error instanceof Error) return error.stack || error.message;
  return String(error);
}

function withTimeout(promise, timeoutMs, label) {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(`${label} exceeded ${timeoutMs} ms`)), timeoutMs);
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

function writeJson(filePath, value) {
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

const config = readJson(CONFIG_PATH);
const lighthousePolicy = config.lighthouse;
const baseUrl = process.env.AETHERIA_QA_BASE_URL || 'http://127.0.0.1:4174';
const chromePath = process.env.CHROME_PATH;

fs.mkdirSync(ARTIFACT_ROOT, { recursive: true });

const summary = {
  schemaVersion: '1.0.0',
  status: 'pass',
  authority: 'repository-software-qa',
  mode: lighthousePolicy.mode,
  scoreEnforcement: lighthousePolicy.scoreEnforcement,
  baseUrl,
  chromePath: chromePath || null,
  toolchain: config.toolchain,
  categories: lighthousePolicy.categories,
  formFactors: lighthousePolicy.formFactors,
  audits: [],
  failures: [],
  notes: [
    'This stage proves Lighthouse report production and records scores.',
    'Score enforcement is intentionally disabled until canonical historical floors are recovered or deliberately re-approved.',
    'Lighthouse output is software-delivery evidence only and does not qualify VX4800 engineering or physical product performance.'
  ]
};

function recordFailure({ route, formFactor, attempt, phase, error }) {
  const failure = {
    routeId: route.id,
    path: route.path,
    formFactor,
    attempt,
    phase,
    message: errorMessage(error)
  };
  summary.failures.push(failure);
  writeJson(
    path.join(ARTIFACT_ROOT, `${safeId(route.id)}-${formFactor}-attempt-${attempt}.failure.json`),
    failure
  );
  return failure;
}

async function runAuditAttempt(route, formFactor, attempt) {
  const url = new URL(route.path, baseUrl).toString();
  const startedAt = new Date().toISOString();
  let chrome;

  try {
    chrome = await chromeLauncher.launch({
      chromePath,
      logLevel: 'silent',
      chromeFlags: [
        '--headless=new',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--no-first-run',
        '--no-default-browser-check'
      ]
    });
  } catch (error) {
    recordFailure({ route, formFactor, attempt, phase: 'browser-launch', error });
    return null;
  }

  try {
    const flags = {
      port: chrome.port,
      logLevel: 'error',
      output: ['json', 'html'],
      onlyCategories: lighthousePolicy.categories,
      maxWaitForFcp: lighthousePolicy.maxWaitForFcpMs,
      maxWaitForLoad: lighthousePolicy.maxWaitForLoadMs
    };
    const activeConfig = formFactor === 'desktop' ? desktopConfig : undefined;
    const result = await withTimeout(
      lighthouse(url, flags, activeConfig),
      lighthousePolicy.auditTimeoutMs,
      `${route.id}/${formFactor} Lighthouse audit`
    );

    if (!result?.lhr) {
      throw new Error('Lighthouse returned no LHR payload');
    }

    const reportOutputs = Array.isArray(result.report) ? result.report : [result.report];
    if (reportOutputs.length !== 2) {
      throw new Error(`Expected JSON and HTML Lighthouse reports, received ${reportOutputs.length}`);
    }

    const scores = {};
    for (const category of lighthousePolicy.categories) {
      const score = result.lhr.categories?.[category]?.score;
      if (typeof score !== 'number' || !Number.isFinite(score)) {
        throw new Error(`Missing numeric Lighthouse score for ${category}`);
      }
      scores[category] = Number(score.toFixed(3));
    }

    const prefix = `${safeId(route.id)}-${formFactor}`;
    fs.writeFileSync(path.join(ARTIFACT_ROOT, `${prefix}.report.json`), reportOutputs[0]);
    fs.writeFileSync(path.join(ARTIFACT_ROOT, `${prefix}.report.html`), reportOutputs[1]);

    const audit = {
      routeId: route.id,
      path: route.path,
      url,
      formFactor,
      attempt,
      status: 'produced',
      startedAt,
      completedAt: new Date().toISOString(),
      fetchTime: result.lhr.fetchTime || null,
      finalDisplayedUrl: result.lhr.finalDisplayedUrl || null,
      lighthouseVersion: result.lhr.lighthouseVersion || null,
      userAgent: result.lhr.userAgent || null,
      scores
    };
    summary.audits.push(audit);
    writeJson(path.join(ARTIFACT_ROOT, `${prefix}.summary.json`), audit);
    return audit;
  } catch (error) {
    recordFailure({ route, formFactor, attempt, phase: 'audit-production', error });
    return null;
  } finally {
    if (chrome) {
      try {
        await chrome.kill();
      } catch (error) {
        recordFailure({ route, formFactor, attempt, phase: 'browser-cleanup', error });
      }
    }
  }
}

if (!lighthousePolicy.enabled) {
  summary.status = 'skipped';
  summary.notes.push('Lighthouse is disabled in the repository quality policy.');
  writeJson(path.join(ARTIFACT_ROOT, 'summary.json'), summary);
  console.log(JSON.stringify(summary, null, 2));
  process.exit(0);
}

if (!chromePath || !fs.existsSync(chromePath)) {
  summary.status = 'fail';
  summary.failures.push({
    routeId: null,
    path: null,
    formFactor: null,
    attempt: 0,
    phase: 'browser-launch',
    message: `CHROME_PATH is missing or not executable: ${chromePath || '<unset>'}`
  });
  writeJson(path.join(ARTIFACT_ROOT, 'summary.json'), summary);
  console.error(JSON.stringify(summary, null, 2));
  process.exit(1);
}

for (const route of config.routes) {
  for (const formFactor of lighthousePolicy.formFactors) {
    let produced = null;
    for (let attempt = 1; attempt <= lighthousePolicy.maxAttempts; attempt += 1) {
      produced = await runAuditAttempt(route, formFactor, attempt);
      if (produced) break;
    }
    if (!produced) summary.status = 'fail';
  }
}

writeJson(path.join(ARTIFACT_ROOT, 'summary.json'), summary);
console.log(JSON.stringify(summary, null, 2));

if (summary.status !== 'pass') process.exit(1);
