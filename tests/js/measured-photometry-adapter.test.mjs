import assert from 'node:assert/strict';
import { createMeasuredDistributionAdapter, sampleMeasuredDistribution, PhotometryAdapterError } from '../../tools/web/measured-photometry-adapter.mjs';

const sha = '9ced87c0320a082aca89b09f04158b77f6513d65e3f2ac6670dafb1d32bbbf33';
const configuration = {
  photometryStatus: 'parsed',
  iesPath: 'tests/fixtures/photometry/synthetic-narrow.ies',
  iesSha256: sha
};
const report = {
  source: { provenanceStatus: 'synthetic-test' },
  lm63: { tilt: 'NONE' },
  photometry: {
    verticalAnglesDeg: [0, 2, 4, 6, 8, 10, 15, 20, 30, 45],
    horizontalAnglesDeg: [0],
    candela: [[1000, 800, 500, 200, 80, 30, 10, 3, 1, 0]],
    maxCandela: 1000
  },
  integrity: { sha256: sha }
};

assert.throws(
  () => createMeasuredDistributionAdapter(configuration, report),
  (err) => err instanceof PhotometryAdapterError && err.code === 'provenance-not-approved'
);

const adapter = createMeasuredDistributionAdapter(configuration, report, { allowSyntheticTest: true, sampleCount: 64, maxAngleDeg: 45 });
assert.equal(adapter.kind, 'aetheria-measured-angular-lut-v1');
assert.equal(adapter.sourceSha256, sha);
assert.equal(adapter.sampleCount, 64);
assert.equal(adapter.values[0], 1);
assert.ok(sampleMeasuredDistribution(adapter, 4) > 0.45 && sampleMeasuredDistribution(adapter, 4) < 0.55);
assert.ok(sampleMeasuredDistribution(adapter, 20) < 0.01);

const badSha = structuredClone(configuration);
badSha.iesSha256 = 'a'.repeat(64);
assert.throws(
  () => createMeasuredDistributionAdapter(badSha, report, { allowSyntheticTest: true }),
  (err) => err instanceof PhotometryAdapterError && err.code === 'sha-mismatch'
);

const multiPlane = structuredClone(report);
multiPlane.photometry.horizontalAnglesDeg = [0, 90];
multiPlane.photometry.candela = [report.photometry.candela[0], report.photometry.candela[0]];
assert.throws(
  () => createMeasuredDistributionAdapter(configuration, multiPlane, { allowSyntheticTest: true }),
  (err) => err instanceof PhotometryAdapterError && err.code === 'multi-plane-unsupported'
);

console.log('measured-photometry-adapter tests passed');
