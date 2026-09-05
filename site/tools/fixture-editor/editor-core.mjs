const AUTHORITY_PREFIXES = [
  "$.$schema",
  "$.schemaVersion",
  "$.identity",
  "$.physical",
  "$.optical",
  "$.composition",
  "$.kinematics",
  "$.electrical",
  "$.materials",
  "$.assets",
  "$.interchange",
  "$.manufacturing",
  "$.compliance",
  "$.provenance",
];

export function deepClone(value) {
  return structuredClone(value);
}

export function prettyJson(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

export function humanizeKey(key) {
  return String(key)
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replace(/[_-]+/g, " ")
    .replace(/^./, (match) => match.toUpperCase());
}

export function getAtPath(root, path) {
  return path.reduce((value, key) => (value == null ? undefined : value[key]), root);
}

export function setAtPath(root, path, value) {
  if (path.length === 0) return value;
  let cursor = root;
  for (let index = 0; index < path.length - 1; index += 1) {
    const key = path[index];
    if (cursor[key] === undefined || cursor[key] === null || typeof cursor[key] !== "object") {
      cursor[key] = typeof path[index + 1] === "number" ? [] : {};
    }
    cursor = cursor[key];
  }
  cursor[path.at(-1)] = value;
  return root;
}

export function deleteAtPath(root, path) {
  if (path.length === 0) return root;
  const parent = getAtPath(root, path.slice(0, -1));
  const key = path.at(-1);
  if (Array.isArray(parent) && Number.isInteger(key)) parent.splice(key, 1);
  else if (parent && typeof parent === "object") delete parent[key];
  return root;
}

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map((item) => canonicalJson(item)).join(",")}]`;
  if (isPlainObject(value)) {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function sameJsonValue(left, right) {
  return canonicalJson(left) === canonicalJson(right);
}

function collectChanges(baseline, proposal, path, changes) {
  if (sameJsonValue(baseline, proposal)) return;

  if (isPlainObject(baseline) && isPlainObject(proposal)) {
    const keys = new Set([...Object.keys(baseline), ...Object.keys(proposal)]);
    for (const key of [...keys].sort()) {
      collectChanges(baseline[key], proposal[key], `${path}.${key}`, changes);
    }
    return;
  }

  if (Array.isArray(baseline) && Array.isArray(proposal)) {
    const maxLength = Math.max(baseline.length, proposal.length);
    for (let index = 0; index < maxLength; index += 1) {
      collectChanges(baseline[index], proposal[index], `${path}[${index}]`, changes);
    }
    return;
  }

  changes.push(path);
}

export function changedPaths(baseline, proposal) {
  const changes = [];
  collectChanges(baseline, proposal, "$", changes);
  return changes;
}

export function authorityWarnings(baseline, proposal, paths = changedPaths(baseline, proposal)) {
  const warnings = [];
  const authorityPaths = paths.filter((path) => AUTHORITY_PREFIXES.some((prefix) => path === prefix || path.startsWith(`${prefix}.`) || path.startsWith(`${prefix}[`)));
  if (authorityPaths.length) {
    warnings.push({
      code: "authority-sensitive-change",
      message: `${authorityPaths.length} changed path${authorityPaths.length === 1 ? " is" : "s are"} within schema, engineering, product, asset, compliance or provenance domains. Schema validity does not approve these changes.`,
    });
  }

  if (paths.length && baseline?.identity?.designRevision === proposal?.identity?.designRevision) {
    warnings.push({
      code: "revision-unchanged",
      message: `The proposal differs from the baseline but identity.designRevision is still ${proposal?.identity?.designRevision ?? "unset"}. Review versioning before repository submission.`,
    });
  }

  if (paths.length && baseline?.provenance?.updatedAt === proposal?.provenance?.updatedAt) {
    warnings.push({
      code: "provenance-date-unchanged",
      message: "The proposal differs from the baseline but provenance.updatedAt is unchanged. Update provenance only when the proposed revision is intentionally prepared for repository review.",
    });
  }

  if (baseline?.identity?.fixtureId !== proposal?.identity?.fixtureId || baseline?.identity?.productCode !== proposal?.identity?.productCode) {
    warnings.push({
      code: "registered-identity-change",
      message: "fixtureId or productCode differs from the selected registered product. Treat this as a new identity/re-registration proposal and review registry, routes, assets and downstream references together.",
    });
  }

  if (paths.some((path) => path.startsWith("$.assets"))) {
    warnings.push({
      code: "asset-integrity-review",
      message: "Asset records changed. Recompute and independently verify every affected SHA-256 before controlled repository acceptance.",
    });
  }

  if (proposal?.physical?.massKg?.status && proposal.physical.massKg.status !== "unknown" && proposal.physical.massKg.value === undefined) {
    warnings.push({
      code: "mass-value-missing",
      message: "physical.massKg.status is no longer unknown but no mass value is present.",
    });
  }

  return warnings;
}

export function proposalFilename(slug, proposal) {
  const revision = String(proposal?.identity?.designRevision || "unversioned").replace(/[^a-zA-Z0-9._-]+/g, "-");
  const safeSlug = String(slug || "fixture").replace(/[^a-zA-Z0-9._-]+/g, "-");
  return `${safeSlug}-fixture-proposal-${revision}.json`;
}

export function schemaNodeKind(schema) {
  const type = Array.isArray(schema?.type) ? schema.type.find((item) => item !== "null") : schema?.type;
  if (Array.isArray(schema?.enum)) return "enum";
  if (type === "object" && schema?.properties && typeof schema.properties === "object") return "object-properties";
  if (type === "object") return "json-object";
  if (type === "array") return "json-array";
  if (["string", "number", "integer", "boolean"].includes(type)) return type;
  return "json";
}

export async function sha256Hex(text) {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}
