# AETHAR execution lifecycle

This lifecycle explains how an independent agent takes one bounded issue from discovery to the repository-authorised stop point without duplicate ownership or premature completion claims.

It complements `.aether/FAST-KERNEL.md`; it does not replace AETHERIA authority or validation rules.

## 1. Select a safe implementation issue

When the operator asks to continue through the backlog, do not simply choose the next issue number.

A safe mutation candidate is:

- open;
- implementation-ready rather than a broad programme issue or an external evidence gate;
- dependency-unblocked for the work being attempted;
- not already actively claimed;
- not already implemented by an open PR;
- free of file/glob, interface and conceptual ownership conflicts;
- compatible with the agent's authority/risk capability and the requested stop point.

Prefer higher-priority safe work according to repository policy. If no safe mutation issue exists, report the blockers or take a clearly marked `research-only` lane. Do not manufacture scope just to remain busy.

## 2. Require an agent-ready work item

Before implementation, the issue should make the following clear where applicable:

- outcome and why it matters;
- controlling source(s) of truth;
- exact in-scope work;
- explicit non-goals;
- dependencies/blockers;
- expected files/globs and shared interfaces;
- acceptance criteria;
- validation commands/evidence;
- UI/UX/accessibility/browser checks for visual or interactive work;
- engineering/safety/evidence restrictions for controlled domains;
- rollout/live verification for public/deployed work;
- rollback/recovery needs for persistent or destructive changes;
- completion condition.

If the issue is too broad for one independent owner, split it before coding.

## 3. Preflight and claim

Run the full preflight in `.aether/ISSUE-COORDINATION.md` and post one bounded claim.

Re-read the issue and active board after claiming. If another earlier owner exists or an overlap becomes visible, stop or narrow before changing files.

One agent should hold one active mutation lane by default.

## 4. Implement the smallest complete outcome

Use the authority surface, risk, blast radius, reversibility, evidence state and requested delivery stop from `.aether/FAST-KERNEL.md` to choose the appropriate work/context tier.

Do not expand scope just because nearby problems are visible. For a valid out-of-scope bug, improvement, UX defect, missing state or evidence gap:

1. search for an existing issue;
2. update it if it already exists;
3. otherwise create a detailed follow-up issue;
4. leave the current lane bounded unless ownership is explicitly reconciled.

Do not hide critical in-scope defects behind follow-up issues. Fix them in the current lane and re-verify.

## 5. Critique and independent review

Before finalising the lane, inspect the implementation against:

- the issue acceptance criteria;
- authority/source-of-truth rules;
- engineering/evidence honesty;
- error and edge states;
- UI/UX/accessibility/responsive behaviour where relevant;
- performance/reliability/security where relevant;
- maintainability and regression risk;
- actual changed-file scope.

For medium/high-risk or engineering-significant work, the implementer is not the only acceptance authority. Use independent review when required by the authority kernel, issue or repository policy.

A reviewer is read-only unless it separately owns a repair lane.

## 6. Validate with real evidence

Run the smallest verification frontier that can prove the requested outcome, expanding when the affected authority surface requires it.

Typical repository checks can include:

- `python scripts/validate_repository.py`;
- affected geometry/web-geometry/interchange/photometry QA;
- `pytest -q`;
- product/site builds;
- browser/visual verification for public surfaces;
- independent engineering review;
- qualified external evidence where a repository check cannot create physical truth.

An unrun command is `not-executed`, never PASS. Preserve failures and blockers.

## 7. Reconcile current base before review

Before a PR is called reviewable:

1. fetch the current integration/default branch;
2. compare the claimed branch with current base;
3. preserve newer accepted work;
4. remove superseded or duplicate edits;
5. confirm changed paths and interfaces still fit the accepted claim;
6. rerun required validation on the reconciled state.

If newer work invalidates the lane, narrow, supersede or retire it rather than restoring stale code.

## 8. Pull request and review

The PR should explain:

- problem/outcome;
- exact scope and non-goals;
- source/authority boundary;
- validation actually run;
- unresolved blockers or external evidence still required;
- coordination metadata (`Agent-Claim` and `Agent-ID`).

Do not call the task complete merely because the PR exists.

Resolve applicable review/CI findings. Distinguish code failure from runner/infrastructure failure; a check that never executed is not proof either way.

## 9. Merge and live verification

Merge only when repository/owner policy authorises it and the required gates are satisfied.

For public/deployed behaviour, verify the live result when the issue requires it. Do not substitute a local build for live verification when deployment state is part of acceptance.

For engineering, manufacturing, site, photometry, certification or supplier evidence, repository merge cannot manufacture missing external authority. Keep such gates blocked until real controlled evidence exists.

## 10. Reconcile issue and release ownership

After the authorised stop point:

- update/close the implementation issue truthfully;
- record any remaining external blocker or follow-up issue;
- release the lane when mutation ownership is no longer needed.

Do not keep stale file locks after stopping work.

## 11. Continue with the next issue

If the operator asked to keep going, return to Step 1.

Every new issue requires:

- fresh current-base fetch;
- fresh board/issue/PR overlap review;
- fresh issue quality check;
- fresh claim;
- fresh branch;
- fresh validation plan.

Ownership, assumptions and validation evidence never carry automatically from the previous lane.

## Completion states

Use explicit truth states rather than a generic "done":

- **green**: the requested repository-authorised stop point and required evidence are satisfied;
- **partial**: useful bounded work exists but the requested stop point is not fully satisfied;
- **blocked**: a dependency, ownership conflict, external evidence or authority requirement prevents progress;
- **failed**: attempted work/validation disproved the intended outcome and no safe repair remains in the lane.

For an implementation issue whose requested stop point is end-to-end completion, `green` normally means: implemented, critiqued/reviewed, validated on final reconciled state, PR/CI resolved, merged when authorised, live/public verification completed when applicable, issue reconciled and claim released.
