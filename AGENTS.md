# AETHAR agent rules

These rules apply to every repository-capable human or automated agent working here.

## Load local authority first

Before actionable work, read `.aether/FAST-KERNEL.md`. It is the compact AETHERIA authority and execution kernel. Load deeper engineering, geometry, schema, photometry, manufacturing, release or other domain material only when the task requires it.

The harness coordinates work. It never becomes engineering, manufacturing, photometric, certification, supplier, site or release authority.

## Load ownership and lifecycle rules before mutation

Before changing repository files, also read:

1. `.aether/ISSUE-COORDINATION.md`
2. `.aether/EXECUTION-LIFECYCLE.md`
3. issue #114, `[Agent Board] AETHAR active work claims`
4. the target issue and every current comment
5. open pull requests and likely changed paths/interfaces

Do not begin implementation until one bounded implementation issue is safely claimed.

## One mutation lane per agent by default

- One implementation issue has one active mutation owner at a time.
- One active mutation lane uses one unique branch.
- First valid unreleased claim wins.
- Declared file/glob and shared-interface ownership is serialised across active issues.
- `research-only` reserves no repository files.
- Claims never expire merely because they look old.
- Broad programme/master issues are coordination-only. Split independently reviewable work into child issues before parallel mutation.
- Different issue numbers do not prove two lanes are independent.
- Existing open pull requests count as ownership of their actual changed files until merged or closed.

If a target lane or required path/interface is already owned, narrow the work, select another safe issue, or remain read-only. Do not duplicate implementation.

## Every issue should be agent-ready

Implementation issues intended for independent agents should state the outcome, controlling sources, exact scope, explicit non-goals, dependencies, expected ownership, acceptance criteria, required validation/evidence and completion condition. Use the repository's agent-ready implementation issue form where appropriate.

When implementation discovers a valid problem outside the accepted lane, deduplicate it and create or update a separate issue. Do not silently absorb unrelated work.

## Verification is evidence

A command that did not execute did not pass. Preserve failed, partial and blocked results. Use the verification frontier required by `.aether/FAST-KERNEL.md`, `CONTRIBUTING.md`, the target issue and affected authority surface.

For medium/high-risk or engineering-significant changes, the author is not the only acceptance authority. Use independent review where repository policy or the authority kernel requires it.

## Done means done

An open PR is not completion. Follow `.aether/EXECUTION-LIFECYCLE.md` to the repository-authorised stop point: reconcile current base, run required validation, resolve review/CI, merge when authorised, verify public/live behaviour when applicable, reconcile the issue and release the claim.

If the operator asks to continue through the backlog, finish or truthfully stop the current lane, then perform a fresh preflight and claim a fresh safe issue. Ownership never carries from one issue to the next.
