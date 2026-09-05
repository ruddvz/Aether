import { findUnsupportedSchemaKeywords, validateSchemaValue } from "./schema-validator.mjs";
import {
  authorityWarnings,
  changedPaths,
  deepClone,
  deleteAtPath,
  getAtPath,
  humanizeKey,
  prettyJson,
  proposalFilename,
  schemaNodeKind,
  setAtPath,
  sha256Hex,
} from "./editor-core.mjs";

const paths = {
  products: "../../products.json",
  schema: "../../schemas/aether-fixture.schema.json",
};

const ui = {
  product: document.querySelector("#product-select"),
  baselineLabel: document.querySelector("#baseline-label"),
  baselineHash: document.querySelector("#baseline-hash"),
  proposalHash: document.querySelector("#proposal-hash"),
  validationBadge: document.querySelector("#validation-badge"),
  changedBadge: document.querySelector("#changed-badge"),
  schemaBadge: document.querySelector("#schema-badge"),
  form: document.querySelector("#schema-form"),
  raw: document.querySelector("#raw-json"),
  issues: document.querySelector("#issues"),
  changes: document.querySelector("#changes"),
  warnings: document.querySelector("#warnings"),
  download: document.querySelector("#download-proposal"),
  reset: document.querySelector("#reset-proposal"),
  importButton: document.querySelector("#import-proposal"),
  importInput: document.querySelector("#import-file"),
  copy: document.querySelector("#copy-json"),
  status: document.querySelector("#status-line"),
};

const state = {
  registry: [],
  schema: null,
  unsupported: [],
  slug: null,
  baseline: null,
  proposal: null,
  rawParseError: null,
  renderToken: 0,
};

function setStatus(message, level = "neutral") {
  ui.status.textContent = message;
  ui.status.dataset.level = level;
}

function resolvePublicPath(path) {
  return new URL(`../../${path.replace(/^\/+/, "")}`, window.location.href).href;
}

function currentMeta() {
  return state.registry.find((item) => item.slug === state.slug);
}

function isRequired(parentSchema, key) {
  return Array.isArray(parentSchema?.required) && parentSchema.required.includes(key);
}

function controlHelp(schema, required) {
  const fragments = [];
  if (required) fragments.push("Required");
  if (schema.description) fragments.push(schema.description);
  if (schema.pattern) fragments.push(`Pattern: ${schema.pattern}`);
  if (schema.minItems !== undefined || schema.maxItems !== undefined) {
    fragments.push(`Items: ${schema.minItems ?? 0}–${schema.maxItems ?? "∞"}`);
  }
  return fragments.join(" · ");
}

function createFieldShell(label, pathText, schema, required) {
  const wrapper = document.createElement("div");
  wrapper.className = "field";
  const head = document.createElement("div");
  head.className = "field-head";
  const labelEl = document.createElement("label");
  labelEl.textContent = label;
  const pathEl = document.createElement("code");
  pathEl.textContent = pathText;
  head.append(labelEl, pathEl);
  wrapper.append(head);
  const help = controlHelp(schema, required);
  if (help) {
    const helpEl = document.createElement("div");
    helpEl.className = "field-help";
    helpEl.textContent = help;
    wrapper.append(helpEl);
  }
  return wrapper;
}

function commitScalar(path, schema, required, rawValue) {
  if (rawValue === "" && !required) {
    deleteAtPath(state.proposal, path);
    proposalChanged(false);
    return;
  }

  const kind = schemaNodeKind(schema);
  let value = rawValue;
  if (kind === "number" || kind === "integer") {
    value = rawValue === "" ? rawValue : Number(rawValue);
  } else if (kind === "boolean") {
    value = Boolean(rawValue);
  }
  setAtPath(state.proposal, path, value);
  proposalChanged(false);
}

function createScalarControl(schema, value, path, required) {
  const kind = schemaNodeKind(schema);
  if (kind === "enum") {
    const select = document.createElement("select");
    if (!required && value === undefined) {
      const blank = document.createElement("option");
      blank.value = "";
      blank.textContent = "Not set";
      select.append(blank);
    }
    for (const optionValue of schema.enum) {
      const option = document.createElement("option");
      option.value = JSON.stringify(optionValue);
      option.textContent = String(optionValue);
      option.selected = JSON.stringify(optionValue) === JSON.stringify(value);
      select.append(option);
    }
    select.addEventListener("change", () => {
      if (select.value === "" && !required) deleteAtPath(state.proposal, path);
      else setAtPath(state.proposal, path, JSON.parse(select.value));
      proposalChanged(false);
    });
    return select;
  }

  if (kind === "boolean") {
    const input = document.createElement("input");
    input.type = "checkbox";
    input.checked = Boolean(value);
    input.addEventListener("change", () => commitScalar(path, schema, required, input.checked));
    return input;
  }

  const multiline = kind === "string" && (String(value ?? "").length > 90 || schema?.description?.length > 100);
  const input = document.createElement(multiline ? "textarea" : "input");
  if (!multiline) input.type = kind === "number" || kind === "integer" ? "number" : "text";
  if (kind === "integer") input.step = "1";
  if (kind === "number") input.step = "any";
  input.value = value ?? "";
  input.addEventListener("input", () => commitScalar(path, schema, required, input.value));
  return input;
}

