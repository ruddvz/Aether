## What changed

Describe the change and why it is needed.

## Coordination

Agent-Claim: #<implementation-issue>
Agent-ID: <stable-agent-id>

- [ ] I fetched the current integration/default branch before implementation and again before review.
- [ ] I checked issue #114, the target issue/comments, related issues and open PRs for duplicate or overlapping work.
- [ ] The PR head branch matches the active issue claim.
- [ ] Every changed path, including both old and new paths for renames, is inside the accepted claim.
- [ ] No earlier active claim or legacy open PR owns an overlapping required file or shared interface.
- [ ] I reconciled newer accepted base work instead of restoring superseded changes.

For pre-enforcement legacy PRs that genuinely predate the issue-claim system, explain the legacy ownership state instead of inventing claim metadata.

## Scope

- [ ] Presentation / UI only
- [ ] Product geometry or placement
- [ ] Lighting logic
- [ ] Repository infrastructure
- [ ] Documentation
- [ ] Release artifact

State the exact in-scope outcome and explicit non-goals. Valid out-of-scope findings should be linked as separate deduplicated issues rather than silently absorbed.

## Product version

State the affected product and version. Use `N/A` only for repository-only changes that do not alter a controlled product/version.

## Authority and evidence boundary

Identify the controlling source(s) of truth and confirm whether this changes any controlled engineering data. If yes, link the decision/evidence record and explain the downstream impact.

Do not promote generated output, browser visuals, synthetic fixtures, model reasoning or a green repository check into engineering, photometric, manufacturing, certification or site truth.

## Validation

Record the commands/checks that actually ran on the final reconciled branch. An unrun command is not PASS.

- [ ] `python scripts/validate_repository.py` passes, when applicable
- [ ] `pytest -q` passes, when applicable
- [ ] `python scripts/build_site.py` passes, when applicable
- [ ] Scene checked, when affected
- [ ] Vortex checked, when affected
- [ ] Detail checked, when affected
- [ ] Mobile layout checked, when affected
- [ ] Required domain-specific geometry / interchange / photometry / other QA passed
- [ ] Independent review completed when required by the authority surface/risk
- [ ] Public/live verification completed when deployment state is part of acceptance

Paste or link exact evidence for required checks. Distinguish code/test failure from runner or infrastructure failure.

## Critique and remaining risk

Summarise the final self-critique/independent review findings that were resolved. State any remaining blocker, external evidence need, limitation or follow-up issue plainly.

## Completion

An open PR is not end-to-end completion. Confirm the requested repository-authorised stop point for this lane and what remains before issue reconciliation and claim release.
