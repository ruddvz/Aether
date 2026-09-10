---
name: aetheria-agent-cto-fast-kernel
version: 1.0.0
project: AETHERIA
status: executable-v1
issue: 64
---

# AETHERIA Agent CTO Fast Kernel

## Purpose

This is the compact cross-cutting agent kernel for AETHERIA. It is intentionally small. Deeper engineering, geometry, schema, builder, validator, fixture and release documents load only when the task requires them.

The kernel interprets and routes work. It does not become engineering authority.

## Authority rules that always survive compaction

1. `fixtures/<product>/fixture.json` plus controlled engineering assets are product authority.
2. Schemas and validators govern validity. Generated HTML, glTF/GLB, IFC, GDTF, MVR, drawings, site output and release packages are derived outputs/adapters unless a controlled source says otherwise.
3. Reverse dependency traversal may identify impact. It never reverses authority.
4. For VORTEX, engineering revision 1.3.0 remains authoritative over presentation revision 5.2.0 unless the controlled engineering source itself changes.
5. Presentation studies may have declared divergences. Do not silently promote them into engineering truth.
6. Current browser illumination is conceptual. Never report it as measured lux, lumens or candela.
7. Missing LM-63 IES, spectral, manufacturing or engineering evidence remains unknown. Do not fill it from nearby geometry, UI values, generic reference data or model reasoning.
8. A validation/build/test claim requires real command output. An unrun check did not pass.
9. Release/manufacturing or other external irreversible action requires explicit owner/qualified authority. The software harness does not self-authorise physical truth.
10. Use the smallest work/context tier that can prove the requested outcome. Budgets are ceilings, never targets.

## Adaptive workflow

For non-trivial work, classify:

- mode;
- authority surface;
- risk;
- blast radius;
- reversibility;
- evidence state;
- requested delivery stop.

Use:

```bash
python scripts/agent_cto.py --authority-surface <surface> --risk <risk> --blast <blast> --reversibility <state> --evidence <state> --delivery-stop <stop>
python scripts/agent_cto.py --validate
pytest -q tests/test_agent_cto.py
```

The machine policy lives in `.aether/agent-cto.json`.

## Authority surfaces

- `documentation`: non-authoritative repository prose and navigation.
- `presentation`: visual study/presentation surface that does not change canonical engineering truth.
- `public-inspector`: technical browser inspector/review behaviour.
- `builder-validator`: deterministic generation or validation tooling.
- `canonical-fixture`: controlled fixture product data.
- `schema`: versioned canonical data contract.
- `source-geometry`: controlled geometry/model source.
- `photometry-evidence`: controlled photometric/spectral evidence state.
- `release-manufacturing`: release/manufacturing-facing output or decision.

The authority surface is more important than line count. A one-line canonical schema edit can require deeper proof than a large presentation-only CSS change.

## Context economy

Prefer, in order:

1. exact canonical fixture/schema/engineering asset or changed file;
2. declared revision/authority source;
3. bounded repository-intelligence slice from issue #61 when current;
4. affected deterministic builder/validator;
5. broader repository search;
6. full long engineering document only when the narrower evidence cannot answer the task.

Do not load every product/output format for every task. Do not skip an affected output merely to save tokens.

## Value-of-information gate

Before another source, tool, agent or validation step, ask:

> Can this additional work plausibly change canonical authority, affected outputs, engineering evidence, verification requirements or release decision?

If no, skip it.

If a protected engineering/release proof is still missing, it has value even when expensive. Critical work may exceed an ordinary soft ceiling with the reason recorded.

## Parallelism

Default to one mutation lane for one canonical/contract surface. Parallelise independent read-only QA/evidence review only when it avoids duplicate work. Multiple agents do not create missing authority or measured evidence.

Converge shared findings before modifying canonical fixture/schema/geometry state.

## Verification selection

The adaptive governor returns a starting verification frontier. Existing repository validators remain the actual evidence producers. Depending on impact, the frontier can include:

- repository validation;
- geometry QA;
- web geometry QA;
- optimised web geometry QA;
- pytest;
- site build;
- browser visual verification;
- independent engineering review;
- qualified photometry evidence review;
- owner release review.

Missing graph/context coverage is uncertainty, not permission to skip proof.

## Stop rules

Stop additional work when:

- acceptance is proven at the requested delivery stop;
- another source/tool has low expected decision value;
- missing controlled owner/engineering/photometry evidence is the actual blocker;
- the same repair repeats without a new diagnosis;
- the next action exceeds the requested stop point.

Do not mutate for answer/plan-only work. Do not call a draft PR or generated artefact manufacturing truth.

## Learning boundary

Persist only concise, evidence-backed reusable failure modes or routing patterns with applicability, exclusions, confidence and source revision. Do not store hidden chain-of-thought or private prompts.

## Integration boundary

This v1 is additive and does not yet install an always-on root `AGENTS.md`. That is deliberate. The classifier/kernel must first pass repository tests and review. Once proven, a thin root pointer may make it always-on without copying this doctrine into multiple client files.

## Completion rule

Issue #64 is complete only after the kernel/governor tests execute, representative AETHERIA tasks are evaluated, repository-intelligence integration is wired, and authority/verification behaviour is proven. The existence of this file is not completion.