function createJsonControl(schema, value, path, required) {
  const textarea = document.createElement("textarea");
  textarea.className = "json-field";
  textarea.spellcheck = false;
  textarea.value = value === undefined ? "" : JSON.stringify(value, null, 2);
  textarea.addEventListener("change", () => {
    const text = textarea.value.trim();
    if (!text && !required) {
      deleteAtPath(state.proposal, path);
      textarea.classList.remove("invalid");
      proposalChanged(false);
      return;
    }
    try {
      setAtPath(state.proposal, path, JSON.parse(text));
      textarea.classList.remove("invalid");
      proposalChanged(false);
    } catch (error) {
      textarea.classList.add("invalid");
      setStatus(`JSON field error at $.${path.join(".")}: ${error.message}`, "error");
    }
  });
  return textarea;
}

function renderSchemaNode(schema, value, path = [], key = "Fixture", required = true) {
  const kind = schemaNodeKind(schema);
  const pathText = path.length ? `$.${path.join(".")}` : "$";

  if (kind === "object-properties") {
    const section = document.createElement(path.length <= 1 ? "section" : "div");
    section.className = path.length <= 1 ? "schema-section" : "schema-group";
    if (path.length) {
      const title = document.createElement(path.length === 1 ? "h2" : "h3");
      title.textContent = humanizeKey(key);
      section.append(title);
      if (schema.description) {
        const description = document.createElement("p");
        description.className = "section-description";
        description.textContent = schema.description;
        section.append(description);
      }
    }
    const grid = document.createElement("div");
    grid.className = path.length <= 1 ? "field-grid" : "nested-grid";
    for (const [childKey, childSchema] of Object.entries(schema.properties || {})) {
      const childPath = [...path, childKey];
      const childValue = value?.[childKey];
      grid.append(renderSchemaNode(childSchema, childValue, childPath, childKey, isRequired(schema, childKey)));
    }
    section.append(grid);
    return section;
  }

  const shell = createFieldShell(humanizeKey(key), pathText, schema, required);
  const control = ["json-object", "json-array", "json"].includes(kind)
    ? createJsonControl(schema, value, path, required)
    : createScalarControl(schema, value, path, required);
  control.dataset.path = pathText;
  shell.append(control);
  return shell;
}

function renderForm() {
  ui.form.replaceChildren();
  if (!state.schema || !state.proposal) return;
  if (state.unsupported.length) {
    const blocked = document.createElement("div");
    blocked.className = "blocked-panel";
    blocked.textContent = "The published fixture schema uses keywords this editor does not implement. Form editing is disabled until the editor is updated. Raw JSON remains visible for inspection.";
    ui.form.append(blocked);
    return;
  }
  ui.form.append(renderSchemaNode(state.schema, state.proposal));
}

function renderList(container, items, emptyText, formatter) {
  container.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = emptyText;
    container.append(empty);
    return;
  }
  const list = document.createElement("ul");
  for (const item of items) {
    const li = document.createElement("li");
    const result = formatter(item);
    if (result instanceof Node) li.append(result);
    else li.textContent = result;
    list.append(li);
  }
  container.append(list);
}

async function refreshDiagnostics() {
  const token = ++state.renderToken;
  const parseError = state.rawParseError;
  const issues = parseError || !state.schema || !state.proposal ? [] : validateSchemaValue(state.schema, state.proposal);
  const changes = state.baseline && state.proposal ? changedPaths(state.baseline, state.proposal) : [];
  const warnings = state.baseline && state.proposal ? authorityWarnings(state.baseline, state.proposal, changes) : [];

  ui.validationBadge.textContent = parseError ? "Invalid JSON" : issues.length ? `${issues.length} schema issue${issues.length === 1 ? "" : "s"}` : "Schema valid";
  ui.validationBadge.dataset.state = parseError || issues.length ? "bad" : "good";
  ui.changedBadge.textContent = `${changes.length} changed path${changes.length === 1 ? "" : "s"}`;
  ui.changedBadge.dataset.state = changes.length ? "warn" : "neutral";
  ui.schemaBadge.textContent = state.unsupported.length ? `${state.unsupported.length} unsupported schema keyword${state.unsupported.length === 1 ? "" : "s"}` : "Schema supported";
  ui.schemaBadge.dataset.state = state.unsupported.length ? "bad" : "good";

  renderList(ui.issues, parseError ? [parseError] : issues, "No validation issues.", (item) => `${item.path ?? "$"} · ${item.keyword ?? "json"}: ${item.message}`);
  renderList(ui.changes, changes.slice(0, 80), "No proposal changes.", (item) => item);
  renderList(ui.warnings, warnings, "No authority warnings. Repository review is still required.", (item) => `${item.code}: ${item.message}`);

  ui.download.disabled = Boolean(parseError || issues.length || state.unsupported.length || !changes.length);
  if (token !== state.renderToken || !state.proposal) return;
  const proposalText = prettyJson(state.proposal);
  const proposalHash = await sha256Hex(proposalText);
  if (token === state.renderToken) ui.proposalHash.textContent = proposalHash;
}

