const ANNOTATION_KEYWORDS = new Set([
  "$schema",
  "$id",
  "title",
  "description",
  "default",
  "examples",
]);

const SUPPORTED_KEYWORDS = new Set([
  ...ANNOTATION_KEYWORDS,
  "type",
  "properties",
  "required",
  "additionalProperties",
  "items",
  "minItems",
  "maxItems",
  "uniqueItems",
  "minLength",
  "maxLength",
  "pattern",
  "enum",
  "const",
  "minimum",
  "maximum",
  "exclusiveMinimum",
  "exclusiveMaximum",
]);

const SUPPORTED_TYPES = new Set(["object", "array", "string", "number", "integer", "boolean", "null"]);

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

function typeMatches(type, value) {
  switch (type) {
    case "object":
      return isPlainObject(value);
    case "array":
      return Array.isArray(value);
    case "string":
      return typeof value === "string";
    case "number":
      return typeof value === "number" && Number.isFinite(value);
    case "integer":
      return Number.isInteger(value);
    case "boolean":
      return typeof value === "boolean";
    case "null":
      return value === null;
    default:
      return false;
  }
}

function issue(path, keyword, message) {
  return { path, keyword, message };
}

function unsupported(found, path, keyword, detail = null) {
  found.push(detail ? { path, keyword, detail } : { path, keyword });
}

function visitUnsupported(schema, path, found) {
  if (!isPlainObject(schema)) {
    unsupported(found, path, "schema-node", "schema nodes must be objects in the browser validator subset");
    return;
  }

  for (const key of Object.keys(schema)) {
    if (!SUPPORTED_KEYWORDS.has(key)) unsupported(found, path, key);
  }

  if (schema.type !== undefined) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!types.length || types.some((type) => typeof type !== "string" || !SUPPORTED_TYPES.has(type))) {
      unsupported(found, path, "type", "unsupported type declaration");
    }
  }

  if (schema.properties !== undefined && !isPlainObject(schema.properties)) {
    unsupported(found, path, "properties", "properties must be an object");
  }
  if (schema.required !== undefined && (!Array.isArray(schema.required) || schema.required.some((item) => typeof item !== "string"))) {
    unsupported(found, path, "required", "required must be an array of strings");
  }
  if (schema.additionalProperties !== undefined && typeof schema.additionalProperties !== "boolean") {
    unsupported(found, path, "additionalProperties", "schema-valued additionalProperties is not implemented");
  }
  if (schema.items !== undefined && !isPlainObject(schema.items)) {
    unsupported(found, path, "items", "tuple/boolean items forms are not implemented");
  }
  if (schema.enum !== undefined && !Array.isArray(schema.enum)) {
    unsupported(found, path, "enum", "enum must be an array");
  }
  if (schema.uniqueItems !== undefined && typeof schema.uniqueItems !== "boolean") {
    unsupported(found, path, "uniqueItems", "uniqueItems must be boolean");
  }

  if (isPlainObject(schema.properties)) {
    for (const [name, child] of Object.entries(schema.properties)) {
      visitUnsupported(child, `${path}.properties.${name}`, found);
    }
  }
  if (isPlainObject(schema.items)) {
    visitUnsupported(schema.items, `${path}.items`, found);
  }
}

export function findUnsupportedSchemaKeywords(schema) {
  const found = [];
  visitUnsupported(schema, "$", found);
  return found;
}

export function validateSchemaValue(schema, value, path = "$") {
  const issues = [];

  if (!isPlainObject(schema)) {
    return [issue(path, "schema", "Schema node must be an object")];
  }

  if (schema.const !== undefined && !sameJsonValue(value, schema.const)) {
    issues.push(issue(path, "const", `must equal ${JSON.stringify(schema.const)}`));
  }

  if (Array.isArray(schema.enum) && !schema.enum.some((candidate) => sameJsonValue(candidate, value))) {
    issues.push(issue(path, "enum", `must be one of ${schema.enum.map((item) => JSON.stringify(item)).join(", ")}`));
  }

  if (schema.type !== undefined) {
    const allowed = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!allowed.some((type) => typeMatches(type, value))) {
      issues.push(issue(path, "type", `must be ${allowed.join(" or ")}`));
      return issues;
    }
  }

  if (typeof value === "string") {
    if (Number.isInteger(schema.minLength) && value.length < schema.minLength) {
      issues.push(issue(path, "minLength", `must contain at least ${schema.minLength} characters`));
    }
    if (Number.isInteger(schema.maxLength) && value.length > schema.maxLength) {
      issues.push(issue(path, "maxLength", `must contain at most ${schema.maxLength} characters`));
    }
    if (typeof schema.pattern === "string") {
      let regex;
      try {
        regex = new RegExp(schema.pattern);
      } catch {
        issues.push(issue(path, "pattern", "schema contains an invalid regular expression"));
        return issues;
      }
      if (!regex.test(value)) issues.push(issue(path, "pattern", `must match ${schema.pattern}`));
    }
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    if (typeof schema.minimum === "number" && value < schema.minimum) {
      issues.push(issue(path, "minimum", `must be at least ${schema.minimum}`));
    }
    if (typeof schema.maximum === "number" && value > schema.maximum) {
      issues.push(issue(path, "maximum", `must be at most ${schema.maximum}`));
    }
    if (typeof schema.exclusiveMinimum === "number" && value <= schema.exclusiveMinimum) {
      issues.push(issue(path, "exclusiveMinimum", `must be greater than ${schema.exclusiveMinimum}`));
    }
    if (typeof schema.exclusiveMaximum === "number" && value >= schema.exclusiveMaximum) {
      issues.push(issue(path, "exclusiveMaximum", `must be less than ${schema.exclusiveMaximum}`));
    }
  }

  if (Array.isArray(value)) {
    if (Number.isInteger(schema.minItems) && value.length < schema.minItems) {
      issues.push(issue(path, "minItems", `must contain at least ${schema.minItems} items`));
    }
    if (Number.isInteger(schema.maxItems) && value.length > schema.maxItems) {
      issues.push(issue(path, "maxItems", `must contain at most ${schema.maxItems} items`));
    }
    if (schema.uniqueItems === true) {
      const encoded = value.map((item) => canonicalJson(item));
      if (new Set(encoded).size !== encoded.length) issues.push(issue(path, "uniqueItems", "must not contain duplicate items"));
    }
    if (isPlainObject(schema.items)) {
      value.forEach((item, index) => {
        issues.push(...validateSchemaValue(schema.items, item, `${path}[${index}]`));
      });
    }
  }

  if (isPlainObject(value)) {
    const properties = isPlainObject(schema.properties) ? schema.properties : {};
    const required = Array.isArray(schema.required) ? schema.required : [];

    for (const name of required) {
      if (!Object.prototype.hasOwnProperty.call(value, name)) issues.push(issue(`${path}.${name}`, "required", "is required"));
    }

    if (schema.additionalProperties === false) {
      for (const name of Object.keys(value)) {
        if (!Object.prototype.hasOwnProperty.call(properties, name)) {
          issues.push(issue(`${path}.${name}`, "additionalProperties", "is not allowed by the schema"));
        }
      }
    }

    for (const [name, childSchema] of Object.entries(properties)) {
      if (Object.prototype.hasOwnProperty.call(value, name)) {
        issues.push(...validateSchemaValue(childSchema, value[name], `${path}.${name}`));
      }
    }
  }

  return issues;
}
