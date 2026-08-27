---
name: build-feature
description: Use when implementing a feature plan file split into phases with task checkboxes. Builds one phase per branch, opens a PR against a feature-wide integration branch, reviews it twice in a subagent, fixes what is worth fixing, then merges before the next phase. Demos the whole feature at the end and leaves the final merge to main to the user.
argument-hint: "[<path to plan file>]"
user-invocable: true
disable-model-invocation: true
---

# Build a Feature, Phase by Phase

Turn a phased plan into merged code. One phase is one PR, reviewed twice and fixed twice before it merges — a plan built in one giant branch cannot be tried by the user, and code merged after a single review pass merges its fixes unreviewed.

```
main
 └─ integrate/<plan>                         cut once, before the first phase
     ├─ <plan>-phase-1 ──PR──▶ integrate     build, verify, review x2, fix, merge
     ├─ <plan>-phase-2 ──PR──▶ integrate
     ├─ <plan>-phase-N ──PR──▶ integrate
     └──────────────────PR──▶ main           demo the feature, then the user merges
```

**Start from the plan file, never from memory.** Take the path from the argument, else look under `plans/` and ask if several match. Re-read it at the start of every phase. If any decision is still `_open_`, stop and send the user back to planning. Read every Verify line before phase 1 — a phase naming no proof and no deferral is a planning bug, cheapest to raise before any code exists.

**One feature, one integration branch; one phase, one branch, one PR.** Before the first phase, cut `integrate/<plan-name>` from an up-to-date `main` and push it, reusing it if it exists. Every phase branches from it and every phase PR targets it, so `main` never holds half a feature. Build the first phase with unchecked boxes, and never pull work forward from a later one even when it is three lines and right there — the phase boundary is what makes the PR reviewable and its verification meaningful.

**Write the code yourself; delegate only the review.** The plan, the code, and the verification stay in one head — that is what keeps a phase coherent. Apply the review fixes yourself too; you already have the diff in context.

**Do the phase's tasks and nothing else.** Unrelated bugs and tempting refactors go into the plan as a one-line note, not into this PR. Tick task boxes and update `## Progress` in the same commit as the work, so an interrupted session knows where it stopped.

**Verify before opening the PR, locally.** Every phase owes proof that it does what it promised, plus the repo's own checks — `make build` / `make test` / `make lint` when a Makefile has them, otherwise the project's native commands. The proof is the plan's Verify line; failing that, a test that fails without this phase's code, or a run against a local fixture or dev server. "It compiles" is not proof.

Verification runs against something disposable. If it would need a deployed host, a shared or production database, or an admin login, stop and ask the user first, naming what it would change. Never open a credential file to make it runnable — an unset `DATABASE_URL` is a stop sign, not a puzzle.

When the Verify line says `deferred` (older plans say `**Demo:**`), run the repo's checks, report that the proof is deferred to the final demo, and move on. Do not invent one.

**Open the PR against the integration branch** with `gh pr create --base integrate/<plan-name>` — a phase PR never targets `main`. Title it `Phase <n>: <imperative title>`, then a `## Summary` of what the user gains, with bullets proportional to what changed, and a line naming the plan file. No test plan, no checklist, no co-author line. If `gh` or a GitHub remote is unavailable, stop at the pushed branch and say so — do not fake a review cycle.

**Review the PR in a subagent — both rounds, always.** Use the repo's review skill if installed, invoked as `review-code` with target `pr <number> --sub`; otherwise spawn a subagent to review that PR's diff for correctness, security, resource, and performance defects, rating each finding by severity, likelihood, and whether it is worth fixing. The reviewer must be a fresh subagent: you wrote this code, so you are the last one who will spot what you assumed. Ask for plain prose — attaching an output schema fails the task before any review starts. Spawn it, then block on the runtime's own wait rather than polling. Relay the report as-is.

Run the second round even when the first was clean — fixes are new, unreviewed code, and that is where the next bug is. Point it at the same PR after the fix commits land. Stop at two rounds; if round 2 still surfaces must-fix findings, the phase is too big — say so and let the user decide.

**Fix only what is worth fixing.** Findings marked worth fixing get fixed in this PR. Judgment calls get fixed if they are trivial or small *and* in this phase's scope, otherwise logged in the plan. Nits get left. Fixes land as their own commits so round 2 can see them, and you say in one line what you skipped and why — a silently dropped finding reads as one that never existed.

**Merge only when all four hold:** verification passes, both rounds ran, no must-fix finding is unfixed, CI is green. Merge into the integration branch with a merge commit — never squash, the per-phase history is the record of how the feature was built — then delete the phase branch and return to an up-to-date integration branch.

**Report the phase in one short block, then start the next.** PR link, tasks done, findings fixed, findings skipped, what you ran to verify. Continue without asking unless the user said to stop.

**When the build proves a locked decision wrong, stop and say so.** Name the decision, what the code showed, and which later phases it invalidates. The user amends the plan; you do not quietly re-plan around their choice.

**Demo once, at the end, then hand the last merge over.** When every phase has merged, ask the user with `AskUserQuestion` how they want the feature demonstrated, offering concrete options from the plan — a local run they drive with your steps, a scripted walkthrough you run and report, or the plan's end-to-end check. Do not pick for them. Whatever they choose must cover every phase whose verification was deferred. Run it and report what you saw; if it breaks, the fix belongs to the phase that owns it, through the same branch-review-merge cycle.

Then open one PR from the integration branch to `main`: a feature summary, the phase PRs it contains, the demo and its result, the commands the user can run themselves, and any steps the plan leaves for them to run against shared systems after merge. If `main` has moved, merge it into the integration branch and re-run the repo's checks. Then stop — the user merges that PR.