function proposalChanged(syncRaw = true) {
  state.rawParseError = null;
  if (syncRaw) ui.raw.value = prettyJson(state.proposal);
  refreshDiagnostics();
}

async function loadProduct(slug) {
  const meta = state.registry.find((item) => item.slug === slug);
  if (!meta) throw new Error(`Unknown product ${slug}`);
  setStatus(`Loading ${meta.displayName}…`);
  const fixtureUrl = resolvePublicPath(meta.fixtureDataPath);
  const fixtureResponse = await fetch(fixtureUrl, { cache: "no-store" });
  if (!fixtureResponse.ok) throw new Error(`Fixture request failed with ${fixtureResponse.status}`);
  const fixture = await fixtureResponse.json();

  state.slug = slug;
  state.baseline = deepClone(fixture);
  state.proposal = deepClone(fixture);
  state.rawParseError = null;
  ui.product.value = slug;
  ui.baselineLabel.textContent = `${meta.model} · design ${meta.designRevision}`;
  ui.raw.value = prettyJson(state.proposal);
  ui.baselineHash.textContent = await sha256Hex(prettyJson(state.baseline));
  renderForm();
  await refreshDiagnostics();
  setStatus("Loaded canonical public fixture. Changes remain local to this browser until you download a proposal.", "good");
}

async function initialize() {
  try {
    const [registryResponse, schemaResponse] = await Promise.all([
      fetch(paths.products, { cache: "no-store" }),
      fetch(paths.schema, { cache: "no-store" }),
    ]);
    if (!registryResponse.ok) throw new Error(`Product registry request failed with ${registryResponse.status}`);
    if (!schemaResponse.ok) throw new Error(`Fixture schema request failed with ${schemaResponse.status}`);
    state.registry = await registryResponse.json();
    state.schema = await schemaResponse.json();
    state.unsupported = findUnsupportedSchemaKeywords(state.schema);

    ui.product.replaceChildren();
    for (const product of state.registry) {
      const option = document.createElement("option");
      option.value = product.slug;
      option.textContent = `${product.displayName} · ${product.model}`;
      ui.product.append(option);
    }
    if (!state.registry.length) throw new Error("No products are published in products.json");
    await loadProduct(state.registry[0].slug);
  } catch (error) {
    console.error(error);
    setStatus(error.message, "error");
    ui.download.disabled = true;
  }
}

ui.product.addEventListener("change", () => loadProduct(ui.product.value).catch((error) => setStatus(error.message, "error")));
ui.reset.addEventListener("click", () => {
  state.proposal = deepClone(state.baseline);
  state.rawParseError = null;
  ui.raw.value = prettyJson(state.proposal);
  renderForm();
  refreshDiagnostics();
  setStatus("Proposal reset to the published baseline.", "neutral");
});
ui.raw.addEventListener("input", () => {
  try {
    state.proposal = JSON.parse(ui.raw.value);
    state.rawParseError = null;
    renderForm();
    refreshDiagnostics();
  } catch (error) {
    state.rawParseError = { path: "$", keyword: "json", message: error.message };
    refreshDiagnostics();
  }
});
ui.importButton.addEventListener("click", () => ui.importInput.click());
ui.importInput.addEventListener("change", async () => {
  const file = ui.importInput.files?.[0];
  if (!file) return;
  try {
    state.proposal = JSON.parse(await file.text());
    state.rawParseError = null;
    ui.raw.value = prettyJson(state.proposal);
    renderForm();
    await refreshDiagnostics();
    setStatus(`Imported local proposal ${file.name}. Nothing was uploaded.`, "good");
  } catch (error) {
    setStatus(`Import failed: ${error.message}`, "error");
  } finally {
    ui.importInput.value = "";
  }
});
ui.copy.addEventListener("click", async () => {
  if (!state.proposal) return;
  await navigator.clipboard.writeText(prettyJson(state.proposal));
  setStatus("Proposal JSON copied to clipboard.", "good");
});
ui.download.addEventListener("click", () => {
  if (!state.proposal || ui.download.disabled) return;
  const blob = new Blob([prettyJson(state.proposal)], { type: "application/json" });
  const anchor = document.createElement("a");
  anchor.href = URL.createObjectURL(blob);
  anchor.download = proposalFilename(state.slug, state.proposal);
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(anchor.href), 0);
  setStatus("Proposal downloaded. It has no repository or engineering authority until reviewed, committed, and validated through the normal workflow.", "good");
});

initialize();
