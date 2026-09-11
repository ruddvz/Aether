# AETHAR issue coordination

This protocol coordinates concurrent repository work. It does not change AETHERIA engineering or evidence authority.

Central board: issue #114, `[Agent Board] AETHAR active work claims`.

## Source of ownership truth

Ownership is determined from implementation-issue comment history, not chat state, local worktrees, GitHub assignees or the board table.

The first valid `agent-claim` comment that has not been released or explicitly overridden owns that issue lane. The board is a derived view for visibility.

Until the Phase-B machine enforcement in #115 is installed, agents must perform these checks manually and fail closed on uncertainty.

## Preflight before mutation

1. Fetch the current integration/default branch and inspect newer remote work.
2. Read `AGENTS.md`, `.aether/FAST-KERNEL.md` and `.aether/EXECUTION-LIFECYCLE.md`.
3. Read issue #114.
4. Read the target issue and every current comment.
5. Inspect related parent/child issues and open PRs for conceptual overlap.
6. Inspect likely changed files and shared interfaces/contracts.
7. Treat open pre-enforcement PRs as legacy owners of their actual changed files.
8. If the target is broad, split it into bounded child implementation issues before parallel work.
9. Post one exact claim and re-read the issue before coding.
10. Stop or narrow if an earlier active owner overlaps the issue, branch, path/glob, interface or conceptual lane.

Different issue numbers are not proof of independence.

## Claim format

Use a stable agent ID for the life of one lane and a unique branch dedicated to that lane.

```text
<!-- agent-claim
agent: <stable-agent-id>
branch: <unique-branch>
scope: <short exact scope>
files: <semicolon-delimited paths/globs or "research-only">
interfaces: <shared interfaces/contracts or "none">
-->
CLAIM: <stable-agent-id> owns this lane on <unique-branch>.
```

`research-only` reserves no repository files and does not authorise mutation.

## Ownership rules

- One implementation issue has one active mutation owner at a time.
- One active branch belongs to one active issue at a time.
- First valid unreleased ownership wins.
- Earlier declared file/glob ownership wins over later overlapping claims.
- Shared interface/contract collisions must be serialised even when the files differ.
- A later conflicting agent does not gain ownership by creating a second PR or recreating the change on another branch.
- Existing open PRs remain owners of their actual changed files until merged or closed.
- Claims do not expire automatically.
- A claim that looks stale is still owned until release, issue closure or explicit repository-owner override.

## Updating a claim

A current owner may narrow its scope by posting another `agent-claim` with the same agent and branch. Narrowing does not reset first-claim priority.

Do not silently broaden a claim into another active lane. If additional work is independently reviewable, create a separate issue and claim it separately.

## Heartbeats

A long-running concrete lane without a PR may post a real status heartbeat:

```text
<!-- agent-heartbeat
agent: <stable-agent-id>
branch: <unique-branch>
status: <current progress or blocker>
-->
HEARTBEAT: lane remains active.
```

A heartbeat changes no scope, files, interfaces, branch identity or ownership order. Repeated empty heartbeats are not progress.

## Releasing a lane

When work is merged, abandoned or intentionally handed off, release the matching lane:

```text
<!-- agent-release
agent: <stable-agent-id>
branch: <unique-branch>
-->
RELEASE: lane is available.
```

Do not leave ownership active after stopping work.

## Owner override and reassignment

Agents must not self-declare another active claim abandoned. A repository owner may explicitly reconcile a genuinely abandoned lane.

Phase-B enforcement in #115 must use the hardened `harness-claims/v2` semantics: actor-bound claims where identity is available, safe edited/deleted-comment handling, idempotent event processing and atomic reassignment that transfers ordinary lifecycle control to the actual successor actor while preventing scope broadening.

Until that enforcement exists, an override must be explicit in the issue history and must identify the predecessor lane and intended successor. Ambiguity means stop, not assume ownership.

## Pull request contract

Governed implementation PRs should include:

```text
Agent-Claim: #<implementation-issue>
Agent-ID: <stable-agent-id>
```

Before a PR is called reviewable, verify:

- the implementation issue is still open and owned by the PR agent;
- the PR head branch matches the claim branch;
- every changed path is inside the accepted claim, including both old and new paths for renames;
- no earlier active claim or legacy PR owns an overlapping path/interface;
- current base has been reconciled without restoring obsolete work;
- required validation ran on the final reconciled state.

Phase-B enforcement will make these checks deterministic. Manual discipline remains mandatory until then.

## Conflict handling

If overlap appears:

1. stop mutation on the overlapping scope;
2. preserve the earlier owner's work;
3. narrow the later lane, choose another safe issue, or wait for release;
4. document conceptual conflicts that path matching alone cannot detect;
5. never solve coordination failure by racing another branch.

## Safe parallelism

Parallel mutation is allowed only for demonstrably independent issues/resources. Read-only research/review can run in parallel when it reserves no files.

Sending many agents is safe only when the backlog exposes enough independent ready lanes. Extra agents should remain read-only/idle or take explicit `research-only` work instead of duplicating mutation.
