/**
 * Renderer-neutral bridge from a controlled AETHERIA parsed LM-63 report to a
 * normalized angular lookup table suitable for browser visualization.
 *
 * This module does not parse raw IES, calculate room lux, or approve a product.
 * Product use is gated by candidate configuration status, SHA-256 provenance,
 * supplier/laboratory provenance, TILT=NONE and a distribution shape this
 * first adapter can represent without approximation.
 */

export class PhotometryAdapterError extends Error {
  constructor(code, message) {
    super(message);
    this.name = 'PhotometryAdapterError';
    this.code = code;
  }
}

function fail(code, message) {
  throw new PhotometryAdapterError(code, message);
}

function assertFiniteNumber(value, label) {
  if (!Number.isFinite(value)) fail('invalid-number', `${label} must be a finite number.`);
}

function interpolate(xs, ys, x) {
  if (x <= xs[0]) return ys[0];
  if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
  let lo = 0;
  let hi = xs.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (xs[mid] <= x) lo = mid;
    else hi = mid;
  }
  const span = xs[hi] - xs[lo];
  if (span <= 0) return ys[lo];
  const t = (x - xs[lo]) / span;
  return ys[lo] + (ys[hi] - ys[lo]) * t;
}

export function validateControlledBinding(configuration, report, options = {}) {
  if (!configuration || typeof configuration !== 'object') fail('configuration-missing', 'Candidate configuration is required.');
  if (!report || typeof report !== 'object') fail('report-missing', 'Parsed LM-63 report is required.');

  const allowedStatus = new Set(['parsed', 'verified']);
  if (!allowedStatus.has(configuration.photometryStatus)) {
    fail('photometry-not-controlled', `Candidate photometryStatus must be parsed or verified, got ${configuration.photometryStatus ?? 'missing'}.`);
  }

  const sha = report.integrity?.sha256;
  if (typeof sha !== 'string' || !/^[0-9a-f]{64}$/.test(sha)) fail('report-sha-missing', 'Parsed report SHA-256 is missing or invalid.');
  if (configuration.iesSha256 !== sha) fail('sha-mismatch', 'Candidate IES SHA-256 does not match the parsed report.');
  if (!configuration.iesPath) fail('ies-path-missing', 'Candidate controlled IES path is missing.');

  const provenance = report.source?.provenanceStatus;
  const allowSyntheticTest = options.allowSyntheticTest === true;
  if (!['supplier', 'laboratory'].includes(provenance)) {
    if (!(allowSyntheticTest && provenance === 'synthetic-test')) {
      fail('provenance-not-approved', `Measured browser distribution requires supplier or laboratory provenance, got ${provenance ?? 'missing'}.`);
    }
  }

  if (report.lm63?.tilt !== 'NONE') fail('tilt-unsupported', `Only TILT=NONE is supported, got ${report.lm63?.tilt ?? 'missing'}.`);

  const angles = report.photometry?.verticalAnglesDeg;
  const horizontal = report.photometry?.horizontalAnglesDeg;
  const candela = report.photometry?.candela;
  if (!Array.isArray(angles) || angles.length < 2) fail('vertical-angles-invalid', 'At least two vertical angles are required.');
  if (!Array.isArray(horizontal) || horizontal.length !== 1) {
    fail('multi-plane-unsupported', 'The first measured browser adapter only accepts a single horizontal plane. Multi-plane distributions require a 2D angular adapter and are not collapsed silently.');
  }
  if (!Array.isArray(candela) || candela.length !== 1 || !Array.isArray(candela[0]) || candela[0].length !== angles.length) {
    fail('candela-shape-invalid', 'Candela matrix must contain one horizontal plane matching the vertical-angle count.');
  }

  for (let i = 0; i < angles.length; i++) {
    assertFiniteNumber(angles[i], `verticalAnglesDeg[${i}]`);
    assertFiniteNumber(candela[0][i], `candela[0][${i}]`);
    if (i > 0 && angles[i] <= angles[i - 1]) fail('vertical-angles-unsorted', 'Vertical angles must be strictly increasing.');
    if (candela[0][i] < 0) fail('negative-candela', 'Candela values cannot be negative.');
  }

  const maxCandela = report.photometry?.maxCandela;
  if (!Number.isFinite(maxCandela) || maxCandela <= 0) fail('max-candela-invalid', 'maxCandela must be greater than zero.');

  return { sha, provenance, angles, plane: candela[0], maxCandela };
}

export function createMeasuredDistributionAdapter(configuration, report, options = {}) {
  const controlled = validateControlledBinding(configuration, report, options);
  const sampleCount = options.sampleCount ?? 256;
  if (!Number.isInteger(sampleCount) || sampleCount < 16 || sampleCount > 4096) {
    fail('sample-count-invalid', 'sampleCount must be an integer between 16 and 4096.');
  }

  const sourceMaxAngle = controlled.angles[controlled.angles.length - 1];
  const maxAngleDeg = options.maxAngleDeg ?? Math.min(90, sourceMaxAngle);
  assertFiniteNumber(maxAngleDeg, 'maxAngleDeg');
  if (maxAngleDeg <= 0 || maxAngleDeg > sourceMaxAngle) {
    fail('max-angle-invalid', `maxAngleDeg must be >0 and <= source maximum ${sourceMaxAngle}.`);
  }

  const values = new Float32Array(sampleCount);
  for (let i = 0; i < sampleCount; i++) {
    const angle = (i / (sampleCount - 1)) * maxAngleDeg;
    values[i] = Math.max(0, Math.min(1, interpolate(controlled.angles, controlled.plane, angle) / controlled.maxCandela));
  }

  return {
    kind: 'aetheria-measured-angular-lut-v1',
    sourceSha256: controlled.sha,
    provenanceStatus: controlled.provenance,
    maxCandelaCd: controlled.maxCandela,
    maxAngleDeg,
    sampleCount,
    values,
    note: 'Normalized measured intensity only. This is not a lux simulation or luminaire approval.'
  };
}

export function sampleMeasuredDistribution(adapter, angleDeg) {
  if (!adapter || adapter.kind !== 'aetheria-measured-angular-lut-v1') fail('adapter-invalid', 'Measured distribution adapter is invalid.');
  assertFiniteNumber(angleDeg, 'angleDeg');
  const a = Math.max(0, Math.min(adapter.maxAngleDeg, angleDeg));
  const x = (a / adapter.maxAngleDeg) * (adapter.sampleCount - 1);
  const i0 = Math.floor(x);
  const i1 = Math.min(adapter.sampleCount - 1, i0 + 1);
  const t = x - i0;
  return adapter.values[i0] + (adapter.values[i1] - adapter.values[i0]) * t;
}
