# AETHERIA interchange loss reporting

AETHERIA interchange adapters must report semantic and authority loss explicitly. An export that opens successfully in another application is not evidence that all controlled product meaning survived the conversion.

The first implementation targets VX4800 and establishes a reusable boundary for planned IFC, GDTF and MVR adapters.

## Why this exists

The canonical VX4800 record combines product identity, controlled engineering schedules, coordination geometry, conceptual photometry, unresolved kinetic engineering, prototype material decisions and explicit release limitations. IFC, GDTF and MVR represent different subsets of that information.

A silent conversion can therefore create dangerous ambiguity. Typical examples include:

- treating coordination geometry as fabrication geometry;
- turning a conceptual 14-head lighting study into approved luminaire photometry;
- inventing a GDTF control personality from a DALI concept;
- using Blender light poses as engineering aiming data;
- presenting a static scene exchange as evidence of kinetic safety;
- omitting unresolved mass, secondary retention or braking information without warning.

The loss-reporting layer prevents those cases from becoming invisible.

## Files

- `fixtures/vx4800/interchange/export-profile-v1.json` defines target-specific mapping and loss policy.
- `schemas/aether-interchange-loss-report.schema.json` defines the generated report contract.
- `scripts/build_interchange_loss_report.py` builds deterministic reports from the canonical fixture and policy.
- `tests/test_interchange_loss_reporting.py` enforces source invariants and authority boundaries.

## Controlled source invariants

Before generating a report, the VX4800 profile requires the canonical source to remain:

- fixture ID `vx4800-bf-01`;
- design revision `1.3.0`;
- 240 controlled butterfly elements;
- 66 S / 144 M / 30 L;
- 240 main suspension lines;
- 14 fixed lighting heads.

If those values change without an updated interchange profile, report generation fails. The adapter must be reviewed against the new controlled design instead of assuming the old mapping remains valid.

## Dispositions

Every mapping is classified as one of:

- `preserved`: the source meaning can be carried without an authority downgrade;
- `approximated`: a useful review representation is possible, but the target representation is not equivalent to the source;
- `external-reference`: the authoritative information remains outside the target file and should be referenced rather than flattened silently;
- `omitted`: the target output does not carry the source meaning.

Losses are separately classified as `info`, `warning` or `blocking`.

## IFC baseline

The current IFC direction is eligible only for **coordination-only** exchange.

The baseline may carry product identity, envelope/proxy geometry, controlled counts and references to controlled schedules. It may identify the product as kinetic and describe unresolved photometry as metadata.

It may not become:

- manufacturing geometry;
- structural design;
- kinetic safety evidence;
- approved photometry;
- construction release authority.

A future IfcOpenShell exporter should consume this policy and attach the generated loss report or equivalent machine-readable provenance to the exported package.

## GDTF baseline

GDTF generation is currently **blocked**.

The controlled product record does not yet contain the exact approved lighting-head model/optic, final emitter evidence, or a released GDTF/DMX control personality. Creating those values from the conceptual lighting study would fabricate product data.

The GDTF gate can be revisited after exact head selection, angular/spectral evidence and actual control functions are released.

## MVR baseline

MVR generation is currently **blocked** for lighting-authoritative exchange.

The engineering 14-head setout can be retained as a controlled external reference, but a useful lighting MVR package depends on released fixture-type data and controlled final aiming/target definitions. Blender photographic lights and visualization aiming are expressly excluded as engineering input.

## Commands

Generate an IFC coordination-loss report:

```bash
python scripts/build_interchange_loss_report.py --target ifc
```

Write a report to disk:

```bash
python scripts/build_interchange_loss_report.py \
  --target ifc \
  --output build/interchange/vx4800-ifc-loss-report.json
```

The command exits `0` when the target is eligible at its declared authority level. It exits `2` when blocking losses make the target ineligible. Therefore GDTF and MVR intentionally return `2` today.

## Promotion rule

A future exporter must not remove a blocking loss merely because code can technically emit a file. Promotion requires the missing controlled engineering/product input to exist and the corresponding profile, tests and documentation to be deliberately updated.

The loss report itself is `derived-interchange-review` authority. It documents conversion boundaries. It does not approve manufacturing, structural design, photometry, kinetic safety or construction release.
