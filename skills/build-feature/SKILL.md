---
name: build-feature
description: Use when implementing a feature plan file split into phases with task checkboxes. Builds one phase per branch, opens a PR against a feature-wide integration branch, reviews it twice in a subagent, fixes what is worth fixing, then merges before the next phase. Runs the plan's demo once at the end and leaves the final merge to main to the user.
argument-hint: "[<path to plan file>]"
user-invocable: true
disable-model-invocation: true
---

# Build a Feature, Phase by Phase

One phase, one PR, reviewed twice and fixed twice before merge. A feature built in one branch can't be tried; code merged after one review pass merges its fixes unreviewed.

```
main
 └─ integrate/<plan>                         cut once, before the first phase
     ├─ <plan>-phase-1 ──PR──▶ integrate     build, verify, review x2, fix, merge
     ├─ <plan>-phase-2 ──PR──▶ integrate
     ├─ <plan>-phase-N ──PR──▶ integrate
     └──────────────────PR──▶ main           demo, then the user merges
```

**Start from the plan file, never memory.** Path from the argument, else look under `plans/` and ask if several match. Re-read it each phase. Any `_open_` decision: stop, send the user back to planning. Read every Verify line and `## Demo` before phase 1 — a phase with no proof and no deferral is a planning bug, cheapest to raise now.

**One integration branch per feature; one branch and one PR per phase.** Cut `integrate/<plan-name>` from up-to-date `main` and push it, reusing it if it exists. Every phase branches from it and targets it, so `main` never holds half a feature. Build the first phase with unchecked boxes. Never pull work forward from a later phase, even three lines — the boundary is what makes the PR reviewable.

**Resume before you start.** Check what already exists: the integration branch, phase branches, `gh pr list --base integrate/<plan-name>`. An open PR for the current phase means you're mid-cycle — read its commits and review comments for which rounds already ran, and continue from there. Never restart a phase that already has a PR.

**Write the code yourself; delegate only the review.** Plan, code, and verification in one head keeps a phase coherent. Apply review fixes yourself too — you already hold the diff.

**This phase's tasks, nothing else.** Unrelated bugs and tempting refactors become a one-line note in the plan. Tick boxes and update `## Progress` in the same commit as the work.

**Verify before the PR, locally.** Proof it does what it promised, plus the repo's checks — `make build` / `make test` / `make lint` when a Makefile has them, else the project's native commands. Proof is the plan's Verify line; failing that, a test that fails without this phase's code, or a run against a local fixture or dev server. "It compiles" is not proof.

Run against something disposable. Needs a deployed host, shared database, or admin login? Stop and ask, naming what it would change. Never open a credential file to make it runnable — an unset `DATABASE_URL` is a stop sign, not a puzzle.

`deferred` Verify line (older plans say `**Demo:**`): run the repo's checks, say the proof is deferred to the demo, move on. Don't invent one.

**PR targets the integration branch** — `gh pr create --base integrate/<plan-name>`, never `main`. Title `Phase <n>: <imperative title>`, then `## Summary` of what the user gains, bullets proportional to the change, and the plan file path. No test plan, no checklist, no co-author line. No `gh` or no GitHub remote: stop at the pushed branch and say so — don't fake a review cycle.

**Review in a subagent, both rounds, always.** Repo's review skill if installed, as `review-code` with target `pr <number> --sub`; else spawn a subagent to review the diff for correctness, security, resource, and performance defects, rating severity, likelihood, and worth-fixing. Fresh subagent, never you — you wrote it, so you're last to spot what you assumed. Ask for plain prose; an output schema fails the task before the review starts. Spawn, then block on the runtime's wait — no polling. Relay the report as-is.

Round 2 runs even when round 1 was clean: fixes are new code, and that's where the next bug is. Same PR, after the fix commits. Stop at two — still must-fix findings means the phase is too big; say so and let the user decide.

**Fix only what's worth fixing.** Worth-fixing findings get fixed here. Judgment calls: fix if trivial or small *and* in this phase's scope, else log in the plan. Nits stay. Fixes land as their own commits so round 2 sees them. Name what you skipped in one line — a silently dropped finding reads as one that never existed.

**Merge on all four:** verification passes *after the last fix commit* (fixes are code too), both rounds ran, no must-fix left, CI green — wait for it with one blocking `gh pr checks --watch`, not a poll loop. Fallen behind the integration branch? Merge it in and re-verify first. Merge commit, never squash — the per-phase history is the record. Delete the phase branch, return to an up-to-date integration branch.

**Report each phase in one block, then start the next.** PR link, tasks done, findings fixed, findings skipped, what you ran. No asking unless the user said to stop.

**A locked decision proved wrong stops the build.** Name the decision, what the code showed, which later phases it invalidates. The user amends the plan; you don't quietly re-plan around their choice.

**Demo once at the end, exactly as the plan says.** After every phase merges, run `## Demo` and report what you saw. The plan decides, not you: `none` skips straight to the final PR; something you can't run yourself means handing the user steps and waiting. Never invent a demo, never stage one per phase. Plan silent (older ones are)? Ask, record the answer in the plan, then run. Broken demo: fix belongs to the phase that owns it, same branch-review-merge cycle.

**Final PR, integration branch to `main`:** feature summary, the phase PRs, the demo and its result if the plan called for one, commands the user can run, plus any post-merge steps the plan leaves them. `main` moved? Merge it in and re-run the repo's checks. Then stop — the user merges that PR.
