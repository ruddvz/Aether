const AUTHORITY_PREFIXES = [
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
  if (parent && typeof parent === "object") delete parent[path.at(-1)];
  return root;
}

function sameJsonValue(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

function collectChanges(baseline, proposal, path, changes) {
  if (sameJsonValue(baseline, proposal)) return;

  const baseObject = baseline !== null && typeof baseline === "object" && !Array.isArray(baseline);
  const proposalObject = proposal !== null && typeof proposal === "object" && !Array.isArray(proposal);
  if (baseObject && proposalObject) {
    const keys = new Set([...Object.keys(baseline), ...Object.keys(proposal)]);
    for (const key of [...keys].sort()) {
      collectChanges(baseline[key], proposal[key], `${path}.${key}`, changes);
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
      message: `${authorityPaths.length} changed path${authorityPaths.length === 1 ? " is" : "s are"} within engineering, product, asset or compliance domains. Schema validity does not approve these changes.`,
    });
  }

  if (paths.length && baseline?.identity?.designRevision === proposal?.identity?.designRevision) {
    warnings.push({
      code: "revision-unchanged",
      message: `The proposal differs from the baseline but identity.designRevision is still ${proposal?.identity?.designRevision ?? "unset"}. Review versioning before repository submission.`,
    });
  }

  const controlledAssetsChanged = paths.some((path) => path.startsWith("$.assets"));
  if (controlledAssetsChanged) {
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
