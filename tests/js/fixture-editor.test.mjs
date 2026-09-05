import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { findUnsupportedSchemaKeywords, validateSchemaValue } from "../../site/tools/fixture-editor/schema-validator.mjs";
import { authorityWarnings, changedPaths, deepClone, proposalFilename, schemaNodeKind } from "../../site/tools/fixture-editor/editor-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../..");
const schema = JSON.parse(fs.readFileSync(path.join(root, "schemas/aether-fixture.schema.json"), "utf8"));
const fixture = JSON.parse(fs.readFileSync(path.join(root, "fixtures/vx4800/fixture.json"), "utf8"));

assert.deepEqual(findUnsupportedSchemaKeywords(schema), [], "published fixture schema must stay within the browser validator subset");
assert.deepEqual(validateSchemaValue(schema, fixture), [], "canonical VX4800 fixture must validate in the browser validator");

const invalid = deepClone(fixture);
invalid.physical.envelopeMm[0] = 0;
const invalidIssues = validateSchemaValue(schema, invalid);
assert.ok(invalidIssues.some((issue) => issue.path === "$.physical.envelopeMm[0]" && issue.keyword === "exclusiveMinimum"));

const missing = deepClone(fixture);
delete missing.identity.productCode;
assert.ok(validateSchemaValue(schema, missing).some((issue) => issue.path === "$.identity.productCode" && issue.keyword === "required"));

const extra = deepClone(fixture);
extra.uncontrolledEditorField = true;
assert.ok(validateSchemaValue(schema, extra).some((issue) => issue.path === "$.uncontrolledEditorField" && issue.keyword === "additionalProperties"));

const unsupportedKeyword = deepClone(schema);
unsupportedKeyword.properties.identity.properties.name.oneOf = [{ type: "string" }];
assert.deepEqual(findUnsupportedSchemaKeywords(unsupportedKeyword), [{ path: "$.properties.identity.properties.name", keyword: "oneOf" }]);

const unsupportedAdditionalSchema = deepClone(schema);
unsupportedAdditionalSchema.properties.identity.additionalProperties = { type: "string" };
assert.deepEqual(findUnsupportedSchemaKeywords(unsupportedAdditionalSchema), [{
  path: "$.properties.identity",
  keyword: "additionalProperties",
  detail: "schema-valued additionalProperties is not implemented",
}]);

const unsupportedTupleItems = deepClone(schema);
unsupportedTupleItems.properties.assets.items = [{ type: "string" }];
assert.deepEqual(findUnsupportedSchemaKeywords(unsupportedTupleItems), [{
  path: "$.properties.assets",
  keyword: "items",
  detail: "tuple/boolean items forms are not implemented",
}]);

const objectUniquenessSchema = { type: "array", uniqueItems: true, items: { type: "object" } };
const duplicateObjectsDifferentKeyOrder = [{ a: 1, b: 2 }, { b: 2, a: 1 }];
assert.ok(validateSchemaValue(objectUniquenessSchema, duplicateObjectsDifferentKeyOrder).some((issue) => issue.keyword === "uniqueItems"));

const objectEnumSchema = { enum: [{ a: 1, b: 2 }] };
assert.deepEqual(validateSchemaValue(objectEnumSchema, { b: 2, a: 1 }), [], "JSON object equality must ignore property ordering");

const proposal = deepClone(fixture);
proposal.physical.maximumDropMm = 4700;
const changes = changedPaths(fixture, proposal);
assert.deepEqual(changes, ["$.physical.maximumDropMm"]);
const warnings = authorityWarnings(fixture, proposal, changes);
assert.ok(warnings.some((warning) => warning.code === "authority-sensitive-change"));
assert.ok(warnings.some((warning) => warning.code === "revision-unchanged"));

const assetProposal = deepClone(fixture);
assetProposal.assets[0].sha256 = "a".repeat(64);
assert.ok(authorityWarnings(fixture, assetProposal).some((warning) => warning.code === "asset-integrity-review"));

const massProposal = deepClone(fixture);
massProposal.physical.massKg.status = "measured";
assert.ok(authorityWarnings(fixture, massProposal).some((warning) => warning.code === "mass-value-missing"));

assert.equal(proposalFilename("vx4800", fixture), "vx4800-fixture-proposal-1.3.0.json");
assert.equal(schemaNodeKind({ type: "object", properties: { name: { type: "string" } } }), "object-properties");
assert.equal(schemaNodeKind({ type: "array", items: { type: "string" } }), "json-array");
assert.equal(schemaNodeKind({ enum: ["a", "b"] }), "enum");

console.log("fixture-editor tests passed");
