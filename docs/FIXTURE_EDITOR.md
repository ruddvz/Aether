# AETHERIA fixture proposal editor

The fixture editor is a browser-only proposal workspace for canonical AETHERIA fixture JSON.

Public route after the Pages build:

`/Aether/tools/fixture-editor/`

The editor is deliberately not a direct repository editor. It cannot write to GitHub, replace a controlled fixture, alter controlled assets, approve engineering changes, or create construction-release evidence.

## Purpose

The editor gives product and engineering reviewers a safer way to inspect and propose changes to a fixture definition without hand-editing a large JSON document blind.

It:

- loads the generated `products.json` registry;
- loads the published canonical fixture JSON for the selected registered product;
- loads the published `aether-fixture.schema.json` schema;
- generates typed controls from schema properties;
- uses JSON blocks for object/array domains where the schema intentionally does not define deeper field semantics;
- keeps a synchronized raw JSON view;
- validates the proposal in the browser;
- reports changed JSON paths relative to the published baseline;
- reports authority-sensitive changes separately from schema errors;
- computes SHA-256 for the exact published baseline text and the normalized proposal JSON;
- imports a local JSON proposal without uploading it;
- downloads a schema-valid changed proposal as a local JSON file.

## Authority boundary

A downloaded proposal has **no repository or engineering authority**.

Schema validity means only that the JSON conforms to the currently published fixture schema subset implemented by the browser validator. It does not mean that:

- physical dimensions are approved;
- mass or centre of gravity is controlled;
- suspension hardware is rated or qualified;
- materials or attachment systems are production approved;
- structural reactions are calculated;
- photometry is approved;
- kinetic safety is validated;
- electrical architecture is released;
- certification evidence exists;
- manufacturing geometry is approved;
- construction release has been granted.

Repository acceptance still requires the normal Git review and validation workflow, plus any physical evidence and release gates applicable to the changed domain.

## Fail-closed schema behavior

`site/tools/fixture-editor/schema-validator.mjs` intentionally implements only the JSON Schema keywords currently needed by `schemas/aether-fixture.schema.json`.

Before enabling structured form editing, the editor recursively checks the published schema for unsupported keywords. If an unsupported keyword appears, structured editing and proposal download are blocked rather than silently treating the new schema rule as optional.

This is important because browser convenience must never weaken canonical validation semantics.

The main repository continues to use the Python `jsonschema` implementation as the canonical schema-validation path. The browser validator is a proposal-time guard, not a replacement for repository validation.

## Schema-generated controls

The current renderer uses these rules:

- `enum` becomes a select control;
- `string` becomes text or multiline text according to content length;
- `number` and `integer` become numeric inputs;
- `boolean` becomes a checkbox;
- objects with declared `properties` become nested schema-driven groups;
- arrays and objects without declared sub-properties remain explicit JSON text blocks.

The last rule is deliberate. The editor does not invent form semantics for unconstrained domains such as conceptual optical, kinematic, electrical, material, manufacturing, or compliance structures.

## Proposal review signals

The editor distinguishes three things:

1. JSON parse state.
2. JSON Schema validation state.
3. Authority/revision review warnings.

Authority warnings currently cover changes under identity, physical, optical, composition, kinematics, electrical, materials, assets, interchange, manufacturing and compliance domains.

Additional warnings are shown when:

- a proposal changed while `identity.designRevision` stayed unchanged;
- asset records changed and controlled hashes therefore need independent recomputation;
- mass status is changed away from `unknown` without a numeric mass value.

These warnings do not attempt to replace engineering review. They are intentionally conservative prompts.

## Integrity hashes

The baseline SHA-256 is computed from the exact text returned by the published fixture route.

The proposal SHA-256 is computed from the editor's normalized pretty-printed JSON with a trailing newline. The downloaded proposal uses the same serialization, so the displayed proposal hash corresponds to the downloaded content at the moment of download.

## Browser privacy and writes

All editing state lives in the browser page process.

The editor performs only public `GET` requests for:

- `products.json`;
- the fixture schema;
- the selected product fixture JSON.

Imported local JSON is read through the browser File API. It is not uploaded.

Downloaded proposals use a local Blob URL. There is no GitHub token, repository-write API, server-side persistence endpoint, analytics upload, or hidden synchronization path in the editor.

## Validation

The ordinary `Validate AETHERIA` workflow now runs:

`node --test tests/js/*.test.mjs`

The fixture-editor test verifies:

- the real published fixture schema uses only supported browser-validator keywords;
- the canonical VX4800 fixture validates in the browser validator;
- invalid physical envelope values are rejected;
- missing required identity is rejected;
- forbidden root properties are rejected;
- unsupported future schema keywords are detected;
- authority-sensitive physical changes produce warnings;
- unchanged revision after a changed proposal produces a warning;
- asset edits require integrity review;
- incomplete measured-mass promotion produces a warning;
- proposal file naming remains deterministic.

The Pages build also fails if the editor HTML or its required modules are not published.

## Adding another product

The product dropdown is generated from `_site/products.json`, which is itself generated from `project.json`.

A newly registered product with a published fixture route therefore becomes available to the editor without hard-coding another product into the editor application. The fixture still must conform to the shared AETHERIA fixture schema or the editor will report the resulting validation differences.
